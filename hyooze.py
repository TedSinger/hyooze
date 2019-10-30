import bisect

from colormath.color_objects import sRGBColor, XYZColor
from colormath.color_conversions import convert_color
from colormath.color_appearance_models import CIECAM02
import numpy
import math
from matplotlib import pyplot

def color_to_td_pair(color):
    td = '''<td style='color: {fg}; background-color: {bg}; text-rendering: optimizeLegibility; line-height:0; margin:0; font-weight: bold; font-size: x-large; font-family: monospace;'>{text}</td>'''
    return td.format(fg=color, bg='#f4f5f4', text=color) + td.format(fg="#000000", bg=color, text=color)
    
def brightness_group_to_rows(brightness):
    ret = ''
    
    nRows = max([len(chroma) for chroma in brightness])
    for i in range(nRows):
        pairs = [color_to_td_pair(chroma[i]) if i < len(chroma) else "<td style='background-color: #ffffff'/>"*2 for chroma in brightness]
        tds = ''.join(pairs)
        ret += f'''<tr>{tds}</tr>'''
    return ret

def demo(brightnesses):
    rows = list(map(brightness_group_to_rows, brightnesses))
    rows = ''.join(rows)
    return f'''<table>{rows}</table>'''

LIME_ON_BLUE = f'''<text style='font-weight: bold; color: HSL(120, 100%, 50%); background-color: HSL(240, 100%, 50%);'>
Lime (#00FF00, HSL(120, 100%, 50%)) on Blue (#0000FF, HSL(240, 100%, 50%))<br>
is quite readable, even though the HSL lightness is the same.</text>'''


WHITE_XYZ = convert_color(sRGBColor(1,1,1), XYZColor)
BITS = 8
M = 2**(8 - BITS) # useful for doing some quick, low-res iteration
DEPTH = 2**BITS
xFF = DEPTH - 1

class Office:
    def __init__(self, ambient_lightness, background):
        self.ambient_lightness = ambient_lightness
        self.background = background
        background_xyz = convert_color(background, XYZColor)
        self.background_brightness = background_xyz.xyz_y
        self._mesh_cache = {}
        
    def rgb_to_cbh(self, r, g, b):
        xyz = convert_color(sRGBColor(r*M, g*M, b*M, is_upscaled=True), 
                            XYZColor)
        cbh = CIECAM02(
            xyz.xyz_x, xyz.xyz_y, xyz.xyz_z,
            WHITE_XYZ.xyz_x, WHITE_XYZ.xyz_y, WHITE_XYZ.xyz_z,
            c=0.69, n_c=1, f=1,
            l_a=self.ambient_lightness, y_b=self.background_brightness)
        return cbh.colorfulness, cbh.brightness, cbh.hue_angle

    def find_green(self, target_brightness, red, blue, lo=0, hi=xFF):
        assert lo <= hi
        assert red != DEPTH
        assert blue != DEPTH
        while hi - lo > 1:
            mid = (lo + hi) / 2
            c, b, h = self.rgb_to_cbh(red, mid, blue)
            if b < target_brightness:
                lo = math.floor(mid)
            else:
                hi = math.ceil(mid)

        c0, b0, h0 = self.rgb_to_cbh(red, lo, blue)
        c1, b1, h1 = self.rgb_to_cbh(red, hi, blue)
        if abs(b0-target_brightness) < abs(b1-target_brightness):
            best, c, b, h = lo, c0, b0, h0
        else:
            best, c, b, h = hi, c1, b1, h1
        return (True, red, best, blue, lo, hi, c, b, h)

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

def hexcode(meshpoint):
    return sRGBColor(meshpoint[Vals.RED]*M, 
                     meshpoint[Vals.GREEN_BEST]*M, 
                     meshpoint[Vals.BLUE]*M, 
                     is_upscaled=True).get_rgb_hex()

BRIGHT_OFFICE = Office(100, sRGBColor(1,1,1))

def clamp(idx):
    return min(idx, xFF)

MESHES = {}

class EqualBrightnessMesh:
    """Dims 1 and 2 are Red and Blue"""
    def __init__(self, office, target_brightness):
        self.office = office
        self.brightness = target_brightness
        self.mesh = numpy.zeros((DEPTH, DEPTH, Vals.HUE+1))
        self.mesh[0, 0] = office.find_green(target_brightness, 0, 0)
        self.mesh[0, xFF] = office.find_green(target_brightness, 0, xFF)
        self.mesh[xFF, 0] = office.find_green(target_brightness, xFF, 0)
        self.mesh[xFF, xFF] = office.find_green(target_brightness, xFF, xFF)
    
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
        mask = 1
        while ((red == xFF) or (mask & red == 0)) and ((blue == xFF) or (mask & blue == 0)):
            mask = (mask << 1)
        if (red != xFF) and (mask & red != 0):
            low_red, low_blue = (red - (mask & red), blue)
            high_red, high_blue = (red + (mask & red), blue)
        else:
            low_red, low_blue = (red, blue - (mask & blue))
            high_red, high_blue = (red, blue + (mask & blue))
        # print(red, blue, low_red, low_blue, high_red, high_blue)
        lo = self._find_green(clamp(high_red), clamp(high_blue))[Vals.GREEN_LO]
        hi = self._find_green(low_red, low_blue)[Vals.GREEN_HI]
        ret = self.office.find_green(self.brightness, red, blue, 
                                     lo=lo, hi=hi)
        self.mesh[red, blue, :] = ret
        return ret
    
    def compute(self):
        for red in range(DEPTH):
            for blue in range(DEPTH):
                self._find_green(red, blue)


class ArcDict:
    """We want to look at hue-arcs of possibilities, rather than individual colors"""
    def __init__(self, vals, resolution):
        self._res = resolution
        self._vals = vals
        self._list = sorted(vals.keys())
    
    def __getitem__(self, needle):
        insertion_point = bisect.bisect(self._list, needle)
        
        if not self._list:
            raise KeyError(needle)
        elif insertion_point == 0:
            candidates = [self._list[0]]
        elif insertion_point == len(self._list):
            candidates = [self._list[-1]]
        else:
            candidates = [self._list[insertion_point - 1], self._list[insertion_point]]

        best_key = min(candidates, key=lambda key: abs(needle - key))
        if abs(needle - best_key) > self._res:
            raise KeyError(needle)
        else:
            return self._vals[best_key]
    
    def __repr__(self):
        intervals = [[self._list[0], self._list[0]]]
        for key in self._list:
            if key > intervals[-1][1] + self._res * 2:
                intervals.append([key, key])
            else:
                intervals[-1][1] = key
        key_to_str = lambda k: f'{round(k, 1)}: {self._vals[k]}'
        
        strs = [f'[{key_to_str(low)}]' if low == high else f'[{key_to_str(low)}, {key_to_str(high)}]' for [low, high] in intervals]
        range_text = ', '.join(strs)
        return f'ArcDict({range_text})'


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
    brightness_mask = numpy.abs(mesh[:,:,Vals.BRIGHTNESS] - target_brightness) < 0.5678*M #arbitrary small number
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

def ciecam02_brightness_planes(office, brightnesses, target_chromas):
    matches = {}
    fig = pyplot.figure(figsize=(12,12))
    for i, brightness in enumerate(brightnesses):
        mesh = EqualBrightnessMesh.get(brightness)
        mesh.compute()
        axes = fig.add_subplot((len(brightnesses)+1//2), 2, i+1)
        axes.set_aspect('equal')
        matches[brightness] = display_brightness_level(mesh.mesh, axes, brightness, target_chromas)
    
    return matches, fig
    