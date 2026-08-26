from __future__ import annotations

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from engine.skill_store import SkillStore
from engine.leveling import NewServerLevelingStrategy


def knowledge_search(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse({'results': []})
    results = [
        {'file': x['file'], 'excerpt': x['text'][:800]}
        for x in SkillStore().search(query)
    ]
    return JsonResponse({'results': results})
