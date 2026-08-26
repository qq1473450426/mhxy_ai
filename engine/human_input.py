"""面向 GUI 自动化的拟人化输入层。

目标不是绕过游戏检测，而是让普通桌面自动化避免固定坐标、固定节奏和瞬时点击。
"""
from __future__ import annotations
import random
import time
from dataclasses import dataclass
from typing import Callable

try:
    import pyautogui
except ImportError:  # pragma: no cover
    pyautogui = None


@dataclass(frozen=True)
class Point:
    x: int
    y: int


class HumanInput:
    def __init__(self, move_duration=(0.12, 0.35), pause=(0.08, 0.22), jitter=3):
        self.move_duration = move_duration
        self.pause = pause
        self.jitter = jitter

    def _require(self):
        if pyautogui is None:
            raise RuntimeError("需要安装 pyautogui 才能执行桌面输入")

    def click(self, point: Point, button: str = "left", double: bool = False):
        self._require()
        x = point.x + random.randint(-self.jitter, self.jitter)
        y = point.y + random.randint(-self.jitter, self.jitter)
        duration = random.uniform(*self.move_duration)
        pyautogui.moveTo(x, y, duration=duration)
        time.sleep(random.uniform(*self.pause))
        if double:
            pyautogui.click(x, y, clicks=2, interval=random.uniform(0.08, 0.16), button=button)
        else:
            pyautogui.click(x, y, button=button)
        time.sleep(random.uniform(*self.pause))

    def click_target(self, target: tuple[int, int, int, int], **kwargs):
        left, top, right, bottom = target
        return self.click(Point(random.randint(left, right), random.randint(top, bottom)), **kwargs)

    def run_after(self, action: Callable[[], None], delay=(0.15, 0.5)):
        time.sleep(random.uniform(*delay))
        action()
