from __future__ import annotations

import weakref

from game.cache import from_cache
from game.structures.enums import CombatPhase
from game.systems.combat.combat_engine.phase_handler import PhaseHandler, EffectActivator
import game.systems.entity.entities as entities


class CombatEngine:

    PHASE_HANDLERS: dict[CombatPhase, list[type]] = {
        CombatPhase.START_PHASE: [EffectActivator],
        CombatPhase.PRE_ACTION_PHASE: [EffectActivator],
        CombatPhase.ACTION_PHASE: [],
        CombatPhase.POST_ACTION_PHASE: [EffectActivator],
        CombatPhase.END_PHASE: [EffectActivator]
    }

    @classmethod
    def get_master_phase_order(cls) -> list[CombatPhase]:
        return [
            CombatPhase.START_PHASE, CombatPhase.PRE_ACTION_PHASE, CombatPhase.ACTION_PHASE,
            CombatPhase.POST_ACTION_PHASE, CombatPhase.END_PHASE
        ]

    def __init__(self, ally_entity_ids: list[int], enemy_entity_ids: list[int]):
        # Master collections
        entity_manager = from_cache("managers.EntityManager")
        self._allies: list[entities.CombatEntity] = [entity_manager[e_id] for e_id in ally_entity_ids]  # Master list of allied _entity_manifest
        self._enemies: list[entities.CombatEntity] = [entity_manager[e_id] for e_id in enemy_entity_ids]  # Master list of opposed _entity_manifest
        self._player_ref: entities.Player = from_cache('player')

        # Master ordered lists
        self._turn_order: list[entities.CombatEntity] = []  # Proxied list of all _entity_manifest arranged by index via turn order
        self._PHASE_ORDER = tuple(CombatEngine.get_master_phase_order())  # Ordered immutable collection of phases

        # State data for current turn
        self.current_turn: int = 0
        self.current_phase: CombatPhase = CombatPhase.START_PHASE

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
