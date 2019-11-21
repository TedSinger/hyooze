from colormath.color_objects import sRGBColor, XYZColor
from colormath.color_conversions import convert_color
from colormath.color_appearance_models import CIECAM02
from hyooze import xFF, DEPTH
from hyooze.mesh import EqualBrightnessMesh

REFERENCE_WHITE = convert_color(sRGBColor(1, 1, 1), XYZColor)


class Office:
    """Color perception models are environment dependent. This class encodes the
    assumptions about viewing conditions."""

    def __init__(self, ambient_lightness, background):
        self.ambient_lightness = ambient_lightness
        self.background = background
        background_xyz = convert_color(background, XYZColor)
        self.background_brightness = background_xyz.xyz_y

        self._mesh_cache = {}

    def rgb_to_cbh(self, r, g, b):
        target_xyz = convert_color(sRGBColor(r, g, b, is_upscaled=True), XYZColor)
        perception = CIECAM02(
            target_xyz.xyz_x,
            target_xyz.xyz_y,
            target_xyz.xyz_z,
            REFERENCE_WHITE.xyz_x,
            REFERENCE_WHITE.xyz_y,
            REFERENCE_WHITE.xyz_z,
            c=0.69, n_c=1, f=1,  # I do not know what these parameters mean
            l_a=self.ambient_lightness,
            y_b=self.background_brightness,
        )
        return perception.chroma, perception.brightness, perception.hue_angle

    def getMesh(self, b):
        if b not in self._mesh_cache:
            self._mesh_cache[b] = EqualBrightnessMesh(BRIGHT_OFFICE, b)
        return self._mesh_cache[b]


# 100 is a typical bright office. I am (optimistically) assuming that:
# 1) The screen is calibrated to be as bright as the office, and
# 2) The background is mostly white.
BRIGHT_OFFICE = Office(100, sRGBColor(1, 1, 1))

