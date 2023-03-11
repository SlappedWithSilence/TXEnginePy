import copy
import enum
import weakref
import inspect
from abc import abstractmethod, ABC
from typing import Callable

from loguru import logger

from game.structures import enums
from game.structures.enums import InputType
from game.util.input_utils import is_valid_range, to_range, affirmative_range, affirmative_to_bool
from game.structures.messages import Frame


class StateDevice(ABC):
    """
    An abstract class that defines an object that represents game logic
    """

    def __init__(self, input_type: InputType, input_range: dict[str, int] = None, name: str = "StateDevice"):
        self.input_type: InputType = input_type
        self.input_range: dict[str, int] = input_range or to_range()
        self.name: str = name
        self._controller: any = None  # This value should only be set by the GameStateController

    @property
    def controller(self) -> any:
        return self._controller

    @controller.setter
    def controller(self, engine_in) -> None:
        self._controller = weakref.ref(engine_in)

    @property
    def domain_min(self) -> any:
        return self.input_range["min"]

    @domain_min.setter
    def domain_min(self, val: any) -> None:
        if is_valid_range(self.input_type,
                          min_value=val,
                          max_value=self.domain_max,
                          length=self.domain_length):
            self.input_range["min"] = val
        else:
            raise ValueError(f"Tried to set lower limit of {self.input_type} to value of type {type(val)}!")

    @property
    def domain_max(self) -> any:
        """
        An optional value that determines the maximum value a submitted int can have
        """
        return self.input_range["max"]

    @domain_max.setter
    def domain_max(self, val: any) -> None:
        if is_valid_range(self.input_type,
                          min_value=self.domain_min,
                          max_value=val,
                          length=self.domain_length):
            self.input_range["max"] = val
        else:
            raise ValueError(f"Tried to set lower limit of {self.input_type} to value of type {type(val)}!")

    @property
    def domain_length(self) -> [int, None]:
        """
        An optional value that determines the maximum length of a submitted string
        """
        if "length" not in self.input_range:
            return None

        return self.input_range["length"]

    @domain_length.setter
    def domain_length(self, val: [int, None]) -> None:
        if is_valid_range(self.input_type,
                          min_value=self.domain_min,
                          max_value=self.domain_max,
                          length=self.domain_length):
            self.input_range["min"] = val
        else:
            raise ValueError(f"Tried to set lower limit of {self.input_type} to value of type {type(val)}!")

    @property
    def input_domain(self) -> dict[str, any]:
        """
        A map that stores the domain of the allowed values for the StateDevice
        """
        return self.input_range

    @input_domain.setter
    def input_domain(self, input_type: InputType, max=None, min=None, length=None) -> None:
        if not is_valid_range(input_type, max, min, length):
            raise ValueError(f"""Invalid input domain values for type {input_type}:\n 
                                                                       min: {min}\n
                                                                       max: {max}\n
                                                                       length: {length}
                              """)

    @property
    @abstractmethod
    def components(self) -> dict[str, any]:
        """
        The basic display components of the device
        """
        pass

    def validate_input(self, input_value) -> bool:
        """
        Compare the user's input against the allowed values to determine if it is valid.

        Args:
            input_value: The user's input

        Returns: True if the input value is valid, False otherwise
        """

        if self.input_type == InputType.SILENT or self.input_type == InputType.ANY:
            return True

        # Input must be str matching the set of strings in the array
        elif self.input_type == InputType.AFFIRMATIVE:
            if type(input_value) == str and str.lower(input_value) in affirmative_range:
                return True
            else:
                logger.warning(f"[{self}]: Failed to validate input! {input_value} must be in {affirmative_range}")
                return False

        # Input must be an int that is below the maximum and above the minimum
        elif self.input_type == InputType.INT:
            if type(input_value) == int:
                if self.input_range["min"] and input_value < self.input_range["min"]:
                    logger.warning(
                        f"[{self}]: Failed to validate input! {input_value} must be >= {self.input_range['min']}")
                    return False

                if self.input_range["max"] and input_value > self.input_range["max"]:
                    logger.warning(
                        f"[{self}]: Failed to validate input! {input_value} must be <= {self.input_range['max']}")
                    return False

                return True
            else:
                logger.warning(f"input_type.INT requires int, not type: {type(input_value)}!")

        # Input must be a str shorter than length
        elif self.input_type == InputType.STR:
            if type(input_value) == str:
                if self.input_range["len"] and len(input_value) <= self.input_range["len"]:
                    return True

            logger.warning(
                f"[{self}]: Failed to validate input! {input_value} is not a str of len <= {self.input_range['len']}"
            )
            return False
        else:
            raise ValueError(f"Unknown InputType: {self.input_type.name}!")

    @abstractmethod
    def _logic(self, user_input: any) -> None:
        """
        The actual game logic. This must be overriden by subclasses.

        Args:
            user_input:

        Returns: None

        """
        pass

    def input(self, user_input: any) -> bool:
        """
        Submits the user's input to the state device. The state device advances its internal logic and modifies its
        output. If the input is not valid, it is rejected.

        Args:
            user_input: The value passed by the user

        Returns: True if the input is valid, False otherwise

        """
        if self.validate_input(user_input):

            if self.input_type == enums.InputType.AFFIRMATIVE:  # Intercept affirmative input values and transform them
                self._logic(affirmative_to_bool(user_input))
            else:  # Handle all other input values normally
                self._logic(user_input)
            return True

        return False

    def __frame__(self) -> Frame:
        """
            A method to convert a state device into a corresponding frame.

            Returns: The Frame-equivalent of a given state device

        """
        return Frame(components=self.components,
                     input_type=self.input_type,
                     input_range=self.input_range,
                     frame_type=self.__class__.__name__
                     )

    def __str__(self) -> str:
        return f"{self.name} ({self.__class__.__name__})"

    def to_frame(self) -> Frame:
        """
            A method to convert a state device into a corresponding frame.

            Returns: The Frame-equivalent of a given state device

        """
        return self.__frame__()


