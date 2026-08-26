"""Windows 屏幕自动化基础层。

默认 dry_run=True，只记录动作，不执行真实输入。
所有坐标默认使用“游戏窗口相对坐标”，由上层提供窗口矩形。
"""
import time

import cv2
import numpy as np
from PIL import ImageGrab
import pyautogui


class AutomationEngine:
    def __init__(self, dry_run=True, threshold=0.88):
        self.dry_run = dry_run
        self.threshold = threshold

    def capture(self, rect):
        if not rect:
            return None
        return cv2.cvtColor(np.array(ImageGrab.grab(bbox=rect)), cv2.COLOR_RGB2BGR)

    def find_template(self, frame, path, threshold=None):
        tpl = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
        if frame is None or tpl is None:
            return None
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        r = cv2.matchTemplate(gray, tpl, cv2.TM_CCOEFF_NORMED)
        _, score, _, loc = cv2.minMaxLoc(r)
        th = self.threshold if threshold is None else threshold
        if score < th:
            return None
        h, w = tpl.shape[:2]
        return {"x": loc[0] + w // 2, "y": loc[1] + h // 2, "score": float(score)}

    def click(self, x, y):
        if self.dry_run:
            return {"executed": False, "action": "click", "x": x, "y": y}
        pyautogui.click(x, y)
        return {"executed": True, "action": "click", "x": x, "y": y}

    def press(self, key):
        if self.dry_run:
            return {"executed": False, "action": "press", "key": key}
        pyautogui.press(key)
        return {"executed": True, "action": "press", "key": key}

    def move_to(self, x, y, observation=None):
        """移动到游戏窗口内的相对坐标。

        当前采用点击移动点的方式；实际客户端是否支持该交互需要用真实截图验证。
        dry_run 下只返回计划动作，不点击。
        """
        rect = (observation or {}).get("window_rect")
        if not rect or len(rect) != 4:
            return {"completed": False, "retryable": True, "reason": "缺少游戏窗口矩形"}
        left, top, right, bottom = rect
        screen_x, screen_y = left + int(x), top + int(y)
        if not (left <= screen_x <= right and top <= screen_y <= bottom):
            return {"completed": False, "retryable": False, "reason": "目标坐标超出游戏窗口"}
        result = self.click(screen_x, screen_y)
        return {
            "completed": self.dry_run,
            "retryable": False,
            "executed": result["executed"],
            "screen_x": screen_x,
            "screen_y": screen_y,
        }

    def wait(self, seconds):
        time.sleep(seconds)
