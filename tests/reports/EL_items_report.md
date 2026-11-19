# Ear Lab item generation and scoring: register 0.48 items R4, EL-6, EL-7, EL-10, EL-11 (logic), R16

Branch `048-elitems`, from live 0.47 (`ef97cdb`). One commit per item. All changes are to generation, marking, stats and answer data, plus the
small amount of copy those items need. `earPlay` and the transport code are unchanged. Card layout and styling are also unchanged: new
controls use the existing `.chip` and `.mini` classes, and the one new wrapper class, `.earask`, has no CSS yet.

| Item | Commit |
|---|---|
| EL-6 chord quality root position | `24e49c1` |
| EL-7 cadences rung 1 | `e9130c0` |
| R4 cadences rung 3, six answers | `d491875` |
| R16 fixture rows | `36c6735` |
| EL-10 scoring integrity | `bed0090` |
| EL-11 rungs and the Stage switch (logic) | `d06502a` |

New suite: `tests/earlab_items_test.py`, added to `tests/run_all`, so `tests/run_all earlab` now runs three suites.

---

## EL-6 Chord quality: root position at rungs 1–3

* `earGenQual`: `inv` is always 0. Close spacing and the two registers are unchanged: the lowest note (the root) is C♯3–C4 or C♯4–C5.
* `earAnsTxt` (qual): augmented and diminished 7th answers give the spelling and say *"It is symmetrical: each note is a major (minor) 3rd above the
  last, so by ear it has no root position or inversion."* They do not name an inversion. Every other answer still says "root position".
* `EARHOW.qual`: "The chord may be inverted …, so the lowest note is not always the root" now reads "Every chord is in root position, played high or low."
* Tests (section Q): 1,500 seeded items per rung. Each is checked for no inversion, the notes against a music21 `ChordSymbol` in root position,
  close spacing, both registers used, the answer text, and three register tells (lowest note banded, lowest note exact, highest note banded). All pass.
* **Judgement for Justin:** with root position only, rung 1 can produce only 2 qualities × 12 roots × 2 registers = 48 distinct voicings.
  The old floor in earlab_test section D (100 distinct items at level 1, from E11) cannot be met, so for chord quality the floor is now
  "all 48 reached". To get back above 100, the options are a third register or open spacing, but the register item says to keep both as they are.

## EL-7 Cadences rung 1: the four basic cadences

* `CADT[1]` is now `perfect: V–I`, `plagal: IV–I`, `imperfect: I–V, IV–V`, `interrupted: V–vi`, in major keys only. The question is the key chord,
  which `earPlay` already plays first, followed by exactly these two chords.
* New `earSATBPair` realises rung 1. It weighs every pair of voicings that is open-spaced (soprano more than an octave above the tenor) and that
  gives no checker error and no checker warning (no leaps of a 7th, no hidden 5ths). It then picks the pair nearest a register drawn at random
  (lowest note, highest note, first bass, last soprano), with smooth voice leading counted too.
* Rung 1 now draws from all 12 major keys (`CKEYS1`). With only two chords and the old 7 keys, the absolute pitch of the last chord predicted
  the answer 41–45% of the time against a chance of 26%. The register-matched choice and the 12 keys bring every tell inside the margin.
* New helpers: `earCadKeys(l, mode)` and `earCadProg(l, rns, key, reg)`, the realisation path for each rung. Questions now carry their rung as `q.l`.
* Tests (section K): 2,000 seeded questions, plus every model × 12 keys × 1,620 register draws (19,440 realisations). Each is checked for exactly
  two chords after the key chord (the playback order is read by stubbing `c2Tone`), open spacing on every chord, 0 errors from the app's SATB checker,
  the independent strict-SATB rules, the cadence type in music21, and major key. Answers are balanced (511/487/505/497). Tells checked: lowest
  and highest note (banded), the register draw, top note of the first and last chord, highest top note, bass of the first and last chord,
  lowest bass, and key. All are inside chance + 5%. The largest excess, the first chord's bass banded, is about 4%.
