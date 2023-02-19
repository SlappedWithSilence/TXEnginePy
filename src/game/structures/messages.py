from typing import Any

from pydantic import BaseModel

from .enums import InputType
from game.formatting import get_style


def _to_style_args(form: list[str] | str) -> list[str]:
    return form if type(form) == list else get_style(form)


class StringContent(BaseModel):
    """
    An object that stores a string alongside formatting data.
    """
    value: str
    formatting: list[str] | str = []

    def __init__(self, **data):
        if "formatting" in data:
            data["formatting"] = _to_style_args(data["formatting"])  # Allow for style name references

        super().__init__(**data)

    def __str__(self) -> str:
        return self.value

    def __add__(self, other):

        if type(other) == str:
            return StringContent(value=self.value + other, formatting=self.formatting)

        elif type(other) == StringContent:
            return StringContent(value=self.value + other.value, formatting=self.formatting + other.formatting)

        else:
            raise TypeError()


class Frame(BaseModel):
    """
    An object that contains organized data for a Game Frame.
    """

    components: dict[str, Any]
    input_type: InputType
    input_range: dict[str, int | None]
    frame_type: str = "Generic"


if __name__ == "__main__":
    f = Frame(components={}, input_type=InputType.AFFIRMATIVE, input_range={})
    print(f.schema())
    print(f.json())

    s = StringContent(value="This is a StringContent", formatting=["bold", "blue"])
    print(s.json())
