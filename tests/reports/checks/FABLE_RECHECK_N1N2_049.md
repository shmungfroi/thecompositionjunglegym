# Fable's re-check of N1 and N2: Ear Lab 0.49 RC

Reviewed: branch `049-rc` at e90aa5b, in the copy at `/home/claude/wt/fable`. Against `FABLE_SIGNOFF_UI2_049.md`.
Method: this time I rendered it. Headless Chrome, the real `index.html`, at 1366 x 768, 1024 x 768 and 390 x 844, and I looked at the PNGs. Everything is in `tests/reports/checks/fable_recheck_049/`: 168 PNGs, `facts.json` (the labels, bar-map text, ladder rows and sentences read from the page for every view), and the three scripts that made them (`shots.py`, `width_check.py`, `dist.py`).

## Verdict

| Item | Verdict |
|---|---|
| N1 bar map and "bar n" labels | **PASS** |
| N2 rung 11 bass octave marks (option A) | **PASS** |
| Should: stave width measured once per render | **PASS** |
| Should: 3/4 at 1366 is one bar, test says `== 1` | **PASS** |
| Should: `KEY2` real | **PASS** |
| Should: dead `rest16th` branch | **PASS** |
| Nearby breakage from e90aa5b | None found |
| N3 (new, older than e90aa5b): phone bar map ignores the bass at rung 11 | Must at e90aa5b; **PASS at 7087b74** (see the last section) |

**Updated after 7087b74: N1, N2 and N3 are all closed. SIGN OFF for the 0.49 RC** (final section). At e90aa5b the verdict was: N1 and N2 closed, RC not signed off because of one new Must, N3. N3 was not a regression: my last review listed "a bass error at rung 11" under Not checked, and the first render of it showed it wrong on a phone.

## N1: PASS

Seen at all three widths, entry and reveal, rung 12, 3/4 with semiquavers and an upbeat (the only metre where the engine gives semiquavers with an upbeat: no 4/4 item in 3,000 tries), plus 4/4 without an upbeat.

- Bar map, system holding the upbeat and bar 1: the button reads **1**, aria-label "Bar 1, with the upbeat". No "up" anywhere. Other buttons: "2", "Bar 2". `n1_r12_up34_entry_390_staves.png`.
- Reveal labels: "YOU WROTE · UPBEAT · BAR 1", "THE MELODY · UPBEAT · BAR 1", then "· BAR 2". No "BARS 1". `n1_r12_up34_result_390_staves.png`, `n1_r12_up34_result_1366_card.png`, `n1_r12_up34_result_1024_card.png`.
- 4/4, four systems: "BAR 1" to "BAR 4", map "1 2 3 4", the error bar opened first and flagged. `n1_r12_noup44_result_1024_kk_card.png`, `n1_r12_noup44_result_390_staves.png`.
- Two bars to a system still read "BARS 1–2", "Bars 1 to 2, with the upbeat". `n1_r12_nosemi_up_result_*`, `n1_r6_up68_result_390_staves.png`.
- The test I asked for is in `ladder_ui_test` and is real (first button "1", every button a number with "Bar n", no label ending `bars \d+`).

## N2: PASS

Seen for both modes and all three offsets (0, 1 and 2 octaves), bass half written, and the reveal with a wrong bass note, at all three widths.

- **Ladder, stave and sentence now agree.** E flat major, bass home E flat 3: ladder top row **d**, the stave under it **d d l, d**, sentence "Bass, bar 2: the first note is l,: you wrote t,." with the red **t,** under the wrong note. `n2_r11_maj_off1_basswrong_1366_card.png`, `n2_r11_maj_off1_basswrong_390_kk_staves.png`.
- Two octaves: A flat major, bass home A flat 2 shows **d**, then **l, l, m**. `n2_r11_maj_off2_bassentry_1366_card.png`, `..._390_ladder.png`.
- Minor: the bass starts on **l,** in every case. `n2_r11_min_off1_basswrong_1024_card.png`, `n2_r11_min_off2_basswrong_390_staves.png`.
- The line names the do and the right number of octaves: "In the bass, d is the do one octave below the melody's d. Octave marks count from there." / "two octaves". No line at offset 0. I checked the octave count against the MIDI notes in `facts.json` (63 against 51, 68 against 44, and so on). It wraps to two lines at 12 px beside the ladder and is readable at every width.
- aria-labels follow the drawn name ("low" only where a comma is drawn): `rows` in `facts.json`.
- The test is real: 64 items at each width, expectation worked out from MIDI, not from `earBassOff`. My run: 232 checks, 0 failures; offsets seen 1 (39 and 37 items) and 2 (25 and 27); 64 "Bass, bar n" sentences read at each width.
- Over 1,500 fresh rung 11 items (`r11_offset_distribution.json`): offset 1 in 893, offset 2 in 605, offset 0 in 2. With offset 1 or 2 no row carries more than two marks and nearly every answer uses none or one.

