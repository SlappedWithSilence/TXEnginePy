from ...util.string_util import c_tag, o_tag
from loguru import logger

text_colors: [str, list[str]] = {"item_name": ["orange"],
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

    return o_tag(text_colors[form]) + text + c_tag(text_colors[form])
