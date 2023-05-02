from abc import ABC

from game.cache import cached, from_cache
from game.structures.enums import CombatPhase
from game.structures.loadable import LoadableMixin
from game.systems.combat.effect import CombatEffect
from game.systems.requirement.requirements import RequirementsMixin


class AbilityBase(ABC):
    def __init__(self, name: str, description: str, on_use: str,
                 effects: dict[CombatPhase, list[CombatEffect]] = None,
                 damage: int = 1,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name: str = name
        self.description: str = description
        self.on_use: str = on_use
        self.effects: dict[CombatPhase, list[CombatEffect]] = effects or {}
        self.damage: int = damage


class Ability(LoadableMixin, RequirementsMixin, AbilityBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "Ability", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        """
        Loads an Ability object from a JSON blob.

        Required JSON fields:
        - name (str)
        - description (str)
        - on_use (str)
        - effects {CombatPhase:CombatEffect}
        - damage (int)

        Optional JSON fields:
        - None
        """

        required_fields: list[tuple[str, type]] = [
            ("name", str), ("description", str), ("on_use", str), ("class", str),
            ("damage", int),
            ("effects", dict)
        ]

        for field_name, field_type in required_fields:
            if field_name not in json or type(json[field_name] != field_type):
                raise ValueError(f"Missing or poorly-typed field: {field_type}:{str(field_type)}")

        if json['class'] != 'Ability':
            raise ValueError('Incorrect class designation!')

        # Pre-parse the effects fields
        effects = {}
        for phase in json['effects']:
            if phase not in CombatPhase:
                raise ValueError(f"Unknown combat phase: {phase}")

            if type(json['effects'][phase]) != list:
                raise TypeError(f"Expected phase {phase} to map to a list, got {type(json['effects'][phase])} instead!")

            if CombatPhase(phase) not in effects:
                effects[CombatPhase(phase)] = []

            for raw_effect in json['effects'][phase]:
                effects[CombatPhase(phase)].append(from_cache('loader.ability.from_json')(raw_effect))

        return Ability(
            name=json['name'],
            descritpion=json['description'],
            on_use=json['on_use'],
            damage=json['damage'],
            effects=effects
        )
