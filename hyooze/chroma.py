import math
import numpy

SUBPIXELS = ('red','green','blue')

def max_chroma_boundary(target_lightness, conn):
    faces = [f'({c1} = 0 or {c1} = 255)' for c1 in SUBPIXELS]
    sides = []
    for face in faces:
        sides.extend(conn.execute(
            f'select greenred, blueyellow from color where {face} and (lightness between ? * 0.98 and ? * 1.02)', [target_lightness, target_lightness]
        ).fetchall())
    chroma_hues = [(abs(gr + 1j * by), numpy.angle(gr + 1j * by)) for gr, by in sides]
    return sorted(chroma_hues, key=lambda c_h: c_h[1])

def chroma_area(boundary):
    area = 0
    for i in range(-1, len(boundary)-1):
        chroma_0, hue_0 = boundary[i]
        chroma_1, hue_1 = boundary[i+1]
        angle = (hue_1 - hue_0) % (2 *math.pi)
        area += (chroma_0 ** 2 + chroma_1 ** 2) * angle / 4  # good enough when angle is small
    return area