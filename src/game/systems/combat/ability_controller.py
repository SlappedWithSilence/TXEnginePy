from game.cache import from_cache
import game.systems.entity.entities as entities


class AbilityController:

    def __init__(self, abilities: list[str] = None, owner: entities.CombatEntity = None):
        if owner is not None and not isinstance(owner, entities.CombatEntity):
            raise TypeError("Cannot assigned an owner to AbilityController that is not of type CombatEntity!")

        self.owner = entities.CombatEntity

        # Validate that each str is a real ability
        if abilities is not None:
            for ab in abilities:
                if not from_cache('managers.AbilityManager').is_ability(ab):
                    raise ValueError(f"{ab} is not a known Ability!")

        self.abilities: list[str] = abilities or []


    def is_learnable(self, ability_name: str) -> bool:
        pass

    def is_learned(self, ability_name: str) -> bool:
        pass

    def learn(self, ability_name: str) ->  bool:
        pass
