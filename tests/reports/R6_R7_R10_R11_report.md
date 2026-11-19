# 0.48 correction register: R6, R7, R10, R11 (branch `048-r6terms`, based on 0.47 `ef97cdb`)

Four commits plus this report. Nothing was pushed and `main` was not touched.

| Item | Commit subject |
|---|---|
| R7 | footer line drops the sample-library credits; Credits panel keeps them; content_lint checks the panel |
| R10 | double accidentals are 𝄫/𝄪 everywhere; spelling_test scans every rendered label |
| R11 | the circle of fifths flags D♭ minor, G♯ major and D♯ major as theoretical keys |
| R6 | Australian and US terms (shared term list, clutter rule, `tests/terms_test.py`) |

---

## R7: footer credits

* Footer line before: `Composition Jungle Gym · preview 0.47 · sampled piano (VCSL Steinway B, CC0), guitar and bass (FluidR3_GM by Frank Wen, CC BY 3.0); without the samples the built-in synth plays · no accounts, no tracking · ...`
* After: `Composition Jungle Gym · preview 0.47 · no accounts, no tracking · ...`. The Credits link (`details#credits`) is unchanged and its Sound paragraph still carries VCSL Steinway B (CC0 1.0), FluidR3_GM by Frank Wen via midi-js-soundfonts (CC BY 3.0), and every other credit.
* The clause "without the samples the built-in synth plays" went with the credits, because it was part of the same sentence. It is a functional note, not a credit; say if you want it back.
* `tests/content_lint.py`: the credits section now reads the panel (`<details id="credits">`), not the footer element. New checks: the panel names VCSL, Steinway B, CC0, FluidR3_GM, Frank Wen, CC BY 3.0 and midi-js-soundfonts; the footer line outside the panel must not carry FluidR3, Frank Wen, CC BY 3.0, VCSL or Steinway; the footer still has a Credits link. All the older on-screen credit checks (Sapp, NIFC, Curwen/KMEIA, licence links and so on) now run against the panel.

## R10: double accidentals

Cause: `pretty()` converted a double accidental only at the very end of a string, so a chord symbol with a suffix ("B♭b" + "m7", "F♯♯" + "m") came out wrong, and runs of three or four accidentals (the R3 respelling cases) came out as "B♭b𝄫".

Fixes in `index.html`:
* `pretty()` now converts any run of 2+ sharps or flats after a note letter (also before a chord suffix such as m, maj, dim, aug, sus, add): double = 𝄪 / 𝄫, triple = ♯𝄪 / ♭𝄫, quadruple = 𝄪𝄪 / 𝄫𝄫. Words such as "Abbey" are not touched.
* Chords room root menu showed the raw "Cbb", "C##" in the `<option>` text; the text now goes through `pretty()` (the option `value` is unchanged).
* Degree labels in the Chords room (tile, formula, voicing cards) showed "♭♭7"; they now use `degPretty()` (𝄫7); `degPretty()` also handles "##".

Keys-room chord buttons (about 306): checked by the existing K section (5,238 chords of the key), no failures; the SP-2 known failure is removed from `KNOWN`.

Test: `tests/spelling_test.py` section G scans every text node and every title/aria-label/alt in the Keys room (every scale, circle key, interval), the Chords room (every root spelling x quality), every climb render, and every room as first opened at Stages 4, 5, 6. It fails on "♭b", "♭♭", "♯♯", "♯#", "##", and a note letter followed by "bb" used as an accidental (the "Bbb", "Bbbm7" forms; not "Abbey").

## R11: circle of fifths

Parallel key of D♭ major, G♯ minor and D♯ minor is now flagged in red in the same style as the Scales tab, for example:
`G♯ major · same home, different key signature · a theoretical key (8 sharps); musicians write A♭ major`
D♭ minor -> 8 flats, C♯ minor; D♯ major -> 9 sharps, E♭ major. The test (section C) requires "theoretical", the accidental count and the usual equivalent for every circle key whose parallel needs more than 7 accidentals, and checks with music21 that the equivalent is not itself theoretical. SP-3 is removed from `KNOWN`.

