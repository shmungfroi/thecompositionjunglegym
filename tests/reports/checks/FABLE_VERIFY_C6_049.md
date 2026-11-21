# Fable verification of C6 and C13–C16 (0.49)

Build checked: branch `049-c6`, Sonnet's commit 7bf4065 (base c49222f), plus my fixes in the commit that carries this file. Spec: `tests/reports/fable_049/DESIGN_049.md` section C6, `fn049.css`, `cvd_sim.py`; register rows C13–C17. Sonnet's report: `tests/reports/C6_UI_049_report.md`.

## Verdict: SIGN OFF

Signed off on the build with my four fixes in it (below). Two of them were Musts, and both were faults in my own spec, not in Sonnet's build: Sonnet lifted `fn049.css` and the markup notes as written.

Scripts and pictures: `tests/reports/checks/fable_c6/` (`verify.py`, `c6grid.py`, `sweep.py`, `piano.py`, `c6box.py`). Sonnet's `after_*` PNGs in `tests/reports/c6_049/png/` are re-rendered from this build, so the wheel pictures show the fix. Sizes: 1440, 1366×768, 1024, 390; climb 6 also at 800 and 360. No page errors and no sideways scroll at any size.

## What I changed

| # | Was | Now | Whose fault |
|---|---|---|---|
| F-1 (Must) | Wheel letter at `x+25, y-21` sat on the node's stroke: "PD" 3.5 px inside it, "D" 1.2 px, "T" 0.8 px (all three, not only "PD") | `x+27, y-24`, and `x+32` for a two-letter cue. Every letter now clears the stroke by 2.0 to 3.3 px at all four sizes. `.wheel{overflow:visible}` so the top node's "T" can never be clipped. `wheel_*.png` | Spec |
| F-2 (Must) | Climb 6: the function letter ran into the falling-fifth mark ("↓d5PD") when bars are narrow: 0 px apart at 390, 8 px overlap at 360, 5 to 10 px overlap at 1024 (bars are 52 px beside the wheel). `c6grid_before_*.png` | The climb 6 grid is `bargrid c6grid`, a size container. When the grid is 360 px or narrower the bars gain 16 px at the foot and the letter has a line of its own. Wider grids are untouched (least gap 14 px at 800, 22 at 1366, 33 at 1440). Bar widths are identical before and after at all six sizes. `c6grid_after_*.png` | Spec: I did not draw climb 6 |
| F-3 | `earlab_ui_test` FR-19 failed at 1440 and 390 (it asked for `accent-color` gold) | **The spec is right, the test was stale.** C5-2 draws every checkbox (`appearance:none`), so `accent-color` does nothing and `c5.css` sets it to `auto` on purpose. The test now checks what is on screen: 18 px, drawn, clear when unticked, gold ground when ticked, 44 px label row on phones | Test |
| F-4 | `fn049.css` | Kept in step with F-1 and F-2 | |

## Ruling on Sonnet's question (term-only hovers)

**Leave them as "US: quarter note". No change.**

L63 and C14 fix the order of a pair: the Australian term first, the American in a bracket after it. A hover that sits on the Australian word already has that order: the word on the page, then the gloss. Writing "stave (US: staff)" on the word "stave" repeats the word the pointer is on and adds nothing. The bracket is needed only where the hover has to name the Australian term itself, because the face of the button shows something else ("ta", "ti-ti"). That is what C14 changed and it is right.

So the rule, app-wide: a hover that names the Australian term reads "Australian (US: American)"; a hover on the Australian term reads "US: American". `terms_test` T6 already holds both. If Justin wants the literal bracket on every hover it is a small change in `termBtnSync` and the `abbr.tm` title, plus two test expectations: Could, his call.

## Checks

