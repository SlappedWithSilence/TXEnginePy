from enum import Enum

from game.cache import cached, from_cache
from game.structures.enums import InputType
from game.structures.messages import ComponentFactory, StringContent
from game.structures.state_device import FiniteStateDevice
from game.systems.entity import Player
from game.systems.skill.skills import Skill
from game.systems.event.events import Event
from game.structures.loadable_factory import LoadableFactory
from game.structures.loadable import LoadableMixin


class ViewSkillsEvent(Event):
    class States(Enum):
        DEFAULT = 0
        VIEW_SKILLS = 1
        SKILL_SELECTED = 2
        TERMINATE = -1

    def __init__(self):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
        self._selected_skill: int | None = None
        self._player_ref: Player = None

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:

            # Deffer acquired player reference until StateDevice is actually run
            if not self._player_ref:
                self._player_ref = from_cache("player")

            self._selected_skill = None
            self.set_state(self.States.VIEW_SKILLS)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.VIEW_SKILLS, InputType.INT,
                                       -1, lambda: len(self._player_ref.skill_controller.skills.keys()) - 1)
        def logic(user_input: int) -> None:
            if user_input == -1:
                self.set_state(self.States.TERMINATE)
                return

            self._selected_skill = list(self._player_ref.skill_controller.skills.keys())[user_input]
            self.set_state(self.States.SKILL_SELECTED)

        @FiniteStateDevice.state_content(self, self.States.VIEW_SKILLS)
        def content() -> dict:
            return ComponentFactory.get(
                ["Skills: "],
                self._player_ref.skill_controller.get_skills_as_options()
            )

        @FiniteStateDevice.state_logic(self, self.States.SKILL_SELECTED, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.VIEW_SKILLS)

        @FiniteStateDevice.state_content(self, self.States.SKILL_SELECTED)
        def content() -> dict:
            return ComponentFactory.get(
                [
                    StringContent(value=self._player_ref.skill_controller.skills[self._selected_skill].name, formatting="skill_name"),
                    self._player_ref.skill_controller.get_skill_as_option(self._selected_skill),
                    "\n",
                    self._player_ref.skill_controller.skills[self._selected_skill].description
                ]
            )

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "ViewSkillsEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        return ViewSkillsEvent()
