# Ear Lab 0.48: rung 1 S2 (model share) and S1 (soprano switch), after IC_EAR2_048

Branch `048-ear2` from `048-int` @ `1ae7b0f` (worktree head `5f178a8`). Scope: `earR1Pool`, `earR1Fit` / `earR1Weights`, `earSATBPair` in
`index.html`, and `tests/earlab_items_test.py` (new section K2). Tradition for every voicing rule: common practice (strict four-part style).

Method. "Before" is `5f178a8` (the merged H build). Sampled figures: 5 xorshift seeds x 4,000 rung 1 questions through `earGen('cad',1)`,
held-out predictor (`predict_acc`, fit on one half, score the other), accuracy in % with chance 25–26%; "edge" = accuracy minus chance, mean
over seeds (max in brackets). Exact figures: Bayes accuracy computed from the app's weights (the way IC_EAR2_048 computed its soprano numbers).
Variety: distinct (key, voicing) per answer in 20,000 real draws (the checker's definition).

## S2: IV–V had almost vanished from imperfect cadences

| | |
|---|---|
| Finding | After the H fitting, imperfect items were 84% I–V and 16% IV–V, so a first chord of IV meant plagal 86% of the time (the first chord alone answered 71%). |
| Change | `earR1Fit` holds the model share inside each answer with two models (imperfect: I–V, IV–V) at half each, before the first sweep and again at the end of every sweep, so the share is fixed rather than traded against the register balance. |
| Tests | `earlab_items_test` K2 (6,000 items per switch state): IV–V share 42–58% of imperfect; first chord IV -> plagal <= 72%; first chord alone <= 66%; plus every register tell (lowest+highest at 1/2/3/4/6-semitone bands, span, first/last bass and soprano, key) within the 5-point margin; strict rules (`ic_errors`) and open spacing on every item. |

| Rung 1 | Before | After (switch off) |
|---|---|---|
| IV–V share of imperfect | 16.2% | 49.9% |
| first chord IV -> plagal | 86.3% | 67.2% (two in three is the floor: every plagal and half of imperfect start on IV) |
| first chord alone (accuracy) | 71.4% | 63.1% |

### Variety: true numbers from real draws

My H report's "72 / 126 / 193" was wrong as a measure of what students hear: `earlab_items_test` K counted the generated items together with
the fixed-register sweep (`earCadProg(1, ...)` over 19,440 registers), which is not how questions are drawn. The checker's 47 / 67 / 96 is right.

To raise variety without a tell, V–I may now end on the incomplete tonic (5th left out, root tripled, the leading note still rising to the
home note): `EARR1OPT.inc`, on by default. This is the common-practice incomplete I after V. It adds 55 perfect realisations to the pool
(75 -> 130), and it also gives V–I the so–mi top line that only V–vi had. Every other chord stays complete (IV keeps the home note the
plagal feedback names). The rung 1 sentences still check true (`earlab_items_test` P; the checker's `cadcheck.py`, 4,000 rung 1 items:
0 voice-leading faults, 0 false sentences).

| Distinct in 20,000 draws | perfect | plagal | imperfect | interrupted | total |
|---|---|---|---|---|---|
| Before (H) | 47 | 69 | 98 | 28 | 242 |
| After, switch off | 92 | 65 | 81 | 28 | 266 |
| After, switch on | 106 | 90 | 112 | 28 | 336 |

Imperfect falls (98 -> 81) because IV–V, which has fewer strict open voicings, now carries half of it. Interrupted stays at 28: V–vi in
strict open spacing with a complete V has about two voicings per key. I tried flattening the weights (raising them to a power < 1) for more
variety: +20 to +40 distinct cost +1 to +3 Bayes points on first bass and span, so I left it out.

## S1: soprano solfa (switch, default off)

| | |
|---|---|
| Finding | The top line in solfa alone answered rung 1 90.9% of the time (so–mi only in V–vi, so–so only in V–I, do/la over IV only in plagal). |
| Change | `let RUNG1_SOP_BALANCE=false` (Justin has not ruled). When on, the top-line solfa path (first and last soprano degree together) joins the balanced features, fitted first in each sweep so the register features keep the last word. All voicings are from the same strict pool. Weights are cached per switch state. I also tried balancing the two soprano degrees separately: soprano tells went a little lower (path 74–75%) but the span and lowest+highest tells rose by 4–5 Bayes points, so the switch uses the path alone. |
| Tests | K2: the default is false; with it on, the three soprano tells are lower than with it off, the soprano path is <= 86% with it off, and the register tells, the IV–V share, the IV-first ambiguity, strict rules and open spacing hold in both states. The flag is reset to false after the section. |

Soprano tells (sampled accuracy %, chance about 25.5%):

| Rung 1 soprano feature | Before | Switch off | Switch on |
|---|---|---|---|
| top-line solfa path | 91.3 | 81.9 | 78.0 |
| soprano degree, first chord | 72.5 | 62.9 | 54.6 |
| soprano degree, last chord | 68.2 | 56.0 | 53.0 |

The path cannot go much lower: the last top note sits in the last chord (I in perfect and plagal; V in imperfect; vi in interrupted), and
V–vi has only two top lines (ti–do, so–mi). That part is the cadence itself.

## Register tells, all three states (sampled edge, points: mean / max)

| Rung 1 feature | Before | Switch off | Switch on |
|---|---|---|---|
| lowest+highest, exact | +0.2 / +0.7 | +0.0 / +1.5 | -0.1 / +1.3 |
| lowest+highest, 2 | +0.3 / +1.3 | +0.3 / +1.1 | +0.7 / +2.3 |
| lowest+highest, 3 | +0.6 / +1.5 | +0.3 / +1.2 | +0.8 / +1.8 |
| lowest+highest, 4 | +0.2 / +1.7 | +0.9 / +2.1 | +0.3 / +2.3 |
| lowest+highest, 6 | +1.3 / +2.6 | +1.0 / +2.6 | +1.0 / +2.2 |
| span | -1.0 / -0.3 | -1.0 / -0.4 | -0.5 / +0.6 |
| lowest / highest | -0.4 / -0.2 | -1.0 / -0.6 | -0.4 / -0.5 |
| first bass | +3.0 / +3.5 | +0.7 / +1.4 | +0.9 / +1.4 |
| last bass | +1.5 / +3.2 | +2.4 / +4.3 | +3.0 / +3.7 |
| first soprano (pitch) | +0.1 / +1.2 | -0.9 / +0.2 | -0.3 / +1.2 |
| last soprano (pitch) | +1.8 / +2.9 | +0.3 / +1.4 | +1.0 / +2.7 |
| key | -0.3 / +1.5 | -0.3 / +0.2 | -0.9 / -0.2 |

Exact Bayes accuracy from the weights (chance 25%), switch off / on: lowest+highest 27.7 / 27.8; span 25.5 / 26.0; first bass 28.6 / 28.6;
last bass 29.5 / 30.1. Last bass is up about a point in both states: the bass interval (so–la, so–do, fa–so ...) is the cadence. It is
within noise in the sampled figures and inside the test margin.

## Suites

| Suite | Result |
|---|---|
| earlab_test | pass, 0 failures |
| earlab_items_test | pass, 0 failures (new section K2) |
| earlab_r2_test | pass, 1,666 checks |
| earlab_ui_test | pass, 469 checks |
| unit_test | pass, 761 checks |
| content_lint | pass |

## Self-checks

- Measured from real draws and from the weights both, and against the merged build with the same seeds.
- The incomplete tonic: pcs within I, 3rd single, root tripled, leading note rising; section V's strict rules run over every pool
  realisation, including these (they allow an omitted 5th, as the checker's rules do).
- The switch changes only the weights; the pool, rules and spacing are shared, and `earSATBPair` follows `EARR1OPT.inc`, not the switch.

## Open

1. S1 is for Justin: whether the top line counts as content. With the switch on the path still answers 78% (floor set by the last chord).
2. Interrupted rung 1 variety is fixed at 28 by strict open V–vi with a complete V. An incomplete V (root tripled) would add some, but I
   did not add it without a ruling.
3. `EARR1OPT.inc` (incomplete tonic in V–I) is a default change made for variety; one line to turn it off if Justin wants complete
   chords only at rung 1.
