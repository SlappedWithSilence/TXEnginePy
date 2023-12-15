from game.structures.manager import Manager


class LootManager(Manager):
    """
    The global manager for reusable loot tables
    """

    LOOT_ASSET_PATH = "loot"

    def __init__(self):
        super().__init__()
        self._manifest: dict[int, tuple[list[int], list[int]]] = {}

    def register_loot_table(self, loot_table_id: int, loot_probabilities: dict[int, float],
                            drop_probabilities: dict[int, float]):
        pass

    def load(self) -> None:
        pass

    def save(self) -> None:
        pass
