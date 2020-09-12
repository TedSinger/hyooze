from hyooze.cache import get_conn
from hyooze.brightness import fit_greys_between, grey_to_brightness
from hyooze.chroma import max_chroma_boundary, chroma_area
from hyooze.hue import choose_hues
from hyooze.equal_space import select_colors
from matplotlib import pyplot
import math
import numpy
import pandas

conn = get_conn()

greys = fit_greys_between(9, "#000000", "#f7f7f6", conn) + ["#f7f7f6"]
brightnesses = [grey_to_brightness(grey, conn) for grey in greys]
colors = []

for grey, brightness in zip(greys, brightnesses):
    print(grey)

    area = chroma_area(max_chroma_boundary(brightness, conn))
    these_colors = select_colors(brightness, 4 + int(area / 4.5e8), conn)
    for chroma, hue, hexcode in these_colors:
        colors.append((brightness, chroma, hue, hexcode))

df = pandas.DataFrame(data=colors, columns=["brightness", "chroma", "hue", "hexcode"])

h0, h1 = (-180, 180)
h_size = h1 - h0
r = 10
HEIGHT = 300
width = 400


def scale_brightness(b):
    index = min(range(len(greys)), key=lambda i: abs(brightnesses[i] - b))
    return round((width - 4 * r) * index / (len(greys) - 1), 2) + 2 * r


def scale_hue(hue, height):
    return round((height - 4 * r) * ((hue - h0) / h_size), 2) + 2 * r


def row_to_circle(brightness, hue, hexcode, height):
    return f'<circle cx="{scale_brightness(brightness)}" cy="{scale_hue(hue, height)}" r="{r}" fill="{hexcode}"><title>{hexcode}</title></circle>'


def circles(brightnesses, hues, hexcodes, height):
    return [row_to_circle(b, h, hexcode, height) for b, h, hexcode in zip(brightnesses, hues, hexcodes)]


BACKGROUND_RECTANGLES = """
    <rect width="50%" height="100%" fill="white"></rect>
    <rect x="50%" width="50%" height="100%" fill="black"></rect>
    <rect width="100%" height="100%" fill="none" stroke="#888888" stroke-width="2px"></rect>
"""
def svg_template(brightnesses, hues, hexcodes, height):
    c = circles(brightnesses, hues, hexcodes, height)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
        {BACKGROUND_RECTANGLES}
        {c}
        </svg>"""


image_sources = [
    [brightnesses, [0] * len(greys), greys, 4 * r, "grey-palette.svg"]
]


chroma_quantiles = [0, 0.333, 0.667, 1]
chroma_thresholds = df["chroma"].quantile(chroma_quantiles)
names = ['', "subtle-palette.svg", "muted-palette.svg", "loud-palette.svg"]
chroma_ranges = list(zip(
    [0] + chroma_thresholds.tolist(),
    chroma_thresholds,
    names
))[1:]

for c_min, c_max, name in chroma_ranges:
    subpalette = df[(c_min <= df["chroma"]) & (df["chroma"] <= c_max)]
    src = [subpalette['brightness'], subpalette['hue'], subpalette['hexcode'], HEIGHT, name]
    image_sources.append(src)

text = "<html><body>"
for src in image_sources:
    b, h, hexcodes, height, name = src
    svg = svg_template(b, h, hexcodes, height)
    with open(name, "w") as f:
        f.write(svg)
    text += svg
    text += "<br> <br>"

text += "</body></html>"

with open("/dev/shm/foo.html", "w") as f:
    f.write(text)
