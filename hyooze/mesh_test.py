from hyooze.perception import BRIGHT_OFFICE
from hyooze.mesh import _nearest_green, _get_bounds
from hyooze import xFF
import random


def test_nearest_green_sanity():
    assert _nearest_green(BRIGHT_OFFICE, 0, 0, 0)[1] == 0
    assert _nearest_green(BRIGHT_OFFICE, 1000, 0, 0)[1] == xFF
    assert _nearest_green(BRIGHT_OFFICE, 0, xFF, xFF)[1] == 0
    assert _nearest_green(BRIGHT_OFFICE, 1000, xFF, xFF)[1] == xFF


def _test_nearest_green_accuracy():
    target_brightness = random.randint(0, 120)
    red = random.randint(0, 255)
    blue = random.randint(0, 255)
    best_green = _nearest_green(BRIGHT_OFFICE, target_brightness, red, blue)[1]
    _, this_brightness, _ = BRIGHT_OFFICE.rgb_to_cbh(red, best_green, blue)
    if best_green < xFF:
        other_green = best_green + 1
        _, other_brightness, _ = BRIGHT_OFFICE.rgb_to_cbh(red, other_green, blue)
        assert abs(this_brightness - target_brightness) < abs(
            other_brightness - target_brightness
        )
    if best_green > 0:
        other_green = best_green - 1
        _, other_brightness, _ = BRIGHT_OFFICE.rgb_to_cbh(red, other_green, blue)
        assert abs(this_brightness - target_brightness) < abs(
            other_brightness - target_brightness
        )


def test_nearest_green_accuracy():
    for i in range(1000):
        _test_nearest_green_accuracy()


def test_get_bounds():
    assert _get_bounds(0b1101, 0b1010) == (0b1100, 0b1010, 0b1110, 0b1010)
    assert _get_bounds(0b1100, 0b1010) == (0b1100, 0b1000, 0b1100, 0b1100)
    success = False
    try:
        _get_bounds(0b0000, 0b0000)
        success = True
    except ValueError:
        pass
    assert not success
