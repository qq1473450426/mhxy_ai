"""梦幻西游画面感知层。

本模块只负责“看”：截图、模板匹配、可选 OCR 和基础状态推断。
不负责点击，也不决定做哪个任务。

OCR 采用可选依赖 pytesseract；没有安装 OCR 引擎时，模板识别仍可正常工作。
建议后续针对实际客户端截图建立 skills/perception/templates/ 模板库。
"""
from dataclasses import dataclass, field
from pathlib import Path
import re
from typing import Any

import cv2
import numpy as np

from .automation import AutomationEngine
from .window_manager import find_window

try:
    import pytesseract
except ImportError:  # pragma: no cover - 可选依赖
    pytesseract = None


@dataclass
class PerceptionConfig:
    """相对于游戏窗口左上角的感知区域。"""

    level_region: tuple[int, int, int, int] | None = None
    exp_region: tuple[int, int, int, int] | None = None
    map_region: tuple[int, int, int, int] | None = None
    state_region: tuple[int, int, int, int] | None = None
    templates: dict[str, str] = field(default_factory=dict)
    ocr_lang: str = "chi_sim+eng"


class ScreenLevelingObserver:
    """基于游戏窗口截图的练级状态观察器。

    默认只读，不会执行任何输入操作。区域坐标必须通过实际客户端截图标定。
    """

    def __init__(self, hwnd=None, window_title="梦幻西游", config: PerceptionConfig | None = None, dry_run=True):
        self.hwnd = hwnd
        self.window_title = window_title
        self.config = config or PerceptionConfig()
        self.engine = AutomationEngine(dry_run=dry_run)

    def observe(self) -> dict[str, Any]:
        info = find_window(self.hwnd, self.window_title)
        if not info:
            return {"window_available": False, "level_known": False, "state": "DISCONNECTED", "candidates": []}

        frame = self.engine.capture(info.rect)
        if frame is None:
            return {"window_available": True, "level_known": False, "state": "ERROR", "candidates": []}

        result: dict[str, Any] = {
            "window_available": True,
            "level_known": False,
            "state": "IDLE",
            "hwnd": info.hwnd,
            "window_rect": info.rect,
            "level": 0,
            "exp_percent": 0,
            "map_name": "",
            "candidates": [],
        }
        level_text = self._ocr_region(frame, info.rect, self.config.level_region)
        level = self._parse_level(level_text)
        if level is not None:
            result["level"] = level
            result["level_known"] = True

        exp_text = self._ocr_region(frame, info.rect, self.config.exp_region)
        exp = self._parse_percent(exp_text)
        if exp is not None:
            result["exp_percent"] = exp

        map_text = self._ocr_region(frame, info.rect, self.config.map_region)
        if map_text:
            result["map_name"] = map_text.strip()

        result.update(self._detect_templates(frame))
        return result

    def _ocr_region(self, frame, window_rect, region):
        if pytesseract is None or not region:
            return ""
        x, y, w, h = region
        left, top, _, _ = window_rect
        crop = frame[max(0, y):max(0, y) + h, max(0, x):max(0, x) + w]
        if crop.size == 0:
            return ""
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        try:
            return pytesseract.image_to_string(binary, lang=self.config.ocr_lang, config="--psm 7").strip()
        except Exception:
            return ""

    def _detect_templates(self, frame) -> dict[str, Any]:
        state = "IDLE"
        matches = {}
        for name, path in self.config.templates.items():
            hit = self.engine.find_template(frame, Path(path))
            matches[name] = hit
        if matches.get("battle"):
            state = "BATTLE"
        elif matches.get("error"):
            state = "ERROR"
        elif matches.get("task_complete"):
            state = "TASK"
        return {"state": state, "template_matches": matches}

    @staticmethod
    def _parse_level(text: str) -> int | None:
        match = re.search(r"(?:等级|级|Lv|LV)\s*[:：]?\s*(\d{1,3})", text or "")
        if match:
            return int(match.group(1))
        numbers = re.findall(r"\b(\d{1,3})\b", text or "")
        return int(numbers[0]) if len(numbers) == 1 and 0 <= int(numbers[0]) <= 175 else None

    @staticmethod
    def _parse_percent(text: str) -> int | None:
        match = re.search(r"(\d{1,3})\s*%", text or "")
        if not match:
            return None
        return max(0, min(100, int(match.group(1))))
