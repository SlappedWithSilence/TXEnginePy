from textual.message import Message


class GameTextChange(Message, bubble=True):
    _handler: str = "handle_game_text_change"


class OptionSelected(Message, bubble=True):
    _handler: str = "handle_option_selected"
