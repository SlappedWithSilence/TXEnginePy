from abc import ABC
from enum import Enum

import game
import game.cache as cache
import game.systems.room as room
import game.systems.item as item
import game.structures.enums as enums
import game.structures.state_device as state_device
import game.systems.event.events as events
import game.systems.requirement.requirements as requirements
from game.structures.messages import StringContent
from game.systems.currency.currency import Currency


class Action(state_device.StateDevice, requirements.RequirementsMixin, ABC):
    """
    Base class for all actions.
    """

    def __init__(self, menu_name: str, activation_text: str, visible: bool = True, reveal_other_action_index: int = -1,
                 hide_after_use: bool = False, requirement_list: list[requirements.Requirement] = None, *args,
                 **kwargs):
        super().__init__(*args, **kwargs)

        self._menu_name: str = menu_name  # Name of the Action when viewed from a room
        self.activation_text: str = activation_text  # Text that is printed when the Action is run
        self.visible: bool = visible  # If True, visible in the owning Room
        self.reveal_other_action_index: int = reveal_other_action_index  # If >= 0 set room.actions[idx].hidden to False
        self.hide_after_use: bool = hide_after_use  # If True, the action will set itself to hidden after being used
        self.room: room.Room = None  # The Room that owns this action. Should ONLY be a weakref.proxy
        self.requirements = requirement_list or []

    @property
    def menu_name(self) -> str:
        """
        Programmatically return menu name. Some subclasses of Action may need to dynamically adjust this property.
        """

        return self._menu_name


class ExitAction(Action):
    """
    An Action that signal to the state_device_controller that the containing Room StateDevice should be terminated
    """

    def __init__(self, target_room: int, menu_name: str = None, visible: bool = True,
                 reveal_other_action_index: int = -1, hide_after_use: bool = False, requirement_list: list = None,
                 on_exit: list[events.Event] = None):
        super().__init__(input_type=enums.InputType.AFFIRMATIVE, menu_name=menu_name, activation_text="",
                         visible=visible,
                         reveal_other_action_index=reveal_other_action_index, hide_after_use=hide_after_use,
                         requirement_list=requirement_list)

        # Set instance variables
        self.target_room = target_room
        self.input_type = enums.InputType.AFFIRMATIVE
        self.__on_exit: list[events.Event] = on_exit or []

    # Override abstract methods
    def _logic(self, user_input: any) -> None:
        cache.get_cache()["player_location"] = self.target_room
        room.room_manager.visit_room(self.room.id)  # Inform the room manager that this room has been "visited"
        game.state_device_controller.set_dead()  # Set the action as dead

    @property
    def menu_name(self) -> str:
        """
        Dynamically return a menu name that retrieves the room_name of the target Room
        """
        return f"Move to {room.room_manager.get_name(self.target_room)}"

    @property
    def components(self) -> dict[str, any]:
        return {"content":
                    [f"Do you want to move to",
                     StringContent(value=room.room_manager.get_name(self.target_room), formatting="room_name")]
                }


class ShopState(Enum):
    """
    Enum values to be used to represent state information within the ShopAction.

    Each enum value is correlated to the states described within the ShopAction docstring.
    """
    DISPLAY_WARES = 2,
    WARE_SELECTED = 3,
    READ_WARE_DESC = 5,
    CONFIRM_WARE_PURCHASE = 8,
    PURCHASE_FAILURE = 10


class ShopAction(Action):
    """
    An Action that simulates the user entering a shop.

    A Shop's flow is as follows:
    - 1. Display wares
    - 2. Select a ware or exit (input_type.int[ -1 : len(wares)])
    - 3. Prompt to purchase, get description, or cancel (input_type.int[-1 : 1])
    - 4. If cancel, go to 1. If get desc, go to 5. If purchase, go to 7
    - 5. Print selected item's description (input_type.NONE)
    - 6 Go to 3
    - 7. Check if purchase can be made. If yes, go to 8
    - 8. Confirm the purchase (input_type.affirmative)
    - 9. Go to 1
    - 10. Explain that the user has insufficient funds (input_type.none)
    - 4. Go to 1
    """

    def __init__(self, menu_name: str, activation_text: str, wares: list[tuple[int, Currency]], *args, **kwargs):
        super().__init__(menu_name, activation_text, *args, **kwargs)
        self.wares: list[tuple[int, Currency]] = wares  # list of tuples where idx[0] == item_id and idx[1] == item_cost
        self.state = ShopState.DISPLAY_WARES
        self.ware_of_interest: tuple[int, Currency] = None  # The tuple of the ware last selected by the user

    def _get_ware_options(self) -> list[list[StringContent | str]]:
        return [
            [
                "Purchase ",
                StringContent(value=item.item_manager.get_name(self.ware_of_interest[0])),
                " for ",
                StringContent(value=str(self.ware_of_interest[1]))
            ],
            [
                "Read ",
                StringContent(value=item.item_manager.get_name(self.ware_of_interest[0])),
                "'s description"
            ]
        ]

    def _ware_to_option(self) -> list[list[StringContent | str]]:
        """
        Convert a list of ware tuples into formatted lists of StringContent

        Returns: A list of list[StringContent | str]. This list contains lists that contain the items available for
        purchase at the shop as well as their costs.
        """
        return [
            [StringContent(value=item.item_manager.get_name(item_id), formatting="item_name"),
             StringContent(value=str(currency), format="item_cost")]
            for item_id, currency in self.wares]

    @property
    def components(self) -> dict[str, any]:
        if self.state == ShopState.DISPLAY_WARES:

            # Adjust input type and domain
            self.input_type = enums.InputType.INT
            self.domain_min = -1
            self.domain_max = len(self.wares) - 1

            return {"content": [self.activation_text],
                    "options": self._ware_to_option()
                    }
        elif self.state == ShopState.WARE_SELECTED:

            # Adjust input type and domain
            self.input_type = enums.InputType.INT
            self.domain_min = -1
            self.domain_max = len(self._get_ware_options()) - 1

            return {
                "content": ["What would you like to do with ",
                            StringContent(value=item.item_manager.get_name(self.ware_of_interest),
                                          formatting="item_name"),
                            "?"
                            ],
                "options": self._get_ware_options()
            }
        elif self.state == ShopState.READ_WARE_DESC:
            self.input_type = enums.InputType.NONE

            return {
                "content": [
                    item.item_manager.get_name(self.ware_of_interest[0]) + ":\n",
                    item.item_manager.get_desc(self.ware_of_interest[0])
                ]
            }

    def _logic(self, user_input: any) -> None:
        pass


class TestAction(Action):

    def __init__(self, menu_name: str, activation_text, *args, **kwargs):
        super().__init__(menu_name, activation_text, *args, **kwargs)

    @property
    def components(self) -> dict[str, any]:
        return {"content": "Test"}

    def _logic(self, user_input: any) -> None:
        pass


if __name__ == "__main__":
    a = TestAction("Test", "Test", input_type=enums.InputType.NONE, name="TestAction", requirements=[])
    print(a.__dict__)
    print(a.is_requirements_fulfilled())
