from hyooze import mesh
import bisect
from matplotlib import pyplot


class ArcDict:
    """We want to look at hue-arcs of possibilities, rather than individual colors"""
    def __init__(self, vals, resolution):
        self._res = resolution
        self._vals = vals
        self._list = sorted(vals.keys())
    
    def __getitem__(self, needle):
        insertion_point = bisect.bisect(self._list, needle)
        
        if not self._list:
            raise KeyError(needle)
        elif insertion_point == 0:
            candidates = [self._list[0]]
        elif insertion_point == len(self._list):
            candidates = [self._list[-1]]
        else:
            candidates = [self._list[insertion_point - 1], self._list[insertion_point]]

        best_key = min(candidates, key=lambda key: abs(needle - key))
        if abs(needle - best_key) > self._res:
            raise KeyError(needle)
        else:
            return self._vals[best_key]
    
    def __repr__(self):
        intervals = [[self._list[0], self._list[0]]]
        for key in self._list:
            if key > intervals[-1][1] + self._res * 2:
                intervals.append([key, key])
            else:
                intervals[-1][1] = key
        key_to_str = lambda k: f'{round(k, 1)}: {self._vals[k]}'
        
        strs = [f'[{key_to_str(low)}]' if low == high else f'[{key_to_str(low)}, {key_to_str(high)}]' for [low, high] in intervals]
        range_text = ', '.join(strs)
        return f'ArcDict({range_text})'


def ciecam02_brightness_planes(office, brightnesses, target_chromas):
    matches = {}
    fig = pyplot.figure(figsize=(12,12))
    for i, brightness in enumerate(brightnesses):
        mymesh = mesh.EqualBrightnessMesh.get(brightness)
        mymesh.compute()
        axes = fig.add_subplot((len(brightnesses)+1//2), 2, i+1)
        axes.set_aspect('equal')
        brightness_mask, chroma_masks = mesh.get_masks(mymesh.mesh, brightness, target_chromas)
        xs, ys, hexcodes = mesh.get_colors_by_mask(mymesh.mesh, brightness_mask, ['x', 'y', 'hexcode'])
        mesh.display(axes, target_chromas, xs, ys, hexcodes)
        matches[brightness] = dict([(chroma, mesh.get_colors_by_mask(mymesh.mesh, mask, ['hue', 'hexcode'])) for chroma, mask in chroma_masks.items()])
    
    return matches, fig
    