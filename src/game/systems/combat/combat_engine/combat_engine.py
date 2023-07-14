from __future__ import annotations

import copy
import weakref
from enum import Enum

import game.systems.entity.entities as entities
from game.cache import from_cache, cache_element
from game.structures.enums import CombatPhase, InputType
from game.structures.messages import ComponentFactory
from game.structures.state_device import FiniteStateDevice
from game.systems.combat.combat_engine.phase_handler import PhaseHandler, EffectActivator
from game.systems.combat.combat_engine.termination_handler import TerminationHandler, PlayerResourceCondition, \
    EnemyResourceCondition


class CombatEngine(FiniteStateDevice):
    PHASE_HANDLERS: dict[CombatPhase, list[type[PhaseHandler]]] = {
        CombatPhase.START_PHASE: [EffectActivator],
        CombatPhase.PRE_ACTION_PHASE: [EffectActivator],
        CombatPhase.ACTION_PHASE: [],
        CombatPhase.POST_ACTION_PHASE: [EffectActivator],
        CombatPhase.END_PHASE: [EffectActivator]
    }

    class States(Enum):
        DEFAULT = 0
        START_TURN_CYCLE = 1
        START_ENTITY_TURN = 2
        HANDLE_PHASE = 3  # For the current phase, call all phase handlers
        DETECT_COMBAT_TERMINATION = 4  # Call all TerminationHandlers and end combat if triggered
        PLAYER_LOSS = 5  # Player sucks and has lost
        PLAYER_VICTORY = 6  # Player doesn't suck and has won
        TERMINATE = -1

    @classmethod
    def get_master_phase_order(cls) -> list[CombatPhase]:
        return [
            CombatPhase.START_PHASE, CombatPhase.PRE_ACTION_PHASE, CombatPhase.ACTION_PHASE,
            CombatPhase.POST_ACTION_PHASE, CombatPhase.END_PHASE
        ]

    def __init__(self, ally_entity_ids: list[int], enemy_entity_ids: list[int],
                 termination_conditions: list[TerminationHandler] = None):
        super().__init__(InputType.ANY, self.States, self.States.DEFAULT)

        # Validate termination conditions
        self._termination_conditions = termination_conditions or self._get_default_termination_conditions()
        win_con_found = False
        loss_con_found = False
        for condition in self._termination_conditions:
            if condition.mode == TerminationHandler.TerminationMode.WIN:
                win_con_found = True
            else:
                loss_con_found = True

        if not win_con_found and loss_con_found:
            raise ValueError(
                "CombatEngine must have at least 1 win termination condition and 1 loss termination condition!"
            )

        # Master collections
        entity_manager = from_cache("managers.EntityManager")
        self._allies: list[entities.CombatEntity] = [entity_manager[e_id] for e_id in
                                                     ally_entity_ids]  # Master list of allied entities
        self._enemies: list[entities.CombatEntity] = [entity_manager[e_id] for e_id in
                                                      enemy_entity_ids]  # Master list of opposed entities
        self._player_ref: entities.Player = from_cache('player')
        self._allies.append(self._player_ref)

        # Master ordered lists
        self._turn_order: list[
            entities.CombatEntity] = []  # Proxied list of all entities arranged by index via turn order
        self._PHASE_ORDER = tuple(CombatEngine.get_master_phase_order())  # Ordered immutable collection of phases

        # State data for current turn
        self.total_turn_cycles: int = 0
        self.current_turn: int = 0
        self.current_phase: CombatPhase = CombatPhase.START_PHASE

        self._build_states()

        # Cache a global weak reference to this instance for later use by CombatSummary state devices.
        if from_cache("combat") is not None:
            raise RuntimeError("An active combat is already cached!")
        cache_element("combat", weakref.proxy(self))

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
        self._turn_order.sort(key=lambda x: x.turn_speed)

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

        ability = from_cache("managers.AbilityManager").get_ability(ability_name)

        if not ability.is_requirements_fulfilled(self.active_entity):
            raise RuntimeError(
                f"Cannot activate ability '{ability}! Requirements not met for entity: {self.active_entity}"
            )

        for target in targets:  # For each selected target of the chosen ability
            for phase, effects in ability.effects:  # Unpack the ability's effects into phases
                for effect in effects:  # Iterate through each effect and assign it to that phase on the target
                    effect_copy = copy.deepcopy(effect)  # Deepcopy may cause an issue

                    # Assign sources and targets from the deepcopy
                    effect_copy.assign(self.active_entity, target)
                    target.acquire_effect(effect_copy, phase)

        self.active_entity.ability_controller.consume_ability_resources(ability_name)

    def _handle_pass_turn(self) -> None:
        """
        The active entity has chosen to not make an action during its turn.
        """
        pass

    @property
    def active_entity(self) -> entities.CombatEntity:
        """
        Return a weakref to the active entity.
        """

        return self._turn_order[self.current_turn]

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

    def handle_turn_action(self, choice: int | str | None) -> None:
        """
        Perform the logic for executing the choice made by the active entity.
        """

        if type(choice) == int:
            self._handle_use_item(choice)
        elif type(choice) == str:
            self._handle_use_item(choice)
        elif choice is None:
            self._handle_pass_turn()
        else:
            raise TypeError(f"Unexpected type for choice! Expected str, int, None, got {type(choice)} instead!")

    @classmethod
    def _get_default_termination_conditions(cls) -> list[TerminationHandler]:
        """
        Returns a PlayerResourceCondition.Health == 0 for loss condition and an EnemyResourceCondition.Health == 0
        for a win condition.
        """

        return [
            PlayerResourceCondition("Heath", 0, PlayerResourceCondition.TerminationMode.WIN),
            EnemyResourceCondition("Heath", 0, EnemyResourceCondition.TerminationMode.LOSS),
        ]

    def _build_states(self) -> None:
        """
        Build the state logic and content providers for the FiniteStateDevice functionality of the CombatEngine.
        """
        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:

            self.set_state(self.States.START_TURN_CYCLE)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content():
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.START_TURN_CYCLE, InputType.SILENT)
        def logic(_: any) -> None:
            self.total_turn_cycles += 1
            self.set_state(self.States.START_ENTITY_TURN)

        @FiniteStateDevice.state_content(self, self.States.START_TURN_CYCLE)
        def content() -> dict:
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.START_ENTITY_TURN, InputType.SILENT)
        def logic(_: any) -> None:
            self.set_state(self.States.HANDLE_PHASE)

        @FiniteStateDevice.state_logic(self, self.States.HANDLE_PHASE, InputType.SILENT)
        def logic(_: any) -> None:
            for handler_cls in self.PHASE_HANDLERS[self.current_phase]:
                handler_cls().handle_phase(self)

            self.set_state(self.States.DETECT_COMBAT_TERMINATION)

        @FiniteStateDevice.state_content(self, self.States.HANDLE_PHASE)
        def content():
            return ComponentFactory.get()

        @FiniteStateDevice.state_logic(self, self.States.DETECT_COMBAT_TERMINATION, InputType.SILENT)
        def logic(_: any) -> None:
            pass

        @FiniteStateDevice.state_content(self, self.States.DETECT_COMBAT_TERMINATION)
        def content():
            return ComponentFactory.get()
