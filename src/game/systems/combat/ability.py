from abc import ABC

from game.cache import cached
from game.structures.enums import CombatPhase, TargetMode
from game.structures.loadable import LoadableMixin
from game.structures.loadable_factory import LoadableFactory
from game.systems.combat.effect import CombatEffect
from game.systems.requirement.requirements import RequirementsMixin


class AbilityBase(ABC):
    """
    The functional base class of Ability.

    This class is required in order to make proper use of the cooperative inheritance constructors specified in
    LoadableMixin and RequirementsMixin.
    """

    def __init__(self, name: str, description: str, on_use: str,
                 target_mode: TargetMode,
                 effects: dict[CombatPhase, list[CombatEffect]] = None,
                 damage: int = 1,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name: str = name
        self.description: str = description
        self.on_use: str = on_use
        self.effects: dict[CombatPhase, list[CombatEffect]] = effects or {ev: [] for ev in CombatPhase}
        self.target_mode = target_mode
        self.damage: int = damage


class Ability(LoadableMixin, RequirementsMixin, AbilityBase):
    """
    Ability objects represent 'moves' that can be used by CombatEntity's during Combat.

    Abilities are one of the two ways that a CombatEntity may be assigned a CombatEffect.
    """

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
        - target_mode (str)
        - damage (int)

        Optional JSON fields:
        - effects {CombatPhase:[CombatEffect]}
        - requirements
        """

        required_fields: list[tuple[str, type]] = [
            ("name", str), ("description", str), ("on_use", str), ("target_mode", str),
            ("damage", int),

        ]

        optional_fields = [
            ("effects", dict), ("requirements", list)
        ]

        LoadableFactory.validate_fields(required_fields, json)
        LoadableFactory.validate_fields(optional_fields, json, False, False)

        if json['class'] != 'Ability':
            raise ValueError('Incorrect class designation!')

        # Build complex optional field collections
        kwargs = {}

        # Build, verify and store effects
        if 'effects' in json:
            effects = {}  # Pass to kwargs once filled

            for phase in json['effects']:  # Effects are sorted into lists based on trigger phase; iterate through phase
                if phase not in CombatPhase:  # Catch bad phase
                    raise ValueError(f"Unknown combat phase: {phase}")

                # Catch broken formatting
                if type(json['effects'][phase]) != list:
                    raise TypeError(f"Expected phase {phase} to map to a list, got {type(json['effects'][phase])} instead!")

                # If the phase hasn't been observed yet, make a list for it
                if CombatPhase(phase) not in effects:
                    effects[CombatPhase(phase)] = []

                # Load the effect via class-field (raw_effect['class'])
                for raw_effect in json['effects'][phase]:
                    effects[CombatPhase(phase)].append(LoadableFactory.get(raw_effect))

            kwargs['effects'] = effects

        # Build requirements via LoadableFactory.
        if 'requirements' in json:
            requirements = LoadableFactory.collect_requirements(json)
            kwargs['requirements'] = requirements

        return Ability(
            name=json['name'],
            description=json['description'],
            on_use=json['on_use'],
            damage=json['damage'],
            target_mode=TargetMode(json['target_mode']),
            **kwargs  # Optional fields might not be present, so store and split via dict unpacking
        )
