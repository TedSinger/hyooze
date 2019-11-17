from colormath.color_objects import sRGBColor
import numpy
import math
from hyooze import DEPTH, xFF
from hyooze.perception import BRIGHT_OFFICE
import xarray as xr
from collections import namedtuple

HyoozeColor = namedtuple('HyoozeColor', ['computed', 'red', 'best_green', 'blue', 'low_green', 'high_green', 'chroma', 'brightness', 'hue'])

class Vals:
    COMPUTED = 0
    RED = 1
    GREEN_BEST = 2
    BLUE = 3
    GREEN_LO = 4
    GREEN_HI = 5
    CHROMA = 6
    BRIGHTNESS = 7
    HUE = 8


def find_green(office, target_brightness, red, blue, lo=0, hi=xFF):
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
    return (True, red, best, blue, lo, hi, c, b, h)

def hexcode(meshpoint):
    return sRGBColor(meshpoint[Vals.RED], 
                     meshpoint[Vals.GREEN_BEST], 
                     meshpoint[Vals.BLUE], 
                     is_upscaled=True).get_rgb_hex()
MESHES = {}

class EqualBrightnessMesh:
    """Dims 1 and 2 are Red and Blue"""
    def __init__(self, office, target_brightness):
        self.office = office
        self.brightness = target_brightness
        self.mesh = numpy.zeros((DEPTH, DEPTH, Vals.HUE+1))
        self.mesh[0, 0] = find_green(office, target_brightness, 0, 0)
        self.mesh[0, xFF] = find_green(office, target_brightness, 0, xFF)
        self.mesh[xFF, 0] = find_green(office, target_brightness, xFF, 0)
        self.mesh[xFF, xFF] = find_green(office, target_brightness, xFF, xFF)
    
    @classmethod
    def get(cls, b):
        if b not in MESHES:
            MESHES[b] = EqualBrightnessMesh(BRIGHT_OFFICE, b)
        return MESHES[b]
        
    def _find_green(self, red, blue):
        """To reduce the number of calls to office.rgb_to_cbh, we use the endpoints of
        some interval as bounds on the possible green for the midpoint. Since we want
        to compute across the whole mesh anyway, it nicely doubles as a cache and
        recursive base-case.
        """
        if self.mesh[red, blue, Vals.COMPUTED]:
            return self.mesh[red, blue, :]

        low_red, low_blue, high_red, high_blue = _get_bounds(red, blue)

        lo = self._find_green(high_red, high_blue)[Vals.GREEN_LO]
        hi = self._find_green(low_red, low_blue)[Vals.GREEN_HI]
        ret = find_green(self.office, self.brightness, red, blue, 
                                     lo=lo, hi=hi)
        self.mesh[red, blue, :] = ret
        return ret
    
    def compute(self):
        for red in range(0, DEPTH, 8):
            for blue in range(0, DEPTH, 4):
                self._find_green(red, blue)

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

#doing two things. mesh stuff belongs on the mesh
def display_brightness_level(mesh, pyplotaxes, target_brightness, target_chromas):
    for chroma in target_chromas:
        pyplotaxes.plot(
            chroma * numpy.cos(numpy.arange(0, 6.28, 0.01)), 
            chroma * numpy.sin(numpy.arange(0, 6.28, 0.01)),
            color='black'
        )
    
    theta = mesh[:, :, Vals.HUE] * math.pi / 180
    x = mesh[:, :, Vals.CHROMA] * numpy.cos(theta)
    y = mesh[:, :, Vals.CHROMA] * numpy.sin(theta)
    
    hexes = numpy.apply_along_axis(hexcode, 2, mesh)
    brightness_mask = numpy.abs(mesh[:,:,Vals.BRIGHTNESS] - target_brightness) < 0.5678 #arbitrary small number
    xs = x[brightness_mask]
    ys = y[brightness_mask]
    colors = hexes[brightness_mask]
    matching_colors = {}
    for chroma in target_chromas:
        chroma_mask = brightness_mask & (numpy.abs(mesh[:,:,Vals.CHROMA] - chroma) < 2.3456) #arbitrary small number
        hues = mesh[:,:,Vals.HUE][chroma_mask]
        matches = hexes[chroma_mask]
        matching_colors[chroma] = dict(zip(hues, matches))
    min_chroma = numpy.min(mesh[:, :, Vals.CHROMA])
    matching_colors[0] = hexes[mesh[:, :, Vals.CHROMA] == min_chroma][0]
    pyplotaxes.scatter(xs,ys,c=colors, marker='.')
    return matching_colors
