from ..effect.effect import Effect
from ...ui.color import style
from .mixins.usable import UsableMixin
from .mixins.equipment import EquipmentMixin


class Item:
    def __init__(self, name: str, desc: str, item_id: int, value: int = 0, max_stacks: int = 10):
        self.name: str = name
        self.desc: str = desc
        self.id: int = item_id
        self.value: int = value
        self.max_stacks: int = max_stacks

    @property
    def summary(self):
        """Returns a formatted string containing pertinent information about the item."""
        return style(self.name, "item_name") + "\n" \
               + style(self.desc, "item_desc") + "\n" \
               + "Value: " + style(str(self.value), "item_value")


class Usable(Item, UsableMixin):
    """An item that can be used to perform a specific set of Effects.

    An item of type Usable does not degrade after use unless consumable = True
    """

    def __init__(self, name: str, desc: str, item_id: int, value: int = 0, max_stacks: int = 10,
                 effects: list[Effect] = None, consumable: bool = False):
        super().__init__(name, desc, item_id, value, max_stacks)

        self.consumable = consumable
        self.effects = effects or []


class Equipment(Item, EquipmentMixin):
    def __init__(self, name: str, desc: str, item_id: int, value: int = 0, max_stacks: int = 10):
        super().__init__(name, desc, item_id, value, max_stacks)

    @property
    def summary(self):
        return super().summary + "\n" \
               + style("attack", "stat_name") + ": " + style(str(self.damage_bonus), "stat_value") + "\n" \
               + style("defense", "stat_name") + ": " + style(str(self.damage_resistance), "stat_value") + "\n"
