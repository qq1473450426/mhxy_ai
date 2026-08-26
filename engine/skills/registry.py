"""Skill 注册表。"""
from __future__ import annotations
from .base import Skill

class SkillRegistry:
    def __init__(self):
        self._items: dict[str, Skill] = {}

    def register(self, skill: Skill) -> Skill:
        self._items[skill.name] = skill
        return skill

    def get(self, name: str) -> Skill | None:
        return self._items.get(name)

    def all(self) -> list[Skill]:
        return list(self._items.values())

registry = SkillRegistry()
