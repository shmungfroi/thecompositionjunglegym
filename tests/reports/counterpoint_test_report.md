# counterpoint_test.py: report (charter suite 6, species and fugue)

Run: `python3 tests/counterpoint_test.py <repo>`. Against the current `index.html` it passes (exit 0) in about 100 s (wall clock 1 min 37 s), with 0 failures and 7 known failures (plus one model listed for the record). It is deterministic: fixed seeds, so a rerun gives the same counts.

## What it checks and how

The suite drives the app's own functions in a headless page and judges everything in Python: music21 for interval names, plus a rule checker written from the rule-book texts (C2RB, C3RB, C3MRB) and Fux. It never uses the app's checker as the oracle. It compares every issue the app reports, errors and warnings, as (rule code, severity, notes). Where the app's code departs from its own rule book, the suite follows the rule book. The app's reading of each such rule is coded as a named switch (a "quirk"). If the app agrees with the rule book, the case passes. If it agrees only once a quirk is switched on, the case counts as a known failure with that id. Anything else is a failure. If a known failure stops showing up, it is listed under `known_failures_not_seen_this_run`.

| Section | What | Count |
|---|---|---|
| A | `c2Iv` name and class for every ordered pair of 105 pitches (C2–B6, ♭/♮/♯) vs music21, plus the name of every vertical in every two-voice check | 11,025 + 272,669 = **283,694 names** |
| B | rhythm layout of species 1, 2, 2-with-whole-note penultimate, 3, 4 (broken ligatures), 5 (florid plans), 4–16 bars; `c2Plan` obeys the florid limits; `c2RhFix` keeps valid plans | 182 layouts, 240 plans |
| C | two voices, 6 modes × 6 species × 2 positions: 71 embedded models, 529 solver outputs (3 seeds; 3 ligature sets for species 4; 3 rhythm plans for species 5; 10 random cantus lines of your own, rising and falling), 16 mutations each, one random walk each, random florid plans. Models and solver outputs must be error-free. The 24 rule-card examples must show their rule | **10,980 counterpoints** |
| D | cantus checker C1–C15 (built-in cantus must be error-free) | 4,006 lines |
| E | three voices, first species (T1–T9, V1–V2, M rules): 18 models, 27 solver outputs, 40 mutations each | 1,845 |
| F | three voices, mixed species (MX1–3, T, V, M1/M4/M7): 108 models, 18 solver outputs, 25 mutations each | 3,276 |
| G | climb 13: subject pitches in 24 keys and 6 modes (4 built-in + 600 random subjects); real answer (exactly a 5th up; modal: a 5th up within the mode); tonal answer (so in the head answered by do); inversion around the first note and 1↔5 (same rhythm, every step reversed, do↔so); augmentation (every value doubled); drawn lines (moved by octaves only, within a tritone of the subject); playback buttons (diminution = exactly half the subject's onsets and lengths, augmentation = double, inversion = the independently pitched inversion) | 1,815 lines (~21,700 pitches), 1,210 inversions, 605 augmentations, 20 playback runs |

**Compared with the previous suite** (6,300 counterpoints, 243,113 names): this run checks 10,980 two-voice counterpoints and 5,121 three-voice ones, which the old count may not have included. Its 283,694 interval names include a complete 11,025-pair table. I do not know exactly how the old suite counted. My guess is that its names came only from verticals, as Section A's second figure does here.

## Defects found (known_failures; the app is not changed)

- **CP-1. Third-species cambiata needs a fifth note (S3b/S3c).** `c2Check` species 3 also requires the note after the figure to step up: `(!n2||!n3||n3.dn-n2.dn===1)`. The rule book S3c, Fux, and the app's own species-5 check all use the four-note figure. Repro: Dorian, species 3, above, cp `[…,31,32,31,29,30,29,…]` (attacks 28–33 of the CP-1 example in the JSON report). The app gives S3b at attacks 29–31. 68 cases.
- **CP-2. Florid tied unison not reported (H4).** In species 5, a tied note that makes a unison on the downbeat gets no message at all. Species 4 warns about the same thing, and H4 is tagged "Must 5". 385 cases (warnings), including 16 solver outputs and 1 model.
- **CP-3. Cantus C6.** The text says to turn back by step after a 5th, 6th or octave. The checker accepts a leap back after a 5th. Repro: cantus on F, `… C4 G4 D4 …`. 732 cases.
- **CP-4. Three-voice M3.** `c3Check` judges two leaps by adding their sizes (gen sum > 7). So it warns about leaps outlining an octave (3rd+6th, 4th+5th) and misses those outlining a tritone. A repeated note between the two leaps also does not reset the count. Repro: Dorian, cantus low, middle voice `33,35,40` (a 3rd then a 6th: an octave) is warned. 101 cases.
- **CP-5. Mixed species misses V2 into the downbeat.** From the species voice's last note into the next downbeat, only similar-motion 5ths and octaves are checked. **Built-in model `lydhigh23` breaks V2:** bottom voice F3 → C3 against middle F3 → C4, a unison to an octave by contrary motion (bars 1–2). 107 cases.
- **CP-6. Mixed species, successive downbeats.** Perfect intervals on successive downbeats involving the species voice are always V1/V2 errors. The rule book (MX2: "the same rules as two-voice species") points to S2c (allowed if the weak beat leaps more than a 3rd) and S3d (a Should). 170 cases. This one is a judgement call, but the app's own text supports the rule-book reading.
- **C13-1. Minor 7th spelled wrong at the ends of a line.** `c13P` raises the 7th degree when a neighbouring note is the tonic. A missing neighbour (first or last note) counts as the tonic because JS `mod(null,7)===0`. Repro: A minor, cells `[2,1,-1]` → C4 B3 G♯3 (a diminished 4th). `[2,1,-1,-2]` gives G3. 48 lines; answers inherit it.

## Notes, not tested

- `aeo2above` has no model (null), so the solver finds none. The suite reports it as a count and does not check whether a counterpoint exists.
- `c3Check` T8 tells the user to "raise it if needed" (the minor 3rd in the final chord), but nothing in the app can raise it.
- `c3mCheck` lacks c3's "bass begins on the final or 5th" warning. So `lydhigh23` opens with the species voice entering on D3, under F3–F4.
- Playback: a button clicked in the same tick as the previous one sometimes plays nothing. The test waits 300 ms between clicks and retries once. I could not pin the cause down and did not treat it as a defect.
- Not covered: `c13Pair` and what uses it (canon, stretto, countersubject, transformation tables), the fugue planner, the ladders and the drawing.
- Some details were matched to the app because the rule book leaves them open: where an issue is attached (which notes), the de-duplication of S2c against V1/V2, and the C4 and C12/C13 thresholds.
