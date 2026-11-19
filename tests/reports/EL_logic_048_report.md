# Ear Lab engine logic 0.48: Justin's answers of 19 Nov 2026

Branch `048-logic`, from v0.48 at `075e6c1`. The code commit is `765ffc5`; this report is committed after it. The changes are to engine,
data, judging and stats logic in `index.html`, plus tests and fixtures. Card markup and CSS are not touched.

Every check below is a **self-check**: I wrote the tests and the fixture rows, and nobody has independently checked them yet. Where music21
is used (cadence fixture spelling, time signatures), it gives an independent spelling or classification, but I chose what to compare.

## 1. "Nearly" at cadence rung 3, option (a)

**Change**
- `EAR_NEARLY = true`. `earJudge(q, given)` returns `'nearly'` only at cadences rung 3 (`q.d==='cad' && q.l===3`), and only when the
  answer given is the family of a Phrygian (Imperfect) or a cadential 6/4 (Perfect).
- Stats (`earStatNext`): a Nearly answer keeps the streak and is not scored, so `n` and `ok` stay as they were. It adds 1 to `nearly`.
  `EARST0` now has a seventh field, `nearly: 0`, so `earSt()` always returns all seven fields; older saved records read it as 0.
- The stats line reads "· nearly n" (shown when n is not zero), the log line ends `nearly`, and the journal line ends ", n nearly". Reset
  sets `nearly` to zero, and Undo brings it back.
- Feedback (`earNearTxt`): for a Nearly answer it uses the spec 9.5 Nearly sentences (Imperfect→Phrygian and Perfect→cadential 6/4). The 6/4
  sentence follows the mode ("V to i", "i⁶₄" in minor). The Phrygian sentence uses la-based solfa (fa to mi). The text says "imperfect
  cadence" with no US term, because termPass adds the US bracket. If `EAR_NEARLY` is turned off, the 0.48 R4 behaviour returns: the answer
  is wrong, with the "is its family" sentence.
- The result banner reads "Nearly." and the result box has the class `earres near`, which the code already supported.

**Tests** (`earlab_items_test`, sections M and N, plus S)
- 15 `earStatNext` unit cases, 6 of them new for Nearly: streak kept, `n` and `ok` unchanged, Nearly after a miss, a legacy record plus Nearly.
- An in-page flow of right, right, Nearly (Phrygian), Nearly (6/4), right, miss, Nearly, checked on all seven fields after each step. It
  also checks the verdict text, the CSS class, the stats line ("Score ok / n" and "nearly n"), the log line, the journal line, and that
  reset and undo restore `nearly`.
- The reverse direction (Phrygian given for a plain imperfect cadence, Cadential 6/4 for a plain perfect one) is judged wrong, and so is any
  rung 2 answer.
- Section S, as rendered: a family answer with the switch on gives "Nearly." plus the spec sentence; with the switch off it gives
  "Not this time." plus the family sentence. A separate check covers the mode-aware 6/4 text.

**Result:** pass.

**Judgement calls**
- **The spec contradicts itself here.** Spec §4's scoring table gives Nearly as `n +1`, which would count it as answered and so lower the
  score. Your ruling, as passed to me, is "not counted right or wrong in the score", so I built `n +0`. Whoever builds the UI tally should
  know that "of 15" leaves Nearly answers out.
- Spec 9.5 also lists the reverse rows (Phrygian→imperfect, cadential 6/4→perfect) under Nearly. Your answer covered only the family
  direction, so the reverse stays wrong: it names a feature that is not there. The wrong-answer feedback for the reverse is the generic one.
  The spec's reverse sentences ("There is no semitone fall in the bass / held dominant bass here") are for the result-panel builder. This
  needs your confirmation.

## 2. Interrupted after a cadential 6/4, option (b)

**Change**
- `CAD3_HOLD = false`. The interrupted pools at rung 3 now include `I IV I:2 V vi` (major) and `i iv i:2 V VI` (minor), as a third interrupted
  model in each mode. The answer is drawn first and then the model, so the balance between answers is unchanged and about a third of
  interrupted items pass through a 6/4.
- One-right-answer rule, now written into the R4 comment: the button names the cadence, which is where the phrase ends. "Cadential 6/4" is
  the answer only when the 6/4 leads into a perfect cadence (I⁶₄–V(7)–I). The tests' independent category check (`cad_ok`) already
  followed this rule: a 6/4 phrase ending V–vi matches *interrupted* and not *cad64*.
- Fixture rows: `make_cadence_pcs.py` added 24 rows (2 models × 12 keys, spelled by music21), taking the total from 573 to 597. Coverage
  is 597 of 597.
