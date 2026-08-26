"""新区五开运营总控。

把每日调度器、队伍同步和实际 Executor 串起来。
每次 tick 只做一次决策/一次执行，便于 Worker 循环和异常恢复。
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

from .operations_scheduler import DailyProgress, NewServerDailyScheduler
from .team_coordinator import TeamCoordinator


class OperationExecutor(Protocol):
    def execute(self, skill: str, context: dict[str, Any]) -> dict[str, Any]: ...


@dataclass
class OperationTickResult:
    status: str
    task: str
    skill: str
    reason: str
    events: list[str] = field(default_factory=list)


class NewServerOperationsController:
    def __init__(self, team: TeamCoordinator, executor: OperationExecutor, target_level: int = 69):
        self.team = team
        self.executor = executor
        self.scheduler = NewServerDailyScheduler()
        self.progress = DailyProgress(date="")
        self.target_level = target_level

    def tick(self, observation: dict[str, Any] | None = None, now: datetime | None = None) -> OperationTickResult:
        observation = observation or {}
        level = int(observation.get("level", 0) or 0)
        if level < 0:
            return OperationTickResult("ERROR", "IDLE", "", "等级数据无效", ["INVALID_LEVEL"])

        team_state = self.team.evaluate()
        if team_state.status == "PAUSED":
            return OperationTickResult("PAUSED", "IDLE", "", team_state.reason, ["TEAM_PAUSED"])

        task = self.scheduler.choose(level, self.progress, now, team_ready=team_state.status == "READY")
        if task is None:
            return OperationTickResult("IDLE", "IDLE", "", "当前没有满足条件的日常任务", ["NO_TASK"])

        context = {
            "level": level,
            "team": self.team.profile.name,
            "task": task.name,
            "skill": task.skill,
            "completed": self.progress.count(task.name),
            "target_level": self.target_level,
        }
        result = self.executor.execute(task.skill, context) or {}
        if result.get("completed") is True:
            self.progress.record(task.name, int(result.get("count", 1) or 1))
            return OperationTickResult("COMPLETED", task.name, task.skill, "任务完成，下一轮重新调度。", ["TASK_STARTED", "TASK_COMPLETED"])
        if result.get("retryable") is True:
            return OperationTickResult("RETRY", task.name, task.skill, result.get("reason", "任务可重试"), ["TASK_FAILED", "RETRYABLE"])
        return OperationTickResult("ERROR", task.name, task.skill, result.get("reason", "任务未完成验证"), ["TASK_FAILED", "STOP"])
