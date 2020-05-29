''' desiderata
consistent brightness levels: any two colors N bands apart have the same contrast ratio = (rel lum A + 0.5) / (rel lum B + 0.5). target a ratio per band of 21**(1/size(bands))
    no, this is wrong. i don't need the contrast ratio of 2a on 00 or ff on d6 to be predictable. better to lump the top/bottom grey levels in with black/white, and measure contrast from those
    grey:
    000000
    101010
    ??????
    f5f4f4
    ffffff
As many different high-chroma colors as possible


tricky problems:
    choose brightness levels - i think this can be manual
    choose chroma levels
        i can get all corners (where two of rgb are in {0,255})
        for each of those chroma levels and each / 2 and each / 3
        that is between 12k and 20k
        that is at least 1/5 of the max chroma level
        compute sum([(chroma - level * floor(chroma / level))**2 for chroma in corners])
        
    choose number of colors per brightness/chroma level
        # target 1 per 3.3k chroma?
    place colors in brightness/chroma levels
'''
