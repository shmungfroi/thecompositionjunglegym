#!/usr/bin/env python3
"""Composition Jungle Gym hand signs, 0.49 design set. Original artwork: every outline below was written by hand as

Frame: viewBox 0 0 80 64. One right hand, wrist entering from the right, fingers to the left.
Each base shape is drawn with the wrist centre at (0,0) and the forearm along +x, then placed with
translate / rotate / flip. Outline 2.6, inner lines 1.7, round caps; the silhouette carries a 10% tint of the same colour.
"""
import json, pathlib
H = pathlib.Path(__file__).resolve().parent
OUT = H.parent / 'svg'

# ---- base shapes: (silhouette, [inner lines]) ----
BLADE = ("M14 -6.4 C8 -7 2 -7.2 -4 -6.6 C-16 -5.6 -29 -4.2 -41.5 -3.2 C-46.8 -2.8 -47.4 3 -42.2 3.5 C-34 4.2 -26.5 4.6 -19.4 4.7 C-19.8 8.2 -15.4 9.8 -10.4 9.2 C-5 8.6 2 7.4 14 7.2",
         ["M-18.2 4.4 C-13.2 2.9 -8 2.6 -3.4 3.3"])
# the blade with the thumb let fall (ra)
BLADE_T = ("M14 -6.4 C8 -7 2 -7.2 -4 -6.6 C-16 -5.6 -29 -4.2 -41.5 -3.2 C-46.8 -2.8 -47.4 3 -42.2 3.5 C-34 4.2 -27 4.6 -21.5 4.8 C-22.4 8.4 -23 11.6 -22.8 14.6 C-22.4 18.6 -17.4 18.6 -16.6 15 C-16 12.6 -14.6 11.4 -11 9.4 C-5.5 8.4 2 7.4 14 7.2",
           ["M-36 0.6 C-30 0.9 -25 1.3 -20 1.5"])
FIST = ("M14 -7.6 C9 -8 4 -8.8 -1 -10.4 C-6 -12.2 -11 -15 -17 -16 C-22 -16.8 -27 -15.6 -29.6 -12 C-31.4 -8.6 -32 -3 -31.6 2 C-31.4 7 -29 11.6 -24 13 C-18 14.4 -11 13 -6 11.6 C0 10.2 7 8.8 14 8.4",
        ["M-7 2.6 C-12 0.4 -17.4 0.4 -21.6 2.6 C-24.6 4.4 -23.6 8.4 -19.8 8.2 C-16 8 -12.6 7.6 -9.6 8.2",
         "M-30.6 -3 C-26 -4.4 -21.6 -3.8 -18.6 -1.4", "M-27.6 -10.8 C-24.8 -12.4 -21.8 -12.4 -19.2 -11.2"])
FA = ("M14 -7.6 C9 -8 4 -8.6 -1 -10 C-7 -12.4 -14 -15.6 -21 -15.2 C-27 -14.8 -32 -11.6 -33.6 -6.4 C-35.4 -3 -35.2 1.4 -32.6 4.4 C-30.8 6.2 -29.6 7 -28.8 7.4 C-29.2 12 -29.4 17 -28.8 21.6 C-28 26.8 -20.4 26.8 -19.8 21.6 C-19.4 17.6 -19 14.6 -17.8 11.8 C-12 12.6 -6 11.6 -1 10.6 C4 9.6 9 8.8 14 8.4",
      ["M-33 -1 C-27.6 -3 -21.6 -2.4 -17.6 0.6 C-15.8 3 -16.4 6.4 -18.4 9",
       "M-33.6 -6.4 C-28 -8.4 -22.6 -8 -19 -5.8"])
