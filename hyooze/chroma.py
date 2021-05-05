import math
SUBPIXELS = ('red','green','blue')

def max_chroma_boundary(target_lightness, conn):
    faces = [f'({c1} = 0 or {c1} = 255)' for c1 in SUBPIXELS]
    sides = []
    for face in faces:
        sides.extend(conn.execute(
            f'select greenred, blueyellow from color where {face} and (brightness between ? * 0.99 and ? * 1.01)', [target_lightness, target_lightness]
        ).fetchall())
    return sorted(sides, key=lambda gr_by: math.atan(gr_by[1] / gr_by[0]))

def chroma_area(boundary):
    area = 0
    for i in range(-1, len(boundary)-1):
        chroma_0, hue_0 = boundary[i]
        chroma_1, hue_1 = boundary[i+1]
        angle = ((hue_1 - hue_0) * math.pi / 18000) % (2 *math.pi)
        area += (chroma_0 ** 2 + chroma_1 ** 2) * angle / 4  # good enough when angle is small
    return area