"""新区日常运营调度器。

把“练级/师门/抓鬼/副本/活动”等运营任务统一成可配置的日程项。
本模块只做决策，不直接点击游戏；真实执行仍由 TaskRunner/Executor 负责。
"""
from dataclasses import dataclass, field
from datetime import datetime, time
from typing import Any


@dataclass(frozen=True)
class OperationTask:
    name: str
    skill: str
    daily_limit: int = 0
    min_level: int = 0
    max_level: int | None = None
    duration_minutes: int = 0
    priority: int = 50
    start_time: time | None = None
    end_time: time | None = None
    requires_team: bool = False
    requires_leader: bool = False
    enabled: bool = True

    def available(self, level: int, completed: int, now: time, team_ready: bool) -> bool:
        if not self.enabled or level < self.min_level:
            return False
        if self.max_level is not None and level > self.max_level:
            return False
        if self.daily_limit and completed >= self.daily_limit:
            return False
        if self.requires_team and not team_ready:
            return False
        if self.start_time is not None and self.end_time is not None:
            if self.start_time <= self.end_time:
                if not (self.start_time <= now <= self.end_time):
                    return False
            elif not (now >= self.start_time or now <= self.end_time):
                return False
        return True


@dataclass
class DailyProgress:
    date: str
    completed: dict[str, int] = field(default_factory=dict)

    def count(self, task_name: str) -> int:
        return int(self.completed.get(task_name, 0) or 0)

    def record(self, task_name: str, amount: int = 1) -> None:
        self.completed[task_name] = self.count(task_name) + max(0, amount)


DEFAULT_NEW_SERVER_SCHEDULE: tuple[OperationTask, ...] = (
    OperationTask("副本三连", "operations/daily_dungeons", daily_limit=1, min_level=30, duration_minutes=60, priority=100, requires_team=True),
    OperationTask("师门", "operations/teacher_mission", daily_limit=20, min_level=20, duration_minutes=30, priority=95, requires_team=False),
    OperationTask("抓鬼", "operations/ghost_hunting", daily_limit=30, min_level=40, duration_minutes=90, priority=90, requires_team=True),
    OperationTask("新区练级", "leveling/new_server_fast_leveling", min_level=0, max_level=68, duration_minutes=30, priority=80),
    OperationTask("周末活动", "operations/weekend_event", daily_limit=1, min_level=30, duration_minutes=90, priority=85, requires_team=True, start_time=time(12, 0), end_time=time(23, 0)),
)


class NewServerDailyScheduler:
    """根据等级、次数、时间和队伍状态选择下一项日常任务。"""

    def __init__(self, tasks: tuple[OperationTask, ...] = DEFAULT_NEW_SERVER_SCHEDULE):
        self.tasks = tasks

    def choose(self, level: int, progress: DailyProgress, now: datetime | None = None, team_ready: bool = True) -> OperationTask | None:
        current = now or datetime.now()
        candidates = [
            task for task in self.tasks
            if task.available(level, progress.count(task.name), current.time(), team_ready)
        ]
        if not candidates:
            return None
        # 优先级为主，剩余次数越多越优先；相同条件下用时更短的先做。
        return max(candidates, key=lambda task: (task.priority, -task.duration_minutes, task.daily_limit == 0))

    def snapshot(self, level: int, progress: DailyProgress, now: datetime | None = None, team_ready: bool = True) -> list[dict[str, Any]]:
        current = now or datetime.now()
        rows = []
        for task in self.tasks:
            count = progress.count(task.name)
            rows.append({
                "name": task.name,
                "skill": task.skill,
                "completed": count,
                "limit": task.daily_limit,
                "available": task.available(level, count, current.time(), team_ready),
                "priority": task.priority,
            })
        return rows
