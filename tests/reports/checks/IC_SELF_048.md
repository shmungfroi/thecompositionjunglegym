# IC_SELF_048: independent check of the 0.48 fixes that had only a self-check

Checker: independent (did not build these fixes). Worktree `/home/claude/wt/ic-self`, branch `049-ic-self` (live 0.48 + REGISTER_049).
Commits under check: `06afa46` (Ear Lab rung 1: S2 share, incomplete tonic, RUNG1_SOP_BALANCE) and `9c470c0` (M-12, S-F1/S-F2, S-T1, X-12).
Builder reports were not read. Every expectation below is this checker's own reading of the spec; the app's own rules were not reused
to judge the app (music21 and own arithmetic were used instead).

## Verdicts

| # | Item | Verdict |
|---|------|---------|
| 1 | Rung 1 imperfect: I–V and IV–V balanced | **PASS** |
| 2 | Rung 1 perfect: incomplete tonic (`EARR1OPT.inc`), strict voice leading | **PASS** on strictness; one Should on how often it is used (S1) |
| 3 | `RUNG1_SOP_BALANCE` exists, defaults off, nothing breaks when on | **PASS** |
| 4 | sus / power chords on the 5th stay D | **PASS** |
| 5 | `MD_MAJOR` on: borrowed v / ♭VII in major are MD; minor v / VII are MD; labels, colours, hovers agree | **PASS** |
| 6 | Climb 13 countersubject labels and IC1 note | **PASS** |
| 7 | `syn` tile hover one to one, Australian first, US after | **PASS** for `syn`; one Should on the other tiles (S2), one format query (S3) |

Required suites, run once each on this worktree: `python3 tests/earlab_test.py .` → 0 failures (4 min 17 s);
`python3 tests/unit_test.py .` → 859 checks, 0 failures.

No Musts.

## Evidence

### 1. Imperfect forms balanced (probe p1)
- Fitted weights (`earR1Weights()`), switch off: imperfect = I–V 0.5000, IV–V 0.5000. Switch on: 0.5000 / 0.5000.
- 20,000 seeded items (`earGen('cad',1)`, seed 53), switch off: answers perfect 4947, plagal 5055, imperfect 5125, interrupted 4873;
  imperfect forms I–V 2545, IV–V 2580 (49.7 / 50.3 %). Switch on (seed 71, 20,000): I–V 2513, IV–V 2508.
- Register does not predict the answer (held-out best guess, chance 0.256): lowest+highest note 0.268, span 0.261, key 0.255,
  first bass 0.282, last soprano 0.273.
- Inherent to the four models, not a defect of the fix: a first chord of IV is plagal 66 % of the time (5055 vs 2580), the most the
  model set allows at a 50/50 imperfect split; the soprano's solfa path predicts the answer at 0.818 (0.776 with the switch on).

### 2. Incomplete tonic, strict voice leading (probe p1)
- The pool (`earR1Pool()`) has 686 realisations; 55 are incomplete, all of them the final I of V–I (no other model, never the first chord).
- Own checker on all 686 pool entries and on all 40,000 generated items (both switch states): 0 errors. It checks, without the app's rules:
  chord identity and root position by music21 (`romanNumeralFromChord`, chord transposed to C), no non-chord tone, the 3rd present,
  incomplete chords only as the final tonic of V–I and only as root ×3 + 3rd ×1 (5th omitted), no doubled leading note, no crossing,
  no overlap, S–A and A–T within an octave, ranges B 40–60, T 48–67, A 55–74, S 60–79, no leap of a 7th, tritone or more than an octave,
  no consecutive 5ths / octaves / unisons in any pair (similar or contrary), no hidden 5th / octave in the outer voices with a soprano leap,
  the leading note rises in an outer voice (and in V–vi in any voice; an inner leading note in V–I either rises or falls to the 5th).
  The app's own `checkSATB` also reports nothing above info on all 40,000 items.
