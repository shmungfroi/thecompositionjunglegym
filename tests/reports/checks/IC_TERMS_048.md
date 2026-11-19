# IC_TERMS_048: independent check of the Australian and US terms and the spelling fixes (0.48, `fde5842`)

Checker: an independent agent that did not build this. The verdicts below come from my own sweep and my own checks. I read the
builder reports (R6fix_report.md, TERMS_048_merge_report.md) only after the verdicts were set (see the last section).
Build: `/home/claude/wt-check-int`, detached at `fde5842`, read only. Scratch files: `/home/claude/checks/terms/`.

## Method (my own)

* `sweep.py` uses the repo harness (cjg.py, Chrome). It opens 195 views at Stages 4, 5 and 6: every room, the Keys tabs (scales,
  circle, intervals), climbs 1 to 13, 10 forms, Analysis (map, prog and 10 scores), and the Ear Lab (7 drills × 3 rungs, play, then
  4 answers each). It clicks up to 30 buttons per view at Stage 6 and up to 12 at Stages 4 and 5. After each step it saves the
  visible prose (buttons and scores removed), the button text and title, headings, the svg text and every visible `[title]`.
  That gave 2,447 snapshots, 164k button instances, 41.9k headings (1,403 of them name a term), 2.5k scores, 8,322 rendered US
  brackets and 252 Ear Lab answers.
* `analyse.py` holds my own term regexes. It checks for: a US term alone, a bracket on a button, a button with no US hover, a heading
  with no bracket, the first mention in each view, bar or stave bracketed again, compound or locator brackets, nested or back-to-back
  brackets, a capital mid-sentence, the IAC note, ♭♭/bb/##, W/H step letters, and abbreviations in the checker.
* `target.py` checks: every Keys scale (step letters, legend, octatonic); 72 Ear Lab cadence and blind feedback panels and 30 chord
  quality panels, read as rendered; the Ear Lab key line at 1000 px; the rondo labels.
* `circ.py` checks all 24 circle keys against music21 10.5.2: signature, relative, parallel, V and IV keys (P5 and P4
  transposition), the enharmonic "also written as", and the theoretical-key flags.
* Climb 2: `c2Check` fuzzed over every mode × species {1, 2, 2.5, 3, 4, 5} × above/below × 25 lines. That gave 425 distinct
  messages in 35 codes.
* Content lint was probed on a scratch copy of index.html with "quarter note", "measure", "deceptive cadence", "whole step" and
  "staff" injected.
* For reference, `terms_test` was run alone (TERMS_FAST=1): 0 failures. My verdicts do not rest on it.

## Verdict table

| Rule | Verdict | Count / evidence |
|---|---|---|
| One shared term list (TERMS, IAC label, note) | PASS | 14 entries match the spec; `TERM_IAC`/`TERM_NOTE` exact |
| Headings that name a term carry both | PASS | 1,403 term headings, 0 without bracket |
| First mention in each room carries both | **FAIL** | 569 view×term first mentions; 0 fail in prose proper, but Ear Lab feedback headings (below) and forms/rondo (cadence terms never bracketed in the room, 3 stages) |
| Answer feedback carries both | **FAIL** | Ear Lab cadence/blind: correct-answer panels show "Imperfect/Perfect/Interrupted cadence" with no US term on screen (US term only in a 1×1 px screen-reader region); chord-quality "a tone under the octave" unpaired |
| Australian only on buttons/chips, US on hover | **FAIL** | 0 brackets on any button (PASS part); Ear Lab rhythm answer tiles hover "crotchet", "2 quavers", "minim", "dotted crotchet, quaver"… with no US term (9 cells) |
| Australian only inside scores | PASS | 2,529 svgs, 0 US terms / brackets |
| No US term alone / no shortened US term | **FAIL** | Analysis "Imperfect (half) cadence" (13 strings in scores/meta.json, all stages); Ear Lab key line "Imperfect = US half" (visible < 1180 px) |
| IAC label + one-line note | PASS | forms/phrase prose and chip hover both carry the note; 0 "Weaker perfect"; 0 capital mid-sentence |
| Answer 6: bar/stave once per room; locators unbracketed | PASS | 0 views with a second bar/stave bracket outside headings; 0 bracketed "Bar N, beat N" after first mention |
| N-bar compounds / "bar by bar" not bracketed | PASS | 0 (Twelve-bar buttons carry no measure hover either) |
| Keys T/S, US W/H in legend; octatonic | PASS | 17 scales: steps T/S/T+S; legend "T = tone (US: whole step, W) · S = semitone (US: half step, H)"; "semitone–tone diminished (US: half–whole diminished)" |
| Short cadence buttons hover full US term; Plagal/Phrygian/Cad 6/4 none | PASS | Ear Lab rungs 1–3: "US: authentic cadence", "US: half cadence", "US: deceptive cadence"; others no title |
| Nested bracket uses [US: …]; no back-to-back | PASS | 11 square-bracket forms seen, 0 nested round, 0 back-to-back |
| Content lint fails a US term alone | **FAIL** | lint passes "quarter note", "measure", "deceptive cadence", "whole step", "staff" alone; it only knows "authentic"/"half cadence", and it whitelists "Imperfect (half)" |
| Spelling: no ♭♭/bb/## for 𝄫/𝄪 | PASS | 0 real cases; 50 regex hits all checked as adjacent separate elements (note + degree "E♭" "♭3", "B♭" "♭VII") |
| Circle of fifths spelling (24 keys, music21) | PASS (spelling) / **FAIL** (case) | signature, relative, parallel, V, IV, enharmonic twin all correct; D♭ maj IV = G♭, F♯ maj V = C♯ ✓. But minor keys' neighbours are printed upper-case: B♭ minor shows "F … · E♭", D♯ minor "A♯ … · G♯" (spec: e♭, a♯), 12 keys × 2 |
| Theoretical keys flagged | PASS | D♭ minor "(8 flats); musicians write C♯ minor", G♯ major "(8 sharps)… A♭ major", D♯ major "(9 sharps)… E♭ major" |
| Climb 2 checker spells out intervals | PASS | 425 messages: "a diminished 5th", "an augmented octave", "a perfect 4th"; 0 abbreviations (d5, A4, P5…) |

