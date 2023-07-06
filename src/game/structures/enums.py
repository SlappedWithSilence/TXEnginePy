import enum


class EquipmentType(enum.Enum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    WEAPON = "weapon"
    # Armor
    HEAD = "head"
    CHEST = "chest"
    HANDS = "hands"
    LEGS = "legs"
    FEET = "feet"
    # Jewelry
    RING = "ring"
    NECKLACE = "necklace"


class InputType(enum.Enum):
    AFFIRMATIVE = "affirmative"  # Get a yes or no
    INT = "int"  # Get an int
    STR = "str"  # Get a string
    SILENT = "silent"  # Operate silently, don't attempt to prompt user
    ANY = "any"  # Get any key value as a response. Useful to simply prompt the user to continue


class CombatPhase(enum.Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    START_PHASE = "start_phase"
    PRE_ACTION_PHASE = "pre_action_phase"
    ACTION_PHASE = "action_phase"
    POST_ACTION_PHASE = "post_action_phase"
    END_PHASE = "end_phase"


class TargetMode(enum.Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    ALL = "all"
    SINGLE = "single"
    SINGLE_ALLY = "single_ally"
    SINGLE_ENEMY = "single_enemy"
    ALL_ALLY = "all_allies"
    ALL_ENEMY = "all_enemies"
    NOT_SELF = "not_self"
    SELF = "self"


