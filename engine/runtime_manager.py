"""多开 Runtime 管理器。

每个账号拥有独立的 SkillRunner，主控只负责启动/停止/查询，不共享账号执行上下文。
"""
from __future__ import annotations
from dataclasses import dataclass
from threading import Lock
from .skills.runner import SkillRunner

@dataclass
class Runtime:
    account_id: int
    runner: SkillRunner
    running: bool = False
    mode: str = "single"
    role: str | None = None

class RuntimeManager:
    def __init__(self):
        self._items: dict[int, Runtime] = {}
        self._lock = Lock()

    def start(self, account_id: int, mode: str = "single", role: str | None = None) -> Runtime:
        with self._lock:
            runtime = self._items.get(account_id)
            if runtime is None:
                runtime = Runtime(account_id, SkillRunner(account_id))
                self._items[account_id] = runtime
            runtime.running = True
            runtime.mode = mode
            if role is not None:
                runtime.role = role
            return runtime

    def stop(self, account_id: int) -> bool:
        with self._lock:
            runtime = self._items.get(account_id)
            if not runtime:
                return False
            runtime.running = False
            return True

    def stop_all(self) -> None:
        with self._lock:
            for runtime in self._items.values():
                runtime.running = False

    def get(self, account_id: int) -> Runtime | None:
        return self._items.get(account_id)

    def snapshot(self) -> list[dict]:
        with self._lock:
            return [{"account_id": r.account_id, "running": r.running, "mode": r.mode, "role": r.role} for r in self._items.values()]

runtime_manager = RuntimeManager()
