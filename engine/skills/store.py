"""Filesystem-backed SkillStore compatibility layer.

The runtime skill registry (engine.skills.registry) handles executable Skill
objects. SkillStore handles the separate data/rules files under ``skills/``
used for planning and keyword lookup.
"""
from __future__ import annotations

from pathlib import Path
import re


class SkillStore:
    """Search human-readable Skill data without executing it."""

    def __init__(self, root: str | Path = "skills"):
        self.root = Path(root)

    def _files(self):
        if not self.root.exists():
            return []
        return [
            p for p in self.root.rglob("*")
            if p.is_file() and p.suffix.lower() in {".md", ".txt", ".yaml", ".yml", ".json"}
        ]

    def search(self, query: str) -> list[dict]:
        """Return matching Skill documents with file name and text excerpt."""
        query = (query or "").strip()
        if not query:
            return []

        terms = [x.lower() for x in re.findall(r"[^\s,，:：]+", query) if x.strip()]
        results = []
        for path in self._files():
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            haystack = text.lower()
            if all(term in haystack or term in path.stem.lower() for term in terms):
                results.append({
                    "file": path.relative_to(self.root).as_posix(),
                    "text": text,
                })

        results.sort(key=lambda item: item["file"])
        return results
