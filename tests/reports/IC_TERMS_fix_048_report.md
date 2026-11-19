# IC_TERMS_048 fix round (branch `048-ictermsfix`, from 048-int `2767e9a`)

Fixes the four Musts and Shoulds S1, S2, S4 and S5 in `tests/reports/checks/IC_TERMS_048.md`. S3 (the Ear Lab key line,
"Imperfect = US half") is left as it is: it is pending Justin. All results are **self-checks** by the builder. An independent check
is still needed. Nothing was pushed.

## Findings → change → test → result

| Finding | Change | Test (fails on `2767e9a`, passes now) |
|---|---|---|
| **M1** Ear Lab cadence and blind feedback showed no US term on screen | The headline stays clean (`data-notm`, Fable FR-1). The teaching sentence now names the answer's cadence, and the term pass brackets that first mention. Right answers (shown or correct) lead with it: "An imperfect cadence (US: half cadence): it stops on V and waits there.", "A perfect cadence (US: authentic cadence; V to I): the leading note…" (the pass merges the bracket into the following bracket), "An interrupted cadence (US: deceptive cadence): V sets up the close…". Blind analysis does the same: "A perfect cadence, V7 – I: …", "An imperfect cadence, I – V: …". Every other sentence that does not name the answer's cadence (wrong answers, "Listen to the last chords: …") ends with "This is an imperfect cadence." (`earCadNamed`). Phrygian, Cadential 6/4 and Plagal have no US term, so their text is unchanged. | terms_test **M1i** (every scan): a `data-notm` heading that names a term must have that term's US form on screen in its own panel, outside screen-reader-only text. Targeted: 2,130 result panels as `earResultHTML` draws them (cadences rungs 1–3 × 60 items × every given answer, shown, Nearly on and off; every blind excerpt × every answer). Each panel with a Perfect, Imperfect or Interrupted headline must carry "US: … cadence" in its sentence. On `2767e9a`: 26+ M1i failures, e.g. "Perfect cadence / V to I: the leading note rises…" |
| **M2** "Imperfect (half) cadence" (13 in scores/meta.json, including the Chopin 20 row) | Now "Imperfect cadence (ends on V)" etc. (12) and "an imperfect cadence" (1). They render as "Imperfect cadence (US: half cadence; ends on V)". `tests/numeral_reread.py` expectation updated (ohaupt 3). | content_lint **us_terms**: a shortened US term in a bracket, "(US: half|authentic|deceptive)" or bare "(half)", fails. The "Imperfect (half)" exception is gone. On `2767e9a`: 14 failures (13 meta.json strings plus the teacher note below). |
| **M3** Rhythm tile hovers gave the Australian term only | Tiles carry `data-tt`: the term pass reads the button's own title as text, so the hover becomes "crotchet · US: quarter note", "2 quavers · US: eighth notes", "dotted crotchet, quaver · US: dotted quarter note, eighth note", "crotchet rest · US: quarter rest" (from the shared term list, `termBtnSync`). | terms_test **M3i** (every scan): a button whose own title names a non-scoped term must carry its US hover. Targeted: all 9 cells at rungs 1–3 must match exactly, plus a fragment button. On `2767e9a`: fails ("crotchet", "2 quavers", …). |
| **M4** Circle of fifths: a minor key's neighbours printed in capitals | The neighbours now carry the mode word, as the Relative and Parallel rows above them do: "F minor (one step clockwise: the dominant key) · E♭ minor (one step back: …)". Major keys read "G major". | spelling_test **C**: each neighbour must read as the right mode (a mode word, or lower case with no word means minor), on top of the music21 spelling (48 + 48 checks). On `2767e9a`: 24 failures ("circle A minor: dominant key reads 'E', which reads as major"). terms_test **M4i**: the same rule over all 24 keys. On `2767e9a`: fails. |
| **S1** "a tone under the octave" unpaired | `tone` rx: "under" added to the interval words. | terms_test targeted fragment: "a tone (US: whole step) under the octave". |
| **S2** "dotted crotchet (US: quarter note)" | The note-value rx take an optional "dotted ", and `termUSw` keeps it: "dotted crotchet (US: dotted quarter note)" (also hovers and rests). terms_test's own finder and `usOf` follow the same rule. | terms_test targeted: "A dotted crotchet (US: dotted quarter note) and a quaver (US: eighth note)". The per-scan hover check now expects the dotted form. On `2767e9a`: fails. |
| **S4** forms/rondo never shows both cadence names | "Listen for" gains one line of prose: "Inside the refrain, the fourth bar (US: measure) asks with an imperfect cadence (US: half cadence; it ends on V) and the eighth answers with a perfect cadence (US: authentic cadence; V–I)." | Covered by the existing per-scan first-mention check, now that the term is in prose. Checked as rendered at Stage 6. |
| **S5** content lint knew only "authentic" and "half cadence" | content_lint section 1 is rewritten as **us_terms**. It checks every L63 pair: authentic, deceptive, half cadence, quarter/eighth/sixteenth/half/whole note or rest, whole/half step, staff(s) in a music sense, measure(s) as a counted noun. A term is allowed only inside "(US: …)" / "[US: …]", in the term list's `us:`/`usp:` fields, straight after "US", or in a code comment. Ordinary English is not flagged: "half the class", "Measure every interval", "teaching staff", "staff room", "the whole phrase", "whole-tone", "half-diminished", "a measure of". 27 + 7 built-in positive and negative cases run first, so the lint tests itself. Found in passing: a teacher note had "V7/vi → IV (US: deceptive)", now "the interrupted resolution V7/vi → IV (US: deceptive resolution)". | content_lint passes on this branch and fails on `2767e9a` (14). |

