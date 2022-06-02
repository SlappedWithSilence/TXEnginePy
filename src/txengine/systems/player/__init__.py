from typing import Union
from ..entity.entity import Entity

from ..entity.resource import EntityResource


class Player(Entity):
    room_index: int

    def __init__(self, name: str, resources: dict[str, EntityResource], skills: dict[str, any]):
        super().__init__(name, resources, skills)


player = Player(name="Player", resources={}, skills={})
