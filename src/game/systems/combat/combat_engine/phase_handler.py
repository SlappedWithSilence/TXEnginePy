from abc import ABC


class PhaseHandler(ABC):

    def __init__(self):
        pass

    def handle_phase(self, combat_engine) -> None:
        raise NotImplementedError()


class EffectActivator(PhaseHandler):
    """
    For the active entity, activate all Effects that are stored in it for the current Phase.
    """

    def handle_phase(self, combat_engine) -> None:
        active_entity = combat_engine.turn_order[combat_engine.current_turn]

        for effect in active_entity.active_effects[combat_engine.current_phase]:
            effect.perform()  # Assumes that the effect has already been assigned
