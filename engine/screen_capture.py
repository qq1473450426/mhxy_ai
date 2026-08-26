"""游戏窗口截图采集。

默认只截取指定 HWND，避免把整台电脑桌面暴露给 WebUI。
"""
from __future__ import annotations
import io
import os
from typing import Any


def capture_window(hwnd: int, quality: int = 72) -> bytes:
    if os.name != "nt":
        raise RuntimeError("窗口截图目前需要 Windows")
    import win32gui
    from PIL import ImageGrab
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    if right <= left or bottom <= top:
        raise RuntimeError("游戏窗口尺寸无效")
    image = ImageGrab.grab(bbox=(left, top, right, bottom), include_layered_windows=True)
    image.thumbnail((1280, 720))
    output = io.BytesIO()
    image.convert("RGB").save(output, format="JPEG", quality=max(40, min(90, quality)), optimize=True)
    return output.getvalue()