## Findings

### Must

**M1. Ear Lab cadence feedback shows the term with no US term (Cadences and Blind analysis drills, every stage).**
The verdict heading is `<div class="el-answer" role="heading" data-notm>` (index.html l.7259) and it holds `CADL[a]`. `data-notm`
stops the term pass, so the heading never gets a bracket or a hover. The US bracket appears only in `#earLive.el-sr`, a 1×1 px
clipped screen-reader region. When the teaching sentence does not name the cadence, which is true of every right answer and of
several wrong ones, a sighted student sees no US term at all. Rendered examples:
* `S6 ear/cad/r1`: "CORRECT / Imperfect cadence / It stops on V and waits there. A comma, not a full stop."
* "CORRECT / Perfect cadence / V to I: the leading note rises…"
* "NOT THIS TIME / Interrupted cadence / You heard V set up a close…"
* Blind analysis, S4/S5/S6: "Correct / Imperfect cadence / It stops on V…"

Fix: take `data-notm` off `.el-answer` and let the pass bracket it ("Imperfect cadence (US: half cadence)"), or write
`termDual()` into the heading by hand. Keep the Phrygian and Cadential 6/4 heads as they are.

**M2. Analysis cadence tables: "Imperfect (half) cadence (ends on V)" (13 strings in scores/meta.json; shown at S4, S5 and S6).**
This is a shortened US term in a bare bracket. It also splits the Australian term, so the pass does not see "imperfect cadence"
and adds no bracket or hover. Seen in analysis/map and the chorale, Jesu, K331a, K331d and Chopin 20 tables. Chopin 20 also has
"ending on V (an imperfect (half) cadence)". It is the L8 form the merge round banned, and content_lint lets it through
(`lead` ends in "Imperfect"). Fix: change meta.json to "Imperfect cadence (ends on V)", which the pass turns into "(US: half
cadence; ends on V)". Also take the "(half)/(authentic)" exception out of content_lint.

**M3. Ear Lab rhythm dictation answer tiles hover the Australian term only (S4, S5).**
The `[data-earcell]` titles are "crotchet", "2 quavers", "minim", "4 semiquavers", "crotchet rest", "dotted crotchet, quaver",
"quaver, 2 semiquavers", "2 semiquavers, quaver" and "quaver, crotchet, quaver". The visible text is the time name ("ta"), so
`termBtnSync` finds no term and adds no "US: …". The spec asks for the US term on the hover of answer buttons. Fix: build the
title from RCELL with the US form, e.g. "crotchet · US: quarter note", "dotted crotchet, quaver · US: dotted quarter note, eighth
note", "crotchet rest · US: quarter rest". Or set `data-tk` and let `termBtnSync` add it.

**M4. Circle of fifths: a minor key's dominant and subdominant keys are printed in capitals (12 minor keys).**
B♭ minor shows "F (one step clockwise: the dominant key) · E♭ (one step back: the subdominant key)". D♯ minor shows
"A♯ … · G♯ …". A minor shows "E … · D …". The letters and accidentals are right (music21, all 24 keys). But the app's own circle
writes minor keys in lower case, and the spec gives "B♭ minor iv = e♭, D♯ minor v = a♯". In capitals a student reads E♭ major.
Fix: in `renderCircle`, for `CSEL.minor` print `pretty(dom).toLowerCase()` (or "E♭ minor").

### Should

**S1. Ear Lab chord quality feedback: "You heard the 7th a tone under the octave, and that is right." The interval "tone" is
unpaired in answer feedback** (index.html: "a tone under the octave, and it wants to move", 2 strings). The `tone` rx does not
cover "a tone under". Fix: add `under|over|below` to the rx, or write "a tone (US: whole step) under the octave".

