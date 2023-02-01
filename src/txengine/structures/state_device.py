import weakref

from pydantic import BaseModel

from .enums import InputType, is_valid_range
from .messages import Frame


class StateDevice(BaseModel):
    input_type: InputType
    input_range: dict[str: any] = {"upper_limit": None,
                                   "lower_limit": None,
                                   "length": None
                                   }
    __engine = None

    @property
    def engine(self):
        return self.__engine

    @engine.setter
    def engine(self, engine_in) -> None:
        self.__engine = weakref.ref(engine_in)

    @property
    def domain_lower_limit(self) -> any:
        return self.input_range["lower_limit"]

    @domain_lower_limit.setter
    def domain_lower_limit(self, val: any) -> None:
        if is_valid_range(self.input_type,
                          lower_limit=val,
                          upper_limit=self.domain_upper_limit,
                          length=self.domain_length):
            self.input_range["lower_limit"] = val
        else:
            raise ValueError(f"Tried to set lower limit of {self.input_type} to value of type {type(val)}!")

    @property
    def domain_upper_limit(self) -> any:
        return self.input_range["upper_limit"]

    @domain_upper_limit.setter
    def domain_upper_limit(self, val: any) -> None:
        if is_valid_range(self.input_type,
                          lower_limit=self.domain_lower_limit,
                          upper_limit=val,
                          length=self.domain_length):
            self.input_range["lower_limit"] = val
        else:
            raise ValueError(f"Tried to set lower limit of {self.input_type} to value of type {type(val)}!")

    @property
    def domain_length(self) -> [int, None]:
        return self.input_range["length"]

    @domain_length.setter
    def domain_length(self, val: [int, None]) -> None:
        if is_valid_range(self.input_type,
                          lower_limit=self.domain_lower_limit,
                          upper_limit=self.domain_upper_limit,
                          length=self.domain_length):
            self.input_range["lower_limit"] = val
        else:
            raise ValueError(f"Tried to set lower limit of {self.input_type} to value of type {type(val)}!")

    @property
    def input_domain(self) -> dict[str, any]:
        return self.input_range

    @input_domain.setter
    def input_domain(self, input_type: InputType, upper_limit=None, lower_limit=None, length=None) -> None:
        if not is_valid_range(input_type, upper_limit, lower_limit, length):
            raise ValueError(f"""Invalid input domain values for type {input_type}:\n 
                                                                       lower_limit: {lower_limit}\n
                                                                       upper_limit: {upper_limit}\n
                                                                       length: {length}
                              """)

    @property
    def components(self) -> dict[str, any]:
        raise NotImplementedError

    def validate_input(self, input_value) -> bool:

        # Input must be str matching the set of strings in the array
        if self.input_type == InputType.AFFIRMATIVE:
            if type(input_value) == str and str.lower(input_value) in ['y', 'n', 'yes', 'no']:
                return True
            else:
                return False

        # Input must be an int that is below the maximum and above the minimum
        elif self.input_type == InputType.INT:
            if type(input_value) == int:
                if self.input_range["lower_limit"] and input_value < self.input_range["lower_limit"]:
                    return False

                if self.input_range["upper_limit"] and input_value > self.input_range["upper_limit"]:
                    return False

                return True

        # Input must be a str shorter than length
        elif self.input_type == InputType.STR:
            if type(input_value) == str:
                if self.input_range["length"] and len(input_value) <= self.input_range["length"]:
                    return True

            return False
        else:
            raise ValueError(f"Unknown InputType: {self.input_type.name}!")

    def __logic(self, user_input: any) -> None:
        """
        The actual game logic. This must be overriden by subclasses.

        Args:
            user_input:

        Returns: None

        """
        raise NotImplementedError("Cannot run a bare StateDevice!")

    def input(self, user_input:any) -> bool:
        """
        Submits the user's input to the state device. The state device advances its internal logic and modifies its
        output. If the input is not valid, it is rejected.

        Args:
            user_input: The value passed by the user

        Returns: True if the input is valid, False otherwise

        """
        if self.validate_input(user_input):
            self.__logic(user_input)
            return True

        return False

    def to_frame(self) -> Frame:
        return Frame(self.components, self.input_type, self.input_range, self.__class__.__name__)
