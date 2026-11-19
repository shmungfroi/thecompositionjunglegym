# Ear Lab 0.48 reconcile: result-panel text, Nearly, cadential 6/4 label, tests on the card DOM

Branch `048-reconcile`, from `048-int` at `38ea640` (the logic branch `048-logic` and the card branch `048-elui` merged). The code and
test commit is `6b1f3c0`; this report is committed after it. Every check here is a **self-check**: I wrote the tests, and nobody has
checked them independently yet.

## 1. The result panel's cadence sentences must be true of the item

**What was wrong** (seen with `/home/claude/scripts/probe_cad.py`, and in a sweep of 18,000 items, `/home/claude/scratch_logic/claims.py`):

| Case | Card text before | Fact |
|---|---|---|
| Interrupted after a 6/4, answered Interrupted | "V sets up the close, then the bass steps up to vi …"; the 6/4 was not mentioned | The phrase passes through I⁶₄ before V |
| The same phrase, answered Cadential 6/4 | "… There is no held dominant bass here." | False: I⁶₄ and V share the dominant bass |
| Any phrase answered Cadential 6/4 when it was perfect or interrupted at rung 3 | "There is no held dominant bass here" | False for every `I IV V V7 I` and `I IV V V7 vi`: the bass stays on so across V–V7. That is 1,083 of 1,095 perfect items, and many interrupted ones |
| Minor key, answered Interrupted correctly | "… steps up to **vi**" | It is VI. The spec's right-answer sentences were mode-blind apart from "V to I" (Plagal said "IV to I" and the 6/4 said "I⁶₄" in minor) |
| Answered Interrupted when it was perfect | "This time it arrives: the bass **falls** to the home note" | In 55% (rung 1), 65% (rung 2) and 62% (rung 3) of perfect items the bass rises a 4th to do |
| Cadential 6/4 shown or wrong | "falling home to I" | Same: the bass often rises to do |
| Plagal (right answer, or Perfect given) | "the home note is held through both chords" | At rung 1, 183 of 1,489 items have no voice holding do |
| Answered Plagal when it was imperfect | "You heard IV near the end, and that is right" | False when V is not preceded by IV: all of rung 1 `I V`, 210 of 1,458 at rung 2, and every rung 3 imperfect (ii⁶ or V7/V before V) |
| Answered Phrygian when it was something else | "There is no semitone fall in the bass here" | False for 299 rung 3 imperfect, 304 plagal and 84 rung 2 interrupted items, whose bass does fall a semitone somewhere. The true point is that there is none *into a final V* |

**Change: one source of truth.** These are now the only functions that hold cadence teaching sentences:

- `earCadRight(a, q, min)` gives the right-answer and Shown sentences.
- `earCadWrong(a, g, q, min, res)` gives the sentences for a wrong answer.
- `earCadNear(a, min, on)` gives the family answer, as Nearly when the switch is on and as wrong when it is off.
- `earCad64IntGiven(min, on)` covers "Cadential 6/4" given for an interrupted phrase that passes through a 6/4.
- `CAD64INT(md)` is the 6/4-on-the-way sentence, shared with `earAnsTxt`.

The logic branch's `EARNEAR`, `earNearTxt` and `EAR64INT` are removed, and the test checks they no longer exist. All of these functions
are mode-aware: I/i, vi/VI, IV/iv, and so/mi under la-based minor. `earCadFacts(q)` reads each item to support its sentences: the bass
move into the last chord, whether a voice holds do, whether the bass stays on so between chords, the chord before the last, and whether
the phrase is an interrupted one through a 6/4.

**What the panel says now**

- Interrupted through a 6/4, right answer: "V sets up the close, then the bass steps up to vi instead of going home. A cadential 6/4 (I⁶₄,
  the home chord over the dominant bass) comes on the way, but the cadence itself is interrupted (V–vi)." The minor version uses i⁶₄ and
  VI. The 6/4 sentence is also added after every *wrong* answer on these phrases.
