"""梦幻西游桌面画面感知层。

本模块只负责“看”：截图、模板匹配、可选 OCR 和基础状态推断。
不负责点击，也不决定任务策略。模板路径和 OCR 区域需要根据实际客户端截图标定。
不包含反作弊、风控或检测规避逻辑。
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
except ImportError:  # pragma: no cover
    pytesseract = None


@dataclass
class PerceptionConfig:
    """相对于游戏窗口左上角的感知配置。"""

    level_region: tuple[int, int, int, int] | None = None
    exp_region: tuple[int, int, int, int] | None = None
    map_region: tuple[int, int, int, int] | None = None
    state_region: tuple[int, int, int, int] | None = None
    templates: dict[str, str] = field(default_factory=dict)
    ocr_lang: str = "chi_sim+eng"
    template_threshold: float = 0.88


@dataclass
class StateCandidate:
    state: str
    confidence: float
    source: str
    evidence: list[str] = field(default_factory=list)


class ScreenLevelingObserver:
    """从真实游戏窗口截图生成统一 observation。

    没有实际客户端模板时会保守返回 UNKNOWN，而不是猜测主界面。
    """

    TEMPLATE_STATES = {
        "login": "LOGIN",
        "character_select": "CHARACTER_SELECT",
        "loading": "LOADING",
        "main_game": "MAIN_GAME",
        "dialog": "DIALOG",
        "story": "STORY",
        "battle": "BATTLE",
        "battle_result": "BATTLE_RESULT",
        "disconnected": "DISCONNECTED",
        "error": "ERROR",
    }

    OCR_KEYWORDS = {
        "DISCONNECTED": ("掉线", "重新连接", "连接失败", "网络异常"),
        "CHARACTER_SELECT": ("角色选择", "选择角色", "创建角色"),
        "LOGIN": ("账号", "密码", "登录", "进入游戏"),
        "BATTLE_RESULT": ("战斗胜利", "战斗失败", "战斗结束", "获得经验"),
        "BATTLE": ("自动", "防御", "逃跑", "法术", "攻击"),
        "DIALOG": ("确定", "取消", "下一步"),
        "STORY": ("跳过", "下一步", "剧情"),
        "MAIN_GAME": ("任务", "背包", "技能", "队伍"),
    }

    PRIORITY = (
        "DISCONNECTED", "ERROR", "CHARACTER_SELECT", "LOGIN", "BATTLE_RESULT",
        "BATTLE", "STORY", "DIALOG", "MAIN_GAME", "LOADING",
    )

    def __init__(self, hwnd=None, window_title="梦幻西游", config: PerceptionConfig | None = None, dry_run=True):
        self.hwnd = hwnd
        self.window_title = window_title
        self.config = config or PerceptionConfig()
        self.engine = AutomationEngine(dry_run=dry_run, threshold=self.config.template_threshold)

    def observe(self) -> dict[str, Any]:
        info = find_window(self.hwnd, self.window_title)
        if not info:
            return {
                "window_available": False,
                "state": "DISCONNECTED",
                "confidence": 0.98,
                "candidates": [{"state": "DISCONNECTED", "confidence": 0.98, "source": "window"}],
            }

        frame = self.engine.capture(info.rect)
        if frame is None:
            return {
                "window_available": True,
                "state": "ERROR",
                "confidence": 0.95,
                "hwnd": info.hwnd,
                "window_rect": info.rect,
                "candidates": [{"state": "ERROR", "confidence": 0.95, "source": "capture"}],
            }

        templates = self._detect_templates(frame)
        ocr_text = self._ocr_region(frame, self.config.state_region, self.config.ocr_lang)
        candidates = self._build_candidates(templates, ocr_text)
        best = max(candidates, key=lambda item: item.confidence) if candidates else None

        result: dict[str, Any] = {
            "window_available": True,
            "hwnd": info.hwnd,
            "window_rect": info.rect,
            "state": best.state if best else "UNKNOWN",
            "confidence": best.confidence if best else 0.0,
            "detector": best.source if best else "none",
            "candidates": [c.__dict__ for c in candidates],
            "ocr_text": ocr_text,
            "template_matches": templates,
            "level": 0,
            "level_known": False,
            "exp_percent": 0,
            "map_name": "",
        }

        level_text = self._ocr_region(frame, self.config.level_region, self.config.ocr_lang)
        level = self._parse_level(level_text)
        if level is not None:
            result["level"] = level
            result["level_known"] = True

        exp = self._parse_percent(self._ocr_region(frame, self.config.exp_region, self.config.ocr_lang))
        if exp is not None:
            result["exp_percent"] = exp

        map_text = self._ocr_region(frame, self.config.map_region, self.config.ocr_lang)
        if map_text:
            result["map_name"] = map_text.strip()

        return result

    def _detect_templates(self, frame) -> dict[str, Any]:
        matches: dict[str, Any] = {}
        for name, path in self.config.templates.items():
            matches[name] = self.engine.find_template(frame, Path(path))
        return matches

    def _build_candidates(self, templates: dict[str, Any], ocr_text: str) -> list[StateCandidate]:
        candidates: list[StateCandidate] = []
        for name, state in self.TEMPLATE_STATES.items():
            hit = templates.get(name)
            if hit:
                candidates.append(StateCandidate(state, float(hit.get("score", 0.0)), "template", [name]))

        normalized = re.sub(r"\s+", "", ocr_text or "")
        for state in self.PRIORITY:
            matched = [word for word in self.OCR_KEYWORDS.get(state, ()) if word in normalized]
            if matched:
                confidence = min(0.94, 0.70 + 0.08 * (len(matched) - 1))
                candidates.append(StateCandidate(state, confidence, "ocr", matched))
        return candidates

    @staticmethod
    def _ocr_region(frame, region, lang):
        if pytesseract is None or not region or frame is None:
            return ""
        x, y, w, h = region
        crop = frame[max(0, y):max(0, y) + h, max(0, x):max(0, x) + w]
        if crop.size == 0:
            return ""
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        try:
            return pytesseract.image_to_string(binary, lang=lang, config="--psm 7").strip()
        except Exception:
            return ""

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

    def observe_frame(self, frame: np.ndarray, window_rect: tuple[int, int, int, int] | None = None) -> dict[str, Any]:
        """供 WebUI/测试直接分析已经获取的截图。"""
        templates = self._detect_templates(frame)
        text = self._ocr_region(frame, self.config.state_region, self.config.ocr_lang)
        candidates = self._build_candidates(templates, text)
        best = max(candidates, key=lambda item: item.confidence) if candidates else None
        return {
            "state": best.state if best else "UNKNOWN",
            "confidence": best.confidence if best else 0.0,
            "detector": best.source if best else "none",
            "candidates": [c.__dict__ for c in candidates],
            "ocr_text": text,
            "template_matches": templates,
            "window_rect": window_rect,
        }
