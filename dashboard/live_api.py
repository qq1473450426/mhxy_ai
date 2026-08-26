"""实时多开监控 API。"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Account
from engine.live_control import live_store


@require_GET
def live_snapshot(request):
    accounts = list(Account.objects.all().order_by("id"))
    names = {account.id: account.name for account in accounts}
    states = {item["account_id"]: item for item in live_store.snapshot(names)}
    workers = []
    for account in accounts:
        workers.append(states.get(account.id, {
            "account_id": account.id,
            "name": account.name,
            "state": "STOPPED",
            "level": None,
            "exp_percent": None,
            "world": None,
            "task": None,
            "progress": 0,
            "battle": False,
            "reconnect_count": 0,
            "backup_switch_count": 0,
            "character": None,
            "role": getattr(account, "role", None),
            "updated_at": None,
            "error": None,
        }))
    return JsonResponse({"server_time": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(), "workers": workers})
