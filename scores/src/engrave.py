"""Engrave the ten Analysis-room scores with Verovio from the licensed Humdrum sources in this folder.

Run from the repo root:   python3 scores/src/engrave.py          (needs: pip install verovio==6.4.1)

For each score it writes three engravings, all shown 1:1 (never stretched):
  scores/<key>.svg      desktop: Verovio scale 40 (staff-space 7.2 px), 880 px systems
  scores/<key>.t.svg    tablet:  scale 40, 600 px systems (panels narrower than 880 px, wider than a phone)
  scores/<key>.p.svg    phone:   scale 33 (staff-space 5.94 px), 308 px systems, spacingLinear 0.2, spacingNonLinear 0.5
House standard (SPEC, "House engraving standard"): Bravura; Verovio's embedded stylesheet stripped (colours and line
weights come from the app's CSS on .vrv); Humdrum instrument-name tokens blanked (no voice labels, no first-system
indent); chorales as closed score on a grand staff (Humdrum filter satb2gs); stave gap 6 staff-spaces (8 for the
chorales); between systems 9 staff-spaces plus room for the overlay rows the app draws; text set in final px.

The app's analysis data (scores/meta.json) addresses notes and bars by the ids Verovio gives the UNFILTERED source
(note-L<line>F<field>, measure-L<line>). satb2gs rewrites the file, so for the chorales every note and bar of the
grand-staff engraving is given back its canonical id, matched by onset, pitch and duration. The script stops with an
error if any id cannot be matched, if the bar count changes, or if the notes no longer match meta.json's events.
"""
import json, re, sys, collections, pathlib
import verovio

HERE = pathlib.Path(__file__).resolve().parent
SCORES = HERE.parent
SRC = {  # key: (file, repo, revision the app's ids were made from; see scores/src/README.md)
    'chorale': 'chor001.krn', 'ohaupt': 'chor080.krn', 'jesu': 'chor138.krn',
    'k545': 'sonata15-1.krn', 'k331a': 'sonata11-1a.krn', 'k331d': 'sonata11-1d.krn',
    'maple': 'mapleleaf.krn', 'entertainer': 'entertainer.krn',
    'chopin7': '028-1-BH-007.krn', 'chopin20': '028-1-BH-020.krn'}
CHORALES = {'chorale', 'ohaupt', 'jesu'}
VARIANTS = {  # suffix: (scale, system width px, extra options)
    '': (40, 880, {}),
    '.t': (40, 600, {}),
    '.p': (33, 308, {'spacingLinear': 0.2, 'spacingNonLinear': 0.5}),
}
LEFT_PX = 22  # room for the brace / bracket left of the staves (never clipped)
# overlay rows the app draws (final px): form rule + label above the system, harmony row, cadence-tag row below
ROW_ABOVE_FORM, ROW_HARM, ROW_CAD = 24, 24, 20
# final-px text sizes (SPEC, Text table)
PX = {'mNum': 11, 'tempo': 14, 'dir': 14, 'ending': 12, 'reh': 12, 'other': 12}


def prep(key, text):
    """Blank instrument-name tokens in place (same line count, so ids stay put); grand staff for the chorales."""
    out = []
    for ln in text.split('\n'):
        if ln.startswith('*') and not ln.startswith('**') and '*I' in ln:  # *I"name, *I'abbr, *Ipiano, *ICklav ...
            ln = '\t'.join('*' if t.startswith('*I') else t for t in ln.split('\t'))
        out.append(ln)
    t = '\n'.join(out)
    return t


def toolkit(opts, data):
    tk = verovio.toolkit()
    tk.setOptions(opts)
    if not tk.loadData(data):
        raise SystemExit('Verovio could not load the data')
    return tk


def note_table(tk):
    """id -> (onset ms, midi pitch, duration ms) for every sounding note."""
    tm = tk.renderToTimemap({'includeRests': False})
    on, out = {}, {}
    for e in tm:
        for i in e.get('on', []):
            on[i] = e['tstamp']
        for i in e.get('off', []):
            if i in on:
                out[i] = (round(on[i]), tk.getMIDIValuesForElement(i)['pitch'], round(e['tstamp'] - on[i]))
    return out


def id_map(canon_tk, gs_tk, canon_svg, gs_svg):
    """map grand-staff ids -> canonical ids (notes by onset/pitch/duration, bars by order)."""
    a, b = note_table(canon_tk), note_table(gs_tk)
    pool = collections.defaultdict(list)
    for i, k in sorted(a.items()):
        pool[k].append(i)
    m = {}
    for i, k in sorted(b.items()):
        if not pool.get(k):
            raise SystemExit(f'no canonical note for {i} {k}')
        m[i] = pool[k].pop(0)
    if any(pool.values()):
        raise SystemExit('canonical notes left unmatched: ' + str([v for v in pool.values() if v][:5]))
    ma = re.findall(r'data-id="(measure-[^"]+)"', canon_svg)
    mb = re.findall(r'data-id="(measure-[^"]+)"', gs_svg)
    if len(ma) != len(mb):
        raise SystemExit(f'bar count changed under satb2gs: {len(ma)} -> {len(mb)}')
    m.update(dict(zip(mb, ma)))
    return m


