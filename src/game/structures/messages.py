from typing import Any

from pydantic import BaseModel

from game.systems.entity.entities import CombatEntity
from .enums import InputType
from game.formatting import get_style


def _to_style_args(form: list[str] | str) -> list[str]:
    """
    A function that unpacks a string-based style reference.

    If form is a string, evaluate it as a named style reference and look it up in the cache. If it is a list, evaluate
    it as a style override and pass the list along directly.
    """
    if type(form) != list and type(form) != str:
        raise TypeError(f"Unknown type for style! Expected str or list[str], got {type(form)} instead.")

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


class ComponentFactory:
    """
    A factory class that generates a specially-structured dicts. These dicts are intended to be embedded within the
    'components' field of Frame and StateDevice objects.
    """

    @classmethod
    def get(cls,
            content: list[str | StringContent] | None = None,
            options: list[list[str | StringContent]] | None = None,
            allies: list[CombatEntity] | None = None,
            enemies: list[CombatEntity] | None = None) -> dict[str, list]:
        """
        A components dict only has two fields: content and options. 'content' is required while 'options' is not.

        Args: content: A list of str or str-like objects. This is the main text the user sees.
        options: A list of lists of str or str-like objects. If there are options for the user to choose from within a
        given frame, they are embedded inside 'options'.

        Returns: A structured dict containing all the passed fields.
        """

        def scrape_entity(entity) -> dict[str, any]:
            """
            Return a dict of all necessary info about the entity.
            """

            if type(entity) != CombatEntity:
                raise TypeError(f"scrape_entity expected object of type CombatEntity! Got {type(entity)} instead!")

            return {
                "name": entity.name,
                "id": entity.id,
                "primary_resource_val": entity.resource_controller.primary_resource.value,
                "primary_resource_max": entity.resource_controller.primary_resource.max
            }

        if content and type(content) != list:
            raise TypeError(f"components.content must be of type list! Got {type(content)} instead.")

        if options and type(options) != list:
            raise TypeError(f"components.options must be of type list! Got {type(options)} instead.")

        if allies and type(allies) != list:
            raise TypeError(f"components.allies must be of type list! Got {type(allies)} instead.")

        if enemies and type(enemies) != list:
            raise TypeError(f"components.enemies must be of type list! Got {type(enemies)} instead.")

        return {
            "content": content,
            "options": options,
            "allies": [scrape_entity(e) for e in allies] if allies else [],
            "enemies": [scrape_entity(e) for e in enemies] if enemies else []
        }


if __name__ == "__main__":
    f = Frame(components={}, input_type=InputType.AFFIRMATIVE, input_range={})
    print(f.schema())
    print(f.json())

    s = StringContent(value="This is a StringContent", formatting=["bold", "blue"])
    print(s.json())
