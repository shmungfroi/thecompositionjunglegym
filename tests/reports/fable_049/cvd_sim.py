#!/usr/bin/env python3
"""Colour-blind safety of the function colours (register 0.49, row C6).

Run from the repo root:
  python3 tests/reports/fable_049/cvd_sim.py                 report on the colours now in index.html
  python3 tests/reports/fable_049/cvd_sim.py --proposed      report on the proposed values (PROPOSED below)
  python3 tests/reports/fable_049/cvd_sim.py --search        look for better values near each Garden hue
  python3 tests/reports/fable_049/cvd_sim.py --proposed --check   exit 1 if a rule fails (for tests/run_all)
  ... --md  prints the tables as markdown;  --swatches FILE.html writes a swatch sheet

Method
  Simulation: Machado, Oliveira and Fernandes (2009), severity 1.0 (full dichromacy: protanopia, deuteranopia,
  tritanopia), matrices applied in linear RGB. Severity 0.6 (a common anomalous trichromat) is reported as well.
  Difference: CIEDE2000 between the simulated colours (D65, 2 degree observer).
  Contrast: WCAG 2.x relative luminance ratio. It does not change under simulation here: it is measured on the
  true colours, as WCAG defines it.
Rules checked (--check)
  R1  every function colour >= 4.5:1 on every dark ground it is drawn on as text, >= 3:1 on the gold-washed "now" bar
      (where only the 3 px stripe carries it), and the ivory variant >= 4.5:1 on ivory
  R2  every pair of function colours differs by dE00 >= 11 under normal vision and each simulation
      (below 11 two small swatches are hard to tell apart without a side-by-side comparison; the non-colour cue
      covers what colour cannot)
No third-party packages.
"""
import sys, re, math, itertools, pathlib

REPO = pathlib.Path(__file__).resolve().parents[3]
NAMES = {'T': 'tonic', 'PD': 'pre-dominant', 'D': 'dominant', 'MD': 'modal dominant', 'C': 'chromatic / outside the key'}
TOKEN = {'T': '--green', 'PD': '--gold', 'D': '--red', 'MD': '--md', 'C': '--violet'}
# The grounds a function colour is drawn on (index.html): page, cards, insets, tiles, and the gold-washed "now" bar.
GROUNDS = {'--ink page': '#0b0906', '--inset / .bar / .vrv': '#0e0c08', '--panel card': '#12100b', 'wheel node': '#14110c',
           'dock': '#16130d', '--panel2': '#17140e', 'tile / play': '#1b170f', '.bar.now (gold 20% on inset)': None}
IVORY = '#ece2c8'
# Proposed 0.49 values (see DESIGN_049.md, C6). Gold is the Garden's own gold and stays.
PROPOSED = {'T': '#9dc995', 'PD': '#c9a24a', 'D': '#d15e5d', 'MD': '#b1729d', 'C': '#a493d8', 'MDI': '#8b4978'}

