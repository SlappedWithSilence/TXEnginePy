import weakref
from abc import ABC
from enum import Enum

import game.systems.currency as currency
import game.systems.flag as flag
from game.cache import from_cache, cached
from game.structures.enums import InputType
from game.structures.loadable import LoadableMixin
from game.structures.loadable_factory import LoadableFactory
from game.structures.messages import StringContent, ComponentFactory
from game.structures.state_device import FiniteStateDevice
from game.systems.crafting import recipe_manager
from game.systems.entity import entities as entities
from game.systems.entity.resource import ResourceController


class Event(FiniteStateDevice, LoadableMixin, ABC):

    def __init__(self, default_input_type: InputType, states: type[Enum], default_state):
        super().__init__(default_input_type, states, default_state)

    def __str__(self) -> str:
        return f"{self.__class__}"


class FlagEvent(Event):
    """ An event that sets a specific flag to a given value

        TXEngine Flags are slightly different from exact str-bool mappings. A Flag may define itself to be a part of a
        flag "subgroup" using dot-notation.
        For example:
         - A flag with a key of some.flag = True would store itself in the flags cache as flags['some']['flag'] = True
         - A flag with a key of this.is.a.deep.flag = False would be flags['this']['is']['a']['deep']['flag'] = False
    """

    def __init__(self, flags: list[tuple[str, bool]]):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
        self._flags = flags  # The flags to set and their corresponding values

        @FiniteStateDevice.state_logic(input_type=InputType.SILENT, instance=self, state=self.States.DEFAULT)
        def logic(_: any) -> None:
            """
            Perform some logic for setting flags
            """
            for f in self._flags:
                flag.flag_manager.set_flag(*f)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get()

    def __copy__(self):
        return FlagEvent(self._flags)

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "FlagEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
       Loads a FlagEvent object from a JSON blob.

       Required JSON fields:
       - flags[[str, bool]]
       """

        required_fields = [
            ('flags', list[list[str | bool]])
        ]

        LoadableFactory.validate_fields(required_fields, json)

        _flags = []

        for flag_bundle in json['flags']:
            if len(flag_bundle) != 2:
                raise ValueError(f"Flag data should be of length 2! Got length {len(flag_bundle)} instead.")

            assert type(flag_bundle[0]) == str, "Flag data must have a str at pos 0!"
            assert type(flag_bundle[1]) == bool, "Flag data must have a bool at ps 1!"

            _flags.append((flag_bundle[0], flag_bundle[1]))

        return FlagEvent(_flags)


class LearnAbilityEvent(Event):
    """Causes the player to learn a given ability"""

    class States(Enum):
        DEFAULT = 0
        ALREADY_LEARNED = 1
        NOT_ALREADY_LEARNED = 2
        REQUIREMENTS_NOT_MET = 3
        REQUIREMENTS_MET = 4
        TERMINATE = -1

    def __init__(self, ability_name: str):
        super().__init__(InputType.SILENT, LearnAbilityEvent.States, self.States.DEFAULT)
        self.target_ability: str = ability_name
        self.player_ref = None

        @FiniteStateDevice.state_content(instance=self, state=self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            if not self.player_ref:
                self.player_ref = from_cache("player")

            if self.player_ref.ability_controller.is_learned(ability_name):
                self.set_state(self.States.ALREADY_LEARNED)
            else:
                self.set_state(self.States.NOT_ALREADY_LEARNED)

        @FiniteStateDevice.state_logic(self, self.States.NOT_ALREADY_LEARNED, InputType.SILENT)
        def logic(_: any) -> None:
            if self.player_ref.ability_controller.is_learnable(ability_name):
                self.set_state(self.States.REQUIREMENTS_MET)

            else:
                self.set_state(self.States.REQUIREMENTS_NOT_MET)

        @FiniteStateDevice.state_content(self, self.States.NOT_ALREADY_LEARNED)
        def content():
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.ALREADY_LEARNED, input_type=InputType.ANY)
        def logic(_: any):
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.ALREADY_LEARNED)
        def content() -> dict:
            already_learned_message = [StringContent(value="You already learned "),
                                       StringContent(value=ability_name,
                                                     formatting="ability_name")
                                       ]
            return ComponentFactory.get(already_learned_message)

        @FiniteStateDevice.state_logic(self, self.States.REQUIREMENTS_MET, InputType.ANY)
        def logic(_: any) -> None:
            self.player_ref.ability_controller.learn(ability_name)
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.REQUIREMENTS_MET)
        def content() -> dict:
            learn_message = [StringContent(value="You learned a new ability!\n"),
                             StringContent(value=ability_name,
                                           formatting="ability_name")]
            return ComponentFactory.get(learn_message)

        @FiniteStateDevice.state_logic(self, self.States.REQUIREMENTS_NOT_MET, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.REQUIREMENTS_NOT_MET)
        def content():
            return ComponentFactory.get(
                ["You do not meet the requirements for learning ",
                 StringContent(value=ability_name, formatting="ability_name"),
                 "."],
                # Retrieve the requirements for this ability and pass them through the options argument
                from_cache("managers.AbilityManager").get_ability(ability_name).get_requirements_as_options()
            )

    def __copy__(self):
        return LearnAbilityEvent(self.target_ability)

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "LearnAbilityEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
        Loads a LearnAbilityEvent object from a JSON blob.

        Required JSON fields:
        - ability_name (str)
        """

        required_fields = [
            ("ability_name", str)
        ]

        LoadableFactory.validate_fields(required_fields, json)

        if json['class'] != "LearnAbilityEvent":
            raise ValueError()

        return LearnAbilityEvent(json['ability_name'])