* earlab_test was adjusted. The level-1 "≥ 3 models" rule became an exact model rule. The second-chord and opening-voicing tells now run at
  rungs 2–3 only, because at rung 1 those chords *are* the cadence.
* **Judgement for Justin:** interrupted V–vi in open voicing, with the 3rd of vi doubled and strict rules, has few voicings: 28 distinct items
  over 12 keys, compared with 90–157 for the other three. The brief set no distinct-item floor for rung 1. If you want more variety, close
  voicing for vi only, or allowing a doubled root after V, would raise it. Both break a rule you set, so neither is done.

## R4 Cadences rung 3 (Stage 6): six answers

* `CADT[3]` was rebuilt. Every model is five chords long and opens I–IV (i–iv), so neither the length nor the second chord gives the answer away.
  * major: perfect `I IV V V7 I`; plagal `I IV I6 IV I`, `I IV vi IV I`; imperfect `I IV I6 ii6 V`, `I IV ii6 V7/V V`;
    interrupted `I IV V V7 vi`, `I IV ii6 V vi`; cadential 6/4 `I IV I6/4 V I`, `I IV I6/4 V7 I`
  * minor: the same shapes on i–iv (ii°6 for ii6, VI for vi), plus Phrygian `i iv VI iv6 V`, `i iv i6 iv6 V`.
* Buttons (`earCadOpts(3)`, `CADL3`): Perfect (authentic), Plagal, Imperfect (half), Interrupted (deceptive), Phrygian, Cadential 6/4. All six show in both modes.
* Feedback (`CADFAM`, in `earAnsTxt`) names the parent family:
  * Phrygian: "an imperfect (half) cadence in a minor key: iv⁶–V, with the bass falling a semitone (le–so)"
  * Cadential 6/4: "the decorated approach to V in a perfect or imperfect cadence: over the bass so, a 6/4 chord falls to 5/3 as it becomes V.
    Here it decorates a perfect (authentic) cadence".
* `earNearTxt`: if the student answers with the family (imperfect for a Phrygian cadence, perfect for a cadential 6/4), the answer is still
  marked wrong, and the feedback adds "… is its family, so you heard the right kind of ending; the answer here is the more exact name."
* The mode is drawn first (50/50), then the answer from the ones that mode has. Minor draws all six, major draws five (no Phrygian). Given the
  mode, the best guess is therefore exactly at chance.
* Rung 3 uses all 12 major and 12 minor keys and a wider register draw (bass 41–53, soprano 64–76). Without these, the Phrygian (minor only)
  did not reach 100 distinct items.
* Tests (section S): 12,000 seeded questions, plus every model × 24 keys × 5 registers (1,200 realisations). These are checked with the app's
  SATB checker (0 errors), the independent rules (including the cadential 6/4 rule that the 6th and 4th fall by step), and the cadence type.
  Each question has exactly one right answer: no other category's ending fits. The six-button set is checked.
  * Mode tell: no answer in either mode exceeds chance + 5%, and the predict test with mode, and with key + mode, also passes.
  * 6/4 bass motion: the bass held on so occurs in perfect (2,239), interrupted (1,130) and cad64 (2,200). Every cadential 6/4 bass ending is
    also heard in a perfect cadence, and the whole bass line does not separate 6/4 from perfect.
  * Distinct items per button: perfect 153, plagal 298, imperfect 270, interrupted 227, Phrygian 150, cadential 6/4 246 (all ≥ 100).
  * Buttons and feedback are checked as rendered, including the family strip after a family answer.
