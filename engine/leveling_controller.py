"""新区练级闭环控制器。

负责把“状态识别 → 任务决策 → 执行 → 完成验证”串起来。
具体的 OCR、地图识别、坐标和按钮模板由外部 provider 注入，避免把客户端细节硬编码到策略层。
"""
from dataclasses import dataclass, field
from typing import Any, Protocol

from .leveling import LevelingCandidate, NewServerLevelingStrategy


class LevelingObserver(Protocol):
    """游戏状态观察接口。"""

    def observe(self) -> dict[str, Any]: ...


class LevelingExecutor(Protocol):
    """游戏动作执行接口。"""

    def execute(self, task: str, observation: dict[str, Any]) -> dict[str, Any]: ...


@dataclass
class LevelingLoopResult:
    """一次闭环运行结果。"""

    status: str
    task: str
    stage: str
    reason: str
    progress: int = 0
    events: list[str] = field(default_factory=list)


class NewServerLevelingController:
    """新区 0→69 的通用闭环控制器。

    Controller 不负责猜测游戏画面，也不直接操作鼠标键盘。
    Observer 提供状态，Strategy 选择任务，Executor 执行动作并返回验证结果。
    """

    def __init__(self, observer: LevelingObserver, executor: LevelingExecutor, target_level: int = 69):
        self.observer = observer
        self.executor = executor
        self.target_level = target_level
        self.strategy = NewServerLevelingStrategy()

    def tick(self) -> LevelingLoopResult:
        """执行一个最小安全闭环，不在单次 tick 内无限重试。"""
        observation = self.observer.observe() or {}
        level = int(observation.get("level", 0) or 0)
        candidates = self._candidates(observation)

        if observation.get("window_available") is False:
            return LevelingLoopResult("DISCONNECTED", "IDLE", self.strategy.stage_for_level(level), "游戏窗口不可用。", events=["WINDOW_MISSING"])
        if observation.get("state") in {"ERROR", "DISCONNECTED"}:
            return LevelingLoopResult(str(observation["state"]), "IDLE", self.strategy.stage_for_level(level), "当前账号处于异常状态，停止自动动作。", events=["UNSAFE_STATE"])
        if observation.get("level_known") is False:
            return LevelingLoopResult("WAIT", "IDLE", self.strategy.stage_for_level(level), "无法可靠识别当前等级，等待重新识别。", events=["LEVEL_UNKNOWN"])

        decision = self.strategy.choose(level, candidates, target_level=self.target_level)
        if decision.task == "STOP":
            return LevelingLoopResult("TARGET_REACHED", decision.task, decision.stage, decision.reason, 100, ["TARGET_REACHED"])
        if decision.task == "IDLE":
            return LevelingLoopResult("WAIT", decision.task, decision.stage, decision.reason, 0, ["NO_CANDIDATE"])

        result = self.executor.execute(decision.task, observation) or {}
        if result.get("completed") is True:
            next_level = int(result.get("level", level) or level)
            progress = int(result.get("progress", observation.get("exp_percent", 0)) or 0)
            return LevelingLoopResult("COMPLETED", decision.task, decision.stage, "任务完成，下一 tick 重新识别并选择任务。", progress, ["TASK_STARTED", "TASK_COMPLETED", f"LEVEL={next_level}"])

        if result.get("retryable") is True:
            return LevelingLoopResult("RETRY", decision.task, decision.stage, result.get("reason", "任务执行失败，允许下一轮重新定位。"), 0, ["TASK_FAILED", "RETRYABLE"])

        return LevelingLoopResult("ERROR", decision.task, decision.stage, result.get("reason", "任务执行未通过完成验证。"), 0, ["TASK_FAILED", "STOP"])

    @staticmethod
    def _candidates(observation: dict[str, Any]) -> list[LevelingCandidate]:
        raw = observation.get("candidates", [])
        result: list[LevelingCandidate] = []
        for item in raw:
            if not isinstance(item, dict) or not item.get("name"):
                continue
            result.append(LevelingCandidate(
                name=str(item["name"]),
                estimated_exp=float(item.get("estimated_exp", 0) or 0),
                estimated_travel_seconds=float(item.get("estimated_travel_seconds", 0) or 0),
                failure_risk=float(item.get("failure_risk", 0) or 0),
                repeatability=float(item.get("repeatability", 0) or 0),
                unlock_value=float(item.get("unlock_value", 0) or 0),
                available=bool(item.get("available", True)),
            ))
        return result
