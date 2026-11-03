import pytest

from src.utils.image_position import image_position

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("character_id, expected", [
    (123, 4),     # example from the task: 1 + 3
    (1, 1), (7, 7), (9, 9),          # one digit: tens digit is 0
    (10, 1), (45, 9), (99, 18),      # two digits: tens + ones
    (100, 1), (800, 8), (826, 14), (999, 18),   # three digits: hundreds + ones
    (1234, 6),    # 4+ digits: same hundreds + ones rule (2 + 4)
])
def test_image_position(character_id, expected):
    assert image_position(character_id) == expected


@pytest.mark.parametrize("bad_id", [0, -5, 1000, 2000])
def test_invalid_or_zero_position_raises(bad_id):
    with pytest.raises(ValueError):
        image_position(bad_id)


@pytest.mark.parametrize("bad_id", ["12", 1.5, None, True])
def test_non_int_raises(bad_id):
    with pytest.raises(TypeError):
        image_position(bad_id)