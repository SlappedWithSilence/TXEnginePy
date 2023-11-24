from abc import ABC

import game
import game.systems.entity.entities as entities
from loguru import logger

from game.cache import from_cache
from game.structures.errors import CombatError


class PhaseHandler(ABC):

    def __init__(self):
        pass

    def _phase_logic(self) -> None:
        """
        Inner logic for executive phase handling.
        """
        raise NotImplementedError()

    def handle_phase(self) -> None:
        """
        Wrapper for _phase_logic that provides consistent stateless error checking against the combat_engine.
        """
        ce = from_cache("combat")

        logger.debug(f"current_turn: {ce.current_turn}")
        logger.debug(f"current_phase: {ce.current_phase}")
        logger.debug(f"turn_order: {ce._turn_order}")

        if ce.active_entity is None or not isinstance(ce.active_entity, entities.CombatEntity):
            raise CombatError(
                f"Active entity must be instance of CombatEntity! Got {type(ce.active_entity)} instead!",
                {TypeError: "Invalid active_entity type"}
            )

        self._phase_logic()


class EffectActivator(PhaseHandler):
    """
    For the active entity, activate all Effects that are stored in it for the current Phase.

    Since Effects are StateDevices, put them on the StateDevice stack and execute them state-wise. The LAST-CREATED
    EFFECT is resolved first (LIFO order).
    """

    def _phase_logic(self) -> None:
        ce = from_cache("combat")

        active_entity: entities.CombatEntity = ce.active_entity

        for effect in reversed(active_entity.active_effects[ce.current_phase]):
            effect.reset()  # Reset the Effect state device in case it was previously used
            game.state_device_controller.add_state_device(effect)  # Add it to the stack


class ChoiceActivator(PhaseHandler):
    """
    For the active entity, compute that entity's turn choice.
    """

    def _phase_logic(self) -> None:
        """
        Compute the choice made by the active entity and pass it back to the combat_engine instance to handle execution.
        """
        ce = from_cache("combat")
        logger.debug(f"Running ChoiceActivator logic for entity {ce.active_entity.name}")
        ce.active_entity.make_choice()

