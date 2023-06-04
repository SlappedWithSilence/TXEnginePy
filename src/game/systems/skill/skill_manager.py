from __future__ import annotations

import copy

from game.structures.manager import Manager
import game.systems.skill.skills as skills


class SkillManager(Manager):

    def __init__(self):
        super().__init__()
        self._manifest: dict[int, skills.Skill] = {}

    def __getitem__(self, item) -> skills.Skill:
        return self.get_skill(item)

    def __contains__(self, item) -> bool:
        return self._manifest.__contains__(item)

    def register_skill(self, skill: skills.Skill) -> None:
        if not isinstance(skill, skills.Skill):
            raise TypeError(f"Expected object of type skills.Skill, got {type(skill)} instead!")

        if skill.id in self._manifest:
            raise ValueError(f"skills.Skill with id {skill.id} already registered!")

        self._manifest[skill.id] = skill

    def get_skill(self, skill_id: int) -> skills.Skill:
        if type(skill_id) != int:
            raise TypeError(f"Expected skill_id of type int, got {type(skill_id)} instead!")
        if skill_id not in self._manifest:
            raise ValueError(f"No skill with id {skill_id}!")

        return copy.deepcopy(self._manifest[skill_id])

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass
