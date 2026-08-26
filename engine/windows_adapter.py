"""Windows 桌面适配器。

只负责正常 Windows 窗口管理、截图与坐标换算，不实现反作弊/风控规避。
依赖：pywin32、Pillow（安装后启用截图功能）。
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
import ctypes

try:
    import win32gui
    import win32con
except ImportError:  # 非 Windows / 未安装依赖时允许项目导入
    win32gui = None
    win32con = None

@dataclass
class WindowInfo:
    hwnd: int
    title: str
    left: int
    top: int
    right: int
    bottom: int

class WindowsWindowAdapter:
    def __init__(self, title_keywords: list[str] | None = None):
        self.title_keywords = title_keywords or ["梦幻西游"]

    def available(self) -> bool:
        return win32gui is not None

    def find_windows(self) -> list[WindowInfo]:
        if not self.available():
            return []
        result: list[WindowInfo] = []
        def callback(hwnd: int, _: Any) -> None:
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd).strip()
            if not title:
                return
            if any(k.lower() in title.lower() for k in self.title_keywords):
                l, t, r, b = win32gui.GetWindowRect(hwnd)
                result.append(WindowInfo(hwnd, title, l, t, r, b))
        win32gui.EnumWindows(callback, None)
        return result

    def get_window(self, hwnd: int) -> WindowInfo | None:
        if not self.available() or not win32gui.IsWindow(hwnd):
            return None
        title = win32gui.GetWindowText(hwnd).strip()
        l, t, r, b = win32gui.GetWindowRect(hwnd)
        return WindowInfo(hwnd, title, l, t, r, b)

    def activate(self, hwnd: int) -> bool:
        if not self.available() or not win32gui.IsWindow(hwnd):
            return False
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception:
            return False

    @staticmethod
    def client_to_screen(hwnd: int, x: int, y: int) -> tuple[int, int]:
        if win32gui is None:
            return x, y
        return tuple(win32gui.ClientToScreen(hwnd, (int(x), int(y))))

    @staticmethod
    def screen_to_client(hwnd: int, x: int, y: int) -> tuple[int, int]:
        if win32gui is None:
            return x, y
        return tuple(win32gui.ScreenToClient(hwnd, (int(x), int(y))))

    def capture(self, hwnd: int):
        """返回窗口客户区截图；未安装 Pillow/截图依赖时返回 None。"""
        if not self.available():
            return None
        try:
            from PIL import ImageGrab
            info = self.get_window(hwnd)
            if not info:
                return None
            return ImageGrab.grab(bbox=(info.left, info.top, info.right, info.bottom), all_screens=True)
        except Exception:
            return None

    def layout(self, hwnds: list[int], columns: int = 2, width: int = 960, height: int = 540, gap: int = 8) -> list[dict[str, int]]:
        """计算窗口排列位置。实际移动由上层决定，避免在测试阶段意外移动窗口。"""
        columns = max(1, int(columns))
        result = []
        for index, hwnd in enumerate(hwnds):
            col = index % columns
            row = index // columns
            result.append({"hwnd": hwnd, "x": col * (width + gap), "y": row * (height + gap), "width": width, "height": height})
        return result

__all__ = ["WindowInfo", "WindowsWindowAdapter"]
