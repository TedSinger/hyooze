def unhexcode(hexcode):
    '''
    >>> unhexcode('#304050')
    (48, 64, 80)
    '''
    red = int(hexcode[1:3], base=16)
    green = int(hexcode[3:5], base=16)
    blue = int(hexcode[5:7], base=16)
    return red, green, blue
    