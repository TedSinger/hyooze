from matplotlib import pyplot
from colormath.color_objects import sRGBColor
import math
from hyooze.cache import get_conn

conn = get_conn()
SUBPIXELS = ('red','green','blue')

def grey_to_brightness(grey_hexcode, conn):
    red = int(grey_hexcode[1:3], base=16)
    green = int(grey_hexcode[3:5], base=16)
    blue = int(grey_hexcode[5:7], base=16)
    brightness = conn.execute('select brightness from color_view where red = ? and green = ? and blue = ?', [red, green, blue]).fetchone()[0]
    return brightness

def graph(grey_hexcode, limit, conn):
    brightness_target = grey_to_brightness(grey_hexcode, conn)
    chroma_extremes = chroma_extremes_for_brightness(brightness_target, conn)
    chroma_target = chroma_ring_size(chroma_extremes)
    rows = conn.execute('''select chroma, hue / 100, hexcode from color_view where
     abs(((chroma / ?) - round(chroma / ?))) < 0.03 order by abs(brightness - ?) asc limit ?''', [float(chroma_target), float(chroma_target), brightness_target, limit]).fetchall()
    xs = [chroma * math.cos(hue * math.pi / 180) for chroma, hue, _ in rows]
    ys = [chroma * math.sin(hue * math.pi / 180) for chroma, hue, _ in rows] 
    hexcodes = [hexcode for _, _, hexcode in rows]

    
    fig = pyplot.figure(figsize=(12, 12))
    axes = fig.add_subplot(1, 1, 1)
    axes.set_facecolor('black')
    axes.set_aspect("equal")
    axes.get_xaxis().set_visible(False)
    axes.get_yaxis().set_visible(False)
    axes.autoscale(enable=True)
    axes.scatter(xs, ys, c=hexcodes, marker=".")
    axes.autoscale(enable=False)

def chroma_extremes_for_brightness(target_brightness, conn):
    edges = [f'({c1} = {c1b}) and ({c2} = {c2b})' for c1 in SUBPIXELS 
        for c2 in SUBPIXELS if c1 > c2 
        for c1b in [0,255] 
        for c2b in [0,255]]
    corner_chromas = []
    for edge in edges:
        brightness, chroma, hexcode = conn.execute(f'select brightness, chroma, hexcode from color_view where {edge} order by abs(brightness - {target_brightness}) asc limit 1').fetchone()
        if abs(brightness - target_brightness) / target_brightness < 0.01:
            corner_chromas.append(chroma)

    return corner_chromas

def keyFn(chroma_extremes):
    def _keyFn(chroma_level):
        return sum([(chroma - chroma_level * math.floor(chroma / chroma_level))**2 for chroma in chroma_extremes])
    return _keyFn

def chroma_ring_size(chroma_extremes):
    max_chroma = max(chroma_extremes)
    candidates = [c_e / n for c_e in chroma_extremes for n in (1,2,3)]
    candidates = [c for c in candidates if 12000 < c < 20000 and max_chroma / 5 < c]
    return max(candidates, key=keyFn(chroma_extremes))