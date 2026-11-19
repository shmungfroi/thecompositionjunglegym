# CP 0.48: Justin's answers 8, 9 and 10 (climb 2 counterpoint)

Branch `048-cp`, from v0.48 (`075e6c1`). Worktree `/home/claude/wt-cp`. All checks below are **self-checks** by the builder (no independent check yet).

Not in scope, deferred by Justin ("come back to this later"): register addendum **R19–R22** (raised leading note against the unraised 7th in eight models; mixed fourth species S4d; mixed third-species entry note; mixed species M2/M3/M6 and double-reported parallels). None of them was fixed. Where my changes touched the same code (message wording in `c3Check` and `c3mCheck`), the behaviour was left as is: only the wording of the interval names changed.

## Answer → change → test → result

### 8. Tied unison in fifth species stays a warning; the H4 card matches

| | |
|---|---|
| **Change** | `C2RB` H4 tag: "Must 1–3, 5 · Should 4" → **"Must 1–3, 5 (new notes) · Should 4, 5 (tied notes)"**. Text: "No unison in the middle of first species, or from a new note on a downbeat in second, third or fifth species. In fourth species a unison is allowed but use it sparingly. In fifth species a tied note may make a unison on the downbeat, as in fourth species; use it sparingly." The checker is unchanged: it already warned (R12, CP-2). The card stays a "Must" card (its tag begins with Must), as its first three species are. |
| **Test** | `counterpoint_test.py` section N-8: the tag and text, read from the page; over all 10,980 two-voice counterpoints of section C, every H4 in fourth species is a warning, every H4 on a tied florid downbeat is a warning, and every H4 from a new note on a florid downbeat is an error. |
| **Result** | Pass. H4 in section C: species 5 tied: 407 warnings; species 5 new note: 142 errors; species 4: 852 warnings; no other combination. Against the unchanged 0.48 the card tests fail (the severity test passes, as it should: the behaviour was already right). |

### 9. S3d into the final bar: both checkers follow the card; the two-voice checker warns

| | |
|---|---|
| **Change** | `c2Check`: the S3d block no longer leaves out the final downbeat (`v.a!==N-1` removed). The three-voice mixed checker (`c3mCheck`) already included it, so it is unchanged. Both now warn (S3d is a Should). No model was changed. |
| **Test** | The test's own rule-book checker drops the same exclusion (the card has none). N-9: (a) for each third-species two-voice model, the penultimate downbeat is replaced by a note that makes the same perfect interval as the final with no error: found for 4 models (Ionian and Lydian, above and below); each gives S3d **warn** on attacks 35 and 39 and agrees exactly with the rule book; (b) the same for the mixed third-species models: found for 2 (`dormid23`, `dorhigh13`), S3d warn on bars 10–11; (c) counts in the corpora: 320 two-voice and 32 mixed S3d messages into the final bar, all warnings, all agreeing with the rule book; (d) no two-voice model gets S3d into the final bar. |
| **Result** | Pass. Against the unchanged 0.48, section C fails on every solver/mutation case with a final-bar S3d (the app was silent) and the N-9 two-voice cases fail. |

Note: some two-voice **solver outputs** (not models) now carry this S3d warning, e.g. Ionian third species above. The solver only rejects errors, so this is expected and is no change to the models.

### 10. Interval names spelled out in all counterpoint checker messages

| | |
|---|---|
| **Change** | New helpers after `c2Iv`: `c2IvName(iv)` ("perfect 5th", "diminished 5th", "major 10th", "augmented unison"; a perfect unison and octave are just "unison" and "octave", as in the Keys room) and `c2IvA(iv)` with the article ("an augmented 4th", "an octave", "a minor 7th"); `c2Ord`, `c2Art` (a/an, including "an 11th"). Every `iv.name` / `o.name` in a message of `c2Check`, `c2CantusCheck`, `c3Check` and `c3mCheck` now uses them (27 places). Also fixed by hand: "into a octave" → "into an octave" (two-voice and three-voice direct octaves), "a leap of a octave" → "an octave", "spans a 11th" / "are a 11th apart" → "an 11th". The short names (`iv.name`, e.g. P5) stay in the data, where tests and code compare them. The 11 stored rule-card messages ("The checker says: …") were regenerated from the checker so they match it word for word. No terms were added; the messages keep crotchet, minim, quaver, and no US brackets were written by hand. |
| **Test** | N-10: every message the four checkers give over the whole corpus (sections C, D, E, F and the 24 rule cards: 205,663 messages, 19,796 distinct) is read. With the exercise's pitch names removed (and the notes a step either side, for "resolve to A3"), no `\b[dAPMm]\d+\b` remains; no abbreviation follows "a", "an" or "dissonant" in the raw text; no "a augmented/octave/11th", no "an perfect/major/minor/…". Also `c2IvA` for all 11,025 ordered pairs of 105 pitches (C2–B6, flat/natural/sharp) against music21's own interval name. |
| **Result** | Pass. Against 0.48 both N-10 checks fail. The music21 sweep first caught "doubly altered 0th" for crossed doubly-altered seconds such as E♯/F♭ (c2Iv's generic number is 0 there); `c2IvName` now gives "doubly altered 2nd". Climb 2 never produces flats, so students could not meet it. |

## Rule cards re-verified

Section C re-checks all 24 rule-card examples on every run: each "follows" example has no error (apart from the stated fragment H2 waiver), and each "breaks it" example shows exactly its own fault, by the app and by the test's own rule book. All 24 pass after the S3d change (no S3 card example reaches a final-bar S3d) and after the message changes. The H4 card's examples (first species) are unchanged.

## Suite results (self-checks)

| Suite | Result |
|---|---|
| counterpoint_test | **pass, 0 failures** (316 s); 29 regression cases, all pass (15 R12 + 14 new N); 10,980 two-voice, 1,845 three-voice, 3,276 mixed counterpoints; 4,006 cantus lines; 205,663 messages read; 11,025 + 11,025 interval names vs music21; 0 page errors |
| counterpoint_test against unchanged 0.48 (`075e6c1`) | fails as intended: 335 failures (final-bar S3d disagreements, card tag/text, abbreviations, helper missing) |
| unit_test | pass, 637 checks, 0 failures |
| content_lint | pass |
| terms_test | pass, 0 failures, 153 views, 2,499 page scans. The first attempt, with a 590 s limit set by me, produced no output while other agents' browsers were running (it was too short, not a crash); it passed on the next run with a 45 min limit. It ran against the code before the report-only commit; index.html is identical. |

## Gaps and open points

1. **Climb 13 not changed.** `c13Pair` (canon, stretto, countersubject) still writes "a P4", "(M2)" and so on, and `c13` code tests the message text for "a P4". It is a counterpoint checker, but outside climb 2 and outside this brief (other agents edit other parts). Recommend the same helper there in a follow-up.
2. The climb 2 ladder's hover title still shows the short name ("A4 against D4: P5"). It is a tooltip, not a checker message; left as is.
3. The two-voice and mixed S3d differ in one edge: two-voice needs the species voice to move, mixed needs both voices to move. Not part of answer 9; unchanged.
4. R19–R22 untouched (see top).
5. The new N-9 case-building finds 4 two-voice and 2 mixed models where a single note change yields a clean final-bar S3d; thresholds are set at those counts (deterministic).
