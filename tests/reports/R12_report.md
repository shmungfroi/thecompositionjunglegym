# R12: counterpoint checker defects (0.48 correction register, Must)

Branch `048-r12`, based on 0.47 (`ef97cdb`). Files changed: `index.html`, `tests/counterpoint_test.py`, `tests/reports/counterpoint_test_report.md`, this report.

The rule source in every case is the app's own rule book (climb 2 rule cards `C2RB`, `C3RB`, `C3MRB`). No rule was added.

## The seven defects

| id | defect | cause | fix (function) | regression case (section R of `counterpoint_test.py`) |
|---|---|---|---|---|
| CP-1 | Third species: the cambiata needed a fifth note | the `camb` test in species 3 also asked that the note after the figure step up: `(!n2\|\|!n3\|\|n3.dn-n2.dn===1)` | `c2Check` (species 3): the extra test is removed. The four-note figure is what S3c, Fux and the app's own species-5 check use. | Dorian, species 3 above, attacks 28–31 D4 C4 A3 B3 and then A3: no S3b, and the app agrees with the rule book on the whole line |
| CP-2 | Florid: a tied unison on the downbeat was not reported (H4) | the species-5 tied-note branch handled dissonant ties only | `c2Check` (species 5): a consonant tied note that makes a unison on the downbeat gets an H4 warning, worded as in fourth species | Aeolian florid solver output: H4 warning at attack 11 |
| CP-3 | Cantus C6 accepted a leap back after a 5th | the "turn back by step" test was applied only after a 6th or octave (`iv.gen>=6&&…`) | `c2CantusCheck` (C6): after a 5th, 6th or octave the next move must turn back **by step**, as the card says. The message already said this. | cantus on F, `… C4 G4 D4 …`: C6 warning on notes 9–11 |
| CP-4 | Three voices, M3: two leaps judged by summed size; a repeated note did not reset | `c3Check` warned when the two generic sizes added to more than 7 | `c3Check` (M3, rule `twoleaps`): the outline of the two leaps is judged, as in the rule card and the two-voice checker: warn on a 7th, a tritone or more than an octave; a 5th, 6th or octave is fine. A repeated note (or an empty bar) ends the pair. New message names the outline. | Dorian, cantus low: (a) D4 F4 C5 (an octave) not warned; (b) B3 D4 F4 (diminished 5th) warned at bars 4–6; (c) A3 D4 D4 A4 not warned |
| CP-5 | Mixed species: V2 into the downbeat missed; model `lydhigh23` broke V2 | the "last note of a bar into the next downbeat" loop only checked similar motion | `c3mCheck`: that loop now reports V2 (`consecutive`) for contrary motion too. Model `C3MMODELS.lydhigh23` replaced by a `c3mSolve` output (seed 17) | Phrygian (top voice in second species): V2 at bars 10–11; the 0.47 `lydhigh23` now shows its V2 (bars 1–2, bottom/middle); the new `lydhigh23` has no errors in the app or the independent checker |
| CP-6 | Mixed species: perfect intervals on successive downbeats always V1/V2 | the downbeat-to-downbeat loop treated every pair of voices as first species | `c3mCheck`: between the species voice and another voice, in second species S2c applies (error only when the weak beat moves a step or a 3rd; a leap of more than a 3rd breaks them up), in third species S3d applies (a Should, warning). The two whole-note voices, fourth species and the first bar (species voice entering after the rest) keep V1/V2. New rule names `beat5`→S2c and `qbeat`→S3d in `C3MCODE`. One sentence added to the mixed-species "Understand" text saying so. | Phrygian second species: S2c at bars 9–10 and no V1/V2 there for that pair; Phrygian third species: S3d warning at bars 6–7 and no V1 |
| C13-1 | Climb 13: the minor 7th spelled wrong at the ends of a line | `c13P` raised the 7th when `mod(prev,7)===0`; JS `mod(null,7)` is 0, so a missing neighbour counted as the tonic | `c13P`: only a neighbour that exists and is the tonic raises the 7th | A minor C B G and G E A: G natural; C♯ minor subject: B natural; A minor A G A: G♯ still raised |

The new `lydhigh23` (Lydian, cantus on top, bottom voice in third species, middle voice in whole notes): middle F4 E4 G4 F4 E4 C4 D4 E4 D4 E4 C4; bottom begins on F3 (the final; the 0.47 model began on D3) and ends E3–F3. The checker notes one T6 (a unison in the middle). It was the best-scoring of 16 solver seeds with the bass on the final (seed 1 scored the same, with an S3d note, but began on D3).

## Tests

- `counterpoint_test.py`: the quirk switches and known-failure list are gone. The independent checker is the rule book only, and every disagreement fails. Models and solver outputs must be error-free under the rule book (before, only under the app's readings). New section R: 15 regression checks for the seven defects; each must agree with the rule book **and** show the fixed behaviour. The report JSON now has `regression_cases` in place of `known_failures`.
- Results (this worktree):
  - `counterpoint`: pass, 0 failures, 15/15 regression checks. Sweep: 10,980 two-voice counterpoints (71 models, 529 solver outputs), 4,006 cantus lines, 1,845 three-voice, 3,276 mixed-species (108 models), 283,694 interval names, 1,812 climb-13 lines, 1,208 inversions, 604 augmentations, 20 playback checks, 0 page errors. About 400 s under parallel load (100 s alone).
  - `unit`: pass, 142 checks, 0 failures.
  - `content_lint`: pass.
  - `pageerrors`: pass, 153 views, 4,244 clicks, 881 random clicks, 0 errors.
- `counterpoint_test_report.md` updated: the defects are marked fixed, and section R is added to the table.

## Judgements for Justin

1. **CP-2 severity.** H4's tag says Must for species 5. The tied unison is a fourth-species element inside florid, and fourth species only warns about it ("allowed but use it sparingly"), so florid now **warns** too. A unison from a new note on a florid downbeat is still an error. The species-5 description supports this: "Each note value keeps the rules of its own species".
2. **CP-6 reading.** The MX2 card says "The same rules as two-voice species, now checked against both other voices", so S2c and S3d are applied to pairs that include the species voice. In third species this turns a 0.47 error into a warning (S3d is a Should). The S3d card has no exception for the final bar, so S3d also covers the step into the last downbeat in mixed species. The two-voice checker leaves that one out. I followed the card; say if you want them made the same.
3. **CP-6, S2c with a missing weak beat.** While a student is still filling in the line, S2c waits until the weak-beat note is written, as the two-voice checker does.
4. **Messages.** New or changed wording: the CP-2 warning, the CP-4 M3 message (now names the outline, like the two-voice one), the CP-5 V2 message ("by contrary motion"), and the CP-6 S2c/S3d messages (taken from the two-voice wording, naming the voices).

## Not done / notes

- `c3mCheck` still has no "bass begins on the final or 5th" warning. That is a known note and is not part of R12. Only the replacement model was chosen to begin on the final.
- In `c2Check` species 3 the variable `n3` is now unused. I left it to keep the diff small.
- No other models changed. I checked: none of the 108 mixed-species models gets an S2c or S3d message under the new rules, and none has an error.