class FiniteStateDevice(StateDevice, ABC):
    """
    A subclass of StateDevice that adds support for explicit state ordering and transitions
    """

    def __init__(self, default_input_type: InputType, states: enum.Enum, default_state=None):
        super().__init__(default_input_type)

        self.states: enum.Enum = states
        self.current_state = default_state

        state_data_dict = {
            "input_type": enums.InputType.ANY,
            "min": None,
            "max": None,
            "len": None,
            "logic": None,
            "content": None
        }

        self.state_data: dict[states, dict] = {k.value: copy.deepcopy(state_data_dict) for k in self.states}
        self.state_history: list[states] = [self.current_state]

    def dump(self) -> None:
        """A debug method. Prints a large volume of useful information about the FiniteStateDevice."""
        logger.error(f"Something went wrong with FiniteStateDevice::{self.__class__}::{self.name}!")
        logger.error(f"State history::{self.state_history}")
        logger.error(f"State data")
        for state in self.state_data:
            logger.error(f"state::{state}")
            logger.error(self.state_data[state])

    def set_state(self, next_state) -> None:
        if next_state.value not in self.state_data:
            raise ValueError(f"Unknown state {next_state}!")

        self.current_state = next_state
        self.input_type = self.state_data[next_state.value]['input_type']
        self.domain_min = self.state_data[next_state.value]['min'] \
            if not callable(self.state_data[next_state.value]['min']) else self.state_data[next_state.value]['min']()
        self.domain_max = self.state_data[next_state.value]['max'] \
            if not callable(self.state_data[next_state.value]['max']) else self.state_data[next_state.value]['max']()

        self.domain_length = self.state_data[next_state.value]['len']

        # Append history for debugging purposes
        self.state_history.append(next_state)

    # Custom Decorators
    @staticmethod
    def state_logic(instance, state, input_type: enums.InputType,
                    input_min: int | Callable = None, input_max: int | Callable = None,
                    input_len: int = None):
        """
        A decorator factory that registers a function as a logic provider within an instance of FiniteStateDevice and
        stores auxiliary state information such as input type and input range.

        Args:
            instance: an instance of a FiniteStateDevice to operate on
            state: The state to map 'func' to
            input_type: The input type for this state
            input_min: The input range's min for this state. This may be an int or a callable that returns an int.
            input_max: The input range's max for this state. This may be an int or a callable that returns an int.
            input_len: The input range's length for this state. This must be an int.

        Returns: A decorator that registers the wrapped function and passed input information to 'instance'
        """

        # Type and value checking
        if not isinstance(instance, FiniteStateDevice):
            raise TypeError(f"Can only wrap instances of FiniteStateDevice! Type {type(instance)} is not supported.")
        if state not in instance.state_data and state.value not in instance.state_data:
            instance.dump()
            raise ValueError(f"Unknown state {state}:{state.value}!")
        if instance.state_data[state.value]['logic']:
            instance.dump()
            raise ValueError(f"State.logic collision! {state} already has a logic function registered.")

        if input_min and (not callable(input_min) and not type(input_min) == int):
            instance.dump()
            raise TypeError(f"input_min must be an int or a callable! Got {type(input_min)} instead.")

        if input_max and (not callable(input_max) and not type(input_max) == int):
            instance.dump()
            raise TypeError(f"input_max must be an int or a callable! Got {type(input_max)} instead.")

        def decorate(fn):
            """
            Register to instance and then return the function untouched.
            """

            spec = inspect.getfullargspec(fn)
            if len(spec.args) != 1:
                instance.dump()
                raise ValueError(
                    f"""Error registering logic provider for state {state}.
                    State logic functions must accept only a single positional argument, not {len(spec.args)}!""")

            instance.state_data[state.value]['input_type'] = input_type
            instance.state_data[state.value]['min'] = input_min
            instance.state_data[state.value]['max'] = input_max
            instance.state_data[state.value]['len'] = input_len
            instance.state_data[state.value]['logic'] = fn

            return fn

        return decorate

    @staticmethod
    def state_content(instance, state):  # Outer decorator
        """
        A decorator factory that returns a factory that registers the wrapped function as the content provider for
        state 'state'.

        Args:
            instance: An instance of the FiniteStateDevice to modify
            state: The state to register the content function to

        Returns: A decorator function that registers the wrapped function as a content provider for a given state
        """

        # Check argument types and values
        if not isinstance(instance, FiniteStateDevice):
            raise TypeError(f"Can only wrap instances of FiniteStateDevice! Type {type(instance)} is not supported.")
        if state.value not in instance.state_data:
            instance.dump()
            raise ValueError(f"Unknown state {state}!")
        if instance.state_data[state.value]['content']:
            instance.dump()
            raise ValueError(f"State.content collision! {state} already has a content function registered.")

        # Inner decorator that receives the function
        def decorate(fn):
            """
            A simple decorator that registers the wrapped function to the passed instance
            """
            instance.state_data[state.value]['content'] = fn
            return fn

        return decorate

    def _logic(self, user_input: any) -> None:

        # Check for bad state data
        if self.current_state.value not in self.state_data:
            self.dump()
            raise ValueError(f"State {self.current_state} has not been registered with {self.name}!")

        if 'logic' not in self.state_data[self.current_state.value] \
                or not self.state_data[self.current_state.value]['logic']:
            self.dump()
            raise KeyError(f"No logical provider has been registered for state {self.current_state}!")

        self.state_data[self.current_state.value]['logic'](user_input)

    @property
    def components(self) -> dict[str, any]:
        # Check for bad state data
        if self.current_state.value not in self.state_data:
            raise ValueError(f"State {self.current_state} has not been registered with {self.name}!")

        if 'content' not in self.state_data[self.current_state.value] \
                or not self.state_data[self.current_state.value]['content']:
            raise KeyError(f"No logical provider has been registered for state {self.current_state}!")

        return self.state_data[self.current_state.value]['content']()
