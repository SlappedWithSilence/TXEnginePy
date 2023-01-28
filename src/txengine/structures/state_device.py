from src.txengine.structures.enums import InputType


class StateDevice:

    def __int__(self):
        self.str_buffer = []

    @property
    def val(self) -> list[str]:
        return self.str_buffer
