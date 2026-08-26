"""账号游戏窗口截图 API。"""
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
from .models import Account
from engine.screen_capture import capture_window

@require_GET
def account_screenshot(request, pk: int):
    try:
        account = Account.objects.get(pk=pk)
    except Account.DoesNotExist:
        return JsonResponse({"error": "账号不存在"}, status=404)
    hwnd = getattr(account, "window_handle", None)
    if not hwnd:
        return JsonResponse({"error": "当前账号没有绑定游戏窗口"}, status=409)
    try:
        data = capture_window(int(hwnd))
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=503)
    response = HttpResponse(data, content_type="image/jpeg")
    response["Cache-Control"] = "no-store, max-age=0"
    return response
