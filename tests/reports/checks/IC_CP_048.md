# Independent check: climb 2 counterpoint, CJG 0.48 (items 8, 9, 10)

Checked: `/home/claude/wt-check-int` (detached at `048-int`) against baseline `v0.48` (whose index.html I extracted to `/home/claude/checks/cp/base/` so both could run in the same harness). Read-only; no repo edits. Scratch scripts and raw outputs are in `/home/claude/checks/cp/`. I formed every verdict below from my own cases before reading `tests/reports/CP_048_report.md`.

## Verdict table

| Item | Verdict |
|---|---|
| 8. A tied unison in fifth species is a warning; the H4 card's tag and wording match; new-note downbeat unisons in 2nd/3rd/5th species are still errors | **PASS** |
| 9. S3d into the final bar: the two-voice and mixed checkers both follow the card, and the two-voice checker warns; no models changed | **PASS** |
| 10. Interval names spelled out with the right article; no abbreviations; no "a augmented" | **PASS** (one Could: "doubly altered") |
| Rule cards: each "follows" example has no error and each "breaks it" example shows exactly its own fault | **PASS** (24/24, using the suite's existing H2 fragment waiver) |
| Tradition tags: every rule tagged, no tradition presented as universal | **PASS** |
| Regressions (behaviour other than the intended changes) | **PASS**: across 49,430 cases, the only change in behaviour is the new final-bar S3d warnings |

There are no Must or Should findings. There are four Could findings, listed at the end.

## Evidence

### Item 8 (scripts: `t8.js`, `tui.js`)
- **Sweep.** For every built-in two-voice model (6 modes × above/below × species 1–5), I set each middle-bar downbeat in turn to a unison with the cantus and recorded the H4 result, giving 551 cases.
  - Species 5, tied downbeat: 70 cases, each with exactly one H4 **warn** ("the tied note makes a unison on the downbeat ... use it sparingly").
  - Species 5, new note on the downbeat: 42 cases, each an H4 **error**.
  - Species 1, 2 and 3 new-note unisons: 112, 103 and 112 cases, all errors.
  - Species 4: tied 102 and broken-ligature new note 10, all warnings. This matches "Should 4".
  - No failures.
- **Card.** The H4 card renders with the tag "Must 1–3, 5 (new notes) · Should 4, 5 (tied notes)". It keeps the `must` class, like the other mixed cards (S4c, M7). Its text now names fifth-species tied unisons as allowed but to be used sparingly. The tag, the text and the checker agree.

### Item 9 (script: `t9.js`)
- **My own rule.** I wrote an S3d rule independently: two consecutive downbeats form the same perfect class (5th, or octave/unison), the cantus moves, and the counterpoint moves.
  - **Two-voice:** I took every species 3 and 5 model and enumerated every pitch for each attack of the penultimate bar except the cadence note (27,252 counterpoints). The app's S3d set matched mine exactly in all cases. 4,056 of them have S3d into the final bar, all as **warn**; 71 of those are otherwise error-free, for example Dorian 3rd species above, bars 10–11.
  - **Baseline v0.48:** the same run gives mismatches only on final-bar S3d, where the app was silent. So the change is exactly the removed exclusion.
  - **Mixed:** same method on the 36 mixed third-species models (41,404 variants). The app's S3d (bars and voices) matched my rule in every case, with 7,542 final-bar warnings and no errors. The mixed code is unchanged from v0.48 apart from message wording, and it already included the final bar.
- **Models.** The `C2MODELS`, `C3MODELS` and `C3MMODELS` strings are byte-identical to v0.48 (md5 checked). All two-voice models are still error-free, and none of the third- or fifth-species models gets an S3d warning.

### Item 10 (scripts: `tiv.js` + `cmp_iv.py`, `tmsg.js` + `scan.py`)
- **Names against music21.** I compared `c2IvA` with music21's interval name for all 11,025 ordered pairs of C2–B6 (flat, natural, sharp). The names matched in every case, including compound, augmented, diminished and augmented-unison names, and "an 11th"/"an 18th". The only differences are the 1,800 doubly altered pairs: the app says "a doubly altered 4th" where music21 says "doubly augmented" or "doubly diminished" (see C-1). An extended set with double sharps and double flats (3,850 pairs) shows the same: the only differences are on the "x" quality.
- **Message corpus.** I collected 19,940 distinct messages from all four checkers: models plus random mutations in species 1, 2, 2-with-semibreve, 3, 4 and 5; 3,000 random cantus lines; three-voice and mixed mutations; and wide-spacing cases. With pitch names removed, there are **no** interval abbreviations (`[PMmAdx]\d+`) and no article errors. The same scan on v0.48 gives 10,965 hits.
  - I counted every "a/an + interval" phrase. All are correct, for example "an augmented 4th", "an octave", "an 11th", "an augmented unison", "a unison", "a diminished 5th", "a perfect 12th".
  - The rule-card texts, the 24 stored example messages and the species descriptions contain no interval abbreviations; the only matches are rule codes such as M1.
- **Stored messages.** The stored rule-card messages match the checker's output word for word in all 24 cases.

### Rule cards (script: `tex.js`)
- **Follows and breaks examples.** I ran all 24 `C2EXAMPLES` through the checker.
  - **Follows:** under the suite's established excerpt convention (H2 is waived when an excerpt starts on a consonance), no "follows" example has an error.
  - **Breaks it:** every "breaks it" example has exactly its own error. Where the card is a Should rule, the example has only its own warning.
  - **Companion warnings:** a few "breaks it" examples also carry other warnings. These are documented (H5 brings V4), or are an unavoidable H4 warning in S4c, where 2–1 resolves to a unison.
  - **Unchanged from v0.48:** the only change to the examples is the message text.
- **Tags.** Every C2RB, C3RB and C3MRB rule has a source tag in `C2SRC`, and every checker code maps to a card. S3d is tagged "later teaching", and its message says "many teachers ask you to avoid this", so it is not presented as universal. The checker messages keep the Australian terms: crotchet, minim, quaver.

### Regressions (script: `tsig.js`)
- **Base against new.** I compared the full issue signatures (code, severity, attacks, bars, voices) on 49,430 identical inputs from all four checkers. The only difference is 118 added `S3d:warn` issues, all on final-bar pairs. Nothing else changed.
- **Deferred items.** R19–R22 are not made worse. The mixed third-species entry (bar 1 beat 2 into bar 2 is still reported as a V1/V2 error), S4d and the M2/M3/M6 logic are untouched.
- **Suite.** `tests/counterpoint_test.py` on 048-int: pass, 0 failures, 0 page errors (184 s).

## Findings

There are no Must or Should findings. Could:

- **C-1. "doubly altered" is vague.** `C2QN.x='doubly altered'` gives a name that doesn't say whether the interval is augmented or diminished (music21: doubly augmented or doubly diminished). `c2Iv` also uses `x` for triply altered intervals.
  - Students can't currently reach this. Pitches come only from natural input plus a raised leading note, and the own-cantus ladder is naturals only. I only produced it with synthetic sharps in the cantus checker.
  - Fix: in `c2Iv`, set `q` to 'dd' or 'AA' from the sign of the offset, and name these "doubly diminished" and "doubly augmented".
- **C-2. Spacing and range say "a 15th".** These messages use `c2Ord`, so they say "the voices are a 15th apart", while `c2IvName` says "double octave". Both terms are correct but they are inconsistent. Fix: use "a double octave" for 15 in the spacing and range messages.
- **C-3. S3d wording.**
  - The message says "The crotchets in between soften them" for fifth species too, where the bar may hold minims or ties. Since final-bar S3d now fires in species 5, this message appears more often.
  - "octaves on two downbeats in a row" is also used for octave → unison into the final bar when the counterpoint is below the cantus.
  - Fix: use "The notes in between" when `sp===5`, and "octaves (or an octave and a unison)" when one of the two is a unison.
- **C-4. "Bars 10–10" in M6 (pre-existing, not from this change).** The M6 tritone-outline message can say "Bars 10–10" when both turning points are in the same bar, for example in third species. Fix: print one bar number when the two are equal. The climb 2 ladder hover still shows short names ("P5"), but that is a tooltip, not a checker message. The builder notes this too.

## Comparison with the builder's report (read after my verdicts)
- **Agree** on all three items:
  - Item 8: the checker already warned, and only the card changed.
  - Item 9: one exclusion removed in `c2Check`; mixed was already correct; models are unchanged.
  - Item 10: helpers added, the 27 call sites converted, the stored messages regenerated.
  - Rule cards: 24/24.
- **Agree** with the builder's gaps 1–3 (climb 13 still uses abbreviations and is out of scope; the ladder tooltip; the two-voice and mixed S3d differ on whether both voices must move). On the third, I found no case where the difference matters in two voices, because the cantus never repeats a note.
- **Extra from this check:** C-1 (the doubly altered name is imprecise, not only the "0th" bug the builder fixed), C-3 and C-4.

## What I could not check
- How the issue lists look on screen, and their US-term bracketing (that is the terms branch; out of scope here).
- Climb 13's `c13Pair` messages (outside climb 2).
- Whether musicians agree that tied florid unisons should be "sparingly" (a Should) rather than an error. The checker and card agree with the spec as Justin answered it; I did not research the sources further.