**S2. "dotted crotchet (US: quarter note)" pairs a dotted value with a plain one.** Seen in Ear Lab rhythm tips (all stages: "A
dotted crotchet (US: quarter note) and a quaver…") and in climbs/5 ("the tempo is the dotted crotchet [US: quarter note]").
Because "dotted" sits outside the term, the bracket says a dotted crotchet is a quarter note. Fix: add `dotted crotchets?` (and
dotted minim/quaver) to the rx so the result is "(US: dotted quarter note)".

**S3. Ear Lab key line "Perfect = US authentic · Imperfect = US half · Interrupted = US deceptive"** is visible below 1180 px wide
(checked at 1000 px). This is the shortened US form that C1/L8 removed everywhere else, and it does not use the bracket form.
The merge report keeps it by design (Justin, 19 Nov, answer 7). It is listed here for his decision. The suggested form is
"Perfect (US: authentic cadence) · Imperfect (US: half cadence) · Interrupted (US: deceptive cadence)".

**S4. forms/rondo never shows the cadence terms with both names** (S4, S5, S6). The phrase labels "4 · imperfect cadence" and
"8 · perfect cadence" are `.fbar>small`, which counts as a chip (hover only). The only prose sentence is inside the refrain
button ("Bar 4 asks with an imperfect cadence…"). So the first mention in the room is never bracketed. Fix: put the sentence in
the room's explanation text (outside the button), or let the first `.fbar>small` in the room take the bracket.

**S5. Content lint does not fail a US term used alone** (the spec says it should). Fix: in content_lint, flag deceptive, quarter,
eighth, half, whole and sixteenth note or rest, whole or half step, staff and measure outside a "(US: …)" / "[US: …]" / `us:'…'`
field. Remove the "Imperfect (half)" whitelist. Runtime T2 in terms_test covers rendered text only.

### Could

**C1. "In the US" rows in climb 3:** "perfect cadence = authentic cadence" repeats what the heading bracket above it already says
("See · Perfect cadence (US: authentic cadence)"), in a second format. Consider dropping the row, or showing it only for Plagal
and Cadential 6/4 ("the same name").

**C2. A locator gets the room's one bar bracket:** "the turnaround (bar [US: measure] 12)" (climbs/4); "Phrase 1 · from bar
(US: measure) 1" (Analysis). This is allowed, but it splits the locator. Prefer a non-locator mention for the bracket.

**C3. "Weak-crotchet (US: quarter note) dissonance"** (climb 2 rules table): the bracket sits inside a hyphenated compound.
Consider "Dissonance on a weak crotchet (US: quarter note)".

**C4. Climb 2 can produce very wide compound names** ("a dissonant perfect 18th", "major 16th") when lines range widely. They are
correct, but "a perfect 4th plus two octaves" may read better.

## What I could not check

* Real tap behaviour on touch devices. I checked that title attributes exist; I did not check a tooltip on a phone.
* Audio-dependent Ear Lab states. Answer buttons were force-enabled after Play, so every answer path was reached, but whether a
  real listener hears what the feedback describes is outside this check.
* Every possible checker message in climbs 1 and 3–13 and Forms checkers beyond what the click sweep produced.
* Journal exports and imported files (skipped as destructive) for term pairing.
* Narrow-width layouts other than 1000 px for the key line.

## Comparison with the builder reports (read after the verdicts)

* **Agree:** shared list, headings, scores, N-bar compounds, "bar by bar", answer 6, square nested brackets, T/S letters and the
  legend, octatonic, IAC note, short cadence hovers (C1), ♭♭ fixes, and circle spelling (R6fix L6: G♭, C♯, A♯ fixed). My music21
  pass found all 24 keys right for letters and accidentals. terms_test fast run: 0, the same as their result.
* **Disagree / not covered:**
  * M1: the merge report says every Ear Lab cadence feedback sentence is bracketed. That is true of the sentences, but the visible
    heading is `data-notm`, and terms_test skips `data-notm`. On a correct answer there is no sentence naming the cadence, so no US
    term shows.
  * M2: neither report mentions "Imperfect (half) cadence" in meta.json. content_lint allows it on purpose, and the term pass
    cannot see it.
  * M3: the merge report touches the rhythm tip (`data-notm` on "quaver, crotchet, quaver") but not the rhythm tile hovers. T3
    reads only a button's own text, so a title naming the Australian term is not checked.
  * M4: R6fix checked letters only, not case.
  * S2: the merge report quotes "A dotted crotchet (US: quarter note)" as correct. I read it as inaccurate.
  * S1: R6fix judgement 2 accepted a narrow `tone` rx. One answer-feedback string slips through.
* **Same open items:** content lint for a US term alone (R6fix "not fixed": left to main session) and the key line (merge report
  "Open"). I list both as Should.
