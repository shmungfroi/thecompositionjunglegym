#!/usr/bin/env python3
"""From the posed hand to an ink drawing. What is drawn is what is seen: the outer contour, every edge where one part
passes in front of another, the lines between touching fingers, the folds at bent joints, then nails and skin creases
placed on the surface in 3D (so they foreshorten correctly), and one flat tone on the side turned from the light.
Line weight is set by the light too: heavier underneath and on the shadow side, light for creases and nails.
Output: filled vector shapes in a 0 0 80 64 viewBox, one colour."""
import numpy as np, cv2, json, pathlib, sys, time
from scipy import ndimage as ndi
from skimage import measure
import poses
from hand3d import FINGERS, ORDER as FORDER, unit

L3 = unit([-0.50, 0.72, 0.48]); L2 = unit([-0.57, 0.82]); UP = 2          # ink raster = render x UP
def catmull(P, n=14):
    P = np.asarray(P, float); P = np.vstack([P[0], P, P[-1]]); out = []
    for i in range(1, len(P) - 2):
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * P[i]) + (-P[i - 1] + P[i + 1]) * t + (2 * P[i - 1] - 5 * P[i] + 4 * P[i + 1] - P[i + 2]) * t * t + (-P[i - 1] + 3 * P[i] - 3 * P[i + 1] + P[i + 2]) * t ** 3))
    out.append(P[-2]); return np.array(out)

def decals(h):
    """3D lines on the skin, in hand coordinates: (points, outward normals, max half-width mm, closed)"""
    D = []
    def surf(seg, s, th):
        a, b, r1, r2, d, n, l = seg; c = a + (b - a) * s; r = r1 + (r2 - r1) * s; o = np.cos(th) * n + np.sin(th) * l; return c + o * (r + .25), o
    def nail(seg, half, s0):
        pts = []; ths = np.radians(np.linspace(-half, half, 15))
        for s in np.linspace(s0, .88, 8): pts.append(surf(seg, s, ths[0]))
        for th in ths: pts.append(surf(seg, .88 + .12 * np.cos(th / ths[-1] * np.pi / 2) ** .7, th))
        for s in np.linspace(.88, s0, 8): pts.append(surf(seg, s, ths[-1]))
        for th in ths[::-1]: pts.append(surf(seg, s0 - .07 * np.cos(th / ths[-1] * np.pi / 2), th))
        D.append((np.array([p for p, o in pts]), np.array([o for p, o in pts]), .20, True))
    def ring(seg0, seg1, phi, half, centre, w):
        a, b, r1, r2, d1, n1, l = seg1; d0, n0 = seg0[4], seg0[5]; n = unit(n0 + n1); d = unit(d0 + d1); pts = []
        for th in np.radians(np.linspace(centre - half, centre + half, 13)):
            o = np.cos(th) * (n * np.cos(phi) + d * np.sin(phi)) + np.sin(th) * l; pts.append((a + o * (r1 + .3), o))
        D.append((np.array([p for p, o in pts]), np.array([o for p, o in pts]), w, False))
    for f in FORDER + ['thumb']:
        S = h.fr[f]; nail(S[2], 54 if f != 'thumb' else 58, .40)
        if f == 'thumb':
            ring(S[1], S[2], 0, 48, 0, .2); ring(S[1], S[2], 0, 50, 180, .22); continue
        bend1 = np.degrees(np.arccos(np.clip(S[0][4] @ S[1][4], -1, 1))); bend2 = np.degrees(np.arccos(np.clip(S[1][4] @ S[2][4], -1, 1)))
        if bend1 < 40: ring(S[0], S[1], -.14, 46, 0, .2); ring(S[0], S[1], .14, 40, 0, .18)
        if bend2 < 40: ring(S[1], S[2], 0, 40, 0, .17)
        if bend1 < 60: ring(S[0], S[1], 0, 52, 180, .22)
        if bend2 < 60: ring(S[1], S[2], 0, 48, 180, .2)
        a, b, r1, r2, d, n, l = S[0]; pts = [surf(S[0], .20, th) for th in np.radians(np.linspace(130, 230, 11))]
        D.append((np.array([p for p, o in pts]), np.array([o for p, o in pts]), .2, False))
    # palm creases: dropped onto the palm surface from below
    for xz, w in [([(-76, 24), (-68, 11), (-54, 4), (-38, 1), (-22, 3), (-10, 7)], .26), ([(-78, 27), (-71, 14), (-65, 0), (-59, -14), (-55, -25)], .22),
                  ([(-80, -31), (-85, -17), (-87, -3), (-85, 8), (-80, 17)], .22)]:
        C = catmull(xz, 10); P = np.stack([C[:, 0], np.full(len(C), -48.0), C[:, 1]], 1)
        for _ in range(60):
            d = h.sdf(P @ h.H.T + h.t); P[:, 1] += np.maximum(d, 0) * .9
        D.append((P + np.array([0, -.25, 0]), np.tile([0, -1.0, 0], (len(P), 1)), w, False))
    return D

