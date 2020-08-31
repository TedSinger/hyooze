from hyooze.cache import get_conn
from hyooze.brightness import fit_greys_between, grey_to_brightness
from hyooze.chroma import max_chroma_boundary, chroma_area
from hyooze.hue import choose_hues
from hyooze.equal_space import select_colors
from matplotlib import pyplot
import math
import numpy
from hyooze.html import demo
import pandas

conn = get_conn()

greys = fit_greys_between(9, '#000000', '#f7f7f6', conn) + ['#f7f7f6']

colors = []

for grey in greys:
    print(grey)
    brightness = grey_to_brightness(grey, conn)

    area = chroma_area(max_chroma_boundary(brightness, conn))
    these_colors = select_colors(brightness, 4 + int(area / 4.5e8), conn)
    for chroma, hue, hexcode in these_colors:
        colors.append((brightness, chroma, hue, hexcode))

df = pandas.DataFrame(data=colors, columns=["brightness", "chroma", "hue","hexcode"])

# brightness_thresholds = [0, grey_to_brightness(greys[5], conn), grey_to_brightness(greys[-1], conn)]
# chroma_quantiles = [0, .1, .5, 1]  # want to separate out the greys

brighter = df[df['brightness'] >= grey_to_brightness(greys[5], conn)]
brighter_louder = brighter[brighter['chroma'] >= brighter['chroma'].median()]
brighter_muted = brighter[brighter['chroma'] < brighter['chroma'].median()]
darker = df[df['brightness'] < grey_to_brightness(greys[5], conn)]
darker_louder = darker[darker['chroma'] >= darker['chroma'].median()]
darker_muted = darker[darker['chroma'] < darker['chroma'].median()]


fig = pyplot.figure(figsize=(12, 12))

axes = fig.add_subplot(2, 2, 1)
axes.get_xaxis().set_visible(False)
axes.get_yaxis().set_visible(False)
axes.set_facecolor('white')
axes.scatter(
    darker_louder['brightness'],
    darker_louder['hue'],
    c=darker_louder['hexcode'],
    marker="o"
)
axes = fig.add_subplot(2, 2, 2)
axes.get_xaxis().set_visible(False)
axes.get_yaxis().set_visible(False)
axes.set_facecolor('black')
axes.scatter(
    brighter_louder['brightness'],
    brighter_louder['hue'],
    c=brighter_louder['hexcode'],
    marker="o"
)
axes = fig.add_subplot(2, 2, 3)
axes.get_xaxis().set_visible(False)
axes.get_yaxis().set_visible(False)
axes.set_facecolor('white')
axes.scatter(
    darker_muted['brightness'],
    darker_muted['hue'],
    c=darker_muted['hexcode'],
    marker="o"
)
axes = fig.add_subplot(2, 2, 4)
axes.get_xaxis().set_visible(False)
axes.get_yaxis().set_visible(False)
axes.set_facecolor('black')
axes.scatter(
    brighter_muted['brightness'],
    brighter_muted['hue'],
    c=brighter_muted['hexcode'],
    marker="o"
)