from __future__ import annotations

import weakref
from abc import ABC
from enum import Enum

import game.cache
import game.systems.currency as currency
import game.systems.flag as flag
import game.util.input_utils
from game.cache import from_cache
from game.structures.enums import InputType
from game.structures.loadable import LoadableMixin, LoadableFactory
from game.structures.messages import StringContent, ComponentFactory
from game.structures.state_device import FiniteStateDevice
from game.systems import item as item
from game.systems.entity import entities as entities
from game.systems.entity.resource import ResourceController
from game.systems.crafting import recipe_manager


class Event(FiniteStateDevice, LoadableMixin, ABC):

    def __init__(self, default_input_type: InputType, states: Enum, default_state):
        super().__init__(default_input_type, states, default_state)


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

    @staticmethod
    @game.cache.cached([LoadableMixin.LOADER_KEY, "FlagEvent", LoadableMixin.ATTR_KEY])
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
        self.player_ref = from_cache("player")

        @FiniteStateDevice.state_content(instance=self, state=self.States.DEFAULT)
        def content() -> dict:
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:

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

        @FiniteStateDevice.state_content(self, self.States.TERMINATE)
        def content() -> dict:
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.TERMINATE, InputType.SILENT)
        def logic(_: any) -> None:
            game.state_device_controller.set_dead()

    @staticmethod
    @game.cache.cached([LoadableMixin.LOADER_KEY, "LearnAbilityEvent", LoadableMixin.ATTR_KEY])
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

    @staticmethod
    @game.cache.cached([LoadableMixin.LOADER_KEY, "CurrencyEvent", LoadableMixin.ATTR_KEY])
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

        if 'silent' in json:
            return CurrencyEvent(json['currency_id'], json['quantity'], json['silent'])

        return CurrencyEvent(json['currency_id'], json['quantity'])


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

    @staticmethod
    @game.cache.cached([LoadableMixin.LOADER_KEY, "LearnRecipeEvent", LoadableMixin.ATTR_KEY])
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
        self.message = [StringContent(value="Your reputation with "),
                        StringContent(value=f"faction::{faction_id}",
                                      formatting="faction_name"),
                        StringContent(value="decreased" if self.reputation_change < 0 else "increased"),
                        StringContent(value=f" by {reputation_change}")
                        ]

    @staticmethod
    @game.cache.cached([LoadableMixin.LOADER_KEY, "ReputationEvent", LoadableMixin.ATTR_KEY])
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

        if 'silent' in json:
            return ReputationEvent(json['faction_id'], json['reputation_change'], json['silent'])

        return ReputationEvent(json['faction_id'], json['reputation_change'])


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

    def __init__(self, stat_name: str, stat_change: int | float, target, silent: bool = False):
        super().__init__(InputType.ANY, self.States, self.States.DEFAULT)
        self.stat_name: str = stat_name
        self.amount: int | float = stat_change
        self.target = weakref.proxy(target)  # Weakref to an Entity object
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
            self._build_summary(resource_controller.resources[self.stat_name].value,  # Current value
                                resource_controller.resources[self.stat_name].adjust(self.amount))  # Post-adjust value
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

        @FiniteStateDevice.state_logic(self, self.States.TERMINATE, InputType.SILENT)
        def logic(_: any) -> None:
            game.state_device_controller.set_dead()

        @FiniteStateDevice.state_content(self, self.States.TERMINATE)
        def content():
            return ComponentFactory.get()


