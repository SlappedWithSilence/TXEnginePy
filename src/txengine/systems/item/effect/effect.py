from abc import ABC


class Effect(ABC):
    def __init__(self):
        self.properties: list[str, int, float] = []

    def perform(self):
        """The heart of the Effect class. This method executes some arbitrary code based on the property values of the
        Effect

        This should always be overridden when creating subclasses of Effect.
        """
        pass


class FlatResourceEffect(Effect):
    """Changes one of the player's combat resources by a flat value

    The properties for this effect are [resource_name:str, change_value:int]
    """

    def __init__(self):
        super().__init__()

    def perform(self):
        pass


class LevelResourceEffect(Effect):
    """Changes one of the player's combat resources by a value scaled to their level.

    The properties for this effect are [resource_name:str, change_value:int, scale_factor:float]
    """

    def __init__(self):
        super().__init__()

    def perform(self):
        pass


class ProportionalResourceEffect(Effect):
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
        pass
