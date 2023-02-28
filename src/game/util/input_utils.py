from game.structures.enums import InputType


def is_valid_range(input_type: InputType, min_value: any = None, max_value: any = None, length: int = None) -> bool:
    """
    Determine if a given input range is valid for a given InputType

    Parameters:
        input_type (InputType): The type of InputType to evaluate
        min_value (any): optional lower limit value
        max_value (any): optional upper limit value
        length (int) : optional length limit

    Returns:
        True if the given parameters are valid for the given InputType, False otherwise
    """
    if type(input_type) != InputType:
        raise TypeError(f"Cannot evaluate type {type(input_type)}! Must be of type InputType")

    if input_type == InputType.AFFIRMATIVE:
        return not min_value and not max_value and not length

    if input_type == InputType.INT:

        # If upper or lower is provided, it must be an int
        if (max_value and not type(max_value) == int) or (min_value and not type(min_value) == int):
            return False

        # If only an upper or lower limit is provided, that is valid
        if (max_value and not min_value) or (min_value and not max_value):
            return True

        # If both upper and lower limit, upper limit must be higher than lower limit
        else:
            return (max_value or 0) >= min_value

    if input_type == InputType.STR:
        return not length or (type(length) == int and length > 0)

    # If you got here, something isn't right.
    return None


def to_range(min_value: int = None, max_value: int = None, length: int = None) -> dict[str, int | None]:
    """
    Transform values into a standardized dict structure.

    Args:
        min_value:
        max_value:
        length:

    Returns: A formatted dict containing the input values

    """
    return {"min": min_value,
            "max": max_value,
            "len": length
            }


affirmative_t_range = ['y', 'yes']
affirmative_f_range = ['n', 'no']
affirmative_range = affirmative_t_range + affirmative_f_range


def affirmative_to_bool(user_input: str) -> bool:
    """
    Transform user input into a bool.

    """
    if user_input.lower() in affirmative_t_range:
        return True
    elif user_input.lower() in affirmative_f_range:
        return False
    else:
        return None

