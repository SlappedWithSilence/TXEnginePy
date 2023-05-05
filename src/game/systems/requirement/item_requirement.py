from loguru import logger
import game
from game.structures.messages import StringContent
from game.systems import item as item
from game.systems.event.events import ConsumeItemEvent
from game.systems.requirement.requirements import Requirement


class ItemRequirement(Requirement):
    """
    Enforce that the player must have 'n' of a given item in his/her inventory.
    """

    def __init__(self, item_id: int, item_quantity: int):
        self.item_id: int = item_id
        self.item_quantity: int = item_quantity

    def fulfilled(self, entity) -> bool:
        logger.warning(f"Checking for {self.item_quantity} of {self.item_id}... Found {entity.inventory.total_quantity(self.item_id)}x")
        return entity.inventory.total_quantity(self.item_id) >= self.item_quantity

    @property
    def description(self) -> list[str | StringContent]:
        return [
            "You must have at least ",
            StringContent(value=f"{self.item_quantity}x", formatting="item_quantity"),
            " ",
            StringContent(value=f"{item.item_manager.get_name(self.item_id)}", formatting="item_name"),
            "!"
        ]


class ConsumeItemRequirement(ItemRequirement):
    """
    Enforce that the player must have and consume 'n' of a given item in his/her inventory.
    """

    def __init__(self, item_id: int, item_quantity: int):
        super().__init__(item_id, item_quantity)

        self.passed_event: bool = False

    def set_passed(self, passed: bool) -> None:
        logger.warning(f"set_passed: {passed}")
        self.passed_event = passed

    def fulfilled(self, entity) -> bool:
        if entity.inventory.total_quantity(self.item_id) < self.item_quantity:
            return False

        e = ConsumeItemEvent(self.item_id, self.item_quantity, self.set_passed)
        game.state_device_controller.add_state_device(e)
        return self.passed_event

    @property
    def description(self) -> list[str | StringContent]:
        return [
            "You must have at least ",
            StringContent(value=f"{self.item_quantity}x", formatting="item_quantity"),
            " ",
            StringContent(value=f"{item.item_manager.get_name(self.item_id)}", formatting="item_name"),
            "!"
        ]
