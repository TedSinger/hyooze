from hyooze.cache import get_conn
from hyooze.brightness import fit_greys_between, grey_to_brightness
from hyooze.chroma import chroma_extremes_for_brightness, chroma_ring_size, chroma_ring
from hyooze.hue import choose_hues

conn = get_conn()

# FIXME: rethink these choices
greys =  ['#202020'] + fit_greys_between(7, '#202020', '#f3f3f3', conn) + ['#f3f3f3'] 

# FIXME: question mark?
MIN_CHROMA_TIMES_HUE_DIFF = 5000000 * 360 / 8

# FIXME: wrong data structure
color_scheme = []

for grey in greys:
    print(grey)
    brightness = grey_to_brightness(grey, conn)
    chroma_extremes = chroma_extremes_for_brightness(brightness, conn)
    ring_size = chroma_ring_size(chroma_extremes)
    color_scheme.append([grey])
    for chroma_target in range(int(ring_size), max(chroma_extremes) + 1, int(ring_size)):
        print(chroma_target)
        ring_colors = chroma_ring(brightness, chroma_target, conn)
        hues = [h for _, h, _ in ring_colors]
        chosen_hues = choose_hues(hues, MIN_CHROMA_TIMES_HUE_DIFF / (chroma_target + 1))
        print(chosen_hues)
        # FIXME: this is not a hashmap
        chosen_colors = [hexcode for _, h, hexcode in ring_colors if h in chosen_hues]
        color_scheme.append(chosen_colors)