class CurrencyEvent(Event):
    """
    A currency event changes the player's balance for a specific currency.
    """

    def __init__(self, currency_id: int | str, quantity: int, silent: bool = False):
        super().__init__(InputType.ANY, self.States, self.States.DEFAULT)
        self._currency_id = currency_id
        self._quantity = quantity
        self._cur = currency.currency_manager.to_currency(currency_id, quantity)
        self._player_ref = from_cache("player")
        self._silent = silent
        self._gain_message: list[StringContent] = [
            f"{self._player_ref.name} gained ",
            StringContent(value=str(self._cur))
        ]
        self._loss_message: list[StringContent] = [
            f"{self._player_ref.name} lost ",
            StringContent(value=str(self._cur))
        ]

        self._message = self._gain_message if quantity >= 0 else self._loss_message

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.ANY if not silent else InputType.SILENT)
        def logic(_: any) -> None:
            self._player_ref.coin_purse.adjust(self._currency_id, self._quantity)
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content():
            return ComponentFactory.get(self._message)

    def __copy__(self):
        return CurrencyEvent(self._currency_id, self._quantity, self._silent)

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "CurrencyEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
        Loads a CurrencyEvent object from a JSON blob.

        Required JSON fields:
        - currency_id: int
        - quantity: int

        Optional JSON fields:
        - silent: bool
        """

        required_fields = [
            ('currency_id', int),
            ('quantity', int),
        ]

        optional_fields = [
            ('silent', bool)
        ]

        LoadableFactory.validate_fields(required_fields, json, required=True)
        LoadableFactory.validate_fields(optional_fields, json, required=False, implicit_fields=False)

        if json['class'] != "CurrencyEvent":
            raise ValueError()

        kwargs = LoadableFactory.collect_optional_fields(optional_fields, json)

        return CurrencyEvent(json['currency_id'], json['quantity'], **kwargs)


class LearnRecipeEvent(Event):
    """
    A RecipeEvent unlocks a specified recipe for the Player.
    """

    class States(Enum):
        DEFAULT = 0
        CAN_LEARN = 1
        CANNOT_LEARN = 2
        TERMINATE = -1

    def __init__(self, recipe_id: int):
        super().__init__(InputType.ANY, self.States, self.States.DEFAULT)
        self.recipe_id = recipe_id
        self._player_ref = from_cache('player')

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any):
            if self._player_ref.crafting_controller.can_learn_recipe(self.recipe_id):
                self.set_state(self.States.CAN_LEARN)
            else:
                self.set_state(self.States.CANNOT_LEARN)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content():
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.CAN_LEARN, InputType.ANY)
        def logic(_: any) -> None:
            self._player_ref.crafting_controller.learn_recipe(recipe_id)
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.CAN_LEARN)
        def content():
            return ComponentFactory.get(
                [f"{self._player_ref.name} learned a recipe!\n{recipe_manager[recipe_id].name}"]
            )

        @FiniteStateDevice.state_logic(self, self.States.CANNOT_LEARN, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.CANNOT_LEARN)
        def content():
            return ComponentFactory.get(
                [f"{self._player_ref.name} cannot learn {recipe_manager[recipe_id].name}!"],
                recipe_manager[recipe_id].get_requirements_as_options()
            )

    def __copy__(self):
        return LearnRecipeEvent(self.recipe_id)

    def __deepcopy__(self, memodict={}):
        return LearnRecipeEvent(self.recipe_id)

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "LearnRecipeEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
        Loads a LearnRecipeEvent object from a JSON blob.

        Required JSON fields:
        - recipe_id (int)
        """

        required_fields = [
            ('recipe_id', int)
        ]

        LoadableFactory.validate_fields(required_fields, json)

        if json['class'] != "LearnRecipeEvent":
            raise ValueError()

        return LearnRecipeEvent(json['recipe_id'])


