import math
h0, h1 = (-math.pi, math.pi)
h_size = h1 - h0
R = 10
WIDTH = 800
# FIXME: create a ColorDisplayGraph object with the full collection of colors
# some of these magic constants become derived numbers
MIN_CHROMA = 6512
MAX_CHROMA = 36906
MID_CHROMA = (MIN_CHROMA + MAX_CHROMA) / 2
CHROMA_SPREAD = MAX_CHROMA - MIN_CHROMA
N_COLUMNS = 10
COLUMN_WIDTH = WIDTH / N_COLUMNS
HEIGHT = 400

def scale_width(column, chroma):
    if chroma < MIN_CHROMA: # center greys, even though they have zero chroma
        offset = 0
    else:
        offset = (COLUMN_WIDTH - 2 * R) * (chroma - MID_CHROMA) / CHROMA_SPREAD
    column_center = COLUMN_WIDTH * (column + 1/2)
    return round(column_center + offset, 2)


def scale_hue(hue, height):
    return round((height - 4 * R) * ((hue - h0) / h_size), 2) + 2 * R


def row_to_circle(color, height):
    cx = scale_width(color.column_index, color.chroma)
    cy = scale_hue(color.hue_radians, height)
    return f'''<circle cx="{cx}" 
        cy="{cy}" r="{R}" fill="{color.hexcode}" 
        stroke="{'black' if color.column_index > 0.5 else 'white'}"
        style="transform-origin: {int(cx)}px {int(cy)}px">
        <title>{color.hexcode}</title>
        </circle>'''


def colors_to_svg(colors, height, title):
    circles = '\n'.join([row_to_circle(color, height) for color in colors])
    js = '''<script type="text/javascript"><![CDATA[
        function clippify(event) {
            elem = event.target;
            text = elem.childNodes[1].textContent;
            navigator.clipboard.writeText(text);
            console.log(text);
        }
        var circles = document.getElementsByTagName('circle');
        for (i = 0; i < circles.length; i++) {
            circle = circles[i];
            circle.onclick = clippify;
        }
    ]]></script>'''

    return f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}">
    <style type="text/css">
    circle:hover {'{transform: scaleX(2.5);}'}
    </style>
    <g>
        <rect width="50%" height="100%" fill="white"><title>{title}</title></rect>
        <rect x="50%" width="50%" height="100%" fill="black"><title>{title}</title></rect>
        <rect width="100%" height="100%" fill="none" stroke="#888888" stroke-width="2px"></rect>
    {circles}
    </g>
    {js}
    </svg>"""


def write_svgs(colors, greys):
    with open('grey-palette.svg', 'w') as f:
        f.write(colors_to_svg(greys, 4 * R, "greys"))
    with open('color-palette.svg', 'w') as f:
        f.write(colors_to_svg(colors, HEIGHT, "colors"))