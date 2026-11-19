"""Content lint (charter regression suite 8). No browser needed.
Run: python3 tests/content_lint.py <repo dir>      Prints a JSON report; exits 1 on any failure.

 1. cadence names: "half cadence" and "authentic" only with the NSW term first and the US term in brackets
    (index.html and scores/meta.json)
 2. censor terms: no radio-edit / clean-version / instrumental-excerpt style advice in any song `suitability` string
 3. sources: every song entry has two sources, or one authoritative source (a URL); entries with no recorded
    sources are the known exceptions below (open question OQ6) and are counted, not failed
 4. credits: NOTICE.md names every third-party source; the footer has a Credits link; the Credits panel (details#credits,
    not the footer line) holds the sound credits and
    include the score and hand-sign credits
"""
import sys, re, json, pathlib

REPO = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
INDEX = (REPO / 'index.html').read_text(encoding='utf-8')
META = (REPO / 'scores' / 'meta.json').read_text(encoding='utf-8')

# Known entries with no recorded sources (OQ6, Justin's open question): (song, artist)
KNOWN_NO_SOURCES = set()  # OQ6 closed (L69): every song entry now has real source URLs

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
    if good and not any('already verified' in str(u) for u in srcs):
        continue
    if any('already verified' in str(u) for u in srcs):
        report['sources']['failures'].append({'song': x['song'], 'artist': x['artist'], 'sources': srcs, 'why': 'placeholder source text'})
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
        'Poiret One', 'SIL', 'OFL', 'Verovio', 'LGPL', 'non-commercial',
        "First Editions of Fryderyk Chopin's Music", 'Copyright 2017-2021 The Fryderyk Chopin Institute (https://nifc.pl)',
        'https://chopinscores.org', 'Copyright (C) 2009 Craig Stuart Sapp', 'Copyright (C) 2004-2018 Craig Stuart Sapp',
        'Copyright (C) 2004-2021 Craig Stuart Sapp', 'licenses/by/3.0/us/', 'Leipzig', 'Bravura',
        'permission confirmed by Justin Ossher', 'github.com/craigsapp/bach-370-chorales',
        'github.com/craigsapp/mozart-piano-sonatas', 'github.com/craigsapp/joplin', 'chopin-first-editions']
nt = REPO / 'NOTICE.md'
if not nt.exists():
    report['credits']['failures'].append('NOTICE.md missing')
else:
    notice = nt.read_text(encoding='utf-8')
    for t in NEED:
        if t.lower() not in notice.lower() and not (t == 'OFL' and 'open font licence' in notice.lower()):
            report['credits']['failures'].append(f'NOTICE.md does not mention "{t}"')
ftm = re.search(r'<footer>(.*?)</footer>', INDEX, re.S)
# R7 (0.48): the footer line no longer carries the sample-library credits; the Credits panel (details#credits) holds them all.
fm = re.search(r'<details[^>]*id="credits"[^>]*>(.*?)</details>', INDEX, re.S)
if not ftm:
    report['credits']['failures'].append('footer not found')
elif not fm:
    report['credits']['failures'].append('Credits panel (details#credits) not found')
else:
    foot = fm.group(1)
    line = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', ftm.group(1).replace(fm.group(0), '')))
    for t in ['FluidR3', 'Frank Wen', 'CC BY 3.0', 'VCSL', 'Steinway']:
        if t in line:
            report['credits']['failures'].append(f'footer line still carries the sample credit "{t}" (it belongs in the Credits panel)')
    if not re.search(r'<summary[^>]*>\s*Credits\s*</summary>|<a [^>]*>\s*Credits\s*</a>|<button[^>]*>\s*Credits\s*</button>', ftm.group(1)):
        report['credits']['failures'].append('footer has no Credits link')
    for t in ['VCSL', 'Steinway B', 'CC0', 'FluidR3_GM', 'Frank Wen', 'CC BY 3.0', 'midi-js-soundfonts']:
        if t not in foot:
            report['credits']['failures'].append(f'Credits panel does not mention "{t}"')
    text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', foot.replace('<br>', ' '))).replace('&amp;', '&')
    for t in ['Sapp', 'Chopin Institute', 'NIFC', 'Curwen', 'Kodály Music Education Institute of Australia', 'KMEIA', 'used with permission',
              'CC BY-NC-SA 4.0', 'CC BY 4.0', 'Verovio',
              "First Editions of Fryderyk Chopin's Music", 'Copyright 2017-2021 The Fryderyk Chopin Institute (https://nifc.pl)',
              'https://chopinscores.org', 'Copyright (C) 2009 Craig Stuart Sapp', 'Copyright (C) 2004-2018 Craig Stuart Sapp',
              'Copyright (C) 2004-2021 Craig Stuart Sapp', 'Leipzig', 'Bravura']:
        if t not in text:
            report['credits']['failures'].append(f'on-screen credits do not mention "{t}"')

# on-screen links, README pointer, meta.json licence on every score
for u in ['creativecommons.org/licenses/by-nc-sa/4.0/', 'creativecommons.org/licenses/by/4.0/', 'creativecommons.org/licenses/by/3.0/us/',
          'creativecommons.org/publicdomain/zero/1.0/', 'github.com/craigsapp/bach-370-chorales', 'github.com/craigsapp/mozart-piano-sonatas',
          'github.com/craigsapp/joplin', 'github.com/pl-wnifc/humdrum-chopin-first-editions']:
    if fm and u not in fm.group(1):
        report['credits']['failures'].append(f'on-screen credits have no link to {u}')
rd = REPO / 'README.md'
if not rd.exists() or 'NOTICE.md' not in rd.read_text(encoding='utf-8'):
    report['credits']['failures'].append('README.md does not point to NOTICE.md')
try:
    for k, v in json.loads(META).items():
        if 'src' in v and not re.search(r'Analysis layer[^.]*\(CC BY(-NC-SA)? 4\.0\)|Form layer[^.]*\(CC BY(-NC-SA)? 4\.0\)', v['src']):
            report['credits']['failures'].append(f'meta.json {k}: src does not state the annotation layer licence')
except Exception as e:
    report['credits']['failures'].append(f'meta.json unreadable: {e}')

# lyric lint: content-warning text must describe, not quote (no quoted words, no known lyric words)
WARN_TEXT = []
wm = re.search(r'const WARN=\{(.*?)\};', INDEX, re.S)
if wm:
    WARN_TEXT += re.findall(r"n:'((?:[^'\\]|\\.)*)'", wm.group(1))
WARN_TEXT += [str(x.get('suitability') or '') for _, x in entries]
for mm in re.finditer(r'"content": \{[^{}]*?"note": "((?:[^"\\]|\\.)*)"', INDEX):
    WARN_TEXT.append(mm.group(1))
QUOTED = re.compile(r"(^|[\s(])(['\"\u2018\u201c])[^'\"\u2019\u201d]{2,}(['\"\u2019\u201d])(?![A-Za-z])")
LYRICWORD = re.compile(r'libido|mulatto|pissed|deaf, dumb|white boy|\bdamn\b', re.I)
report['lyric_words'] = {'failures': []}
for s in WARN_TEXT:
    if QUOTED.search(s) or LYRICWORD.search(s):
        report['lyric_words']['failures'].append(s)

report['passed'] = not any(report[k]['failures'] for k in ('cadence_names', 'censor_terms', 'sources', 'credits', 'lyric_words'))
print(json.dumps(report, ensure_ascii=False, indent=1))
sys.exit(0 if report['passed'] else 1)
