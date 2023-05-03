from game.cache import from_cache


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
        return from_cache("managers.AbilityManager").get_ability(ability_name).is_requirements_fulfilled()

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

        In order to add flow to check for requirements, use an AbilityEvent!

        args:
            ability_name: The name of the Ability to learn

        returns:
            True if the ability is learned, False otherwise
        """
        if not self.is_learned(ability_name):
            self.abilities.add(ability_name)
            return True

        return False