## The Shoulds: PASS

- **Width once per render.** `width_check.py`: 104 states (2/4, 3/4, 4/4, 6/8 with semiquavers, entry and reveal, new item then resized through 1366, 1200, 1100, 1024, 900, 800, 761, 760, 390 and back). In every one `EAR.melW` equals the stave's real width, the bars-per-system the page was built with equals the current answer, the bar map has one button a system and the drawn labels match. 0 disagreements, 0 page errors. `width_check.txt`.
- **3/4 at 1366 is one bar**: stave 474 px, one bar a system; the test now says `== 1`.
- **`KEY2`**: sets the longest live length first, needs `before != first`, no `||true`.
- **`rest16th` branch** gone from `earCellDraw`; the palette key still draws its own glyph.

## Nearby

- `ladder_ui_test` 232 checks, 0 failed. `layout_test` 332 views, none with findings, no page errors. `earlab_ui_test` 469 checks, 0 failed.
- No sideways scroll and no page errors in any of my views.
- Rhythm names: both settings rendered (`*_kk*`). These views hold no tuplets, so the two settings draw the same names; nothing moved.

## New Must

### N3. On a phone the bar map marks a bar right when its bass note is wrong (rung 11)

Older than e90aa5b; not caused by it. `earMelBarState` and `earMelFirstBad` read the melody's marks only.

- `n2_r11_min_off2_basswrong_390.png` and `..._390_staves.png`: the card says "Bass 3 of 4 · Bass, bar 3: the first note is m: you wrote d'." The bar map under it shows **1–2** and **3–4** all green, opens on bars 1–2, and neither button says "an error here". The student has to guess that the red note is behind the other button.
- `n2_r11_maj_off1_basswrong_390_kk_staves.png`: bars 1–2 both green in the map, with the red **t,** drawn in bar 2 directly below.
- The melody is handled properly (`n2_r11_maj_off1_melwrong_*`: "Bars 1 to 2, an error here").

Fix: at rung 11 a bar's state is the worse of the two parts (bad if either part has a wrong note or rhythm there), and the reveal opens on the first system with an error in either part. Test (`ladder_ui_test`, 390): a rung 11 item with the melody right and one wrong bass note outside the first system: that system's button has the bad mark and "an error here", and it is the one pressed.

If this is to be carried to 0.50 instead, that is Justin's call to make, not mine; I would not ship a green mark over a wrong note without it being a known, logged issue.

## Shoulds (none blocks)

