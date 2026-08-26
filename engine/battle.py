"""任务战斗模板与自动战斗策略。

模板描述“识别什么、优先使用什么策略”，不保存截图中的敏感信息，也不假定固定坐标。
"""
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class BattleTemplate:
    name: str
    task_types: tuple[str, ...]
    priority: tuple[str, ...]
    allow_escape: bool = False
    max_rounds: int = 30
    conditions: dict[str, Any] = field(default_factory=dict)


DEFAULT_TEMPLATES = [
    BattleTemplate("普通任务战斗", ("DAILY", "SIDE", "MAIN"), ("点杀低血量", "群体技能", "普攻")),
    BattleTemplate("抓鬼", ("GHOST", "DAILY"), ("点杀主怪", "群体技能", "普攻"), max_rounds=25),
    BattleTemplate("副本小怪", ("DUNGEON", "DAILY"), ("群体技能", "控制", "普攻")),
    BattleTemplate("副本首领", ("BOSS", "DUNGEON"), ("点杀主怪", "治疗", "防御"), max_rounds=40),
]


class BattleTemplateStore:
    def __init__(self, templates=None):
        self.templates = list(templates or DEFAULT_TEMPLATES)

    def choose(self, task_type: str, battle_name: str = "") -> BattleTemplate | None:
        task_type = task_type.upper()
        for template in self.templates:
            if task_type in template.task_types or battle_name in template.name:
                return template
        return self.templates[0] if self.templates else None


class AutoBattleController:
    """根据感知结果生成下一动作；实际点击由 AutomationEngine/Executor 完成。"""
    def __init__(self, store: BattleTemplateStore | None = None):
        self.store = store or BattleTemplateStore()

    def decide(self, observation: dict[str, Any], task_type: str = "DAILY") -> dict[str, Any]:
        if not observation.get("in_battle"):
            return {"status": "WAIT", "reason": "当前不在战斗"}
        template = self.store.choose(task_type, str(observation.get("battle_name", "")))
        if not template:
            return {"status": "STOP", "reason": "没有战斗模板"}
        if observation.get("rounds", 0) >= template.max_rounds:
            return {"status": "STOP", "reason": "超过模板最大回合数", "allow_escape": template.allow_escape}
        return {"status": "ACTION", "template": template.name, "strategy": template.priority[0], "fallback": list(template.priority[1:])}
