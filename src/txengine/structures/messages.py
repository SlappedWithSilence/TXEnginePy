from dataclasses import dataclass, field
from typing import List, Dict

from .enums import InputType


@dataclass
class StringContent:
    """
    An object that stores a string alongside formatting data.
    """
    value: str
    formatting: List[str] = field(default_factory=List)

    def __str__(self) -> str:
        return self.value

    def __json__(self) -> dict[str, any]:
        return {"value": self.value,
                "formatting": self.formatting
                }

    def __add__(self, other):

        if type(other) == str:
            return StringContent(self.value + other, self.formatting)

        elif type(other) == StringContent:
            return StringContent(self.value + other.value, self.formatting + other.formatting)

        else:
            raise TypeError()


@dataclass
class Frame:
    """
    An object that contains organized data for a Game Frame.
    """

    components: dict[str, any]
    input_type: InputType
    input_range: dict[str: any] = field(default_factory=dict)
    frame_type: str = "Generic"

    def __json__(self) -> dict[str, any]:
        return {"frame_type": self.frame_type, "input_type": self.input_type.name} | self.components | self.input_range

    @property
    def json(self) -> dict[str,  any]:
        return self.__json__()
