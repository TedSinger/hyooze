import numpy
import math

def field_for_neighbor(neighbor, xys):
    square_diffs = numpy.zeros_like(xys)
    numpy.subtract(xys, numpy.array([xys[:,neighbor]]).T, out=square_diffs)
    numpy.multiply(square_diffs, square_diffs, out=square_diffs)
    field = numpy.sum(square_diffs, axis=0)
    numpy.power(field, 2, out=field)
    numpy.add(field, 0.0001, out=field)
    numpy.divide(1, field, out=field)
    return field

def best_replacment(neighbor, xys, whole_field):
    this_field = field_for_neighbor(neighbor, xys) # should pass this in instead of recomputing it. or cache? tried a cache but it was buggy
    rest_of_field = numpy.subtract(whole_field, this_field, out=this_field)
    best_neighbor = numpy.argmin(rest_of_field)
    return best_neighbor

def minimum_energy_placement(xys, n):
    '''
    >>> xys = array([[0.1, 0, 1], [0, 0, 1]])
    >>> set(find_happy_neighbors(xys, 2))
    {1, 2}
    >>> set(find_happy_neighbors(xys, 3))
    {0, 1, 2}
    '''
    current = list(range(n))
    whole_field = numpy.sum([field_for_neighbor(neighbor, xys) for neighbor in current], axis=0)
    updated = True
    while updated:
        updated = False
        # would like to prioritize indices that have recently changed
        for idx, neighbor in enumerate(current):
            replacement = best_replacment(neighbor, xys, whole_field)
            if replacement != neighbor:
                current[idx] = replacement
                whole_field = numpy.subtract(whole_field, field_for_neighbor(neighbor, xys), out=whole_field)
                whole_field = numpy.add(whole_field, field_for_neighbor(replacement, xys), out=whole_field)
                updated = True
    return current

def select_colors(brightness, n, conn):
    colors = conn.execute('''select chroma, hue, hexcode from color_view where
      (brightness between ? * 0.997 and ? * 1.003)''', 
        [brightness, brightness]).fetchall()

    xs = [((chroma/10000)**0.5) * math.cos(hue * math.pi / 18000) for chroma, hue, _ in colors]
    ys = [((chroma/10000)**0.5) * math.sin(hue * math.pi / 18000) for chroma, hue, _ in colors]
    xys = numpy.array([xs, ys])
    indices = minimum_energy_placement(xys, n)
    return [colors[idx] for idx in indices]