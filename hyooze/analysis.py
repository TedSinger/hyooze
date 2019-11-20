from hyooze.mesh import EqualBrightnessMesh, get_masks, get_attrs_by_mask, get_grey
import bisect
from matplotlib import pyplot
import numpy


class ArcDict:
    """We want to look at hue-arcs of possibilities and select colors from them.
    `ArcDict` displays a range of contiguous keys as a single arc
    This does not account for the discontinuity at 0/360
    """

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
        if not self._list:
            return "ArcDict({})"
        intervals = [[self._list[0], self._list[0]]]
        for key in self._list:
            if key > intervals[-1][1] + self._res * 2:
                intervals.append([key, key])
            else:
                intervals[-1][1] = key
        key_to_str = lambda k: f"{round(k, 1)}: {self._vals[k]}"

        strs = [
            f"[{key_to_str(low)}]"
            if low == high
            else f"[{key_to_str(low)}, {key_to_str(high)}]"
            for [low, high] in intervals
        ]
        range_text = ", ".join(strs)
        return f"ArcDict({range_text})"


def graph(target_chromas, xs, ys, colors):
    fig = pyplot.figure(figsize=(12, 12))
    axes = fig.add_subplot(1, 1, 1)
    axes.set_aspect("equal")
    for chroma in target_chromas:
        axes.plot(
            chroma * numpy.cos(numpy.arange(0, 6.28, 0.01)),
            chroma * numpy.sin(numpy.arange(0, 6.28, 0.01)),
            color="black",
        )
    axes.scatter(xs, ys, c=colors, marker=".")
    return fig


def display(office, brightness, target_chromas, resolution=1):
    mymesh = EqualBrightnessMesh.get(brightness)
    mymesh.compute(resolution)

    brightness_mask, chroma_masks = get_masks(
        mymesh.mesh, brightness, target_chromas
    )
    xs, ys, hexcodes = get_attrs_by_mask(
        mymesh.mesh, brightness_mask, ["x", "y", "hexcode"]
    )
    fig = graph(target_chromas, xs, ys, hexcodes)

    matches = {}
    for chroma, mask in chroma_masks.items():
        hues, hexcodes = get_attrs_by_mask(mymesh.mesh, mask, ["hue", "hexcode"])
        matches[chroma] = dict(zip(hues, hexcodes))

    return matches, get_grey(mymesh.mesh)

