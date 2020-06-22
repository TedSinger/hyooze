from minizinc import Instance, Model, Solver
import os

def _fit_hues(arc, n):
    if n == 1 or len(arc) == 1:
        return [arc[0]], 0
    else:
        gecode = Solver.lookup('gecode')
        mzn_path = os.path.join(os.path.dirname(__file__), 'hue_fitting.mzn')
        m = Model(mzn_path)
        i = Instance(gecode, m)
        i["nHues"] = n
        i["available_hue"] = set(arc)
        result = i.solve()
        return result.solution.hues, result.solution.objective
        
def choose_hues(arc, min_hue_diff):
    n = 2
    hues, hue_diff = _fit_hues(arc, n)
    if hue_diff < min_hue_diff:
        return _fit_hues(arc, 1)[0]
    else:
        new_hues, new_diff = hues, hue_diff
        while new_diff > min_hue_diff:
            hues, hue_diff = new_hues, new_diff
            n += 1
            new_hues, new_diff = _fit_hues(arc, n)
        return hues
