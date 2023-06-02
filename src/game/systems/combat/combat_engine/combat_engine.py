from __future__ import annotations

import weakref
from enum import Enum

import game.systems.entity.entities as entities
from game.cache import from_cache, cache_element
from game.structures.enums import CombatPhase, InputType
from game.structures.messages import ComponentFactory
from game.structures.state_device import FiniteStateDevice
from game.systems.combat.combat_engine.phase_handler import PhaseHandler, EffectActivator


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
        HANDLE_PHASE = 1
        DETECT_COMBAT_TERMINATION = 2
        PLAYER_LOSS = 3
        PLAYER_VICTORY = 4
        TERMINATE = -1

    @classmethod
    def get_master_phase_order(cls) -> list[CombatPhase]:
        return [
            CombatPhase.START_PHASE, CombatPhase.PRE_ACTION_PHASE, CombatPhase.ACTION_PHASE,
            CombatPhase.POST_ACTION_PHASE, CombatPhase.END_PHASE
        ]

    def __init__(self, ally_entity_ids: list[int], enemy_entity_ids: list[int]):
        super().__init__(InputType.ANY, self.States, self.States.DEFAULT)

        # Master collections
        entity_manager = from_cache("managers.EntityManager")
        self._allies: list[entities.CombatEntity] = [entity_manager[e_id] for e_id in
                                                     ally_entity_ids]  # Master list of allied _entity_manifest
        self._enemies: list[entities.CombatEntity] = [entity_manager[e_id] for e_id in
                                                      enemy_entity_ids]  # Master list of opposed _entity_manifest
        self._player_ref: entities.Player = from_cache('player')
        self._allies.append(self._player_ref)

        # Master ordered lists
        self._turn_order: list[
            entities.CombatEntity] = []  # Proxied list of all entities arranged by index via turn order
        self._PHASE_ORDER = tuple(CombatEngine.get_master_phase_order())  # Ordered immutable collection of phases

        # State data for current turn
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
        pass

    def _handle_use_ability(self, ability_name: str) -> None:
        """
        The active entity has chosen to use an Ability. Handle its usage.
        """
        pass

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

    def _build_states(self) -> None:
        """
        Build the state logic and content providers for the FiniteStateDevice functionality of the CombatEngine.
        """
        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:

            self.set_state(self.States.HANDLE_PHASE)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content():
            return ComponentFactory.get()

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
