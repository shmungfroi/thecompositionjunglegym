# 0.50 V10: Ear Lab 21-rung picker (build report)

Branch `050-rungs` (from `050-levels` 339c696), single file `index.html`. Not pushed. All checks below are self-checks (the builder's own).

## What was built
- Every drill (all seven in `EDR`) now shows 21 slots in seven level groups (spec 3). Laptop over 900 px: one row with captions. 900 px and under: seven level tabs over the three rungs of the open level (CSS `display:contents`, from `levels050.css`).
- Rung number = 3 x (level - 1) + step. Written slots come from `EARSLOT`; `data-earlv` still carries the internal rung, the text carries the place. No migration (spec 3.5 item 8 handled by EARSLOT as in V9).
- Unwritten runs in a level are one `.el-ny` cell with `--n`; a level with nothing written is `.none` (one cell, n = 3). Classes `you`, `none`, `open`, `has`, `sug` as spec; aria-labels as spec.
- Behaviour 3.5 items 1-7, 9: tabs open a level without changing the rung (`EAR.band`); entering a drill (and any rung click) resets `EAR.band` so the open tab is the rung's level; first visit chooses first written rung at the learner's level, else nearest written below, else lowest (`earFirstRung`, fixed in `EAR.lvl` on first use, so a later learner-level change cannot move it); the suggestion (8 of last 10) points to the next written rung (`ladRdState` uses internal numbers); changing the learner level only moves `.you`.
- Removed: `.el-rungs`, `.el-band*`, `.el-bandtab`, `.el-bandmore`, `.el-all`, `EAR.all` (field, save, load, click handler, focus key, level-button hook), the "Show all rungs" and "n more for Stage" controls. `earDrillShown` now always true; `earRungsShown` returns all rungs.
- Rung line (3.4): `<b>Rung 10 of 21</b> · Level 4, Intermediate (≈ NSW Stage 5) · …`; bracket wrapped in `white-space:nowrap`, omitted when `curHint` returns ''. `curHint` fallback defined right after the `LVN` line, exactly as given, only if absent.
- Labels (3.6): Ear Lab drill tab sub-label "12 rungs"; card tag "Rungs 2 to 18 · 12 written" (written places, min to max). Other Stage wording untouched.
- `levels050.css` appended unchanged to the end of the main `<style>` (verified byte-for-byte contained).

## Commits
- 0.50 V10: Ear Lab 21-rung picker (index.html)
- 0.50 V10: tests (updated old-picker assertions, new picker test, screenshots)
- 0.50 V10: report

## Tests (all self-checks, run one at a time)
| Test | Result |
|---|---|
| tests/earlab_test.py | 0 failures (one assertion updated: "rungs shown by Stage" now expects all rungs at every level) |
| tests/ladder_ui_test.py | 242 checks, 0 failures (picker markup asserts now `.el-ltab` x7, 21 slots, no old classes) |
| tests/earlab_ui_test.py | 469 checks, 0 failed (focus-order query moved to `.el-lgr button`; the FR-10/11 "show all rungs" check replaced by "no show-all control; 44 px targets on phones") |
| tests/pageerrors_test.py | 357 views, 9,929 clicks, 0 errors (P2-5 sequences clean) |
| tests/layout_test.py | 332 views; 16 views with findings vs 18 on 339c696 (see below). Exit code 1 on both, as at base |
| tests/earlab_items_test.py (not on the list, but asserted the old markup) | 0 failures after updates (section U: all drills and written rungs offered at Levels 4-6, no show-all; two stale V9 assertions on the metre tag/stage fixed: 'Levels 1–3', stage from EARSLOT) |
| tests/rungs_picker_test.py (new) | 3,715 checks, 0 failures |

No marking, tell or generator assertions were changed.

New picker test covers, for all seven drills at learner levels 1-7: 7 groups, 21 slots, written slots equal EARSLOT, number = 3*(l-1)+step, `.you`/`.none`/`.open`/`.has`, first-visit rule (written out independently in the test), tab clicks leave the rung unchanged, the open tab follows the rung on entering a drill, suggestion skips 'not yet' (9 gap cases: mel 6->9, 10->12, 13->15, 16->18; rhy 2->4, 5->7, 9->11, 11->13, 13->15), learner-level change through the real level buttons leaves the rung and open tab alone, label wording with and without `cjg_curric=''`, no old markup.

## Screenshots and geometry (tests/reports/rungs_050/)
`picker_mel_{1440x900,1366x768,1280x800,1024x768,900x800,820x1180,390x844,360x740}.png`, plus `picker_cad_1440x900.png` and `picker_cad_390x844.png`. No sideways scroll at any of the eight sizes (mel, cad, metre drills). Rung cell width over 900: 33-35 px at 1440/1366, 33-34 at 1280, 35-37 at 1024 (spec measured 35/34/37; 32 at 901 not measured, 900 uses the tab layout). Rung cells 32 px high inside the 34 px pill. Phone: tabs 44 px high, rung buttons and "not yet" cells 48 px; tabs 44 px wide at 390, 40 px at 360 (accepted per decision 7). No text under 11 px in the picker or rung line.

## Deviations and ambiguities
1. Nine drills: the brief says nine, the app has seven (`EDR`/`EARSLOT`: metre, rhy, qual, cad, bass, mel, blind). All seven tested.
2. Rung line description for drills other than melody and rhythm: `earRungWhat` only exists for those two. Pulse and metre now says "metres: …", Chord quality "chords: …", from the generators' own answer sets; Cadences, Bass and numerals, Blind analysis show no description. Needs wording if wanted.
3. "Last 10" and the suggestion stay for the melody and rhythm ladders only, because readiness is only recorded for those (`ladRdPush`). The picker would show a suggestion for other drills if data existed; none does.
4. Not-yet aria for a run of two: "Rungs 8 to 9, not yet written" (the spec gives only the 1 and 3 forms).
5. Drill-tab and card tag wording is new; `earStageTag`/`EDR[2]` (level ranges) are kept because tests use them, though no UI shows them.
6. layout_test: the cadence drill now opens on its rung at the learner's level (level 6 test view opens place 13, six answers), which exposes an existing flag on the stacked "6/4" glyph of the Cadential 6/4 answer button (overlap of the "6" and "4", w 7 px) in four cad views at each of four widths. Not caused by the picker; those views previously opened on rung 1. The old 390 px mel/rhy findings (old band tabs) are gone.
7. The tip text on the Cadences card still says "Rung 3 (Stage 6) adds…"; Stage wording outside the Ear Lab labels was left to the other agent as instructed.
8. `earBands` is now unused (left in place); the stale `EAR.all` comment above `earRungs` remains.
