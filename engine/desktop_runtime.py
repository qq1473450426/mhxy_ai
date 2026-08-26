"""单账号桌面联调 Runtime。

第一阶段只提供安全的观察/状态循环与 dry-run 动作接口，不执行游戏反作弊或检测规避。
实际桌面适配器可注入 screenshot_provider、perception、interactor。
"""
from __future__ import annotations
from dataclasses import dataclass, field
from time import monotonic
from typing import Any, Callable

from .state_machine import RuntimeStateMachine
from .skills.runner import SkillRunner

@dataclass
class DesktopObservation:
    state: str = "STARTING"
    confidence: float = 0.0
    data: dict[str, Any] = field(default_factory=dict)

@dataclass
class RuntimeEvent:
    account_id: int
    state: str
    action: str
    confidence: float
    message: str
    timestamp: float

class DesktopRuntime:
    """一个账号一个 Runtime；依赖可替换，方便单账号桌面测试。"""
    def __init__(self, account_id: int, screenshot_provider: Callable[[], Any] | None = None,
                 perception: Callable[[Any], DesktopObservation] | None = None,
                 interactor: Any | None = None, min_confidence: float = 0.72):
        self.account_id = account_id
        self.screenshot_provider = screenshot_provider
        self.perception = perception
        self.interactor = interactor
        self.state_machine = RuntimeStateMachine(min_confidence=min_confidence)
        self.skill_runner = SkillRunner(account_id)
        self.running = False
        self.paused = False
        self.last_observation: DesktopObservation | None = None
        self.events: list[RuntimeEvent] = []

    def observe_once(self) -> DesktopObservation:
        if self.screenshot_provider is None or self.perception is None:
            obs = DesktopObservation(self.state_machine.state.value, 0.0, {"mode": "no_adapter"})
        else:
            frame = self.screenshot_provider()
            obs = self.perception(frame)
        self.last_observation = obs
        transition = self.state_machine.next({"state": obs.state, "confidence": obs.confidence, **obs.data})
        self._event(transition.action, obs.confidence, transition.message)
        return obs

    def step(self) -> RuntimeEvent:
        obs = self.observe_once()
        action = self.state_machine.next({"state": obs.state, "confidence": obs.confidence}).action
        self._event(action, obs.confidence, "dry-run：等待桌面适配器动作")
        return self.events[-1]

    def run_once(self) -> RuntimeEvent:
        if not self.running:
            self.running = True
        if self.paused:
            return self._event("PAUSED", 1.0, "Runtime 已暂停")
        return self.step()

    def stop(self) -> None:
        self.running = False
        self.paused = False
        self._event("STOP", 1.0, "Runtime 已停止")

    def pause(self) -> None:
        self.paused = True
        self._event("PAUSE", 1.0, "Runtime 已暂停")

    def resume(self) -> None:
        self.paused = False
        self._event("RESUME", 1.0, "Runtime 已恢复")

    def _event(self, action: str, confidence: float, message: str) -> RuntimeEvent:
        event = RuntimeEvent(self.account_id, self.state_machine.state.value, action, confidence, message, monotonic())
        self.events.append(event)
        if len(self.events) > 200:
            self.events = self.events[-200:]
        return event

    def snapshot(self) -> dict[str, Any]:
        obs = self.last_observation
        return {
            "account_id": self.account_id,
            "running": self.running,
            "paused": self.paused,
            "state": self.state_machine.state.value,
            "confidence": obs.confidence if obs else 0.0,
            "observation": obs.data if obs else {},
            "last_event": self.events[-1].__dict__ if self.events else None,
        }
