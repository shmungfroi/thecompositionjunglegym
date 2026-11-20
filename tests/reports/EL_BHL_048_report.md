# Ear Lab 0.48: B, H, L (Justin's decisions, 20 Nov 2026)

Branch `048-ear1` from `048-int` @ `a24d936`. Scope: Ear Lab generation and judging (`index.html`) and its tests. Nothing outside the Ear Lab
section of `index.html` changed. Tradition for all harmony rules below: common practice (strict four-part chorale style).

Measurement method (before = `a24d936` exported to `/tmp/bhl/base`, after = this branch):
- Tells: my own script (`/tmp/bhl/scratch/measure.py`), 5 xorshift seeds x 4,000 items per cadence rung (3,000 per chord-quality rung), the
  same held-out predictor as the tests and the independent checker (`predict_acc`: fit on one half, score the other, both ways), edge =
  accuracy minus the most common answer, in points. Mean over seeds, max in brackets.
- Independent checker: the checker's own scripts (`/home/claude/checks/ear/dump.py`, `cadcheck.py`, `basscheck.py`, `tells.py`), copied to
  `/tmp/bhl/ic` (after) and `/tmp/bhl/icb` (before) with only the repo path changed, on 2,600 / 3,600 / 4,200 cadence items (rungs 1 / 2 / 3,
  seeds 11 / 12 / 13) and 3,000 bass-and-numerals items (1,000 per rung).

## B. Interrupted after a cadential 6/4: "Cadential 6/4" is Nearly

| | |
|---|---|
| Finding | Justin ruled (20 Nov) that on the two rung 3 phrases `I IV I:2 V vi` / `i iv i:2 V VI`, the answer "Cadential 6/4" is Nearly. |
| Change | `CAD64_INT_NEARLY = true` (was false); comments at the constant and at `CAD3_HELD` updated. `earJudge` already returns `'nearly'` under the flag; `earMark` records kind `nearly` (gold, streak kept, not added to n or ok, counted in `nearly`); the result panel text comes from `earCadWrong` -> `earCad64IntGiven(min, on=true)`: "You heard the cadential 6/4, and that is right: ... so the cadence itself is interrupted (V–vi), and the answer names the cadence." No other code needed changing. |
| Tests | `earlab_test` merge check now expects the flag on. `earlab_items_test` N flags expect it on; section I: default judging of "Cadential 6/4" on these items is `nearly`, both switch states are still exercised with real clicks (off: "Not this time", streak 0, n+1; on: "Nearly", tally (5,4,3,3,0,0,1) i.e. n and ok unchanged, streak kept, nearly +1, "that is right" text), and the flag is restored to its default (true) after the section and before section U. Section P (every sentence true, both flag states) unchanged and passing. |
| Before / after | before: judge `wrong`, 253 of 4,200 rung 3 items in the checker's sample affected; after: judge `nearly` in all 253 (the checker's `cadcheck.py` still lists them because it was written when the flag was off: expected). |

## H. Rung 1 outer-voice tell

Finding: at cadences rung 1 (four basic cadences, major, open voicing, key chord then two chords), the lowest and highest notes together
predicted the answer: `earlab_test` C failed (32% vs 26% at 6-semitone bands); the checker measured +9.8 / +6.5 / +7.7 (exact / 2 / 3 semitones).
The cause is the span: V–vi in strict open spacing fits only a few registers (bass so rising a step to la, soprano two octaves or two octaves
and a 4th above the lowest note), while V–I, IV–I, I–V and IV–V have many. So the distance from the lowest to the highest note
(span exact: +12.7) told the interrupted cadence apart.

Change (`earR1Pool`, `earR1Weights`, `earR1Draw`, `earWPick`, `earCadReg` rung 1 branch, `earGenCad`, `earSATBPair`):
- Every strict open realisation of each rung 1 model in each of the 12 major keys is listed once: every voicing in the voice ranges with the
  soprano more than an octave above the tenor, no checker error, the strict chord rules, complete chords (so IV keeps the home note the
  feedback names), one 3rd (two in vi after V), no checker error or warning and no strict fault between the chords, and in V–I the leading
  note rises to the home note (the feedback says so). 1,208 realisations before the last two conditions; 631 with them
  (perfect 75, plagal 217, imperfect 311, interrupted 28).
- Each gets a prior (smooth voice leading, `exp(-moveCost/10)`), then iterative proportional fitting (60 sweeps, damped, deterministic, run
  once, about 0.35 s on first use) balances the four answers on: first bass, last bass, first soprano, last soprano, key, the lowest+highest
  pair (exact), and the span. A question draws the answer, then a model and key from that answer's weights, then the voicing (in `earCadReg`,
  still the one register path that `earGenCad` calls).
- The bass interval itself (so–la, so–do, fa–do ...) is the cadence and is not hidden. It is why the result cannot be exactly zero on every
  outer-voice feature at once: the interrupted bass always rises a step from the lowest note, the perfect bass rises a 4th or falls a 5th, so
  the absolute first bass, last bass and lowest note cannot all have the same distribution for every answer inside a bounded bass range.
  The weights split the residual so that no feature is above about +3 points (mean).
