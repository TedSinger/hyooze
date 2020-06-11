from matplotlib import pyplot
import math
from hyooze.cache import get_conn
from hyooze.brightness import fit_greys_between, grey_to_brightness
from hyooze.chroma import chroma_extremes_for_brightness, chroma_ring_size, chroma_ring
from hyooze.hue import choose_hues
conn = get_conn()

def graph(grey_hexcode, conn):
    brightness_target = grey_to_brightness(grey_hexcode, conn)
    chroma_extremes = chroma_extremes_for_brightness(brightness_target, conn)
    size = chroma_ring_size(chroma_extremes)
    rows = []
    for chroma_target in range(0, max(chroma_extremes) + 1, int(size)):
        ring = chroma_ring(brightness_target, chroma_target, conn)
        print(len(ring))
        rows.extend(ring)
    
    xs = [chroma * math.cos(hue * math.pi / 180) for chroma, hue, _ in rows]
    ys = [chroma * math.sin(hue * math.pi / 180) for chroma, hue, _ in rows] 
    hexcodes = [hexcode for _, _, hexcode in rows]

    fig = pyplot.figure(figsize=(12, 12))
    axes = fig.add_subplot(1, 1, 1)
    axes.set_facecolor('white')
    axes.set_aspect("equal")
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)
    axes.autoscale(enable=True)
    axes.scatter(xs, ys, c=hexcodes, marker=".")
    axes.autoscale(enable=False)
