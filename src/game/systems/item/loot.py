from abc import ABC
from random import randint

from game.cache import from_cache


class LootTable:
    LOOT_TABLE_RESOLUTION = 1000  # The length of the loot table array
    DROP_TABLE_RESOLUTION = 1000  # The length of the drop table array

    def __init__(self, loot_probabilities: dict[int, float], drop_probabilities: dict[int, float]):
        self._loot_table = self._generate_loot_table(loot_probabilities)  # Probability a drop is a specific item
        self._drop_table = self._generate_drop_table(drop_probabilities)

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
        if drop_probabilities is None:
            return dict[0:1.0]

        if sum(drop_probabilities.values()) != 1.0:
            raise ValueError("The sum of probabilities in a drop table must be exactly 1.0!")


class LootableMixin(ABC):

    def __init__(self, loot_table_id: int = None, loot_probabilities: dict[int, float] = None,
                 drop_probabilities: dict[int, float] = None,
                 **kwargs):
        super(**kwargs)

        if loot_table_id is not None and (loot_probabilities or drop_probabilities):
            raise ValueError("A LootableMixin cannot specify both a loot_table_id and a custom loot table!")

        if loot_table_id is None and not (loot_probabilities and drop_probabilities):
            raise ValueError(
                "A LootableMixin without a loot_table_id must provide both a loot_probabilities and drop_probabilities!"
            )

        if loot_table_id is not None:
            self._loot_table_id = loot_table_id  # The ID of a pre-made re-usable loot table defined in assets folder

        else:
            self._loot_table_instance = LootTable(loot_probabilities, drop_probabilities)

    def _get_num_drops(self) -> int:
        """
        Generate a random number to determine how many drops should be generated
        """
        return self._drop_table[randint(0, len(self._drop_table) - 1)]

    def _get_loot_instance(self) -> int:
        """
        Generate a random number to determine which item should drop
        """
        return self._loot_table[randint(0, len(self._loot_table) - 1)]

    def get_loot(self) -> dict[int, int]:
        """
        Fetch loot in the form of a dict.

        Each key represents an Item ID and the mapped values represents quantity
        """
