# Fable's sign-off review: Ear Lab 0.49 ladder UI, second pass

Reviewed: branch `049-ladder-ui2` at 4aec1ab (also `origin/049-int`), against `FABLE_VERIFY_LADDER_UI_049.md`.
Method: Sonnet's report, its PNGs in `tests/reports/ladder_ui2_049/png/`, `metrics.json`, and the diff `68b589f..4aec1ab` (index.html and the four test files). Nothing was run: no browser, no suite (a regression run had the machine). Every "works" below means "seen in Sonnet's PNG or read in the diff", not re-rendered by me.

## Verdict

**Not a full sign-off yet. Two Musts, both small.**

| Item | Verdict |
|---|---|
| M1 rung 12 semiquaver systems | Spacing **signed off**. One Must on the labels it broke (N1). |
| M2 `rest16th` key | **Signed off.** |
| S1 phone drum lanes | **Signed off.** |
| S2 5/4 and 7/8 pairing | **Signed off** (two Coulds). |
| S3 rung 11 sentence | **Signed off** for the melody. Its bass names fall under N2. |
| S4 bass ladder octave marks | **Not signed off** (N2). The offset is wrong for about half the keys and the ladder now disagrees with the stave. |
| S5 digits | **Signed off** from the diff. |
| S6 double rule | **Signed off.** |
| Two test-expectation changes | **Accepted.** |
| Change to my `ladder_ui_test` names check | **Accepted.** |

Rung 12 is signed off once N1 is in. S4 is signed off once N2 is in, or S4 is reverted (see N2, option B).

## Musts

### N1. One bar to a system left two labels wrong

Seen in `pal_r12_semi34_390_entry.png` and `res_r12_semi_*`.

1. **The phone bar map reads "up", "2".** When a system holds the upbeat and bar 1, its button says "up" and there is no "1"; its aria-label is "Bars up". In `earMelSysMapHTML` the text is `nb.length>1 ? … : s[0].bi===0 ? 'up' : nb[0]`. Fix: use the bar number whenever the system has a full bar: `t = nb.length>1 ? `${nb[0]}–${nb[1]}` : nb.length ? `${nb[0]}` : 'up'`. aria-label: "Bar 1, with the upbeat" for that button, "Bar n" for a single bar, "Bars a to b" for two.
2. **The reveal labels read "YOU WROTE · BARS 1", "THE MELODY · BARS 1".** In `mkSys`'s `lab`, write "bar n" for one bar and "bars a–b" for two; a system with the upbeat and one bar reads "upbeat · bar 1" (as `earMelTag` already does at entry).

Test to add (`ladder_ui_test`, 390): a rung 12 item with semiquavers and an upbeat: first bar-map button text is "1"; no reveal label matches `bars \d+$`.

### N2. S4: the bass's marks are counted from the wrong do, and only on the ladder

Sonnet's reading, "the bass's own do is two octaves below the melody's do", is not right. Minus 14 steps is the low edge of the bass ladder's window, not the bass's do. `ladBass` puts the bass between MIDI 41 and 62 and starts it near 48, so the bass's home note is one octave below the melody's do in some keys and two in others.

The PNGs show the result (`two_r11_bass_*`, `res_r11_*`, E flat major): the bass's home do is E flat 3, one octave below the melody's. The ladder row for it now reads **d'** (and carries the home bar), while the stave under it still reads **d,** and the next bass notes read **l,,** and **s,,**. So the student taps "d'" and sees "d," written. That is worse than the "t,,," I asked to be rid of. The S3 sentence for the bass would also speak in the engine's names, and the rows' aria-labels still say "low" for a row drawn as d'.

**Option A (preferred): finish it.**

