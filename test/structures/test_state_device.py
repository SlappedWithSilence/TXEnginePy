from game.structures.enums import InputType
from game.structures.state_device import StateDevice
from game.structures.messages import ComponentFactory


class MockDevice(StateDevice):

    def __init__(self, input_type: InputType):
        super().__init__(input_type)

        self.counter: int = 0

    @property
    def components(self) -> dict[str, any]:
        return ComponentFactory.get([str(self.counter)])

    def _logic(self, user_input: any) -> None:
        self.counter = self.counter + 1


def test_init():
    md = MockDevice(InputType.ANY)
    assert isinstance(md, StateDevice)
    assert md.name == "StateDevice::MockDevice"
    assert type(md.input_range) == dict
    assert 'max' in md.input_range
    assert 'min' in md.input_range
    assert 'len' in md.input_range
    assert md.input_type == InputType.ANY
    assert not md._controller


def test_input_any():
    md = MockDevice(InputType.ANY)

    various_inputs = ['', ' ', None, 1, True]

    assert md.counter == 0

    for idx, val in enumerate(various_inputs):
        assert md.input(val)
        assert md.counter == idx + 1


def test_components_trivial():
    md = MockDevice(InputType.ANY)
    res = md.components
    assert res
    assert type(res) == dict
    assert 'content' in res
    assert type(res['content']) == list
    assert len(res['content']) == 1
    assert res['content'][0] == '0'