* **Judgements for Justin:**
  1. **Only the perfect form of the cadential 6/4 (I⁶₄–V(7)–I) is used.** The imperfect form (…I⁶₄–V at the end) would end with the bass on so
     held over the last two chords. No other button can end that way, so the bass alone would give it away, which is what the tell test
     forbids. The feedback still defines it as "the decorated approach to V in a perfect or imperfect cadence".
  2. **The perfect button has one model per mode (I–IV–V–V7–I).** That makes its whole bass line identical to the cadential 6/4's. With a
     second perfect model (I–IV–ii⁶–V–I), the bass line alone identified the 6/4 75% of the time against 51% chance.
  3. Marking a family answer as wrong, with an explanation, is my reading of "feedback names the parent family". If you would rather credit
     it as half right, that is a stats-model change: a new kind, `near`.
  4. Rung 3 no longer includes rung 2's 4- and 5-chord models. Rung 2 stays as it was, for review.
  5. The rung 3 minor cadential 6/4 `i iv i6/4 V7 i` resolves the complete V7 to a tonic with a doubled 3rd and no 5th (A A C C). This is legal,
     and the checker passes it, but some textbooks prefer the tripled root.

## R16 Fixture rows

* `tests/fixtures/make_cadence_pcs.py` (new) rebuilds `cadence_pcs`. The app supplies only the models and keys for each rung, and music21
  spells every chord.
* 220 rows for models retired in 0.46.1 were dropped. The brief counted 225: the other 5 (`i iv i6/4 V i` in five minor keys) are live again as
  R4's minor cadential 6/4 model, so they stay. 414 rows were added for rungs 1 and 3, and for the rung 2 model × key pairs that had no row.
  The file now has 573 rows, one for every model × key the app uses. The blind rows are unchanged.
* earlab_test section J: a row for a model the app no longer has now fails instead of being skipped, and every model × key must have a row.
  Result: "fixture rows (chords)" 573, coverage 573 of 573, no skips.

## EL-10 Scoring integrity

**Stats model** (per drill, saved in `localStorage` key `cjg_ear` under `st[drill]`). This is what the UI builder needs:

```
{ n, ok, streak, best, shown, skipped }
  n        answered questions (right or wrong); the score reads ok / n
  ok       right answers
  streak   right answers in a row; only a wrong answer resets it
  best     longest streak
  shown    "Show me" before answering: not a miss, not counted in n, streak kept
  skipped  left before answering (Next, or a change of rung or drill): not a miss, not counted in n, streak kept
```

* `EARST0` holds the zero record. `earStatNext(s, kind)` is the pure update, with `kind` one of `ok | miss | shown | skipped`. It never changes
  its input, and it fills in `shown`/`skipped` for old saved records.
* `earRecord(kind)`, `earSkip()` (returns true if a question was skipped) and `earMark(ok, given)` all use `earStatNext`. `EAR.res` gains
  `kind`. To render counts, read `earSt()` (all six fields, always present).
* Stats line: "Score ok / n · streak · best", then "· shown n" and "· skipped n" when they are not zero. The journal line includes shown and skipped.
* Next before answering records the question as skipped, with the toast "Skipped. It counts as skipped, not as a miss."
* Undo/redo after marking: `earMark` clears the ear history stacks, `histActive()` returns null once the question is marked (so Ctrl/⌘Z and Y
  do nothing), and Clear and the history setter are guarded.
* Reset: the button now shows an inline prompt, "Reset the <drill> score to zero? [Reset] [Keep it]". After Reset it shows "Score reset. [Undo]",
  and Undo restores and saves the old record. The Undo stays until the next marked question. No `confirm` or `alert` is used.
  State: `EAR.resetAsk`, `EAR.resetUndo`. Markup: `earResetHTML()`, buttons `data-earresetyes`, `data-earresetno`, `data-earresetundo`.
* Tests (section M): 9 unit cases on `earStatNext`, including a legacy record and the input left unchanged. The flow test in the page runs
  right, right, Show me, Next (marked), Next (unanswered), wrong, and checks all six fields after each step, the stats line and the toast.
  It also checks the melody undo button before marking and none after, Ctrl+Z and Ctrl+Y after marking, the reset prompt, Keep it, Reset,
  Undo and the saved record, and that no browser dialog opens.

