from __future__ import annotations

import copy
import weakref
from enum import Enum

from loguru import logger

import game
import game.systems.entity.entities as entities
from game.cache import from_cache, cache_element, delete_element, get_config
from game.structures.enums import CombatPhase, InputType, TargetMode
from game.structures.errors import CombatError
from game.structures.state_device import FiniteStateDevice
from game.systems.combat.combat_engine.choice_data import ChoiceData
from game.systems.combat.combat_engine.phase_handler import PhaseHandler, EffectActivator, ChoiceActivator
from game.systems.combat.combat_engine.termination_handler import TerminationHandler, PlayerResourceCondition, \
    EnemyResourceCondition, GroupResourceCondition


class CombatEngine(FiniteStateDevice):
    PHASE_HANDLERS: dict[CombatPhase, list[type[PhaseHandler]]] = {
        CombatPhase.START_PHASE: [EffectActivator],
        CombatPhase.PRE_ACTION_PHASE: [EffectActivator],
        CombatPhase.ACTION_PHASE: [ChoiceActivator],
        CombatPhase.POST_ACTION_PHASE: [EffectActivator],
        CombatPhase.END_PHASE: [EffectActivator]
    }

    class States(Enum):
        DEFAULT = 0
        START_TURN_CYCLE = 1
        START_ENTITY_TURN = 2
        HANDLE_PHASE = 3  # For the current phase, call all phase handlers
        NEXT_PHASE = 4
        DETECT_COMBAT_TERMINATION = 5  # Call all TerminationHandlers and end combat if triggered
        PLAYER_LOSS = 6  # Player sucks and has lost
        PLAYER_VICTORY = 7  # Player doesn't suck and has won
        EXECUTE_ENTITY_CHOICE = 8
        TERMINATE = -1

    def __init__(self, ally_entity_ids: list[int], enemy_entity_ids: list[int],
                 termination_conditions: list[TerminationHandler] = None):
        super().__init__(InputType.ANY, self.States, self.States.DEFAULT)

        # Verify that there's at least one win and one loss condition
        self._termination_conditions = termination_conditions or self._get_default_termination_conditions()
        win_con_found = False
        loss_con_found = False
        for condition in self._termination_conditions:
            if condition.termination_mode == TerminationHandler.TerminationMode.WIN:
                win_con_found = True
            else:
                loss_con_found = True

        if not (win_con_found and loss_con_found):
            raise ValueError(
                "CombatEngine must have at least 1 win termination condition and 1 loss termination condition!"
            )

        if len(enemy_entity_ids) < 1:
            raise ValueError("Combat must have at least one enemy entity!")

        # Master collections
        entity_manager = from_cache("managers.EntityManager")
        self._allies: list[entities.CombatEntity] = [entity_manager[e_id] for e_id in ally_entity_ids]  # alies
        self._enemies: list[entities.CombatEntity] = [entity_manager[e_id] for e_id in enemy_entity_ids]  # enemies
        self._player_ref: entities.Player = from_cache('player')
        self._allies.append(self._player_ref)

        # Ordered lists
        self._turn_order: list[
            entities.CombatEntity] = []  # Proxied list of all entities arranged by index via turn order
        self._PHASE_ORDER = tuple(CombatEngine.get_master_phase_order())  # Ordered immutable collection of phases

        # State data for current turn
        self.total_turn_cycles: int = 0
        self.current_turn: int = -1  # Start at -1 so that when combat begins the index can be incremented to 0
        self.current_phase_index: int = 0  # Index of current phase against self._PHASE_ORDER

        # The choice made by the active entity during the ACTION_PHASE combat phase
        self.active_entity_choice: ChoiceData = None

        self._build_states()

        # Cache a global weak reference to this instance for later use by CombatSummary state devices.
        if from_cache("combat") is not None:
            raise RuntimeError("An active combat is already cached!")

        cache_element("combat", self)

    # Private helper functions

    def _handle_phase(self) -> None:
        """
        Dispatch handling of the current phase to a new instance of a designated handler.

        Each type that is mapped to the current combat phase is instantiated statelessly and passed a reference to self.
        Handlers are instantiated and activated in the order that they are stored in the PHASE_HANDLERS dict.
        """

        for handler_class in self.PHASE_HANDLERS[self.current_phase]:
            handler: PhaseHandler = handler_class()
            handler.handle_phase(self)

    def _compute_turn_order(self):
        """
        Determine turn order by sorting all entities via turn_speed
        """

        # Build the weakref list if it doesn't exist
        if self._turn_order is None or len(self._turn_order) == 0:
            self._turn_order = [weakref.proxy(e) for e in self._allies + self._enemies]

        # Sort in place
        self._turn_order.sort(key=lambda x: x.turn_speed, reverse=True)

    def _handle_use_item(self, item_id: int) -> None:
        """
        The active entity has chosen to ue an Item. Handle its usage.
        """
        from game.systems.item.item import Usable

        # Get an instance of the item
        item_instance = from_cache("managers.ItemManager").get_instance(item_id)

        # Type check
        if not isinstance(item_instance, Usable):
            raise TypeError(f"Cannot use {item_instance}! Not an instance of Usable!")

        # Use the item on the active entity, then decrement its quantity
        item_instance.use(self.active_entity)
        self.active_entity.inventory.consume_item(item_id, 1)

    def _handle_use_ability(self, ability_name: str, targets: list[entities.CombatEntity]) -> None:
        """
        The active entity has chosen to use an Ability. Handle its usage.
        """

        if type(ability_name) is not str:
            raise TypeError()

        ability = from_cache("managers.AbilityManager").get_instance(ability_name)

        if not ability.is_requirements_fulfilled(self.active_entity):
            raise RuntimeError(
                f"Cannot activate ability '{ability}! Requirements not met for entity: {self.active_entity}"
            )

        _targets = targets if type(targets) == list else [targets]

        for target in _targets:  # For each selected target of the chosen ability
            for phase, effects in ability.effects.items():  # Unpack the ability's effects into phases
                for effect in effects:  # Iterate through each effect and assign it to that phase on the target
                    effect_copy = copy.deepcopy(effect)  # Deepcopy may cause an issue

                    # Assign sources and targets from the deepcopy
                    effect_copy.assign(self.active_entity, target)
                    target.acquire_effect(effect_copy, phase)

                target.resource_controller[get_config()["resources"]["primary_resource"]].adjust(ability.damage * -1)

        self.active_entity.ability_controller.consume_ability_resources(ability_name)

    def _handle_pass_turn(self) -> None:
        """
        The active entity has chosen to not make an action during its turn.
        """
        pass

    # Public methods
    def get_relative_allies(self, entity: entities.CombatEntity) -> list[entities.CombatEntity]:
        """
        Fetch a list of entities that are the allies of the given entity.

        For example, an entity that is in the enemies list would return the enemeies list.
        """
        if entity in self.allies:
            return self.allies

        elif entity in self.enemies:
            return self.enemies

        else:
            raise CombatError(f"Failed to get relative allies! Unknown entity: {entity}")

    def get_relative_enemies(self, entity: entities.CombatEntity) -> list[entities.CombatEntity]:
        """
        Fetch a list of entities that are the enemies of the given entity.

        For example, an entity that is in the enemies list would return the allies list.
        """

        if entity in self.allies:
            return self.enemies

        elif entity in self.enemies:
            return self.allies

        else:
            raise CombatError(f"Failed to get relative enemies! Unknown entity: {entity}")

    def get_ability_targets(self, entity: entities.CombatEntity, ability_name: str) -> list[entities.CombatEntity]:
        """
        Fetch a list of entities that can be targeted by a given ability.

        Abilities that target groups (ie ALL_ALLIES, ALL_ENEMIES, ALL, etc) will return an empty list; there's no
        targeting to be done.

        args:
            entity: The CombatEntity that is performing the targeting
            ability_name: The name of the Ability that `entity` will be performing

        returns:
            A list of CombatEntities from among all participants in combat that are valid targets for `ability_name`
        """

        if not isinstance(entity, entities.CombatEntity):
            raise TypeError(f"argument `entity` is not of type CombatEntity! Got {type(entity)} instead.")

        if type(ability_name) is not str:
            raise TypeError(f"argument `ability_name` is not of type str! Got {type(ability_name)} instead.")
        target_mode: TargetMode = from_cache("managers.AbilityManager").get_instance(ability_name).target_mode

        match target_mode:

            # Return a list of all entities
            case TargetMode.SINGLE:
                return self.allies + self.enemies

            # Return a list of all entities that are not `entity`
            case TargetMode.NOT_SELF:
                return [ally for ally in self.allies is not entity] + \
                    [enemy for enemy in self.enemies if enemy is not entity]

            # Return a list of all relative allies
            case TargetMode.SINGLE_ALLY:
                return self.get_relative_allies(entity)

            # Return a list of all relative enemies
            case TargetMode.SINGLE_ENEMY:
                return self.get_relative_enemies(entity)

            case TargetMode.ALL:
                return self.enemies + self.allies
            case TargetMode.ALL_ALLY:
                return self.get_relative_allies(entity)
            case TargetMode.ALL_ENEMY:
                return self.get_relative_enemies(entity)

            case _:
                raise CombatError(f'Unknown targeting mode: {target_mode}')

    def submit_entity_choice(self, entity, choice: ChoiceData) -> None:
        """
        Submit an entity's turn action to the combat engine from any context.
        """

        # Validate the entity that's submitted a choice
        from game.systems.entity.entities import CombatEntity
        if not isinstance(entity, CombatEntity):
            raise TypeError(f"Entity's that submit choices must be of type CombatEntity! Got {type(entity)} instead.")

        if entity != self.active_entity:
            raise RuntimeError("An entity that is not the active entity has submitted a choice!")

        # Type and value checking
        if choice is not None and type(choice) is not ChoiceData:
            raise TypeError(f"Unknown type for entity choice: {type(choice)}. Expected type ChoiceData!")

        # Store choice for later
        self.active_entity_choice = choice

    def handle_turn_action(self, choice: ChoiceData) -> None:
        """
        Perform the logic for executing the choice made by the active entity.
        """

        if choice.choice_type == ChoiceData.ChoiceType.ITEM:
            self._handle_use_item(choice.item_id)
        elif choice.choice_type == ChoiceData.ChoiceType.ABILITY:
            self._handle_use_ability(choice.ability_name, choice.ability_target)
        elif choice.choice_type.PASS:
            self._handle_pass_turn()
        else:
            raise TypeError(f"Unexpected type for choice! Expected str, int, None, got {type(choice)} instead!")

    # Properties

    @property
    def current_phase(self) -> CombatPhase:
        return self._PHASE_ORDER[self.current_phase_index]

    @property
    def active_entity(self) -> entities.CombatEntity:
        """
        Return a weakref to the active entity.
        """

        return self._turn_order[self.current_turn] if self.current_turn < len(self._turn_order) else None

    @property
    def next_entity(self) -> entities.CombatEntity | None:
        """
        Return a weakref to next active Entity.
        """
        return self.current_turn + 1 if self.current_turn < len(self._turn_order) - 1 else None

    @property
    def enemies(self) -> list[entities.CombatEntity]:
        return self._enemies

    @property
    def allies(self) -> list[entities.CombatEntity]:
        return self._allies

    # Class Methods

    @classmethod
    def _get_default_termination_conditions(cls) -> list[TerminationHandler]:
        """
        Returns a PlayerResourceCondition.Health == 0 for loss condition and an EnemyResourceCondition.Health == 0
        for a win condition.
        """

        primary_resource = get_config()['resources']['primary_resource']

        return [
            PlayerResourceCondition(
                primary_resource, 0, TerminationHandler.TerminationMode.WIN, GroupResourceCondition.Mode.LESS_THAN),
            EnemyResourceCondition(
                primary_resource, 0, TerminationHandler.TerminationMode.LOSS, GroupResourceCondition.Mode.LESS_THAN),
        ]

    @classmethod
    def get_master_phase_order(cls) -> list[CombatPhase]:
        return [
            CombatPhase.START_PHASE, CombatPhase.PRE_ACTION_PHASE, CombatPhase.ACTION_PHASE,
            CombatPhase.POST_ACTION_PHASE, CombatPhase.END_PHASE
        ]

    # State logic

    def _build_states(self) -> None:
        """
        Build the state logic and content providers for the FiniteStateDevice functionality of the CombatEngine.
        """
        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:

            self.set_state(self.States.START_TURN_CYCLE)

        @FiniteStateDevice.state_logic(self, self.States.START_TURN_CYCLE, InputType.SILENT)
        def logic(_: any) -> None:
            self._compute_turn_order()
            self.total_turn_cycles += 1
            self.current_turn = -1
            self.set_state(self.States.START_ENTITY_TURN)

        @FiniteStateDevice.state_logic(self, self.States.START_ENTITY_TURN, InputType.SILENT)
        def logic(_: any) -> None:
            self.current_turn += 1  # Increment turn index
            self.current_phase_index = 0  # Reset phase index to 0 (Start phase)

            if self.active_entity:  # If incremented position is in range, handle the turn's phase logic
                self.set_state(self.States.HANDLE_PHASE)
            else:  # If not, then all entities have had a turn, start a new turn cycle
                self.set_state(self.States.START_TURN_CYCLE)

        @FiniteStateDevice.state_logic(self, self.States.HANDLE_PHASE, InputType.SILENT)
        def logic(_: any) -> None:

            # Check if the current phase index is out of bounds. If so, start the next entity's turn and reset phase.
            if self.current_phase_index >= len(self._PHASE_ORDER):
                self.set_state(self.States.START_ENTITY_TURN)
                return

            for handler_cls in self.PHASE_HANDLERS[self.current_phase]:
                handler_cls().handle_phase()

            self.set_state(self.States.DETECT_COMBAT_TERMINATION)

            if self.current_phase == CombatPhase.ACTION_PHASE:
                self.set_state(self.States.EXECUTE_ENTITY_CHOICE)

        @FiniteStateDevice.state_logic(self, self.States.EXECUTE_ENTITY_CHOICE, InputType.SILENT)
        def logic(_: any):
            self.handle_turn_action(self.active_entity_choice)
            self.set_state(self.States.DETECT_COMBAT_TERMINATION)

        @FiniteStateDevice.state_logic(self, self.States.DETECT_COMBAT_TERMINATION, InputType.SILENT)
        def logic(_: any) -> None:
            loss = False
            win = False
            for termination_condition in self._termination_conditions:
                try:
                    if termination_condition.is_conditions_met():
                        if termination_condition.mode == TerminationHandler.TerminationMode.WIN:
                            win = True
                        else:
                            loss = True

                except Exception as e:
                    logger.error("An error was raised while running a TerminationHandler.")
                    logger.error(f"class: {termination_condition.__class__}")
                    raise e

            if loss:
                self.set_state(self.States.PLAYER_LOSS)
            elif win:
                self.set_state(self.States.PLAYER_VICTORY)
            else:
                self.set_state(self.States.NEXT_PHASE)

        @FiniteStateDevice.state_logic(self, self.States.NEXT_PHASE, InputType.SILENT)
        def logic(_: any):
            self.current_phase_index += 1
            self.set_state(self.States.HANDLE_PHASE)

        @FiniteStateDevice.state_logic(self, self.States.TERMINATE, InputType.SILENT, override=True)
        def logic(_: any) -> None:
            delete_element("combat")  # Kill the global combat reference
            game.state_device_controller.set_dead()  # Set self as dead to be removed from the stack