- The same phrase, Cadential 6/4 given, switch off (wrong): "You heard the cadential 6/4, and it is there: I⁶₄ over the dominant bass,
  then V. But V does not go home to I: it moves up to vi, so the cadence itself is interrupted (V–vi). The answer names the cadence:
  Cadential 6/4 is the answer only when the 6/4 leads into a perfect cadence (V–I)."
- With `CAD64_INT_NEARLY` on (Nearly): "You heard the cadential 6/4, and that is right: I⁶₄ over the dominant bass, then V. But V does
  not go home to I: it moves up to vi, so the cadence itself is interrupted (V–vi), and the answer names the cadence."
- Cadential 6/4 given on another phrase: if the bass stays on so (V–V7), "The bass does stay on the dominant here, but the chord over it
  is V all along (V, then V7): there is no I⁶₄." Otherwise, "There is no I⁶₄ (the home chord over the dominant bass) here."
- Cadential 6/4 answer, Perfect given, on a perfect item with V–V7: the spec sentence, plus "(The bass does stay on so, but the chord over
  it is V, then V7.)"
- "the bass falls / rises to the home note" follows the item. The home note is "held through both chords" only when a voice holds it;
  otherwise it "sounds in both chords".
- Answered Plagal when it was imperfect: if IV is just before V, the spec sentence. Otherwise, "The last chord is V, not I, so the
  phrase is left open. The chord before it is ii⁶, not IV."
- Answered Phrygian, not imperfect: the parent family's sentence, plus "A Phrygian cadence stops on V, after the bass falls a semitone
  into it."

**Blind analysis** has no voicing data, so `earCadFacts` returns `has:false` and the neutral wordings are used ("goes to the home note",
"sounds in both chords"). Two sentences remain unverified for real score excerpts: the perfect "the leading note rises to the home
note", and Plagal→Imperfect "You heard IV near the end". That is a gap; fixing it needs the blind pool's chord data.

## 2. Nearly: one text, both switch states coherent

- The panel draws Nearly text from `earCadNear` only. With the switch **on** it is spec 9.5 word for word, with "(US: half)" and
  mode-aware details: "You heard V to i close the phrase …" and i⁶₄ in minor; the Phrygian bass is fa to mi.
- With the switch **off**, the answer is marked wrong and the text no longer says "that is right" about it. It says "… and that is the
  right family: a Phrygian cadence is a kind of imperfect cadence (US: half). The answer here is the more exact name. …" The cadential
  6/4 version reads the same way ("a cadential 6/4 decorates a perfect cadence").

## 3. The cadential I⁶₄ in the chord strip

**Decision:** a 6/4 chord directly before V is labelled **"cadential 6/4"** under the numeral, not "tonic". Its hover (`title`) gives both
readings: "Cadential 6/4: the tonic chord in second inversion (I⁶₄, also written Ic), over the dominant bass. Read by its spelling it is
a tonic chord, as this app's Analysis labels it; many harmony texts hear it as part of the dominant, because its 6th and 4th fall to the
5th and 3rd of V over the same bass." The chip colour stays as the app's numeral analysis gives it (tonic, the same as `analyse()` and
the Analysis room), so the strip does not contradict the rest of the app. Inside the cadence bracket (cadential 6/4 answers), the chip
still reads "bass so", as before, with the same hover.

**Why:** both readings are standard, and neither is universal.
- *Spelling, or "Ic":* the British and Australian tradition, and many schoolbooks, name the chord I⁶₄ (Ic), a tonic triad in second
  inversion. The app's `analyse()` follows this everywhere (Analysis, Gym bar grids, the climbs).