class ReputationEvent(Event):
    """
    A ReputationEvent modifies the Player's reputation with a specified Faction
    """

    def __init__(self, faction_id: int, reputation_change: int, silent: bool = False):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
        self.faction_id = faction_id
        self.reputation_change = reputation_change
        self._silent = silent
        self.message = [StringContent(value="Your reputation with "),
                        StringContent(value=f"faction::{faction_id}",
                                      formatting="faction_name"),
                        StringContent(value="decreased" if self.reputation_change < 0 else "increased"),
                        StringContent(value=f" by {reputation_change}")
                        ]

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.ANY)
        def logic(_: any) -> None:
            from_cache("managers.FactionManager").adjust_affinity(self.faction_id, self.reputation_change)

            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get(
                self.message
            )

    def __copy__(self):
        return ReputationEvent(self.faction_id, self.reputation_change, self._silent)

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "ReputationEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
        Loads a ReputationEvent object from a JSON blob.

        Required JSON fields:
        - faction_id (int)
        - reputation_change (int)

        Optional JSON fields:
        - silent (bool)
        """

        required_fields = [
            ('faction_id', int),
            ('reputation_change', int)
        ]

        optional_fields = [
            ('silent', bool)
        ]

        LoadableFactory.validate_fields(required_fields, json)
        LoadableFactory.validate_fields(optional_fields, json, required=False, implicit_fields=False)

        if json['class'] != "ReputationEvent":
            raise ValueError()

        kwargs = LoadableFactory.collect_optional_fields(optional_fields, json)

        return ReputationEvent(json['faction_id'], json['reputation_change'], **kwargs)


class ResourceEvent(Event):
    """
    A ResourceEvent modifies the specified Resource for a given Entity.
    """

    class States(Enum):
        DEFAULT = 0
        APPLY = 1
        SUMMARY = 2
        TERMINATE = -1

    def _build_summary(self, start_value: int, end_value: int) -> None:
        """Assemble a list[str | StringContent] to be printed within the SUMMARY state"""
        self._summary = [
            f"{self.target.name} {'lost' if self.amount < 0 else 'gained'}",
            f"{abs(start_value - end_value)} ",
            StringContent(value=f"{self.stat_name}.", formatting="resource_name")
        ]

    def __init__(self, resource_name: str, quantity: int | float, target=None, silent: bool = False):
        super().__init__(InputType.ANY, self.States, self.States.DEFAULT)
        self.stat_name: str = resource_name
        self.amount: int | float = quantity
        self.target = weakref.proxy(target) if target else None  # Weakref to an Entity object
        self._summary: list[str | StringContent] = None
        self._silent = silent

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_):
            from game.systems.entity.entities import Entity  # Import locally to prevent circular import issues

            if not isinstance(self.target, Entity):
                raise TypeError(f"Cannot apply a ResourceEvent to an object of type {self.target}")

            self.set_state(self.States.APPLY)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content():
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.APPLY, InputType.SILENT)
        def logic(_):
            resource_controller: ResourceController = self.target.resources
            self._build_summary(resource_controller.resources[self.stat_name]['instance'].value,  # Current value
                                resource_controller.resources[self.stat_name]['instance'].adjust(
                                    self.amount))  # Post-adjust value
            self.set_state(self.States.SUMMARY)

        @FiniteStateDevice.state_content(self, self.States.APPLY)
        def content():
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.SUMMARY, InputType.SILENT if self._silent else InputType.ANY)
        def logic(_: any):
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.SUMMARY)
        def content():
            return ComponentFactory.get(self._summary)

    def set_target(self, entity) -> None:
        if not isinstance(entity, entities.Entity):
            raise TypeError(f"Target Entity must be of type Entity! Got {type(entity)} instead.")

        self.target = weakref.proxy(entity)

    def __copy__(self):
        return ResourceEvent(self.stat_name, self.amount, self.target, self._silent)

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "ResourceEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
       Loads a ResourceEvent object from a JSON blob.

       Required JSON fields:
       - resource_name (str)
       - quantity: (int | float)

       Optional JSON fields:
       - silent (bool)
       """

        required_fields = [
            ("resource_name", str),
            ("quantity", (int, float))
        ]

        optional_fields = [
            ("silent", bool)
        ]

        LoadableFactory.validate_fields(required_fields, json)
        LoadableFactory.validate_fields(optional_fields, json, False, False)

        if json["class"] != "ResourceEvent":
            raise ValueError()

        kwargs = LoadableFactory.collect_optional_fields(optional_fields, json)

        return ResourceEvent(json['resource_name'], json['quantity'], None, **kwargs)


