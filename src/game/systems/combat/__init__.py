import copy

from game.structures.manager import Manager
from game.systems.combat.resource import Resource


class ResourceManager(Manager):
    """
    A master manager that tracks the default state of all available Resources.
    """

    def __init__(self):
        super().__init__()

        self.master_resource_manifest: dict[str, Resource] = {}

    @property
    def all_resources(self) -> list[Resource]:
        """
        Generate a list of deep copies of each Resource in the master list

        Returns:
            A list of references to the Resources in the master list
        """
        return [copy.deepcopy(r) for r in self.master_resource_manifest.values()]

    def get_resource(self, resource_name: str) -> Resource:
        """
        Retrieves a deep copy of a master resource

        Args:
            resource_name (str): The name of the resource to retrieve

        Returns: A deep copy of the requested Resource
        """
        return copy.deepcopy(self.master_resource_manifest[resource_name])

    def register_resource(self, resource_object: Resource) -> None:
        """
        Add a resource to the master list.

        Args:
            resource_object (Resource): The Resource to add to the master list

        Returns: None
        """
        if not isinstance(resource_object, Resource):
            raise TypeError(f"Cannot register a non-resource object! Expected Resource, got {type(resource_object)}")

        if resource_object.name in self.master_resource_manifest:
            raise ValueError(f"Cannot register duplicate Resource of name {resource_object.name}")

        self.master_resource_manifest[resource_object.name] = resource_object

    def load(self) -> None:
        """
        Load resources from disk
        """
        pass

    def save(self) -> None:
        """
        Save resources to disk
        """
        pass


resource_manager: ResourceManager = ResourceManager()