- *Function:* most current harmony texts (for example Aldwell & Schachter, and Caplin's formal-function theory) treat the cadential 6/4
  as an embellishment of V. They hear the dominant arriving early, with the 6th and 4th as suspensions or appoggiaturas over 5̂. The app
  already says this in words: the chord library calls it "a grand, decorated perfect cadence: the bass sits on so", the SATB checker
  requires the 6th and 4th to fall, and the R4 feedback calls it "the decorated approach to V".

Labelling it "tonic" in the strip picked one tradition, in the place where the Ear Lab is teaching the other. Naming it by its job
("cadential 6/4") is true in both, and the hover names both traditions. I did not change `earNumFn`, the colour scheme or the app's other
function labels, so nothing else moves.

## 4. Tests rewired to the card (`tests/earlab_items_test.py`)

- **S:** the Nearly (on) and family (off) results are read from `#earMain .el-result`: the class (`near` or `bad`), `.el-verdict`
  ("Nearly" / "Not this time"), the `.el-teach` text, and the option marked `.is-near`. Off must contain "that is the right family" and
  "The answer here is the more exact name", and must not contain "and that is right".
- **N:** the result is `.el-verdict | .el-teach`, the class comes from `.el-result`, the foot from `.el-foot` (must contain "n answered ·
  m nearly · s shown · k skipped"; "answered" excludes Nearly), and the tally from `.el-tally`'s `aria-label` ("Score ok of n, streak s").
  The mode-aware `earCadNear` texts are checked in both states, and so is the absence of a second Nearly source. The Phrygian Nearly text
  must contain neither "le" nor "so".
- **I:** the panel for the interrupted-through-6/4 phrases is checked answered Interrupted (spec sentence plus `CAD64INT`), and answered
  Cadential 6/4 with the switch off and on (lead sentence, "(V–vi)"/"(V–VI)", I⁶₄/i⁶₄, never "held dominant bass", never "that is right"
  when wrong). The chord strip must have exactly one chip labelled "cadential 6/4", with both readings in its title, and no "tonic" 6/4.
- **P (new):** every cadence panel sentence, for every option, Shown, both Nearly switch states, and both `CAD64_INT_NEARLY` states. That
  is 8,000 items over rungs 1–3 and 76,506 sentences, each checked against its own item: bass falls or rises to do, do held, bass steps up
  to vi, no 6/4 claimed where there is one, IV before V, a semitone into V, the 6/4 bass held, V–V7 over one bass, the 6/4-on-the-way
  sentence on exactly the right items, no major numerals or do-based solfa in minor (and no minor numerals in major), no wrong mark
  calling the answer right, and every Nearly saying "that is right". Each rule in P would have caught a row of the table in section 1.

## Test results (`/home/claude/wt-reconcile`, final state)

| Suite | Result |
|---|---|
| `earlab_items_test` | **pass**, 0 failures. S/N/I/P/T counts include 76,506 panel sentences, N 10 flow + 3 Nearly + 3 reverse checks, I 4 feedback + 4 switch checks, 47 tell checks |
| `earlab_ui_test` | **pass**, 367 checks |
| `earlab_r2_test` | **pass**, 1,666 checks |
| `unit_test` | **pass**, 640 checks |
| `content_lint` | **pass** |
| `earlab_test` | **1 failure, still open with Justin:** "cadences L1: lowest and highest note (6-semitone bands) predicts the answer 32% (chance 26%)". Unchanged from 048-logic; seeds not touched. |
| `terms_test` (run alone) | **fail, 200 failures, the same on base `38ea640`**. The 25 listed are T6 "stale or wrong hover 'US: authentic / half / deceptive' on 'Perfect' / 'Imperfect' / 'Interrupted'" in the Forms room and climbs at Stage 4. Buttons with the short Australian word carry the card branch's short US hover, and terms_test's T6 rule expects the hover only where the full term ("perfect cadence") is in the text. This came in with the 048-elui merge. It is not in the Ear Lab cadence text I changed, and I did not touch it. |

## Open points

1. `CAD64_INT_NEARLY`: still with Justin. Both states read correctly and are tested.
2. The rung 1 cadence register tell in earlab_test: still with Justin.
3. terms_test T6 on short-word cadence buttons (from the card merge): the card owner should either drop the hover from single-word
   buttons outside the Ear Lab key line, or terms_test should accept a short-word hover. Either way it is a decision about the terms
   rule, not about cadence theory.
4. Blind analysis: two sentences (above) cannot be checked against real excerpts without the blind pool's chord data.
5. Fable's spec 9.5 wording has been changed where it was untrue of the item. These are theory-accuracy changes to approved copy, so
   Justin may want to read the new variants (section 1).