class ConsumeItemEvent(Event):
    """Provides a standardized flow for prompting the user to optionally consume 'n' of a given item from his/her
    inventory
    """

    class States(Enum):
        DEFAULT = 0
        PROMPT_CONSUME = 1
        INSUFFICIENT_QUANTITY = 2
        REFUSED_CONSUME = 3
        ACCEPTED_CONSUME = 4
        TERMINATE = -1

    def __init__(self, item_id: int, item_quantity: int, callback: any = None):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)
        self.item_id = item_id
        self.item_quantity = item_quantity
        self.player_ref: entities.Player = game.cache.get_cache()['player']

        if callable(callback):
            self.callback = callback
        elif callback is not None:
            raise TypeError(f"Callback must be callable! Got {type(callback)} instead.")
        else:
            self.callback = None

        # DEFAULT

        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:
            # Detect item quantities
            if self.player_ref.inventory.total_quantity(self.item_id) < self.item_quantity:
                self.set_state(self.States.INSUFFICIENT_QUANTITY)
            else:
                self.set_state(self.States.PROMPT_CONSUME)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content():
            return ComponentFactory.get()

        # INSUFFICIENT_QUANTITY

        @FiniteStateDevice.state_logic(self, self.States.INSUFFICIENT_QUANTITY, InputType.ANY)
        def logic(_: any) -> None:
            if self.callback:
                self.callback(False)  # Transmit that the player failed to consume items to the callback
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.INSUFFICIENT_QUANTITY)
        def content():
            return ComponentFactory.get([
                "Insufficient quantity of ",
                StringContent(value=f"{item.item_manager.get_name(self.item_id)}", formatting="item_name"),
                "!"
            ])

        # PROMPT_CONSUME

        @FiniteStateDevice.state_logic(self, self.States.PROMPT_CONSUME, InputType.AFFIRMATIVE)
        def logic(user_input: bool) -> None:
            if user_input:
                self.set_state(self.States.ACCEPTED_CONSUME)
            else:
                self.set_state(self.States.REFUSED_CONSUME)

        @FiniteStateDevice.state_content(self, self.States.PROMPT_CONSUME)
        def content():
            return ComponentFactory.get([
                "Are you sure that you want to consume ",
                StringContent(value=f"{self.item_quantity}x ", formatting="item_quantity"),
                StringContent(value=f"{item.item_manager.get_name(self.item_id)}", formatting="item_name"),
                "?"
            ])

        # ACCEPTED_CONSUME

        @FiniteStateDevice.state_logic(self, self.States.ACCEPTED_CONSUME, InputType.ANY)
        def logic(_: any) -> None:
            assert self.player_ref.inventory.consume_item(self.item_id, self.item_quantity)
            if self.callback:
                self.callback(True)  # Transmit that the player successfully consumed items to the callback
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.ACCEPTED_CONSUME)
        def content():
            return ComponentFactory.get([
                "You consumed ",
                StringContent(value=f"{self.item_quantity}x ", formatting="item_quantity"),
                StringContent(value=f"{item.item_manager.get_name(self.item_id)}", formatting="item_name"),
                "."
            ])

        # REFUSED_CONSUME

        @FiniteStateDevice.state_logic(self, self.States.REFUSED_CONSUME, InputType.ANY)
        def logic(_: any) -> None:
            if self.callback:
                self.callback(False)  # Transmit that the player did not consume items to the callback
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.REFUSED_CONSUME)
        def content():
            return ComponentFactory.get([
                "You refused to consume ",
                StringContent(value=f"{self.item_quantity}x ", formatting="item_quantity"),
                StringContent(value=f"{item.item_manager.get_name(self.item_id)}", formatting="item_name"),
                "."
            ])


class CraftingEvent(Event):
    """
    Provide a standardized flow for guiding the Player through the process of crafting items via Recipes.
    """

    class States(Enum):
        DEFAULT = 0  # Pre-logic
        WHAT_DO_NOW = 1  # Select crafting activity
        DISPLAY_RECIPES = 2  # Choose a recipe
        CONFIRM_RECIPE = 3  # Confirm usage
        RECIPE_UNAVAILABLE = 4  # Missing items
        TERMINATE = -1

    def __init__(self):
        super().__init__(InputType.SILENT, self.States, self.States.DEFAULT)

        # TODO: Implement
