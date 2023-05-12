import copy

from game.structures.manager import Manager
from game.systems.skill.skills import Skill


class SkillManager(Manager):

    def __init__(self):
        super().__init__()
        self._skill_manifest: dict[int, Skill] = {}

    def __getitem__(self, item) -> Skill:
        return self.get_skill(item)

    def __contains__(self, item) -> bool:
        return self._skill_manifest.__contains__(item)

    def register_skill(self, skill: Skill) -> None:
        if not isinstance(skill, Skill):
            raise TypeError(f"Expected object of type Skill, got {type(skill)} instead!")

        if skill.id in self._skill_manifest:
            raise ValueError(f"Skill with id {skill.id} already registered!")

        self._skill_manifest[skill.id] = skill

    def get_skill(self, skill_id: int) -> Skill:
        if type(skill_id) != int:
            raise TypeError(f"Expected skill_id of type int, got {type(skill_id)} instead!")
        if skill_id not in self._skill_manifest:
            raise ValueError(f"No skill with id {skill_id}!")

        return copy.deepcopy(self._skill_manifest[skill_id])

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass
