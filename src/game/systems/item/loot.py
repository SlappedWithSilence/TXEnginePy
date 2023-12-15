from abc import ABC
from random import randint


class LootableMixin(ABC):
    LOOT_TABLE_RESOLUTION = 1000  # The length of the loot table array
    DROP_TABLE_RESOLUTION = 1000  # The length of the drop table array

    @classmethod
    def _generate_loot_table(cls, loot_probabilities: dict[int, float]) -> list[int]:
        """
        Transform a dict of item probabilities into a list of item IDs.
        """
        if loot_probabilities is None:
            return []

    @classmethod
    def _generate_drop_table(cls, drop_probabilities: dict[int, float]) -> list[int]:
        if drop_probabilities is None:
            return dict[0:1.0]

    def __init__(self, loot_probabilities: dict[int, float] = None, drop_probabilities: dict[int, float] = None,
                 **kwargs):
        super(**kwargs)

        self._loot_table = self._generate_loot_table(loot_probabilities)  # Probability a drop becomes a specific item
        self._drop_table = self._generate_drop_table(drop_probabilities)  # Probability 'n' items are dropped

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
