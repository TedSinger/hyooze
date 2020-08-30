import math
SUBPIXELS = ('red','green','blue')

def max_chroma_boundary(target_brightness, conn):
    faces = [f'({c1} = 0 or {c1} = 255)' for c1 in SUBPIXELS]
    sides = []
    for face in faces:
        sides.extend(conn.execute(
            f'select chroma, hue from color_view where {face} and (brightness between ? * 0.99 and ? * 1.01)', [target_brightness, target_brightness]
        ).fetchall())
    return sorted(sides, key=lambda chroma_hue: chroma_hue[1])

def chroma_area(boundary):
    area = 0
    for i in range(-1, len(boundary)-1):
        chroma_0, hue_0 = boundary[i]
        chroma_1, hue_1 = boundary[i+1]
        angle = ((hue_1 - hue_0) * math.pi / 18000) % (2 *math.pi)
        area += (chroma_0 ** 2 + chroma_1 ** 2) * angle / 4  # good enough when angle is small
    return area