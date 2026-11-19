# 0.48 R6 fix round (branch `048-r6fix`, based on v0.48 `075e6c1`)

Fixes every finding in `tests/reports/checks/IC_R6.md`, applies Justin's answer 6 (19 Nov), and fixes the circle-of-fifths
neighbour spelling (Must). Nothing was pushed. Code commit: `c67a252`. All checks below are **self-checks** by the builder.
An independent check is still needed.

## Findings → change → test → result

| Finding | Change (index.html unless stated) | Test | Result |
|---|---|---|---|
| **H1** Gym cadence reader `#cad` treated as a button: no bracket in feedback; hovers pile up | `.cad` removed from `TM_BTN`. All the cadence cards are `<button>`s already, so only `#cad` changes, and it now brackets like feedback. Button and chip hovers are rebuilt from the element's **current** text on every pass (`termBtnSync`): no adding to `data-us`. The app's own title is kept (and picked up again if the app changes it). The observer also re-checks a button when nodes are only removed from it. | terms_test T6: the Gym reader fed I–IV–V–I, I–IV–I, I–V, I–IV–V–vi, V6–I and an empty progression must show the bracket and carry no US hover. Buttons whose text changes (term lost, term changed, app title changed) must get a rebuilt hover. On every scan, no hover may name a US term that the element's current text lacks. | pass (v0.48: fails, e.g. "Add two or more chords…" titled "US: authentic cadence, half cadence, deceptive cadence, imperfect authentic") |
| **H2** "12-bar (US: measure) blues", "8-bar (US: measure) phrase", "8- to 16-bar", hovers on "Twelve-bar blues" | The `bar` rx skips a bar straight after a hyphen (`(?<![-‑])`), so it never pairs "N-bar" compounds, on text or on hover. Plain "12 bars" and "Twelve bars" are still paired. | T6 targeted (the exact IC strings) + per-scan: no bracket after an N-bar compound, no `abbr` for a bar after a hyphen, no "measure" hover on "Twelve-bar blues" | pass (v0.48: fails) |
| **H3** "♭♭7" in the inversion caption and the guitar/bass fretboard dots | `degPretty()` in the inversion caption and both fretboard `dg` helpers. The same naive replace was also used for the Keys chord numerals, so that one uses `degPretty()` too. | spelling_test section G now scans every inversion on piano and the guitar, ukulele and bass views for every root spelling × quality (5,425 views, one page call per root) | pass (v0.48: fails, "the ♭♭7 is in the bass" (C dim7 inv 3), "♭♭7" on the C dim7 guitar diagram) |
| **M1** bare interval "tone" never paired | The `tone` rx also matches "a tone" when it is plainly an interval: followed by higher/lower/above/below/apart/up/down, by ")" or at the end of the text ("ii–Vs down a tone"). It does not match "chord tone", "tone colour", "common tone" or the Ear Lab's pitched "from rung 2 a tone, because…". Climb 9 "slips down a semitone (or a tone)" reworded to "a semitone or a tone" (it would otherwise nest). | T6 targeted (heading, the ♭VII card strings, false friends) + per-scan "every term is marked" | pass (v0.48: fails) |
| **M2** W/H step letters; "half–whole diminished" alone | Steps are now **T / S / T+S**. Legend: "T = tone (US: whole step, W) · S = semitone (US: half step, H)". Octatonic: chip subtitle "semitone–tone diminished" with the hover "US: half–whole diminished"; the scale's name line reads "semitone–tone diminished (US: half–whole diminished)". | spelling_test K expects T/S (612 scales); T6 per-scan: no W/H step letter, no W/H legend, no "half–whole" on its own | pass (v0.48: fails) |
| **M3** "crotchet rest" paired with "quarter note"; singular hovers on "2 quavers" | The note-value rx include an optional " rest(s)". `termUSw()` gives "quarter rest(s)" for a rest and keeps plurals, on buttons and in prose. | T6: rest and plural button hovers; every marked term's hover has the right form | pass (v0.48: fails) |
| **M4** a bracket on every line of a checker list | `TM_LIST = '.c2iss,.checker,.fchk'` makes each issue list one block, so the first mention in the list gets the bracket and the rest get the hover. Counterpoint messages are not edited. | T6: at most one bracket per term per list (targeted and per scan) | pass (v0.48: fails, 4 instead of 2) |
| **Answer 6** bar/stave both terms only in headings and at the first mention in each room | Already the scoped rule. Confirmed: "Bar 7, beat 3", "Bars 6–7", "from bar 14" after the first mention carry the hover only. No per-list bracket for bar/stave (IC condition 3 not taken, per answer 6). | T6: locators in a feedback box carry no bracket but are still marked; per scan, a bar/stave bracket outside headings appears at most once per room | pass |
| **L1** back-to-back and nested brackets | The pass now picks one of three forms. Normal: " (US: x)". When the term is followed by its own bracket (also when the term ends a `<b>`), the US term goes inside that bracket: "Perfect cadence (US: authentic cadence; V–I)", "an imperfect cadence (US: half cadence; the question)". When the term is already inside an open bracket: square brackets, "(an imperfect cadence [US: half cadence] in minor, iv⁶–V)". A hand-written "(US: …)" after a `<b>` term is now recognised as the bracket, which also fixes a doubled "(US: imperfect authentic) (US: imperfect authentic)" in the Forms phrase intro. Voices: "Span: 7 semitones (US: half steps), 0.6 octaves". | T6 targeted (merge, square) + per scan: no "(US: …) (" and no round US bracket inside an open bracket of its block | pass |
| **L2** "bar (US: measure) by bar" | The `bar` rx skips "bar by bar" (and "bar-by-bar"). | T6 targeted + per scan | pass |
| **L3** "a Perfect cadence, less final" mid-sentence | `TERM_IAC_LC` is used in the Gym reader and in `cadWord()` (report, chips, journal). | T6 per scan: no capital mid-sentence | pass |
| **L4** "= US authentic cadence" | The "In the US" row reads "perfect cadence = authentic cadence". | T6 per scan: no "= US" | pass |
| **L5** IAC hover and journal line without the note | A button or chip hover naming "imperfect authentic" appends the note. The journal line (`anReportText`) appends the note when it names the less-final cadence. | T6: chip hover carries the note; per scan, every such hover carries it | pass |
| **L6** circle: D♭ major IV as F♯, B♭ minor iv as d♯ | Neighbour keys are spelled from the key signature (n+1 / n−1 accidentals), not from the wheel labels. The whole circle was checked: **two more** were wrong. F♯ major's V showed D♭ (now **C♯**) and D♯ minor's v showed B♭ (now **A♯**). Relative and parallel keys were already right (they share the index or the tonic). | spelling_test C: each neighbour must equal music21's P5 / P4 transposition exactly, with a signature one accidental away (48 checks) | pass (v0.48: 4 failures, the four above) |
| **L7** dotted underline under already-bracketed terms | `abbr.tm.tmb{text-decoration:none}`. The pass sets `tmb` when the bracket shows. | T6 targeted + per scan | pass |

