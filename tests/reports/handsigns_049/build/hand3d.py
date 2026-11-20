#!/usr/bin/env python3
"""A posable right hand built from anatomical measurements, for the 0.49 hand-sign drawings (round 2).

Nothing here is traced. The hand is a set of bones with real proportions (an adult hand about 185 mm long), each joint
bent only where a real joint bends; flesh is a signed-distance surface (rounded cones and ellipsoids, blended) around the
bones. The pose of each sign is set in degrees per joint, the model is looked at from the signer's own eye, and the
drawing is derived from what is seen: contours, overlaps, creases, nails, shadow side.

Hand frame (mm): wrist centre at 0; fingers along -x; back of the hand +y; thumb (radial) side +z.
Camera: looks along -z; screen x = x, screen up = y. Larger z is nearer.
"""
import numpy as np

def Rx(d):
    a = np.radians(d); c, s = np.cos(a), np.sin(a); return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
def Ry(d):
    a = np.radians(d); c, s = np.cos(a), np.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
def Rz(d):
    a = np.radians(d); c, s = np.cos(a), np.sin(a); return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
def unit(v):
    v = np.asarray(v, float); return v / np.linalg.norm(v)

# ---- measurements (mm). Phalanx lengths are external segment lengths, knuckle to knuckle ----
FINGERS = {  # mcp position, (proximal, middle, distal) lengths, radii at mcp, pip, dip, tip
 'index':  dict(mcp=(-97, 1, 27),  L=(44, 25, 23), r=(9.6, 8.6, 7.6, 6.6)),
 'middle': dict(mcp=(-101, 2, 8.5), L=(48, 29, 24), r=(9.7, 8.7, 7.7, 6.7)),
 'ring':   dict(mcp=(-96, 1, -9.5), L=(44, 27, 23), r=(9.2, 8.2, 7.3, 6.3)),
 'little': dict(mcp=(-86, -1, -26), L=(34, 19, 21), r=(8.2, 7.3, 6.5, 5.7)),
}
ORDER = ['index', 'middle', 'ring', 'little']
THUMB = dict(cmc=(-20, -7, 25), L=(42, 31, 27), r=(11.5, 10.2, 9.0, 7.6))
GROUPS = ['body', 'index', 'middle', 'ring', 'little', 'thumb']

