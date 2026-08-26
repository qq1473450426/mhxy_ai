"""多开控制层：单开/多开、窗口排列、角色选择和运行模式。

控制层只编排账号与 Worker，不直接伪造游戏状态；真实客户端操作继续由 Login/Automation/Skill 执行。
"""
from dataclasses import dataclass
from typing import Iterable

from .manager import manager
from .window_manager import find_window, enumerate_windows


@dataclass(frozen=True)
class LayoutConfig:
    columns: int = 2
    width: int = 960
    height: int = 540
    gap: int = 8
    origin_x: int = 0
    origin_y: int = 0


class MultiOpenController:
    """统一控制单开与多开，避免前端直接操作多个 Worker。"""

    def start(self, accounts: Iterable, mode: str = "single", layout: LayoutConfig | None = None) -> dict:
        accounts = list(accounts)
        if not accounts:
            return {"status": "ERROR", "reason": "没有可启动账号"}
        mode = str(mode).lower()
        if mode == "single":
            accounts = accounts[:1]
        elif mode != "multi":
            return {"status": "ERROR", "reason": "mode 必须为 single 或 multi"}

        for account in accounts:
            manager.start(account)
        arranged = self.arrange(accounts, layout or LayoutConfig())
        return {"status": "STARTING", "mode": mode, "account_ids": [a.id for a in accounts], "arranged": arranged}

    def stop(self, accounts: Iterable) -> dict:
        accounts = list(accounts)
        for account in accounts:
            manager.stop(account)
        return {"status": "STOPPED", "account_ids": [a.id for a in accounts]}

    def arrange(self, accounts: Iterable, layout: LayoutConfig) -> list[dict]:
        """客户端启动后可重复调用；没有找到窗口的账号会返回 WAITING。"""
        result = []
        for index, account in enumerate(accounts):
            info = find_window(account.hwnd, account.window_title)
            if not info:
                result.append({"account_id": account.id, "status": "WAITING_WINDOW"})
                continue
            row, col = divmod(index, max(1, layout.columns))
            x = layout.origin_x + col * (layout.width + layout.gap)
            y = layout.origin_y + row * (layout.height + layout.gap)
            try:
                import win32gui
                win32gui.MoveWindow(info.hwnd, x, y, layout.width, layout.height, True)
                result.append({"account_id": account.id, "status": "ARRANGED", "x": x, "y": y, "width": layout.width, "height": layout.height})
            except Exception as exc:
                result.append({"account_id": account.id, "status": "ARRANGE_FAILED", "reason": str(exc)})
        return result

    @staticmethod
    def role_plan(accounts: Iterable, recommended_roles: list[str] | None = None) -> list[dict]:
        """生成组队角色建议。用户已配置角色时优先使用配置，否则按推荐顺序填充。"""
        recommended_roles = recommended_roles or ["辅助", "输出", "输出", "输出", "输出"]
        out = []
        for index, account in enumerate(accounts):
            role = getattr(account, "role_name", "") or (recommended_roles[index] if index < len(recommended_roles) else "输出")
            out.append({"account_id": account.id, "role": role, "character_slot": getattr(account, "character_slot", 1)})
        return out
