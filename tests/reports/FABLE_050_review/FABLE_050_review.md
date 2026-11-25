# FABLE_050_review: design check (Fable)

25 Nov 2026. Build checked: `050-levels` at f08f1cc (V3 to V7 and V10 merged), against `tests/reports/fable_050/DESIGN_050.md`, `levels050.css` and the mock renders.
This is a design check by the author of the spec. It is not a functional test pass and no test suite was run.
`index.html` was not edited. Everything here is under `tests/reports/FABLE_050_review/` (`png/` renders, `tools/` scripts, `*.json` raw measurements).

## Verdict: CHANGES NEEDED

Two Musts. Both are small. Apart from them the build is what I designed: `levels050.css` is in the file byte for byte, the three bands, the level list, the compact cards and the 21-rung picker match the mocks at every width, and nothing reads as templated.

- **M1.** The filled gold "your level" disc is missing from the top bar and the level list on every page load, and it disappears again after every room change and every Play.
- **M2.** On laptops the Chord Library side panel is taller than the window when the page opens, so the selected chord type and the Inversion buttons are off screen and the ROOT label is cut.

M1 is partly my fault: the spec named the state `.lvm.now`, and the app already uses `.now` for "playing now".

## What passed

| Check | Result |
|---|---|
| Sideways scroll | None at 1440, 1366x768, 1280x800, 1024, 820, 390, 360, in the top bar, level list, More sheet, Chord Library (Levels 1, 4, 7), Forms and Climbs (Levels 2, 5), Ear Lab melody and cadences (Levels 1, 4, 7), Keys, Voices |
| Text under 11 px | None in anything 0.50 added. Older items remain: `.plbl` 10 px on phones, `.stp` 10 px in Keys |
| Phone tap targets under 44 px | None in anything 0.50 added, except the rung tabs at 360 px (40 x 44, accepted in decision 7). Level rows 52, chord rows 46, band headers 44, rung cells 48, chord-type button 48. Older items remain: sheet close 36 x 28, Journal in the sheet 36 high, search 38 high, root pads 40 x 40 and 40 x 22 |
| Keyboard through the level list | Tab reaches the button; Enter opens with focus on the checked row; Up, Down, Left, Right, Home, End move, select and wrap; Enter, Space and Esc on a row close and return focus to the button; only the checked row is in the tab order. Two gaps: S1 |
| Focus rings | 2 px ring on the level button, level rows, curriculum select, band summaries, compact cards (offset 2 px) and chord rows (inset). None clipped (`E_focus_montage.png`) |
| Reduced motion | With `prefers-reduced-motion: reduce` no transition or animation is left on any 0.50 control. Without it the only motion is the 0.15 s colour and caret transitions in the spec |
| Colour-blind simulation of the three marks | Protan, deutan, tritan (Machado, full severity) and greyscale: filled disc, solid ring and dashed ring stay distinct in all five (`E_marks_cvd.png`) |
| Approved wording | The seven level descriptions and the four Stage hints match the approved text exactly. Each description sits on one line at every width |
| Curriculum None | Hints go from the button, the list header, the rows, the `aria-label` and the rung line; the name centres on its own in the button |
| Top bar | Search field 420 px from 820 to 1440, 366 at 390, 336 at 360. Level button shrinks to disc and caret at 820, Journal to its icon. Fits at 1024 with Stop showing |
| Ear Lab picker | 21 slots in one row above 900 px (cells 33 to 37 x 32); seven tabs over three rungs at 820, 390, 360; a tab change leaves the rung in use alone; `you`, `has`, `none`, `open` states as designed |
| "AI-generated" look | No stray emoji, no decorative gradients (the green-to-pink bar appears only as "you are here"), radii stay in the existing family (10, 12, 14, 18, 22), spacing between bands is 26 px desktop and 22 px phone as specified |

## Findings

