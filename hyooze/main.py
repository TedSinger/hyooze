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


def svg_elems(colors):
    # force to correct number of columns
    h0, h1 = (-180, 180)
    h_size = h1 - h0
    r = 20
    height = 750
    width = 1500
    # FIXME: extend by half a column in both directions
    b0, b1 = (colors['brightness'].min(), colors['brightness'].max())
    b_size = b1 - b0
    def scale_brightness(b):
        return round((width - 2*r) * ((b - b0) / b_size), 2) + r
    def scale_hue(h):
        return round((height - 2*r) * ((h - h0) / h_size), 2) + r
    def row_to_circle(row):
        (b,_,h,hexcode) = row
        return f'<circle cx="{scale_brightness(b)}" cy="{scale_hue(h)}" r="{r}" fill="{hexcode}"><title>{hexcode}</title></circle>'
    return colors.apply(row_to_circle, axis=1)


print('<html><body>')

chroma_quantiles = [0, .511, 1]
for c_idx in range(len(chroma_quantiles) - 1):
    c_min = df['chroma'].quantile(chroma_quantiles[c_idx])
    c_max = df['chroma'].quantile(chroma_quantiles[c_idx + 1])
    colors_matching_both = df[(df['chroma'] >= c_min) & (df['chroma'] <= c_max)]
    s = '\n'.join(svg_elems(colors_matching_both).tolist())
    svg = f'''<svg width="1500" height="750">
        <rect width="50%" height="100%" fill="white"></rect>
        <rect x="50%" width="50%" height="100%" fill="black"></rect>
        {s}
        </svg>'''
    print(svg)
    print()
print('</body></html>')
# FIXME: show greys, too