- Offset per item, not fixed: `earBassOff(q) = q.l===11 && q.bass && q.bass.length ? -Math.ceil(ladSemis(q.bass[0].i, q.bass[0].a)/12) : 0`. The bass's first note is always the root of the tonic chord, so this makes the do at or next above the bass's home note the unmarked one: a bass that starts on d, or d,, starts on **d**; a minor bass that starts on l,, or l,,, starts on **l,**.
- One helper for the shown name (syllable plus `elmk(octave + offset)`), used everywhere a bass name is drawn at rung 11: the ladder rows (as now), the names under the bass stave at entry and at the reveal ("You wrote" and "The answer"), the "Bass, bar n: …" sentence (both the answer's name and the student's), and the "low" / "high" words in the ladder rows' aria-labels. `data-earsol`, the engine's names and marking stay untouched.
- The line above the ladder. "The bass's octave marks count from the bass's own do." does not tell a student which do that is. Use the offset to say it: **"In the bass, d is the do one octave below the melody's d. Octave marks count from there."** ("two octaves" when the offset is 2; no line when it is 0.) Content may polish the wording; the fact it must carry is which do.
- Tests: over at least 60 rung 11 items (both modes): the bass's first note is shown as "d" (major) or "l," (minor) on the ladder; the name under the first bass note on the stave equals the text of the ladder row with the same `data-earsol`; the line above the ladder names the right number of octaves. Replace the present check, which passes if any one row has two marks fewer.

**Option B: revert S4** (ladder back to the engine's names, the line removed) and carry S4 to 0.50. Acceptable. The present half state is not.

## What I checked and found right

- **M1.** `pal_r12_semi44_*`, `pal_r12_semi34_*`, `res_r12_semi_*`: one bar to a system at both widths; two semiquavers stand about 19 px apart on the phone and 25 px on the desktop, and "d' r' d'" and "m' f' m'" read as separate syllables. The phone bar map has one button a bar (four at 4/4). The reveal pairs each bar of yours over the answer's.
- **M2.** The semiquaver-rest key has two hooks, the quaver-rest key one; they cannot be mistaken. The glyph sits inside its key.
- **S1.** `rhy_r10_lanes_390_drums.png`: each half bar is a K row over an S row, four cells of about 82 × 44, beat under beat, "Bar n" above the first half. Clear.
- **S2.** `rhy_r9_57_result_1366_card.png`, `rhy_r9_78_result_1366_card.png`: each line of yours sits directly over the same line of the answer, labels on the first pair.
- **S3.** "Melody, bar 1: the sixth note is r: you wrote m." beside "Melody 18 of 19 notes" and the red sixth note. True and placed. The old sentence stays as the fallback.
- **S6.** One double rule, before the first rest key, in both palettes.
- **S5.** The condition now takes any target inside `#earMain` that is not an input, textarea, select or editable. Right as written.

## The test changes

- **terms_test, rung 2 prompt "two bars".** Accepted. `LRBARS` gives rung 2 two bars at 68b589f as well, so the test was stale, not the page.
- **terms_test, tiles `w` and `hd`.** Accepted. Both cells exist in `LCELL` (semibreve, dotted minim) and the expected hovers follow the one-US-name rule.
- **My names check in `ladder_ui_test`.** Accepted. `(ss[1]||ss[0])` is the answer's first line in both layouts and still compares the same first bar. It is not loosened.

## Shoulds (none blocks)

- **The width behind the 26 px rule.** `earMelPerSys` reads `#earMel`'s width, and a guess (`innerWidth − 44`, up to 1,056) before the element exists. At 1366 the guess gives two bars and the real stave (about 440 px) gives one, so two calls in one render can disagree. Compute it once per render from one source.
- **The report is wrong on one point:** it says a 3/4 bar with semiquavers stays two to a system at 1366; `pal_r12_semi34_1366_card.png` shows one. One is fine (the stave is never wide enough for two). Correct the report and make the test say `== 1` rather than `<= 2`.
- **`KEY2` in `ladder_ui_test`** ends `||true` and passes without proof when the chosen length is already the shortest. Set `EAR.len` to another length first and drop the `||true`.
- **Dead branch:** the `rest16th` case in `earCellDraw` can never run (no rhythm cell has a semiquaver rest). Harmless; the report's "a semiquaver rest on the stave was also drawn as a quaver rest" overstates it.

## Coulds

- S2: put "bar 2", "bar 3" in the empty label column of the later pairs, and widen the gap between pairs from 8 to 16 px so each pair reads as a unit.
- 7/8 bars are narrow enough for two to a line at 1366.
- The key "a wrong note / a beat with the wrong rhythm" still shows under a wholly correct answer (older than this pass).

## Not checked

- Nothing was re-rendered or run by me; the suite results are Sonnet's.
- No PNG shows a semiquaver rest on a melody stave (VexFlow draws that one itself), a bar map with more than six buttons, a bass error at rung 11, or S5 in use.
- The diff also carries the transport change in `ladSchedRhy` and `ladSchedRhyBeat` (L32). Not part of this review.
- No real phone.
