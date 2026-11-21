# Fable's verification: Ear Lab 0.49 ladder UI

Branch `049-fable-uiv`, from `049-int` at 1c5ba27 (the UI, the fixed engine, the C6 colours and the cadence fixes together). Checked against `fable_049/DESIGN_049.md` 2.1 and 2.2, `ladder049.css`, and `fable_049/ladder_ui/SPEC.md` with its CSS and reference markup.

Everything was re-rendered from this build in headless Chrome at 1366×768 and 390×844 (`fable_ladderui/shots.py`, 25 scenes, 146 PNGs, `metrics.json`). Sonnet's own PNGs predate the merge and were not used for the verdict. No real phone was used.

## Verdict

**SIGN OFF for melody rungs 4 to 11, rhythm rungs 1 to 10 and the picker, with the fixes below already made on this branch.**
**Not signed off: melody rung 12** (two Musts for Sonnet, M1 and M2).

The build is faithful to the spec and reads as one hand: the palette, the held block on phones, the half rungs, the gauge, the two-part headline and the paired staves all match the mock-ups to within a few pixels. But the re-render found five real faults that the builder's tests could not see, three of them wrong information on screen. I fixed all five here, because each was a few lines.

## Faults found and fixed on this branch

| # | What was wrong | Where it showed | Fix |
|---|---|---|---|
| F1 | **Move do, after a mutation: the answer was read through the student's mutation.** "The melody" was drawn a fifth too high from the pivot on, a wholly right answer read "Correct" beside "✗ Solfa 17 of 36" and a false sentence ("In bar 5, the first note is s: you wrote d"), and "Hear bar n: yours, then the answer" played the answer a fifth high. | rung 9, Move do, every item that moves do | `earMelLine` takes a `truth` flag; new `earMelTruth()` used by the staves, the counts, the sentence, the bar map and the bar replay |
| F2 | **The mutation verdict was always "Mutation early"** when it was not in place: the result stored the marker's yes/no where the note index was wanted, so "missing" and "late" could never show. | rung 9, Move do | `EAR.res.pivot = EAR.pivot` |
| F3 | **The time names at the rhythm reveal sat one bar to the right** whenever there was no upbeat (bar 2 carried bar 1's names; bar 1 had none). The engine's name list starts with the upbeat's bar. | every rhythm rung | index by bar number |
| F4 | **Sideways scroll (40 px) on phones at Nearly**: "Solfa right by sound" and "1 other spelling" could not wrap. | rung 10, 390 | the headline's parts may wrap on phones |
| F5 | **Long tuplet names ran into their neighbours** at the reveal ("ta-da-ki-na-dom" over "ta"); `layout_test` caught it on some runs and not others. | rhythm rung 9 | five- and seven-tuplet names sit one line lower; at the end of a bar they end with the bar |

Smaller things fixed at the same time:

- **7/8 headline** now counts the beats as drawn ("10 of 12 beats", the three groups of each bar), not the engine's quavers ("24 of 28"). Gap 8.
- **The fa–si gauge** was drawn on a second, cut-off pair of rows (s, and si, at the foot of the ladder, with no fa under them). It now shows only where the whole step is on the ladder.
- **A stem-down first note touched the time signature.** 5 px more room after it.
- **Nearly**: the sentence dropped the octave marks ("you wrote si,; going down it is le,." read as typing slips); the phone bar map marks the bar with a dotted gold line, not the red "error" outline.
- **Rung 11**: one line down the left joins the two staves of a system; the answer's pair is labelled "The answer", not "The melody"; the melody palette lost the dotted crotchet (and, in 4/4, the dotted minim), which rung 11 never writes.
- **Drum lanes at the reveal**: each drum's "you wrote" row now sits over its "it was" row; the labels no longer break in two.
- **Two-row palette** (`.el-pal.two`, my CSS): eleven cells made 5 + 5 + 1. Now a six-column grid, 6 + 5.
- **When no mutation was marked**, the sentence names the answer in the home key, as the student did ("is s: you wrote d"), not in the new one ("is d: you wrote d").
- Two regression checks added to `ladder_ui_test` (a right answer has no cross in its headline; the names row has as many names in bar 1 as bar 1 has cells).

## Musts for Sonnet (melody rung 12 only)

**M1. A bar with semiquavers needs room.** SPEC 1.3 asked for a 4/4 bar with semiquavers to take a system to itself on phones; it is two bars to a system at both widths. In `pal_r12_390_entry.png` and `pal_r12_1366_card.png` the syllables run together ("s'm'd'") and a semiquaver rest sits on the next note. Rule to build: a system holds one bar whenever its shortest written or expected value is a semiquaver and two bars would give a semiquaver less than 26 px of advance (at 390 that is every 4/4 and 3/4 bar with semiquavers; at 1366, 4/4). The bar map then has one button per bar; above six buttons it scrolls sideways inside its row. Add the view to `layout_test` and `ladder_ui_test` V with an item chosen to have semiquavers.

**M2. The semiquaver rest and the quaver rest are the same drawing** in the palette (`earLenGlyph` uses `rest8th` for both). Add Bravura `rest16th` (U+E4E7) to `ELGLY` and use it for 105 ticks. Two keys that look alike and write different things cannot ship.

## Shoulds

- **S1. Drum lanes on phones (rhythm rung 10).** Kick and snare are 16 cells each, four to a row, so the snare's beat 1 is four rows below the kick's and the two cannot be read together. Regroup by time on phones: for each half bar, a kick row over a snare row (four cells each, 82×44), with a small "K" and "S" at the left and the bar number as a caption. Desktop stays as it is.
- **S2. Rhythm reveal in 5/4 and 7/8 at 1366.** With the "You wrote" label column, only one bar fits a line, so "You wrote" is four lines and "It was" is four more, far apart. Pair them: line 1 of yours over line 1 of the answer.
- **S3. Rung 11 sentence.** "The melody is not right yet. Compare the staves below." names no place. Use the rung 4 to 10 sentence for the part that is wrong ("Melody, bar 1: the sixth note is r: you wrote m").
- **S4. Bass ladder names (rung 11).** Rows read "t,,," and "s,,,". Count the bass's octave marks from its own do (display only; `data-earsol` and the engine's names unchanged), and say so once above the ladder.
- **S5. Digits 1 to 7** should choose a length whenever focus is inside the Ear Lab card and not in a text field, not only on the page body. Gap 12.
- **S6. The double rule before rests** is drawn before every rest key; it belongs before the first only (`.el-len:not(.rest)+.el-len.rest`).
- **S7. For Content, not Sonnet:** a wrong-note sentence can end a syllable's octave comma against a colon ("is t,: you wrote d"); three US glosses can land in one feedback sentence ("Bar (US: measure) 3, beat 1 is two quavers (US: eighth notes) … crotchet (US: quarter note)"). Both are the house rules working as written; they read badly here.

