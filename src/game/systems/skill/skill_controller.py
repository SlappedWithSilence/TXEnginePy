from game.systems.skill import skill_manager


class SkillController:
    """
    Manages the Skill instances for a specific Entity.
    """

    def __init__(self, obtain_all: bool = False, skill_ids: list[int] = None):
        """
        Args:
            obtain_all (bool): If True, get all skills from the skill_manager
            skill_ids (list[int]): If obtain_all is False and skill_ids is not None, obtain all the Skills in this list
        """

        if type(obtain_all) != bool:
            raise TypeError()

        if type(skill_ids) is not None and type(skill_ids) != list:
            raise TypeError()

        self.skills = {}

        if obtain_all:
            for skill_id in skill_manager:
                self.skills[skill_id] = skill_manager.get_skill(skill_id)

        elif skill_ids is not None:
            for skill_id in skill_ids:
                self.skills[skill_id] = skill_manager.get_skill(skill_id)

    def get_level(self, skill_id: int) -> int:
        """
        Fetch a skill's level by looking up its ID.
        """

        if skill_id not in self.skills:
            raise ValueError(f"No skill with id {skill_id} found!")

        return self.skills[skill_id].level
