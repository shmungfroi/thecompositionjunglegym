# Ear Lab 0.49 ladder UI, second pass (Sonnet)

Branch `049-ladder-ui2`, from `049-int` (Fable's fixes kept; `origin/049-int` with the terms_test fix merged in). Engine logic untouched. All checks below are self-checks.

## Done

| Item | What changed |
|---|---|
| M1 | `earMelPerSys(q)`: a system holds one bar when the item's shortest value (the answer's, and after the check the student's too) is a semiquaver and two bars would give it under 26 px (width of the stave minus about 100 px for clef, key and time, halved, times 105 over the longest bar). Results: every 4/4 and 3/4 bar with semiquavers on phones, 4/4 at 1366. `earMelSystems` and so the stave, the reveal and the bar map follow; the bar map has one button per bar and scrolls sideways inside its row above six (`.el-sysmap.many`). |
| M2 | Bravura `rest16th` (U+E4E7, from VexFlow's Bravura outline, converted) added to ELGLY; used for 105 ticks in the palette key and in the stave (a semiquaver rest on the stave was also drawn as a quaver rest). |
| S1 | Phones, rhythm rung 10: for each half bar a kick row over a snare row, four cells each (about 82 x 44), "K" and "S" at the left, "Bar n" as the caption of the first half. Desktop unchanged. |
| S2 | 5/4 and 7/8 reveal at 1366: lines pair up (upbeat and bar 1 on line 1, then one bar a line), each of yours over the same line of the answer; "You wrote" / "It was" label the first pair. |
| S3 | Rung 11: the wrong part gets the rung 4 to 10 sentence with its name in front ("Melody, bar 1: the second note is d: you wrote d'"), rhythm sentence when only the rhythm is wrong. |
| S4 | Rung 11 bass ladder: shown names count octave marks from the bass's own do (two octaves down, display only; `data-earsol` and engine names unchanged); one line above the ladder says so. |
| S5 | Digits 1 to 7 choose a length when focus is on the page body or anywhere inside `#earMain`, except in a text field. |
| S6 | The double rule stands before the first rest key only (`.el-len:not(.rest)+.el-len.rest`). |
| S7 | Not mine (Content). |
| terms | The coordinator's 22 terms_test failures: the palette keys (lengths and rests) carry `data-tt`, so each gets its US hover ("Crotchet (US: quarter note)", "Semiquaver rest (US: sixteenth rest)"...). The rung 2 prompt and the rhythm tile table were stale in the test, not in the page: rung 2 now has two bars ("two bars (US: measures)"), and the new cells `w` and `hd` are in the expected hover table. No check loosened; the two edits make the test expect what the 0.49 engine gives. |

Fable's changes kept: F1 to F5, the 7/8 beat count, the gauge, stem-down room, Nearly octave marks, rung 11 system line and labels, drum rows at the reveal, the two-row palette, the home-key sentence.

One change to a test of Fable's: the names check in `ladder_ui_test` E2E read "the last `.el-sys`"; with S2 the answer has several lines at 5/4 and 7/8, so it reads the first answer line.

## Tests (run one at a time)

| Suite | Result |
|---|---|
| layout_test | 324 views, none with findings (6 new views: rung 12 semiquavers 4/4, 3/4 and result, rhythm rung 10, rhythm rung 9 7/8 result) |
| ladder_ui_test | 214 checks, 0 failed (new: M1 bars to a system and bar map at both widths, M2 rest keys differ, S6 one double rule, S5 digit with focus on a ladder row, S4 note and marks, S1 rows, S2 pairing, S3 sentence) |
| earlab_ui_test | 469 checks, 0 failed |
| pageerrors_test | 0 errors |
| unit_test | 0 failures |
| content_lint | passed |
| terms_test | full run, 0 failures (153 views, 2,350 clicks, 2,239 counted checks) |

## PNGs

`tests/reports/ladder_ui2_049/png/` at 1366 and 390 (made with `shots.py` here, a copy of Fable's with the output folder and four scenes added): `pal_r12_semi44`, `pal_r12_semi34`, `res_r12_semi`, `res_r11`, `two_r11_bass`, `rhy_r10_lanes`, `rhy_r10_result`, `rhy_r9_78_result`, `rhy_r9_57_result`, and `rhy_r10_lanes_390_drums.png` (the lanes as a phone shows them).

## Notes and gaps

- The 26 px rule is an estimate (proportional time spacing); at 1366 a 3/4 bar with semiquavers stays two to a system.
- Layout choice reads the item's answer for "has semiquavers", the same data the bar count already uses; the layout does not move as notes are written.
- S4: "the bass's own do" is taken as two octaves below the melody's do, the bass ladder's own offset in the engine.
- No real phone.