def draw(n, small=False, ppm=3.0):
    fr = poses.frame(n, small); h = poses.hand(n, arm=fr['arm']); R = h.render(win=fr['win'], ppm=ppm, centre=fr['centre'])
    Z, ID, N = R['Z'], R['ID'], R['N']; M = ~np.isnan(Z); Zf = np.where(M, Z, -1e4); Hh, W = M.shape; px = ppm
    rad = np.zeros((Hh, W), np.float32)                                    # half line width in mm, per edge pixel
    def put(mask, r): np.maximum(rad, np.where(mask, r, 0).astype(np.float32), out=rad)
    n2 = N[..., :2] / np.maximum(np.linalg.norm(N[..., :2], axis=2, keepdims=True), 1e-4)
    shade = np.clip(.5 - .5 * (n2 @ L2), 0, 1)                             # 1 on the side away from the light
    sil = M & ~ndi.binary_erosion(M, np.ones((3, 3)))
    put(sil, (.50 + .62 * shade) if not small else (2.5 + .7 * shade))
    occ = np.zeros((Hh, W), np.float32); fid = np.zeros((Hh, W), bool); cre = np.zeros((Hh, W), bool)
    for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
        Zs = np.roll(Zf, (dy, dx), (0, 1)); Ms = np.roll(M, (dy, dx), (0, 1)); Is = np.roll(ID, (dy, dx), (0, 1))
        dz = Zf - Zs; e = M & Ms & (dz > 3.2); occ = np.maximum(occ, np.where(e, np.clip((dz - 3.2) / 16, 0, 1) + .01, 0))
        fid |= M & Ms & (np.abs(dz) <= 3.2) & (ID != Is) & (ID >= 1) & (Is >= 1) & (dz >= 0)
    for dy, dx in [(0, 2), (2, 0), (2, 2), (2, -2)]:
        Ns = np.roll(N, (dy, dx), (0, 1)); Zs = np.roll(Zf, (dy, dx), (0, 1)); Ms = np.roll(M, (dy, dx), (0, 1))
        cre |= M & Ms & (np.abs(Zf - Zs) < 2.5) & (np.einsum('ijk,ijk->ij', N, Ns) < .45)
    cre = ndi.binary_opening(cre, np.ones((2, 2)))
    if small:
        put(occ > .45, 1.5 + .5 * occ)
    else:
        put(occ > 0, .22 + .42 * occ + .18 * shade * (occ > .3)); put(fid, .26); put(cre & ~(occ > 0), .2)
    rad[R['armx'] > h.arm - 2.2] = 0                                        # the forearm ends open, not boxed
    # even the weight along each line so it swells and thins smoothly
    e = rad > 0; num = cv2.GaussianBlur(rad, (0, 0), 2.2); den = cv2.GaussianBlur(e.astype(np.float32), (0, 0), 2.2); rad = np.where(e, num / np.maximum(den, 1e-4), 0)
    S = px * UP; ink = np.zeros((Hh * UP, W * UP), np.uint8)
    lv = np.round(rad * 10).astype(int)
    for q in np.unique(lv[lv > 0]):
        m = cv2.resize((lv == q).astype(np.uint8), (W * UP, Hh * UP), interpolation=cv2.INTER_NEAREST); r = max(1, int(round(q / 10 * S)))
        ink |= cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    if not small:                                                          # nails and creases, only where the skin faces us
        for P, O, w, closed in decals(h):
            Pc = P @ h.H.T + h.t; Oc = O @ h.H.T; x, y, z = h.project(Pc, R); xi = np.clip(np.round(x).astype(int), 0, W - 1); yi = np.clip(np.round(y).astype(int), 0, Hh - 1)
            vis = (Oc[:, 2] > .12) & M[yi, xi] & (np.abs(Zf[yi, xi] - z) < 2.6)
            idx = np.arange(len(P)); m = len(P)
            for i in range(m - (0 if closed else 1)):
                j = (i + 1) % m
                if not (vis[i] and vis[j]): continue
                u = (i + .5) / m; tw = 1.0 if closed else (.35 + .65 * np.sin(np.pi * u) ** .8)
                cv2.line(ink, (int(round(x[i] * UP)), int(round(y[i] * UP))), (int(round(x[j] * UP)), int(round(y[j] * UP))), 1, max(1, int(round(2 * w * tw * S))), cv2.LINE_8)
    inkf = cv2.GaussianBlur(ink.astype(np.float32), (0, 0), 1.5 if not small else 3.0)
    # tone: one flat mid-tone on the side turned from the light (small variant: a light tint over the whole hand)
    if small: tone = cv2.GaussianBlur(cv2.resize(M.astype(np.float32), (W * UP, Hh * UP)), (0, 0), 2)
    else:
        sh = (M & ((N @ L3) < -.02) & (R['armx'] < h.arm - 1.5)).astype(np.float32); sh = cv2.GaussianBlur(cv2.resize(sh, (W * UP, Hh * UP)), (0, 0), 5); t = sh > .5
        lab, k = ndi.label(t); sizes = ndi.sum(t, lab, range(1, k + 1)); t = np.isin(lab, [i + 1 for i, a in enumerate(sizes) if a > (9 * S) ** 2])
        tone = cv2.GaussianBlur(t.astype(np.float32), (0, 0), 2)
    k = 80.0 / (W * UP)
    return path(inkf, k, .55 if not small else 1.2), path(tone, k, .9 if not small else 1.6), M

