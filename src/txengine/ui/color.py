from typing import Union

from loguru import logger

tag_map: [str, list[str]] = {}


def init_default_tag_map() -> None:
    tag_map["index"] = ["orange", "bold"]
    tag_map["listed_option"] = []
    tag_map["input_query"] = ["italic"]


def load_tag_styles(path: str) -> None:
    """Load tag styles from a JSON file at 'path'"""
    logger.debug("Not implemented!")


def otag(tag: str) -> str:
    """Returns an open tag for a rich styling property"""
    return f"[{tag}]"


def ctag(tag: str) -> str:
    """Returns a closing tag for a rich styling property"""
    return f"[/{tag}]"


def wrap(text: str, tag: Union[list[str], str]) -> str:
    """Wraps a string in tags for a rich styling property"""
    if type(tag) == str:
        return f"{otag(tag)}{text}{ctag(tag)}"

    elif type(tag) == list:
        opener = ""
        closer = ""

        for element in tag:
            opener = opener + otag(element)
            closer = closer + otag(element)

        return f"{opener}{text}{closer}"

    else:
        raise TypeError("Invalid type for tags! Must be a str or list!")


def style(text: str, tag_style: str) -> str:
    """Automatically wrap text in a pre-defined style"""

    if tag_style not in tag_map:
        raise ValueError(f"Unknown tag style {tag_style}!")

    return wrap(text, tag_map[tag_style])