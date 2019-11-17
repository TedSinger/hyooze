
def color_to_td_pair(color):
    td = '''<td style='color: {fg}; background-color: {bg}; text-rendering: optimizeLegibility; line-height:0; margin:0; font-weight: bold; font-size: x-large; font-family: monospace;'>{text}</td>'''
    return td.format(fg=color, bg='#f4f5f4', text=color) + td.format(fg="#000000", bg=color, text=color)
    
def brightness_group_to_rows(brightness):
    ret = ''
    
    nRows = max([len(chroma) for chroma in brightness])
    for i in range(nRows):
        pairs = [color_to_td_pair(chroma[i]) if i < len(chroma) else "<td style='background-color: #ffffff'/>"*2 for chroma in brightness]
        tds = ''.join(pairs)
        ret += f'''<tr>{tds}</tr>'''
    return ret

def demo(brightnesses):
    rows = list(map(brightness_group_to_rows, brightnesses))
    rows = ''.join(rows)
    return f'''<table>{rows}</table>'''

LIME_ON_BLUE = f'''<text style='font-weight: bold; color: HSL(120, 100%, 50%); background-color: HSL(240, 100%, 50%);'>
Lime (#00FF00, HSL(120, 100%, 50%)) on Blue (#0000FF, HSL(240, 100%, 50%))<br>
is quite readable, even though the HSL lightness is the same.</text>'''