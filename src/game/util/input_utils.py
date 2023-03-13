from game.structures.enums import InputType


def is_valid_range(input_type: InputType,
                   min_value: int | None = None,
                   max_value: int | None = None,
                   length: int | None = None) -> bool:
    """
    Determine if a given input range is valid for a given InputType

    Parameters:
        input_type (InputType): The type of InputType to evaluate
        min_value (int | None): optional lower limit value
        max_value (int | None): optional upper limit value
        length (int | None) : optional length limit

    Returns:
        True if the given parameters are valid for the given InputType, False otherwise
    """
    if type(input_type) != InputType:
        raise TypeError(f"Cannot evaluate type {type(input_type)}! Must be of type InputType")

    if input_type == InputType.AFFIRMATIVE or input_type == InputType.ANY or input_type == InputType.SILENT:
        return True

    if input_type == InputType.INT:
        return (min_value is None or type(min_value) == int or callable(min_value)) and (
                    max_value is None or type(max_value) == int or callable(max_value))

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