| id | Where | What I saw (file in `png/`) | Spec | Level | Exact fix |
|---|---|---|---|---|---|
| M1 | Level button, level list (popover and More sheet), "New at Level n" headers, Ear Lab caption | On a fresh load the current level's mark has class `lvm lg`, not `lvm lg now`: an empty ring where the mock has the filled disc (`A_top_montage.png` rows 1 to 5, `A_list_open_1366.png`, `A_list_open_360.png`). It fills when a level is picked, then empties on the next room change. Pressing Play in the Ear Lab empties the picker caption disc too. Cause: `stopAll()` (line 3063) runs `document.querySelectorAll('.now').forEach(e=>e.classList.remove('now'))`, and it runs at load, on every route change and on every stop. Trace in `e_checks.json` under `nowstrip` | 0, 1.2, 1.3 | **Must** | Line 3063: change the selector to `'.now:not(.lvm)'`. Add a test: after load, after a rail click and after Play in the Ear Lab, `#lvBtn .lvm` and the checked row's `.lvm` have class `now`. (Longer term, rename the level state to `.lvm.cur` in CSS and markup so the two meanings cannot meet again.) |
| M2 | Chord Library, 1100 px and up | Fresh load at 1366x768: the panel runs from y 195 to 875 in a 768 px window. The selected row (Bm7) is at y 837, Inversion is at y 1100 inside the panel's own scroll, and the panel has scrolled itself 25 px so the ROOT label is cut (`F_lib_fresh_asbuilt_1366.png`; at Level 4 the root pads are cut in half, `B_lib_L4_1366.png`). Same at 1280x800, 1440x900 and 1100x700. The whole panel scrolls as one, so Root and Inversion scroll away from the list | 2.2 (panel was mock scaffolding), 2.4 items 2 and 4 | **Must** | Make only the list scroll; pin Root above it and Inversion below it. Add after the existing `@media (min-width:1100px)` block: `#room-seed>#picker{display:flex;flex-direction:column;overflow:hidden;max-height:calc(100vh - 212px)}` `#room-seed #picker>.prow{flex:none}` `#room-seed #picker>.prow2{display:flex;flex-direction:column;flex-wrap:nowrap;align-items:stretch;gap:0;flex:1 1 auto;min-height:0;margin:0}` `#room-seed #picker .prow2>.prow:first-child{display:flex;flex-direction:column;align-items:stretch;gap:0;flex:1 1 auto;min-height:0;margin:0}` `#room-seed #picker .prow2>.prow:first-child>.plbl{flex:none}` `#room-seed #picker #qualPads{display:flex;flex-direction:column;flex:1 1 auto;min-height:0}` `#room-seed #picker #qualList{flex:1 1 auto;min-height:0;overflow-y:auto;overscroll-behavior:contain;padding-right:4px}` `#room-seed #picker .prow2>.prow:last-child{flex:none;margin:10px 0 0;padding-top:10px;border-top:1px solid var(--line)}` `#room-seed #picker .ip span{display:none}` (short inversion pills, as in the mock; the bass note is already in the Seed card). Trialled by injecting this CSS, not by editing the file: at 1366x768 Root, the selected row and Inversion are all on screen, list area 284 px (`F_lib_fresh_fix_1366.png`); also checked at 1100x700, 1280x800, 1440x900, no sideways scroll. The builder must run the suites on it |
| S1 | Level popover | Esc while focus is on the Curriculum select does not close the popover. Tabbing past the select moves focus to Journal and leaves the popover open (`e_keys.txt`) | 1.8 item 4 | Should | In the level-control block: close on Esc from anywhere inside `.lvc` (`if(e.key==='Escape'&&!pop.hidden&&e.target.closest('.lvc')){closePop(true)}`), and add `document.querySelector('.lvc').addEventListener('focusout',e=>{if(!pop.hidden&&e.relatedTarget&&!e.relatedTarget.closest('.lvc'))closePop(false)})` |
| S2 | Ear Lab rung tabs, 900 px and under | After a tab is pressed the picker re-renders and focus falls to `body`; a keyboard user starts again from the top | 3.5 item 9 | Should | In the tab handler set `EAR.focus='.el-ltab[data-band="'+n+'"]'` before `renderEar()` (the same mechanism Play uses) |
| S3 | Chord-type sheet, under 1100 px | After a row is picked the sheet closes and focus falls to `body` (the button is rebuilt by `render()`) | 2.2 Phone | Should | After the sheet closes: `document.getElementById('qualBtn').focus()` |
| S4 | Chord-type sheet, 761 to 1099 px | Rows are 32 px and band headers 30 px in the tablet sheet (`B_lib_sheet_L4_1024.png`); these widths are touch tablets | 2.2 (46 and 44 on phones) | Should | `@media (max-width:1099px){#qsheet .lvrow{min-height:46px}#qsheet .lvbh{min-height:44px}}` |
| S5 | Ear Lab rung line: Cadences, Bass and numerals, Blind analysis | The line stops at "Rung 5 of 21 · Level 2, Foundation (≈ NSW Stage 4)" with nothing about what the rung holds (`D_ear_cad_L4_1024.png`) | 3.4 | Should | Nine short phrases, one per written rung, added to `earRungWhat`. The wording is Justin's to approve; the mock's "perfect or plagal, in root position" was illustrative |
| S6 | Ear Lab, Melodic dictation, before the first Play | The instruction reads "then null clicks count you in" (`D_ear_mel_L4_1366.png`, `D_ear_mel_L4_390.png`). `earMelAsk` (line 9135) prints the click count before a question exists. The same code is in the base commit 339c696, so it predates 0.50; the new first-visit rule now lands more students on these rungs | not in spec | Should | Line 9135: replace `(ELNUMW[n]||n)+' clicks count you in'` with `(n?(ELNUMW[n]||n)+' clicks count':'clicks count')+' you in'` |
| S7 | Climbs gallery | Sorted by level, the compact cards read Climb 1, 3, 4, 5, 11, 6, 8, 2, 7, 9, 13 (`C_climbs_L5_1366.png`). The rule is working as designed, but the climb numbers now look out of order, and Reharmonisation (Climb 11) sits at Level 2, ahead of the cycle of 5ths | 2.1, 2.3 | Should (decision for Justin) | Either drop "Climb n ·" from the compact card's small line and keep the family only, or keep it and accept the jumps. Check Climb 11's Level 2 floor against Retag 05 first (I could not read the project docs here) |
| S8 | Chord Library at Levels 6 and 7 | The level list promises "11ths, 13ths, augmented 6ths" and "altered dominants, quartal and slash chords", but the library's highest chord type is Level 5, so Level 7 shows "New at Level 7 · 0" (`B_lib_L7_1440.png`). The empty-band line itself is as specified | 2.1 | Should (content, not layout) | Add the Level 6 and 7 types (Chord Library Expansion Framework) before the descriptions are seen by students, or hold the two descriptions back until then |
| S9 | Keys & Scales, scale and interval pickers | A 430 px list on the left of a full-width card with the right half empty (`E_keys_L4_1366.png`). No layout was specified, so this is a gap in my spec | 2.2 | Should (later) | Leave for 0.50. Give Keys the same side-panel layout as the Chord Library (with the M2 fix) in the Chord Library layout pass |
| C1 | Ear Lab picker, 901 to about 1100 px | A single "not yet" cell is 40 px wide there, so the words sit on one line touching both edges (`D_ear_cad_L4_1024.png`); at 1280 and up they wrap to two lines as designed | 3.2 | Could | For `.el-ny` with `--n:1` above 900 px: `padding:0 5px;white-space:normal;word-spacing:100vw;line-height:1.05` |
| C2 | Ear Lab card tag, 360 px | "RUNGS 4 TO 13 · 3 WRITTEN" breaks before the last word (`D_ear_cad_L4_360_tab6.png`) | 3.6 | Could | `@media (max-width:380px){.el-tag{letter-spacing:1.5px}}` |
| C3 | Climbs, full card | The small line reads "BEYOND · LEVELS 5 TO 7"; the spec said family only | 2.3 | Could | Leave. It is a level range, not a curriculum hint, and it is useful on a climb that spans levels |
| C4 | Keys & Scales rows | Whole-tone and Chromatic carry the small name "Beyond", which describes nothing | 2.2 | Could | Use "six whole tones" and "all twelve notes", or leave the small name empty |
| C5 | Climb pages | The function legend prints as "TtonicPDpre-dominantDdominant…" (`E_climb3_L4_1366.png`). `.fnkey` has no CSS in this build or in the base commit, so it predates 0.50 | not in spec | Could (not 0.50) | Log for the next pass |

