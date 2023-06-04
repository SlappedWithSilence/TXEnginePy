import copy

from game.structures import manager as manager
from game.structures.loadable_factory import LoadableFactory
from game.systems.entity import entities as entities
from game.util.asset_utils import get_asset


class EntityManager(manager.Manager):
    """
    A class that specializes in handling entities.
    """

    ENTITY_ASSET_PATH = "entities"

    def __init__(self):
        super().__init__()
        self._manifest: dict[int, entities.Entity] = {}
        self.player_entity: entities.Entity = None

    def __getitem__(self, item) -> entities.Entity:
        return self.get_instance(item)

    def __contains__(self, item) -> bool:
        return self._manifest.__contains__(item)

    def register_entity(self, entity: entities.Entity) -> None:
        """
        Register the entity object with the EntityManager

        Args:
            entity (Entity): The object to register:

        Returns: None
        """

        # Type Check
        if not isinstance(entity, entities.Entity):
            raise TypeError(f"EntityManager cannot register object of type {type(entity)}")

        # Value Check
        if entity.id in self._manifest:
            raise ValueError(f"Cannot register entity with duplicate id:{entity.id}")

        self._manifest[entity.id] = entity

    def get_instance(self, entity_id) -> entities.Entity:
        return copy.deepcopy(self._manifest[entity_id])

    def load(self) -> None:
        raw_asset: dict[str, any] = get_asset(self.ENTITY_ASSET_PATH)
        for raw_entity in raw_asset['content']:
            entity = LoadableFactory.get(raw_entity)
            if not isinstance(entity, entities.Entity):
                raise TypeError(f"Expected object of type Entity, got {type(entity)} instead!")

            self.register_entity(entity)

    def save(self) -> None:
        pass
