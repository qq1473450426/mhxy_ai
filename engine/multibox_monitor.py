"""五开账号健康监控。

每次 tick 只做一次健康检查/恢复动作：
1. 检查游戏窗口是否仍存在；
2. 掉线后按策略重连；
3. 连续重连达到上限后按备用账号顺序切换；
4. 任一账号异常时给队伍返回 PAUSE，避免其他账号继续跑任务。
"""
from dataclasses import dataclass, field
from typing import Any

from django.utils import timezone

from dashboard.models import Account, Worker, Log
from .manager import manager
from .reconnect import ReconnectCoordinator, ReconnectPolicy, ReconnectState
from .window_manager import find_window


class ManagerReconnectExecutor:
    def reconnect(self, account_id: int, password: str | None = None) -> dict[str, Any]:
        account = Account.objects.get(pk=account_id)
        manager.start(account)
        return {"success": True, "mode": "RESTART_CLIENT"}

    def switch_account(self, failed_account_id: int, backup_account_id: int) -> dict[str, Any]:
        failed = Account.objects.get(pk=failed_account_id)
        backup = Account.objects.get(pk=backup_account_id)
        manager.stop(failed)
        manager.start(backup)
        return {"success": True, "mode": "SWITCH_BACKUP"}


@dataclass
class TeamHealthResult:
    status: str
    accounts: list[dict[str, Any]] = field(default_factory=list)


class MultiAccountMonitor:
    def __init__(self):
        self.states: dict[int, ReconnectState] = {}

    def _state(self, account: Account) -> ReconnectState:
        return self.states.setdefault(account.id, ReconnectState(account.id, active_account_id=account.id))

    def check_account(self, account: Account) -> dict[str, Any]:
        worker, _ = Worker.objects.get_or_create(account=account)
        window = find_window(account.hwnd, account.window_title)
        if window:
            worker.state = 'IDLE' if worker.state in {'DISCONNECTED', 'ERROR', 'STARTING', 'LOGIN'} else worker.state
            worker.pid = window.pid
            worker.last_heartbeat = timezone.now()
            worker.message = '客户端窗口正常'
            worker.save(update_fields=['state', 'pid', 'last_heartbeat', 'message', 'updated'])
            return {'account_id': account.id, 'healthy': True, 'state': worker.state, 'window': True}

        worker.state = 'DISCONNECTED'
        worker.message = '检测不到游戏窗口'
        worker.save(update_fields=['state', 'message', 'updated'])
        Log.objects.create(account=account, level='WARN', event='DISCONNECT_DETECTED', message='多开健康检查：检测不到游戏窗口')

        if not account.auto_reconnect:
            return {'account_id': account.id, 'healthy': False, 'state': 'DISCONNECTED', 'action': 'PAUSE_AUTO_RECONNECT_OFF'}

        state = self._state(account)
        backups = list(account.backup_accounts.values_list('id', flat=True))
        coordinator = ReconnectCoordinator(ManagerReconnectExecutor(), ReconnectPolicy(account.max_reconnect_attempts, account.max_backup_switches, account.reconnect_delay_seconds))
        result = coordinator.handle_disconnect(state, backups)
        if result['status'] in {'RECONNECTED', 'SWITCHED_BACKUP'}:
            worker.reconnects += 1
            worker.message = result['status']
            worker.save(update_fields=['reconnects', 'message', 'updated'])
        return {'account_id': account.id, 'healthy': False, 'state': worker.state, 'action': result['status'], 'result': result}

    def check_team(self, account_ids: list[int]) -> TeamHealthResult:
        accounts = list(Account.objects.filter(id__in=account_ids, enabled=True).order_by('id'))
        results = [self.check_account(account) for account in accounts]
        unhealthy = [x for x in results if not x['healthy']]
        return TeamHealthResult('PAUSE' if unhealthy else 'RUNNING', results)


monitor = MultiAccountMonitor()
