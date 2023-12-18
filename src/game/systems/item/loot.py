from abc import ABC
from random import randint

from game.cache import from_cache


class LootTable:
    """
    LootTable objects store organized data about the types of items that can drop and how many of them should drop.
    """
    ITEM_TABLE_RESOLUTION = 1000  # The length of the loot table array
    DROP_TABLE_RESOLUTION = 1000  # The length of the drop table array

    def __init__(self, item_probabilities: dict[int, float], drop_probabilities: dict[int, float]):
        self.item_table = self._generate_loot_table(item_probabilities)  # Probability a drop is a specific item
        self.drop_table = self._generate_drop_table(drop_probabilities)

    @classmethod
    def _generate_loot_table(cls, loot_probabilities: dict[int, float]) -> list[int]:
        """
        Transform a dict of item probabilities into a list of item IDs.
        """
        if loot_probabilities is None:
            return []

        if sum(loot_probabilities.values()) != 1.0:
            raise ValueError("The sum of probabilities in a loot table must be exactly 1.0!")

    @classmethod
    def _generate_drop_table(cls, drop_probabilities: dict[int, float]) -> list[int]:
        """
        Transform a dict of item probabilities into a list of item quantities.
        """
        if drop_probabilities is None:
            return dict[0:1.0]

        if sum(drop_probabilities.values()) != 1.0:
            raise ValueError("The sum of probabilities in a drop table must be exactly 1.0!")


class LootableMixin(ABC):
    """
    A Mixin class that allows an object to support 'looting'.

    LootableMixin provides support for direct definition of LootTable objects or global referencing via the LootManager.
    - To use direct definition, provide a value to `item_probabilities` and `drop_probabilities`.
    - To use global referencing, provide a LootTable ID to `loot_table_id`. This should correspond to the ID of a
        LootTable that has been registered with the LootManager.
    """

    def __init__(self, loot_table_id: int = None, item_probabilities: dict[int, float] = None,
                 drop_probabilities: dict[int, float] = None,
                 **kwargs):
        super(**kwargs)

        if loot_table_id is not None and (item_probabilities or drop_probabilities):
            raise ValueError("A LootableMixin cannot specify both a loot_table_id and a custom loot table!")

        if loot_table_id is None and not (item_probabilities and drop_probabilities):
            raise ValueError(
                "A LootableMixin without a loot_table_id must provide both a loot_probabilities and drop_probabilities!"
            )

        if loot_table_id is not None:
            self._loot_table_id = loot_table_id  # The ID of a pre-made re-usable loot table defined in assets folder

        else:
            self._loot_table_instance = LootTable(item_probabilities, drop_probabilities)

    @property
    def loot_table(self) -> LootTable:
        if self._loot_table_id is not None:
            return from_cache("managers.LootManager").get_instance(self._loot_table_id)
        else:
            return self._loot_table_instance

    def _get_num_drops(self) -> int:
        """
        Generate a random number to determine how many drops should be generated
        """
        return self.loot_table.drop_table[randint(0, len(self.loot_table.drop_table) - 1)]

    def _get_item_from_pool(self) -> int:
        """
        Generate a random number to determine which item should drop
        """
        return self.loot_table.item_table[randint(0, len(self.loot_table.item_table) - 1)]

    def get_loot(self) -> dict[int, int]:
        """
        Fetch loot in the form of a dict.

        Each key represents an Item ID and the mapped values represents quantity
        """

        drops: dict[int, int] = {}

        for i in range(0, self._get_num_drops()):
            item_id = self._get_item_from_pool()
            if item_id not in drops:
                drops[item_id] = 1
            else:
                drops[item_id] = drops[item_id] + 1

        return drops
