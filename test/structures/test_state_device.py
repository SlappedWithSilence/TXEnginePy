import pytest

from game.structures.enums import InputType
from game.structures.state_device import StateDevice
from game.structures.messages import ComponentFactory
from game.util.input_utils import to_range


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


setter_mixed_cases_good = [
    # Trivial
    [InputType.INT, None, None, None],
    [InputType.STR, None, None, None],
    [InputType.ANY, None, None, None],
    [InputType.AFFIRMATIVE, None, None, None],
    [InputType.SILENT, None, None, None],

    # Int
    [InputType.INT, 0, None, None],
    [InputType.INT, -1, None, None],
    [InputType.INT, 1, None, None],
    [InputType.INT, 1000, None, None],
    [InputType.INT, 0, 0, None],
    [InputType.INT, -1, 0, None],
    [InputType.INT, -1, -1, None],
    [InputType.INT, 0, 1, None],
    [InputType.INT, -1, 1, None],
    [InputType.INT, -1, 13, None],
    [InputType.INT, -100, -20, None],

    # Str
    [InputType.STR, None, None, 1],
    [InputType.STR, None, None, 10],

]


@pytest.mark.parametrize("input_type, i_min, i_max, i_len", setter_mixed_cases_good)
def test_domain_setters_mixed(input_type: InputType, i_min: int | None, i_max: int | None, i_len: int | None):
    md = MockDevice(input_type)
    md.domain_min = i_min
    md.domain_max = i_max
    md.domain_length = i_len


@pytest.mark.parametrize("input_type, i_min, i_max, i_len", setter_mixed_cases_good)
def test_input_domain_property_setter(input_type: InputType, i_min: int | None, i_max: int | None, i_len: int | None):
    md = MockDevice(input_type)
    md.input_domain = to_range(i_min, i_max, i_len)


setter_mixed_cases_bad = [
    # INT
    [InputType.INT, 1, -1, None],  # Inverted min/max
    [InputType.INT, 6, 3, None],
    [InputType.INT, 3, 6, 5],  # Extraneous length
    [InputType.INT, None, None, 1],
    [InputType.INT, '3', 6, None],  # Bad types
    [InputType.INT, 3, '6', None],
    [InputType.INT, 3.2, 6, None],
    [InputType.INT, 3, 6.2, None],
    [InputType.INT, 3, 6, 1.1],
    [InputType.INT, 3, 6, "Definitely a number"],
    [InputType.INT, lambda: pow(2, 2), 6, None],
    [InputType.INT, -1, lambda: pow(2, 2), None],

    # STR
    [InputType.STR, None, None, 0],  # Bad length value
    [InputType.STR, None, None, -1],
    [InputType.STR, 3, 6, 0],
    [InputType.STR, 3, 6, -1],
    [InputType.STR, 3, 6, None],  # Extraneous values
    [InputType.STR, 3, 6, 1],
    [InputType.STR, True, 6, None],
    [InputType.STR, 3, False, None],
    [InputType.STR, None, False, 4],

]


@pytest.mark.parametrize("input_type, i_min, i_max, i_len", setter_mixed_cases_bad)
def test_domain_setters_mixed_bad(input_type, i_min, i_max, i_len):
    with pytest.raises(ValueError) as e_info:
        md = MockDevice(input_type)
        md.domain_min = i_min
        md.domain_max = i_max
        md.domain_length = i_len


@pytest.mark.parametrize("input_type, i_min, i_max, i_len", setter_mixed_cases_bad)
def test_input_domain_property_setter_bad(input_type, i_min, i_max, i_len):
    with pytest.raises(ValueError) as e_info:
        md = MockDevice(input_type)
        md.input_domain = to_range(i_min, i_max, i_len)


def test_input_any():
    """
    Test that StateDevice::input() correctly handles an input when
    state_device.input_type == InputType.ANY

    A counter must be tracked, so parameterization doesn't work on this test.
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
