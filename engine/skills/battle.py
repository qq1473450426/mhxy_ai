"""战斗模板 Skill。仅负责模板选择，不包含反检测逻辑。"""
from .base import Skill, SkillContext, SkillResult
from .registry import registry

class BattleTemplateSkill(Skill):
    name = "battle_template"
    timeout_seconds = 120
    max_retries = 1

    def can_run(self, ctx: SkillContext) -> bool:
        return bool(ctx.state.get("battle"))

    def run(self, ctx: SkillContext) -> SkillResult:
        template = ctx.config.get("template", "safe")
        return SkillResult(True, "execute_battle_template", f"使用战斗模板：{template}", next_state="BATTLE")

registry.register(BattleTemplateSkill())
