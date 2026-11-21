"""Linear-programming fit for the cadence drill's balanced weights (0.49 C31, C33). Used by tests/gen_cad1_weights.py (rung 1, EAR1W)
and tests/gen_cad23_weights.py (rungs 2 and 3, EAR23W). Needs numpy and scipy (HiGHS); the suites themselves do not.

A tell is measured exactly from the weights: with every answer equally likely, the best guess of the answer from a feature alone is right
  sum over the feature's values x of  max over answers a of P(x | a)  /  (number of answers),
and chance is 1 / (number of answers). The tell is that minus chance, in points. It is the limit of the suites' held-out best-guess
measure as the number of items grows, so it is never below what a suite measures on average.

The weights w (one per pool entry) are found in stages, each a linear programme:
  1. caps:  every capped feature's tell <= its floor + cap;
  2. objective: the weighted sum of the listed features' excess over their floors is made as small as it can be;
  3. spread: with every feature held at the stage-2 level (+ slack), the weights are moved as little as possible (L1) from an anchor
     (the old fitted weights), so the voicings keep their variety and only what has to move moves.
A fixed share `mix` of the plain draw (each model's share spread evenly over its voicings) is part of every weight, so every strict
voicing stays in use; the tells are measured with it included.
"""
import collections
import numpy as np
import scipy.sparse as sp
from scipy.optimize import linprog


def plain(P, share):
    """the plain draw: each (answer, model) gets its share, spread evenly over its entries"""
    cnt = collections.Counter((p['a'], p['t']) for p in P)
    return np.array([share[(p['a'], p['t'])] / cnt[(p['a'], p['t'])] for p in P])


def _lp(P, answers, F, share, caps, objw, mix, anchor=None):
    n = len(P)
    u = plain(P, share)
    names = [k for k in F if k in caps or k in objw]
    mv, fv = {}, {}
    for k in names:
        f, R, fl = F[k]
        fv[k] = [f(p) if p['a'] in R else None for p in P]
        for v in set(x for x in fv[k] if x is not None):
            mv[(k, v)] = len(mv)
    sl = [k for k in names if k in objw]
    nm, ns, nd = len(mv), len(sl), (n if anchor is not None else 0)
    M0, S0, D0 = n, n + nm, n + nm + ns
    N = n + nm + ns + nd
    rows, cols, vals, b = [], [], [], []
    r = 0
    for k in names:
        f, R, fl = F[k]
        g = collections.defaultdict(list)
        for i in range(n):
            if fv[k][i] is not None:
                g[(P[i]['a'], fv[k][i])].append(i)
        for (a, v), ii in g.items():
            rows += [r] * len(ii); cols += ii; vals += [1 - mix] * len(ii)
            rows.append(r); cols.append(M0 + mv[(k, v)]); vals.append(-1); b.append(-mix * u[ii].sum()); r += 1
        for (k2, v), j in mv.items():
            if k2 == k:
                rows.append(r); cols.append(M0 + j); vals.append(1)
        nA = len(R)
        if k in sl:
            rows.append(r); cols.append(S0 + sl.index(k)); vals.append(-nA / 100); b.append(1 + nA * fl / 100)
        else:
            b.append(1 + nA * (caps[k] + fl) / 100)
        r += 1
    if anchor is not None:
        for i in range(n):
            rows += [r, r]; cols += [i, D0 + i]; vals += [1, -1]; b.append(anchor[i]); r += 1
            rows += [r, r]; cols += [i, D0 + i]; vals += [-1, -1]; b.append(-anchor[i]); r += 1
    Aub = sp.csr_matrix((vals, (rows, cols)), shape=(r, N))
    er, ec, ev, beq = [], [], [], []
    for j, ((a, t), s) in enumerate(sorted(share.items())):
        ii = [i for i, p in enumerate(P) if p['a'] == a and p['t'] == t]
        er += [j] * len(ii); ec += ii; ev += [1] * len(ii); beq.append(s)
    Aeq = sp.csr_matrix((ev, (er, ec)), shape=(len(beq), N))
    c = np.zeros(N)
    for j, k in enumerate(sl):
        c[S0 + j] = objw[k]
    if anchor is not None:
        c[D0:] = 1
    bounds = [(0, None)] * (n + nm) + [(None, None)] * ns + [(0, None)] * nd
    res = linprog(c, A_ub=Aub, b_ub=b, A_eq=Aeq, b_eq=beq, bounds=bounds, method='highs')
    if res.x is None:
        raise RuntimeError('LP failed: ' + res.message)
    w = np.clip(res.x[:n], 0, None)
    return {k: float(res.x[S0 + j]) for j, k in enumerate(sl)}, (1 - mix) * w + mix * u


def tells(P, F, w):
    """the exact tell of every feature (points above chance) for weights w (per answer they need not sum to 1)"""
    out = {}
    for k, (f, R, fl) in F.items():
        M = collections.defaultdict(collections.Counter); tot = collections.Counter()
        for i, p in enumerate(P):
            if p['a'] in R:
                M[f(p)][p['a']] += w[i]; tot[p['a']] += w[i]
        out[k] = 100 * (sum(max(c[a] / tot[a] for a in R) for c in M.values()) / len(R) - 1 / len(R))
    return out


def fit(P, answers, F, share, caps, objw, mix, anchor, slack=.25):
    """stages 1-3 above. caps: feature -> points over its floor. objw: feature -> weight in the stage-2 objective.
    Returns (weights, stage-2 excesses)."""
    s, _ = _lp(P, answers, F, share, caps, objw, mix)
    caps2 = dict(caps, **{k: max(v, 0) + slack for k, v in s.items()})
    # the anchor is compared on the free part of the weight (without the plain-draw share)
    a = np.array(anchor, float)
    _, w = _lp(P, answers, F, share, caps2, {}, mix, anchor=a)
    return w, s


def minimax(P, answers, F, share, names, mix, caps=None):
    """the smallest t such that every feature in names has a tell <= its floor + t (with caps on others)"""
    import math
    lo, hi = 0.0, 50.0
    caps = dict(caps or {})
    for _ in range(14):
        mid = (lo + hi) / 2
        try:
            _lp(P, answers, F, share, dict(caps, **{k: mid for k in names}), {}, mix)
            hi = mid
        except RuntimeError:
            lo = mid
    return hi
