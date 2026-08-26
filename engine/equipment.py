"""装备评分与穿戴策略。

目标不是追求市场价格最高，而是以当前角色的有效战斗能力为第一目标。
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Equipment:
    id: int
    name: str
    slot: str
    level: int
    score: float
    combat_power: float
    required_level: int = 0
    bound: bool = False


class EquipmentOptimizer:
    def __init__(self, minimum_combat_gain: float = 0.0):
        self.minimum_combat_gain = minimum_combat_gain

    def rank(self, items: list[Equipment], role: str = "输出") -> list[Equipment]:
        return sorted(
            [x for x in items if x.required_level <= 999],
            key=lambda x: (x.combat_power, x.score, x.level),
            reverse=True,
        )

    def best_by_slot(self, items: list[Equipment], current_level: int) -> dict[str, Equipment]:
        usable = [x for x in items if x.required_level <= current_level]
        result: dict[str, Equipment] = {}
        for item in usable:
            old = result.get(item.slot)
            if old is None or (item.combat_power, item.score, item.level) > (old.combat_power, old.score, old.level):
                result[item.slot] = item
        return result

    def plan_equip(self, items: list[Equipment], current: list[Equipment], current_level: int) -> list[dict]:
        best = self.best_by_slot(items, current_level)
        current_map = {x.slot: x for x in current}
        plan = []
        for slot, new_item in best.items():
            old = current_map.get(slot)
            if old is None or new_item.combat_power - old.combat_power > self.minimum_combat_gain:
                plan.append({"slot": slot, "equip_id": new_item.id, "equip_name": new_item.name, "reason": "有效战斗能力更高"})
        return plan
