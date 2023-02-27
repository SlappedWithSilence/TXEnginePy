from enum import Enum

import game
import game.systems.item as item
import game.systems.entity.entities as entities
from game.cache import get_cache
from game.structures import enums
from game.structures.messages import StringContent, ComponentFactory
from game.systems.room.action.actions import Action


class ShopAction(Action):
    """
    An Action that simulates the user entering a shop.

    A Shop's flow is as follows:
    - 1. Display wares
    - 2. Select a ware or exit (input_type.int[ -1 : len(wares)])
        - Go to 12 if exit
    - 3. Prompt to purchase, get description, or cancel (input_type.int[-1 : 1])
    - 4. If cancel, go to 1. If get desc, go to 5. If purchase, go to 7
    - 5. Print selected item's description (input_type.NONE)
    - 6 Go to 3
    - 7. Check if purchase can be made. If yes, go to 8
    - 8. Confirm the purchase (input_type.affirmative)
    - 9. Go to 1
    - 10. Explain that the user has insufficient funds (input_type.none)
    - 11. Go to 1
    - 12. Terminate
    """

    class ShopState(Enum):
        """
        Enum values to be used to represent state information within the ShopAction.

        Each enum value is correlated to the states described within the ShopAction docstring.
        """
        DISPLAY_WARES = 2,
        WARE_SELECTED = 3,
        READ_WARE_DESC = 5,
        CONFIRM_WARE_PURCHASE = 8,
        PURCHASE_FAILURE = 10,
        TERMINATE = 12

    def __init__(self, menu_name: str, activation_text: str, wares: list[int],
                 default_currency: int = 0, *args, **kwargs):
        super().__init__(menu_name, activation_text, input_type=enums.InputType.INT, *args, **kwargs)
        self.wares: list[int] = wares  # list of tuples where idx[0] == item_id and idx[1] == item_cost
        self.state = self.ShopState.DISPLAY_WARES
        self._ware_of_interest: item.Item = None  # The tuple of the ware last selected by the user
        self.default_currency: int = default_currency

    @property
    def ware_of_interest(self) -> item.Item:
        return self._ware_of_interest

    @ware_of_interest.setter
    def ware_of_interest(self, i: item.Item | int) -> None:

        if type(i) == int:
            self._ware_of_interest = item.item_manager.get_instance(i)
        elif isinstance(i, item.Item):
            self._ware_of_interest = i
        else:
            raise TypeError(f"Ware of interest cannot be set to {type(i)}. Acceptable types are int, Item.")

    def _get_ware_options(self) -> list[list[StringContent | str]]:
        return [
            [
                "Purchase ",
                StringContent(value=self.ware_of_interest.name, formatting="item_name"),
                " for ",
                StringContent(value=self.ware_of_interest.value[self.default_currency], formatting="item_cost")
            ],
            [
                "Read ",
                StringContent(value=self.ware_of_interest.name, formatting="item_name"),
                "'s description"
            ]
        ]

    def _ware_to_option(self) -> list[list[StringContent | str]]:
        """
        Convert a list of ware tuples into formatted lists of StringContent

        Returns: A list of list[StringContent | str]. This list contains lists that contain the item available for
        purchase at the shop as well as their costs.
        """
        return [
            [StringContent(value=item.item_manager.get_name(item_id), formatting="item_name"),
             " : ",
             StringContent(value=str(item.item_manager.get_cost(item_id, self.default_currency, True)),
                           formatting="item_cost")]
            for item_id in self.wares]

    @property
    def components(self) -> dict[str, any]:
        if self.state == self.ShopState.DISPLAY_WARES:

            # Adjust input type and domain
            self.input_type = enums.InputType.INT
            self.domain_min = -1
            self.domain_max = len(self.wares) - 1

            return {"content": [self.activation_text],
                    "options": self._ware_to_option()
                    }
        elif self.state == self.ShopState.WARE_SELECTED:

            # Adjust input type and domain
            self.input_type = enums.InputType.INT
            self.domain_min = -1
            self.domain_max = len(self._get_ware_options()) - 1
            content = ["What would you like to do with ",
                       StringContent(value=self.ware_of_interest.name, formatting="item_name"),
                       "?"
                       ]
            return ComponentFactory.get(content, self._get_ware_options())
        elif self.state == self.ShopState.READ_WARE_DESC:
            self.input_type = enums.InputType.NONE

            return {
                "content": [
                    StringContent(value=self.ware_of_interest.name + ":\n", formatting="item_name"),
                    self.ware_of_interest.description
                ]
            }
        elif self.state == self.ShopState.CONFIRM_WARE_PURCHASE:
            self.input_type = enums.InputType.AFFIRMATIVE

            return {
                "content": [
                    "Are you sure that you would like to purchase 1x ",
                    StringContent(value=self.ware_of_interest.name + ":\n", formatting="item_name"),
                    " for ",
                    StringContent(value=self.ware_of_interest.get_currency_value(self.default_currency),
                                  formatting="item_cost"),
                    "?"
                ]
            }

        elif self.state == self.ShopState.PURCHASE_FAILURE:
            self.input_type = enums.InputType.NONE
            return {
                "content": [
                    "Cannot purchase ",
                    StringContent(value=self.ware_of_interest.name, formatting="item_name"),
                    ". Item costs ",
                    StringContent(value=self.ware_of_interest.get_currency_value(self.default_currency),
                                  formatting="item_cost"),
                    ", but you only have RETRIEVE USER CURRENCY.\nYou need USER CURRENCY - COST more to purchase."
                ]
            }

        elif self.state == self.ShopState.TERMINATE:
            self.input_type = enums.InputType.NONE
            return {
                "content": ["You leave the shop."]
            }

    def _logic(self, user_input: any) -> None:

        # State 2
        if self.state == self.ShopState.DISPLAY_WARES:  # Select a ware
            if user_input == -1:  # Chose to exit
                self.state = self.ShopState.TERMINATE
            else:  # Chose an item
                self.ware_of_interest = self.wares[user_input]
                self.state = self.ShopState.WARE_SELECTED

        # State 3
        elif self.state == self.ShopState.WARE_SELECTED:

            # TODO: Handle input dispatching better. Remove hardcoded state transitions
            if user_input == -1:
                self.state = self.ShopState.DISPLAY_WARES
            elif user_input == 0:
                self.state = self.ShopState.CONFIRM_WARE_PURCHASE
            elif user_input == 1:
                self.state = self.ShopState.READ_WARE_DESC

        # State 5
        elif self.state == self.ShopState.READ_WARE_DESC:
            self.state = self.ShopState.WARE_SELECTED

        # State 8
        elif self.state == self.ShopState.CONFIRM_WARE_PURCHASE:
            if user_input:

                player: entities.Player = get_cache()['player']
                if player.coin_purse.test_purchase(self.ware_of_interest.id, self.default_currency):
                    player.coin_purse.spend(self.ware_of_interest.get_currency_value(self.default_currency))
                    player.inventory.add_item(self.ware_of_interest.id, 1)
                    self.state = self.ShopState.DISPLAY_WARES

                else:
                    self.state = self.ShopState.PURCHASE_FAILURE

            else:
                self.state = self.ShopState.WARE_SELECTED

        # State 12
        elif self.state == self.ShopState.TERMINATE:
            game.state_device_controller.set_dead()