- Variety: distinct perfect voicings drawn in 20,000 items 91 (switch off) / 108 (on); incomplete ones 46 / 51.
- `EARR1OPT.inc=false` (weights cache cleared): 0 incomplete entries in the fitted weights and 0 incomplete finals in 2,000 items (probe p5).

### 3. RUNG1_SOP_BALANCE (probes p1, p5)
- `let RUNG1_SOP_BALANCE=false` (index.html l. 6911); read in the page as `false`. Not persisted or exposed in the UI.
- On: 20,000 items strict-clean by the own checker and by `checkSATB`; imperfect share 50/50; register tells at chance
  (lowest+highest 0.258, span 0.252 vs chance 0.254); soprano path 0.776 (from 0.818).
- On, in the live page: 40 rung 1 questions through `earNew()`, an answer click and the feedback panel: every question had four answers,
  finished (`EAR.done`), had a realisation, no checker error, no page error.

### 4. sus / power chords on the 5th (probe p2)
`analyse()` and `homes()` for every key (12 major, 12 minor), chords on the 5th: V, V7, Vsus4, Vsus2 (major), V5, V7sus4 → D in both modes;
v, v7 → MD. homes() and analyse() agree on every diatonic case (360 cases, 0 mismatches). Keys room text for Gsus4 (C major), G5 and
G7sus4 (C minor) says "a dominant-function chord with no 3rd ... open whether it will act as V ... or as the softer minor v"; Gm (C minor)
gets the MDv text. Gym cards: Gsus4 / G5 / Esus4 / E5 show "pull · dominant" in red #c8473b.

### 5. MD_MAJOR (probe p2)
- On (as shipped): in all 12 major keys v, v7, ♭VII, ♭VII7, ♭VIIsus4, ♭VIIsus2, ♭VII5, ♭VII7sus4 → MD; in all 12 minor keys v, v7, VII, VII7,
  VIIsus4, VIIsus2, VII5, VII7sus4 → MD; raised vii°, vii°7 → D. Every MD has FNHEX #bd6b97 and FNAME "soft pull · modal dominant".
