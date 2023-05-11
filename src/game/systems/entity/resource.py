import copy

from game.structures.messages import StringContent
import game.systems.entity as entity

import dataclasses

from loguru import logger

@dataclasses.dataclass
class Resource:
    """
    Represents an entity resource, ex: Health, Mana, Stamina, etc
    """
    name: str
    value: int
    max: int
    description: str

    def test_adjust(self, amount: int | float) -> int:
        """
        Fake adjusts the value of the Resource. If amount is int, value is added to amount. If amount is float, value
        is added to (value*amount).

        Args:
            amount: An int or float that determines how the resource's value is changed.

        Returns:
            What the Resource's value would be after the adjustment
        """

        if type(amount) == int:
            return max(0, min(self.max, self.value + amount))

        elif type(amount) == float:
            return max(0, min(self.max, self.value + (self.value * amount)))

        else:
            raise TypeError(f"Cannot adjust Resource by type {type(amount)}! Must be int or float.")

    def adjust(self, amount: int | float) -> int:
        """
        Adjusts the value of the Resource. If amount is an int, value is added to amount. If amount is a float, value
        is added to (value*amount).

        Args:
            amount: An int or float that determines how the resource's value is changed.

        Returns:
            The Resource's value after the adjustment
        """

        self.value = self.test_adjust(amount)
        logger.debug(f"Setting value to {self.test_adjust(amount)}")
        return self.value

    def __str__(self) -> str:
        return f"[{self.name}: {self.value}/{self.max}]"

    def __txengine__repr__(self) -> list[StringContent]:
        return [
            StringContent(value="["),
            StringContent(value=self.name, formatting="resource_name"),
            StringContent(value=": "),
            StringContent(value=str(self.value), formatting="resource_value"),
            StringContent(value="/"),
            StringContent(value=str(self.max), formatting="resource_max"),
            StringContent(value="]")
        ]

    def __repr__(self):
        return self.__str__()


class ResourceController:
    """
    A controller that manages an individual entity's resources.
    """

    def __init__(self, resources: list[tuple[str, int, int] | Resource] = None):

        self.resources: dict[str, Resource] = {r.name: r for r in entity.resource_manager.all_resources}

        if resources:
            if type(resources) != list:
                raise TypeError(f"ResourceController.resources must be of type list! Got {type(resources)} instead.")

            for overloaded_resource in resources:
                if type(overloaded_resource) == Resource:
                    if overloaded_resource.name not in self.resources:
                        raise ValueError(
                            f"Cannot overload a resource that doesn't exist! Unknown resource: {overloaded_resource.name}")

                    self.resources[overloaded_resource.name] = copy.deepcopy(overloaded_resource)

                elif type(overloaded_resource) == tuple[str, int, int]:
                    if overloaded_resource[0] not in self.resources:
                        raise ValueError(
                            f"Cannot overload a resource that doesn't exist! Unknown resource: {overloaded_resource[0]}")

                    self.resources[overloaded_resource[0]].value = overloaded_resource[1]
                    self.resources[overloaded_resource[0]].max = overloaded_resource[2]

    def __contains__(self, resource: str | Resource) -> bool:
        if type(resource) == str:
            return resource in self.resources
        elif type(resource) == Resource:
            return resource.name in self.resources

        return False

    def __getitem__(self, item) -> Resource:
        return self.resources.__getitem__(item)

    def __setitem__(self, key, value) -> None:
        self.resources.__setitem__(key, value)
