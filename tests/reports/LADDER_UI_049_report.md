# Ear Lab 0.49 ladders: UI build report (Sonnet)

Branch `049-ladder-ui` (worktree /home/claude/wt/ladder-ui), based on `origin/049-int` with `origin/049-fable-ladderui` (Fable's spec files) merged. The engine was called only through `tests/reports/ladder_049/ENGINE_API.md`; no engine logic was changed. Everything below is a "self-check" by the builder, not Fable's verification.

## What is built

- **Stage 1, CSS and glyphs**: `ladder049.css` (minus the rules `ladder_ui.css` replaces) then `ladder_ui.css`, lifted as written; the three Bravura outlines added to `ELGLY`.
- **Stage 2, picker**: banded rung picker for melody and rhythm only (`.el-rp`, `.el-bandtab`, `.el-band`, `.el-bandmore`), Stage filter chip, phone tabs (one band open), rung line, last-10 marks (window leaves out Shown, Skipped and Nearly), suggestion row (crosses a Stage with "Rung 5 starts Stage 5"), `EAR.reached` saved with `cjg_ear`.
- **Stage 3, rhythm desk**: drawn in ticks (no 16-semiquaver assumption): simple, compound (6/8, 12/8), quintuplet and septuplet beats widened (1.3x, 1.75x), 5/4 with a dashed group line, 7/8 as groups, upbeat and short last bars as regions of a bar. Tiles for every rung (families from the rung where there are more than nine), konnakol names on 5- and 7-tuplet tiles in both settings, "Names" setting from rung 7, one big tuplet per bar, count-in sentence with grouping, per-beat marks, a time-name row at the reveal, replay of the first wrong beat. Rung 10 (not in Fable's spec): riff tiles plus kick and snare quaver lanes.
- **Stage 4, melody desk from rung 4**: duration palette (derived from the rung's cells, live-length rule through a thin adapter `earLenLive` over `ladPalette`, chosen length moves to the longest live shorter one, announced through `earLiveSay`), held block on phones, bar map and one-tap Undo, stave in ticks with engine beams and the gold marker, result with "You wrote" over "The melody", verdict first, rhythm counted in beats and solfa bar by bar in order, red head and red rule marks and key line, fa-si gauge and gap figure and bracket at rung 7, chromatic half rungs with solfa names only (no hand-sign art), rung 9 setting "Keep home do" / "Move do (mutation)", "Mutation here: so = do" button only under Move do, "was ..." labels after the pivot, "s = d" under the pivot note, the exact mutation sentence, L107 (needless mutation on a relative-key item with every note right counts as right, with the specified sentence for M-vi), first-mention gloss, rung 11 as a part switch over two stacked staves, rung 12 palette.
- **Tests**: `tests/ladder_ui_test.py` (new, in `run_all`), `tests/layout_test.py` (new views at 1440/1366/1024/390: long header, palette desk, result, rung 7, rung 9 Move do, rhythm rung 9 and its result), `tests/earlab_ui_test.py` (old 0.48 fixtures replaced with engine items).
- **PNGs**: `tests/reports/ladder_ui_049/png/` (16 views at 1366 and 390, 32 files).

## Commits (branch 049-ladder-ui)

1. `4cdce60` stage 1 CSS and glyphs; 2. `4be3a4d` picker; 3. `8e26759` rhythm desk; 4. `89b5d88` melody desk; 5. `0ed5c1c` ladder_ui_test and run_all; 6. `4d94d46` playback routing fix, placeholders, test updates, layout views; 7. PNGs; 8. this report (final hash in the summary message).

## Test counts (self-check)

| Suite | Result |
|---|---|
| content_lint | pass |
| unit_test | pass, 1099 checks |
| ladder_ui_test (new) | pass; last-10 window, suggestion, earLenLive over every rung, end-to-end right answers through the UI at melody rungs 4 to 12 (rung 9 in both settings, 12 items each) and rhythm rungs 1 to 10 (25 each), new views at 1366 and 390 (11 px, 44 px, sideways scroll, picker, setting, mutation button) |
| earlab_test | pass |
| layout_test | pass, including the new views at 1440, 1366, 1024, 390 |
| pageerrors_test | pass |
| earlab_ui_test | 469 checks, 2 failed: FR-19 (letter-names checkbox `accent-color`, 1440 and 390). The rule `accent-color:auto` comes from C5 already on 049-int (`#earMain input[type=checkbox]...`), so the 0.48 check is stale; not touched |
| transport_test | 6 fails, all "state end vs last node stop" (about 0.6 s) on rhythm rungs 1 and 2. The untouched `origin/049-int` fails the same way (8 fails); this is the engine's rhythm scheduler end time, not the UI |
| terms_test | "Target crashed" at the same place on three runs of this branch and on the untouched `origin/049-int` (same line, re-opening an Ear Lab view after a click loop). A click loop over every Ear Lab view and stage in a separate script did not crash, so I could not isolate it; not a result of these changes as far as I can tell, but the suite has not passed here |

## Bugs found by the tests and fixed

- `earSched` routed rhythm items to my melody replay adapter (a bad edit); caught by earlab_test and layout_test.
- Ladder range now widened to the notes' own semitones (chromatic notes outside the diatonic range had no row).
- Bass part of rung 11 with an upbeat (bass line starts after the upbeat) aligned to the melody's bars.

## Not matched to the spec, or gaps

1. **C6 colour tokens** are not in the app, so `--red` is still `#c8473b` (the mock expects `#d15e5d`).
2. **Palette**: ending figures (dotted crotchet; dotted minim in 4/4) are included from rung 6 because the engine's last bar can need them although the spec table does not list them. Rung 12's palette is the union of the excerpt values, up to the 7 cells plus rests (`.el-pal.two` beyond that). The engine's legal-length fixes in progress on 049-ladder-eng should be re-run through `ladder_ui_test` at merge.
3. **Setting name**: the Move do setting is stored as `EAR.mod` (the engine's name), not `EAR.do` as in the spec.
4. **Rung 11** is a Melody/Bass switch over two stacked staves (treble and bass), not a joined grand staff; no Fable mock exists.
5. **Rung 10 rhythm** drum lanes (`.el-lane`, `.el-dcell`, `.el-lanes`) are my design; no Fable mock.
6. **Replays `bar` and `a2`** ("Hear bar 2: yours, then the answer", "Hear fa to si, then fa to so") are adapters in `earSchedMel4`; the engine has no such variants.
7. **Solfa count** is by the nth note in each bar against the nth note of that bar (Fable's O4), computed in the UI, not by `ladMelMark`'s onset alignment; the journal line still uses the engine's `nRight`.
8. **Rhythm 7/8 counts**: the engine counts 7/8 in quavers, so the headline reads "24 of 28 beats"; drawn beats are the three groups.
9. **Rhythm names setting** also should change the melody reveal names; it does (the names come from the engine's `ladNameTable`). Not independently reviewed for rungs 11 and 12.
10. **Nearly at rung 10** and the **rung 9 reveal** were drawn through the real engine (PNGs) but not reviewed against a mock (Fable did not draw them).
11. The Move do setting cannot be changed after an answer (a toast says it changes at the next question); the spec did not say.
12. Digits 1 to 7 choose the nth palette cell only when focus is on the page body; arrows work inside the palette; Backspace undoes.
13. Not tested on a real phone.
