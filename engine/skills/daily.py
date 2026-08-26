"""通用日常任务 Skill：先建立执行框架，不绑定具体游戏坐标。"""
from .base import Skill, SkillContext, SkillResult
from .registry import registry

class DailyTaskSkill(Skill):
    name = "daily_task"
    timeout_seconds = 60
    max_retries = 2

    def can_run(self, ctx: SkillContext) -> bool:
        return bool(ctx.config.get("enabled", True)) and ctx.state.get("online", True)

    def run(self, ctx: SkillContext) -> SkillResult:
        task = ctx.config.get("task", "daily")
        return SkillResult(True, "plan_task", f"已选择日常任务模板：{task}", next_state="TASK")

registry.register(DailyTaskSkill())
