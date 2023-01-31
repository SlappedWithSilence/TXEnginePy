from ...structures.enums import InputType
from ...structures.messages import Frame
from ...structures.state_device import StateDevice


class Engine:

    def __init__(self) -> None:
        debug_device = StateDevice(InputType.AFFIRMATIVE)  # TODO: Remove debugging code

        self.state_device_stack: list[StateDevice] = []

    def add_device(self, state_device: StateDevice) -> None:
        """
        Adds a state device to the stack. This forces the engine to pull frames from the last-added state device.
        A state device is automatically removed from the stack when it terminates.

        Args:
            state_device: The device to add to the stack

        Returns: None

        """
        state_device.engine = self
        self.state_device_stack.append(state_device)

    def pop_device(self) -> StateDevice:
        """
        Removes the most-recently-added state device from the state_device_stack

        Returns: The state device at the end of the state_device_stack

        """
        state_device = self.state_device_stack[-1]
        del self.state_device_stack[-1]
        return state_device

    def submit_input(self, user_input: any) -> bool:
        """
        Submit the user's input to the engine and advance to the next logical game frame

        Args:
            user_input: The user's last distinct input.

        Returns: True if the input was valid, false otherwise

        """
        pass

    def __load(self) -> None:
        """
        Load game assets and save data from disk.

        Returns:

        """
        pass

    def __save(self) -> None:
        """
        Dump save data to the disk.

        Returns:

        """
        pass

    def get_device(self) -> StateDevice:
        """
        Retrieves the topmost device from the state_device_stack

        Returns: The topmost device from the state_device_stack

        """
        return self.state_device_stack[-1]

    def get_frame(self) -> Frame:
        """
        Retrieves the current logical frame. Not to be confused with submit_input.

        Returns: the current game frame

        """
        return self.get_device().to_frame()
