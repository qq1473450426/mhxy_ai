"""梦幻西游客户端登录执行器。

登录层只处理标准登录表单：激活窗口、输入账号/密码、点击登录、等待窗口状态变化。
不处理验证码、滑块或其他安全验证；遇到验证时由上层暂停并人工处理。
"""
from __future__ import annotations
import json
import os
import time
from dataclasses import dataclass
from typing import Any

import pyautogui

from .credential_store import decrypt_password
from .window_manager import find_window


@dataclass(frozen=True)
class LoginLayout:
    account: tuple[int, int]
    password: tuple[int, int]
    login: tuple[int, int]

    @classmethod
    def from_env(cls) -> "LoginLayout | None":
        raw = os.getenv("MHXY_LOGIN_LAYOUT_JSON", "").strip()
        if not raw:
            return None
        try:
            d = json.loads(raw)
            return cls(
                (int(d["account"]["x"]), int(d["account"]["y"])),
                (int(d["password"]["x"]), int(d["password"]["y"])),
                (int(d["login"]["x"]), int(d["login"]["y"])),
            )
        except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            raise RuntimeError("MHXY_LOGIN_LAYOUT_JSON 格式错误") from exc


class LoginExecutor:
    def __init__(self, layout: LoginLayout | None = None, wait_seconds: float = 2.0):
        self.layout = layout or LoginLayout.from_env()
        self.wait_seconds = wait_seconds

    def login(self, account, password: str | None = None) -> dict[str, Any]:
        if not account.account_name:
            return {"success": False, "status": "CONFIG_ERROR", "reason": "未配置登录账号"}
        if not password:
            return {"success": False, "status": "CONFIG_ERROR", "reason": "未配置登录密码"}
        info = find_window(account.hwnd, account.window_title)
        if not info:
            return {"success": False, "status": "WINDOW_MISSING", "reason": "未找到游戏窗口"}
        if not self.layout:
            return {"success": False, "status": "LAYOUT_REQUIRED", "reason": "未配置登录控件坐标"}
        try:
            left, top, _, _ = info.rect
            self._click_type((left + self.layout.account[0], top + self.layout.account[1]), account.account_name)
            self._click_type((left + self.layout.password[0], top + self.layout.password[1]), password)
            pyautogui.click(left + self.layout.login[0], top + self.layout.login[1])
            time.sleep(self.wait_seconds)
            after = find_window(info.hwnd, account.window_title)
            if not after:
                return {"success": False, "status": "WINDOW_MISSING", "reason": "登录后窗口消失"}
            return {"success": True, "status": "LOGIN_SUBMITTED", "hwnd": after.hwnd, "pid": after.pid}
        except Exception as exc:
            return {"success": False, "status": "EXECUTION_ERROR", "reason": str(exc)}

    @staticmethod
    def _click_type(point: tuple[int, int], text: str) -> None:
        pyautogui.click(*point)
        pyautogui.hotkey("ctrl", "a")
        pyautogui.write(text, interval=0.02)


def login_account(account) -> dict[str, Any]:
    """解密凭据并执行一次登录；调用方负责记录结果，不得记录密码。"""
    password = decrypt_password(account.password)
    return LoginExecutor().login(account, password)
