from .resource import EntityResource


class Entity:

    def __init__(self, name: str, resources: dict[str, EntityResource], skills: dict[str, any]):
        self.name: str = name
        self.resources: dict[str, EntityResource] = resources
        self.skills: dict[str, any] = skills