- `earSATBPair` (the fixed-register path used by tests and fixtures through `earCadProg(1, ...)`) now picks from the same strict pool.

Tests: `earlab_test` C (6-semitone bands) passes. `earlab_items_test` K adds the lowest+highest pair at exact, 2-, 3-, 4- and 6-semitone
bands and the exact span (5-point margin, like the other tells), and section V runs the strict rules over every realisation in the pool.

Before / after (my seeds, mean edge in points, max in brackets):

| Rung 1 feature | Before | After |
|---|---|---|
| lowest+highest, exact | +14.0 (+14.9) | +1.4 (+2.7) |
| lowest+highest, 2-semitone bands | +8.6 (+9.5) | +1.5 (+2.9) |
| lowest+highest, 3-semitone bands | +8.0 (+8.8) | +1.0 (+2.0) |
| lowest+highest, 4-semitone bands | +6.8 (+8.4) | +1.3 (+2.5) |
| lowest+highest, 6-semitone bands | +5.3 (+6.7) | +1.3 (+1.8) |
| span, exact | +12.7 (+13.7) | -1.0 (-0.4) |
| lowest note, exact | +3.3 (+4.5) | +1.1 (+2.5) |
| highest note, exact | +0.5 (+1.6) | +0.5 (+1.7) |
| first bass | +2.9 (+3.2) | +2.8 (+4.0) |
| last bass | +2.0 (+2.9) | +2.2 (+3.9) |
| first soprano | +1.3 (+2.6) | +1.2 (+2.2) |
| last soprano | +2.8 (+3.8) | +2.1 (+4.4) |
| key | -0.4 (+1.4) | +0.8 (+2.4) |

The checker's own `tells.py` on its own-seed dumps: lowest+highest +15.5 -> -0.9; span +11.4 -> 0.0; outer-voice range bucket (3-semitone)
+8.6 -> +1.8; first bass +4.5 -> +1.6; last soprano +5.8 -> +1.4. Noise floor (answers shuffled, 10 shuffles, exact lowest+highest):
mean -1.1 (range -2.6 to -0.1), so the remaining edge on the exact pair is about 2 points above a shuffled baseline, from +15 before.
`earlab_test` (the failing suite) now passes.

Distinct rung 1 items in 2,000 (`earlab_items_test` K): perfect 91 -> 72, plagal 113 -> 126, imperfect 159 -> 193, interrupted 28 -> 28.
(Perfect is smaller because V–I must now have every chord complete and the leading note rising, which the feedback claims.)

## L. Independent check S1–S3

