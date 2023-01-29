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
    AFFIRMATIVE = 0,
    INT = 1,
    STR = 2


def is_valid_range(input_type: InputType, lower_limit: any = None, upper_limit: any = None, length: int = None) -> bool:
    """
    Determine if a given input range is valid for a given InputType

    Parameters:
        input_type (InputType): The type of InputType to evaluate
        lower_limit (any): optional lower limit value
        upper_limit (any): optional upper limit value
        length (int) : optional length limit

    Returns:
        True if the given parameters are valid for the given InputType, False otherwise
    """

    if type(input_type) != InputType:
        raise TypeError(f"Cannot evaluate type {type(input_type)}! Must be of type InputType")

    if input_type == InputType.AFFIRMATIVE:
        return not lower_limit and not upper_limit and not length

    if input_type == InputType.INT:

        # If upper or lower is provided, it must be an int
        if (upper_limit and not type(upper_limit) == int) or (lower_limit and not type(lower_limit) == int):
            return False

        # If only an upper or lower limit is provided, that is valid
        if (upper_limit and not lower_limit) or (lower_limit and not upper_limit):
            return True

        # If both upper and lower limit, upper limit must be higher than lower limit
        else:
            return upper_limit > lower_limit

    if input_type == InputType.STR:
        return not length or (type(length) == int and length > 0)

    # If you got here, something isn't right.
    return None
