import dataclasses
import weakref
from abc import abstractmethod
from .enums import InputType, is_valid_range, to_range
from .messages import Frame


@dataclasses.dataclass
class StateDevice:
    input_type: InputType
    input_range: dict[str, int] = dataclasses.field(default_factory=to_range)
    _engine: any = None  # DO NOT SET

    def get_engine(self):
        return self._engine

    def set_engine(self, engine_in) -> None:
        self._engine = weakref.ref(engine_in)

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
        return self.input_range["max"]

    @domain_max.setter
    def domain_max(self, val: any) -> None:
        if is_valid_range(self.input_type,
                          min_value=self.domain_min,
                          max_value=val,
                          length=self.domain_length):
            self.input_range["min"] = val
        else:
            raise ValueError(f"Tried to set lower limit of {self.input_type} to value of type {type(val)}!")

    @property
    def domain_length(self) -> [int, None]:
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
        pass

    def validate_input(self, input_value) -> bool:

        if self.input_type == InputType.SILENT:
            return True

        # Input must be str matching the set of strings in the array
        if self.input_type == InputType.AFFIRMATIVE:
            if type(input_value) == str and str.lower(input_value) in ['y', 'n', 'yes', 'no']:
                return True
            else:
                return False

        # Input must be an int that is below the maximum and above the minimum
        elif self.input_type == InputType.INT:
            if type(input_value) == int:
                if self.input_range["min"] and input_value < self.input_range["min"]:
                    return False

                if self.input_range["max"] and input_value > self.input_range["max"]:
                    return False

                return True

        # Input must be a str shorter than length
        elif self.input_type == InputType.STR:
            if type(input_value) == str:
                if self.input_range["len"] and len(input_value) <= self.input_range["len"]:
                    return True

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

    def to_frame(self) -> Frame:
        """
            A method to convert a state device into a corresponding frame.

            Returns: The Frame-equivalent of a given state device

        """
        return self.__frame__()
