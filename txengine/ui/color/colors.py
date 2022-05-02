from typing import Union

from ..util.string_util import o_tag, c_tag
from loguru import logger

text_colors = {"item_name": ["orange"],
               "item_quantity": ["cyan"],
               "item_desc": ["italic"],
               "item_value": ["green"],
               "stat_name": [],
               "stat_value": ["green"],
               "generic_value": ["green"],
               "menu_opt_number": ["bold"],
               "menu_opt_text": []
               }


def c_form(text: str, form: str) -> str:
    """Formats text given formatting rules specified in txengine.ui.color.colors.py

    Compatible with all Rich formatting cues. See https://rich.readthedocs.io/en/stable/introduction.html
    """
    if form not in text_colors:
        logger.error("Cannot find format " + form + " in text_colors!")
        return None

    prefix = ""
    suffix = ""

    for tag in text_colors[form]:
        prefix = f"{prefix}[{tag}]"
        suffix = f"{suffix}[{tag}]"

    return f"{prefix}{text}{suffix}"
