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
brightnesses = [grey_to_brightness(grey, conn) for grey in greys]
colors = []

for grey, brightness in zip(greys, brightnesses):
    print(grey)

    area = chroma_area(max_chroma_boundary(brightness, conn))
    these_colors = select_colors(brightness, 4 + int(area / 4.5e8), conn)
    for chroma, hue, hexcode in these_colors:
        colors.append((brightness, chroma, hue, hexcode))

df = pandas.DataFrame(data=colors, columns=["brightness", "chroma", "hue","hexcode"])

h0, h1 = (-180, 180)
h_size = h1 - h0
r = 10
height = 300
width = 400

def svg_elems(colors):
    def scale_brightness(b):
        index = min(range(len(greys)), key=lambda i: abs(brightnesses[i]-b))
        return round((width - 4*r) * index/(len(greys) - 1), 2) + 2*r
    def scale_hue(h):
        return round((height - 4*r) * ((h - h0) / h_size), 2) + 2*r
    def row_to_circle(row):
        (b,_,h,hexcode) = row
        return f'<circle cx="{scale_brightness(b)}" cy="{scale_hue(h)}" r="{r}" fill="{hexcode}"><title>{hexcode}</title></circle>'
    return colors.apply(row_to_circle, axis=1)

def grey_circles(greys):
    ret = ''
    for i, hexcode in enumerate(greys):
        ret += f'<circle cx="{round((width - 4*r) * i/(len(greys) - 1), 2) + 2*r}" cy="{2*r}" r="{r}" fill="{hexcode}"><title>{hexcode}</title></circle>'
    return ret

text = '<html><body>'
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{4*r}">
        <rect width="50%" height="100%" fill="white"></rect>
        <rect x="50%" width="50%" height="100%" fill="black"></rect>
        <rect width="100%" height="100%" fill="none" stroke="#888888" stroke-width="1px"></rect>
        {grey_circles(greys)}
        </svg>'''
text += svg
with open('grey-palette.svg', 'w') as f:
    f.write(svg)
chroma_quantiles = [0, .333, .667, 1]
names = ['subtle-palette.svg', 'muted-palette.svg', 'loud-palette.svg']
for c_idx in range(len(chroma_quantiles) - 1):
    c_min = df['chroma'].quantile(chroma_quantiles[c_idx])
    c_max = df['chroma'].quantile(chroma_quantiles[c_idx + 1])
    colors_matching_both = df[(df['chroma'] >= c_min) & (df['chroma'] <= c_max)]
    s = '\n'.join(svg_elems(colors_matching_both).tolist())
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
        <rect width="50%" height="100%" fill="white"></rect>
        <rect x="50%" width="50%" height="100%" fill="black"></rect>
        <rect width="100%" height="100%" fill="none" stroke="#888888" stroke-width="1px"></rect>
        {s}
        </svg>'''
    with open(names[c_idx], 'w') as f:
        f.write(svg)
    text += '<br> <br>'
    text += svg

text += '</body></html>'
# FIXME: show greys, too
with open('/dev/shm/foo.html', 'w') as f:
    f.write(text)