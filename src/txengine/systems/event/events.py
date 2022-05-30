from abc import ABC
from typing import Union

from rich import print


class Event(ABC):

    def __init__(self, properties: Union[list[str]], text: Union[str, None] = None):
        self.__properties: list[str] = properties
        self.__text: Union[str, None] = text

    def logic(self) -> None:
        """Core logic for the Event"""
        pass

    def perform(self) -> None:
        """Wrapper for logic that prints optional user prompting"""
        if self.__text:
            print(self.__text)
        self.logic()
