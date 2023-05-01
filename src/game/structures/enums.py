import enum


class EquipmentType(enum.Enum):
    WEAPON = 0,
    # Armor
    HEAD = 1,
    CHEST = 2,
    HANDS = 3,
    LEGS = 4,
    FEET = 5,
    # Jewelry
    RING = 6,
    NECKLACE = 7


class InputType(enum.Enum):
    AFFIRMATIVE = "affirmative",  # Get a yes or no
    INT = "int",  # Get an int
    STR = "str",  # Get a string
    SILENT = "silent",  # Operate silently, don't attempt to prompt user
    ANY = "any"  # Get any key value as a response. Useful to simply prompt the user to continue


class CombatPhase(enum.Enum):
    START_PHASE = 0
    PRE_ACTION_PHASE = 1
    ACTION_PHASE = 2
    POST_ACTION_PHASE = 3
    END_PHASE = 4


class TargetMode(enum.Enum):
    ALL = 0
    SINGLE = 1
    SINGLE_ALLY = 2
    SINGLE_ENEMY = 3
    ALL_ALLY = 4
    ALL_ENEMY = 5
    NOT_SELF = 6