## Rulings on Sonnet's 13 gaps

| # | Gap | Ruling |
|---|---|---|
| 1 | C6 colour tokens not in the app | **Closed by the merge.** `--red` is `#d15e5d`, `--green` `#9dc995`; the stave reads the token. |
| 2 | Ending figures in the palette from rung 6; rung 12 is the union | **Accept for rungs 6 to 10**: over 400 items a rung and metre, every palette length is written and nothing written is missing, so my table was the incomplete one. **Rung 11 fixed** (it listed lengths it never writes). **Rung 12**: accept the union (eleven cells), now in two even rows; see M1 and M2. |
| 3 | `EAR.mod`, not `EAR.do` | **Accept.** The engine's name wins; one name is what matters. |
| 4 | Rung 11 as two stacked staves with a Melody/Bass switch | **Accept**, with the system line added here. Good on desktop. On phones the held block is 373 px, which leaves about four ladder rows above the play bar: workable, tight, and for a real phone to judge. S3 and S4 stand. |
| 5 | Rung 10 drum lanes, Sonnet's design | **Accept on desktop** (two lanes, quaver cells numbered 1 & 2 &, clear and in keeping). **Phones: S1.** |
| 6 | Replays `bar` and `a2` as UI adapters | **Accept.** The bar replay's answer was wrong under Move do (F1); fixed. |
| 7 | Solfa counted in the UI, bar by bar | **Accept** as my O4, still the checker's to confirm. It was the cause of F1's false count; fixed, and now guarded by a test. |
| 8 | 7/8 headline in quavers | **Fixed here.** |
| 9 | Names setting changes the melody reveal's names | **Accept.** Seen working at rungs 6, 7, 9, 10 and 11. |
| 10 | Nearly at rung 10 and the rung 9 reveal not reviewed | **Reviewed now.** Nearly: right once F4 and the two small points were mended. Rung 9 reveal: F1 and F2 were both here. |
| 11 | Move do cannot be changed after an answer (a toast says so) | **Accept.** It is the honest behaviour; the answer was marked under the setting it was written in. |
| 12 | Digits only with focus on the body | **Accept for 0.49**; S5. |
| 13 | Not tested on a real phone | **Open, and Justin's.** Nothing here replaces it. The 6/8 phone stave, the rung 10 ladder (18 rows) and rung 11's held block are the three to try first. |

