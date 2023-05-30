from abc import ABC

import game
import game.systems.entity.entities as entities


class PhaseHandler(ABC):

    def __init__(self):
        pass

    def _phase_logic(self, combat_engine) -> None:
        """
        Inner logic for executive phase handling.
        """
        raise NotImplementedError()

    def handle_phase(self, combat_engine) -> None:
        """
        Wrapper for _phase_logic that provides consistent stateless error checking against the combat_engine.
        """

        if combat_engine.active_entity is None or not isinstance(combat_engine.active_entity, entities.CombatEntity):
            raise TypeError(
                f"Active entity must be instance of CombatEntity! Got {type(combat_engine.active_entity)} instead!")

        self._phase_logic(combat_engine)


class EffectActivator(PhaseHandler):
    """
    For the active entity, activate all Effects that are stored in it for the current Phase.

    Since Effects are StateDevices, put them on the StateDevice stack and execute them state-wise. The LAST-CREATED
    EFFECT is resolved first (LIFO order).
    """

    def _phase_logic(self, combat_engine) -> None:
        active_entity: entities.CombatEntity = combat_engine.active_entity

        for effect in reversed(active_entity.active_effects[combat_engine.current_phase]):
            effect.reset()  # Reset the Effect state device in case it was previously used
            game.state_device_controller.add_state_device(effect)  # Add it to the stack


class ChoiceActivator(PhaseHandler):
    """
    For the active entity, compute that entity's turn choice.
    """

    def _phase_logic(self, combat_engine) -> None:
        """
        Compute the choice made by the active entity and pass it back to the combat_engine instance to handle execution.
        """

        combat_engine.handle_turn_action(combat_engine.active_entity.make_choice())


class LossDetector(PhaseHandler):
    """
    Detect if the conditions for a loss have been met and inform the CombatEngine.
    """

    def _phase_logic(self, combat_engine) -> None:
        pass


class VictoryDetector(PhaseHandler):
    """
    Detect if the conditions for a win have been met and inform the CombatEngine.
    """

    def _phase_logic(self, combat_engine) -> None:
        pass
