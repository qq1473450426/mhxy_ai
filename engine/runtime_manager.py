"""多开 Runtime 管理器。

每个账号拥有独立 SkillRunner；主控只负责生命周期与运行配置。
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
    paused: bool = False
    mode: str = "single"
    role: str | None = None
    character_slot: int = 1
    skill: str = "daily_task"

class RuntimeManager:
    def __init__(self):
        self._items: dict[int, Runtime] = {}
        self._lock = Lock()

    def start(self, account_id: int, mode="single", role=None, character_slot=1, skill="daily_task"):
        with self._lock:
            r=self._items.get(account_id) or Runtime(account_id, SkillRunner(account_id))
            r.running=True; r.paused=False; r.mode=mode; r.role=role; r.character_slot=max(1,int(character_slot)); r.skill=skill
            self._items[account_id]=r
            return r

    def stop(self, account_id):
        with self._lock:
            r=self._items.get(account_id)
            if not r:return False
            r.running=False; r.paused=False
            return True

    def pause(self, account_id):
        with self._lock:
            r=self._items.get(account_id)
            if not r or not r.running:return False
            r.paused=True
            return True

    def resume(self, account_id):
        with self._lock:
            r=self._items.get(account_id)
            if not r or not r.running:return False
            r.paused=False
            return True

    def stop_all(self):
        with self._lock:
            for r in self._items.values(): r.running=False; r.paused=False

    def get(self, account_id): return self._items.get(account_id)

    def snapshot(self):
        with self._lock:
            return [{"account_id":r.account_id,"running":r.running,"paused":r.paused,"mode":r.mode,"role":r.role,"character_slot":r.character_slot,"skill":r.skill} for r in self._items.values()]

runtime_manager=RuntimeManager()
