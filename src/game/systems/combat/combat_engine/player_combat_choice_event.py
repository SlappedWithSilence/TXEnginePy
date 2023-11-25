from __future__ import annotations

from enum import Enum

from loguru import logger

import game
import game.systems.item as items
from game.cache import cached, from_cache, from_storage
from game.structures.enums import InputType
from game.structures.loadable import LoadableMixin
from game.structures.messages import ComponentFactory, StringContent
from game.structures.state_device import FiniteStateDevice
from game.systems.combat.combat_engine.choice_data import ChoiceData
from game.systems.event import Event
from game.systems.event.select_element_event import SelectElementEventFactory
from game.systems.event.select_item_event import SelectItemEvent


class PlayerCombatChoiceEvent(Event):
    """
    Guides the player through choosing an action to take for a given entity during Combat
    """

    class States(Enum):
        DEFAULT = 0  # Setup
        CHOOSE_TURN_OPTION = 1  # Show the user which options are available
        CHOOSE_AN_ABILITY = 2  # Show the user abilities and request a selection
        CHOOSE_ABILITY_TARGET = 3  # If the ability requires a target, show available targets and request an selection
        CANNOT_USE_ABILITY = 4  # If the ability cannot be user for some reason, say so
        CHOOSE_AN_ITEM = 5  # Show the user all available items and request a selection
        DETECT_ITEM_USABLE = 6  # Check if the user can use the item and go to the appropriate state
        CANNOT_USE_ITEM = 7  # If the item cannot be used for some reason, say so
        SUBMIT_CHOICE = 8  # Once all choices have been finalized, submit them to the global combat instance
        PASS_TURN = 9  # If the choice was to pass, do so
        LIST_ENEMIES = 10  # Show a list of enemies that can be inspected
        LIST_ALLIES = 11  # SHow a list of allies that can be inspected
        INSPECT_ENTITY = 12  # SHow details about a specific entity
        CHECK_ABILITY_USABLE = 13  # Verify that selected ability can be used
        TERMINATE = -1  # Clean up

    def _get_turn_choices(self) -> dict[str, States]:
        return {
            "Inspect enemies": self.States.LIST_ENEMIES,
            "Inspect allies": self.States.LIST_ALLIES,
            "Use an ability": self.States.CHOOSE_AN_ABILITY,
            "Use an item": self.States.CHOOSE_AN_ITEM,
            "Pass turn": self.States.PASS_TURN
        }

    def __init__(self, entity):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
        self._links: dict[str, dict[str, str]] = {}
        self._entity = entity  # The entity for which to make a choice
        self._choice_data: ChoiceData = None
        self._available_turn_choices: dict[str, PlayerCombatChoiceEvent.States] = self._get_turn_choices()

        from game.systems.entity.entities import CombatEntity
        if not isinstance(self._entity, CombatEntity):
            raise TypeError(f"Invalid type for field `entity`! Expected CombatEntity, got {type(entity)}")

        self._setup_states()

    def _setup_states(self) -> None:
        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            self.set_state(self.States.CHOOSE_TURN_OPTION)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get()

        # SHOW_OPTIONS
        FiniteStateDevice.user_branching_state(self, self.States.CHOOSE_TURN_OPTION, self._available_turn_choices,
                                               "What would you like to do?")

        # CHOOSE_AN_ABILITY
        @FiniteStateDevice.state_logic(self, self.States.CHOOSE_AN_ABILITY, InputType.SILENT)
        def logic(_: any) -> None:
            choose_ability_event = SelectElementEventFactory.get_select_ability_event(self._entity, False, False)
            self._links["CHOOSE_AN_ABILITY"] = choose_ability_event.link()
            game.state_device_controller.add_state_device(choose_ability_event)
            self.set_state(self.States.CHECK_ABILITY_USABLE)

        @FiniteStateDevice.state_content(self, self.States.CHOOSE_AN_ABILITY)
        def content() -> dict:
            return ComponentFactory.get()

        # CHECK_ABILITY_USABLE
        @FiniteStateDevice.state_logic(self, self.States.CHECK_ABILITY_USABLE, InputType.SILENT)
        def logic(_: any) -> None:
            selected_ability = from_storage(self._links["CHOOSE_AN_ABILITY"]["selected_element"])

            if selected_ability is None:
                self.set_state(self.States.CHOOSE_TURN_OPTION)

            elif not self._entity.ability_controller.is_ability_usable(selected_ability):
                self.set_state(self.States.CANNOT_USE_ABILITY)

            else:
                self.set_state(self.States.CHOOSE_ABILITY_TARGET)

        @FiniteStateDevice.state_content(self, self.States.CHECK_ABILITY_USABLE)
        def content() -> dict:
            return ComponentFactory.get()

        # CHOOSE_ABILITY_TARGET
        @FiniteStateDevice.state_logic(self, self.States.CHOOSE_ABILITY_TARGET, InputType.INT)
        def logic(entity_index: int) -> None:

            chosen_ability = from_storage(self._links["CHOOSE_AN_ABILITY"]["selected_element"])
            self._choice_data = ChoiceData(
                ChoiceData.ChoiceType.ABILITY, ability_name=chosen_ability,
                ability_target=from_cache("combat").get_ability_targets(self._entity, chosen_ability)[entity_index]
            )
            self.set_state(self.States.SUBMIT_CHOICE)

        @FiniteStateDevice.state_content(self, self.States.CHOOSE_ABILITY_TARGET)
        def content() -> dict:
            chosen_ability = from_storage(self._links["CHOOSE_AN_ABILITY"]["selected_element"])

            return ComponentFactory.get(["Select a target:"],
                                        from_cache("combat").get_ability_targets(self._entity, chosen_ability),
                                        is_combat_frame=True)

        # CANNOT_USE_ABILITY
        @FiniteStateDevice.state_logic(self, self.States.CANNOT_USE_ABILITY, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.CHOOSE_TURN_OPTION)

        @FiniteStateDevice.state_content(self, self.States.CANNOT_USE_ABILITY)
        def content() -> dict:
            return ComponentFactory.get(["You cannot use that Ability."])

        # CHOOSE_AN_ITEM
        @FiniteStateDevice.state_logic(self, self.States.CHOOSE_AN_ITEM, InputType.SILENT)
        def logic(_: any) -> None:
            from game.systems.item.item import Usable
            # Generate a SelectItemEvent that only displays Usable Items
            select_usable_event = SelectItemEvent(self._entity, lambda item: isinstance(item, Usable))

            # Generate a storage link and cache it in _links
            self._links['CHOOSE_AN_ITEM'] = select_usable_event.link()

            # Add s_u_e to event stack
            game.state_device_controller.add_state_device(select_usable_event)

            # Transition state
            self.set_state(self.States.DETECT_ITEM_USABLE)

        @FiniteStateDevice.state_content(self, self.States.CHOOSE_AN_ITEM)
        def content() -> dict:
            return ComponentFactory.get()

        # DETECT_ITEM_USABLE
        @FiniteStateDevice.state_logic(self, self.States.DETECT_ITEM_USABLE, InputType.SILENT)
        def logic(_: any) -> None:
            from game.systems.item import Usable

            # Decode the linked storage ID to retrieve the ID of the item selected by the user
            chosen_item_id = from_storage(self._links["CHOOSE_AN_ITEM"]['selected_item_id'])

            if chosen_item_id is None:
                self.set_state(self.States.CHOOSE_TURN_OPTION)  # Return to main state
                return

            instance_of_chosen_item: Usable = items.item_manager.get_instance(chosen_item_id)  # Of type Usable
            entity_can_use_item: bool = instance_of_chosen_item.is_requirements_fulfilled(
                self._entity)  # Store to avoid re-computation

            #  If the user actually chose an Item, store that info in a choice_data and move on
            if entity_can_use_item:
                self._choice_data = ChoiceData(ChoiceData.ChoiceType.ITEM, item_id=chosen_item_id)
                self.set_state(self.States.SUBMIT_CHOICE)

            # Entity fails requirements checks
            elif not entity_can_use_item:
                self.set_state(self.States.CANNOT_USE_ITEM)

            else:
                raise RuntimeError("Something went wrong with PlayerCombatChoiceEvent")

        @FiniteStateDevice.state_content(self, self.States.DETECT_ITEM_USABLE)
        def content():
            return ComponentFactory.get()

        # CANNOT_USE_ITEM
        @FiniteStateDevice.state_logic(self, self.States.CANNOT_USE_ITEM, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.CHOOSE_AN_ITEM)

        @FiniteStateDevice.state_content(self, self.States.CANNOT_USE_ITEM)
        def content() -> dict:
            item_instance = from_cache('managers.ItemManager').get_instance(self._choice)

            return ComponentFactory.get(
                [
                    f"You cannot use ",
                    StringContent(value=item_instance.name, formatting="item_name"),
                    "!"
                ],
                item_instance.get_requirements_as_options()
            )

        # SUBMIT_CHOICE
        @FiniteStateDevice.state_logic(self, self.States.SUBMIT_CHOICE, InputType.SILENT)
        def logic(_: any) -> None:
            from_cache("combat").submit_entity_choice(self._entity, self._choice)
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.SUBMIT_CHOICE)
        def content() -> dict:
            return ComponentFactory.get()

        # PASS_TURN
        @FiniteStateDevice.state_logic(self, self.States.PASS_TURN, InputType.ANY)
        def logic(_: any) -> None:
            self._choice_data = ChoiceData(ChoiceData.ChoiceType.PASS)
            self.set_state(self.States.SUBMIT_CHOICE)

        @FiniteStateDevice.state_content(self, self.States.PASS_TURN)
        def content() -> dict:
            return ComponentFactory.get(
                [StringContent(value=self._entity.name, formatting="entity_name"), " chose not to act."]
            )

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "PlayerCombatChoiceEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        raise RuntimeError("Loading of PlayerCombatChoiceEvent from JSON is not supported!")
