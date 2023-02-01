from ...structures.state_device import StateDevice


class RoomDevice(StateDevice):

    id: int
    actions: list[ActionDevice]

    @property
    def components(self) -> dict[str, any]:
        pass