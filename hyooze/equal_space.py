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
    this_field = field_for_neighbor(neighbor, xys)
    rest_of_field = numpy.subtract(whole_field, this_field, out=this_field)
    best_neighbor = numpy.argmin(rest_of_field)
    return best_neighbor

def minimum_energy_placement(xys, n, baseline_energy):
    '''
    >>> xys = numpy.array([[0.1, 0, 1], [0, 0, 1]])
    >>> set(minimum_energy_placement(xys, 2))
    {1, 2}
    >>> set(minimum_energy_placement(xys, 3))
    {0, 1, 2}
    '''
    current = list(range(n))
    whole_field = numpy.sum([field_for_neighbor(neighbor, xys) for neighbor in current], axis=0)
    whole_field += baseline_energy
    updated = True
    while updated:
        updated = False
        for idx, neighbor in enumerate(current):
            replacement = best_replacment(neighbor, xys, whole_field)
            if replacement != neighbor:
                current[idx] = replacement
                whole_field = numpy.subtract(whole_field, field_for_neighbor(neighbor, xys), out=whole_field)
                whole_field = numpy.add(whole_field, field_for_neighbor(replacement, xys), out=whole_field)
                updated = True
    return current

def select_colors(lightness, n, conn):
    colors = conn.execute('''select greenred, blueyellow, hexcode from color where
      (lightness between ? * 0.997 and ? * 1.003)''',
        [lightness, lightness]).fetchall()
    grey_idx = min(range(len(colors)), key=lambda i: colors[i][0])
    xys = list(zip(*colors))[:2]
    indices = minimum_energy_placement(xys, n, field_for_neighbor(grey_idx, xys) * n/3.)
    return [colors[idx] for idx in indices]