def base_opts(scale, width, extra, spacing_system, staff_gap, margins):
    o = {'svgHtml5': True, 'svgRemoveXlink': True, 'font': 'Bravura', 'scale': scale,
         'pageWidth': round(width * 100 / scale), 'pageMarginLeft': round(LEFT_PX * 100 / scale), 'pageMarginRight': 0,
         'pageMarginTop': round(margins[0] * 100 / scale), 'pageMarginBottom': round(margins[1] * 100 / scale),
         'svgFormatRaw': True,
         'pageHeight': 60000, 'adjustPageHeight': True, 'breaks': 'auto', 'header': 'none', 'footer': 'none',
         'spacingStaff': staff_gap, 'spacingSystem': spacing_system, 'justifyVertically': False,
         'mnumInterval': 0, 'minLastJustification': 0.8}
    o.update(extra)
    return o


def post(svg, scale, idm):
    """strip the embedded stylesheet, give canonical ids back, set text in final px."""
    svg = re.sub(r'<style[^>]*>.*?</style>', '', svg, flags=re.S)
    # NIFC editorial notes to the encoders (!LO:TX:...:problem) are not part of the score
    svg = re.sub(r'<g [^>]*class="dir problem"[^>]*>.*?</g>', '', svg, flags=re.S)
    # Verovio's stylesheet hid its expansion/section placeholders; with the stylesheet gone, remove them
    svg = re.sub(r'<g [^>]*class="[^"]*\bplaceholder\b[^"]*"[^>]*?(?:/>|>(?:<ellipse[^>]*/>)?</g>)', '', svg)
    if idm:
        svg = re.sub(r'data-id="([^"]+)"', lambda mm: f'data-id="{idm.get(mm.group(1), mm.group(1))}"', svg)
    upx = scale / 100 / 10  # screen px per SVG user unit inside the definition-scale viewBox (unit 10 per px at 100)

    def resize(mm):
        size = PX.get(mm.group(2).split()[0], PX['other'])
        return mm.group(1) + re.sub(r'<tspan font-size="\d+px"', f'<tspan font-size="{round(size / upx)}px"', mm.group(3))
    svg = re.sub(r'(<g [^>]*class="(mNum[^"]*|tempo|dir|ending|reh)"[^>]*>)(.*?</g>)', resize, svg, flags=re.S)
    return svg


def verify(key, svg, meta, tk_canon):
    m = meta[key]
    want_bars = [x[1] for x in m['measures']]
    got_bars = re.findall(r'data-id="(measure-[^"]+)"', svg)
    if got_bars != want_bars:
        raise SystemExit(f'{key}: bars differ from meta.json ({len(got_bars)} vs {len(want_bars)})')
    ids = set(re.findall(r'data-id="(note-[^"]+)"', svg))
    need = {x['id'] for x in m.get('labels', [])} | {x['id'] for x in m.get('cads', [])}
    miss = need - ids
    if miss:
        raise SystemExit(f'{key}: overlay anchors missing from the engraving: {sorted(miss)[:5]}')
    ev = sorted(note_table(tk_canon).values())
    me = sorted(tuple(x) for x in m['events'])
    pool = collections.defaultdict(list)  # meta.json rounds onsets down, Verovio to nearest: allow 2 ms
    for x in me:
        pool[x[1]].append(x)
    bad = []
    for a in ev:
        hit = next((b for b in pool[a[1]] if abs(a[0] - b[0]) <= 2 and abs(a[2] - b[2]) <= 2), None)
        if hit is None:
            bad.append(a)
        else:
            pool[a[1]].remove(hit)
    if len(ev) != len(me) or bad:
        raise SystemExit(f'{key}: notes differ from meta.json events: {len(ev)} vs {len(me)}, first diffs {bad[:3]}')
    return len(got_bars), len(ids)


def main():
    meta = json.load(open(SCORES / 'meta.json'))
    keys = sys.argv[1:] or list(SRC)
    report = {}
    for key in keys:
        raw = prep(key, (HERE / SRC[key]).read_text())
        m = meta[key]
        above = ROW_ABOVE_FORM if m['sections'] else 0
        below = (ROW_HARM if m['labels'] else 0) + (ROW_CAD if m['cads'] else 0)
        staff_gap = 16 if key in CHORALES else 12
        for suf, (scale, width, extra) in VARIANTS.items():
            half_space_px = 9 * scale / 100  # one MEI unit (half a staff-space) in px
            spacing_system = 18 + round((above + below) / half_space_px)
            opts = base_opts(scale, width, extra, spacing_system, staff_gap, (max(14, 8 + above), 8 + below))
            tk_c = toolkit(opts, raw)
            canon = tk_c.renderToSVG(1)
            if tk_c.getPageCount() != 1:
                raise SystemExit(f'{key}{suf}: more than one page')
            idm = None
            svg = canon
            if key in CHORALES:
                tk_g = toolkit(opts, raw + ('' if raw.endswith('\n') else '\n') + '!!!filter: satb2gs\n')
                svg = tk_g.renderToSVG(1)
                idm = id_map(tk_c, tk_g, canon, svg)
            svg = post(svg, scale, idm)
            bars, notes = verify(key, svg, meta, tk_c)
            (SCORES / f'{key}{suf}.svg').write_text(svg)
            wh = re.search(r'<svg width="(\d+)px" height="(\d+)px"', svg)
            report[f'{key}{suf}'] = {'bars': bars, 'notes': notes, 'width': int(wh.group(1)), 'height': int(wh.group(2)),
                                    'systems': svg.count('class="system"'), 'kB': len(svg) // 1024}
            print(key + suf, report[key + suf])
    return report


if __name__ == '__main__':
    main()
