# Fable verification of C5 (0.49)

Build checked: branch `049-c5verify` at 4c42ff0 (C5 build 6ea00a0, amendment C5-6a 4c42ff0). Round 1 was at 6fc4392. Spec: `tests/reports/fable_049/DESIGN_049.md`, deliverable 1, C5, and `c5.css`. Sonnet's report: `tests/reports/C5_049_report.md`.

## Verdict: SIGN OFF

Round 2, on the build at 4c42ff0. The one Must from round 1 (M-1, C5-6a) is built and fixed. No Musts remain. All six items are right at 1440, 1366×768, 1024 and 390, by measurement and by eye.

### Round 2: M-1 (C5-6a) on the built version

`c5_6a.css` is in `index.html` byte for byte, straight after the C5-6 block (which is still byte for byte `c5.css`). Nothing was injected this time.

| Swept every pixel, 761–1300, Analysis room | Round 1 build | Round 2 build |
|---|---|---|
| Stage switch on two rows | 761–810, 901–972 | none |
| Chosen stage cut off | 761–776, 901–938 | none |
| Placeholder cut off | 761–859, 901–1021 | 761–805, and it now ends in an ellipsis |
| Search under 220 px | none | none (least 224, at 761) |
| Bar spills past the right edge | none | none |

- The built numbers match what I measured with the amendment injected, at every sampled width.
- By eye: `c56_final_sheet.png` (16 widths from 761 to 1281), `c56_screen_901.png`, `c56_screen_1024.png`. One row, nothing clipped, at every width.
- 1024 and above are as in round 1: 1024 search 271 / 206, switch 217×34, full title; 1280 search 420 / 354.
- Fresh loads at 761, 800, 900, 901, 1024, 1180, 1181, 1280, 1281, in Analysis and Keys: no overlap, no page overflow, no page errors.
- The rest of `verify.py` was rerun at the four sizes on this build: every measurement of the other five items is identical to round 1.
- Round 1 pictures and numbers are kept in `fable_c5/before_6a/`.

What C5-6a changes on screen, as accepted: "COMPOSITION" drops from the title up to 1023 px (was 900); at 761–860 the Stage switch is 182×32 with 13 px text.

### Round 1 finding (now closed)

**M-1 (C5-6a). Stage switch wrapped and the chosen stage was cut off between 901 and 972 px.** A fault in my C5-6 spec, not in Sonnet's build: the search had a 220 px floor and the Stage switch was left free to shrink. At 901 "Stage 6" read "S" (`before_6a/c56_screen_901.png`, `before_6a/c56a_sheet_built_vs_fix.png`). Before C5 the switch was one row from 901 up (`c56_top_901_pre048.png`), so it was a regression. Closed by 4c42ff0.

## The six items

No page errors at any size. No horizontal overflow at any size on a fresh load.

| Item | Result | Measured | Pictures |
|---|---|---|---|
| C5-1 header growth | Pass | Ear Lab header 97 → 97 at 1440, 1366, 1024; 122 → 122 at 390, on metre, cadences, melody and bass. Phone tally 62 px empty and counted. Also answered a real cadence question on the phone (tally "0 of 1"): 122 before, 122 after. | `c51_ear_empty_390.png`, `c51_ear_counted_390.png`, `c51_ear_first_real_answer_390.png` |
| C5-2 drawn checkbox | Pass | 18×18, 5 px radius, no native appearance, every size. Unticked: clear ground, 1 px `--muted` line. Ticked: gold ground, ink tick. Focus ring 2 px `--goldhi`, not clipped. Phone label rows 44 px (Keys, Ear Lab, Analysis, Oracle). | `c52_keys_ticks_zoom_3x.png`, `c52_keys_ticks_a_*.png`, `c52_keys_ticks_b_*.png`, `c52_ear_unticked_*.png`, `c52_ear_ticked_*.png`, `c52_keys_ticks_focus_context_390_2x.png` |
| C5-3 Keys tally at 1024 | Pass | At 40 of 48 the tally sits on the second row, left edge 763, right edge 975 (the card edge). Header 85 px. One row at 1440 (1179) and 1366 (1105). | `c53_keys_gym_0_1024.png`, `c53_keys_gym_9_1024.png`, `c53_keys_gym_48_1024.png` |
| C5-4 song-starter pill | Pass | Ivory, no underline, 1 px line, 14 px radius, 26 px high; 44 px and 22 px radius at 390. Hover measured: `--goldhi` text, gold line. | `c54_keys_songs_1440.png`, `c54_keys_songs_390.png`, `keys_full_390.png` |
| C5-5 Keys controls on a phone | Pass | No control under 44 px high in either mode (Hear it, Sing it back). Gym header 92 px. Desktop sizes unchanged. | `keys_full_390.png`, `sheet_keys_390.png` |
| C5-6 top-bar search | Pass, 761 to 1440 (after C5-6a) | 1024: form 271, input 206, placeholder whole (2 px to spare). 1280: form 420, input 354, crumb hidden. 1281: crumb back, form 311. Typed "Bm7" shows whole at both. | `c56_final_sheet.png`, `c56_top_1024_analysis.png`, `c56_top_1280_analysis.png`, `c56_typed_1024.png`, `c56_screen_1280.png` |

The CSS block in `index.html` is byte-for-byte `c5.css`, at the end of the main style block. The placeholder is `Type a chord: Bm7, E♭9…`.

## Nearby, looked at

- Checkboxes in other rooms: Analysis (follow, cadences, chord on every beat) and Oracle (start at home, colour card, sevenths) are drawn, centred on their labels, 44 px rows on the phone. `sweep_analysis_0_*.png`, `sweep_oracle_0_*.png`.
- Phone top bar (390, 760) unchanged: 366 / 300.
- `content_lint` passed on my round 1 run. I did not rerun `layout_test`, `pageerrors_test` or `transport_test`; Sonnet's report has them clean for C5, and the coordinator reports `layout_test` at 0 findings on 4c42ff0.

## Shoulds and Coulds (not blocking)

- **S-1** 1366 in Analysis: search 396 / 331, where my spec table says 399 / 334. Outside C5-6's range (above 1280), so not from this build; the spec figure is 3 px out.
- **C-1** Keys phone tick label "up" is 41 px wide (44 high). Could: `min-width:44px` on `label.tick` in the phone rule.
- **C-3** The placeholder still does not fit at 761–805 px; it ends in an ellipsis ("Type a chord: B…" at 761). Could: a shorter placeholder at those widths.
- **C-2** With C5-6a the Stage switch is 32 px high at 761–860, which covers tablets held upright. Could: 44 px there in a later pass.

## Not checked

- No real phone or tablet; headless Chrome only.
- The Forms "repeat the exposition" box: I could not reach it in the harness. It is a `label.note` like the Analysis boxes, which are right.
- `c54_keys_songs_hover_1440.png` does not show the hover state (the pointer moved before capture); hover is by measurement only.
- In the width sweep the page was loaded at 1300 and narrowed, so page-width overflow was not judged there; fresh loads show none.
- 4c42ff0 also carries the C-theory merge. I checked only C5 and the top bar.

## Files

`tests/reports/checks/fable_c5/`: `verify.py`, `probe2.py`, `sweep_top.py` (scripts); `metrics.json`, `sweep_top.json` (round 2 numbers); `c5_6a.css` (the amendment, now built); `before_6a/` (round 1 numbers and top-bar pictures); screenshots as named above.
