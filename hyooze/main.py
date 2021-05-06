from hyooze.cache import get_conn
from hyooze.brightness import fit_greys_between, grey_to_lightness
from hyooze.chroma import max_chroma_boundary, chroma_area
# from hyooze.hue import choose_hues
from hyooze.equal_space import select_colors
from matplotlib import pyplot
import math
import numpy
import pandas
from hyooze.display import svg_template, R

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


conn = get_conn()

greys = fit_greys_between(9, "#000000", "#f7f7f6", conn) + ["#f7f7f6"]
lightnesses = [grey_to_lightness(grey, conn) for grey in greys]
colors = []

for idx, (grey, lightness) in enumerate(zip(greys, lightnesses)):
    print(grey)

    area = chroma_area(max_chroma_boundary(lightness, conn))
    these_colors = select_colors(lightness, 4 + int(area / 1.2e8), conn)
    graph(lightness, these_colors, grey, conn)
    for greenred, blueyellow, hexcode in these_colors:
        colors.append((lightness, greenred, blueyellow, hexcode, idx / (len(greys) - 1)))

df = pandas.DataFrame(data=colors, columns=["lightness", "greenred", "blueyellow", "hexcode", "column"])
print('\n'.join([f'<button style="background: {h}; color: {h}">{h}</button>' for h in df['hexcode']]))

# FIXME: recreate svgs
# name the colors
# provide css vars or classes?

HEIGHT = 300

image_sources = [
    [
        [i / (len(greys) - 1) for i in range(len(greys))],
        [0] * len(greys),
        greys,
        4 * R,
        "grey-palette.svg"
    ]
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
    src = [subpalette['column'], subpalette['hue'], subpalette['hexcode'], HEIGHT, name]
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