---

## R6: Australian and US terms

### The one shared term list (`TERMS` in `index.html`, mirrored in `tests/terms_test.py`)

| key | Australian (shown first) | US (in brackets) |
|---|---|---|
| perfect | perfect cadence | authentic cadence |
| iac | perfect cadence, less final | imperfect authentic |
| imperfect | imperfect cadence | half cadence |
| plagal | plagal cadence | (same word, nothing added) |
| interrupted | interrupted cadence | deceptive cadence |
| crotchet | crotchet | quarter note |
| quaver | quaver | eighth note |
| minim | minim | half note |
| semibreve | semibreve | whole note |
| semiquaver | semiquaver | sixteenth note |
| bar | bar | measure |
| stave | stave | staff (plural: staffs) |
| tone | whole tone | whole step |
| semitone | semitone | half step |

Other constants: `TERM_IAC` = "Perfect cadence, less final (US: imperfect authentic)"; `TERM_NOTE` = "US 'imperfect authentic' is still a perfect cadence; the Australian imperfect cadence is the US half cadence." Helpers: `termDual(k, plural)` ("crotchet (US: quarter note)"), `termTip(k)` ("US: quarter note"), `termPass()`.

Format of every bracket: Australian term, then "(US: ...)". A US term is never shown without its Australian term.

### How the clutter rule is applied

These words are drawn in hundreds of places (song data, Teacher notes, counterpoint rule texts, feedback built from templates, and so on). Rather than hand-bracket each one, the rule is applied centrally to everything the app draws, by `termPass()`, which runs once at load and again 90 ms after any DOM change (a `MutationObserver`). It also exposes `window.termPass()` for tests. It is idempotent (tested) and finds terms with the `rx` of each list entry.

| Where the term sits | What the pass does |
|---|---|
| Answer buttons, chips, `<option>`s, cadence cards (`.cad`), pills, the narrow bar labels in the Forms grid | Australian term only; the US term goes in the element's `title` ("US: authentic cadence"; several terms join as "US: a, b"). Any existing title is kept. |
| Headings (`h1`-`h6`, `summary`, `th`, `.disp`, `.kicker`, `.lbl`) | Both: "Perfect cadence (US: authentic cadence)". |
| Explanations and answer feedback (paragraphs, list items, table cells, feedback boxes) | Both, at the first mention of each term in each text block; later mentions in the same block carry the hover only. |
| First mention in each room (and in each open climb) | Always both, including the scoped terms below. |
| `bar` and `stave` (the two words that are everywhere) | Both in headings and at the first mention in each room (each open climb); the hover on every other mention. |
| Scores (everything inside `<svg>`: VexFlow staves, the engraved Analysis scores, the Phrase builder labels) | Australian term only, never a bracket (the pass skips svg). |
| `whole-tone scale`, `bar line`, `bar chart` | Left alone: same in both. |

Prose gets a dotted underline and a small tooltip on focus (tap) as well as the native hover title, so a touch screen can read the US term in running text. Brackets inherit the surrounding size; the test checks every bracket and hover is at least 11 px.

### Hand edits (US-only wording turned Australian-first; the pass then adds the brackets)

