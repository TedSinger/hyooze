import math
SUBPIXELS = ('red','green','blue')

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

def _keyFn(chroma_extremes):
    def _keyFn(chroma_level):
        return sum([(chroma - chroma_level * math.floor(chroma / chroma_level))**2 for chroma in chroma_extremes])
    return _keyFn

# FIXME: what the heck is a ring?

def chroma_ring_size(chroma_extremes):
    max_chroma = max(chroma_extremes)
    candidates = [c_e / n for c_e in chroma_extremes for n in (1,2,3)]
    candidates = [c for c in candidates if 12000 < c < 20000 and max_chroma / 5 < c]
    return max(candidates, key=_keyFn(chroma_extremes))

def chroma_ring(brightness_target, chroma_target, conn):
    return conn.execute('''select chroma, hue, hexcode from color_view where
      (brightness between ? - 100 and ? + 100) and (chroma between ? - 100 and ? + 100) limit 200''', 
        [brightness_target, brightness_target, chroma_target, chroma_target]
       ).fetchall()