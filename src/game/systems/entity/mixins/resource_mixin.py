from __future__ import annotations

from game.systems.entity import resource as resource


class ResourceMixin:
    """
    A mixin for Entity objects that provides ResourceController functionality
    """

    def __init__(self, resource_controller: resource.ResourceController = None, **kwargs):
        super().__init__(**kwargs)
        self.resource_controller: resource.ResourceController = resource_controller or resource.ResourceController()
