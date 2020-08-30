from hyooze.cache import get_conn
from hyooze.brightness import fit_greys_between, grey_to_brightness
from hyooze.chroma import max_chroma_boundary, chroma_area
from hyooze.hue import choose_hues
from hyooze.equal_space import find_happy_neighbors
from matplotlib import pyplot
import math
import numpy
from hyooze.html import demo

def graph(brightness, hues_by_chroma, conn):
    rows = conn.execute('''select chroma, hue / 100.0, hexcode from color_view where
      (brightness between ? * 0.997 and ? * 1.003) limit 20000''', [brightness, brightness]).fetchall()
    
    xs = [chroma * math.cos(hue * math.pi / 180) for chroma, hue, _ in rows]
    ys = [chroma * math.sin(hue * math.pi / 180) for chroma, hue, _ in rows] 
    hexcodes = [hexcode for _, _, hexcode in rows]
    # grey = hues_by_chroma[0][0][1]
    # del hues_by_chroma[0]
    fig = pyplot.figure(figsize=(12, 12))
    axes = fig.add_subplot(1, 1, 1)
    # axes.set_facecolor(grey)
    # axes.set_title(grey)
    axes.set_aspect("equal")
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)
    axes.scatter(xs, ys, c=hexcodes, marker=".")
    axes.autoscale(enable=False)

    for chroma, hue_hexcode_pairs in hues_by_chroma.items():
        # circle = pyplot.Circle((0,0), radius=chroma, fill=False, edgecolor='black')
        # axes.add_artist(circle)
        xs = [chroma * math.cos(hue * math.pi / 18000) for hue, _ in hue_hexcode_pairs]
        ys = [chroma * math.sin(hue * math.pi / 18000) for hue, _ in hue_hexcode_pairs]
        axes.scatter(xs, ys, c='black', marker='o')


conn = get_conn()

# FIXME: rethink these choices
greys = ['#202020'] + fit_greys_between(7, '#202020', '#f3f3f3', conn) + ['#f3f3f3'] 

# {brightness:{chroma:[(hue, hex)]}}
color_scheme = {}

for grey in greys:
    colors_for_level = {
        # 0:[(0, grey)]
    }
    print(grey)
    brightness = grey_to_brightness(grey, conn)
    colors = conn.execute('''select chroma, hue, hexcode from color_view where
      (brightness between ? * 0.997 and ? * 1.003)''', 
        [brightness, brightness]).fetchall()

    xs = [((chroma/10000)**0.5) * math.cos(hue * math.pi / 18000) for chroma, hue, _ in colors]
    ys = [((chroma/10000)**0.5) * math.sin(hue * math.pi / 18000) for chroma, hue, _ in colors]
    xys = numpy.array([xs, ys])

    area = chroma_area(max_chroma_boundary(brightness, conn))
    indices = find_happy_neighbors(xys, 4 + int(area / 4.5e8))
    for idx in indices:
        chroma, hue, hexcode = colors[idx]
        colors_for_level[chroma] = [(hue, hexcode)]

    color_scheme[brightness] = colors_for_level

# for b, hbc in color_scheme.items(): 
#     graph(b, hbc, conn)

brightness_levels = sorted(color_scheme.keys())
all_colors = []
for b in brightness_levels: 
    chromas = sorted(color_scheme[b].keys()) 
    row = [color_scheme[b][c][0][1] for c in chromas] 
    all_colors.append(row)

with open('/dev/shm/foo.html', 'w') as f: 
    f.write(demo(all_colors)) 
