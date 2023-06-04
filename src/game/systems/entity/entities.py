from __future__ import annotations
from abc import ABC

import game.systems.currency.coin_purse
import game.systems.entity.resource as resource
import game.systems.inventory.inventory_controller as inv
from game.cache import cached
from game.structures.enums import CombatPhase
from game.structures.loadable import LoadableMixin
from game.structures.loadable_factory import LoadableFactory
from game.systems.combat.ability_controller import AbilityController
from game.systems.combat.combat_engine.combat_agent import MultiAgentMixin
import game.systems.combat.effect as effects
from game.systems.crafting.crafting_controller import CraftingController
from game.systems.inventory import EquipmentController

from loguru import logger

from game.systems.skill.skill_controller import SkillController


class EntityBase(ABC):

    def __init__(self, id: int, name: str):
        logger.debug("EntityBase.init")
        if type(id) != int:
            raise TypeError(f"Expected id to be of type int, got {type(id)} instead.")

        if type(name) != str:
            raise TypeError(f"Expected name to be of type str, got {type(name)} instead.")

        self.id: int = id
        self.name: str = name


class InventoryMixin:
    """
    A mixin for Entity objects that provides Inventory functionality.
    """

    def __init__(self, inventory: inv.InventoryController = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        """
        An InventoryController's content may be provided via instance, by tuple, or both.
        """
        if inventory is None:
            logger.debug("Using default inventory")
        else:
            logger.debug("Valid inventory found!")
            logger.debug(str(inventory.items))
        self.inventory = inventory or inv.InventoryController()


class CurrencyMixin:
    """
    A mixin for Entity objects that provides CoinPurse functionality.
    """

    def __init__(self, coin_purse=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from game.systems.currency.coin_purse import CoinPurse
        self.coin_purse = coin_purse or CoinPurse()


class ResourceMixin:
    """
    A mixin for Entity objects that provides ResourceController functionality
    """

    def __init__(self, resource_controller: resource.ResourceController = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resource_controller: resource.ResourceController = resource_controller or resource.ResourceController()


class Entity(CurrencyMixin, InventoryMixin, LoadableMixin, ResourceMixin, EntityBase):
    """A basic object that stores an entity's instance attributes such as name, ID, inventory, currencies, etc"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "Entity", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
        Instantiate an Entity object from a JSON blob.

        Args:
            json: a dict-form representation of a json object

        Returns: an Entity instance with the properties defined in the JSON

        Required JSON fields:
        - name: str
        - id: int
        - attributes: [any]

        Optional attribute fields:
        - inventory_controller: InventoryController
        - coin_purse: CoinPurse

        Optional JSON fields:
        - None
        """

        # Turn the attributes JSON fields into key-word arguments to be passed to Entity's subclasses
        kw = {}
        for attr in json['attributes']:
            kw[attr] = LoadableFactory.get(json['attributes'][attr][0])

        e = Entity(name=json['name'], id=json['id'], **kw)

        return e


class EquipmentMixin:
    """
    A mixin for Entity objects that provides EquipmentController functionality
    """

    def __init__(self, equipment_controller: EquipmentController = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.equipment_controller = equipment_controller or EquipmentController()
        self.equipment_controller.owner = self


class AbilityMixin:
    """
    A Mixin that grants an Entity the capacity to learn Abilities
    """

    def __init__(self, abilities: list[str] = None, ability_controller=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ability_controller = ability_controller or AbilityController()
        if abilities is not None:
            for ability in abilities:
                self.ability_controller.learn(ability)


class CombatEntity(AbilityMixin, EquipmentMixin, MultiAgentMixin, Entity):
    """
    A subclass of Entity that contains all the necessary components to participate in Combat.
    """

    def __init__(self,
                 xp_yield: int = 1,
                 turn_speed: int = 1,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.xp_yield: int = xp_yield
        self.turn_speed = turn_speed
        self.active_effects: dict[CombatPhase, list[effects.CombatEffect]] = {phase: [] for phase in CombatPhase}

    def make_choice(self) -> str | int | None:
        """
        Compute the next action that should be taken during combat.
        """
        pass

    def acquire_effect(self, effect: effects.CombatEffect, phase: CombatPhase) -> None:
        """
        Ingest an effect and store it in a phase's list.
        """

        self.active_effects[phase].append(effect)

    def clear_effects(self) -> None:
        """
        Remove all Effects from the Entity.
        """
        for phase in self.active_effects:
            self.active_effects[phase] = []

    def _prune_effects(self) -> None:
        """
        Remove all dead Effects from the Entity.

        An Effect is considered dead when its duration has decremented to zero.
        """
        for phase in self.active_effects:
            for i in range(len(self.active_effects[phase])):
                if self.active_effects[phase][i].duration == 0:
                    del self.active_effects[phase][i]

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "Entity", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
        Instantiate an Entity object from a JSON blob.

        Args:
            json: a dict-form representation of a json object

        Returns: an Entity instance with the properties defined in the JSON

        Required JSON fields:
        - name: str
        - id: int
        - xp_yield: int
        - turn_speed: int

        Optional JSON fields:
        - combat_provider (str)
        - inventory_controller: InventoryController
        - resource_controller: ResourceController
        - equipment_controller: EquipmentController
        - coin_purse: CoinPurse
        - abilities: [str]
        """

        required_fields = [
            ("name", str), ("id", int), ("xp_yield", int), ("turn_speed", int)
        ]

        optional_fields = [
            ("combat_provider", str), ("inventory_controller", dict), ("resource_controller", dict),
            ("equipment_controller", dict), ("coin_purse", dict), ("abilities", list)
        ]

        LoadableFactory.validate_fields(required_fields, json)
        LoadableFactory.validate_fields(optional_fields, json, False, False)
        kw = LoadableFactory.collect_optional_fields(optional_fields, json)

        ce = CombatEntity(json['xp_yield'], json['turn_speed'], name=json['name'], id=json['id'],
                          abilities=json['abilities'], **kw)

        # Post-init fixing
        # Note: since the equipment_controller only gets assigned an owner assigned AFTER init, it cannot check equip
        #       requirements. Thus, when loading the player's equipment_controller, can allow equipment to be equipped
        #       that the player cannot normally equip.
        if "equipment_controller" in kw:
            ce.equipment_controller.owner = ce

        return ce


class CraftingMixin:

    def __init__(self, recipes: list[int] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.crafting_controller: CraftingController = CraftingController(recipe_manifest=recipes or [], owner=self)


class SkillMixin:

    def __init__(self, skill_manifest: dict[str, dict[str, int]]):
        """
        Expects a dict-form manifest formatted like so:
        {
            "skill_id" : {
                "level" : 1
                "xp" : 1
            }
        }
        """

        self.skill_controller = SkillController(obtain_all=True)
        for skill_id in skill_manifest:
            if skill_id not in self.skill_controller:
                raise ValueError(f"No skill with id {skill_id}!")

            for term in ["level", "xp"]:
                if term not in skill_manifest[skill_id]:
                    raise ValueError(f"Missing field {term} in skill definition for skill {skill_id}")

            try:
                true_id = int(skill_id)
            except ValueError:
                raise ValueError(f"ID of {skill_id} cannot be converted to int!")

            self.skill_controller[true_id].level = skill_manifest[skill_id]['level']
            self.skill_controller[true_id].xp = skill_manifest[skill_id]['xp']


class Player(CraftingMixin, CombatEntity):

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "Player", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def make_choice(self) -> str | int | None:
        """
        Build a PlayerCombatChoiceEvent and place it onto the DeviceStack.
        """
        pass
