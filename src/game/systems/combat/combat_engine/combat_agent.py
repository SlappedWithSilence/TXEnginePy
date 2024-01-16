from __future__ import annotations

import random
import weakref
from abc import ABC

import game
from game.cache import from_cache
from game.structures.errors import CombatError
from game.systems.combat import Ability
from game.systems.combat.combat_engine.choice_data import ChoiceData


class CombatAgentMixin(ABC):
    """
    A mixin that allows for CombatEngine integration. Mixin MUST be applied to a CombatEntity instance.
    """
    name = "abstract_agent"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        from game.systems.entity.entities import CombatEntity
        if not isinstance(self, CombatEntity):
            raise TypeError("CombatAgentMixin must mixed with a CombatEntity instance!")

    def _choice_logic(self) -> ChoiceData:
        """
        Get an Entity's choice for its turn during Combat.

        An entity may do one of three things:
        - Pass
        - Use an Item
        - Use an Ability

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
    """
    A Naive CombatEntity selects abilities at random at targets for those abilities at random.
    """
    name = "naive_agent"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _choice_logic(self) -> ChoiceData:
        r = random.Random()
        ab: str = r.choice(self.ability_controller.abilities)
        targets = from_cache("combat").get_ability_targets(self, ab)

        target = r.choice(targets)

        return ChoiceData(ChoiceData.ChoiceType.ABILITY, ability_name=ab, ability_target=target)


class IntelligentAgentMixin(CombatAgentMixin):
    name = "intelligent_agent"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def _choice_logic(self) -> ChoiceData:
        return ChoiceData(ChoiceData.ChoiceType.PASS)


class MultiAgentMixin(CombatAgentMixin):
    AVAILABLE_AGENTS = [NaiveAgentMixin, IntelligentAgentMixin]
    AGENT_MAP = {agent.name: agent for agent in AVAILABLE_AGENTS}

    def __init__(self, combat_provider: str = "naive_agent", *args, **kwargs):
        super().__init__(**kwargs)
        self.choice_provider: CombatAgentMixin = MultiAgentMixin.AGENT_MAP[combat_provider]()

    def _choice_logic(self) -> ChoiceData:
        return self.choice_provider._choice_logic()


class PlayerAgentMixin(CombatAgentMixin):
    """
    A CombatAgentMixin that makes the player choose what to do.
    """

    def _choice_logic(self) -> ChoiceData:
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
        from game.systems.combat.combat_engine.player_combat_choice_event import PlayerCombatChoiceEvent
        game.state_device_controller.add_state_device(PlayerCombatChoiceEvent(self))
