"""Skill 基类与统一执行结果。"""
from __future__ import annotations
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

@dataclass
class SkillContext:
    account_id: int
    state: dict = field(default_factory=dict)
    config: dict = field(default_factory=dict)

@dataclass
class SkillResult:
    success: bool
    action: str
    message: str
    next_state: str | None = None
    retryable: bool = True

class Skill(ABC):
    name = "base"
    timeout_seconds = 30
    max_retries = 2

    @abstractmethod
    def can_run(self, ctx: SkillContext) -> bool:
        raise NotImplementedError

    @abstractmethod
    def run(self, ctx: SkillContext) -> SkillResult:
        raise NotImplementedError