## Rulings on the stated deviations

| Deviation | Ruling |
|---|---|
| Chord Library: side panel from 1100 px, button and sheet below 1100 | **Accept** the breakpoint and the tablet sheet (560 px wide, centred, same component). **Change** the panel's insides (M2) and the tablet row heights (S4) |
| Climb example pickers keep `.cad` cards inside the bands | **Accept.** The cards carry the chord string and the one-line feel, which a two-field row would lose. The rail, the marks and the headers are the same as the row lists, so the rule still reads as one rule (`E_climb3_L4_1366.png`, `E_climb3_L4_390.png`) |
| Level popover 376 px wide, 52 px rows | **Accept.** 52 px is the height I gave for rows with a description (decision 5). At 376 px every approved description sits on one line at every width; at 340 the Level 6 line would wrap |
| "Rungs 8 to 9, not yet written" for a run of two | **Change** to "Rungs 8 and 9, not yet written" (the `aria-label` only). "8 to 9" reads like a range of more than two. In the build this shows as "Rungs 7 to 8" and "Rungs 14 to 15" |
| Only melody and rhythm show Last 10 and the suggestion | **Accept** for 0.50. Readiness is recorded for those two drills only, and an empty Last 10 on the others would be decoration. My cadence mock showed an empty Last 10; that was illustrative. Log "record readiness for the other five drills" as a future item |
| No rung description for cadences, bass, blind | **Change** (S5). It needs nine phrases approved by Justin, so it can follow the two Musts and need not hold them up |