## Checks

| Check | Result |
|---|---|
| Text under 11 px (HTML and SVG, as drawn) | none in any of the 25 scenes at either width |
| Phone targets under 44 px | none (the 18 px checkbox sits inside a 44 px label) |
| Sideways scroll | none after F4 (before: 40 px at Nearly, 390) |
| Page errors | none |
| Reduced motion | no transition or animation left running in the melody desk, the rhythm desk or the picker under `prefers-reduced-motion` |
| Focus rings | 2 px `--goldhi` on rung buttons, band tabs, palette cells, ladder rows and half rungs, setting buttons, tiles, drum cells, the part switch and the bar map |
| Sizes against the spec | header 126 / 188; palette 292×58 and 328×50; half rung 145×36 and 163×44; mutation button 328×44; setting 302×66; gap figure 396×43 and 302×93; headline 396×66 and 256×57; held block 245 (spec 242) and 300 at rung 9 (spec 294) |
| Does it look made by a person | Yes. One type scale, one gold, engraved notes, no stock components. The places that did not (the orphan palette row, the cut-off gauge, the stem on the time signature, "si,;") are mended; rung 12's stave (M1) is the one that is left. |

| Suite, after the last change | Result |
|---|---|
| `ladder_ui_test` | pass, 165 checks (two new) |
| `layout_test` | pass, 304 views, none with findings (before the fixes one run failed on F5) |
| `earlab_ui_test` | pass, 469 checks |
| `pageerrors_test` | pass, 153 views, 4,231 clicks, no errors |
| `unit_test`, `content_lint` | pass (1,164 checks) |

Not run: `transport_test` and `terms_test` (Sonnet reports both failing on the untouched base for reasons outside the UI; I did not look into them).

## Not checked

- No real phone, and no student.
- The mutation "early" verdict was reasoned from the code after F2; "in place", "late" and "missing" were seen on screen.
- The suggestion row and the "8 more" chip were covered by the tests, not re-rendered.
- Rung 12 beyond the one excerpt drawn.

## The PNGs

`tests/reports/checks/fable_ladderui/`: `<scene>_1366.png` (the screen), `_1366_card.png` (the whole card), `_390.png` (the phone at the card's head), `_390_entry.png` (held block stuck, ladder under it), `_390_result.png`, `_390_staves.png`, `_390_card.png` (half size). Scenes: `picker_long_header`, `pal_r6_24`, `pal_r6_68`, `res_r6`, `a2_r7`, `a2_r7_entry`, `mut_r9_before`, `mut_r9_MV`, `mut_r9_mv_was_ri` ("was ri" on the si row), `res_r9_move`, `res_r9_move_missing`, `res_r9_home`, `nearly_r10`, `lad_r10_entry`, `two_r11_mel`, `two_r11_bass`, `res_r11`, `pal_r12`, `rhy_r4_result`, `rhy_r9_sept`, `rhy_r9_sept_kk`, `rhy_r9_result`, `rhy_r9_78_result`, `rhy_r10_lanes`, `rhy_r10_result`. `res_r9_move_late` did not stage the late mutation and shows the missing case again.