- Live Gym cards (C major I v ♭VII V Vsus4 v7 ♭VII7, A minor i v VII V VII7 v7): numeral, label and colour agree on every card
  (MD = #bd6b97 + "soft pull · modal dominant"). Climb 8 bars in C major: v and ♭VII drawn `--c:var(--md)` with class `md`.
- Off (same page with `const MD_MAJOR=false` substituted at load): major-key borrowed v / ♭VII → C (violet, "colour"), climb 8 bars violet
  without `md`; minor keys unchanged (MD). No page errors in either state.
- Analysis precomputed labels (scores/meta.json): no major-key piece contains a borrowed v / ♭VII, so the "and borrowed into major" key
  text cannot disagree with any label; jesu (E minor) has VII / v⁶ labelled MD.

### 6. Climb 13 countersubject (probe p3)
7,509 subject/countersubject pairs (9 fixed cases + 1,500 random per context: C major, A minor, G minor, F♯ minor, D Dorian) through
`c13CSCheck`. For every pair issue (I1, IC1, I2, I3, I4; answer issues and CS1 left out): 0 failures on each of
- register word ("CS above / below / on the same note as the subject", "CS an octave lower, ...") against the sounding pitches;
- the interval named in the message equals the music21 interval of the two sounding pitches, with the right article;
- the two pitches printed ("X against Y") are the sounding pitches;
- IC1 is issued exactly when the inverted position has, on a strong beat with both notes struck, a perfect 4th / 11th that was a
  perfect 5th / 12th as written (1,608 issued, 1,608 expected);
- the "was a 5th before the voices swapped" note appears on IC1 only, never on I1 or I2.
Intervals met and named correctly include P4, P11, A4, d5, A11, d12, and in minor A2, d7, A1, A8, d8, A9, d4, A5, d14.
Fixed cases: a 5th above on beats 1 and 3 gives IC1 + note in the lower position ("C4 against G3 is a perfect 4th ... This 4th was a 5th
before the voices swapped"); an 11th above gives I1 in both positions, no note; a countersubject written below is labelled below, no IC1;
weak-beat "both voices move" issues carry no note.

### 7. `syn` hover (probe p4, live page)
Ear Lab rhythm drill at rung 3, tiles as drawn by the app, after a real mouse hover, after 5 further `termBtnSync` passes, and after a
click re-renders the tiles: `syn` title is always "quaver, crotchet, quaver · US: eighth note, quarter note, eighth note" (three and three,
in order, repeats kept; aria-label is the Australian half). q, h, qr, dq also pair one to one.

## Findings

**Must**: none.

**Should**
- **S1 (item 2) The incomplete tonic is the usual perfect cadence, and it marks the answer.** 65.9 % of perfect items end on the
  incomplete tonic (3262 of 4947; 68.5 % with RUNG1_SOP_BALANCE on), so it is the norm rather than "for variety", and it only ever occurs in
  perfect cadences: a final chord without its 5th is perfect 100 % of the time. Held-out, that one feature guesses the answer at 0.415
  against chance 0.256; given a final I, a complete tonic means plagal 75 % of the time. A listener who hears the bare (5th-less) tonic
  can tell perfect from plagal without hearing V. Each realisation is correct; the issue is the share. Options for Justin: cap the
  incomplete share (e.g. about a quarter of perfect items), or add "final chord complete" to the balanced features in `earR1Fit`.
  The code comment ("no register tell") is true for register only.
- **S2 (item 7, other tiles) Counts are dropped on the US side.** "2 quavers · US: eighth notes", "4 semiquavers · US: sixteenth notes",
  "quaver, 2 semiquavers · US: eighth note, sixteenth notes", "2 semiquavers, quaver · US: sixteenth notes, eighth note". The number
  is named on the Australian side only, so these are not one to one in the sense applied to `syn`. `syn` itself is correct.
- **S3 (item 7, format) "US in brackets".** The hover reads "Australian · US: American", not "Australian (American)". This is the app's
  house form for every button hover (brackets are used in running text), so it is not a `syn` defect; if Justin's rule is brackets in
  hovers too, it is an app-wide change.

**Could**
- C1 (item 6) A strong-beat 5th that becomes a 4th while one voice is held is reported as an I2 suspension with no "was a 5th" note.
  This matches the stated rule (IC1 only when both notes are struck), but the advice would apply there too.
- C2 (item 2/3) `earR1Weights()` caches by the soprano switch only; changing `EARR1OPT.inc` at run time needs the cache cleared (it is a
  build constant, so this only matters for tests).
- C3 (item 5) The Gym legend still reads "MD modal dominant: soft pull (minor v, VII; no leading note)"; with MD_MAJOR on it could add
  "borrowed v, ♭VII in major", as the Analysis key text and climb 8 legend now do.
- C4 (outside the fixes) Vsus2 in a minor key (e.g. Gsus2 in C minor) is "C" (colour), because its 2nd is the raised 6th.

## Probes run (all under `tests/reports/checks/ic_self/`, each run against this worktree)
1. `p1_rung1.py . 20000`: rung 1 pool (686) + 20,000 items with RUNG1_SOP_BALANCE off and 20,000 on; own music21 + arithmetic checker;
   weights share; answer-prediction tells. (Items 1, 2, 3.)
2. `p2_function.py .`: 360 chord × key cases for analyse()/homes(), live Gym cards, climb 8 bars, Keys texts; with MD_MAJOR as shipped and
   with MD_MAJOR=false substituted at load. (Items 4, 5.)
3. `p3_countersubject.py . 1500`: 7,509 countersubject pairs against music21. (Item 6.)
4. `p4_syn_hover.py .`: live rhythm drill tiles, mouse hover, repeated sync, re-render. (Item 7.)
5. `p5_sop_switch_ui.py .`: 40 live rung 1 questions with RUNG1_SOP_BALANCE on; EARR1OPT.inc=false. (Items 2, 3.)
6. `tests/earlab_test.py .` and `tests/unit_test.py .`, once each: 0 failures.
