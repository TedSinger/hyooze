from colormath.color_objects import sRGBColor
import math
from hyooze import DEPTH, xFF
from hyooze.perception import BRIGHT_OFFICE
import xarray as xr
from collections import namedtuple, OrderedDict

MESH_DEFAULTS = OrderedDict([
    ('computed', False),
    ('best_green', 0),
    ('low_green', 0),
    ('high_green', 0),
    ('chroma', 0.0),
    ('brightness', 0.0),
    ('hue', 0.0),
    ('x', 0.0),
    ('y', 0.0),
    ('hexcode', '#000000'),
])

def _nearest_green(office, target_brightness, red, blue, lo=0, hi=xFF):
    assert lo <= hi
    assert red != DEPTH
    assert blue != DEPTH
    while hi - lo > 1:
        mid = (lo + hi) / 2
        c, b, h = office.rgb_to_cbh(red, mid, blue)
        if b < target_brightness:
            lo = math.floor(mid)
        else:
            hi = math.ceil(mid)

    c0, b0, h0 = office.rgb_to_cbh(red, lo, blue)
    c1, b1, h1 = office.rgb_to_cbh(red, hi, blue)
    if abs(b0-target_brightness) < abs(b1-target_brightness):
        best, c, b, h = lo, c0, b0, h0
    else:
        best, c, b, h = hi, c1, b1, h1
    theta = h * math.pi / 180
    x = c * math.cos(theta)
    y = c * math.sin(theta)
    hexcode = sRGBColor(red, best, blue, is_upscaled=True).get_rgb_hex()
    return (True, best, lo, hi, c, b, h, x, y, hexcode)



class EqualBrightnessMesh:
    _MESHES = {}
    @classmethod
    def get(cls, b):
        if b not in cls._MESHES:
            cls._MESHES[b] = EqualBrightnessMesh(BRIGHT_OFFICE, b)
        return cls._MESHES[b]

    def __init__(self, office, target_brightness):
        self.office = office
        self.brightness = target_brightness
        measures = dict((measure, (['red', 'blue'], [[default]*DEPTH]*DEPTH)) 
                for measure, default in MESH_DEFAULTS.items())
        self.mesh = xr.Dataset(measures, 
            coords={'red':list(range(DEPTH)), 
                    'blue':list(range(DEPTH))})
        
        self._init_corners()

    def _set(self, red, blue, vals):
        for key, val in zip(MESH_DEFAULTS, vals):
            self.mesh[key].loc[{'red':red, 'blue':blue}] = val

    def _init_corners(self):
        for r in [0, xFF]:
            for b in [0, xFF]:
                new_value = _nearest_green(self.office, self.brightness, r, b)
                self._set(r, b, new_value)

    def _get_green_bounds(self, red, blue):
        """To reduce the number of calls to office.rgb_to_cbh, we use the endpoints of
        some interval as bounds on the possible green for the midpoint. Since we want
        to compute across the whole mesh anyway, it nicely doubles as a cache and
        recursive base-case.
        """
        if not self.mesh.isel(red=red, blue=blue).computed:
            low_red, low_blue, high_red, high_blue = _get_bounds(red, blue)

            lo = self._get_green_bounds(high_red, high_blue).low_green
            hi = self._get_green_bounds(low_red, low_blue).high_green
            new_value = _nearest_green(self.office, self.brightness, red, blue, 
                                         lo=lo, hi=hi)
            self._set(red, blue, new_value)
        return self.mesh.isel(red=red, blue=blue)
    
    def compute(self, resolution):
        for red in range(0, DEPTH, resolution):
            for blue in range(0, DEPTH, resolution):
                self._get_green_bounds(red, blue)

def _clamp(idx):
    return min(idx, xFF)

def _get_bounds(red, blue):
    """
    >>> _get_bounds(0b1101, 0b1010)
    0b1100, 0b1010, 0b1110, 0b1010
    >>> _get_bounds(0b1100, 0b1010)
    0b1100, 0b1000, 0b1100, 0b1100
    """
    # We want to ensure that 1) most points choose bounds that are close by, and
    # 2) the graph of dependencies is acyclic
    # So we round the least-significant bit from either coordinate both up and down
    if red in [0, xFF] and blue in [0, xFF]:
        raise ValueError("0 and xFF should be roots of the dependency graph. Their green values must be computed from the full range.")
    mask = 1
    while ((red == xFF) or (mask & red == 0)) and ((blue == xFF) or (mask & blue == 0)):
        mask = (mask << 1)
    if (red != xFF) and (mask & red != 0):
        low_red, low_blue = (red - (mask & red), blue)
        high_red, high_blue = (red + (mask & red), blue)
    else:
        low_red, low_blue = (red, blue - (mask & blue))
        high_red, high_blue = (red, blue + (mask & blue))
    return low_red, low_blue, _clamp(high_red), _clamp(high_blue)



def get_masks(mesh, brightness, chromas, b_tolerance=0.5678, c_tolerance=2.3456):
    matching_brightness = abs(mesh.brightness - brightness) < b_tolerance
    matching_chromas = dict(
        [(c, (abs(mesh.chroma - c) < c_tolerance) & matching_brightness) for c in chromas]
    )
    
    return matching_brightness, matching_chromas


def get_colors_by_mask(mesh, mask, attrs):
    return [mesh[a].data[mask] for a in attrs]

