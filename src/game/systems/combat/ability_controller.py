import game
from game.cache import from_cache
from game.structures.messages import StringContent
import game.systems.event as events


class AbilityController:

    def __init__(self, abilities: list[str] = None, owner=None):
        from game.systems.entity.entities import CombatEntity
        if owner is not None and not isinstance(owner, CombatEntity):
            raise TypeError("Cannot assigned an owner to AbilityController that is not of type CombatEntity!")

        self.owner = owner

        # Validate that each str is a real ability
        if abilities is not None:
            for ab in abilities:
                if not from_cache('managers.AbilityManager').is_ability(ab):
                    raise ValueError(f"{ab} is not a known Ability!")

        self.abilities: set[str] = set(abilities) if abilities is not None else set()

    def is_learnable(self, ability_name: str) -> bool:
        """
        Checks if an Ability can be learned by the owning CombatEntity

        args:
            ability_name: The name of the Ability to check

        Returns:
            True if the Requirements for the Ability are met by the owning CombatEntity, False otherwise.
        """
        return from_cache("managers.AbilityManager").get_ability(ability_name).is_requirements_fulfilled(self.owner)

    def is_learned(self, ability_name: str) -> bool:
        """
        Checks if the Ability in question has already been learned

        args:
            ability_name: The name of the Ability to check

        returns:
            True if the Ability has already been learned.
        """
        return ability_name in self.abilities

    def learn(self, ability_name: str) -> bool:
        """
        Adds the given ability to the learned abilities set. This does not check if requirements are met!

        In order to add flow to check for requirements, use an LearnAbilityEvent!

        args:
            ability_name: The name of the Ability to learn

        returns:
            True if the ability is learned, False otherwise
        """
        if not self.is_learned(ability_name):
            self.abilities.add(ability_name)
            return True

        return False

    def consume_ability_resources(self, ability_name) -> None:
        """
        Consume the required resources for a selected ability.

        args:
            ability_name: The name of the Ability to fetch resource costs for

        returns: None
        """

        for resource, quantity in from_cache("managers.AbilityManager").get_ability(ability_name).costs.items():
            game.state_device_controller.add_state_device(events.ResourceEvent(resource, quantity, self.owner))

    def _get_ability_as_option(self, ability_name) -> list[str | StringContent]:
        """
        Retrieve an instance of the passed ability and return a formatted list containing it.

        Returned formatting is gray if requirements not met, white if met.
        """
        if not from_cache('managers.AbilityManager').is_ability(ability_name):
            raise ValueError(f"{ability_name} is not a known Ability!")

        return [
            StringContent(value=ability_name,
                          formatting="ability_enabled" if
                          from_cache("managers.AbilityManager").get_ability(ability_name).is_requirements_fulfilled(
                              self.owner)
                          else "ability_disabled"
                          )
        ]

    def get_abilities_as_options(self) -> list[list[str | StringContent]]:
        """
        Returns a formatted collection of lists containing all learned abilities.

        Abilities that can be used are white, abilities that cannot be used are grey.

        args:
            None

        Returns: A list of lists that contains formatted learned abilities.
        """

        return [
            self._get_ability_as_option(ability_name) for ability_name in self.abilities
        ]
