from abc import ABC

import game
from game.systems.event.events import Event


class SkillBase(ABC):

    def __init__(self, name: str, level: int = 1, xp: int = 0, initial_level_up_limit: int = 5,
                 next_level_ratio: float = 1.3, level_up_events: dict[int, list[Event]] = None):
        self.name: str = name  # Skill name
        self.level: int = level  # Skill's current level
        self.xp: int = xp  # Skill's current xp quantity
        self.initial_level_up_limit = initial_level_up_limit  # How much XP is required to go from lvl 1 to lvl 2
        self.next_level_ratio = next_level_ratio  # Additional XP required to go from lvl 2 to lvl3, lvl3 to lvl4, etc
        self.level_up_limit = self._xp_ceiling(self.level)  # Current limit to level up against

        self.level_up_events: dict[int, list[Event]] = level_up_events or {}  # Events that are triggered when a level is achieved

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
        for i in range(level):
            _sum = round(_sum * self.next_level_ratio)

        return _sum

    def _level_up(self):
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
                self._level_up()  # Recursively call level_up(). This will make the lowest-level events resolve first.

            # Add all level-up-events to the game-state-controller's stack
            if self.level in self.level_up_events:
                for event in self.level_up_events[self.level]:
                    game.state_device_controller.add_state_device(event)

    def gain_xp(self, xp: int) -> None:
        """
        Add XP to the skill. This will automatically trigger a level-up event if necessary.
        """
        self.xp += xp
        self._level_up()