| | Finding | Change | Test | Before | After |
|---|---|---|---|---|---|
| S1 | Rung 2 cadence realisations broke strict rules (tritone tenor leap VI–V in minor, bass minor-7th leaps): checker 35 in 3,600 | Rung 2 is realised with the strict rules (`earCadProg`: `strict:true` for rungs 2 and 3), with a memoised opening voicing per rung, key and register valid for every model of the rung and mode (`earCadOpen`, generalised from `earCad3Open`), so the opening never depends on the cadence. Strict rules gain: no tritone leap in any voice. | `earlab_items_test` V: 4,000 generated rung 2 items, and every rung 2 model x key x register on the question grid (4,800), through `ic_errors` (now also checking tritone leaps) | checker scripts, seed 12: 23 errors in 5 of 3,600 items (18 tritone leaps, 5 minor-7th bass leaps) | 0 of 3,600; V section 0 errors in 4,000 + 4,800 |
| S2 | Bass-and-numerals realisations broke strict rules (fi of V7/V not rising, bass minor-7th leaps): checker 23 in 800 | `earGenBass` realises with the strict rules (`earBassProg`, trying the drawn register then a fixed list). The V7/V rules now hold for every secondary dominant: `EARRN` gains V7/vi; its leading note (si) is not doubled and rises a semitone. | V: 4,500 generated bass items (1,500 per rung) and every progression x key x register (1,980); `earlab_test` B now realises through `earBassProg` | checker `vl`, 3,000 items: 79 errors in 79 items (29 bass 7th leaps, 50 fi/si not rising) | 0 of 3,000; V section 0 errors |
| S3 | ii⁶–IV (ii°⁶–iv) in 11% of rung 2 items: a retrogression in common practice; the bass drill forbids ii→IV | Rung 2 models rewritten. A four-chord plagal or imperfect model cannot open I–ii⁶ without ii⁶–IV, so the second chord of a four-chord model is vi or I⁶ (VI or i⁶), and of a five-chord model IV, iii or I⁶ (III, iv or i⁶), the same set in every category, so the second chord still gives nothing away. New five-chord models: `I IV ii:1 V I`, `I IV I:1 IV I`, `I IV I:1 ii:1 V`, `I IV ii:1 V vi`, `i i:1 ii°:1 V7 i`, `i i:1 VI iv i`, `i i:1 iv ii°:1 V`, `i i:1 ii°:1 V7 VI`. ii⁶ still precedes V. Fixture rows rebuilt (`tests/fixtures/make_cadence_pcs.py`: 96 retired, 27 added, 528 rows; spellings from music21). | `earlab_test` B: `retro_moves` (ii→IV, ii°→iv) over all 133 cadence models and bass progressions, 6,000 generated cadence questions and 6,000 bass questions | 445 of 3,600 rung 2 items (12.4%, checker's seed 12) | 0 |

Strict-rule coverage now: cadences rungs 1, 2, 3 and bass and numerals, all through the app's `earStrictChord` / `earStrictPair` and
checked independently by `ic_errors` in `earlab_items_test` (S for rung 3, V for the rest).

Also: the checker's `cadcheck.py` now reports no voice-leading fault at any rung (it found 35 at rung 2 before) and no false rung 1 sentence.

## Other tells: re-confirmed (before -> after, mean edge, points)

- Cadences rung 3: identical on every feature (the tritone rule changed no rung 3 realisation): lowest+highest exact +11.3, span exact
  +9.0, 4-semitone bands +3.1, 6-semitone +1.3, last soprano +5.9 (the checker's C2, unchanged).
- Chord quality, rungs 1–3: identical (lowest, highest, 6-semitone bands all within -1.4 to +1.4; the pair at rungs 2–3 is the chord's
  span, i.e. its quality: content, not a tell).
- Cadences rung 2: with the strict rules on the old 3 x 3 register grid the exact-semitone tells grew (pair +10.5 -> +11.7, span +4.9 -> +7.4,
  2-semitone +7.3 -> +8.5). The rung 2 grid is now 4 x 5 (bass 41/45/49/53, soprano 63/67/71/75/79, targets 40–53 / 63–77), which brings
  them below the old values: pair exact +10.5 -> +9.1, 2-semitone +7.3 -> +4.4, 3-semitone +6.5 -> +3.4, 4-semitone +3.9 -> +2.1,
  6-semitone +1.5 -> +1.0, span exact +4.9 -> +4.5, lowest exact +5.7 -> +1.5, last soprano +11.3 -> +7.6, last bass +12.0 -> +10.8.
  Two features moved up by less than a point, inside seed noise: highest exact +2.2 -> +2.4, first soprano -0.1 -> +0.7. Rung 1 key
  -0.4 -> +0.8 (max +2.4), also noise level.

## Suites (after)

| Suite | Result |
|---|---|
| earlab_test | pass, 0 failures (was 1: the rung 1 tell) |
| earlab_items_test | pass, 0 failures (53 tell checks; new section V) |
| earlab_r2_test | pass, 1,666 checks |
| earlab_ui_test | pass, 469 checks |
| unit_test | pass, 640 checks |
| content_lint | pass |

## Self-checks

- Read every rung 2 model for retrogressions by hand as well as by test: the only ii(⁶)→IV were the six the checker named; none in rungs 1
  and 3 or the bass drill (EBALLOW.ii = V, V7/V).
- Second-chord balance: per mode and length every category has the same set (4 chords: vi, I⁶ / VI, i⁶; 5 chords: IV, iii, I⁶ / III, iv, i⁶);
  `earlab_test` C "second chord" and "opening voicing" tells pass at rungs 2 and 3.
- Every rung 2 model x key has a strict realisation on all 20 grid registers (240 of 240); every bass progression x key x register realises.
- Rung 1 feedback facts: complete IV (home note in both chords for "sounds in both chords") and the leading note rising in V–I; the
  checker's sentence checks found 225 + 75 false rung 1 sentences on an intermediate build that allowed incomplete chords; 0 now.
- Ran the checker's scripts on before and after builds with identical seeds, so the S1–S3 numbers compare like with like.
- Cost: first rung 1 question builds the pool and weights once (about 0.35 s). Rung 2 is now strict on 20 registers: a question in a new
  model and key takes up to about 0.3–0.7 s the first time (memoised after; rung 3 already worked this way).

## Open issues

1. Rung 1: the residual is small but not zero (+1 to +3 points on single outer notes; about +2 above a shuffled baseline on the exact pair).
   Exactly zero on all outer-voice features at once is not possible inside the voice ranges, because the bass interval (the cadence itself)
   differs by answer; see H.
2. Rung 1 interrupted items: still 28 distinct voicings (V–vi in strict open spacing with a complete V has about two per key).
3. Rung 2/3 exact-semitone register tells (C2) remain at +9 to +11 for the exact lowest+highest pair (+1 to +2 at 6-semitone bands).
   Rung 2 is now better than before; rung 3 is unchanged. The rung 1 balancing method could be applied to them if Justin wants.
4. Not in my brief but seen while editing: rung 2/3 models `i iv VI ii°:1 V` and `I IV vi IV I` / `i iv VI iv i` move IV(iv) to vi(VI),
   which some common-practice texts also class as a weak (backward) succession. Not changed; flag for Justin.
5. The checker's `cadcheck.py` still reports its "chips" (5,264) and the 253 Nearly judgements: both are expected (the S4 chip label was
   changed by another session, and B is Justin's ruling); its "6/4 bass not held into V" (27 sentences, C1) is unchanged and not mine.
