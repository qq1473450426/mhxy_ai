"""单账号 Skill 执行器。

负责超时、有限重试、状态推进与运行日志；具体游戏动作由 Skill 自己实现。
"""
from __future__ import annotations
from dataclasses import dataclass
from time import monotonic
from .base import SkillContext, SkillResult
from .registry import registry

@dataclass
class RunRecord:
    skill: str
    success: bool
    action: str
    message: str
    attempts: int
    elapsed: float
    next_state: str | None

class SkillRunner:
    def __init__(self, account_id: int):
        self.account_id = account_id
        self.last: RunRecord | None = None

    def execute(self, name: str, state: dict | None = None, config: dict | None = None) -> RunRecord:
        skill = registry.get(name)
        if skill is None:
            raise KeyError(f"Skill 不存在: {name}")
        ctx = SkillContext(self.account_id, state or {}, config or {})
        if not skill.can_run(ctx):
            record = RunRecord(name, False, "SKIP", "当前状态不满足 Skill 前置条件", 0, 0.0, None)
            self.last = record
            return record
        started = monotonic()
        result: SkillResult | None = None
        attempts = 0
        while attempts <= skill.max_retries:
            attempts += 1
            try:
                result = skill.run(ctx)
            except Exception as exc:
                result = SkillResult(False, "ERROR", f"Skill 异常: {exc}", retryable=True)
            if result.success or not result.retryable:
                break
        elapsed = monotonic() - started
        record = RunRecord(name, bool(result and result.success), result.action if result else "ERROR", result.message if result else "未知错误", attempts, elapsed, result.next_state if result else None)
        self.last = record
        return record