## Suites (final tree, self-checks)

| Suite | Result |
|---|---|
| terms_test full (Stages 4, 5, 6), run alone | pass, 0 failures: 153 views, 2,331 clicks, 2,494 scans; 2,130 Ear Lab panels; 1,371 clean-headline scans (M1i). Run before and after the last rondo wording change (see below). |
| terms_test `TERMS_FAST=1`, run alone | pass, 0 failures (51 views) |
| terms_test `TERMS_FAST=1` on `2767e9a` (new test) | 146 failures, including M1i, M3i, M4i, S1/S2, the M3 fragment |
| spelling_test | pass, 49,164 checks, 0 failures (on `2767e9a`: 24 C failures) |
| content_lint | pass (on `2767e9a`: 14 us_terms failures) |
| unit_test | pass, 640 checks |
| earlab_items_test | pass, 0 failures (section P true-of-item checks unchanged; section I now expects "An interrupted cadence: V sets up the close…") |
| earlab_ui_test | pass, 469 checks |
| layout_test | pass, 162 views, 0 findings, 0 page errors |

Order of runs: unit, earlab_ui, earlab_items and spelling were run before a last wording change in the rondo line ("bar 4 …
bar 8" → "the fourth bar … the eighth", so the room's one bar bracket does not land on a locator; IC C2). After it, content_lint, layout_test
and terms_test (fast and full) were re-run.

## Judgement calls

1. **M1 wording.** A right answer starts with the name ("An imperfect cadence (US: half cadence): it stops on V…"). A wrong answer
   ends with "This is a perfect cadence." The panel headline already gives the answer, so this repeats the name once, in the
   sentence, where the US term can sit. Where a wrong-answer sentence already names the cadence ("a plain imperfect cadence"), nothing
   is added. With an interrupted cadence through a 6/4, the closing line follows the 6/4 sentence.
2. **M4** uses "E♭ minor", not lower case "e♭". It matches the Relative and Parallel rows in the same list, and it cannot be misread.
   The test accepts either form.
3. **M3** title reading is opt-in (`data-tt`), not done for every button title. The M3i check scans every button title for
   non-scoped terms. Bar and stave are scoped (no pairing after the first mention), so a hover that only mentions "one bar per chord"
   is left alone. No other button failed M3i.
4. **S5 scope.** "staff" counts only after a music word (the/a/treble/bass/grand…, not followed by room/members/meeting…) or before
   lines/notation/position. "measure" counts only as a counted noun. A US term in a code comment is allowed.

## Open

* **S3**: the key line "Perfect = US authentic · Imperfect = US half · Interrupted = US deceptive" is unchanged (pending Justin). The
  lint's "straight after US" allowance and the test's `.el-key2` exemption keep it passing. If Justin takes the IC's form, both can
  be tightened.
* **IC C1–C4** (Could) are not done, except that the rondo line avoids C2.
* There is no general check for a room whose chips name a term but whose prose never does (S4 was found by eye). The rondo is fixed
  by content, not by a new check.
