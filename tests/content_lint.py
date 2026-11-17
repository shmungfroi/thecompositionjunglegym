"""Content lint (charter regression suite 8). No browser needed.
Run: python3 tests/content_lint.py <repo dir>      Prints a JSON report; exits 1 on any failure.

 1. cadence names: "half cadence" and "authentic" only with the NSW term first and the US term in brackets
    (index.html and scores/meta.json)
 2. censor terms: no radio-edit / clean-version / instrumental-excerpt style advice in any song `suitability` string
 3. sources: every song entry has two sources, or one authoritative source (a URL); entries with no recorded
    sources are the known exceptions below (open question OQ6) and are counted, not failed
 4. credits: NOTICE.md names every third-party source; the footer has a Credits link; the on-screen credits
    include the score and hand-sign credits
"""
import sys, re, json, pathlib

REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
INDEX = (REPO / 'index.html').read_text(encoding='utf-8')
META = (REPO / 'scores' / 'meta.json').read_text(encoding='utf-8')

# Known entries with no recorded sources (OQ6, Justin's open question): (song, artist)
KNOWN_NO_SOURCES = {
    ('Johnny B. Goode', 'Chuck Berry'),
    ('Sk8er Boi', 'Avril Lavigne'),
    ('Smells Like Teen Spirit', 'Nirvana'),
    ('Stick It to the Man', 'School of Rock the Musical cast (Andrew Lloyd Webber)'),
    ('Enter Sandman', 'Metallica'),
    ('Sweet Home Chicago', 'Robert Johnson / The Blues Brothers'),
    ('Twist and Shout', 'The Beatles'),
    ('Heartbreak Hotel', 'Elvis Presley'),
    ('Sweet Georgia Brown', 'Ben Bernie, Maceo Pinkard & Kenneth Casey'),
    ('Nothing Else Matters', 'Metallica'),
    ('Champagne Supernova', 'Oasis'),
    ('The Girl from Ipanema', 'Stan Getz & João Gilberto (with Astrud Gilberto)'),
    ('I Loves You, Porgy', 'George Gershwin / DuBose Heyward (Porgy and Bess)'),
}

report = {'cadence_names': {'failures': []}, 'censor_terms': {'failures': []},
          'sources': {'failures': []}, 'credits': {'failures': []}}


def line_of(text, pos):
    return text.count('\n', 0, pos) + 1


# ---------- 1. cadence names ----------
CAD = re.compile(r'half[ -]?cadence|authentic', re.I)
for name, text in (('index.html', INDEX), ('scores/meta.json', META)):
    for m in CAD.finditer(text):
        ls = text.rfind('\n', 0, m.start()) + 1
        before = text[ls:m.start()]
        after = text[m.end():text.find('\n', m.end()) if '\n' in text[m.end():] else len(text)]
        ok = False
        if m.group(0).lower().startswith('half') and before.endswith('Phrygian '):
            ok = True                                   # "Phrygian half cadence" is a proper name
        # the US-term field of a cadence record: rendered as "<term> (US)"
        elif re.search(r"\bus:'[^']*$", before):
            ok = True
        else:
            # inside a bracket that follows an NSW term, e.g. "Perfect (authentic)", "(US: imperfect authentic)"
            op = before.rfind('(')
            if op != -1 and ')' not in before[op:]:
                lead = re.sub(r'<[^>]+>', '', before[max(0, op - 60):op])
                if re.match(r'\(US\b', before[op:]) or re.search(r'(perfect|imperfect|plagal|interrupted|cadence)\W*$', lead, re.I):
                    ok = True
        if not ok:
            report['cadence_names']['failures'].append(
                {'file': name, 'line': line_of(text, m.start()), 'text': (before[-50:] + m.group(0) + after[:30]).strip()})

# ---------- song data ----------
m = re.search(r'^const SONGS=(\{.*\});?\s*$', INDEX, re.M)
SONGS = json.loads(m.group(1)) if m else {}
entries = [(q, x) for q, v in SONGS.items() for x in v]
report['song_entries'] = len(entries)
if not entries:
    report['sources']['failures'].append('SONGS data not found')

