"""新区经营/收益决策层。

把“练级效率”和“经营收益”分开：任务执行器负责执行，EconomyPlanner 负责比较
经验、产出、时间和风险，避免把截图中的收益数字硬编码成保证收益。
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ActivityProfile:
    name: str
    expected_value: float = 0.0
    expected_exp: float = 0.0
    minutes: float = 1.0
    risk: float = 0.0
    repeatability: float = 1.0
    prerequisites: tuple[str, ...] = ()

    @property
    def value_per_hour(self) -> float:
        if self.minutes <= 0:
            return 0.0
        return self.expected_value * 60.0 / self.minutes

    @property
    def exp_per_hour(self) -> float:
        if self.minutes <= 0:
            return 0.0
        return self.expected_exp * 60.0 / self.minutes


class EconomyPlanner:
    """根据目标选择活动，不承诺截图中的固定收益。"""

    def rank(self, activities, mode="balanced", max_risk=10.0):
        profiles = [a for a in activities if a.risk <= max_risk]
        if mode == "profit":
            key = lambda a: (a.value_per_hour, a.repeatability, -a.risk)
        elif mode == "exp":
            key = lambda a: (a.exp_per_hour, a.repeatability, -a.risk)
        else:
            key = lambda a: (a.value_per_hour * 0.6 + a.exp_per_hour * 0.4, a.repeatability, -a.risk)
        return sorted(profiles, key=key, reverse=True)

    def choose(self, activities, mode="balanced", max_risk=10.0):
        ranked = self.rank(activities, mode=mode, max_risk=max_risk)
        if not ranked:
            return None
        selected = ranked[0]
        return {
            "activity": selected.name,
            "mode": mode,
            "value_per_hour": round(selected.value_per_hour, 2),
            "exp_per_hour": round(selected.exp_per_hour, 2),
            "risk": selected.risk,
            "reason": "按当前输入的单位时间收益/经验与风险排序，不代表固定实际收益",
        }


DEFAULT_NEW_SERVER_ACTIVITIES = (
    ActivityProfile("抓鬼", expected_exp=9000, minutes=30, repeatability=10),
    ActivityProfile("师门", expected_value=5000, expected_exp=5000, minutes=20, repeatability=8),
    ActivityProfile("副本三连", expected_value=100000, expected_exp=30000, minutes=60, repeatability=6),
    ActivityProfile("周末活动", expected_value=200000, expected_exp=50000, minutes=120, repeatability=4),
    ActivityProfile("活力变现", expected_value=30000, minutes=30, repeatability=5),
)
