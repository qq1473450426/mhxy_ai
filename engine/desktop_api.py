"""Desktop Runtime 联调 API。

提供扫描窗口、选择窗口、截图状态与安全 dry-run 步进。
"""
from __future__ import annotations
import base64
import io
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .windows_adapter import WindowsWindowAdapter
from .desktop_runtime import DesktopRuntime
from .perception import PerceptionConfig, ScreenLevelingObserver

_adapter = WindowsWindowAdapter(["梦幻西游"])
_runtimes: dict[int, DesktopRuntime] = {}
_selected: dict[int, int] = {}


def _runtime(account_id: int) -> DesktopRuntime:
    if account_id not in _runtimes:
        _runtimes[account_id] = DesktopRuntime(account_id)
    return _runtimes[account_id]


@csrf_exempt
@require_http_methods(["GET"])
def windows(request):
    return JsonResponse({"available": _adapter.available(), "windows": [w.__dict__ for w in _adapter.find_windows()]})


@csrf_exempt
@require_http_methods(["POST"])
def select_window(request):
    try:
        d = json.loads(request.body or '{}')
        account_id = int(d["account_id"])
        hwnd = int(d["hwnd"])
    except (ValueError, KeyError, TypeError, json.JSONDecodeError):
        return JsonResponse({"error": "account_id/hwnd 无效"}, status=400)
    if not _adapter.get_window(hwnd):
        return JsonResponse({"error": "窗口不存在"}, status=404)
    _selected[account_id] = hwnd
    return JsonResponse({"ok": True, "account_id": account_id, "hwnd": hwnd})


def _capture_image(hwnd):
    return _adapter.capture(hwnd)


def _capture_b64(hwnd):
    image = _capture_image(hwnd)
    if image is None:
        return None
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=75)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def _perception(hwnd, title):
    """只读调用 Perception；任何识别异常都转换为 ERROR observation。"""
    observer = ScreenLevelingObserver(
        hwnd=hwnd,
        window_title=title or "梦幻西游",
        config=PerceptionConfig(),
        dry_run=True,
    )
    return observer.observe()


@csrf_exempt
@require_http_methods(["GET"])
def desktop_snapshot(request, account_id: int):
    hwnd = _selected.get(account_id)
    if not hwnd:
        return JsonResponse({"error": "尚未绑定桌面窗口"}, status=404)
    info = _adapter.get_window(hwnd)
    if not info:
        return JsonResponse({"error": "窗口已不存在"}, status=404)
    perception = _perception(hwnd, info.title)
    return JsonResponse({
        "account_id": account_id,
        "window": info.__dict__,
        "image": _capture_b64(hwnd),
        "perception": perception,
        "runtime": _runtime(account_id).snapshot(),
    })


@csrf_exempt
@require_http_methods(["GET"])
def desktop_perception(request, account_id: int):
    """独立感知接口：用于 WebUI 高频轮询，不包含点击或动作。"""
    hwnd = _selected.get(account_id)
    if not hwnd:
        return JsonResponse({"error": "尚未绑定桌面窗口"}, status=404)
    info = _adapter.get_window(hwnd)
    if not info:
        return JsonResponse({"error": "窗口已不存在"}, status=404)
    result = _perception(hwnd, info.title)
    result.update({"account_id": account_id, "window": info.__dict__})
    return JsonResponse(result)


@csrf_exempt
@require_http_methods(["POST"])
def desktop_step(request, account_id: int):
    if account_id not in _selected:
        return JsonResponse({"error": "尚未绑定桌面窗口"}, status=404)
    # 第一阶段仅观察/dry-run；真实动作适配器单独接入并逐项验证。
    runtime = _runtime(account_id)
    runtime.running = True
    event = runtime.step()
    return JsonResponse({"ok": True, "dry_run": True, "event": event.__dict__, "runtime": runtime.snapshot()})
