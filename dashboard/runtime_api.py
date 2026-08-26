"""WebUI 到 RuntimeManager 的控制接口。"""
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from engine.runtime_manager import runtime_manager

def _body(request):
    try:return json.loads(request.body or '{}')
    except json.JSONDecodeError:return {}

@csrf_exempt
@require_http_methods(["GET"])
def runtimes(request):
    return JsonResponse({"results": runtime_manager.snapshot()})

@csrf_exempt
@require_http_methods(["POST"])
def runtime_control(request):
    d=_body(request); action=d.get("action","start")
    ids=[]
    for value in d.get("account_ids",[]):
        try:ids.append(int(value))
        except (TypeError,ValueError):pass
    if not ids:return JsonResponse({"error":"account_ids 不能为空"},status=400)
    results=[]
    for account_id in ids:
        if action=="start":
            r=runtime_manager.start(account_id,d.get("mode","single"),d.get("role"),d.get("character_slot",1),d.get("skill","daily_task")); results.append({"account_id":account_id,"running":r.running})
        elif action=="stop":results.append({"account_id":account_id,"ok":runtime_manager.stop(account_id)})
        elif action=="pause":results.append({"account_id":account_id,"ok":runtime_manager.pause(account_id)})
        elif action=="resume":results.append({"account_id":account_id,"ok":runtime_manager.resume(account_id)})
        else:return JsonResponse({"error":"未知动作"},status=400)
    return JsonResponse({"results":results})
