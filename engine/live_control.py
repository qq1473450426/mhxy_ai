"""多开实时监控的数据聚合层。"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Iterable


@dataclass
class LiveAccountState:
    account_id: int
    name: str
    state: str = "STOPPED"
    level: int | None = None
    exp_percent: float | None = None
    world: str | None = None
    task: str | None = None
    progress: int = 0
    battle: bool = False
    reconnect_count: int = 0
    backup_switch_count: int = 0
    character: str | None = None
    role: str | None = None
    updated_at: str | None = None
    error: str | None = None


class LiveControlStore:
    """Worker 可写、WebUI 可读的进程内实时状态缓存。

    后续接入 Redis 时保持相同接口即可，不让前端依赖具体存储。
    """

    def __init__(self) -> None:
        self._states: dict[int, LiveAccountState] = {}

    def update(self, account_id: int, **changes: Any) -> LiveAccountState:
        state = self._states.get(account_id) or LiveAccountState(account_id=account_id, name=str(account_id))
        for key, value in changes.items():
            if hasattr(state, key):
                setattr(state, key, value)
        state.updated_at = datetime.now(timezone.utc).isoformat()
        self._states[account_id] = state
        return state

    def get(self, account_id: int) -> LiveAccountState | None:
        return self._states.get(account_id)

    def snapshot(self, account_names: dict[int, str] | None = None) -> list[dict[str, Any]]:
        result = []
        for state in self._states.values():
            if account_names and state.account_id in account_names:
                state.name = account_names[state.account_id]
            result.append(asdict(state))
        return sorted(result, key=lambda item: item["account_id"])


live_store = LiveControlStore()
