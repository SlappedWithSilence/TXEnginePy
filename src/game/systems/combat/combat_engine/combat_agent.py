import weakref
from abc import ABC

from game.systems.combat.combat_engine.combat_engine import CombatEngine


class CombatAgentMixin(ABC):
    """
    A mixin that allows for CombatEngine integration.
    """

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
