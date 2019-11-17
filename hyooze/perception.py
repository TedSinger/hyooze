from colormath.color_objects import sRGBColor, XYZColor
from colormath.color_conversions import convert_color
from colormath.color_appearance_models import CIECAM02
from hyooze import xFF, DEPTH

WHITE_XYZ = convert_color(sRGBColor(1,1,1), XYZColor)


class Office:
    def __init__(self, ambient_lightness, background):
        self.ambient_lightness = ambient_lightness
        self.background = background
        background_xyz = convert_color(background, XYZColor)
        self.background_brightness = background_xyz.xyz_y
        
    def rgb_to_cbh(self, r, g, b):
        xyz = convert_color(sRGBColor(r, g, b, is_upscaled=True), 
                            XYZColor)
        cbh = CIECAM02(
            xyz.xyz_x, xyz.xyz_y, xyz.xyz_z,
            WHITE_XYZ.xyz_x, WHITE_XYZ.xyz_y, WHITE_XYZ.xyz_z,
            c=0.69, n_c=1, f=1,
            l_a=self.ambient_lightness, y_b=self.background_brightness)
        return cbh.colorfulness, cbh.brightness, cbh.hue_angle


BRIGHT_OFFICE = Office(100, sRGBColor(1,1,1))