| Check | Result | Evidence |
|---|---|---|
| Tokens | Pass | First `:root`: `--green #9dc995`, `--red #d15e5d`, `--md #b1729d`, `--md-ivory #8b4978`; gold and violet unchanged. `FNHEX`, `COLS`, `ELC`, `VCOL`, `earMelMount` RED agree |
| No stray old hexes | Pass | `#c8473b`, `#8fbf6a`, `#bd6b97`, `#9e4776` and their `rgba()` forms: none left in `index.html` outside one comment that quotes the change. (The 0.48 design sheets under `design/` keep the old values; they are history) |
| `cvd_sim.py --check` | Pass | All rules. Worst text contrast 4.65 (D on the tile), worst pair 12.6 (PD/MD tritan, MD/C protan), as the spec table. In `run_all` as suite `cvd_sim` |
| Letter on bar grids | Pass after F-2 | Climbs 4, 5, 6, 7, 8 (both grids), 9, 10, 11 and the modal vamp. 11 px, weight 600, in the function colour, bottom right. Every climb 4 example (incl. the three 12-bar grids) and every climb 5 family, with and without the pedal, at 1366, 1024, 390, 360: least gap to the bar's text 13 px |
| Letter on the Analysis strip | Pass | Top right, 11 px. Tested with nine chords including VII (MD) and ♭II (C). `analysis_*.png` |
| Letter on the wheel | Pass after F-1 | 11 px Outfit 600, in the function colour, outside the node |
| Letter on Ear Lab chips | Pass | "**D** bass so", "**PD** pre-dominant", 11 px, in the chip's colour, in both chip builders (cadence and bass). `ear_cad_*.png`, `ear_bass_*.png` |
| `.fnkey` legend | Pass | Exactly one per grid or strip at every size: 1 in each climb, 2 in climb 8 (two grids), 1 under the Analysis strip, 1 under the Ear Lab chord row. 12.5 px. The Analysis "Functions" row no longer repeats it |
| D2(a): status red and green lifted | Pass | Verdict "Not this time" is `rgb(209,94,93)`; result washes, wrong chips, score marks, the tuner meter and the stop button all use the new red and green. One red, one green |
| C13 | Pass | "2 quavers (US: 2 eighth notes)", "quaver, 2 semiquavers (US: eighth note, 2 sixteenth notes)", "4 semiquavers (US: 4 sixteenth notes)". Reads naturally |
| C14 | Pass | All nine rhythm tiles read "Australian (US: American)". Term-only hovers as ruled above |
| C15 | Pass | `.piano .c` 11 px at all sizes; labels do not crowd (least gap 58 px at 390). `piano_390.png` |
| C16 | Pass | `.song .sb a` 44 px high, at least 78 wide at 390 (Keys and Library); 27 px on desktop, unchanged. `songlinks_library_390.png` |
| 11 px floor | Pass | Every new text is 11 px or more; `layout_test` 0 findings |
| 44 px phone targets | Pass | `layout_test` 0 findings; nothing in C6 adds a control |
| Crafted look | Pass | The letter is quiet and sits where the eye ends on each chip; the legend is one muted line. Nothing reads as bolted on |

## Tests (after my fixes)

| Suite | Result |
|---|---|
| `cvd_sim.py --check` | all rules pass |
| `layout_test` | 272 views, 0 findings, 0 page errors |
| `earlab_ui_test` | 469 checks, 0 failed |
| `terms_test` | 0 failures, run one Stage at a time (`TERMS_STAGES=4`, `5`, `6`): 51 views each; 506, 506 and 1,294 clicks scanned |
| `content_lint`, `unit_test` | passed, 0 failures |

`terms_test` as one run (all three Stages on one page, about 15 minutes) ended in Chrome's "Target crashed" three times for me, once on an otherwise idle machine; split by Stage it completes every time. I read it as the single long-lived page running out of memory on this 8 GB machine, not a defect in the app: Should, see S-3.

`earlab_ui_test` stopped twice out of five runs with Playwright's "Element is not attached to the DOM" before reaching its checks (shared machine, other suites running). The complete runs are clean. Not chased further: S-3.

Not rerun by me: `pageerrors_test` and the other `run_all` suites Sonnet lists as not run. `earlab_r2_test` has an edited expectation that nobody has run yet: run it at merge.

## Shoulds and Coulds (not blocking; new register rows, Drafted)

- **S-1** Function colour with no letter remains outside the C6 table: the Gym progression cards (`.pc`) and palette buttons, the Oracle cards (`.tc`), the Keys chord chips (`.kc`) and key chips (`.kchip`). Each shows the numeral, so the chord is never ambiguous, but the function is colour only. My table missed them. Should: give them `data-fn` in a later row.
- **S-2** Climb 6 at 1024: the bar grid is squeezed beside the wheel (bars 52 to 64 px, "copy 2" wraps, the last column runs past the card edge). Present before C6. Should: stack the wheel above the grid up to about 1100 px.
- **S-3** Test robustness. `terms_test` should open a fresh page for each Stage (or `run_all` should call it once per Stage), so a full run does not crash the tab. `earlab_ui_test` flakes under load with a detached-element error: make the step that scrolls a control wait for the re-render.
- **C-1** Keys piano at 390: the solfa names over the highlighted keys run together ("doremifasolatido"). Present before C6. Could.
- **C-2** The cadence chips read "T tonic" while the legend beneath says "T tonic" again. Harmless; Could: drop the word on chips whose small line is only the function name.

## Not checked

- No real phone and no real colour-blind reader: the simulations are a model.
- Hovers were read as text from the DOM, not seen as native tooltips.
