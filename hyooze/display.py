import math
h0, h1 = (-math.pi, math.pi)
h_size = h1 - h0
R = 10
width = 400


def scale_width(column):
    return round((width - 4 * R) * column, 2) + 2 * R


def scale_hue(hue, height):
    return round((height - 4 * R) * ((hue - h0) / h_size), 2) + 2 * R


def row_to_circle(color, height):
    cx = scale_width(color.column_index)
    cy = scale_hue(color.hue_radians, height)
    return f'''<circle cx="{cx}" 
        cy="{cy}" r="{R}" fill="{color.hexcode}" stroke="{'black' if color.column_index > 0.5 else 'white'}"
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
    <svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
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

def subpalettes(colors):
    colors = sorted(colors, key=lambda color: color.chroma)
    n = round(len(colors) / 3)
    return [
        ("pastel", colors[:n]),
        ("muted", colors[n:2*n]),
        ("vivid", colors[2*n:]),
    ]

def write_svgs(colors, greys):
    with open('grey-palette.svg', 'w') as f:
        f.write(colors_to_svg(greys, 4 * R, "greys"))
    for (title, subp) in subpalettes(colors):
        with open(f'{title}-palette.svg', 'w') as f:
            f.write(colors_to_svg(subp, 300, title))