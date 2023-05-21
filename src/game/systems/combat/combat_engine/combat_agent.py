from __future__ import annotations

import weakref
from abc import ABC

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

    def make_choice(self) -> str | int | None:
        """
        Get an Entity's choice for its turn during Combat.

        An entity may do one of three things:
        - Pass
        - Use an Item
        - Use an Ability

        To pass, return None.
        To use an item, return its ID
        To use an ability, return its name
        """

        raise NotImplementedError()


class NaiveAgentMixin(CombatAgentMixin):
    name = "naive_agent"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def make_choice(self) -> str | int | None:
        pass


class IntelligentAgentMixin(CombatAgentMixin):
    name = "intelligent_agent"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def make_choice(self) -> str | int | None:
        pass


class MultiAgentMixin(CombatAgentMixin):
    AVAILABLE_AGENTS = [NaiveAgentMixin, IntelligentAgentMixin]
    AGENT_MAP = {agent.name: agent for agent in AVAILABLE_AGENTS}

    def __init__(self, combat_provider: str = "naive_agent", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.choice_provider: CombatAgentMixin = MultiAgentMixin.AGENT_MAP[combat_provider]()

    def make_choice(self) -> str | int | None:
        return self.choice_provider.make_choice()
