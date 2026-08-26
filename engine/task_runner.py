import time
from pathlib import Path
from dashboard.models import Account, Worker, Log
from .state_machine import RuntimeStateMachine, State
from .skills import SkillStore
from .leveling import NewServerLevelingStrategy, candidates_from_mapping
from .automation import AutomationEngine
from .window_manager import find_window, launch_game


class TaskRunner:
    """任务执行框架。

    默认 DRY_RUN=True，只做识别/状态流转，不执行真实点击。
    新区快速练级属于策略层：先选择任务，再由现有执行层负责实际动作。
    """

    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.sm = RuntimeStateMachine()
        self.skills = SkillStore(Path('skills'))
        self.io = AutomationEngine(dry_run=dry_run)
        self.leveling = NewServerLevelingStrategy()

    def run_once(self, account_id, task='daily'):
        account = Account.objects.get(pk=account_id)
        worker, _ = Worker.objects.get_or_create(account=account)
        self._set(worker, 'TASK', task, 0, '任务开始')
        self._log(account, 'TASK_START', f'任务={task}')
        info = find_window(account.hwnd, account.window_title)
        if not info:
            self._set(worker, 'DISCONNECTED', task, 0, '找不到游戏窗口')
            self._log(account, 'WINDOW_MISSING', '未找到游戏窗口', 'WARN')
            return False
        self._set(worker, 'NAVIGATING', task, 20, '等待 Skill 路线')
        route = self.skills.search(task)
        if not route:
            self._set(worker, 'IDLE', task, 20, '没有匹配 Skill，等待配置')
            self._log(account, 'SKILL_MISSING', f'没有找到 Skill: {task}', 'WARN')
            return False
        self._set(worker, 'BATTLE', task, 60, '进入战斗状态机')
        self._set(worker, 'TASK', task, 90, '任务收尾')
        self._set(worker, 'IDLE', task, 100, '任务完成')
        self._log(account, 'TASK_DONE', f'任务完成: {task}')
        return True

    def select_leveling_task(self, level, candidates, target_level=69, weights=None):
        """根据新区练级策略选择下一任务。

        candidates 可直接使用 LevelingCandidate 列表，也可传入字典列表。
        返回包含 task/stage/score/reason 的决策对象。
        """
        normalized = candidates_from_mapping(candidates) if isinstance(candidates, list) and (not candidates or isinstance(candidates[0], dict)) else candidates
        return self.leveling.choose(
            level=level,
            candidates=normalized,
            target_level=target_level,
            weights=weights,
        )

    def recommended_leveling_order(self, level):
        """返回当前等级阶段的默认任务优先级。"""
        return self.leveling.priority_order(level)

    def _set(self, w, state, task, progress, message):
        w.state = state
        w.task = task
        w.progress = progress
        w.message = message
        w.current_action = message
        w.save()

    def _log(self, a, event, message, level='INFO'):
        Log.objects.create(account=a, level=level, event=event, message=message)
