from enum import Enum
from typing import Callable

from loguru import logger

from game.cache import request_storage_key, store_element, cached
from game.structures.enums import InputType
from game.structures.loadable import LoadableMixin
from game.structures.messages import ComponentFactory
from game.structures.state_device import FiniteStateDevice
from game.systems.event import Event


class SelectElementEvent(Event):
    class States(Enum):
        DEFAULT = 0
        SHOW_ELEMENTS = 1
        PROCESS_CHOICE = 2
        TERMINATE = -1

    def __init__(self,  collection: list, key: Callable, element_filter: Callable = None,
                 to_listing: Callable = str, prompt: str = "Choose an element"):
        super().__init__(default_input_type=InputType.SILENT, states=self.States, default_state=self.States.DEFAULT)
        """
        A generic Event that allows the user to select an element from a list of potential elements.
        
        args:
            - collection: The items from which to select an element
            - key: A callable that takes in the selected element and returns the key to store in storage
            - element_filter: A callable that returns True if the element should be shown to the user, False otherwise
            - to_listing: A callable that takes in an element from the collection and returns a str to show the user
            - prompt: The text to show the user above the list of elements
        """
        self._element_filter: Callable = element_filter
        self._collection: list = collection
        self._key: Callable = key
        self._storage_keys: dict[str, any] = {"selected_element": None}  # A pre-built dict to hold storage keys
        self._prompt: str = prompt
        self._to_listing: Callable = to_listing

        # Temp values
        self.__filtered_collection: list | None = None
        self.__filtered_collection_len: int | None = None

        if len(self._collection) < 1:
            raise RuntimeError("Cannot instantiate a SelectElementEvent with a collection of size 0!")

        self._setup_states()

    def _link(self) -> dict[str, str]:
        """
        Override default link logic to store
        """
        self._storage_keys["selected_element"] = request_storage_key()  # Storage key for the selected element data
        return self._storage_keys

    def _setup_states(self) -> None:
        # DEFAULT
        @FiniteStateDevice.state_logic(self, self.States.DEFAULT, InputType.SILENT)
        def logic(_: any) -> None:

            # Check for a filter and use it if available
            if self._element_filter is not None:
                self.__filtered_collection = [element for element in self._collection if self._element_filter(element)]
            else:
                self.__filtered_collection = self._collection

            # Pre-compute len of remaining items
            self.__filtered_collection_len = len(self.__filtered_collection)

            # Check for broken collections
            if self.__filtered_collection_len < 1:
                logger.error("SelectElementEvent::__filtered_collection_len must be > 0!")
                logger.debug(f"collection: {self._collection}")
                logger.debug(f"key: {str(self._key)}")
                logger.debug(f"to_listing: {str(self._to_listing)}")
                logger.debug(f"element_filter: {str(self._element_filter)}")
                raise RuntimeError("SelectElementEvent cannot have a filtered collection size of 0!")
            self.set_state(self.States.SHOW_ELEMENTS)

        @FiniteStateDevice.state_content(self, self.States.DEFAULT)
        def content():
            return ComponentFactory.get()

        # SHOW_ELEMENTS
        @FiniteStateDevice.state_logic(self, self.States.SHOW_ELEMENTS, InputType.INT, input_min=0,
                                       input_max=lambda: int(self.__filtered_collection_len) - 1)
        def logic(user_input: int) -> None:
            logger.debug("Stored user-choice!")
            store_element(self._storage_keys['selected_element'], self._key(self.__filtered_collection[user_input]))
            self.set_state(self.States.TERMINATE)

        @FiniteStateDevice.state_content(self, self.States.SHOW_ELEMENTS)
        def content():
            return ComponentFactory.get([self._prompt],
                                        [self._to_listing(e) for e in self.__filtered_collection])

        # PROCESS_CHOICE
        @FiniteStateDevice.state_logic(self, self.States.PROCESS_CHOICE, InputType.SILENT)
        def logic(_: any) -> None:
            pass

        @FiniteStateDevice.state_content(self, self.States.PROCESS_CHOICE)
        def content():
            return ComponentFactory.get()

    @staticmethod
    @cached([LoadableMixin.LOADER_KEY, "SelectElementEvent", LoadableMixin.ATTR_KEY])
    def from_json(json: dict[str, any]) -> any:
        raise RuntimeError("Loading SelectElementEvent from JSON is not supported!")

