from hyooze.junk import unhexcode

def relative_luminance(r,g,b):
    '''
    >>> relative_luminance(184,121,202)
    0.3312935947378259
    '''
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
    q = '''select red, green, blue, hexcode from color
        where max(red, green, blue) - min(red,green,blue) <= 1'''
    return conn.execute(q).fetchall()

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

def grey_to_lightness(grey_hexcode, conn):
    red,green,blue = unhexcode(grey_hexcode)
    lightness = conn.execute('select lightness from color where red = ? and green = ? and blue = ?', [red, green, blue]).fetchone()[0]
    return lightness