# Ear Lab ladders 0.49: engine API (for the desk, picker, palette and ladder drawing)

Engine builder (Opus), 21 Nov 2026, branch `049-ladder-eng`. Spec: `LADDER_REGISTER_049.md` (with section 8, Justin's answers L101–L104).
Everything below lives in one block of `index.html` between `EAR LAB LADDERS 0.49 · ENGINE` and `END EAR LAB LADDERS ENGINE`
(plus `LADM12`, the M12 data table, in the same block). Nothing in it draws: the visual UI is yours.

Units: **ticks, 420 to a crotchet** (rule U): semiquaver 105, quaver 210, dotted quaver 315, crotchet 420, dotted crotchet 630, minim 840,
dotted minim 1260, semibreve 1680, triplet quaver 140, quintuplet semiquaver 84, septuplet semiquaver 60.
Solfa: movable do, la-based minor, octave marks `,` and `'` against do = 60 + pc (C4–B4). Chromatic syllables (Justin's chart):
sharps `di ri fi si li`, flats `te le se me ra`.

---

## 1. Where it is wired in already

| app function | now |
|---|---|
| `earGen('mel', l)` / `earGen('rhy', l)` | `ladGenFresh` → `ladGenMel(l, r)` / `ladGenRhy(l, r)`; rhythm rung 1 keeps a no-repeat window of 30 (D1) |
| `earCheck()` | rhythm: `ladRhyMark(q, EAR.ans)`; melody: `ladMelMark(q, EAR.ans, {pivot: EAR.pivot})`. The full result is kept in `EAR.res.mark` |
| `earMark()` | also pushes readiness for `mel` and `rhy` (`ladRdPush`, D10) and saves |
| `earSched(q, variant)` | items with `q.barLen` (rhythm) and every melody item go to `ladSched` (except the old replay variants `q3 q5 q7 qab last pair frag ending`) |
| `EARSTAGE.mel` / `.rhy` | `[4,4,4,4,5,5,5,5,6,6,6,6]` / `[4,4,4,5,5,5,5,6,6,6]`; `earRungs(d)` = `[1..n]` replaces the hard-coded `[1,2,3]` in `earRungsShown` and `earHidden` |
| `EDR` rhythm row | `'4–6'` |
| `earCells(l)` | `ladRhyTiles(l)` (the rung's tiles, both families) |
| `RHYNAMES` | `= LADNAMES` (the nine 0.48 names unchanged); `RHYNAMES_KK = LADNAMES_KK`. The 0.48 rhythm desk now reads `ladNameTable()` (follows `EAR.names`) |
| `RCELL` | every ladder cell added in semiquaver units (tuplets fractional) so the 0.48 desk can still draw them; **new desks should use `LCELL` (ticks)** |
| `ESOL` | gains `di ri fi li ra me se le te` (the 0.48 melody desk can spell them) |
| `elRhyNote(t, d, m, gain=1)` | new optional `gain` (tuplet accents) |
| `elTitle(k)` | tile title: `ELTITLE[k]` (0.48 cells) or `LADTITLE[k]` |

Saved levels keep their number (register 0.3): melody 1→1, 2→2, 3→3 (the new rung 3 is the nearest content); rhythm 2→2, 3→3.
`EAR.st` (per drill) carries over; `EAR.rd` starts empty.

## 2. State and settings (`EAR`, saved in `cjg_ear`)

| field | values | meaning |
|---|---|---|
| `EAR.names` | `'k'` (default) / `'kk'` | Rhythm names: "Kodály names" / "Kodály with konnakol tuplets" (only the triplet changes: tri-o-la → ta-ki-ta; 5- and 7-tuplets show the konnakol names in both, D12). Show the option from R7. |
| `EAR.mod` | `'home'` (default) / `'move'` | M9: "Keep home do" / "Move do (mutation)" (D8, L102). The pivot ("Mutation here: so = do") is asked and marked only under `'move'`. |
| `EAR.pivot` | note index or `null` | the note the student marked as the mutation (M9, Move do); read by `earCheck` |
| `EAR.rd[drill][rung]` | array of 0/1, last 10 | readiness (D10) |

Call `earSave()` after changing any of them.

## 3. Items

### 3.1 Melody item (`ladGenMel(l, r, {wantNew})`, l = 1..12)

| field | |
|---|---|
| `d, l, lvl` | `'mel'`, the rung |
| `id` | distinct-item key (solfa + metre + cells + anacrusis + bass) |
| `key` | `{k: tonic pc, mode, do: do's pc}`; rungs 1–3 `{k: do, mode: 'maj', do}` (0.48 shape) |
| `mode` | `'maj' 'min' 'dor' 'mix'` |
| `modeName` | `'Dorian on re'` / `'Mixolydian on so'` / null (D7: show it above the stave) |
| `doMidi` | 60 + do (MR1) |
| `notes[]` | `{i, a, sol, s, o, midi, on, dur, bar}`: diatonic index, alter, solfa with octave marks, solfa base, octave, MIDI, onset and length in ticks (the anacrusis starts at 0), bar (0 = the anacrusis bar) |
| `a`, `midi`, `idx`, `n`, `range` | 0.48 fields: solfa strings, MIDI, indices, note count, ladder range `[lo, hi]` (do-relative diatonic) |
| `metre, cells, anac, anacCells, barLen` | rung 4 on: metre `'2/4' '3/4' '4/4' '6/8'`; cells by bar (the rhythm, `LCELL` keys); anacrusis length in ticks (0 = none); its cells; each bar's length (the last bar is shortened by the anacrusis, D9). Rungs 1–3: `cells = null`, `step = 0.65` s |
| `tempo` | crotchets a minute, 72–96 (dotted crotchet 48–64 in 6/8); null at rungs 1–3 |
| `new` | whether the item carries the rung's new thing (2/3, D2) |
| `info` | `{mode, var, home, ...}`: `var` = tune type / variant (`pent dia major natmin lapent harm melo dor mix te fi`, M9 `M-V M-vi m-III m-v`, `review:...`) |
| `aug2` | M7 harmonic minor: indices `i` where notes `i → i+1` are the fa–si augmented 2nd (at most one, D5): **show the gap visually** on the ladder and in the feedback |
| `chrom` | M10: indices of the inserted chromatic notes |
| M9 (modulating items): `kind, pivot, pivotWindow, readings, pivotNames, newKey` | kind; the true pivot's note index; `[first, last]` note indices where a marked pivot counts as right; `readings.home` (Keep home do: the old key's syllables, chromatic ones such as fi, ri) and `readings.move` (Move do: the key in force; from the pivot on, the new key's syllables); `pivotNames = [old, new]` (e.g. `['d', 'f,']`: write "d = f" under the pivot); `newKey = {do, mode}`; `newDoMidi` (old do + 7 for the dominant kinds, the old do for the relative ones). Melody range s,..d' in every kind (the new do sits a 5th above or a 4th below).
| M11: `bass[]` | `{on, dur, midi, i, a, sol, chord, sop}`: the bass line (one note per minim in 4/4, per bar in 3/4), its chord label (`I ii IV V vi` / `i ii°6 iv V VI`, `6` = first inversion) and the melody note above it. Grand staff; bass solfa under the lower stave; the ladder reprints two octaves lower |
| M12: `excerpt` | `{id, score, bars, ms: [start, end] in AN.meta[score].events, level, credit}`; notes are in the score's own register |

### 3.2 Rhythm item (`ladGenRhy(l, r, {wantNew})`, l = 1..10)

| field | |
|---|---|
| `d, l, lvl, id` | |
| `metre` | `'2/4' '3/4' '4/4' '6/8' '12/8' '5/4' '7/8'` |
| `grp` | 5/4 `[3,2]`/`[2,3]`, 7/8 `[2,2,3]`/`[3,2,2]`/`[2,3,2]`, else null (draw the dashed group line, `elPicSVG`) |
| `cells` | cells by bar (`LCELL` keys) |
| `anac, anacCells` | R7 on: upbeat length (210 or 420; 210 in compound) and its cell (`'e'` or `'q'`); the last bar is shortened by it |
| `barLen` | each bar's ticks |
| `a` | the whole answer, flat: anacrusis cells first (this is what `EAR.ans` must equal for a right answer) |
| `bars` | number of bars (0.48 field) |
| `swing, backbeat, tup` | R8 swung quavers (print the swing mark and "swung" label), R8 backbeat context, R9 contains a 5/7-tuplet |
| `drums` | R10: `{kick: [8-bit quaver mask per bar], snare: ['bb'|'bb4' per bar]}` (`ladDrumOns(drums)` → onsets) |
| `tempo, pitch, clap, new` | drawn tempo 66–100 (66–84 at R1), the tone's MIDI, clap at R1 |

### 3.3 Cells, names and text

* `LCELL[k] = {t: [[ticks, kind]...], f: 's'|'c', tup?: [groups], tieOut?: true}`; kind `n` note, `r` rest, `t` tied continuation. `ladW(k)` = length.
* `ladRhyTiles(l)` the rung's tiles. Compound tiles (`f: 'c'`) are live only in 6/8 and 12/8; in 7/8 the 2-groups use `e2 q re er` and the 3-groups `c3 cD cqe ceq`.
* Names: `ladNameTable()` (by `EAR.names`), `LADNAMES`, `LADNAMES_KK`. Tooltips/feedback words: `LADTITLE`, `LADCN`, `LADW` (and `ELCN`, `ELW` now hold every cell).
* `ladRhyNames(q)` per bar `[{k, name}]`. **Tie rule (L97, after IC_LADDER_ENG M-5):** a note tied in over the barline (from `antB`, "ti ti-")
  is held on the vowel of the note it is tied from, one "i" for each syllable it would have had, and the cell's other notes keep their own syllables:
  ta → "-i", ta-a → "-i-i", ta-a-a → "-i-i-i", ti-ti → "-i-ti", tika-tika → "-i-ka-ti-ka", tika-ti → "-i-ka-ti", ti-tika → "-i-ti-ka", tam-ti → "-i-ti".
  `ladTiedName(k, table)` gives that name; `LSYLG` holds each cell's syllables note by note. A tuplet never starts under such a tie.
* `trq` (a swung pair written as a triplet crotchet–quaver; it only appears in Nearly feedback): tri-o-la with its first two notes tied, held on the vowel:
  **"tri-i-la"** (Kodály names) and **"ta-a-ta"** (Kodály with konnakol tuplets). Single values by value (L97 extension): quaver "ti", dotted crotchet "tam",
  compound crotchet "ta".
* `ladMelNames(q)` per bar `[{k, name}]` for the **reveal only** (names are not shown during entry, L103).
* New thing texts for the "Ready for the next rung?" line: `LMNEW[rung]`, `LRNEWTXT[rung]`.
* `ladSolInfo('fi')` → `{syl, name, base, alter, sign}`: chromatic syllables have `sign: null` (no hand-sign art, L99): show the solfa name only.
* `ladSpell(i, a, doPc)` → `{letter, acc, name, oct, midi}` (letter-name spelling in the key).

## 4. Melody entry: the duration palette (L103)

The first note is given (pitch and, from rung 4, its length): `ladFirst(q, part)`. The student's entries are **the notes after it**:
`[{s: 'm' | "d'" | null (rest), t: ticks}]` (`EAR.ans`). For M11 `EAR.ans = {mel: [...], bass: [...]}` (the part switch).

* `ladPalette(q, entries, part='mel')` →
  `{done, bar, beat, tick, lengths: [{t, rest, label}]}`: the lengths that are legal **at the current position** and can still lead to a complete bar
  under the rung's rules (IC M-10): inner bars from the rung's cells under RF (quavers in beat pairs, minims and tam-ti from strong beats, the dotted
  minim from beat 1 of 3/4 at M6 on, compound beats in 6/8); the last bar may also hold a minim off a strong beat (never across the middle of 4/4), the
  dotted minim from beat 1 (M6 on) and, filling the bar to its end, a dotted crotchet (simple) or a crotchet (6/8); bar 0 = the upbeat's value (a crotchet
  upbeat may be two quavers). So: no dotted minim inside 4/4 bars, no dotted crotchet at M4–M5, no minim in 6/8, and every offer can be completed.
  `ladPalTilings(l, metre, len, last)` lists the legal fillings. M11 bass (`ladBassNext`): minims on strong beats (and beat 2 of 3/4), crotchets on beats,
  the dotted minim from beat 1 of 3/4; never a dotted crotchet (M11 upbeats are crotchets, so the last bass bar is a minim or minim + crotchet).
  Rests are offered where a note of that length is (up to a crotchet; M12 up to a beat; none in the bass).
  `done: true` once every bar is full. Rungs 1–3: crotchets only. M12: any written value that fits without crossing a beat.
* `ladBeams(q, entries, part)` → arrays of note indices (the given note = 0) to beam together, per beat (dotted-crotchet beat in 6/8).
* `ladEntriesToLine(q, entries, part)` → `[{on, dur, rest, sol, midi}]`: the marking format, from the given note.
* `ladTruthEntries(q, part)` → the right answer in the entry format (for "Show me" and the reveal).
* Desk wording (MU1): from rung 4 show "bar b of n, beat k" (`bar`, `beat` from the palette), never the note count.

## 5. Marking

### `ladMelMark(q, ans, {pivot, mod})` → `{ok, nearly, kind: 'right'|'nearly'|'wrong', detail, extra, nRight, n, pivot, mod, parts}`
* D4: **right only when every note's pitch and rhythm are right.** `detail[j] = {j, pitch, rhythm, spell, given, want}` per note of the answer
  (aligned by onset), for the per-note ticks in the result and "x of y notes" (`nRight`, `n`) in the journal line.
* Nearly only at M10, when every wrong note has the right pitch spelt with the other chromatic syllable (`spell: true`, e.g. fi for se).
* M9 (D8, L102, L107; IC M-6, M-7). Keep home do: every entry is read against the old do; the pivot is not asked.
  Move do, dominant kinds (`M-V`, `m-v`): the student marks the mutation (`EAR.pivot`); entries before it are read against the old do, entries after it
  against the new do (`q.newDoMidi` = old do + 7, the frame of `q.readings.move`), the pivot itself in either key; a note is right when its sound is right.
  Right needs every note right **and** the mark inside `q.pivotWindow`; no mark = wrong.
  Move do, relative kinds (`M-vi`, `m-III`): there is no mutation (do stays). Every note right = right with no mark; a needless mark with every note right
  is still right, and the result's `note` carries the sentence to show ("Every note is right. There is no mutation here: …").
  `pivot: true|false|null` and `note` in the result.
* M11: each part separately in `parts.mel` / `parts.bass`; right when both are.
* M12: rests in the answer are fine where the excerpt is silent.

### `ladRhyMark(q, ans)` → `{ok, nearly, kind, beats: [{bar, beat, ok, anac?}], why, parts?}`
* Right: the same cells; or the same sound in cells that keep the rung's rules (RF).
* Nearly (only these, and only when that is the **only** difference from the answer, cell for cell at the same place): plain syn-co-pa where the
  answer has the tied form across the bar's middle (D11: "ti ti-i ti"); a septuplet with the other grouping (the accents, R9); a swung pair written as a
  triplet crotchet–quaver (`trq`, R8, swing items only). `why` says which.
* 5/4 fills each group as a 3/4 or 2/4 half (no cell across the grouping); 7/8 writes each group as one group cell (2: ti-ti, ta, ti sa, sa ti;
  3: ti-ti-ti, tam, ta ti, ti ta). Two single quavers for a ti-ti are not the notation: wrong.
* R10: `ans = {riff: [cells], drums: {kick: [onsets], snare: [onsets]}}`; `parts = {riff, kick, snare}`.
* `beats` are the per-beat ticks for the result (bar 0 = the anacrusis).

### Readiness (D10)
* `ladRdPush(EAR.rd, drill, rung, kind)` (already called from `earMark`): only `'ok'` and `'miss'` enter the window of 10; shown, skipped and nearly do not.
* `ladRdState(EAR.rd, drill, rung, earRungsShown(drill))` → `{last, n, ok, ready, next, text}`: `ready` when 8 of the last 10 are right and the next
  rung is shown at this Stage; `text` = "Ready for the next rung? Rung n+1: <its new thing>". The button just sets the rung (no automatic move).

## 6. Playback (through the transport: `elPlay(item, variant)`)

| drill | variants | what plays |
|---|---|---|
| melody 1–3 | `all` `nokey` `first` | key cue (tonic chord at do = 60 + pc), one note every 0.65 s (as built) |
| melody 4–11 | `all` `nokey` `first`; M11 also `melonly` `bassonly` | key cue (D7: the mode's own tonic triad, at do = 60 + pc), one bar of woodblock count-in, then the anacrusis on its own beat (the pulse goes on through the short bar), the line at `q.tempo`. M11 bass on the bass samples |
| melody 12 | `all` (melody alone), `accomp` (with the accompaniment; needs `AN.meta` loaded: `anLoadMeta()`), `nokey`, `first` | the excerpt in its own register and tempo |
| rhythm | `all`, `follow` (calls `earRhyCaret(u)` with u in semiquavers), `beat` (`opts.o = [bar, beat]`, bar 0 = anacrusis: your beat, then the right one); R10 `drums` / `riff` | count-in bar (7/8 by groups), the line (clap at R1, tone after), tuplet groups +3 dB on each group's first note, swing 2:1, R8 backbeat context (kick 1 and 3, snare 2 and 4), R10 kick + snare + riff, pulse (`EAR.rhy.pulse`). Tempo: `EAR.rhy.bpm` (72/100) if chosen, else `q.tempo` |

`ladSched` returns `{end, lead, bl, events, start, beat, gain, first}` like the 0.48 schedulers; rhythm `events` list each sounding note `{t, d, on, dur, acc}`.
Helpers: `ladCueNotes(q)`, `ladRhyEvents(cells)` (sounding pattern with ties merged and accents), `ladBeatTicks(metre, grp)`.

## 7. Data

* `LADM12`: 40 phrase excerpts (after IC_LADDER_ENG) from the ten licensed scores (`m12_curate.py`, table in `m12_excerpts.json` and the build report):
  `{id, score, bars, tonic, mode, do, metre, anac, level, rhyExtra, tempo, barLen, ms, notes: [[on, dur, midi|null, sol]], credit}`. Bar outline as D9
  (every bar full, the last shortened by the anacrusis; a phrase that ends earlier finishes with rests). `credit`: composer in full, the work, the score data
  with encoder and licence.
  **Each needs the independent theory check before release.**
* `LADREC = {mel: [], rhy: []}`: contemporary items (D13), empty until the recordings check. Entry shape (notes and rhythm only, no lyrics,
  no audio): `{id, drill, rung, artist, title, year, link, start, end, credit, checked, key: {do, mode}, metre, anac, notes: [[on, dur, sol]] | {riff, drums}}`.
  The desk shows the link and timestamp; the app does not play these.

## 8. Not in the engine (yours)

The rung picker and strip (12 / 10 rungs, scrollable on phones), the readiness line and button, the palette, ladder (half rungs for chromatic
syllables, si/fi beside so/fa, `aug2` gap), "New key from here" / "Mutation here: so = do" control, grand staff for M11, part switches, the
names-setting control (from R7) and the Move do setting (M9), tile families, stave drawing in ticks, the swing mark, the grouping line.
