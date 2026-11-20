"""Content lint (charter regression suite 8). No browser needed.
Run: python3 tests/content_lint.py <repo dir>      Prints a JSON report; exits 1 on any failure.

 1. US terms (L63): no US term on its own, for every pair in the shared term list (cadences, note and rest values, bar/measure,
    stave/staff, tone/semitone), in index.html and scores/meta.json; ordinary "half", "whole", "measure" (verb) and "staff"
    (people) are not flagged. The lint's own positive and negative cases run first.
 2. censor terms: no radio-edit / clean-version / instrumental-excerpt style advice in any song `suitability` string
 3. sources: every song entry has two sources, or one authoritative source (a URL); entries with no recorded
    sources are the known exceptions below (open question OQ6) and are counted, not failed
 3b. source links: every rendered source href is a bare URL (no spaces); the note text is shown beside it
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

report = {'censor_terms': {'failures': []},
          'sources': {'failures': []}, 'source_links': {'failures': []}, 'credits': {'failures': []}}


def line_of(text, pos):
    return text.count('\n', 0, pos) + 1


# ---------- 1. US terms (L63, IC_TERMS_048 S5): no US term on its own ----------
# Every term pair in the shared list (cadences, note and rest values, bar/measure, stave/staff, tone/semitone) is checked, in index.html
# and scores/meta.json. A US term is allowed only where it is labelled as the US term: inside a "(US: ...)" / "[US: ...]" bracket, in the
# term list's us:/usp: fields, straight after "US" ("the US half cadence", "= US authentic"), or in a code comment. Ordinary English is
# not a US term: "half" and "whole" count only with note/rest/step/cadence; "measure" only as a counted noun ("measure 4", "two measures",
# "the next measure"), never the verb; "staff" only in a music sense ("the treble staff", "staff lines"), never people ("staff room").
US_ALONE = re.compile(
    r"\bauthentic\b|\bdeceptive\b|\bhalf[ -]cadences?\b"
    r"|\b(?:quarter|eighth|sixteenth|half|whole)[ -](?:notes?|rests?)\b"
    r"|\b(?:whole|half)[ -]steps?\b"
    r"|\bstaffs\b|\bstaff(?=\s+(?:lines?|notation|position|paper)\b)"
    r"|\b(?:the|a|treble|bass|grand|alto|tenor|each|one|single|five-line|same|top|bottom|lower|upper)\s+staff\b(?!\s+(?:room|members?|meetings?|development|notes))"
    r"|\bmeasures?\s+\d|\b\d+\s+measures?\b"
    r"|\b(?:per|each|every|this|that|next|last|first|final|one|two|three|four|eight|twelve|sixteen|the|a)\s+measures?\b(?!\s+(?:of|the|every|each|how|a|an|it|its|your)\b)",
    re.I)


def us_allowed(text, start):
    ls = text.rfind('\n', 0, start) + 1
    before = text[ls:start]
    for o, c in (('(US', ')'), ('[US', ']')):        # inside a US bracket on the same line
        i = before.rfind(o)
        if i != -1 and c not in before[i:]:
            return True
    if re.search(r"\bus[p]?:'[^']*$", before):        # the term list's US field
        return True
    if re.search(r"\bUS:?\s+'?(?:imperfect\s+|Phrygian\s+)?$", before):   # "the US half cadence", "= US authentic", "US 'imperfect authentic'"
        return True
    # a code comment: // on this line (not a URL's ://), or inside /* ... */ or <!-- ... -->
    if re.search(r"(?:^|[\s;,{}()])//(?!/)", before.replace('://', ':__')):
        return True
    for o, c in (('/*', '*/'), ('<!--', '-->')):
        i = text.rfind(o, 0, start)
        if i != -1 and text.find(c, i) > start:
            return True
    return False


def us_alone(text):
    return [m for m in US_ALONE.finditer(text) if not us_allowed(text, m.start())]


# the lint's own cases: each must be found (or not) exactly as listed
US_CASES = [('Play a quarter note.', 1), ('Count measure 4 again.', 1), ('Two measures later.', 1), ('Write it on the treble staff.', 1),
            ('A deceptive cadence.', 1), ('An authentic close.', 1), ('A half cadence.', 1), ('Go up a whole step.', 1), ('An eighth rest.', 1),
            ('Draw the staff lines.', 1), ('Both staffs.', 1),
            ('Half the class hears it.', 0), ('Measure every interval.', 0), ('Ask the teaching staff.', 0), ('Meet in the staff room.', 0),
            ('The whole phrase.', 0), ('A whole-tone scale.', 0), ('Half-diminished.', 0), ('Take a measure of the gap.', 0),
            ('A crotchet (US: quarter note).', 0), ('an imperfect cadence [US: half cadence] in minor', 0), ("{k:'minim',us:'half note'}", 0),
            ('Imperfect = US half', 0), ("US 'imperfect authentic' is still a perfect cadence; the Australian imperfect cadence is the US half cadence.", 0),
            ('x=1; // a whole note here', 0), ('/* the staff */', 0), ('see https://example.org//quarter-note', 1)]
report['us_terms'] = {'failures': [], 'cases_checked': len(US_CASES)}
for s, n in US_CASES:
    if len(us_alone(s)) != n:
        report['us_terms']['failures'].append({'lint case': s, 'expected': n, 'found': [m.group(0) for m in us_alone(s)]})
# a US bracket gives the whole US term: "(US: half)" or "(US: deceptive)" alone is a shortened term (L8)
US_SHORT = re.compile(r'[(\[]US: (?:authentic|half|deceptive)\s*[)\];,]|\((?:half|authentic|deceptive)\)')
for s, n in (('imperfect cadence (US: half).', 1), ('V7/vi → IV (US: deceptive) follows', 1), ('(US: half cadence)', 0), ('(US: half step, H)', 0),
             ('(US: imperfect authentic)', 0), ('Imperfect (half) cadence (ends on V)', 1), ('(half the class)', 0)):
    if len(US_SHORT.findall(s)) != n:
        report['us_terms']['failures'].append({'lint case (short)': s, 'expected': n})
for name, text in (('index.html', INDEX), ('scores/meta.json', META)):
    for m in US_SHORT.finditer(text):
        ls = text.rfind('\n', 0, m.start()) + 1
        report['us_terms']['failures'].append({'file': name, 'line': line_of(text, m.start()), 'why': 'shortened US term in a bracket',
                                               'text': text[max(ls, m.start() - 50):m.end() + 30].strip()})
for name, text in (('index.html', INDEX), ('scores/meta.json', META)):
    for m in us_alone(text):
        ls = text.rfind('\n', 0, m.start()) + 1
        report['us_terms']['failures'].append({'file': name, 'line': line_of(text, m.start()),
                                               'text': text[max(ls, m.start() - 50):m.end() + 30].strip()})

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
# 0.48 (E): an entry with exactly one source that is a Hooktheory page must say so on the card (where-text) and in the source note.
for q, x in entries:
    srcs = x.get('sources') or []
    if len(srcs) == 1 and 'hooktheory.com' in str(srcs[0]):
        if 'as transcribed on hooktheory' not in str(x.get('where', '')).lower():
            report['sources']['failures'].append({'song': x['song'], 'artist': x['artist'], 'why': 'single Hooktheory source, where-text lacks "as transcribed on Hooktheory"'})
        if 'single community transcription' not in str(srcs[0]):
            report['sources']['failures'].append({'song': x['song'], 'artist': x['artist'], 'why': 'single Hooktheory source, source note lacks "a single community transcription"'})
# Nothing Else Matters add9 placement rests on Hooktheory alone (the second source does not give the placement).
for q, x in entries:
    if x['song'] == 'Nothing Else Matters' and q == 'add9' and 'as transcribed on hooktheory' not in x['where'].lower():
        report['sources']['failures'].append({'song': x['song'], 'why': 'add9 placement not labelled as Hooktheory-only'})
report['sources']['known_exceptions_count'] = len(exceptions_seen)
report['sources']['known_exceptions_listed'] = len(KNOWN_NO_SOURCES)
report['sources']['known_exceptions_now_sourced'] = sorted(' / '.join(k) for k in KNOWN_NO_SOURCES - exceptions_seen)

def href_of(h):
    m = re.search(r'href="([^"]*)"', h)
    return m.group(1).replace('&amp;', '&') if m else None


# ---------- 3b. rendered source links (0.48 SRCFIX): every href is a bare URL, the note is shown as text ----------
# Runs the page's own srcItem() under node on every source string in SONGS and SCSONGS.
import subprocess
fm = re.search(r'^function srcItem\(u\)\{.*$', INDEX, re.M)
em = re.search(r'^const esc=.*$', INDEX, re.M)
sm = re.search(r'^let SCSONGS=(\{.*\});?\s*$', INDEX, re.M)
if not (fm and em and sm):
    report['source_links']['failures'].append('srcItem / esc / SCSONGS not found')
else:
    js = (em.group(0) + '\n' + fm.group(0) + '\nconst S=' + sm.group(1) + ';const T=' + json.dumps(SONGS) + ';\n'
          'const all=[];for(const D of [T,S])for(const k in D)for(const x of D[k])for(const u of (x.sources||[]))all.push(u);\n'
          'console.log(JSON.stringify(all.map(u=>[u,srcItem(u)])))')
    try:
        out = json.loads(subprocess.run(['node', '-e', js], capture_output=True, text=True, check=True).stdout)
        report['source_links']['rendered'] = len(out)
        for u, h in out:
            for href in re.findall(r'href="([^"]*)"', h):
                if not re.fullmatch(r'https?://[^\s"]+', href):
                    report['source_links']['failures'].append({'source': u, 'href': href})
            mu = re.match(r'(.*?)(https?://\S+)(.*)$', u, re.S)
            if mu:
                if href_of(h) != mu.group(2):
                    report['source_links']['failures'].append({'source': u, 'why': 'href is not the first URL token'})
                for part in (mu.group(1).strip().rstrip(':'), mu.group(3).strip()):
                    if len(part) > 30 and part.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;') not in h:
                        report['source_links']['failures'].append({'source': u, 'why': 'note text not shown'})
            elif 'href=' in h:
                report['source_links']['failures'].append({'source': u, 'why': 'link made from a source with no URL'})
    except Exception as e:
        report['source_links']['failures'].append(f'node check failed: {e}')

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

report['passed'] = not any(report[k]['failures'] for k in ('us_terms', 'censor_terms', 'sources', 'source_links', 'credits', 'lyric_words'))
print(json.dumps(report, ensure_ascii=False, indent=1))
sys.exit(0 if report['passed'] else 1)
