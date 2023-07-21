from __future__ import annotations

import weakref
from abc import ABC

import game
from game.cache import from_cache
from game.structures.errors import CombatError
from game.systems.combat.combat_engine.combat_engine import CombatEngine


class CombatAgentMixin(ABC):
    """
    A mixin that allows for CombatEngine integration.
    """
    name = "abstract_agent"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._combat_engine: CombatEngine | None = None

    @property
    def combat_engine(self) -> CombatEngine:
        return self._combat_engine

    @combat_engine.setter
    def combat_engine(self, element) -> None:
        """
        Set a reference to the CombatEngine or remove the existing reference.
        """
        if element is None:
            self._combat_engine = None

        elif isinstance(element, CombatEngine):
            self._combat_engine = weakref.proxy(element)

        else:
            raise TypeError(f"Cannot set combat engine to object of type {type(element)}!")

    def _choice_logic(self) -> str | int | None:
        """
        Get an Entity's choice for its turn during Combat.

        An entity may do one of three things:
        - Pass
        - Use an Item
        - Use an Ability

        To pass, return None.
        To use an item, return its ID
        To use an ability, return its name

        To collect information about the combat's context, retrieve it via  from_cache("combat")
        """
        raise NotImplementedError()

    def make_choice(self) -> None:
        """
        A wrapper for _choice_logic that performs instance checking and validation before submitting the entity choice
        to the combat engine.
        """

        from_cache("combat").submit_entity_choice(self, self._choice_logic())


class NaiveAgentMixin(CombatAgentMixin):
    name = "naive_agent"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _choice_logic(self) -> str | int | None:
        return None  # TODO: Implement


class IntelligentAgentMixin(CombatAgentMixin):
    name = "intelligent_agent"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _choice_logic(self) -> str | int | None:
        return None  # TODO: Implement


class MultiAgentMixin(CombatAgentMixin):
    AVAILABLE_AGENTS = [NaiveAgentMixin, IntelligentAgentMixin]
    AGENT_MAP = {agent.name: agent for agent in AVAILABLE_AGENTS}

    def __init__(self, combat_provider: str = "naive_agent", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choice_provider: CombatAgentMixin = MultiAgentMixin.AGENT_MAP[combat_provider]()

    def _choice_logic(self) -> str | int | None:
        return self.choice_provider.make_choice()


class PlayerAgentMixin(CombatAgentMixin):
    """
    A CombatAgentMixin that makes the player choose what to do.
    """

    def _choice_logic(self) -> str | int | None:
        """
        Dead method. Ignore.
        """
        pass

    def make_choice(self) -> None:
        """
        Spawn a 'PlayerCombatChoiceEvent' and let it handle submitting combat choices to the global combat instance.
        """
        if not from_cache("combat"):
            raise CombatError("Unable to retrieve valid combat instance!")

        # Spawn an event to handle player choice flow.
        # Note that this method does not submit anything to the combat engine directly, all of that is handled within
        # the PlayerCombatChoiceEvent's logic.
        game.state_device_controller.add_state_device(PlayerCombatChoiceEvent(self))