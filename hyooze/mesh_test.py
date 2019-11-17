from hyooze.perception import BRIGHT_OFFICE
from hyooze.mesh import find_green
from hyooze import xFF
import random

def test_find_green_sanity():
    assert find_green(BRIGHT_OFFICE, 0, 0, 0)[2] == 0
    assert find_green(BRIGHT_OFFICE, 1000, 0, 0)[2] == xFF
    assert find_green(BRIGHT_OFFICE, 0, xFF, xFF)[2] == 0
    assert find_green(BRIGHT_OFFICE, 1000, xFF, xFF)[2] == xFF

def test_find_green_accuracy():
    target_brightness = random.randint(0, 120)
    red = random.randint(0, 255)
    blue = random.randint(0, 255)
    best_green = find_green(BRIGHT_OFFICE, target_brightness, red, blue)[2]
    _, this_brightness, _ = BRIGHT_OFFICE.rgb_to_cbh(red, best_green, blue)
    if best_green < xFF:
        other_green = best_green + 1
        _, other_brightness, _ = BRIGHT_OFFICE.rgb_to_cbh(red, other_green, blue)
        assert abs(this_brightness - target_brightness) < abs(other_brightness - target_brightness)
    if best_green > 0:
        other_green = best_green - 1
        _, other_brightness, _ = BRIGHT_OFFICE.rgb_to_cbh(red, other_green, blue)
        assert abs(this_brightness - target_brightness) < abs(other_brightness - target_brightness)