Smaller build notes I also accept: band header ranges taken from the levels actually present; `lvReveal` scrolls only inside a list's own scroll area; the Forms and Analysis levels marked provisional stay provisional until the Retag values are applied.

## What I did not check

- Real phones or tablets, touch, Safari, Firefox. Headless Chrome only, one browser at a time.
- A screen reader. I read the `aria-label`s and roles in the DOM; I did not listen to them.
- No test suite was run (`unit_test`, `ordering_test`, `rungs_picker_test`, `layout_test` and the rest). The builders' counts in their reports are unverified by me.
- The M2 CSS was trialled by injection at four laptop sizes only. It has not been through the suites or checked with three-note chords at every level.
- The Analysis score gallery, the climb 2 cantus chips, the intervals picker and the Voices page were rendered or measured for overflow only, not reviewed as designs.
- The other five Ear Lab drills (only melody and cadences were rendered). The suggestion ring and a filled Last 10 were not seen, because no answers were recorded.
- Widths between the seven sizes, apart from 1100 in the M2 trial. Browser zoom. Contrast ratios. Hover states.
- A side-by-side with 0.49. "Predates 0.50" in S6 and C5 rests on the same code being in base commit 339c696, not on running that build.
- The project docs (Levels Framework, Retag 01 to 09): not readable from this session, so no level tag was checked against them.
- Fonts and VexFlow were served from the existing harness install in `/home/claude/cjg/tests/harness/node_modules` (read only), since this clone has none. The page was loaded from `file://`.

## Fixes applied

25 Nov 2026, branch `050-fablefix` (from `050-levels` at f08f1cc), not pushed. Fixes are in commit 341da37; this section and the review files are in the commit after it.
S7 and S8 were added to the round after Justin approved them on 25 Nov. S5, S9 and the Coulds are untouched.

