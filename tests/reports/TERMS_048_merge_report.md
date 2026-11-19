# terms_test on 048-int: the merge failures (branch `048-termsfix`, from 048-int `2a12353`)

All results below are **self-checks** by the builder. An independent check is still needed. Nothing was pushed.

## Cause

There is one cause, and it comes from the Ear Lab card. The Forms room and the climbs are not involved.

* The Ear Lab card (048-elui, `51cf3cf` / `7890b4c`) gave its short cadence answer buttons ("Perfect", "Imperfect", "Interrupted") a
  hand-made title from `ELCADUS`: `'US: '+elUS(k)`. `elUS()` removes the word "cadence", so the hovers read "US: authentic",
  "US: half" and "US: deceptive".
* The R6 fix round (048-r6fix, `c67a252`) rebuilds button hovers from the button's **current text** (`termBtnSync`). It also added the
  terms_test H1 check: no hover may name a US term that the button's text does not contain. "Perfect" alone does not match the term
  pattern ("perfect cadence"), so `termBtnSync` left the card's own title alone, and the H1 check read "US: authentic" as stale.
* Neither branch saw this alone. 048-elui's terms_test had no H1 check, and 048-r6fix still had the old Ear Lab buttons. The
  conflict appeared only on 048-int.
* The failures were reported in every view (gym, keys, climbs, forms…) because the Ear Lab card stays in the DOM, hidden, when
  another room is open, and the checker scans every button in `main`. The page checker caps its findings at 200 (`__TV`), so the
  reported "~200" is the cap. The real count is 3 hovers in every view and after every click.
* The merge also left two smaller problems in the card's text:
  * The Nearly and wrong-answer cadence sentences (5 strings in `earCadNear` / `earCadWrong`) had a hand-written "imperfect cadence
    (US: half)". The term pass treats a hand-written bracket as already present, so it did not add the full term. The result was a
    shortened US term next to an automatic "semitone (US: half step)" in the same sentence. No check looked at what a hand-written
    bracket said.
  * The rhythm tip still underlined "quaver, crotchet, quaver" three times as hover terms (Fable FR-7, left open in
    EL_fablefix_report).

## Decision under L63

A short cadence button keeps the Australian name only ("Perfect"). Its hover gives the **full** US term: "US: authentic cadence",
"US: half cadence", "US: deceptive cadence". This is the same form as every other hover and bracket in the app. Plagal, Phrygian
and Cadential 6/4 have no hover, because the term is the same in both. The key line under the buttons ("Perfect = US authentic", from
Justin's 19 Nov answer 7) is unchanged. It is a key, not a hover, and terms_test still exempts it (`.el-key2`).

## Changes

**index.html**
1. Term system: a short label can declare the term it stands for with `data-tk="perfect"`, using the keys from the shared TERMS list.
   `termBtnSync` puts the full US term for each declared key into the rebuilt hover, after any title the app gave the button.
   `termPass` queues every `[data-tk]` element in the roots it is given, so the observer handles redrawn buttons too. The H1 rebuild
   logic (never added to, the app's title kept) applies to these buttons unchanged.
2. Ear Lab card: `ELCADUS` (the hand-made shortened hover) is removed. `earOptBtn` takes `tk`, and the cadence and blind answer
   groups set `data-tk` for perfect, imperfect and interrupted (`elTk`). `elUS` is kept for the key line.
3. Cadence feedback: the 5 hand-written "(US: half)" are removed. The term pass now brackets the cadence with the full term:
   "this is an imperfect cadence (US: half cadence). It is the special kind…".
4. Rhythm tip: "quaver, crotchet, quaver" (a rhythm pattern, whose terms are already bracketed earlier in the same sentence) is
   wrapped in `data-notm`. It is no longer underlined three times. "A dotted crotchet (US: quarter note) and a quaver (US: eighth note)"
   still carries both terms.

**tests/terms_test.py** (it checks more now. Nothing was loosened, and the existing H1 rule "no hover beyond the text" still applies to
every other button.)
* **C1** (every scan): the test reads a short cadence answer button on its own terms. Its name (without the card's "Your answer" /
  "Answer" badge) is exactly Perfect, Imperfect or Interrupted, and at least one sibling button in the same group is another cadence
  name. Such a button must carry the full US term from the test's own RULE, and it is the only extra US term allowed. Any hover that
  reads just "authentic", "half" or "deceptive" fails. A lone "Perfect" that is not in a cadence group (an interval quality, say) may
  still carry no cadence hover.
* **L8** (every scan): a hand-written bracket after a term must name that term's full US form (plural and rest forms included). For
  example, "imperfect cadence (US: half)" fails.
* Targeted cases: every Ear Lab cadence feedback sentence (right, wrong, Nearly on and off; 6 answers × 5 given; 66 sentences) is
  bracketed and scanned. The Ear Lab rung 3 buttons must read Perfect, Plagal, Imperfect, Interrupted, Phrygian, Cadential 6/4, with
  exactly the three full hovers, both before and after an answer (when the badges show).

**tests/earlab_items_test.py**: the Nearly sentence check expects the cadence with or without the term pass's
"(US: half cadence)" (the panel is read straight after the click, before the pass runs). It now **fails** on any shortened
"(US: half|authentic|deceptive)".

## Before / after

| Run | 048-int `2a12353` | this branch |
|---|---|---|
| terms_test full, old test | ~200 (capped; EL_fablefix_report: 200) | n/a |
| terms_test `TERMS_FAST=1`, old test | 119 (3 shortened hovers × every view, cap 30 shown per section) | n/a |
| terms_test `TERMS_FAST=1`, **new** test | **202** (C1 shortened hover, T3 "no full hover", L8 × 5 sentences, C1 targeted) | **0** |
| terms_test full (Stages 4, 5, 6), new test | — | **0** failures: 153 views, 2,332 clicks, 2,494 scans, 66 feedback sentences |

## Other suites (final tree)

| Suite | Result |
|---|---|
| content_lint | pass (my first code comment quoted "US: authentic cadence" and tripped the cadence-names lint; I reworded it) |
| unit_test | pass, 640 checks, 0 failures |
| earlab_ui_test | pass, 467 checks, 0 failed |
| earlab_items_test | pass, 0 failures |

terms_test was run alone each time: two full runs and three fast runs. The first full run with the new test found 6 failures that
the fast run could not reach. After an answer, the card adds "Your answer" / "Answer" badges inside the buttons, so C1 did not
recognise "AnswerPerfect" as a cadence button. The test now reads the name without the badge, and a targeted "after an answer"
case was added. The second full run passed. No crashes.

Rendered after the fix (Ear Lab, rung 3, Phrygian answered "Imperfect", Nearly): "You heard it stop on V, and that is right: this is
an imperfect cadence (US: half cadence). It is the special kind. In a minor key the bass steps down a semitone (US: half step), fa to
mi (iv⁶ to V), and that is called a Phrygian cadence." The buttons have the hovers "US: authentic cadence", none, "US: half cadence",
"US: deceptive cadence", none, none.

## Open

* **Fable FR-8b ("one bracket is enough" in the Nearly sentence).** The sentence still has two brackets: the cadence and
  "semitone (US: half step)". L63 asks for both terms in answer feedback, so I kept the semitone bracket. To have one bracket, the
  wording would have to drop "semitone", or Justin would have to make an exception. This is for Justin.
* The key line still reads "Perfect = US authentic" (short form, by design, 19 Nov answer 7). Say if it should read
  "authentic cadence".
