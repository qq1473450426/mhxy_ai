"""实时桌面感知 API。

第一阶段只读：截图 -> Perception -> 状态候选，不触发任何游戏动作。
"""
from __future__ import annotations

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from engine.perception import PerceptionConfig, ScreenLevelingObserver
from engine.windows_adapter import WindowsWindowAdapter
from .models import Account

_adapter = WindowsWindowAdapter(["梦幻西游"])
_selected: dict[int, int] = {}


def bind_window(account_id: int, hwnd: int) -> None:
    _selected[account_id] = hwnd


def _observer(account: Account, hwnd: int | None = None) -> ScreenLevelingObserver:
    return ScreenLevelingObserver(
        hwnd=hwnd or getattr(account, "hwnd", None) or getattr(account, "window_handle", None),
        window_title=account.window_title or "梦幻西游",
        config=PerceptionConfig(),
        dry_run=True,
    )


@require_GET
def perception_snapshot(request, account_id: int):
    account = get_object_or_404(Account, pk=account_id)
    hwnd = _selected.get(account_id) or getattr(account, "hwnd", None) or getattr(account, "window_handle", None)
    if not hwnd:
        return JsonResponse({
            "account_id": account_id,
            "state": "UNKNOWN",
            "confidence": 0.0,
            "detector": "none",
            "candidates": [],
            "ocr_text": "",
            "window_available": False,
            "error": "尚未绑定桌面窗口",
        })

    try:
        result = _observer(account, int(hwnd)).observe()
    except Exception as exc:
        return JsonResponse({
            "account_id": account_id,
            "state": "ERROR",
            "confidence": 0.0,
            "detector": "perception",
            "candidates": [],
            "ocr_text": "",
            "window_available": False,
            "error": str(exc),
        }, status=503)
    result["account_id"] = account_id
    return JsonResponse(result)


@require_GET
def perception_windows(request):
    return JsonResponse({
        "available": _adapter.available(),
        "windows": [w.__dict__ for w in _adapter.find_windows()],
    })
