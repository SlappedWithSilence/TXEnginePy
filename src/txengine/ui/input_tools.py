from rich import print

from .color import style, wrap


def input_int(max_value: int = None, min_value: int = None) -> int:
    """Get a bounded int from the user"""
    value: int = None

    while True:
        print(style(f"Enter a number between {max_value} and {min_value}:", "input_query"))

        try:
            value = int(input().strip())
        except TypeError:
            print(wrap("You must enter an integer!", ["bold", "red"]))

        if max_value >= value >= min_value:
            break

        else:
            print(wrap(f"You must enter a number between {max_value} and {min_value}", ["bold", "red"]))

    return value


def input_affirmative() -> bool:
    """Get an affirmative or negative from the user"""
    value: str = None

    positive = ["yes", "y", "sure", "ok"]
    negative = ["no", "n", "nah"]

    while True:
        print(style("Enter yes or no:", "input_query"))
        value = input().strip().lower()

        if value in positive:
            return True

        elif value in negative:
            return False

        else:
            print(wrap("You must enter yes, no, y, or n!", ["bold", "red"]))
