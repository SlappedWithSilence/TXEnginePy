import pytest

from game.structures.enums import InputType
from game.structures.state_device import StateDevice
from game.structures.messages import ComponentFactory


class MockDevice(StateDevice):
    """
    A trivial subclass of StateDevice designed to allow for easy testing of commonly-used StateDevice functions.
    """

    def __init__(self, input_type: InputType):
        super().__init__(input_type)

        self.counter: int = 0

    @property
    def components(self) -> dict[str, any]:
        return ComponentFactory.get([str(self.counter)])

    def _logic(self, user_input: any) -> None:
        self.counter = self.counter + 1


def test_init():
    """
    Test that a basic subclass of StateDevice is correctly initialized
    """
    md = MockDevice(InputType.ANY)
    assert isinstance(md, StateDevice)
    assert md.name == "StateDevice::MockDevice"
    assert type(md._input_range) == dict
    assert 'max' in md._input_range
    assert 'min' in md._input_range
    assert 'len' in md._input_range
    assert md.input_type == InputType.ANY
    assert not md._controller


def test_components_trivial():
    """
    Test that StateDevice::components returns the correct value in a trivial case
    """
    md = MockDevice(InputType.ANY)
    res = md.components
    assert res
    assert type(res) == dict
    assert 'content' in res
    assert type(res['content']) == list
    assert len(res['content']) == 1
    assert res['content'][0] == '0'


domain_min_set_cases_good = [0, -1, 2222222, None]


@pytest.mark.parametrize("value", domain_min_set_cases_good)
def test_domain_min_set_good(value):
    """
    Test that a given valid value is correctly set using StateDevice::min
    property.

    Note that correctness is dependent on input_utils.is_valid_range
    """
    md = MockDevice(InputType.INT)
    md.domain_min = value

    assert md.input_domain['min'] == value


domain_min_set_cases_bad = [2.2, lambda: pow(2, 2), '5']


@pytest.mark.parametrize("value", domain_min_set_cases_bad)
def test_domain_min_set_good(value):
    """
    Test that StateDevice::domain_min setter rejects badly-typed values

    Note that correctness is dependent on input_utils.is_valid_range
    """
    with pytest.raises(ValueError) as e_info:
        md = MockDevice(InputType.INT)
        md.domain_min = value


domain_max_set_cases_good = [0, -1, 2222222, None]


@pytest.mark.parametrize("value", domain_max_set_cases_good)
def test_domain_max_set_good(value):
    """
    Test that a given valid value is correctly set using StateDevice::domain_max property.

    Note that correctness is dependent on input_utils.is_valid_range
    """
    md = MockDevice(InputType.INT)
    md.domain_max = value

    assert md.input_domain['max'] == value


domain_max_set_cases_bad = [2.2, lambda: pow(2, 2), '5']


@pytest.mark.parametrize("value", domain_max_set_cases_bad)
def test_domain_max_set_bad(value):
    """
    Test that StateDevice::domain_max setter rejects badly-typed values

    Note that correctness is dependent on input_utils.is_valid_range
    """
    with pytest.raises(ValueError) as e_info:
        md = MockDevice(InputType.INT)
        md.domain_max = value


domain_len_set_cases_good = [1, 2222222, None]


@pytest.mark.parametrize("value", domain_len_set_cases_good)
def test_domain_len_set_good(value):
    """
    Test that a given valid value is correctly set using StateDevice::domain_length property.

    Note that correctness is dependent on input_utils.is_valid_range
    """
    md = MockDevice(InputType.STR)
    md.domain_length = value

    assert md.input_domain['len'] == value


domain_len_set_cases_bad = [2.2, lambda: pow(2, 2), '5', 0, -1]


@pytest.mark.parametrize("value", domain_len_set_cases_bad)
def test_domain_len_set_bad(value):
    """
    Test that StateDevice::domain_length setter rejects badly-typed values

    Note that correctness is dependent on input_utils.is_valid_range
    """
    with pytest.raises(ValueError) as e_info:
        md = MockDevice(InputType.STR)
        md.domain_length = value


def test_input_any():
    """
    Test that StateDevice::input() correctly handles an input when
    state_device.input_type == InputType.ANY
    """
    md = MockDevice(InputType.ANY)

    various_inputs = ['', ' ', None, 1, True]

    assert md.counter == 0

    for idx, val in enumerate(various_inputs):
        assert md.input(val)
        assert md.counter == idx + 1


def test_input_int():
    pass


def test_input_affirmative():
    pass


def test_input_silent():
    pass


def test_frame():
    pass
