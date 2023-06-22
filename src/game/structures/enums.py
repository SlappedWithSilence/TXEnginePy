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
    START_PHASE = 0
    PRE_ACTION_PHASE = 1
    ACTION_PHASE = 2
    POST_ACTION_PHASE = 3
    END_PHASE = 4


class TargetMode(enum.Enum):
    ALL = "ALL"
    SINGLE = "SINGLE"
    SINGLE_ALLY = "SINGLE_ALLY"
    SINGLE_ENEMY = "SINGLE_ENEMY"
    ALL_ALLY = "ALL_ALLY"
    ALL_ENEMY = "ALL_ENEMY"
    NOT_SELF = "NOT_SELF"


