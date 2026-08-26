"""多开掉线检测与备用账号切换策略。

本模块只负责状态机和策略，不直接执行登录、进程启动或鼠标键盘操作。
实际登录动作由注入的 ReconnectExecutor 完成。
"""
from dataclasses import dataclass, field
from typing import Any, Protocol


class ReconnectExecutor(Protocol):
    def reconnect(self, account_id: int, password: str | None = None) -> dict[str, Any]: ...
    def switch_account(self, failed_account_id: int, backup_account_id: int) -> dict[str, Any]: ...


@dataclass(frozen=True)
class ReconnectPolicy:
    max_attempts: int = 3
    max_backup_switches: int = 2
    cooldown_seconds: int = 15


@dataclass
class ReconnectState:
    account_id: int
    attempts: int = 0
    backup_switches: int = 0
    active_account_id: int | None = None
    failed: bool = False
    events: list[str] = field(default_factory=list)


class ReconnectCoordinator:
    """处理掉线 -> 多次重连 -> 切换备用账号 -> 再次重连。"""

    def __init__(self, executor: ReconnectExecutor, policy: ReconnectPolicy | None = None):
        self.executor = executor
        self.policy = policy or ReconnectPolicy()

    def handle_disconnect(
        self,
        state: ReconnectState,
        backup_account_ids: list[int],
        password_provider=None,
    ) -> dict[str, Any]:
        state.failed = False
        state.events.append("DISCONNECTED")

        if state.attempts < self.policy.max_attempts:
            state.attempts += 1
            password = password_provider(state.active_account_id or state.account_id) if password_provider else None
            result = self.executor.reconnect(state.active_account_id or state.account_id, password)
            if result.get("success"):
                state.events.append(f"RECONNECTED_ATTEMPT_{state.attempts}")
                return {"status": "RECONNECTED", "account_id": state.active_account_id or state.account_id, "attempt": state.attempts, "events": state.events}
            state.events.append(f"RECONNECT_FAILED_{state.attempts}")
            return {"status": "RETRY", "account_id": state.active_account_id or state.account_id, "attempt": state.attempts, "events": state.events}

        if state.backup_switches >= min(self.policy.max_backup_switches, len(backup_account_ids)):
            state.failed = True
            state.events.append("BACKUP_EXHAUSTED")
            return {"status": "FAILED", "account_id": state.active_account_id or state.account_id, "events": state.events}

        next_backup = backup_account_ids[state.backup_switches]
        state.backup_switches += 1
        state.attempts = 0
        old = state.active_account_id or state.account_id
        result = self.executor.switch_account(old, next_backup)
        if not result.get("success"):
            state.events.append(f"BACKUP_SWITCH_FAILED_{next_backup}")
            return {"status": "RETRY_SWITCH", "account_id": old, "backup_account_id": next_backup, "events": state.events}
        state.active_account_id = next_backup
        state.events.append(f"SWITCH_BACKUP_{next_backup}")
        return {"status": "SWITCHED_BACKUP", "account_id": next_backup, "events": state.events}
