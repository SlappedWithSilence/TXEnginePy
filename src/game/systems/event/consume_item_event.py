from enum import Enum

import game.cache
from game.structures.enums import InputType
from game.structures.messages import ComponentFactory, StringContent
from game.structures.state_device import FiniteStateDevice
from game.systems.event.events import Event
import game.systems.entity.entities as entities
import game.systems.item as item


class ConsumeItemEvent(Event):
    """Provides a standardized flow for prompting the user to optionally consume 'n' of a given item from his/her
    inventory
    """

    class States(Enum):
        DEFAULT = 0
        PROMPT_CONSUME = 1
        INSUFFICIENT_QUANTITY = 2
        REFUSED_CONSUME = 3
        ACCEPTED_CONSUME = 4
        TERMINATE = -1

    def __init__(self, item_id: int, item_quantity: int, callback: any = None):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
        self.item_id = item_id
        self.item_quantity = item_quantity
        self.player_ref: entities.Player = game.cache.get_cache()['player']

        if callback is not None and callable(callback):
            self.callback = callback
        else:
            raise TypeError(f"Callback must be callable! Got {type(callback)} instead.")

        # DEFAULT

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            # Detect item quantities
            if self.player_ref.inventory.total_quantity(self.item_id) < self.item_quantity:
                self.set_state(self.States.INSUFFICIENT_QUANTITY)
            else:
                self.set_state(self.States.PROMPT_CONSUME)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content():
            return ComponentFactory.get()

        # INSUFFICIENT_QUANTITY

        @FiniteStateDevice.state_logic(self, self.States.INSUFFICIENT_QUANTITY, InputType.ANY)
        def logic(_: any) -> None:
            self.callback(False)  # Transmit that the player failed to consume items to the callback
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.INSUFFICIENT_QUANTITY)
        def content():
            return ComponentFactory.get([
                "Insufficient quantity of ",
                StringContent(value=f"{item.item_manager.get_name(self.item_id)}", formatting="item_name"),
                "!"
            ])

        # PROMPT_CONSUME

        @FiniteStateDevice.state_logic(self, self.States.PROMPT_CONSUME, InputType.AFFIRMATIVE)
        def logic(user_input: bool) -> None:
            if user_input:
                self.set_state(self.States.ACCEPTED_CONSUME)
            else:
                self.set_state(self.States.REFUSED_CONSUME)

        @FiniteStateDevice.state_content(self, self.States.PROMPT_CONSUME)
        def content():
            return ComponentFactory.get([
                "Are you sure that you want to consume ",
                StringContent(value=f"{self.item_quantity}x ", formatting="item_quantity"),
                StringContent(value=f"{item.item_manager.get_name(self.item_id)}", formatting="item_name"),
                "?"
            ])

        # ACCEPTED_CONSUME

        @FiniteStateDevice.state_logic(self, self.States.ACCEPTED_CONSUME, InputType.ANY)
        def logic(_: any) -> None:
            assert self.player_ref.inventory.consume_item(self.item_id, self.item_quantity)
            self.callback(True)  # Transmit that the player successfully consumed items to the callback
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.ACCEPTED_CONSUME)
        def content():
            return ComponentFactory.get([
                "You consumed ",
                StringContent(value=f"{self.item_quantity}x ", formatting="item_quantity"),
                StringContent(value=f"{item.item_manager.get_name(self.item_id)}", formatting="item_name"),
                "."
            ])

        # REFUSED_CONSUME

        @FiniteStateDevice.state_logic(self, self.States.REFUSED_CONSUME, InputType.ANY)
        def logic(_: any) -> None:
            self.callback(False)  # Transmit that the player did not consume items to the callback
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.REFUSED_CONSUME)
        def content():
            return ComponentFactory.get([
                "You refused to consume ",
                StringContent(value=f"{self.item_quantity}x ", formatting="item_quantity"),
                StringContent(value=f"{item.item_manager.get_name(self.item_id)}", formatting="item_name"),
                "."
            ])

        # TERMINATE

        @FiniteStateDevice.state_logic(self, self.States.TERMINATE, InputType.SILENT)
        def logic(_: any):
            game.state_device_controller.set_dead()

        @FiniteStateDevice.state_content(self, self.States.TERMINATE)
        def content():
            return ComponentFactory.get()
