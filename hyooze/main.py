from hyooze.cache import get_conn
from hyooze.brightness import fit_greys_between, grey_to_brightness
from hyooze.chroma import chroma_extremes_for_brightness, chroma_ring_size, chroma_ring
from hyooze.hue import choose_hues
from matplotlib import pyplot
import math

def graph(brightness, hues_by_chroma, conn):
    rows = conn.execute('''select chroma, hue / 100.0, hexcode from color_view where
      (brightness between ? * 0.99 and ? * 1.01) limit 20000''', [brightness, brightness]).fetchall()
    
    xs = [chroma * math.cos(hue * math.pi / 180) for chroma, hue, _ in rows]
    ys = [chroma * math.sin(hue * math.pi / 180) for chroma, hue, _ in rows] 
    hexcodes = [hexcode for _, _, hexcode in rows]
    grey = hues_by_chroma[0][0][1]
    fig = pyplot.figure(figsize=(12, 12))
    axes = fig.add_subplot(1, 1, 1)
    axes.set_facecolor(grey)
    axes.set_title(grey)
    axes.set_aspect("equal")
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)
    axes.scatter(xs, ys, c=hexcodes, marker=".")
    axes.autoscale(enable=False)

    for chroma, hue_hexcode_pairs in hues_by_chroma.items():
        circle = pyplot.Circle((0,0), radius=chroma, fill=False, edgecolor='black')
        axes.add_artist(circle)
        xs = [chroma * math.cos(hue * math.pi / 18000) for hue, _ in hue_hexcode_pairs]
        ys = [chroma * math.sin(hue * math.pi / 18000) for hue, _ in hue_hexcode_pairs]
        axes.scatter(xs, ys, c='black', marker='o')


conn = get_conn()

# FIXME: rethink these choices
greys = ['#202020'] + fit_greys_between(7, '#202020', '#f3f3f3', conn) + ['#f3f3f3'] 

# FIXME: question mark?
MIN_CHROMA_TIMES_HUE_DIFF = 3000000 * 360 / 8

# {brightness:{chroma:[(hue, hex)]}}
color_scheme = {}

for grey in greys:
    colors_for_level = {0:[(0, grey)]}
    print(grey)
    brightness = grey_to_brightness(grey, conn)
    chroma_extremes = chroma_extremes_for_brightness(brightness, conn)
    ring_size = chroma_ring_size(chroma_extremes)
    
    for chroma_target in range(int(ring_size), max(chroma_extremes) + 1, int(ring_size)):
        ring_colors = chroma_ring(brightness, chroma_target, conn)
        hexcodes_by_hue = dict((h, hexcode) for _, h, hexcode in ring_colors)
        chosen_hues = choose_hues(list(hexcodes_by_hue.keys()), MIN_CHROMA_TIMES_HUE_DIFF / (chroma_target + 1))
        
        colors_for_level[chroma_target] = [(h, hexcodes_by_hue[h]) for h in chosen_hues]
    color_scheme[brightness] =  colors_for_level

for b, hbc in color_scheme.items(): 
    graph(b, hbc, conn)