from matplotlib import pyplot
from colormath.color_objects import sRGBColor
import math
from hyooze.cache import get_conn
from minizinc import Instance, Model, Solver

conn = get_conn()
SUBPIXELS = ('red','green','blue')

def unhexcode(hexcode):
    red = int(hexcode[1:3], base=16)
    green = int(hexcode[3:5], base=16)
    blue = int(hexcode[5:7], base=16)
    return red, green, blue
    

def relative_luminance(r,g,b):
    # https://www.w3.org/WAI/GL/wiki/Relative_luminance
    RsRGB = r/255
    GsRGB = g/255
    BsRGB = b/255
    if RsRGB <= 0.03928:
        R = RsRGB/12.92
    else:
        R = ((RsRGB+0.055)/1.055) ** 2.4
    if GsRGB <= 0.03928:
        G = GsRGB/12.92
    else:
        G = ((GsRGB+0.055)/1.055) ** 2.4
    if BsRGB <= 0.03928:
        B = BsRGB/12.92
    else:
        B = ((BsRGB+0.055)/1.055) ** 2.4
    rl = 0.2126 * R + 0.7152 * G + 0.0722 * B
    # this 0.05 fudge factor is always present when computing contrast ratio. it's not part of the color's luminance, but it's easy for my math to pretend that it is
    return rl + 0.05

def get_greys(conn):
    return conn.execute('select red, green, blue, hexcode from color_view where max(red, green, blue) - min(red,green,blue) <= 1').fetchall()

def fit_greys_between(n, low, high, conn):
    low_rl = relative_luminance(*unhexcode(low))
    high_rl = relative_luminance(*unhexcode(high))
    total_ratio = high_rl / low_rl
    level_ratio = total_ratio ** (1/(n+1))
    target_rls = [level_ratio**i * low_rl for i in range(1,n+1)]
    greys = get_greys(conn)
    grey_rls = [(relative_luminance(r,g,b), r,g,b, hexcode) for (r,g,b, hexcode) in greys]
    ret = []
    for t in target_rls:
        ret.append(min(grey_rls, key=lambda grey: abs(grey[0] - t))[-1])

    return ret

def grey_to_brightness(grey_hexcode, conn):
    red,green,blue = unhexcode(grey_hexcode)
    brightness = conn.execute('select brightness from color_view where red = ? and green = ? and blue = ?', [red, green, blue]).fetchone()[0]
    return brightness

def chroma_ring(brightness_target, chroma_target, conn):
    return conn.execute('''select chroma, hue / 100, hexcode from color_view where
      (brightness between ? - 100 and ? + 100) and (chroma between ? - 100 and ? + 100)''', 
        [brightness_target, brightness_target, chroma_target, chroma_target]
       ).fetchall()

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


def fit_hues(arc, n):
    if n == 1 or len(arc) == 1:
        return [arc[0]], 0
    else:
        gecode = Solver.lookup('gecode')
        m = Model('hue_fitting.mzn')
        i = Instance(gecode, m)
        i["nHues"] = n
        i["available_hue"] = set(arc)
        result = i.solve()
        return result.solution.hues, result.solution.objective
        


def choose_hues(arc, min_hue_diff):
    n = 2
    hues, hue_diff = fit_hues(arc, n)
    if hue_diff < min_hue_diff:
        return fit_hues(arc, 1)[0]
    else:
        new_hues, new_diff = hues, hue_diff
        while new_diff > min_hue_diff:
            hues, hue_diff = new_hues, new_diff
            n += 1
            new_hues, new_diff = fit_hues(arc, n)
        return hues
