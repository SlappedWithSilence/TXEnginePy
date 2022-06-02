from typing import Union

from ..currency.currency import Currency
from ..entity.entity import Entity
from ..entity.mixins.wallet import WalletMixin
from ..entity.resource import EntityResource
from ...structures.enums import EquipmentType


class Player(Entity, WalletMixin):
    room_index: int

    def __init__(self, name: str,
                 resources: dict[str, EntityResource],
                 skills: dict[str, any],
                 currencies: Union[list[Currency], dict[str, Currency]],
                 equipment: dict[EquipmentType, int]):
        super().__init__(name, resources, skills, equipment)
        super().__init__(currencies)


player = Player(name="Player", resources={}, skills={}, currencies=[], equipment={})