| Room | Before | After |
|---|---|---|
| Gym, cadence reader (V-I with an inverted chord) | "A weaker perfect cadence (US: imperfect authentic cadence)." | "This one is a Perfect cadence, less final (US: imperfect authentic)." + the one-line note |
| Gym / Analysis "my progression" report (chips, Cadences row, journal text) | "weaker perfect (US: imperfect authentic) cadence"; "half cadence" (a US-only name that was displayed); "perfect cadence" | `cadWord()`: "Perfect cadence, less final (US: imperfect authentic)", "imperfect cadence", "perfect cadence", ...; the note once in the Cadences row |
| Oracle (dice) | "The deceptive turn" | "The interrupted cadence" |
| Forms, Phrase builder (palette, slots, phase labels, messages, Understand text) | "Weaker perfect cadence", "(US: imperfect authentic)" | "Perfect cadence, less final" on chips and in the score label; "(US: imperfect authentic)" added by the pass in explanations and feedback; the note in the Understand text and the PM3 feedback |
| Forms (rag, rondo, double period, refrain, phrase builder, 12 places) | "imperfect (half) cadence" | "imperfect cadence" (the pass adds "(US: half cadence)") |
| Ear Lab, cadence and blind-analysis answer buttons | "Perfect (authentic)", "Plagal", "Imperfect (half)", "Interrupted (deceptive)" | "Perfect cadence", "Plagal cadence", "Imperfect cadence", "Interrupted cadence" (US term on hover; in the answer feedback the pass adds it) |
| Ear Lab, help text | "Perfect (authentic): ... Imperfect (half): ... Interrupted (deceptive): ... US terms are in brackets." | the Australian names in full; the pass adds the brackets |
| Climb 3 (cadences), "Also called" row | "authentic cadence (US)" | row "In the US": "perfect cadence = US authentic cadence" (plagal: "the same name") |
| Climb 3 (cadences), Phrygian cadence | "a half step" | "a semitone" |
| Climbs 6-8, 11 (secondary dominants, borrowed chords, review) | "deceptive" (8 places: card names "Deceptive V7/vi of ...", "Deceptive ♭VI", hints, rubric, review text) | "interrupted" (Hutchinson note: "interrupted V7/vi → IV (US: deceptive)") |
| Climb 2 (counterpoint, all species, rule book, 3-voice mixed species, quiz, feedback) | "half note(s)", "whole note(s)", "quarter(s)", "eighth notes", "Eighth notes move by step", "Weak-quarter dissonance", "half rest", "weak quarter of the bar" (dozens of strings) | "minim(s)", "semibreve(s)", "crotchet(s)", "quavers", "Quavers move by step", "Weak-crotchet dissonance", "minim rest", "weak beat of the bar" |
| Climb 9 (jazz guide tones) | "watch the staff"; "in whole notes" | "watch the stave"; "in semibreves" |
| Climb 13 (fugue) | "Three bars of quarter-note cells"; "the middle staff" | "crotchet cells"; "the middle stave" |
| Keys, Scales & Modes (scale descriptions) | "a whole step apart", "the half steps between mi-fa and ti-do", "no half steps", "alternating half and whole steps" | "a whole tone apart", "the semitones between ...", "no semitones", "alternating semitones and whole tones" |
| Keys, Scales & Modes (step legend) | "W = whole step (tone) · H = half step (semitone)" | "W = whole tone · H = semitone" (pass adds the brackets) |
| Forms (Tap a row to see it on the staff), Climb 9, Phrase | "staff" (x4 visible) | "stave" |

Not changed: scores/meta.json and the scores (already Australian only: "Perfect cadence", "Imperfect cadence", ...), the song database strings (they use "whole tone", "semitone" already, so the pass brackets them), code comments.

### Tests

* `tests/terms_test.py` (new, added to `tests/run_all`): T1 the term list equals the rule; T2 with every "(US: ...)" and the note removed no rendered text contains authentic, half cadence, deceptive, quarter/eighth/sixteenth/half/whole note, whole/half step, staff or measure (checked on `main` after every click, and on every title); T3 buttons/chips carry no bracket and have the US hover, headings that name a term carry both, the first mention in each room carries both, svg text has no US term; T4 "imperfect authentic" always comes with the note and "Weaker perfect cadence" is gone; T5 idempotent, brackets at least 11 px, and the observer brackets text added after load.
* `tests/earlab_test.py` section H: it pinned the old labels ("Imperfect (half)", "Perfect (authentic)"); it now requires the four Australian-only answer labels.
* `tests/content_lint.py` rule 1 now also allows the exact one-line note ("US 'imperfect authentic' ...", "the Australian imperfect cadence is the US half cadence") and the "= US ..." row in Climb 3. The main session will add the US-only lint after merging.

---

## Uncertain, for Justin to confirm

