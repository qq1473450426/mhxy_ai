"""视觉目标驱动的 GUI 交互层。

原则：先识别目标，再在目标区域内移动/点击，并通过后续画面确认结果。
不包含任何反作弊、风控或检测规避逻辑。
"""
from __future__ import annotations
from dataclasses import dataclass
import random
import time
from typing import Callable

from .automation import AutomationEngine

@dataclass
class ClickTarget:
    name: str
    rect: tuple[int, int, int, int]
    confidence: float = 1.0

class HumanLikeInteractor:
    def __init__(self, dry_run: bool = True):
        self.engine = AutomationEngine(dry_run=dry_run)

    def click_target(self, target: ClickTarget, verify: Callable[[], bool] | None = None, timeout: float = 2.5) -> bool:
        x, y, w, h = target.rect
        if w <= 0 or h <= 0 or target.confidence <= 0:
            return False
        px = int(x + w * random.uniform(0.35, 0.65))
        py = int(y + h * random.uniform(0.35, 0.65))
        self.engine.move_mouse(px, py, duration=random.uniform(0.10, 0.28))
        time.sleep(random.uniform(0.08, 0.22))
        self.engine.click(px, py)
        if verify is None:
            return True
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if verify():
                return True
            time.sleep(0.12)
        return False

    def safe_click(self, locate: Callable[[], ClickTarget | None], verify: Callable[[], bool] | None = None, retries: int = 2) -> bool:
        for _ in range(max(1, retries + 1)):
            target = locate()
            if target and self.click_target(target, verify):
                return True
            time.sleep(random.uniform(0.15, 0.35))
        return False
