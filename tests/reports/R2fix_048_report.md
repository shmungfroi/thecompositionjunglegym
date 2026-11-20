# 0.48 R2 fixes: M-12, S-F1, S-F2, S-T1, X-12 (from IC_R2_048)

Branch `048-r2fix`, from `048-int` @ `c1d6d5c` (worktree HEAD `f6854a9`). Worktree `/home/claude/wt-r2fix`. All checks are **self-checks** by the builder.

## M-12 (Must). Chords on the 5th with no 3rd

| | |
|---|---|
| **Decision** | A sus4, bare-5th or 7sus4 chord on the 5th has no 3rd, so it has neither the leading note nor the minor 3rd. It is **D in both modes**, as it already was in major. The reasons: a suspended V is a dominant whose 4th falls to the 3rd, in either mode; a bare 5th takes its quality from context, so calling it "the minor v" claims a 3rd that is not there. What stays ambiguous (V or v) is said in the Keys text instead of being decided by colour. |
| **Change** | `isMD()`: on the 5th it now requires the minor 3rd above the root (`pcs.includes(mod(rpc+3,12))`), so v and v7 qualify and Vsus4, V5 and V7sus4 do not. On the unraised 7th it is unchanged, so VIIsus4 and VII5 in minor stay MD with the subtonic text (accepted by the re-check). `homes()` and `analyse()` both call it, so they agree. New Keys text `FTXT.D5` for a D chord on the 5th with no 3rd, in both modes: "a dominant-function chord with no 3rd, so it has no leading note either. In common-practice harmony a suspended V (Vsus4) is heard as a dominant whose 4th will fall to the 3rd, and a bare 5th takes its major or minor quality from the music around it; on its own it is open whether it will act as V (with the leading note) or as the softer minor v. In rock and folk the sus or power chord on the 5th often stands for either." |
| **Test** | `unit_test` M-12: Vsus4, V5, V7sus4, V, v, v7 in 8 tonics, major and minor. `homes()` and `analyse()` give D for the no-3rd chords and MD for v and v7. The rendered Keys text has "no 3rd" and neither "the minor v," nor "modal dominant". v and v7 still show the minor-v text. VIIsus4 and VII5 in 3 minor keys give MD. |
| **Result** | Pass. |

## S-F1 and S-F2 (Should). The climb 13 countersubject note and labels

| | |
|---|---|
| **Change** | **Labels** now give the real register at that beat, not the list the issue came from: "CS above the subject: …" and "CS below the subject: …" for the written position; "CS an octave lower, above / below the subject: …" for the inverted one. **IC1 and the note** are given only for an I1 (strong-beat) perfect 4th or 11th in the lower position that was a perfect 5th or 12th as written. The note now reads "This 4th was a 5th before the voices swapped: avoid 5ths on strong beats in invertible counterpoint." A 4th that came from an 11th above (the CS stays above), or a CS written below whose 4th becomes an 11th, is plain I1 in both positions with no note. I2 issues (weak beat, both voices move) never get the note. The fugue-tab text now says "as you write it (normally above the subject) and an octave lower (normally below it), and each message says where the countersubject is". |
| **Test** | `counterpoint_test` section O. The register label is checked against the pitches on every countersubject issue (5,171). IC1 and the note are expected exactly when music21 calls the lower-position interval a perfect 4th or 11th **and** the written-position interval a perfect 5th or 12th (2,577 issues). Targeted cases in C major: R2-SF1a (CS F5 over C4, an 11th): both positions I1, "above", no note. R2-SF1b (CS G3 under C4): labelled "below", no IC1, no note. R2-SF1c (CS G4 over C4): IC1 with the note, "below". R2-SF2 (weak-beat P4 from a P5, both voices moving): I2, no note. |
| **Result** | Pass, all four cases and the corpus. |

## S-T1 (Should). Rhythm tile hovers pair one to one

| | |
|---|---|
| **Change** | `termBtnSync`: for a `data-tt` button, the terms in its own title are now mapped in order with repeats kept. Terms in the visible face are still de-duplicated, as before. `syn` now reads "quaver, crotchet, quaver · US: eighth note, quarter note, eighth note". |
| **Test** | `unit_test` S-T1: every tile in `ELTITLE` is rendered with `earRhyTile` and synced. The number of comma-separated values must equal the number of US names, and `syn` must be exact. |
| **Result** | Pass, 9 tiles. terms_test, run alone, also passes (see below). |

## X-12 (pending Justin; behaviour unchanged). Major-key v and ♭VII made consistent behind one switch

| | |
|---|---|
| **Change** | `const MD_MAJOR=true` (next to `isMD`). It now gates (1) the borrowed-chord clause in `analyse()`; (2) **climb 8** `c8Bars`, where a bar whose function is MD keeps MD (rose border, rose-tinted `.bar.sec.md`) instead of being forced to colour, and the climb 8 legend adds "borrowed v or ♭VII: a modal dominant, soft pull (no leading note)" when such a bar is shown in a major key; (3) the Analysis numeral key, which now reads "the minor v and the subtonic VII in a minor key, and borrowed into major (v, ♭VII)". Set it to `false` and analyse() gives C again, climb 8 goes violet and the key text drops the major clause: a one-line switch. |
| **Not changed** | The Keys (Seed) legend "(minor v, VII; no leading note)": the Keys room lists only keys the chord is diatonic in, so a borrowed ♭VII never shows MD there. Climb 7's bars force colour only for secondary dominants; any other chord already takes its own function. |
| **Where major MD shows (with the switch on)** | Gym (palette, cards, frame numerals), Oracle (♭VII card at level ≥ 5), Voicing lab SATB numerals, Analysis "My progression" function row, climbs 4, 5 and 11 (bar and numeral colours), and now climb 8 (♭VII and v bars, plus the legend item). |
| **Test** | `unit_test` X-12: the climb 8 ♭VII bar in C major I–♭VII–IV–I carries `var(--md)` and the `md` class; the source has the switch and the conditional key text. |
| **Result** | Pass. |

## Suites

| Suite | Result |
|---|---|
| unit_test | pass, 859 checks (was 761) |
| content_lint | pass |
| counterpoint_test | pass, 0 failures (O-1 to O-4, R2-SF1a/b/c, R2-SF2) |
| layout_test | pass, 272 views, 0 findings |
| pageerrors_test | pass, 153 views + 881 random clicks, 0 errors |
| terms_test (alone) | pass, 153 views, 0 failures. Its M3i expectation for `syn` was updated to the corrected hover (the first run failed only on that hard-coded old string). |

## Open

- C-F1, C-F2, C-12a and C-T1 (Coulds) and S-T2 (content lint gaps) were not in this brief and are not done.
- X-12 waits on Justin; `MD_MAJOR` is the switch.