## Pre-fix demonstration (v0.48 `075e6c1`, the new tests copied into an exported tree)

* `TERMS_FAST=1 terms_test`: **223 failures**. Every targeted T6 case fails except the two answer-6 locator checks, which v0.48 already met. Examples: the Gym reader I–V titled "US: authentic cadence, half cadence"; "12-bar (US: measure) blues"; the "crotchet rest" hover "US: quarter note"; a hover "own · US: half note, whole note" piled up.
* spelling_test (Keys section and the new Chords-room scan; the full suite's renderer was OOM-killed on the export while other agents' browsers were running): 612 step-letter failures (W/H), 4 circle failures, 2 "♭♭7" failures.

## Suites on the final tree (self-checks)

| Suite | Result |
|---|---|
| content_lint | pass (all sections, 56 song entries) |
| unit_test | pass, 637 checks, 0 failures |
| spelling_test | pass, 49,104 checks, 0 failures, no known failures. Includes 5,425 Chords-room views (inversions; guitar, ukulele, bass) and 17,433 distinct rendered strings scanned. |
| terms_test (full: Stages 4, 5, 6) | pass, 0 failures: 153 views, 2,345 clicks, 2,505 scans, 25 targeted T6 checks |
| terms_test `TERMS_FAST=1` | pass, 0 failures (about 40 s). Re-run after the last test edit, which puts the N-bar fragment in its own room so v0.48 fails it; the full run above used the earlier fragment. |
| earlab_items_test | pass, 0 failures |
| layout_test | pass, 162 views, 0 findings, 0 page errors |

Crashes and retries: spelling_test crashed twice with "Target crashed". The kernel log shows a memory-cgroup OOM kill of Chrome while another agent's earlab_items_test (about 1 GB) was running. The first crash was in my own new Chords-room loop, so I split that loop into one page call per root. The second was in the existing Climbs sweep. The third run passed. terms_test did not crash: one full run and seven fast runs, no retries. The first full run had 1 failure, a false positive of the new nested-bracket check (it read across blocks); the check is now per block. The full re-run passed.

## Judgement calls

1. **Nested and back-to-back brackets are solved in the pass, not by editing every source string** (scores/meta.json alone has 16 "Perfect cadence (V–I)"). The US term goes inside a following bracket "(US: x; V–I)", and square brackets are used inside an open bracket. The square bracket is a new visual form; say if you prefer a comma form.
2. **Bare "tone"** is paired only in clear interval contexts ("a tone" + higher/lower/above/below/apart/up/down, ")" or the end of the text). "a tone," is left alone because of the Ear Lab's pitched "a tone, because a clap can't…". Mentions like "a tone." would also stay unpaired.
3. **"N-bar" compounds** are skipped after any hyphen, so "end-of-bar" or "multi-bar" would also stay unpaired (the same in both).
4. **Rest pairing**: "crotchet rest" = "quarter rest" through the same term entry (rx + `termUSw`). T1's term list is unchanged.
5. **Octatonic**: "semitone–tone diminished" with "(US: half–whole diminished)". The chip shows the hover only.
6. **Step legend** keeps the US letters in the bracket ("US: whole step, W") so students who meet W/H elsewhere can map them.
7. **IAC hover** carries the whole one-line note after the US term (long, but it is the rule "wherever both appear").
8. **earlab_items_test** (another agent's area, one line): it lacked `import re`, which crashed the phrygian check on v0.48 too. I added the import, and the regex now also accepts the square nested bracket.

## Not fixed / open

* **Decision (b) key line** under term-bearing answer groups: the Ear Lab key line is the other agent's (card rebuild). The **Forms phrase-builder** cadence chips have no key line yet; not listed in my tasks, so left for the main session.
* **Content lint for a US term used alone** (L63): still left to the main session after merging, as in R6. terms_test T2 covers it at runtime.
* **Found in passing (not R6)**: the Chords-room song source link for "The Girl from Ipanema" renders its source note inside the URL. The `href` includes " (Real Book chart in F; …)" and the link text is cut at "(Real Book ". This is a source-rendering bug, out of scope.
* The footer still reads "preview 0.47" (noted by IC, a release task).
