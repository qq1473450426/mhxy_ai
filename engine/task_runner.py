from pathlib import Path
from dashboard.models import Account, Worker, Log
from .state_machine import RuntimeStateMachine
from .skills import SkillStore
from .leveling import NewServerLevelingStrategy, candidates_from_mapping
from .automation import AutomationEngine
from .window_manager import find_window


class TaskRunner:
    """任务执行框架。

    重要：没有真实 Skill 执行器时绝不伪造“任务完成”。
    dry_run=True 只生成计划；真实执行必须由具体 Skill/Executor 完成并验证。
    """

    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.sm = RuntimeStateMachine()
        self.skills = SkillStore(Path("skills"))
        self.io = AutomationEngine(dry_run=dry_run)
        self.leveling = NewServerLevelingStrategy()

    def run_once(self, account_id, task="daily"):
        account = Account.objects.get(pk=account_id)
        worker, _ = Worker.objects.get_or_create(account=account)
        self._set(worker, "TASK", task, 0, "任务开始")
        self._log(account, "TASK_START", f"任务={task}")

        info = find_window(account.hwnd, account.window_title)
        if not info:
            self._set(worker, "DISCONNECTED", task, 0, "找不到游戏窗口")
            self._log(account, "WINDOW_MISSING", "未找到游戏窗口", "WARN")
            return False

        route = self.skills.search(task)
        if not route:
            self._set(worker, "IDLE", task, 0, "没有匹配 Skill，等待配置")
            self._log(account, "SKILL_MISSING", f"没有找到 Skill: {task}", "WARN")
            return False

        if self.dry_run:
            self._set(worker, "NAVIGATING", task, 10, "DRY_RUN：已找到 Skill，等待执行器")
            self._log(account, "DRY_RUN_PLAN", f"任务={task}，Skill={route}")
            return True

        # 这里不能用占位状态伪造完成；必须由具体 Task Executor 返回 verified=True。
        self._set(worker, "TASK", task, 0, "缺少具体 Task Executor，未执行")
        self._log(account, "EXECUTOR_MISSING", f"任务={task} 尚未绑定可验证执行器", "WARN")
        return False

    def select_leveling_task(self, level, candidates, target_level=69, weights=None):
        normalized = (
            candidates_from_mapping(candidates)
            if isinstance(candidates, list) and (not candidates or isinstance(candidates[0], dict))
            else candidates
        )
        return self.leveling.choose(
            level=level,
            candidates=normalized,
            target_level=target_level,
            weights=weights,
        )

    def recommended_leveling_order(self, level):
        return self.leveling.priority_order(level)

    def _set(self, worker, state, task, progress, message):
        worker.state = state
        worker.task = task
        worker.progress = progress
        worker.message = message
        worker.current_action = message
        worker.save()

    def _log(self, account, event, message, level="INFO"):
        Log.objects.create(account=account, level=level, event=event, message=message)