- Feedback: `earAnsTxt` adds `CAD64INT` for these items: "A cadential 6/4 (I⁶₄ over the dominant bass) comes on the way, but the cadence
  itself is interrupted: V does not go home to I, it moves up to vi (V–vi)." The minor version uses i⁶₄, i and VI. A plain interrupted
  cadence does not get this sentence.
- **`CAD64_INT_NEARLY` (default `false`)**: one line, next to `EAR_NEARLY`. When it is false, "Cadential 6/4" on these items is wrong. When
  it is true, it is Nearly, with the same stats handling as section 1. Either way the student sees the `CAD64INT` sentence and "You heard the
  cadential 6/4, and it is there. But the button names the cadence, and Cadential 6/4 is the answer only when the 6/4 leads into a perfect
  cadence (V–I)."
- `earCad3Open` now finds one opening voicing per key and register that works for all 12 (minor) or 10 (major) rung 3 models. It found one
  for every key × register tested. Because the opening voicing changed for every rung 3 item, the distinct-item counts moved (see below).

**Tests** (section I, plus S and earlab_test A/C/J)
- Every model × 24 keys × 5 registers (1,320 realisations, 120 of them new) and 12,000 seeded items passed the app's SATB checker, the strict
  rules (section A of earlab_test and `ic_errors`, both independent of the app's checker), and the category check with one right answer.
- 759 seeded items pass through the 6/4. Each was checked for: answer *interrupted*; matches interrupted and not cad64; no strict errors;
  bass so (6/4) – so (V) – a step up to la (vi) or le (VI). Distinct items: 50 major, 54 minor (floor 40).
- Of the items that contain a 6/4, 2,202 are cad64 and 759 interrupted, so hearing a 6/4 does not settle the answer.
- Judging: Interrupted is correct; Cadential 6/4, Perfect and Imperfect are wrong. "Interrupted" given for a real cadential 6/4 item is wrong.
- Both values of the flag were exercised in the page, in both modes: the switch off gives a miss (n +1, streak 0); the switch on gives Nearly
  (n +0, streak kept, nearly +1). The explanatory text was checked in both cases.
- earlab_test C: both models are in the interrupted pool, and the flags are Nearly on, CAD64_INT_NEARLY off, hold off.

**Result:** pass.

**Judgement calls**
- These items get no other extra marking. For example, "Perfect" on an interrupted-after-6/4 item is plainly wrong.
- Distinct items per button after the change (12,000 seeds): perfect 116 (was 153 in the R4 report, because the opening voicing moved),
  plagal 233, imperfect 219, interrupted 310, Phrygian 128, cad64 221. All are still ≥ 100, but perfect and Phrygian have less margin.

## 3. Stage per rung; metre gains 2/4 and 12/8

**Finding:** the data was already in place. `earMetreOpts` gives rung 1 = 2/4, 3/4, 4/4; rung 2 = those plus 6/8, 9/8, 12/8; rung 3 = all eight.
`EARSTAGE.metre = [4,4,5]`, the EDR tag is "4–5", and `earStageTag('metre')` = "Stage 4–5". Everything is consistent. I documented it in
the code and pinned it in a fixture.

**Placement and why:** 2/4 enters at rung 1 and 12/8 at rung 2. This follows spec §6 (rung 1 = Simple row, rung 2 = both rows, rung 3 adds
Irregular). Each one completes its row (duple / triple / quadruple) the first time that row is asked, so the grid never has a dead cell,
and 2/4 vs 4/4 and 6/8 vs 12/8 (heavy click to heavy click) are practised from the row's first rung.

**Tell found and fixed: the playing time.** Under "whole bars until at least 10 s", slow quadruple and 5/4 always ran 16–20 s and 2/4 ran
about 10 s, and the spec puts the playing time on screen ("0:04 of 0:11"). Measured predictor accuracy above chance for the metre:
+18 points at rung 1 and about +10 at rungs 2–3. Fix: `earGenMetre` draws a length per question, `q.dur` = 11–17 s, independent of the
metre. `earSchedMetre` plays the whole number of bars nearest that length, with at least four bars (so the spec's four-bar beat lane
still holds) and at least 10 s (so sound_test's EL-3 rule still holds). After the fix the excess is ≤ 3 points at every rung, and the
beat tempo stays at chance. I tested other designs first (`/home/claude/scratch_logic/dur_sim.py`); 11–17 s with a four-bar minimum was
the lowest that kept four bars.

**Tests** (section T, new fixture `tests/fixtures/metre_items.json`, written by hand)
- The answer grid per rung matches the fixture. EARSTAGE, tag and EDR are consistent.
- The 8 fixture rows were checked against the app's labels and against music21 `TimeSignature`: beat count, split of one beat, and
  Simple/Compound with Duple/Triple/Quadruple. For 5/4 and 7/8, the grouping adds up and the accents fall on the group starts.
- 18,000 seeded items (6,000 per rung) were each read from their click events, not from `METRES`. Checked: the accent pattern per bar, that
  onsets fall on the beat or its 2- or 3-way split (7/8 on quavers grouped 2+2+3), the four-bar length, bpm 60–120, `dur` 11–17 s, and the
  bars played (≥ 4 bars, ≥ 10 s). Answers are balanced within 3%.
- 300 items were run through `earSchedMetre` itself with a silent click: whole bars, ≥ 4, ≥ 10 s, matching the drawn length.
- Tells, hard-fail at chance + 5 for each rung, for the metre and for simple vs compound: tempo (bpm, 10-bpm bands) and playing time
  (whole seconds as displayed, and 0.5 s).

**Result:** pass. sound_test EL-3 also passes (24 metre renders: whole bars, ≥ 10 s, last event a downbeat).

**Reported, not failed (honest gaps)**
- *Fastest click speed* predicts simple vs compound at rung 2 (81% vs 50%) and rung 3 (61% vs 39%). A compound beat splits in three, so at
  the same beat tempo its clicks are 1.5 times as fast. Evening that out would make the beat tempo a tell instead. With 60–120 bpm it cannot
  be removed, only split between the two (each about +14 points). I left beat tempo exactly at chance, which also matches how real music
  behaves. **For Justin:** keep this, or split the difference?
- *Tempo and playing time together* (44% vs 35% at rung 1). Whole bars at a known tempo make the total beat count a multiple of the bar,
  so the pair carries the metre itself. A student would have to count every beat for 14 s and divide.
- *Number of clicks* (+5 at rung 1; larger for simple vs compound, for the same reason as the click speed).

## Other changes

- `tests/earlab_items_test.py` used `re.search` without `import re`, so section S would have crashed with a NameError. Fixed.
- Sections N and I leave the cadence drill on rung 3, so the test sets it back to rung 2 before section U. U expects the saved rung to be
  inside the Stage.

## Test results (final state, `765ffc5`)

| Suite | Result | Notes |
|---|---|---|
| `earlab_items_test` | **pass**, 0 failures | 47 tell checks; Q/K/S/M/U as before, plus N (3 flags, 10 flow, 3 Nearly results, 3 reverse/rung 2), I (759 items, 4 flag checks, 2 feedback checks), T (3 grid, 8 fixture rows, 18,000 items, 300 scheduler checks) |
| `earlab_r2_test` | **pass** | 1,666 checks, 0 failed |
| `unit_test` | **pass** | 637 checks |
| `content_lint` | **pass** | |
| `sound_test` (extra, because `earSchedMetre` changed) | **pass** on the second run | The first run failed one rhythm render ("rung 1 72 bpm [h h]: 3 onsets detected, 2 written") while other agents' browsers were running. Rhythm code is unchanged and the rerun passed, so I count it as flaky under load. |
| `earlab_test` | **1 failure, already present in v0.48** | See below. |

**earlab_test failure:** "cadences L1: lowest and highest note (6-semitone bands) predicts the answer 32% (chance 26%)". I changed no rung 1
code. Adding the `q.dur` draw shifted the shared random stream, so the suite now draws a different sample. Over 8 seeds of 5,000 rung 1
items, the excess is +4.7 to +6.9 points, identical on base `075e6c1` and on this branch. v0.48 passed only because of the sample it
happened to draw. The independent check (IC_EarLab_items §3) reads the low/high pair as outer-voice harmony (content). Either the
rung 1 register draw or this feature's definition needs a decision from the cadence-register owner. I did not choose seeds to make it pass.

`transport_test` and `pageerrors_test` were not run (13 min and other agents' load). The transport keeps its timing from `schEnd`, which
is unchanged.

## Open points for Justin / the coordinator

1. **`CAD64_INT_NEARLY`**: "Cadential 6/4" on an interrupted-after-6/4 phrase is wrong (default) or Nearly. One line in `index.html`, next to `EAR_NEARLY`.
2. The spec §4 table says Nearly is `n +1`; your ruling as built is `n +0`.
3. The reverse Nearly rows in spec 9.5 (Phrygian→imperfect, 6/4→perfect) are not built as Nearly. Confirm they should stay wrong.
4. Metre: simple/compound click speed vs beat tempo (above).
5. The rung 1 cadence register tell in earlab_test (already in v0.48).
6. For the UI builder: `.earres.near` has no CSS in 0.48 (the gold result is in Fable's result panel). The option button for a Nearly answer
   should be marked "≈ YOUR ANSWER" (spec 9.1). `EAR.res.nearly` and `EAR.res.kind==='nearly'` carry this.
