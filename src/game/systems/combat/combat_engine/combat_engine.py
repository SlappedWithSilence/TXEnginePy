import weakref
from abc import ABC

from game.systems.combat.combat_engine.phase_handler import PhaseHandler
from game.systems.entity.entities import CombatEntity
from game.structures.enums import CombatPhase


class CombatEngine:
    PHASE_HANDLERS: dict[CombatPhase, list[type]] = {
        CombatPhase.START_PHASE: [],
        CombatPhase.PRE_ACTION_PHASE: [],
        CombatPhase.ACTION_PHASE: [],
        CombatPhase.POST_ACTION_PHASE: [],
        CombatPhase.END_PHASE: []
    }

    @classmethod
    def get_master_phase_order(cls) -> list[CombatPhase]:
        return [
            CombatPhase.START_PHASE, CombatPhase.PRE_ACTION_PHASE, CombatPhase.ACTION_PHASE,
            CombatPhase.POST_ACTION_PHASE, CombatPhase.END_PHASE
        ]

    def __init__(self):
        # Master collections
        self._allies: list[CombatEntity] = []  # Master list of allied entities
        self._enemies: list[CombatEntity] = []  # Master list of opposed entities

        # Master ordered lists
        self._turn_order: list[CombatEntity] = []  # Proxied list of all entities arranged by index via turn order
        self._PHASE_ORDER = tuple(CombatEngine.get_master_phase_order())  # Ordered immutable collection of phases

        # State data for current turn
        self.current_turn: int = 0
        self.current_phase: CombatPhase = CombatPhase.START_PHASE

    def _handle_phase(self) -> None:
        """
        Dispatch handling of the current phase to a new instance of a designated handler.
        """
        for handler_class in self.PHASE_HANDLERS[self.current_phase]:
            handler: PhaseHandler = handler_class()
            handler.handle_phase(self)

    def _compute_turn_order(self):
        pass