| id | What changed in `index.html` |
|---|---|
| M1 | `stopAll()` now clears `.now:not(.lvm)`. The disc stays filled on the level button, both level lists, the "New at Level n" headers and the Ear Lab caption. The rename to `.lvm.cur` is still open |
| M2 | The CSS block from the finding, inside `@media (min-width:1100px)`. One addition: the selected row is revealed again after the Inversion row is drawn. Without it a five-note chord (m9) pushed the selected row 2 px under the list edge |
| S1 | Esc anywhere in the level control closes the list and returns focus to the button. Focus leaving the control closes it. Tab from a row to the Curriculum select keeps it open |
| S2 | The rung-tab handler sets `EAR.focus` to the pressed tab |
| S3 | After a pick in the chord-type sheet, focus goes to the chord-type button (done after `render()`, which rebuilds the button) |
| S4 | `@media (max-width:1099px){#qsheet .lvrow{min-height:46px}#qsheet .lvbh{min-height:44px}}` |
| S6 | Before the first Play the melody instruction reads "then clicks count you in" |
| S7 | Compact climb cards show the title and the family ("Harmony", "Jazz"), with no "Climb n" in the small line or the `aria-label`. Full cards and the climb page keep the number |
| S8 | Chord Library only: when the level is above the highest chord type written, the empty band reads "No new chord types at Level 7 yet: they arrive in a later update. Everything you have met is below." |
| aria | A run of two unwritten rungs reads "Rungs 7 and 8, not yet written". One is "Rung n", three is "Rungs a to c" |

Two choices to confirm:

- **S7.** I kept the family on the small line, as the Forms compact cards do. If "title only" meant no small line at all, it is a one-line change.
- **S8.** The later-update line is switched on for the Chord Library only (`later:true` in `qualList`), and only when nothing is written at that level or above. Scales, intervals, forms, climbs and scores keep the plain "No new … at Level n." line, because I cannot say that content is coming for them.

### Tests (headless Chrome, one browser at a time)

| Suite | Result |
|---|---|
| `tests/level_mark_test.py` (new: M1, M2, S1 to S4, S6, S7, S8, aria) | 590 checks, 0 failed |
| `tests/rungs_picker_test.py` (one expectation changed for the new label) | 3715 checks, 0 failed |
| `tests/ordering_test.py` | 147 checks, 0 failed |
| `tests/pageerrors_test.py` | 357 views, 10099 clicks, 881 random clicks, 0 page errors (about 25 minutes) |
| `tests/layout_test.py` | **Fails, same as the base commit:** 332 views, 16 with findings. All 16 are the "6" over "4" figure overlap in the Ear Lab cadence card. f08f1cc gives the same 16 views |
| `tests/content_lint.py` | **Fails, same as the base commit:** 7 `stage_wording` findings on the Stage hint table (line 2236). f08f1cc gives the same 7. Every other group is clean |

M2 re-rendered from the file on a fresh load (`tools/g_fixed_m2.py`, numbers in `g_fixed.json`, renders `png/G_lib_fixed_*.png`):

| Window | Panel | Root label | Selected row (Bm7) | Inversion | Sideways scroll |
|---|---|---|---|---|---|
| 1100x700 | 195 to 683 | 210 | 528 to 560 | 608 to 670 | none |
| 1280x800 | 195 to 783 | 210 | 628 to 660 | 708 to 770 | none |
| 1366x768 | 195 to 751 | 210 | 596 to 628 | 676 to 738 | none |
| 1440x900 | 195 to 883 | 210 | 728 to 760 | 808 to 870 | none |

`level_mark_test.py` also checks the panel at these four sizes at Levels 1, 4 and 7 with the first, middle and last chord type selected.

Not done: `level_mark_test`, `ordering_test` and `rungs_picker_test` are not in the `tests/run_all` list. The other suites (`unit_test`, the Ear Lab suites, `transport_test` and the rest) were not run on this branch. No real device, Safari, Firefox or screen reader.