SO = ("M14 -6.4 C9 -6.8 4 -7.4 0 -8.6 C-3.4 -9.8 -5.6 -12.4 -7.4 -15.6 C-9.4 -19.2 -11.2 -23 -14.4 -25.4 C-17.6 -27.6 -21.6 -25 -20.4 -21.2 C-19.4 -18 -19.2 -14.8 -20.6 -11.8 "
      "C-27 -11.4 -35 -11 -42.6 -10.4 C-47.2 -10 -47.6 -4.8 -44.4 -4.2 C-50.4 -3.8 -50.6 1.4 -45.6 1.6 C-49.6 2.2 -49.2 7 -44.2 7 C-46.6 8 -45.8 12 -41 11.8 "
      "C-34 11.6 -27 11.8 -21 11.6 C-13 11.4 -6.6 11.2 -2.4 9.6 C2 8.2 8 7.5 14 7.2",
      ["M-44.4 -4.2 C-37 -4.6 -30 -4.8 -24 -4.8", "M-45.6 1.6 C-38 1.4 -31 1.2 -24.6 1.2", "M-44.2 7 C-37.6 6.8 -31 6.7 -25 6.6",
       "M-19.6 -10.4 C-15 -7.6 -12.6 -2.6 -13.4 4"])
# so with the fingers fanned open (si)
SI = ("M14 -6.4 C9 -6.8 4 -7.4 0 -8.6 C-3.4 -9.8 -5 -12.6 -6 -16 C-7.2 -20 -8 -24.4 -10.4 -27.6 C-13 -30.6 -17.6 -28.6 -17 -24.6 C-16.4 -20.8 -17 -16.6 -19.4 -13 "
      "C-25 -15 -32 -18 -39.4 -20.6 C-44.4 -22.2 -46.6 -16.4 -42 -14.6 C-36 -12.2 -30 -9.8 -25.4 -7.6 "
      "C-31.6 -7.8 -39.6 -8.4 -46.4 -8.6 C-51.6 -8.6 -51.8 -2.4 -46.6 -2.2 C-39.6 -2 -32 -1.6 -25.8 -1.2 "
      "C-31.6 0.2 -38.6 2 -44.6 3.8 C-49.4 5.4 -47.8 11.2 -42.8 9.8 C-36.6 8.2 -30.4 6.4 -24.8 5 "
      "C-29 7.4 -33.6 10.4 -37.6 13.6 C-41.2 16.8 -37.6 21 -33.8 18.4 C-29 15.2 -24 12.6 -19 11.4 C-12 10.8 -6.4 10.8 -2.4 9.6 C2 8.2 8 7.5 14 7.2",
      ["M-18.4 -11.4 C-14 -8.4 -11.8 -3 -12.6 3.6"])
LA = ("M14 -6.4 C8 -7.2 2 -9 -4 -10.2 C-11 -11.4 -18.6 -9.6 -23.6 -4.6 C-27.6 -0.4 -30.6 5.6 -32.4 11.4 C-33.4 14.6 -34 17.4 -33.6 19.4 C-33 22.6 -28.8 22.4 -28 19.4 "
      "C-27.8 22.6 -23.4 23.4 -22.4 20 C-21.4 16.4 -20.6 12.6 -18.6 9.2 C-18.4 12.4 -17.8 15.4 -16 18 C-14 20.6 -10.2 18.8 -10.6 15.6 C-11 12.4 -9.4 9.6 -4.6 8.8 C1 8 7 7.5 14 7.2",
      ["M-28 19.4 C-27.6 15.4 -26.6 11.4 -24.6 7.6", "M-22.6 -3.6 C-19.6 -6.2 -15.6 -7.4 -11.6 -7"])
