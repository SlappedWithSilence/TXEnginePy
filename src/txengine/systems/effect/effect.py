from abc import ABC

from ..event.events import AbilityEvent
from ...cache import config
from ..player import player


class Effect(ABC):
    def __init__(self):
        self.properties: list[str] = []

    def perform(self):
        """The heart of the Effect class. This method executes some arbitrary code based on the property values of the
        Effect

        This should always be overridden when creating subclasses of Effect.
        """
        pass


class FlatStatEffect(Effect):
    """Changes one of the player's combat resources by a flat value

    The properties for this effect are [resource_name:str, change_value:int]
    """

    def __init__(self):
        super().__init__()

        if len(self.properties) != 2:
            raise ValueError(f"FlatStatEffect must have exactly two properties! Got {len(self.properties)}")

    def perform(self):
        try:
            stat_name: str = self.properties[0]
            change_value: int = int(self.properties[1])
            player.stats[stat_name].adjust(change_value)
        except TypeError:
            raise ValueError(f"FlatStatEffect's properties must be typed [str, int]!")


class LevelStatEffect(Effect):
    """Changes one of the player's combat resources by a value scaled to their level.

    The properties for this effect are [resource_name:str, change_value:int, scale_factor:float]
    """

    def __init__(self):
        super().__init__()

        if len(self.properties) != 3:
            raise ValueError(f"LevelStatEffect must have exactly three properties! Got {len(self.properties)}")

    def perform(self):

        try:
            stat_name: str = self.properties[0]
            change_value: int = int(self.properties[1])
            scale_factor: float = float(self.properties[2])

            adjustment: int = (player.skills[config['primary_skill']].level * scale_factor) + change_value
            player.stats[stat_name].adjust(int(adjustment))
        except TypeError:
            raise ValueError(f"LevelStatEffect's properties must be typed [str, int, float]!")


class ProportionalStatEffect(Effect):
    """Changes one of the player's combat resources scaled to that resource's current value.

    The properties for this effect are [resource_name:str, change_percentage:float].
    The formula is resource = resource + resource*change_percentage, so a change_percentage value of 0.10 would increase
    the resource's value by 10%.
    """

    def __init__(self):
        super().__init__()

    def perform(self):
        pass


class TeachAbilityEffect(Effect):
    """Teaches the player a specified ability.

    The properties for this effect are [ability_name:str]
    """

    def __init__(self):
        super().__init__()

    def perform(self):
        ae = AbilityEvent([self.properties[0]])
        ae.perform()
