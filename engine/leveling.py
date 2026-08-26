"""梦幻西游新区快速练级策略。

该模块只负责根据角色状态选择下一类练级任务，不直接操作鼠标键盘。
实际执行仍由 TaskRunner / AutomationEngine 负责。
"""
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LevelingCandidate:
    """候选任务及其估算指标。"""

    name: str
    estimated_exp: float = 0.0
    estimated_travel_seconds: float = 0.0
    failure_risk: float = 0.0
    repeatability: float = 0.0
    unlock_value: float = 0.0
    available: bool = True


@dataclass(frozen=True)
class LevelingDecision:
    """练级策略选择结果。"""

    task: str
    stage: str
    score: float
    reason: str


class NewServerLevelingStrategy:
    """新区冲级的确定性策略层。

    输入可以来自 OCR、游戏状态识别或 Dashboard；本类不会自行假设游戏内部状态。
    """

    DEFAULT_WEIGHTS = {
        "exp": 1.0,
        "travel": 0.25,
        "failure": 2.0,
        "repeat": 1.5,
        "unlock": 2.0,
    }

    STAGES = (
        (0, 19, "0-19 新手阶段"),
        (20, 29, "20-29 主线师门"),
        (30, 39, "30-39 稳定刷经验"),
        (40, 49, "40-49 提高单位时间经验"),
        (50, 59, "50-59 冲60"),
        (60, 68, "60-68 冲69"),
        (69, 999, "69级卡级"),
    )

    def stage_for_level(self, level: int) -> str:
        level = max(0, int(level))
        for low, high, stage in self.STAGES:
            if low <= level <= high:
                return stage
        return "未知阶段"

    def priority_order(self, level: int) -> list[str]:
        """返回当前等级对应的默认任务优先级。"""
        level = max(0, int(level))
        if level < 20:
            return ["主线", "新手任务", "师门", "活动"]
        if level < 30:
            return ["主线", "师门", "活动"]
        if level < 40:
            return ["抓鬼", "师门", "副本", "活动", "主线"]
        if level < 60:
            return ["抓鬼", "副本", "活动", "师门", "主线"]
        if level < 69:
            return ["抓鬼", "副本", "活动", "师门", "经验任务"]
        return []

    def _score(self, candidate: LevelingCandidate, weights: dict[str, float]) -> float:
        return (
            weights["exp"] * candidate.estimated_exp
            - weights["travel"] * candidate.estimated_travel_seconds
            - weights["failure"] * candidate.failure_risk
            + weights["repeat"] * candidate.repeatability
            + weights["unlock"] * candidate.unlock_value
        )

    def choose(
        self,
        level: int,
        candidates: list[LevelingCandidate],
        target_level: int = 69,
        weights: dict[str, float] | None = None,
    ) -> LevelingDecision:
        """从可用候选任务中选择当前最优任务。"""
        level = max(0, int(level))
        target_level = max(1, int(target_level))
        stage = self.stage_for_level(level)

        if level >= target_level:
            return LevelingDecision(
                task="STOP",
                stage=stage,
                score=0.0,
                reason=f"已达到目标等级 {target_level}，停止自动冲级。",
            )

        available = [c for c in candidates if c.available]
        if not available:
            return LevelingDecision(
                task="IDLE",
                stage=stage,
                score=0.0,
                reason="没有满足前置条件的练级任务，保持安全待机。",
            )

        selected_weights = dict(self.DEFAULT_WEIGHTS)
        if weights:
            selected_weights.update(weights)

        ranked = sorted(
            ((self._score(c, selected_weights), c) for c in available),
            key=lambda item: item[0],
            reverse=True,
        )
        score, selected = ranked[0]
        return LevelingDecision(
            task=selected.name,
            stage=stage,
            score=round(score, 2),
            reason=(
                f"{stage}：综合经验收益、移动成本、失败风险和连续执行能力，"
                f"选择【{selected.name}】。"
            ),
        )


def candidates_from_mapping(data: list[dict[str, Any]]) -> list[LevelingCandidate]:
    """将 API / OCR 层传来的字典转换为候选任务。"""
    result: list[LevelingCandidate] = []
    for item in data:
        if not isinstance(item, dict) or not item.get("name"):
            continue
        result.append(
            LevelingCandidate(
                name=str(item["name"]),
                estimated_exp=float(item.get("estimated_exp", 0) or 0),
                estimated_travel_seconds=float(item.get("estimated_travel_seconds", 0) or 0),
                failure_risk=float(item.get("failure_risk", 0) or 0),
                repeatability=float(item.get("repeatability", 0) or 0),
                unlock_value=float(item.get("unlock_value", 0) or 0),
                available=bool(item.get("available", True)),
            )
        )
    return result