def hex2rgb(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
def rgb2hex(c): return '#' + ''.join('%02x' % max(0, min(255, round(v * 255))) for v in c)
def lin(v): return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
def unlin(v): v = max(0, min(1, v)); return v * 12.92 if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
def lum(h): r, g, b = (lin(v) for v in hex2rgb(h)); return 0.2126 * r + 0.7152 * g + 0.0722 * b
def contrast(a, b): la, lb = lum(a), lum(b); return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
def over(fg, alpha, bg): f, b = hex2rgb(fg), hex2rgb(bg); return rgb2hex(tuple(alpha * x + (1 - alpha) * y for x, y in zip(f, b)))
GROUNDS['.bar.now (gold 20% on inset)'] = over('#c9a24a', .2, '#0e0c08')

# Machado et al. 2009, severity 1.0 and 0.6
M = {('protan', 1.0): [[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]],
     ('deutan', 1.0): [[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]],
     ('tritan', 1.0): [[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]],
     ('protan', 0.6): [[0.385450, 0.769005, -0.154455], [0.100526, 0.829802, 0.069673], [-0.007442, -0.022190, 1.029632]],
     ('deutan', 0.6): [[0.498864, 0.674741, -0.173604], [0.205199, 0.754872, 0.039929], [-0.011131, 0.030969, 0.980162]],
     ('tritan', 0.6): [[1.104996, -0.046633, -0.058363], [-0.032137, 0.971635, 0.060503], [0.001336, 0.317922, 0.680742]]}
def sim(h, kind, sev=1.0):
    if kind == 'normal': return h
    m = M[(kind, sev)]; l = [lin(v) for v in hex2rgb(h)]
    return rgb2hex(tuple(unlin(sum(m[i][j] * l[j] for j in range(3))) for i in range(3)))

def lab(h):
    r, g, b = (lin(v) for v in hex2rgb(h))
    X = (0.4124564 * r + 0.3575761 * g + 0.1804375 * b) / 0.95047; Y = 0.2126729 * r + 0.7151522 * g + 0.0721750 * b
    Z = (0.0193339 * r + 0.1191920 * g + 0.9503041 * b) / 1.08883
    f = lambda t: t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116
    return 116 * f(Y) - 16, 500 * (f(X) - f(Y)), 200 * (f(Y) - f(Z))
def de00(h1, h2):
    L1, a1, b1 = lab(h1); L2, a2, b2 = lab(h2)
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2); Cm = (C1 + C2) / 2
    G = 0.5 * (1 - math.sqrt(Cm ** 7 / (Cm ** 7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2; C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360 if C1p else 0; h2p = math.degrees(math.atan2(b2, a2p)) % 360 if C2p else 0
    dL, dC = L2 - L1, C2p - C1p; dh = h2p - h1p
    if C1p * C2p == 0: dh = 0
    elif dh > 180: dh -= 360
    elif dh < -180: dh += 360
    dH = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2)); Lm, Cpm = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0: hm = h1p + h2p
    elif abs(h1p - h2p) <= 180: hm = (h1p + h2p) / 2
    else: hm = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    T = 1 - 0.17 * math.cos(math.radians(hm - 30)) + 0.24 * math.cos(math.radians(2 * hm)) + 0.32 * math.cos(math.radians(3 * hm + 6)) - 0.20 * math.cos(math.radians(4 * hm - 63))
    Sl = 1 + 0.015 * (Lm - 50) ** 2 / math.sqrt(20 + (Lm - 50) ** 2); Sc = 1 + 0.045 * Cpm; Sh = 1 + 0.015 * Cpm * T
    Rc = 2 * math.sqrt(Cpm ** 7 / (Cpm ** 7 + 25 ** 7)); Rt = -Rc * math.sin(math.radians(60 * math.exp(-((hm - 275) / 25) ** 2)))
    return math.sqrt((dL / Sl) ** 2 + (dC / Sc) ** 2 + (dH / Sh) ** 2 + Rt * (dC / Sc) * (dH / Sh))

# OKLCH, for the search (move along lightness and chroma, keep the hue family)
def oklch(h):
    r, g, b = (lin(v) for v in hex2rgb(h))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3); m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3); s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s; a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s; bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360