class TextEvent(Event):

    def __init__(self, text: str | list[str | StringContent]):
        super().__init__(InputType.ANY, self.States, self.States.DEFAULT)
        self.text: str | list[str | StringContent] = text

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get(
                self.text if type(text) == list else [self.text]
            )

    def __copy__(self):
        return TextEvent(self.text)

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    @staticmethod
    def from_json(json: dict[str, any]) -> any:
        """
        Loads a TextEvent from a JSON blob

        Required JSON fields:
        - text: str

        Optional JSON fields:
        - none
        """

        required_fields = [("text", str)]

        LoadableFactory.validate_fields(required_fields, json)

        return TextEvent(json["text"])


class SkillXPEvent(Event):
    """
    An Event that gives a specific skill XP.

    Flow handles both level-up and non-level-up scenarios.
    """

    class States(Enum):
        DEFAULT = 0
        GAIN_MESSAGE = 1  # Tell the user how much XP was gained
        LEVEL_UP = 2  # Tell the user that a Skill leveled up
        TERMINATE = -1

    def __init__(self, skill_id: int, xp_gain: int, target=None):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
        self._skill_id = skill_id
        self._xp_gained = xp_gain
        self._target = target  # A skill-enabled entity

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            if self._target is None:
                self._target = from_cache('player')

            self.set_state(self.States.GAIN_MESSAGE)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.GAIN_MESSAGE, InputType.ANY)
        def logic(_: any) -> None:
            self._target.skill_controller[self._skill_id].gain_xp(self._xp_gained)
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.GAIN_MESSAGE)
        def content() -> dict:
            return ComponentFactory.get(
                [
                    f"{self._target.name} gained {self._xp_gained} ",
                    StringContent(value=self._target.skill_controller[self._skill_id].name, formatting="skill_name"),
                    " xp!"
                ]
            )

    def __copy__(self):
        return SkillXPEvent(self._skill_id, self._xp_gained, self._target)

    def __deepcopy__(self, memodict={}):
        return self.__copy__()

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "SkillXPEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
        Load a SkillXPEvent from a JSON blob

        Required JSON fields:
        - skill_id: int
        - xp_gained: int

        Optional JSON fields:
        - None
        """

        required_fields = [
            ("skill_id", int), ("xp_gained", int)
        ]

        LoadableFactory.validate_fields(required_fields, json)

        return SkillXPEvent(json['skill_id'], json['xp_gained'])


class ViewResourcesEvent(Event):

    def __init__(self, target=None):
        super().__init__(InputType.ANY, self.States, self.States.DEFAULT)
        self._target = target  # The entity to read Resource values from

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.ANY)
        def logic(_: any) -> None:
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get(
                [f"{self.target.name}'s resources:"],
                self.target.resource_controller.get_resources_as_options()
            )

    @property
    def target(self):
        """
        Returns the event's target. If no target is specified, return a reference to the player.
        """
        return self._target or from_cache('player')

    @target.setter
    def target(self, ce):
        """
        Set the target of the event to a combat entity
        """
        from game.systems.entity.entities import CombatEntity

        if not isinstance(ce, CombatEntity):
            raise TypeError(
                f"ViewResourcesEvent target must be an instance of class CombatEntity! Got {type(ce)} instead!")

        self._target = ce

    def __copy__(self):
        return ViewResourcesEvent(self.target)

    def __deepcopy__(self, memodict={}):
        return ViewResourcesEvent(self.target)

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "ViewResourcesEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        return ViewResourcesEvent()


class ViewSummaryEvent(Event):

    class States(Enum):
        DEFAULT = 0
        VIEW_OPTIONS = 1
        EXECUTE_OPTION = 2
        TERMINATE = -1

    def __init__(self, target=None):
        super().__init__(InputType.INT, self.States, self.States.DEFAULT)

        self._target = target

    @property
    def target(self):
        """
        Returns the event's target. If no target is specified, return a reference to the player.
        """
        return self._target or from_cache('player')

    @target.setter
    def target(self, entity):
        """
        Set the target of the event to a combat entity
        """
        from game.systems.entity.entities import Entity

        if not isinstance(entity, Entity):
            raise TypeError(
                f"ViewSummaryEvent target must be an instance of class CombatEntity! Got {type(entity)} instead!")

        self._target = entity

    def __copy__(self):
        return ViewSummaryEvent(self.target)

    def __deepcopy__(self, memodict={}):
        return ViewSummaryEvent(self.target)

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "ViewSummaryEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        return ViewSummaryEvent()
