from .resource import EntityResource
from ...structures.enums import EquipmentType


class Entity:

    def __init__(self, name: str,
                 resources: dict[str, EntityResource],
                 skills: dict[str, any],
                 equipment: dict[EquipmentType, int]):

        self.name: str = name
        self.resources: dict[str, EntityResource] = resources
        self.skills: dict[str, any] = skills
        self.equipment: dict[EquipmentType, int] = equipment
