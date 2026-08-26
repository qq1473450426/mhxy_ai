"""梦幻西游基础导航层。

导航层只负责把“当前位置/目标位置”转换为可执行的移动步骤。
不绑定具体任务，也不绕过游戏客户端接口；实际输入由 AutomationEngine 执行。
"""
from dataclasses import dataclass
from math import hypot
from typing import Any


@dataclass(frozen=True)
class MapPoint:
    name: str
    x: int
    y: int


@dataclass(frozen=True)
class RouteStep:
    action: str
    target: MapPoint
    tolerance: int = 30


class NavigationPlanner:
    """基于 Skill 路点的简单路线规划器。

    当前采用直线距离 + 路点顺序，不假设游戏内部寻路 API。
    后续可替换为 A* / 可通行区域规划，而不影响上层 Task。
    """

    def __init__(self, routes: dict[str, list[MapPoint]] | None = None):
        self.routes = routes or {}

    def plan(self, route_name: str, current: MapPoint | None = None) -> list[RouteStep]:
        points = list(self.routes.get(route_name, []))
        if not points:
            return []
        if current is not None:
            points = self._skip_reached(points, current)
        return [RouteStep("MOVE", point) for point in points]

    @staticmethod
    def reached(current: MapPoint, target: MapPoint, tolerance: int = 30) -> bool:
        return current.name == target.name and hypot(current.x - target.x, current.y - target.y) <= tolerance

    @staticmethod
    def _skip_reached(points: list[MapPoint], current: MapPoint) -> list[MapPoint]:
        for index, point in enumerate(points):
            if point.name == current.name:
                return points[index:]
        return points


class NavigationExecutor:
    """将导航步骤交给注入的动作执行器。"""

    def __init__(self, action_executor):
        self.action_executor = action_executor

    def execute(self, step: RouteStep, observation: dict[str, Any]) -> dict[str, Any]:
        if step.action != "MOVE":
            return {"completed": False, "retryable": False, "reason": "未知导航动作"}
        result = self.action_executor.move_to(step.target.x, step.target.y, observation)
        return result if isinstance(result, dict) else {"completed": bool(result), "retryable": not bool(result)}
