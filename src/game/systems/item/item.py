import copy

import game
import game.systems.combat.effect as effect
import game.systems.currency as currency
import game.systems.requirement.requirements as req
from game.cache import cached, from_cache
from game.structures.loadable import LoadableMixin
from game.structures.loadable_factory import LoadableFactory
from game.systems.entity.resource import ResourceModifierMixin
from game.systems.event.events import Event
from game.systems.inventory import equipment_manager


class Item(LoadableMixin):
    """
    A basic item. Objects of this type are inert.
    """

    def __init__(self, name: str, iid: int, value: dict[int, int], description: str, max_quantity: int = 10,
                 **kwargs):
        super().__init__(**kwargs)
        self.name: str = name  # Name of item
        self.id: int = iid  # Unique id of item
        self.value: dict[int, int] = value  # Item's currency values. Key is Currency.id, value is Currency.quantity
        self.description: str = description  # The user-facing description of the item
        self.max_quantity: int = max_quantity  # The maximum number of items allowed in an inventory stack

    def get_currency_value(self, currency_id: int = None) -> currency.Currency:
        if type(currency_id) != int:
            raise TypeError(f"currency_id must be of type int! Got type {type(currency_id)} instead.")
        return from_cache('managers.CurrencyManager').to_currency(currency_id, self.value[currency_id])

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "Item", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> "Item":
        """
        Instantiate an Item object from a JSON blob.

        Args:
            json: a dict-form representation of a JSON object

        Returns: An Item instance with the properties defined in the JSON

        Required JSON fields:
        - name: str
        - id: int
        - value: dict[str, int]
        - description: str

        Optional JSON fields:
        - max_quantity: int (default value 10)
        """

        required_fields = [
            ("name", str), ("id", int), ("value", dict), ("description", str)
        ]

        optional_fields = [
            ("max_quantity", int)
        ]

        LoadableFactory.validate_fields(required_fields, json)
        LoadableFactory.validate_fields(optional_fields, json, False, False)
        kwargs = LoadableFactory.collect_optional_fields(optional_fields, json)

        return Item(json['name'],
                    json['id'],
                    {int(k): json['value'][k] for k in json['value']},
                    json['description'],
                    **kwargs
                    )


class Usable(Item, req.RequirementsMixin):
    """
    A consumable item. When consumed, this item's stack quantity decreases by 1 and the Events in 'use_events' are
    triggered in sequence.
    """

    def __init__(self, name: str, iid: int, value: dict[int, int], description: str, max_quantity: int = 10,
                 on_use_events: list[Event] = None, consumable: bool = False, **kwargs):
        super().__init__(name=name, iid=iid, value=value, description=description, max_quantity=max_quantity, **kwargs)

        self.on_use_events: list[Event] = on_use_events or []  # List of Events that trigger when item is used
        self.consumable: bool = consumable  # Determines if the item should decrement quantity after each use.

    def use(self, target) -> None:

        from game.systems.entity.entities import Entity
        if not isinstance(target, Entity):
            raise TypeError("Usable target must be an instance of Entity!")

        for e in self.on_use_events:
            if not isinstance(e, Event):
                raise TypeError(f"Invalid use_event object type! Got type {type(e)}. Expected type Event!")

            dce = copy.deepcopy(e)
            if hasattr(dce, "_target"):
                dce._target = target

            elif hasattr(dce, "target"):
                dce.target = target

            game.state_device_controller.add_state_device(dce)

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "Usable", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> "Usable":
        """
        Instantiate a Usable object from a JSON blob.

        Args:
            json: a dict-form representation of a JSON object

        Returns: A Usable instance with the properties defined in the JSON

        Required JSON fields:
        - name: str
        - id: int
        - value: {int, int}
        - description: str

        Optional JSON fields:
        - max_quantity: int (default value 10)
        - on_use_events: [Event]
        - consumable: bool
        - requirements: [Requirement]
        """

        required_fields = [
            ("name", str), ("id", int), ("value", dict), ("description", str)
        ]

        optional_fields = [
            ("max_quantity", int), ("on_use_events", list), ("consumable", bool)
        ]

        LoadableFactory.validate_fields(required_fields, json)
        LoadableFactory.validate_fields(optional_fields, json, False, False)

        kwargs = LoadableFactory.collect_optional_fields(optional_fields, json)

        if 'on_use_events' in kwargs:
            kwargs['on_use_events'] = [LoadableFactory.get(raw_effect) for raw_effect in kwargs['on_use_events']]

        return Usable(json['name'],
                      json['id'],
                      {int(k): v for k, v in json['value'].items()},
                      json['description'],
                      **kwargs
                      )


class Equipment(req.RequirementsMixin, ResourceModifierMixin, Item):

    def __init__(self, name: str, iid: int, value: dict[int, int], description: str,
                 equipment_slot: str, damage_buff: int, damage_resist: int,
                 start_of_combat_effects: list[effect.CombatEffect] = None, **kwargs):
        super().__init__(name=name, iid=iid, value=value, description=description, **kwargs)
        self.slot: str = equipment_manager.is_valid_slot(equipment_slot)
        self.start_of_combat_effects: list[effect.CombatEffect] = start_of_combat_effects or []

        self.damage_buff: int = damage_buff
        self.damage_resist: int = damage_resist

        self.resource_mods: dict[str, int | float] = {}

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "Equipment", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> "Equipment":
        """
       Instantiate an Equipment object from a JSON blob.

       Args:
           json: a dict-form representation of a JSON object

       Returns: An Equipment instance with the properties defined in the JSON

       Required JSON fields:
       - name: str
       - id: int
       - value: {int, int}
       - description: str
       - equipment_slot: str
       - damage_buff: int
       - damage_resist: int

       Optional JSON fields:
       - max_quantity: int (default value 10)
       - start_of_combat_effects: list[CombatEffect]
       - requirements: list[Requirement]
       - resource_modifiers: dict[str, int | float]
       """

        required_fields = [
            ("name", str), ("id", int), ("value", dict), ("description", str),
            ("equipment_slot", str), ("damage_buff", int), ("damage_resist", int)
        ]
        optional_fields = [
            ("max_quantity", int), ("start_of_combat_effects", list)
        ]

        LoadableFactory.validate_fields(required_fields, json)
        LoadableFactory.validate_fields(optional_fields, json, False, False)

        # Implicitly collect requirements, resource_modifiers
        kwargs = LoadableFactory.collect_optional_fields(optional_fields, json)

        # Overwrite SOCE since its contents must be cast to Python via LoadableFactory
        start_of_combat_effects = []
        if 'start_of_combat_effects' in json:
            for effect_json in json['start_of_combat_effects']:
                ef = LoadableFactory.get(effect_json)
                if not isinstance(ef, effect.CombatEffect):
                    raise TypeError(f"Expected effect of type CombatEffect, got {type(ef)} instead!")

                start_of_combat_effects.append(ef)

        kwargs['start_of_combat_effects'] = start_of_combat_effects

        return Equipment(json['name'],
                         json['id'],
                         {int(k): v for k, v in json['value'].items()},
                         json['description'],
                         json['equipment_slot'],
                         json['damage_buff'],
                         json['damage_resist'],
                         **kwargs
                         )
