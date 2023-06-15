from __future__ import annotations

import copy
from abc import ABC

import game
from game.cache import cached
from game.structures.loadable import LoadableMixin
from game.structures.loadable_factory import LoadableFactory
import game.systems.event.events as events


class SkillBase(ABC):

    def __init__(self, name: str, id: int, level: int = 1, xp: int = 0, initial_level_up_limit: int = 5,
                 next_level_ratio: float = 1.3, level_up_events: dict[int, list[events.Event]] = None):
        self.name: str = name  # Skill name
        self.id = id  # Unique id associate with this skill

        self.initial_level_up_limit = initial_level_up_limit  # How much XP is required to go from lvl 1 to lvl 2
        self.next_level_ratio = next_level_ratio  # Additional XP required to go from lvl 2 to lvl3, lvl3 to lvl4, etc

        self.level: int = level  # Skill's current level
        self.xp: int = xp  # Skill's current xp quantity
        self.level_up_limit = self._xp_ceiling(self.level)  # Current limit to level up against

        self.level_up_events: dict[int, list[events.Event]] = level_up_events or {}  # events.Events that are triggered on level up

        # Detect xp-level mismatches
        if self.xp >= self.level_up_limit:
            raise ValueError(
                f"Skill {self.name}'s XP level does not match it's level! {self.xp} >= {self.level_up_limit}"
            )

    def _xp_ceiling(self, level: int) -> int:
        """
        Calculate the level_up value for a given level
        """
        _sum = self.initial_level_up_limit
        for i in range(level - 1):
            _sum = round(_sum * self.next_level_ratio)

        return _sum

    def _trigger_level_up_events(self, level: int) -> None:
        """
        For a given level, add all level-up-events to the device stack
        """

        if type(level) != int:
            raise TypeError("Level must be an int!")

        if level in self.level_up_events:
            for event in self.level_up_events[level]:
                game.state_device_controller.add_state_device(copy.deepcopy(event))

    def force_level_up(self) -> None:
        """
        Force a skill to level up regardless of state.

        This increments the level, increments the level_up_limit, and sets XP to 0.
        """
        self.level += 1
        self.xp = 0
        self.level_up_limit = self._xp_ceiling(self.level)
        self._trigger_level_up_events(self.level)

    def _check_level_up(self) -> None:
        """
        A helper function that detects if enough xp has been gained to level the skill up. If so, all appropriate events
        are scheduled and the level and level_up fields are updated. If there is enough remaining xp to level up again,
        return True
        """

        if self.xp >= self.level_up_limit:  # Check for a level-up
            remaining_xp = self.xp - self.level_up_limit  # Calculate how much xp carries into the next level

            self.level += 1
            self.level_up_limit = round(self.level_up_limit * self.next_level_ratio)  # Update level_up_limit
            self.xp = remaining_xp  # Update xp value to carry-over value

            if self.xp >= self.level_up_limit:  # Detect a hanging level up
                self._check_level_up()  # Recursive call. This will make the lowest-level events resolve first.

            self._trigger_level_up_events(self.level)

    def gain_xp(self, xp: int) -> None:
        """
        Add XP to the skill. This will automatically trigger a level-up event if necessary.
        """
        self.xp += xp
        self._check_level_up()

    @property
    def remaining_xp(self) -> int:
        return self.level_up_limit - self.xp


class Skill(LoadableMixin, SkillBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "Skill", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
        Instantiate a Skill object from a JSON blob.

        Args:
            json: a dict-form representation of a json object

        Returns: a Skill instance with the properties defined in the JSON

        Required JSON fields:
        - name: str
        - id: int
        - level_up_events: {str(int), list[events.Event]}

        Optional JSON fields:
        - level: int
        - xp: int
        - initial_level_up_limit: int
        - next_level_ratio: float
        """

        # Validate required fields exist
        required_fields = [("name", str), ("id", int), ("level_up_events", dict)]

        LoadableFactory.validate_fields(required_fields, json)

        level_up_events: dict[int, list[events.Event]] = {}

        for str_level in json['level_up_events']:
            try:
                true_level = int(str_level)
            except TypeError:
                raise TypeError(f"Cannot convert level {str_level} to int!")

            if true_level in level_up_events:
                raise ValueError(f"Duplicate entries for level {true_level}!")

            level_up_events[true_level] = []
            for raw_event in json['level_up_events'][str_level]:
                obj = LoadableFactory.get(raw_event)
                if not isinstance(obj, events.Event):
                    raise TypeError(f"Cannot add object of type {type(obj)} to level_up_event list!")
                level_up_events[true_level].append(obj)

        # Verify that the optional fields are typed correctly if they're present
        optional_fields = [('level', int), ('xp', int), ('initial_level_up_limit', int), ('next_level_ratio', float)]
        LoadableFactory.validate_fields(optional_fields, json, required=False)
        optional_kwargs = {}

        # Collect the optional field values
        for field, _ in optional_fields:
            if field in json:
                optional_kwargs[field] = json[field]

        return Skill(
            name=json['name'],
            id=json['id'],
            level_up_events=level_up_events,
            **optional_kwargs
        )
