"""实时状态总线。

单机开发默认使用内存实现；配置 REDIS_URL 后可切换 Redis，实现多进程共享状态。
"""
from __future__ import annotations
import json
import os
from typing import Any

_PREFIX = "mhxy:live:"
_memory: dict[int, dict[str, Any]] = {}
_redis = None


def _client():
    global _redis
    url = os.getenv("REDIS_URL", "").strip()
    if not url:
        return None
    if _redis is None:
        try:
            import redis
            _redis = redis.Redis.from_url(url, decode_responses=True)
            _redis.ping()
        except Exception:
            _redis = False
    return _redis if _redis is not False else None


def publish(account_id: int, **state: Any) -> dict[str, Any]:
    current = dict(_memory.get(account_id, {}))
    current.update(state)
    current["account_id"] = account_id
    _memory[account_id] = current
    client = _client()
    if client:
        client.set(_PREFIX + str(account_id), json.dumps(current, ensure_ascii=False), ex=120)
    return current


def snapshot() -> list[dict[str, Any]]:
    client = _client()
    if client:
        result = []
        for key in client.scan_iter(match=_PREFIX + "*"):
            raw = client.get(key)
            if raw:
                try:
                    result.append(json.loads(raw))
                except json.JSONDecodeError:
                    pass
        return sorted(result, key=lambda x: x.get("account_id", 0))
    return sorted(_memory.values(), key=lambda x: x.get("account_id", 0))
