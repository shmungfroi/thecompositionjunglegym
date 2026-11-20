# Fable verification of C5 (0.49)

Build checked: branch `049-c5verify` at 6fc4392 (C5 build commit 6ea00a0). Spec: `tests/reports/fable_049/DESIGN_049.md`, deliverable 1, C5, and `c5.css`. Sonnet's report: `tests/reports/C5_049_report.md`.

## Verdict: NOT YET (one Must)

The build is a faithful lift of the spec. All six items are right at 1440, 1366×768, 1024 and 390, by measurement and by eye. The one Must is a fault in **my spec**, not in Sonnet's work: C5-6 breaks the Stage switch at widths between the sizes I measured.

### Must

**M-1 (C5-6a). Stage switch wraps and the chosen stage is cut off between 901 and 972 px.** New with C5-6.

- C5-6 gives the search a 220 px floor but leaves the Stage switch free to shrink, so the switch gives way instead.
- As built: switch on two rows at 761–810 and 901–972; the chosen stage cut off at 761–776 and 901–938 (at 901 "Stage 6" reads "S"). Pictures: `c56_screen_901.png`, `c56a_sheet_built_vs_fix.png`.
- Before C5 (0.48 at 6ea00a0^): the switch was one row, 217×34, from 901 up; it already wrapped at 761–811. So 901–972 is a regression, and 761–810 is an old fault C5-6 half mended. Picture: `c56_top_901_pre048.png`.
- Fix: append `tests/reports/checks/fable_c5/c5_6a.css` after the C5-6 block, as written. No markup change.

| Swept every pixel, 761–1300, Analysis room | As built | With `c5_6a.css` |
|---|---|---|
| Stage switch on two rows | 761–810, 901–972 | none |
| Chosen stage cut off | 761–776, 901–938 | none |
| Placeholder cut off | 761–859, 901–1021 | 761–805 (now ends in an ellipsis) |
| Search under 220 px | none | none (least 224) |
| Bar spills past the right edge | none | none |

What the fix changes on screen: "COMPOSITION" drops from the title up to 1023 px (was 900); at 761–860 the Stage buttons are 13 px text in a 182×32 switch and the bar gap is 12 px. 1024 and above are untouched (1024: search 271, switch 217×34, full title, same as built). The amendment was injected, not built; it needs the same look after Sonnet lifts it. Script: `sweep_top.py`, numbers in `sweep_top.json`.

## The six items

No page errors at any size. No horizontal overflow at any size on a fresh load.

| Item | Result | Measured | Pictures |
|---|---|---|---|
| C5-1 header growth | Pass | Ear Lab header 97 → 97 at 1440, 1366, 1024; 122 → 122 at 390, on metre, cadences, melody and bass. Phone tally 62 px empty and counted. Also answered a real cadence question on the phone (tally "0 of 1"): 122 before, 122 after. | `c51_ear_empty_390.png`, `c51_ear_counted_390.png`, `c51_ear_first_real_answer_390.png` |
| C5-2 drawn checkbox | Pass | 18×18, 5 px radius, no native appearance, every size. Unticked: clear ground, 1 px `--muted` line. Ticked: gold ground, ink tick. Focus ring 2 px `--goldhi`, not clipped. Phone label rows 44 px (Keys, Ear Lab, Analysis, Oracle). | `c52_keys_ticks_zoom_3x.png`, `c52_keys_ticks_a_*.png`, `c52_keys_ticks_b_*.png`, `c52_ear_unticked_*.png`, `c52_ear_ticked_*.png`, `c52_keys_ticks_focus_context_390_2x.png` |
| C5-3 Keys tally at 1024 | Pass | At 40 of 48 the tally sits on the second row, left edge 763, right edge 975 (the card edge). Header 85 px. One row at 1440 (1179) and 1366 (1105). | `c53_keys_gym_0_1024.png`, `c53_keys_gym_9_1024.png`, `c53_keys_gym_48_1024.png` |
| C5-4 song-starter pill | Pass | Ivory, no underline, 1 px line, 14 px radius, 26 px high; 44 px and 22 px radius at 390. Hover measured: `--goldhi` text, gold line. | `c54_keys_songs_1440.png`, `c54_keys_songs_390.png`, `keys_full_390.png` |
| C5-5 Keys controls on a phone | Pass | No control under 44 px high in either mode (Hear it, Sing it back). Gym header 92 px. Desktop sizes unchanged. | `keys_full_390.png`, `sheet_keys_390.png` |
| C5-6 top-bar search | Pass at 1024 and 1280; see M-1 for 901–972 | 1024: form 271, input 206, placeholder whole (2 px to spare). 1280: form 420, input 354, crumb hidden. 1281: crumb back, form 311. Typed "Bm7" shows whole at both. | `c56_top_1024_analysis.png`, `c56_top_1280_analysis.png`, `c56_typed_1024.png`, `c56_screen_1280.png` |

The CSS block in `index.html` is byte-for-byte `c5.css`, at the end of the main style block. The placeholder is `Type a chord: Bm7, E♭9…`.

## Nearby, looked at

- Checkboxes in other rooms: Analysis (follow, cadences, chord on every beat) and Oracle (start at home, colour card, sevenths) are drawn, centred on their labels, 44 px rows on the phone. `sweep_analysis_0_*.png`, `sweep_oracle_0_*.png`.
- Phone top bar (390, 760) unchanged: 366 / 300.
- `content_lint` passed on my run. I did not rerun `layout_test`, `pageerrors_test` or `transport_test`; Sonnet's report has them clean.

## Shoulds and Coulds (not blocking)

- **S-1** 1366 in Analysis: search 396 / 331, where my spec table says 399 / 334. Outside C5-6's range (above 1280), so not from this build; the spec figure is 3 px out.
- **C-1** Keys phone tick label "up" is 41 px wide (44 high). Could: `min-width:44px` on `label.tick` in the phone rule.
- **C-2** With `c5_6a.css` the Stage switch is 32 px high at 761–860, which covers tablets held upright. Could: 44 px there in a later pass.

## Not checked

- No real phone or tablet; headless Chrome only.
- The Forms "repeat the exposition" box: I could not reach it in the harness. It is a `label.note` like the Analysis boxes, which are right.
- `c54_keys_songs_hover_1440.png` does not show the hover state (the pointer moved before capture); hover is by measurement only.
- In the width sweep the page was loaded at 1300 and narrowed, so page-width overflow was not judged there; fresh loads at 761, 762 and 800 show none.

## Files

`tests/reports/checks/fable_c5/`: `verify.py`, `probe2.py`, `sweep_top.py` (scripts); `metrics.json`, `sweep_top.json` (numbers); `c5_6a.css` (the Must, ready to lift); screenshots as named above.