# ---------- 2. censor terms ----------
CENSOR_TERMS = re.compile(
    r'radio[- ]edit|clean (radio )?(version|edit)|edited version|instrumental( excerpt| version| only)?|'
    r'shorter edit|skip (the|that|this|it)|play only|only play|intro only|just the intro|use (the )?riff|'
    r'use this track only|check with your school|check the lyric sheet|lyric sheet|handle with care|'
    r'consider an?|\bmute\b|bleep|censor|swap (in|for)|rather than the lyric|^\s*(mild )?flag\b', re.I)
for q, x in entries:
    s = str(x.get('suitability') or '')
    hit = CENSOR_TERMS.search(s)
    if hit:
        report['censor_terms']['failures'].append({'song': x['song'], 'artist': x['artist'], 'term': hit.group(0), 'text': s})

# ---------- 3. sources ----------
exceptions_seen = set()
for q, x in entries:
    key = (x['song'], x['artist'])
    srcs = x.get('sources') or []
    urls = [u for u in srcs if re.match(r'https?://', str(u))]
    good = len(srcs) >= 2 and len(urls) >= 1 or len(urls) >= 1 and len(srcs) == 1
    if good:
        continue
    if key in KNOWN_NO_SOURCES:
        exceptions_seen.add(key)
        continue
    report['sources']['failures'].append({'song': x['song'], 'artist': x['artist'], 'sources': srcs})
report['sources']['known_exceptions_count'] = len(exceptions_seen)
report['sources']['known_exceptions_listed'] = len(KNOWN_NO_SOURCES)
report['sources']['known_exceptions_now_sourced'] = sorted(' / '.join(k) for k in KNOWN_NO_SOURCES - exceptions_seen)

# ---------- 4. credits ----------
NEED = ['Bach chorales', 'Mozart', 'Joplin', 'Craig Stuart Sapp', 'CC BY-NC-SA 4.0', 'Chopin', 'Op. 28 Nos. 7 and 20',
        'Fryderyk Chopin Institute', 'NIFC', 'CC BY 4.0', 'VCSL', 'CC0', 'FluidR3_GM', 'Frank Wen', 'CC BY 3.0', 'Curwen',
        'Kodály Music Education Institute of Australia', 'KMEIA', '2003', 'VexFlow', 'MIT', 'jsDelivr', 'Outfit',
        'Poiret One', 'SIL', 'OFL', 'Verovio', 'LGPL', 'non-commercial']
nt = REPO / 'NOTICE.md'
if not nt.exists():
    report['credits']['failures'].append('NOTICE.md missing')
else:
    notice = nt.read_text(encoding='utf-8')
    for t in NEED:
        if t.lower() not in notice.lower() and not (t == 'OFL' and 'open font licence' in notice.lower()):
            report['credits']['failures'].append(f'NOTICE.md does not mention "{t}"')
fm = re.search(r'<footer>(.*?)</footer>', INDEX, re.S)
if not fm:
    report['credits']['failures'].append('footer not found')
else:
    foot = fm.group(1)
    if not re.search(r'<summary[^>]*>\s*Credits\s*</summary>|<a [^>]*>\s*Credits\s*</a>|<button[^>]*>\s*Credits\s*</button>', foot):
        report['credits']['failures'].append('footer has no Credits link')
    text = re.sub(r'<[^>]+>', ' ', foot)
    for t in ['Sapp', 'Chopin Institute', 'NIFC', 'Curwen', 'Kodály Music Education Institute of Australia', 'KMEIA', 'used with permission',
              'CC BY-NC-SA 4.0', 'CC BY 4.0', 'Verovio']:
        if t not in text:
            report['credits']['failures'].append(f'on-screen credits do not mention "{t}"')

report['passed'] = not any(report[k]['failures'] for k in ('cadence_names', 'censor_terms', 'sources', 'credits'))
print(json.dumps(report, ensure_ascii=False, indent=1))
sys.exit(0 if report['passed'] else 1)
