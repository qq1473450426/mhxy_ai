"""实时多开监控 API。"""
from datetime import datetime, timezone
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Account
from engine.live_bus import snapshot

@require_GET
def live_snapshot(request):
    accounts = list(Account.objects.all().order_by("id"))
    live = {item["account_id"]: item for item in snapshot()}
    workers = []
    for account in accounts:
        state = live.get(account.id, {})
        workers.append({
            "account_id": account.id, "name": account.name,
            "state": state.get("state", "STOPPED"), "level": state.get("level"),
            "exp_percent": state.get("exp_percent"), "world": state.get("world"),
            "task": state.get("task"), "progress": state.get("progress", 0),
            "battle": state.get("battle", False), "reconnect_count": state.get("reconnect_count", 0),
            "backup_switch_count": state.get("backup_switch_count", 0),
            "character": state.get("character"), "role": state.get("role"),
            "updated_at": state.get("updated_at"), "error": state.get("error"),
        })
    return JsonResponse({"server_time": datetime.now(timezone.utc).isoformat(), "workers": workers})
