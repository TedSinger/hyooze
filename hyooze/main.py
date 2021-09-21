from hyooze.cache import get_conn
from hyooze.brightness import fit_greys_between, grey_to_lightness
from hyooze.chroma import max_chroma_boundary, chroma_area
# from hyooze.hue import choose_hues
from hyooze.equal_space import select_colors
from matplotlib import pyplot
import math
import numpy
import pandas
from hyooze.display import write_svgs
from dataclasses import dataclass

def graph(lightness, selected, grey, conn):
    rows = conn.execute('''select greenred, blueyellow, hexcode from color where
      (lightness between ? * 0.997 and ? * 1.003) limit 20000''', [lightness, lightness]).fetchall()

    xs, ys, _ = zip(*rows)
    hexcodes = [hexcode for _, _, hexcode in rows]
    fig = pyplot.figure(figsize=(12, 12))
    axes = fig.add_subplot(1, 1, 1)
    axes.set_facecolor(grey)
    axes.set_title(grey)
    axes.set_aspect("equal")
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)
    axes.scatter(xs, ys, c=hexcodes, marker=".")
    axes.autoscale(enable=False)
    if selected:
        xs, ys, _ = zip(*(selected + [(0,0,grey)]))
        axes.scatter(xs, ys, c='black', marker='o')


@dataclass
class DisplayColor:
    lightness: float
    greenred: float
    blueyellow: float
    hexcode: str
    column_index: float
    @property
    def chroma(self):
        # FIXME: cache these
        return (self.greenred**2 + self.blueyellow**2)**0.5
    @property
    def hue_radians(self):
        return numpy.angle(self.greenred + 1j * self.blueyellow)

conn = get_conn()

grey_hexcodes = fit_greys_between(9, "#000000", "#f9f9f9", conn) + ["#f9f9f9"]
lightnesses = [grey_to_lightness(grey, conn) for grey in grey_hexcodes]
colors = []
greys = []
for idx, (grey, lightness) in enumerate(zip(grey_hexcodes, lightnesses)):
    print(grey)

    area = chroma_area(max_chroma_boundary(lightness, conn))
    these_colors = select_colors(lightness, 4 + int(area / 1.2e8), conn)
    # graph(lightness, these_colors, grey, conn)
    for greenred, blueyellow, hexcode in these_colors:
        colors.append(DisplayColor(lightness, greenred, blueyellow, hexcode, idx))
    greys.append(DisplayColor(lightness, 0, 0, grey, idx))

write_svgs(colors, greys)
# FIXME:
# advertise clickiness
# include html table
# include text demo
# rotate the svg to rows?