TI = ("M14 -7.6 C8 -8.2 2 -9.2 -3 -10.8 C-9 -12.8 -14.6 -15 -19 -17.4 C-25.4 -21.4 -32 -26.4 -38.6 -31.4 C-43.6 -34.8 -48 -29 -43.6 -25.4 C-37.6 -20.6 -32.4 -15.6 -28.6 -10.6 "
      "C-31.8 -7 -33 -1.6 -31.4 3.6 C-29.6 9.4 -24 12.4 -17.6 12.6 C-11 12.8 -4 11.6 2 10.4 C6 9.6 10 8.8 14 8.4",
      ["M-31 -4.4 C-25.6 -7.4 -18.6 -6.6 -14.6 -3 C-12.4 0.4 -15.6 4.6 -20.4 5 C-23.6 5.2 -26.6 4.8 -29 3.8",
       "M-28.6 -10.6 C-24.6 -12.4 -20.6 -12 -17.8 -10"])
BASE = dict(blade=BLADE, bladeT=BLADE_T, fist=FIST, fa=FA, so=SO, si=SI, la=LA, ti=TI)

# ---- the 17 signs (do' reuses do): base, x, y, rotation (clockwise +), flip, kind ----
# kind: n natural, u raised (turned up), d lowered (turned down)
SIGNS = {
 'do': ('fist', 57, 33, 0, 1, 'n'), 're': ('blade', 62, 46, 27, 1, 'n'), 'mi': ('blade', 62, 31, 0, 1, 'n'),
 'fa': ('fa', 60, 24, 0, 1, 'n'), 'so': ('so', 62, 39, 0, 1, 'n'), 'la': ('la', 58, 24, 0, 1, 'n'), 'ti': ('ti', 62, 46, 0, 1, 'n'),
 'di': ('fist', 56, 42, 28, 1, 'u'), 'ri': ('blade', 50, 43, 52, 1, 'u'), 'fi': ('fa', 60, 40, 0, -1, 'u'),
 'si': ('si', 60, 47, 14, 1, 'u'), 'li': ('la', 58, 40, 0, -1, 'u'),
 'te': ('ti', 62, 18, 0, -1, 'd'), 'le': ('la', 46, 16, -34, 1, 'd'), 'se': ('so', 60, 30, -30, 1, 'd'),
 'me': ('blade', 60, 19, -27, 1, 'd'), 'ra': ('bladeT', 62, 40, 27, 1, 'd'),
}
ORDER = ['do', 'di', 'ra', 're', 'ri', 'me', 'mi', 'fa', 'fi', 'se', 'so', 'si', 'le', 'la', 'li', 'te', 'ti']
NAMES = {'do': 'do', 're': 're', 'mi': 'mi', 'fa': 'fa', 'so': 'so', 'la': 'la', 'ti': 'ti', 'di': 'di (raised do)', 'ri': 'ri (raised re)',
         'fi': 'fi (raised fa)', 'si': 'si (raised so)', 'li': 'li (raised la)', 'te': 'te (lowered ti)', 'le': 'le (lowered la)',
         'se': 'se (lowered so)', 'me': 'me (lowered mi)', 'ra': 'ra (lowered re)'}
W_OUT, W_IN = 2.6, 1.7
CUFF = 'M17.4 -6.2 C19.2 -2.2 19.2 3 17.4 7'   # the cuff: one arc of the Garden's corner curl
DX = -3

def inner(name, cls=True):
    b, x, y, r, f, k = SIGNS[name]
    sil, lines = BASE[b]
    t = f'translate({x + DX} {y})' + (f' rotate({r})' if r else '') + (' scale(1 -1)' if f < 0 else '')
    g = f'<g transform="{t}" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round">'
    g += f'<path d="{sil}" fill="currentColor" fill-opacity=".1" stroke-width="{W_OUT}"/>'
    g += f'<path d="{" ".join(lines)} {CUFF}" stroke-width="{W_IN}"/></g>'
    return g

def svg(name, extra=''):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 64" role="img" aria-label="{NAMES[name]} hand sign"{extra}>'
            f'{inner(name)}</svg>')

if __name__ == '__main__':
    OUT.mkdir(exist_ok=True)
    for n in ORDER:
        (OUT / f'{n}.svg').write_text(svg(n) + '\n')
    print(len(ORDER), 'signs written')
