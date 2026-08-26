"""轻量级实时事件流。

使用 SSE 避免前端持续轮询；浏览器断线后会自动重连。
"""
from __future__ import annotations
import json
import time
from django.http import StreamingHttpResponse
from django.views.decorators.http import require_GET
from engine.live_bus import snapshot


def _events():
    last = None
    while True:
        current = json.dumps(snapshot(), ensure_ascii=False, sort_keys=True)
        if current != last:
            yield f"event: live\ndata: {current}\n\n"
            last = current
        else:
            yield ": heartbeat\n\n"
        time.sleep(2)


@require_GET
def live_stream(request):
    response = StreamingHttpResponse(_events(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response["X-Accel-Buffering"] = "no"
    return response