1. **Dual terms in every explanation block versus clutter.** I read "both terms in headings, explanations and answer feedback" as: both at the first mention of each term in each paragraph, list item, table cell or feedback box (not every repeat). Counterpoint rule tables therefore show "(US: ...)" in each row. Easy to loosen (first per room only) in `termBrackets()`.
2. **`bar` and `stave` are scoped** (both terms in headings and at the first mention in each room, hover elsewhere), because "Bar 3 (US: measure), beat 4" on every feedback line would bury the feedback. This departs from "both terms in answer feedback" for these two words only; flip `scoped:true` to `false` in `TERMS` to bracket them like the others.
3. **Touch screens.** Prose terms show the US term on tap (focus tooltip). Answer buttons, chips and options have only the `title` hover, so a phone cannot see the US term there until the feedback appears. A tap on a button does its job, so I did not add a second tap behaviour.
4. **"tone" is matched only as "whole tone(s)"** (not the bare word "tone", which is also "chord tone" and "tone colour"). "Whole-tone scale" is left alone (same in both).
5. **Plural of stave -> "staffs"** in the bracket (US "staves" is also used; writing "staves (US: staves)" would be useless).
6. **Phrygian cadence** is not in the term list (it is the same in both; the US name "Phrygian half cadence" appears only as "phrygian cadence = US Phrygian half cadence" in Climb 3).
7. **`title` attributes of existing elements** gain " · US: ..." after the existing text (for example the Gym's "one bar per chord. · US: measure").
8. Visible terms are rewritten in the source by phrase ("half note" -> "minim", "quarter" -> "crotchet", "whole step" -> "whole tone"), so any such phrase in a code comment was changed too (harmless).
9. R7: the clause "without the samples the built-in synth plays" left the footer with the credits (see above).
10. Page-error note: one full terms_test run (about 27 min, box under load) ended with a single uncaught "Cannot read properties of undefined (reading 'd')" in a view I could not identify; the same sweep re-run (and a 4,245-click pageerrors_test, and two targeted click sweeps at Stages 4, 5, 6) found none. I could not reproduce it; it is probably a timing race in a button-click sweep, not related to the term pass (the pass only touches text and `title`).

## Not done

* The content-lint check for US-only terms (the main session adds it after merging).
* Song database, scores/meta.json and the engraved scores were not edited.
* No US tap tooltip on buttons (see 3).
* The R6 test sweeps clicks at Stage 6 (40 per view) and Stages 4 and 5 (10 per view) to keep the runtime reasonable; `TERMS_STAGES=6` runs Stage 6 only.

## Suite results (from /home/claude/wt-r6terms, final tree)

All pass on the final tree (`tests/run_all <suite>`; earlab_test and earlab_r2_test ran one edit earlier, before the one-selector change that keeps the Forms grid bar labels to the Australian term only, which cannot affect them).

| Suite | Result |
|---|---|
| content_lint | pass |
| unit_test | pass, 0 failures |
| sound_test | pass, 0 failures |
| earlab_test, earlab_r2_test | pass, pass |
| chordshape_test | pass, 0 failures |
| spelling_test | pass: 49,122 checks, 0 failures, no known failures (SP-2 and SP-3 are fixed). New: section G scanned 12,887 distinct rendered strings; section C: 3 theoretical parallel keys flagged with their equivalents, 21 other parallel keys |
| terms_test (new) | pass: 153 views x Stages 4, 5, 6, 2,345 clicks, 0 failures |
| counterpoint_test | pass |
| pageerrors_test | pass: 153 views, about 4,245 clicks, 0 errors |
| layout_test | pass: 162 views, 0 findings (the first run found the term brackets overlapping the "split" button in the Forms rag and rondo bar labels at 390 px; those labels now take the hover only) |
| transport_test | pass |
| score_measure_test | pass |
| analysis_engrave_test | pass, 0 failures |

Environment note: spelling_test was killed twice by the container's memory limit ("Target crashed", the kernel log shows a Chrome renderer OOM-kill during the Climbs sweep) while other agents' browsers were running. The same crash happened on an untouched copy of 0.47 (`ef97cdb`), so it is not caused by these changes. It passed on the third run once memory was free. terms_test takes about 10 to 25 minutes on a busy machine (`TERMS_STAGES=6` runs Stage 6 only).