- **Offset 0 still shows triple marks.** When the bass starts at or above the melody's do (2 items in 1,500) there is no offset, and the ladder runs 23 rows down to **t,,, l,,, s,,,**. `n2_r11_min_off0_bassentry_1366_card.png`. The names agree everywhere, so it is not N2 again, but those rows sit below the bass's floor (MIDI 41) and can never be the answer. Trim the bass ladder to the notes the bass can reach (41 to 62, plus the item's own notes).
- **`ladder_ui_test` never meets offset 0** (both runs: 1 and 2 only). Stage one offset 0 item so the "no line" branch is tested.

## Coulds

- A two-bar system that holds the upbeat reads "BARS 1–2" at the reveal while a one-bar one reads "UPBEAT · BAR 1". Either is clear; they could match.
- In the bass ladder the word HOME shows only when the engine's own l, or d is a row (offset 0). With an offset, the bass's do or la has the gold bar but not the word.
- The label above the two staves at rung 11 says "MELODY · 4 BARS OF 4/4".
- At 761 to 800 px wide the stave is 277 to 316 px, narrower than on a phone (328).

## Not checked

- `terms_test` did not finish inside my time limit here (stopped at 280 s, no result). The full run on the other copy covers it.
- 4/4 with semiquavers and an upbeat: the engine does not make one.
- A bar map with more than six buttons; a semiquaver rest on a melody stave.
- Sound, and a real phone.

## N3 re-check at 7087b74: PASS

Reviewed: `/home/claude/wt/n3` at 7087b74 (e90aa5b plus the N3 fix). Rendered again at 1366 x 768, 1024 x 768 and 390 x 844: 13 reveal scenes at each width, 104 PNGs and `facts.json` in `tests/reports/checks/fable_recheck_049/n3/`, made by `fable_recheck_049/shots_n3.py`. The bar map is in the page at every width (drawn on the phone), so its state, labels and pressed button were read at all three.

The diff: one helper, `earMelMarked`, gives the marked parts of a reveal (melody and bass at rung 11, the melody alone elsewhere); `earMelBarState` and `earMelFirstBad` both read it. Nothing else in `index.html` changed.

| Scene (rung 11, melody or bass with one wrong note) | Bar map | Opens on | PNG (390) |
|---|---|---|---|
| Major, 1 octave, bass wrong in bar 4 | 1–2 green green; 3–4 green **red**, "Bars 3 to 4, an error here" | 3–4 | `n3_maj_off1_basslate_390_staves.png` |
| Major, 2 octaves, bass wrong in bar 4 | same | 3–4 | `n3_maj_off2_basslate_390_staves.png` |
| Minor, 1 octave, 8 bars, bass wrong in bar 7 | only 7–8 marked, "an error here" | 7–8 | `n3_min_off1_basslate_390_staves.png` |
| Minor, 2 octaves, bass wrong in bar 3 (the scene that failed before) | 3–4 **red** green, "an error here" | 3–4 | `n3_min_off2_basslate_390_staves.png` |
| Major, bass wrong in bar 2 | 1–2 green **red** | 1–2 | `n3_maj_off1_bassfirst_390_staves.png` |
| Major, melody wrong in bar 4 | only 3–4 marked | 3–4 | `n3_maj_off1_mellate_390_staves.png` |
| Minor, melody wrong in bar 3 | only 3–4 marked | 3–4 | `n3_min_off2_mellate_390_staves.png` |
| Minor, bass wrong in bar 3 and melody wrong in bar 7 | 3–4 and 7–8 marked, both "an error here" | 3–4, the first | `n3_min_off1_both_390_staves.png` |
| Major, both parts right | all green, no "an error here" | 1–2 | `n3_maj_off1_allright_390_staves.png` |

In every scene the red bar in the map is the bar with the red note on the stave under it, and the sentence names the same bar. The 1366 and 1024 cards (`*_1366_card.png`, `*_1024_card.png`) show the same red note; identical map state in `n3/facts.json`.

**Rungs without a bass: unchanged.** Rung 12 (3/4 with an upbeat and semiquavers; 4/4 with semiquavers; no semiquavers with an upbeat) and rung 6 (6/8 with an upbeat), same seeds as before: bar-map text, aria-labels, pressed button, reveal labels, sentence and the names under the staves are equal to the e90aa5b run at all three widths (12 of 12 comparisons). `n3/n1_*`.

**Tests.** `ladder_ui_test` at 7087b74: 240 checks, 0 failed (232 before; the 8 new ones stage one wrong bass note, then one wrong melody note, outside the first system on the phone and check the mark, the label, the pressed button, and that no other button is marked). That is the test I asked for. This run also met an offset 0 item at 390 (1 of 64) and it passed.

Not checked for N3: a bass error of rhythm (I could not stage one: the bass palette offered no shorter length at that point). It goes through the same line of code as a wrong note (`d.rhythm===false`). `layout_test`, `earlab_ui_test` and `terms_test` were not re-run at 7087b74 (time limit); the first two passed at e90aa5b and the change does not touch layout.

The two Shoulds and four Coulds above still stand; none blocks.

## Final: SIGN OFF

N1 PASS, N2 PASS, N3 PASS, the four Shoulds from my sign-off review PASS. **The Ear Lab 0.49 RC at 7087b74 is SIGNED OFF** by the design reviewer, subject to the full suite run being green (I did not run `terms_test` to the end, nor the whole suite, myself).