## EL-11 (logic) Rungs and the Stage switch

* UI text: the "Level n" chips are now "Rung n", and level → rung in the cadence and melody notes and the journal and log lines. The
  hand-sign ladder is not called a rung anywhere (checked in the test).
* Stage tags are written out on the drill tabs, as "· Stage 4–5". Each rung chip has its Stages as a tooltip, e.g. "Stage 6".
* Stage switch (`S.level`): a drill is offered at the Stages in its EDR range, and a rung from its start Stage (`ERUNG`) upward:

  | drill | range | rung 1 | rung 2 | rung 3 |
  |---|---|---|---|---|
  | Pulse and metre | 4 | 4 | 4 | 4 |
  | Rhythm dictation | 4–5 | 4 | 4 | 5 |
  | Chord quality | 4–6 | 4 | 5 | 6 |
  | Cadences | 5–6 | 5 | 5 | 6 (Stage 6 only) |
  | Bass and numerals | 5–6 | 5 | 5 | 6 |
  | Melodic dictation | 4–6 | 4 | 5 | 6 |
  | Blind analysis | 5–6 | 5 | 5 | 6 |

  Everything else sits behind a "Show all" chip (`EAR.all`, saved). With Show all on, the chip reads "Show Stage n only". The current drill
  stays visible even when it is outside the Stage, and a drill outside the Stage offers all its rungs.
* `earLvl()` returns an open question's own rung, else the chosen rung if it is shown, else the first rung shown. Answer buttons follow the
  question's own rung.
* Changing rung (or drill) mid-question records the question as skipped and says so in a toast: "Rung changed: the unanswered question was
  recorded as skipped (not a miss)." Clicking the current rung or drill no longer throws the question away.
* Tests (section U): Stages 4, 5 and 6 are set through the real Stage switch. For each, the test checks which drills and rungs are offered,
  then renders, asks and marks every offered rung of every offered drill. It also checks Show all (7 drills, 3 rungs, and back), the wording
  and Stage tags, page errors, a rung change mid-question (skipped 1, n 0, toast, stats line), and a rung change after answering (not a skip).
* **Judgements for Justin:**
  1. The start Stages in the table are mine. They come from the drill ranges already in EDR and from the content of each rung (for example,
     chord quality rung 3 is the 7th chords, so Stage 6). Please confirm or correct them, especially metre (all rungs Stage 4, because EDR
     says Stage 4) and rhythm rung 3 (Stage 5).
  2. A change of drill mid-question is also recorded as skipped. The brief named only the rung, but leaving by drill is the same act, and
     without this the skip count could be dodged.
  3. Changing the Stage itself leaves an open question alone. It is not recorded as skipped.

---

## Test results (this branch, final state)

| Suite | Result | Notes |
|---|---|---|
| `tests/run_all earlab` | pass | earlab_test 0 failures (2,940 cadence realisations, 573 fixture rows / 573 coverage, no skips); earlab_r2_test 1,666 checks 0 failed; earlab_items_test 0 failures (27 tell checks; counts above) |
| `unit_test` | pass | 142 checks |
| `content_lint` | pass | |
| `pageerrors_test` | pass | 881 random clicks, 0 errors |
| `transport_test` | pass | 0 fails, no page errors |

## Not done / for the next builder

* No CSS for `.earask`, and nothing visual for shown/skipped beyond the text in the stats line. The restyle (Fable design) should place the
  shown/skipped counts and the reset prompt.
* The "Show all" chip sits in the drill tab row as an ordinary `.chip`. Its final place and wording belong to the restyle.
* `earPlay` was not touched. Section K reads the playback order (key chord first, then two chord onsets) by stubbing `c2Tone`. If the
  transport agent changes how the key chord is played, that check is the one to look at.
* Saved stats from before 0.48 count earlier "Show me" presses as misses. They cannot be separated after the fact.