class Hand:
    """pose: flex={finger:(mcp,pip,dip)}, spread={finger:deg}, thumb=(dir_meta, dir_prox, dir_dist, nail_normal),
    wrist=(flexion, deviation), arm=length of forearm drawn; view: roll, pitch, yaw, elev; t=(x,y) shift in mm."""
    def __init__(s, flex, spread, thumb, wrist=(0, 0), arm=62, roll=0, pitch=0, yaw=0, elev=0, t=(0, 0), cup=0, fill=None):
        s.arm = arm
        s.G = Rx(elev) @ Ry(yaw) @ Rz(-pitch) @ Rx(-roll)                 # forearm frame -> camera
        s.Wr = Rz(wrist[0]) @ Ry(wrist[1])                               # hand frame -> forearm frame
        s.t = np.array([t[0], t[1], 0.0])
        s.H = s.G @ s.Wr
        s.prims, s.decals, s.fr = [], [], {}
        P = s.hp
        # palm: four metacarpals from the wrist to the knuckles, the thenar and hypothenar pads
        carp = {'index': (-6, 0, 14), 'middle': (-6, 1, 5), 'ring': (-6, 0, -5), 'little': (-6, -1, -14)}
        for f in ORDER:
            m = np.array(FINGERS[f]['mcp'], float)
            if cup and f in ('ring', 'little'): m = m + np.array([0, -cup * (1 if f == 'ring' else 2.2), 0])
            s.fr[f + '_mcp'] = m
            s.rc(P(carp[f]), P(m), 12.5, FINGERS[f]['r'][0] + 1.2, 'body')
            s.rc(P(m + np.array([2, 3.0, 0])), P(m + np.array([6, 3.4, 0])), 7.2, 6.4, 'body')     # knuckle head
        s.ell(P((-52, -3, 0)), s.H, (40, 11.5, 36), 'body')                 # the slab of the palm
        s.ell(P((-36, -12, -24)), s.H @ Ry(-8), (34, 9, 13), 'body')        # hypothenar pad
        if fill:                                                            # a closed fist is full: finger pads and palm meet
            s.rc(P((-95, -25, fill[0])), P((-87, -26, fill[1])), 15, 13, 'body')
        # forearm: elliptical, slightly wider towards the elbow, cut clean
        s.fore = (s.G, s.t)
        # fingers
        for f in ORDER:
            F = FINGERS[f]; a = 0.0; p = s.fr[f + '_mcp'].copy(); A = Ry(spread.get(f, 0)); segs = []
            for i in range(3):
                a += flex[f][i]; d = A @ np.array([-np.cos(np.radians(a)), -np.sin(np.radians(a)), 0])
                n = A @ np.array([-np.sin(np.radians(a)), np.cos(np.radians(a)), 0]); l = A @ np.array([0, 0, 1.0])
                q = p + d * F['L'][i]; segs.append((p.copy(), q.copy(), F['r'][i], F['r'][i + 1], d, n, l)); p = q
            s.fr[f] = segs
            for i, (a0, b0, r1, r2, d, n, l) in enumerate(segs):
                s.rc(P(a0), P(b0), r1, r2, f, part=i)
            s.rc(P(segs[1][0] + segs[1][5] * 0.9), P(segs[1][0] + segs[1][5] * 1.0), segs[1][2] + .15, segs[1][2] + .15, f, part=1)   # pip knuckle
        # thumb
        p = np.array(THUMB['cmc'], float); segs = []
        for i in range(3):
            d = unit(thumb[i]); n = unit(np.asarray(thumb[3], float) - d * np.dot(thumb[3], d)); l = np.cross(d, n)
            q = p + d * THUMB['L'][i]; segs.append((p.copy(), q.copy(), THUMB['r'][i], THUMB['r'][i + 1], d, n, l)); p = q
        s.fr['thumb'] = segs
        a0, b0 = segs[0][0], segs[0][1]
        s.rc(P(a0), P(b0), 13.5, 11.2, 'body')                              # thumb metacarpal with its muscle
        mid = (a0 + b0) / 2 + np.array([4, -3, -6]); ax = unit(b0 - a0)
        s.rc(P(np.array([-10, -9, 12])), P(mid), 12, 13.5, 'body')          # thenar pad, rooted at the wrist
        for i in (1, 2):
            a0, b0, r1, r2 = segs[i][:4]; s.rc(P(a0), P(b0), r1, r2, 'thumb', part=i)
    # ---- helpers ----
    def hp(s, p): return s.H @ np.asarray(p, float) + s.t
    def hv(s, v): return s.H @ np.asarray(v, float)
    def rc(s, a, b, r1, r2, g, part=0): s.prims.append(('rc', np.asarray(a, np.float32), np.asarray(b, np.float32), float(r1), float(r2), g, part))
    def ell(s, c, R, rad, g): s.prims.append(('ell', np.asarray(c, np.float32), np.asarray(R, np.float32), np.asarray(rad, np.float32), g, 0))

    # ---- distance field ----
    @staticmethod
    def _rc(p, a, b, r1, r2):
        ba = b - a; l2 = float(ba @ ba); rr = r1 - r2; a2 = l2 - rr * rr; il2 = 1.0 / l2
        pa = p - a; y = pa @ ba; z = y - l2
        w = pa * l2 - np.outer(y, ba); x2 = np.einsum('ij,ij->i', w, w); y2 = y * y * l2; z2 = z * z * l2
        k = np.sign(rr) * rr * rr * x2
        d = (np.sqrt(np.maximum(x2 * a2 * il2, 0)) + y * rr) * il2 - r1
        c1 = np.sign(z) * a2 * z2 > k; c2 = np.sign(y) * a2 * y2 < k
        d = np.where(c2, np.sqrt(x2 + y2) * il2 - r1, d); d = np.where(c1, np.sqrt(x2 + z2) * il2 - r2, d)
        return d
    @staticmethod
    def _smin(a, b, k):
        h = np.maximum(k - np.abs(a - b), 0) / k; return np.minimum(a, b) - h * h * k * 0.25
    def groups(s, p):
        """distance to each group: body (blended), four finger chains, thumb chain"""
        p = p.astype(np.float32); out = {}
        body = None; ch = {g: [None, None, None] for g in GROUPS[1:]}
        for pr in s.prims:
            if pr[0] == 'rc':
                _, a, b, r1, r2, g, part = pr; d = s._rc(p, a, b, r1, r2)
            else:
                _, c, R, rad, g, part = pr; q = (p - c) @ R; k0 = np.linalg.norm(q / rad, axis=1); k1 = np.linalg.norm(q / (rad * rad), axis=1)
                d = k0 * (k0 - 1.0) / np.maximum(k1, 1e-6)
            if g == 'body': body = d if body is None else s._smin(body, d, 9.0)
            else: ch[g][part] = d if ch[g][part] is None else s._smin(ch[g][part], d, 1.5)
        # forearm
        G, t = s.fore; q = (p - t) @ G; q = q * np.array([1, 1 / 0.70, 1], np.float32)
        fa = s._rc(q, np.array([-4, 0, 0], np.float32), np.array([s.arm + 30, 0, 0], np.float32), 27.5, 31.0) * 0.70
        body = s._smin(body, fa, 12.0)
        cut = ((p - t) @ G)[:, 0] - s.arm
        res = []
        for g in GROUPS[1:]:
            pr = [x for x in ch[g] if x is not None]; c = pr[0]
            for x in pr[1:]: c = s._smin(c, x, 3.0)
            # the proximal segment grows out of the body; the rest of the chain stays its own
            if g == 'thumb': body = s._smin(body, ch[g][1], 5.0)
            else: body = s._smin(body, ch[g][0], 6.0)
            res.append(c)
        body = np.maximum(body, cut)
        return np.stack([body] + res, 1)
    def sdf(s, p): return s.groups(p).min(1)

    # ---- orthographic ray march ----
    def render(s, win=(250, 200), ppm=3.0, centre=(-70, 0)):
        W, Hh = int(win[0] * ppm), int(win[1] * ppm)
        xs = centre[0] + (np.arange(W) + .5) / ppm - win[0] / 2; ys = centre[1] - (np.arange(Hh) + .5) / ppm + win[1] / 2
        X, Y = np.meshgrid(xs, ys); n = W * Hh
        px = X.ravel().astype(np.float32); py = Y.ravel().astype(np.float32); z = np.full(n, 170, np.float32)
        alive = np.arange(n); hit = np.zeros(n, bool)
        for it in range(90):
            if not len(alive): break
            p = np.stack([px[alive], py[alive], z[alive]], 1); d = s.sdf(p)
            h = d < 0.12; hit[alive[h]] = True
            z[alive] -= np.maximum(d, 0.05) * 0.85
            keep = (~h) & (z[alive] > -170); alive = alive[keep]
        idx = np.where(hit)[0]; p = np.stack([px[idx], py[idx], z[idx]], 1)
        g = s.groups(p); gid = g.argmin(1)
        e = 0.35; nrm = np.zeros((len(idx), 3), np.float32)
        for k in range(3):
            dp = np.zeros(3, np.float32); dp[k] = e; nrm[:, k] = s.sdf(p + dp) - s.sdf(p - dp)
        nrm /= np.maximum(np.linalg.norm(nrm, axis=1, keepdims=True), 1e-6)
        Z = np.full(n, np.nan, np.float32); Z[idx] = z[idx]; ID = np.full(n, -1, np.int8); ID[idx] = gid
        N = np.zeros((n, 3), np.float32); N[idx] = nrm
        armx = np.full(n, -1e3, np.float32); armx[idx] = ((p - s.t) @ s.G)[:, 0]
        return dict(Z=Z.reshape(Hh, W), ID=ID.reshape(Hh, W), N=N.reshape(Hh, W, 3), armx=armx.reshape(Hh, W), ppm=ppm, win=win, centre=centre, W=W, H=Hh)
    def project(s, P, R):
        P = np.asarray(P, float); x = (P[:, 0] - R['centre'][0] + R['win'][0] / 2) * R['ppm']; y = (R['centre'][1] + R['win'][1] / 2 - P[:, 1]) * R['ppm']
        return x, y, P[:, 2]
