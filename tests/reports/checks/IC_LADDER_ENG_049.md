# IC_LADDER_ENG_049: Ear Lab ladders engine, independent check

**Independent check** (Opus, 21 Nov 2026). I did not build these ladders. Branch `049-ladder-eng` at d5fcec7; `index.html` was not edited.
Spec used: `tests/reports/ladder_049/LADDER_REGISTER_049.md` (with section 8), plus L102, L103, L104, L107 and the approved names (L97/L98) as the task gives them.
I used the builder's report only to find claims. Every verdict below comes from my own code.

**Method.** The app ran in headless Chrome (`tests/harness`). Items were drawn with my own seeded PRNG (mulberry32, not the app's): **5,000 items for every rung** (M1–M11, R1–R10).
I checked them in Python against my own tables: a solfa-to-semitone table, a cell table in ticks written from register sections 3–4, a name table taken from 4.1/4.3 with D11 (a) and D12 (b), my own outer-voice rules, and my own palette grammar.
I built the marking answers myself and the page only marked them. M12 was checked against the Humdrum sources with music21, using keys from `scores/meta.json`.
The scripts are not committed. They are in `/home/claude/scratch_ic/`: `dump.py check_mel.py check_rhy.py mark.py pal_check.py pal_cat.py tells.py m12_check.py probe.py`.

Volume: 5.48 M melody checks (359 kinds), 1.95 M rhythm checks (201 kinds), 220,258 marking cases (148 kinds), 485,231 palette states, 123 tell measurements, and 46 excerpts.

## Verdict per item

| # | item | verdict |
|---|---|---|
| 1 | Melody M1–M11 | **FAIL** (M7 melodic si, M8 kind mix, M11 consecutive 5ths/8ves; everything else passes) |
| 2 | Rhythm R1–R10 | **FAIL** (antA never generated; tie-in names) |
| 3 | Marking + palette | **FAIL** (M9 Move do; relative kinds under Move do; 5/4 and 7/8 notation; a false Nearly; palette offers illegal lengths) |
| 4 | Tells | **PASS** (123 re-measured, 0 over 5 points) |
| 5 | M12 excerpts | **FAIL** (2 excerpts unsuitable, 2 respelt, credits garbled) |
| 6 | Builder's own labels | **reported**: 1 of 4 follows the approved rules as it stands |
| – | `earlab_test` | **PASS**: 0 failures, one run |
| – | `earlab_items_test` | **PASS**: 0 failures, one run |

## Musts

**M-1 · M7 melodic minor: si does not always go to la.** 1,374 of 3,473 si's in melodic items (40%) leap away; e.g. `si, → m` (up a minor 6th) in `l, si, m l, l, si, m si, l,`.
The cause: the generator raises so whenever the next note is higher, and it checks si → la only for harmonic items. The register (M7) asks for "rising f→fi→si→l", so a raised 7th should only ever rise by step to la.
Harmonic items pass: all 1,001 si → l.

**M-2 · M8: the four kinds are not a quarter each.** Of 3,365 new items: Dorian 1,412, Mixolydian 1,614, te 183, fi 156. That is 42 / 48 / 5 / 5%, against 25% each in register M8.
The te/fi kinds are redrawn whenever no alteration lands, and the kind is redrawn with them, so they lose out.

**M-3 · M11: consecutive octaves/fifths in the outer voices across a bass change.** I compared the last melody note before each bass change with the melody note at the change, in similar motion. This finds 736 consecutive 8ves/5ths (490 octaves, 246 fifths) in **685 of 5,000 items**. 293 of them are at the final V–I: the melody goes s → d while the bass goes s → d.
Example: `m d l r m r s, t, s, d` over `d,, d,, s,,, d,,`.
The engine's checker (`ladOuterCheck`) compares only the soprano note sounding at each bass onset, so it misses these. Every check on the engine's own terms passes (see Passes).

**M-4 · R6: the anticipation of beat 3 (`antA`, "ti ti-i") is never generated.** It appears 0 times in 25,000 R6–R10 items.
`ladCellOK` rejects every 840-tick cell off a strong beat, and `antA` is 840 ticks long and allowed only at 420. The register R6 lists it among the anticipations; only the over-the-barline anticipation (`antB`) occurs.

**M-5 · Tie-in names after `antB` break the approved tie rule.** `ladRhyNames` replaces the first word of the next cell's name with "i":
- `s4` → "i-tika": 3 syllables for 4 notes; it should be "i-ka-ti-ka".
- `s2e` → "i-ti": 2 syllables for 3 notes; it should be "i-ka-ti".
- `h`, `hd`, `w` → "i-a", "i-a-a", "i-a-a-a": the held note changes vowel, but the rule is "held on the vowel of the first note".

Counts at R6: s4 72, s2e 58, h 62, hd 70, w 68, in both name settings. The same names occur at R7–R10.

**M-6 · M9 under Move do: the move reading is marked wrong.** `ladMelMark` reads every entry against the old do. A student who writes the new key's syllables after the pivot (`q.readings.move`) is marked **wrong**: all 530 of 530 dominant-kind items, with the true pivot marked.
ENGINE_API says "either reading is fine", and register M9 says "spelling in the key in force where the student puts the pivot". Neither holds. Answers written in Keep home do syllables are right (1,334/1,334).

**M-7 · M9 relative kinds under Move do.** For M-vi and m-III items with every note right:
- With no mutation marked, they are marked wrong in 804 of 804 cases. There is no mutation in a relative modulation (D8: do moves only for the dominant kinds).
- With a mutation marked outside the window, they are marked wrong in 432 of 432 cases. L107 says a mutation marked on a relative item with every note right = right.

Related: for m-III the "window" is always the whole item (916 of 916). The old minor key set includes fi and si, so no note belongs only to the new key.

**M-8 · Rhythm marking: 5/4 and 7/8 skip the notation rules.** `ladRhyLegal` returns true for any 5/4 or 7/8 answer. So a same-sound answer in illegal cells is marked **right**: 855 of 1,264 R9 items accepted ti-ti written as two single quavers (`e e`).
Register 3.0 and R9: right only "in cells that keep the rung's rules"; in 5/4, cells never cross the grouping.

**M-9 · False Nearly.** The D11 test `ans.some(k==='syn') && truth.includes('synT')` is item-wide, not per position. An answer whose real error is something else, while it has a correct syn-co-pa elsewhere, is marked Nearly.
This happened in 21 items at R6–R8 and 92 at R9 (`e e` for `e2` in items holding both `syn` and `synT`). Nearly is allowed only for the D11, R8 and R9 cases.

**M-10 · The palette offers illegal lengths, and some lead to dead ends.** Counting only states whose prefix is legal under my grammar, it offers:
- a dotted minim at beat 1 of inner 4/4 bars at M6–M11 (19,509 states; register M6: ta-a-a in 3/4 only);
- a dotted crotchet in simple-time bars, mostly last bars, at M4–M11 (about 30,000 states; the API itself says "dotted values where the rung has them", and M4/M5 have none);
- a minim in the 6/8 last bar (4,038 states);
- a dotted crotchet in M11 bass bars (about 13,500 states).

Two choices lead to a dead end:
- M4, a dotted crotchet at beat 1 of the last bar: the next offer is `[]` with `done:false`.
- M6, a minim in the 6/8 last bar: also `[]` with `done:false`.

**The palette never blocked a legal length:** 0 blocked states in 485,231, and no dead end from a legal prefix.

**M-11 · M12: two excerpts are not melodies.**
- `k545_50-53`: the "top line" is the right hand's chord tops (`l' – – l' | s' – – s' …`), with two-beat rests, while the melody is the left-hand semiquaver scales. Bar 50 is also in F (B♭ in the left hand), but it is spelt in C.
- `chopin20_5-8`: note 4 (`ri`, F♯4) is an alto semiquaver sounding under the held soprano D5. The soprano's crotchet is cut to a dotted quaver to make room for it.

Recommend removing `k545_50-53` and holding D5 as a crotchet in `chopin20_5-8`.

**M-12 · M12 credits are garbled.** The credit is built with `src.split('.')[0]`, which cuts at the first full stop. Result:
- "J. Bach" for J. S. Bach (3 scores);
- "W. Mozart" for W. A. Mozart (3 scores);
- "Scott Joplin (c. Joplin, "Maple Leaf Rag"" for Maple Leaf.

The credits also drop the encoder and licence (Craig Stuart Sapp, CC BY-NC-SA 4.0) that `meta.json` carries.

## Shoulds

1. **M9 range and key balance.**
   - 1,010 of 5,000 M9 items go above d', up to s' (do + 19). MR1 caps every rung at s,..d'. Every note still stays inside G3–B5.
   - Rejection by the MIDI ceiling skews the keys: C 526 against B♭ 354 and B 374.
   - The kinds are not a quarter each: M-V 667, M-vi 1,081, m-III 916, m-v 692 (20 / 32 / 27 / 21%).
   - The tells are unaffected (see item 4).
2. **M10 range.** 77 of 5,000 items reach fi, (do − 6) as the lower neighbour of s,, which is below the s,..d' cap.
3. **M11 new flag.** 397 of 5,000 items are flagged new but have no inversion, ii or vi. The share by content is 0.584, below 0.60. The M11 "new thing" is the builder's own definition.
4. **R7 and R8 hidden new share.**
   - R7: only 0.33 of items contain a triplet or tim-ka. The flag counts 12/8 and anacrusis, which are shown on screen.
   - R8: tresillo, Charleston or swing in 0.31 of items. Backbeat is context only.
   - The register excluded on-screen novelties for R2, but the build counts them here.
   - R9 tuplets at 0.23 is by design.
5. **Swing playback.** Swing is applied only to `e2` cells. 671 of 698 swing items also hold other off-beat quavers (syn-co-pa, ti ti-i ti, sa ti, ti sa, tam-ti …), and those play straight.
6. **M12 spelling.** Two excerpts respell the score's chromatic note by the direction rule; the score wrote the other name. Marking is by pitch, so the score is unaffected, but the revealed answer contradicts the score.
   - `maple_30-33`, note 6: "ra" where Joplin wrote A♮ ("di").
   - `chopin20_3-4`, note 5: "ra" where Chopin wrote E♮ ("di").
7. **M12 levels.**
   - `k545_56-57` is labelled level 4 but leaps t → s', a leap outside the tonic triad (M6 material).
   - `jesu_1-2` is labelled 6 but is M5 material (natural minor, steps, crotchets and minims).
8. **M12 bar outlines.** 9 excerpts end in a short last bar that no anacrusis accounts for: jesu_9-11, k545_1-4, k545_56-57, k331a_5-8, k331d_7-8, chopin7_4-5, chopin7_14-15, and two Maple excerpts. The four Maple excerpts also have a 735-tick (7-semiquaver) anacrusis. D9 and the API assume an anacrusis of 210 or 420 that shortens the last bar.

## Coulds

- **M3/M4:** t is repeated (`t t`) 579 times at M3. The register says "t moves to d or steps down to l"; a repeat is not a move, but say so.
- **M7:** melodic 2,492 against harmonic 846; the register gives no ratio.
- **M10:** M10 gets tam-ti (`dq`), which the register gives to M9 only. M11 uses vi6 2,186 times, which is unusually frequent.
- **Tritone in natural minor (M6–M11).** The f–t tritone resolves to the relative major's d/m; that is the dominant 7th of III, not of i. It is legal under L104, but worth a word in the feedback.
- **Tuplet tied in from `antB`.** When a triplet or septuplet begins tied from `antB`, its first note has no onset, so the group's first accent is lost (4 cases at R7, 22 at R8, 23 at R9). Rare; consider forbidding a tuplet straight after `antB`.
- **Charleston.** Tam-ti plus two crotchet rests is marked wrong against the Charleston tile, because rest onsets count. This agrees with the register's definition. Note it in the feedback.

## Item 6 · Builder's labels outside the approved table

| label | where | follows the approved rules? |
|---|---|---|
| `antB` "ti ti-", with the next cell starting "i…" | R6–R10 tile and names | **Yes for "ti ti-"**: a quaver pair whose second note is held over the barline, on its vowel. **No for the tie-in names** (M-5). |
| `trq` "ta ti (triplet)" | answer-only cell (swing Nearly) | **Partly**: the table has no name for a triplet crotchet–quaver. By the triplet's syllables it would be "tri-la" (tri-o-la with "o" held), or "ta-ki-ta" → "ta-ta" in konnakol. Needs Justin. |
| `e` "ti", `qd` "tam", `cq` "ta" | anacrusis and short last bars (simple and compound) | **Yes, by extension**: single quaver = ti (half of ti-ti), dotted crotchet = tam (as in tam-ti and 6/8 tam), crotchet in 6/8 = ta (as in "ta ti"). The table lists none of them on its own: confirm with Justin. |
| `err` "sa", `hr` "sa-a" | defined, never generated | "sa-a" (minim rest) is approved. A quaver rest alone as "sa" follows "sa ti / ti sa". |

## Passes (with counts)

**Melody.** Every item, M1–M11 (5,000 each), passes these:
- MIDI = do + solfa, do = 60 + pc, key signatures from the Stage set (all keys drawn), range G3–B5.
- Solfa: movable do, la-based minor, chromatic spellings from Justin's chart.
- M1–M5 move, start and end rules.
- D6/L104: thirds to sixths and octaves of standard quality; no 7ths; every tritone is f–t and resolves inward (186 items at M6). D5: f–si at most once, and the `aug2` flags are exact.
- Endings; metres; bar counts; bar totals exact against my own cell table; anacrusis 210/420 (210 in 6/8) in 29–34% of items, with the last bar shortened; notes match the cells; minimum note counts; tempo 72–96.
- New-thing shares 0.66–0.67 (M2, M3, M5–M10).
- M8: modes end on the home note, mode names right, te → l, fi → s; cue = the mode's tonic triad at do = 60 + pc.
- M9: phrase 1 is bars 1–4; the pivot is common to both keys and is never fa going to V; phrase 2 is in the new key and ends on the new tonic; `newKey` right; both readings right note by note; pivot names right; pivot window = my own computation (3,356 items).
- M10: every chromatic note is a rising raised passing note, a falling lowered passing note, or a lower neighbour (di fi si); all 15 spellings occur.
- M11 on the engine's terms: one bass note per minim (4/4) or per bar (3/4); chord labels match the bass; the melody is a chord tone at each bass onset; no parallels or direct 5ths/8ves at bass onsets; the leading note in the bass rises; ends V–I; no natural so against V in minor.

**Rhythm.** Every item, R1–R10 (5,000 each), passes these:
- Metres and bars; RF positions; no silent bar; bar totals.
- The sounding pattern from my own table equals the engine's events.
- 5/4 cells never cross the grouping; 7/8 groups use the right families.
- Tuplets: one a bar at most, on a beat, only in 4/4 and 5/4; the accents fall on each group's first note, in the events and in the schedule (q7_43 accents at notes 1 and 5).
- Swing plays 2:1. R10 kick: beat 1 always, never 2 or 4, all 32 patterns occur.
- Names: every cell in the approved table carries its approved name in both settings. `LADNAMES`/`_KK` equal the table; `RHYNAMES` = `LADNAMES`.
- R1: exactly the 99 bars of my own enumeration; no repeat within 30 in 3,000 `earGen` draws.
- Shares 0.66–0.68.

**Marking (2,000 items a rung).** These all pass:
- Right answers are right.
- One wrong pitch, an octave error, a missing note, swapped lengths, or a note as a rest is wrong.
- Enharmonic respelling: Nearly at M10 (1,359), wrong at M7 and M8, right at M9 (marked by pitch).
- M10 Nearly plus another wrong note is wrong.
- M9 Keep home do ignores the pivot. Move do with a pivot in the window is right and outside it is wrong (dominant kinds).
- M11 per part.
- Rhythm Nearly cases: D11 (227 at R6), septuplet grouping (402), and swung pair as a triplet only on swing items (280), with straight items marked wrong.
- R10 per part. M12: 46 right and 46 wrong answers marked correctly, and the palette walks every M12 answer.
- Readiness (D10): shown, skipped and Nearly stay out of the window; ready at 8 of 10 only when the next rung is shown.

**M12 against the sources.** 44 of 46 excerpts have pitches and rhythm faithful to the source top line (the exceptions are M-11). All 46 have the key from meta.json and its sections. Solfa is right apart from the two respellings in Should 6. Metre matches the source. Phrase ends on a cadence or a tonic-triad note, except the half cadences, which end on r, t or si, as they should.

**Item 4 · Tells.** I re-measured 123 tells at 5,000 items: at least 4 a melody rung and 3–7 a rhythm rung.
- Features: tempo band, key signature, playing time, metre, anacrusis, note count, tone pitch, bars (M11 bass) and backbeat.
- Targets: new thing, variant or modulation kind, note 2, penultimate note, bar-1 rhythm, first and last cell, tuplets, kick density.
- Largest gain: 2.3 points (R3, tone pitch → first cell; +1.5 cross-validated). None over 5. Figures are in-sample, with 2-fold cross-validation beside them.

## Test suites (run once each, one at a time)
- `earlab_test`: exit 0, `n_failures: 0`.
- `earlab_items_test`: exit 0, `n_failures: 0`.

Both suites check the builder's own rules. The faults above are outside what they test: the melodic si, the M8 mix, the M9 Move do reading, the 5/4 and 7/8 notation, palette offers beyond the legal set, and the consecutive outer voices between bass onsets.
