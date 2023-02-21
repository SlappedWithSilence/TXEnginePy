import copy

from game.structures.messages import StringContent
import game.systems.entity as entity

import dataclasses


@dataclasses.dataclass
class Resource:
    """
    Represents an entity resource, ex: Health, Mana, Stamina, etc
    """
    name: str
    value: int
    max: int
    description: str

    def __str__(self) -> str:
        return f"[{self.name}: {self.value}/{self.max}]"

    def __repr__(self) -> list[StringContent]:
        return [
            StringContent(value="["),
            StringContent(value=self.name, formatting="resource_name"),
            StringContent(value=": "),
            StringContent(value=str(self.value), formatting="resource_value"),
            StringContent(value="/"),
            StringContent(value=str(self.max), formatting="resource_max"),
            StringContent(value="]")
        ]


class ResourceController:
    """
    A controller that manages an individual entity's resources.
    """

    def __init__(self, resources: list[tuple[str, int, int] | Resource] = None):

        self.resources: dict[str, Resource] = {r.name: r for (r, r.name) in entity.resource_manager.all_resources}

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
