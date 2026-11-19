#!/usr/bin/env python3
"""Colour checks for Decision 12: WCAG contrast, colour-vision simulation (Machado, Oliveira & Fernandes 2009, severity 1.0)
and CIEDE2000 differences between a candidate and the four existing function colours.  Run: python3 colour.py [#hex ...]"""
import math, sys, colorsys

EXIST = {'T': '#8fbf6a', 'PD': '#c9a24a', 'D': '#c8473b', 'C': '#a493d8'}
GROUNDS = {'ink': '#0b0906', 'score': '#0e0c08', 'panel': '#17140e'}
IVORY = '#ece2c8'
CVD = {
    'protan': [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
    'deutan': [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
    'tritan': [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
}


def rgb(h): h = h.lstrip('#'); return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
def hexs(c): return '#' + ''.join(f'{max(0, min(255, round(x * 255))):02x}' for x in c)
def lin(c): return [x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c]
def gam(c): return [12.92 * x if x <= .0031308 else 1.055 * max(x, 0) ** (1 / 2.4) - .055 for x in c]
def lum(h): r, g, b = lin(rgb(h)); return .2126 * r + .7152 * g + .0722 * b
def contrast(a, b): x, y = sorted((lum(a), lum(b)), reverse=True); return (x + .05) / (y + .05)


def sim(h, kind):
    if kind == 'normal': return h
    l = lin(rgb(h)); m = CVD[kind]
    return hexs(gam([min(1, max(0, sum(m[i][j] * l[j] for j in range(3)))) for i in range(3)]))


def lab(h):
    r, g, b = lin(rgb(h))
    x = (.4124564 * r + .3575761 * g + .1804375 * b) / .95047; y = .2126729 * r + .7151522 * g + .0721750 * b; z = (.0193339 * r + .1191920 * g + .9503041 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > .008856 else 7.787 * t + 16 / 116
    return 116 * f(y) - 16, 500 * (f(x) - f(y)), 200 * (f(y) - f(z))


def de00(h1, h2):
    L1, a1, b1 = lab(h1); L2, a2, b2 = lab(h2)
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2); Cm = (C1 + C2) / 2
    G = .5 * (1 - math.sqrt(Cm ** 7 / (Cm ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360; h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dL, dC = L2 - L1, C2p - C1p
    dh = h2p - h1p
    if C1p * C2p == 0: dh = 0
    elif dh > 180: dh -= 360
    elif dh < -180: dh += 360
    dH = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lm, Cpm = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0: hm = h1p + h2p
    elif abs(h1p - h2p) <= 180: hm = (h1p + h2p) / 2
    else: hm = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    T = 1 - .17 * math.cos(math.radians(hm - 30)) + .24 * math.cos(math.radians(2 * hm)) + .32 * math.cos(math.radians(3 * hm + 6)) - .2 * math.cos(math.radians(4 * hm - 63))
    Sl = 1 + .015 * (Lm - 50) ** 2 / math.sqrt(20 + (Lm - 50) ** 2); Sc = 1 + .045 * Cpm; Sh = 1 + .015 * Cpm * T
    Rt = -2 * math.sqrt(Cpm ** 7 / (Cpm ** 7 + 25 ** 7)) * math.sin(math.radians(60 * math.exp(-((hm - 275) / 25) ** 2)))
    return math.sqrt((dL / Sl) ** 2 + (dC / Sc) ** 2 + (dH / Sh) ** 2 + Rt * (dC / Sc) * (dH / Sh))


KINDS = ['normal', 'deutan', 'protan', 'tritan']


def report(h, others=EXIST):
    """For one colour: contrast on each ground and, per vision type, the smallest CIEDE2000 gap to any of the others."""
    out = {'hex': h, 'contrast': {k: round(contrast(h, g), 2) for k, g in GROUNDS.items()}, 'on_ivory': round(contrast(h, IVORY), 2), 'gap': {}}
    for k in KINDS:
        d = {n: de00(sim(h, k), sim(o, k)) for n, o in others.items()}
        n = min(d, key=d.get); out['gap'][k] = (round(d[n], 1), n)
    out['min'] = min(v[0] for v in out['gap'].values())
    return out


def darken_for(h, ground, want=4.5):
    """The same hue, deepened until it reaches `want`:1 on a light ground."""
    r, g, b = rgb(h); hh, l, s = colorsys.rgb_to_hls(r, g, b)
    while l > 0 and contrast(hexs(colorsys.hls_to_rgb(hh, l, s)), ground) < want: l -= .004
    return hexs(colorsys.hls_to_rgb(hh, l, s))


if __name__ == '__main__':
    print('existing four, smallest gap to each other:')
    for n, h in EXIST.items():
        r = report(h, {k: v for k, v in EXIST.items() if k != n}); print(' ', n, h, r['gap'], 'contrast', r['contrast'])
    for h in sys.argv[1:] or ['#7fb3c8']:
        r = report(h); print(h, 'contrast', r['contrast'], 'on ivory', r['on_ivory'], '\n   gaps', r['gap'], 'min', r['min'], ' ivory-ink', darken_for(h, IVORY),
                             ' vs ivory text', round(de00(h, IVORY), 1), ' vs muted', round(de00(h, '#9c927c'), 1), ' sims', [sim(h, k) for k in KINDS[1:]])
