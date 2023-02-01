from pydantic import BaseModel

from enums import InputType


class StringContent(BaseModel):
    """
    An object that stores a string alongside formatting data.
    """
    value: str
    formatting: list[str]

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

    components: dict
    input_type: InputType
    input_range: dict
    frame_type: str = "Generic"


if __name__ == "__main__":
    f = Frame(components={}, input_type=InputType.AFFIRMATIVE, input_range={})
    print(f.schema())
    print(f.json())

    s = StringContent(value="This is a StringContent", formatting=["bold", "blue"])
    print(s.json())
