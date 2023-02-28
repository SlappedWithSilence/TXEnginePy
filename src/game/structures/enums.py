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
    NONE = "null"  # Get any key value as a response. Useful to simply prompt the user to continue


