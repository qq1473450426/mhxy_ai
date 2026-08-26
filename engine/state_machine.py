"""运行时状态机。

感知层只提交 observation；状态机负责确定当前阶段与允许的下一步动作。
不包含反作弊、风控或检测规避逻辑。
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from time import monotonic


class State(str, Enum):
    STOPPED = "STOPPED"
    STARTING = "STARTING"
    LOGIN = "LOGIN"
    CHARACTER_SELECT = "CHARACTER_SELECT"
    STORY = "STORY"
    IDLE = "IDLE"
    TASK = "TASK"
    NAVIGATING = "NAVIGATING"
    BATTLE = "BATTLE"
    BATTLE_RESULT = "BATTLE_RESULT"
    DISCONNECTED = "DISCONNECTED"
    RECONNECTING = "RECONNECTING"
    ERROR = "ERROR"


@dataclass
class Transition:
    state: State
    action: str
    progress: int
    message: str
    changed: bool = False
    confidence: float = 1.0
    observed_at: float = 0.0


class RuntimeStateMachine:
    def __init__(self, min_confidence: float = 0.72):
        self.state = State.STOPPED
        self.min_confidence = min_confidence

    def next(self, observation: dict) -> Transition:
        """根据视觉/运行 observation 决定下一动作；低置信度时保持原状态。"""
        raw = observation.get("state")
        confidence = float(observation.get("confidence", 1.0))
        previous = self.state

        if raw in State._value2member_map_:
            proposed = State(raw)
            if confidence >= self.min_confidence or proposed in {State.DISCONNECTED, State.ERROR}:
                self.state = proposed

        actions = {
            State.STARTING: ("启动客户端", 0, "等待窗口"),
            State.LOGIN: ("执行登录", 5, "等待账号登录完成"),
            State.CHARACTER_SELECT: ("选择角色", 8, "按账号角色配置选择"),
            State.STORY: ("处理剧情", 12, "检测剧情界面并执行允许的跳过动作"),
            State.IDLE: ("待机", 10, "等待任务"),
            State.TASK: ("执行任务", 80, "按任务模板执行"),
            State.NAVIGATING: ("自动寻路", 30, "按导航 Skill 执行"),
            State.BATTLE: ("自动战斗", 60, "按战斗模板执行"),
            State.BATTLE_RESULT: ("处理战斗结果", 70, "确认战斗结束并收集结果"),
            State.DISCONNECTED: ("掉线处理", 0, "进入重连流程"),
            State.RECONNECTING: ("重新连接", 0, "恢复客户端并重新观察"),
            State.ERROR: ("异常停止", 0, "等待恢复或人工处理"),
            State.STOPPED: ("已停止", 0, "Worker 已停止"),
        }
        action, progress, message = actions[self.state]
        return Transition(
            self.state, action, progress, message,
            changed=previous != self.state,
            confidence=confidence,
            observed_at=monotonic(),
        )
