import weakref
from abc import ABC

from loguru import logger

import game.systems.entity.entities as entities
from game.cache import cached
from game.structures.enums import InputType
from game.structures.loadable import LoadableMixin
from game.structures.loadable_factory import LoadableFactory
from game.structures.messages import ComponentFactory, StringContent
from game.structures.state_device import FiniteStateDevice


class CombatEffect(LoadableMixin, FiniteStateDevice, ABC):
    """
    A container object for combat logic.

    A CombatEffect possesses five fundamental properties:
    - The entity that spawned the effect
    - The entity that the effect is assigned to
    - The duration that the effect works for
    - The logic that is run when the effect is triggered
    - Tags

    During an entity's turn, each CombatEffect assigned to it triggers. When a CombatEffect triggers, it decrements its
    'duration' value. When this value hits zero, the CombatEngine removes the effect from its assigned target. A
    CombatEffect with a duration of None will never be removed from its target unless explicitly removed. An entity
    may alter the way that it executes the logic of the Effect based on the relationship of the tags possessed by the
    CombatEffect and the target Entity.

    An Effect does NOT determine what phase it is assigned to. Whatever spawned the Effect must also assign it to a
    CombatPhase explicitly.

    Note that each Effect MUST implement a functional reset() method. A default method is provided, but can be
    overridden if necessary. NEVER modify an Effect's duration via reset().
    """

    def __init__(self,
                 target_entity: entities.CombatEntity = None,
                 source_entity: entities.CombatEntity = None,
                 duration: int | None = 1,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_states()
        self._target_entity: entities.CombatEntity = target_entity  # The entity the effect is assigned
        self._source_entity: entities.CombatEntity = source_entity  # The entity that spawned the Effect
        self.duration: int | None = duration  # Number of remaining turns before Effect is removed
        self.tags: list[str] = []

    def is_assigned(self) -> bool:
        """
        Check if assign has already been called.
        """

        return self._source_entity is not None and self._target_entity is not None

    def assign(self, source_entity: entities.CombatEntity, target_entity: entities.CombatEntity) -> None:
        """
        Assign a source and target to the Effect. This option should be exercised by the CombatEngine
        """

        if not isinstance(source_entity, entities.CombatEntity):
            raise TypeError()
        if not isinstance(target_entity, entities.CombatEntity):
            raise TypeError()

        self._target_entity = weakref.proxy(target_entity)
        self._source_entity = weakref.proxy(source_entity)

    def perform(self):
        """
        Execute the logic for the Effect on the target entity.

        This method wraps the private abstract function _perform.
        """
        if not isinstance(self._target_entity, entities.Entity):
            raise TypeError(
                f"Cannot perform an effect on object of type {type(self._target_entity)}! Expected type Entity")

        self._perform(self._target_entity)  # Execute Effect logic
        if self.duration is not None:  # If Effect has finite duration, decrement its remaining uses
            self.duration -= 1

    def _setup_states(self):
        """
        Perform FiniteStateDevice state setups
        """
        raise NotImplementedError

    def _perform(self, target: entities.Entity):
        """
        Execute the logic of the Effect
        """
        raise NotImplementedError()

    def reset(self) -> None:
        """
        Simply return the state device to the default state.

        When overriding this method, do not include any logic that modifies duration.
        """
        self.set_state(self.States.DEFAULT)


class ResourceEffect(CombatEffect):
    """
    Modify a given resource by a given amount for the target.
    """

    def __init__(self, resource_name: str, adjust_quantity: int | float, trigger_message: str = None):
        super().__init__(default_input_type=InputType.ANY, states=self.States)

        if type(resource_name) != str:
            raise TypeError("resource_name must be of type str!")

        if type(adjust_quantity) != int and type(adjust_quantity) != float:
            raise TypeError("adjust_quantity must be of type int or type float!")

        self._resource_name = resource_name
        self._adjust_quantity = adjust_quantity
        self.trigger_message = trigger_message

    def __str__(self):
        return f"{self.name}: ({self._resource_name}: {self._adjust_quantity})"

    def __repr__(self):
        return self.__str__()

    def _perform(self, target: entities.Entity):
        if self._resource_name not in target.resource_controller:
            raise ValueError(f"Cannot locate resource {self._resource_name} in entity {target.name}!")

        logger.debug(f"Adjusting {self._resource_name} by {self._adjust_quantity}")
        target.resource_controller[self._resource_name].adjust(self._adjust_quantity)

    def _get_change_message(self) -> list[StringContent | str]:
        """
        The message to be printed when the Effect is viewed.
        """
        post_change: int = self._target_entity.resource_controller[self._resource_name].test_adjust(
            self._adjust_quantity)
        net: int = post_change - self._target_entity.resource_controller[self._resource_name].value > -1
        term = "gained" if net else "lost"

        return [
            self._target_entity.name, " ", term, " ", abs(net), " ",
            StringContent(value=self.name, formatting="resource_name"),
            "."
        ]

    def _setup_states(self):

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.ANY)
        def logic(_: any) -> None:
            self.perform()
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content():
            """
            This calculation only works because the client must retrieve state_content before executing state_logic!
            """
            trigger_message = self.trigger_message.format(target=self._target_entity.name)
            return ComponentFactory.get(
                [trigger_message] +
                self._get_change_message()
            )

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "ResourceEffect", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
        Instantiate a ResourceEffect object from a JSON blob.

        Args:
            json: a dict-form representation of a json object

        Returns: a ResourceEffect instance with the properties defined in the JSON

        Required JSON fields:
        - resource_name: (str)
        - adjust_quantity: (int | float)
        - trigger_message: (str)
        """

        # Validate that required fields are present and correctly-typed
        required_fields = [
            ("resource_name", str),
            ("adjust_quantity", (int, float)),
            ("trigger_message", str)
        ]

        LoadableFactory.validate_fields(required_fields, json)

        # Type and value validation
        if json["class"] != "ResourceEffect":
            raise ValueError("Incorrect class field in JSON! Expected class field of value 'ResourceEffect'")

        return ResourceEffect(json['resource_name'], json['adjust_quantity'], json['trigger_message'])
