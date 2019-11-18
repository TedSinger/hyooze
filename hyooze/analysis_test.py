from hyooze.analysis import ArcDict
import random


def test_arcdict_repr():
    a = ArcDict({}, 0)
    str(a)  # should not raise an error
    b = ArcDict({1: 2}, 0)
    assert "1" in str(b) and "2" in str(b)
    c = ArcDict({1: 2, 3: 4}, 0)
    assert str(c).count("[") == 2, "This ArcDict should have two arcs"
    d = ArcDict({1: 2, 3: 4}, 0.99)
    assert str(d).count("[") == 2, "This ArcDict should have two arcs"
    e = ArcDict({1: 2, 3: 4}, 1)
    assert str(e).count("[") == 1, "This ArcDict should have one arc"
    f = ArcDict({1: 2, 2: 9, 3: 4}, 0.99)
    assert str(f).count("[") == 1, "This ArcDict should have one arc"


def test_arcdict_1():
    f = ArcDict({1: 2, 2: 9, 3: 4}, 0.99)
    assert f[1] == 2
    assert f[0.01] == 2, "This is just close enough"
    assert f[1.499999] == 2, "Should take the closest point"
    assert f[1.5] in [2, 9], "I don't care how rounding is handled, but it should be one of these"
    assert f[1.500001] == 9, "Should take the closest point"
    success = False
    try:
        f[0]
        success = True
    except KeyError:
        pass
    assert not success, "This should be too far from the nearest point"


def test_arcdict_2():
    scale = random.random()
    vals = {}
    key = 0
    for i in range(100):
        key += scale + random.random() * 0.25
        vals[key] = key
    a = ArcDict(vals, scale * 0.5 + 0.12)
    for key in vals:
        assert a[key + scale * 0.4999] == key
        assert a[key - scale * 0.4999] == key