def path(img, k, tol):
    out = []
    for c in measure.find_contours(np.pad(img, 1), .5):
        c = measure.approximate_polygon(c - 1, tol)
        if len(c) < 5: continue
        c = c[:-1][:, ::-1] * k; m = (c + np.roll(c, -1, 0)) / 2; nx = np.roll(c, -1, 0)
        f = lambda v: f'{v:.2f}'.rstrip('0').rstrip('.')
        s = f'M{f(m[0][0])} {f(m[0][1])}' + ''.join(f'Q{f(nx[i][0])} {f(nx[i][1])} {f(m[(i + 1) % len(m)][0])} {f(m[(i + 1) % len(m)][1])}' for i in range(len(c))) + 'Z'
        out.append(s)
    return ''.join(out)

if __name__ == '__main__':
    H = pathlib.Path(__file__).resolve().parent; out = H / 'drawn'; out.mkdir(exist_ok=True)
    for n in (sys.argv[1:] or poses.ORDER):
        t0 = time.time(); d = {}
        d['ink'], d['tone'], _ = draw(n); d['ink_s'], d['tone_s'], _ = draw(n, small=True, ppm=2.0)
        (out / f'{n}.json').write_text(json.dumps(d)); print(n, round(time.time() - t0), 's', len(d['ink']) // 1024, 'kB', len(d['ink_s']) // 1024, 'kB', flush=True)