def from_oklch(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3; m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3; s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    rgb = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s, -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s, -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    if min(rgb) < -1e-4 or max(rgb) > 1 + 1e-4: return None
    return rgb2hex(tuple(unlin(v) for v in rgb))

def current():
    css = (REPO / 'index.html').read_text(encoding='utf8'); root = re.search(r':root\{([^}]*)\}', css).group(1)
    tok = dict(re.findall(r'(--[\w-]+):(#[0-9a-fA-F]{6})', root))
    c = {k: tok[v] for k, v in TOKEN.items()}; c['MDI'] = tok.get('--md-ivory', '#9e4776'); return c

VIEWS = ['normal', 'protan', 'deutan', 'tritan']
def pairs(c, sev=1.0):
    out = []
    for a, b in itertools.combinations(['T', 'PD', 'D', 'MD', 'C'], 2):
        out.append((a, b, [de00(sim(c[a], v, sev), sim(c[b], v, sev)) for v in VIEWS]))
    return out
NOW = '.bar.now (gold 20% on inset)'   # only the 3 px function stripe sits on this ground: a graphic, 3:1
def worst_ground(h): return min(contrast(h, g) for n, g in GROUNDS.items() if n != NOW)
def ok_grounds(h): return worst_ground(h) >= 4.5 and contrast(h, GROUNDS[NOW]) >= 3

def report(c, md=False, title=''):
    P = print; fails = []
    P(f'\n## {title}\n' if md else f'\n=== {title} ===')
    P('| fn | hex | ' + ' | '.join(GROUNDS) + ' | worst |' if md else 'contrast on each ground: ' + ', '.join(GROUNDS))
    if md: P('|' + '---|' * (len(GROUNDS) + 3))
    for k in ['T', 'PD', 'D', 'MD', 'C']:
        cs = [contrast(c[k], g) for g in GROUNDS.values()]; w = worst_ground(c[k]); lim = [3 if n == NOW else 4.5 for n in GROUNDS]
        if w < 4.5: fails.append(f'R1 {k} {c[k]} worst text contrast {w:.2f}')
        if cs[-1] < 3: fails.append(f'R1 {k} {c[k]} stripe on the now-bar {cs[-1]:.2f}')
        row = ' | '.join(f'{x:.2f}' + ('' if x >= l else ' ✗') for x, l in zip(cs, lim))
        P(f'| {k} {NAMES[k]} | `{c[k]}` | {row} | **{w:.2f}** |' if md else f'  {k:3} {c[k]}  {row}  worst {w:.2f}')
    iv = contrast(c['MDI'], IVORY); P(('\n' if md else '') + f'Ivory variant {c["MDI"]} on ivory {IVORY}: {iv:.2f}:1' + ('' if iv >= 4.5 else ' ✗'))
    if iv < 4.5: fails.append(f'R1 ivory variant {iv:.2f}')
    for sev in (1.0, 0.6):
        P(f'\nPairs, dE00, severity {sev} (below 11 = collapses ✗, 11 to 20 = weak ~)\n')
        P('| pair | normal | protan | deutan | tritan |' if md else '  pair      normal protan deutan tritan')
        if md: P('|---|---|---|---|---|')
        for a, b, ds in pairs(c, sev):
            cells = [f'{d:.1f}' + (' ✗' if d < 11 else ' ~' if d < 20 else '') for d in ds]
            if sev == 1.0 and min(ds) < 11: fails.append(f'R2 {a}/{b} min dE00 {min(ds):.1f}')
            P(f'| {a} / {b} | ' + ' | '.join(cells) + ' |' if md else f'  {a:3}/{b:3}  ' + '  '.join(f'{x:>7}' for x in cells))
    P('\nSimulated colours (severity 1.0)\n')
    P('| fn | normal | protan | deutan | tritan |' if md else '')
    if md: P('|---|---|---|---|---|')
    for k in ['T', 'PD', 'D', 'MD', 'C']:
        P((f'| {k} | ' + ' | '.join(f'`{sim(c[k], v)}`' for v in VIEWS) + ' |') if md else f'  {k:3} ' + ' '.join(sim(c[k], v) for v in VIEWS))
    P('\n' + ('All rules pass.' if not fails else 'Fails: ' + '; '.join(fails)))
    return fails

def search(c0, fixed=('PD',)):
    """Coordinate descent in OKLCH: each colour may move in lightness and chroma, hue within 10 degrees of the Garden hue.
    Score = smallest pairwise dE00 over normal + three simulations, minus a small cost for moving away from the original."""
    c = dict(c0); base = {k: oklch(c0[k]) for k in TOKEN}
    def score(c):
        ds = sorted(d for _, _, x in pairs(c) for d in x); move = sum(de00(c[k], c0[k]) for k in TOKEN)
        return ds[0] + 0.15 * sum(ds[:5]) / 5 - 0.06 * move
    for rnd in range(4):
        for k in TOKEN:
            if k in fixed: continue
            L0, C0, H0 = base[k]; best = (score(c) if ok_grounds(c[k]) else -1e9, c[k])
            for dL in [x / 100 for x in range(-10, 17, 2)]:
                for dC in [x / 100 for x in range(-6, 7, 2)]:
                    for dH in ((-10, -5, 0, 5, 10, 15, 20) if k == 'T' else (-10, -5, 0, 5, 10)):
                        h = from_oklch(L0 + dL, max(0.02, C0 + dC), (H0 + dH) % 360)
                        if not h or not ok_grounds(h) or worst_ground(h) < 4.6: continue
                        t = dict(c); t[k] = h; s = score(t)
                        if s > best[0] + 1e-6: best = (s, h)
            c[k] = best[1]
    return c

def swatches(path, sets):
    rows = ''
    for title, c in sets:
        rows += f'<h2>{title}</h2><table><tr><th></th>' + ''.join(f'<th>{v}</th>' for v in VIEWS) + '</tr>'
        for k in ['T', 'PD', 'D', 'MD', 'C']:
            rows += f'<tr><th>{k} · {NAMES[k]}<br><code>{c[k]}</code></th>' + ''.join(
                f'<td><span class="bar" style="--c:{sim(c[k], v)}"><b>{k}</b> {sim(c[k], v)}</span><span class="tx" style="color:{sim(c[k], v)}">{NAMES[k]}</span></td>' for v in VIEWS) + '</tr>'
        rows += '</table>'
    pathlib.Path(path).write_text('<!doctype html><meta charset="utf8"><title>CJG function colours, simulated</title><style>body{background:#12100b;color:#ece2c8;font:14px/1.4 Outfit,system-ui,sans-serif;padding:24px}h2{font-weight:400;font-size:18px;margin:26px 0 8px}table{border-collapse:separate;border-spacing:10px 8px}th{font-weight:400;font-size:12.5px;color:#9c927c;text-align:left}code{font-size:12px}.bar{display:block;width:150px;border:1px solid #2a2418;border-top:3px solid var(--c);border-radius:8px;background:#0e0c08;padding:6px 10px;font-size:12.5px;color:#9c927c}.bar b{color:var(--c);font-size:16px;margin-right:6px}.tx{display:block;font-size:14px;margin-top:3px}</style>' + rows, encoding='utf8')

if __name__ == '__main__':
    a = sys.argv[1:]; md = '--md' in a; cur = current(); fails = []
    if '--search' in a:
        s = search(cur); s['MDI'] = cur['MDI']; print('search result:', s); report(s, md, 'Search result')
    elif '--proposed' in a: fails = report(PROPOSED, md, 'Proposed 0.49 function colours')
    else: fails = report(cur, md, 'Function colours in index.html now')
    if '--swatches' in a: swatches(a[a.index('--swatches') + 1], [('Now (0.48)', cur), ('Proposed (0.49)', PROPOSED)])
    if '--check' in a and fails: sys.exit(1)
