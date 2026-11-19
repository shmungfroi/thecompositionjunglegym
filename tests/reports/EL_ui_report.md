# Ear Lab 0.48 card: UI report (branch 048-elui)

All checks below are the builder's own self-checks. Fable reviews the built card against the mock-ups afterwards (screenshots: `design/earlab_048/built/png/`, 1440, 1366, 1024 and 390, from `design/earlab_048/built/shots.py`; every state loads with no page error and no sideways scroll at 390).

Starting point: `git merge v0.48` into 048-elui was clean (no conflicts; R6 term helpers, rung-3 Australian names and the earlab_items fixtures came across unchanged). The first commit (51cf3cf) already held most of the card; this pass closed the gaps, rewired the tests to the new card, and added `tests/earlab_ui_test.py`.

## Spec item -> what was built -> test -> result

| Item | Built | Test | Result |
|---|---|---|---|
| EL-1 / EL-2 toggle, ring, dock | One `.el-play` toggle with real-duration ring, state text, variants, phone dock, `body.ear-sounding`. This pass: variants now precede Show me / Skip in the DOM (grid places them), so keyboard order is drill tabs, rungs, toggle, variants, Show me, Skip, answers. Ring keeps running under `prefers-reduced-motion` (global reduce rule overridden for `.arc`); spin, tally fade and dock slide stay off. | earlab_ui F, transport_test | pass |
| EL-3 metre grid | Grid with rows Simple, Compound, Irregular (rung 3). Rung 3 shows 2/4 and 12/8 (Justin 3); generator pool equals the grid cells. Beat lane now switches to two bars a row from 6 units, so its numbers are never scaled below 11 px at 390. | earlab_ui B, earlab_items | pass |
| EL-5 rhythm | One-line SVG stave, stick notation at rung 1, count-in ruler, sound strip, tiles. **RHYNAMES** (one table, tile-keyed) names every tile at every rung (Justin 4b); tile height 76 px holds the name. Names for rungs 2-3 are placeholders, marked `PENDING JUSTIN` in a code comment beside the table. | earlab_ui C | pass |
| EL-8 feedback | Result panel, teaching sentences, chord row, replays, option marks (as first commit). | earlab_test, earlab_items, earlab_r2 | pass |
| "Nearly" | Gold panel, wave mark, "NEARLY", gold `≈ YOUR ANSWER` on the chosen button, streak kept. Foot reads "15 answered · 2 nearly · 2 shown · 1 skipped" (per coordinator note; Nearly is not in "answered"). EAR_NEARLY untouched (false here). | earlab_ui G forces the flag on and restores it | pass |
| EL-9 accessibility | Focus ring 2 px goldhi on every control reached by Tab; aria-pressed/labels on toggle, rungs, segments; tally `role=status` with spoken label; Esc and Space stop (also with the toggle focused, no restart); nothing under 11 px (this pass: the stacked 6/4 figures were 10.5 px, now `max(11px,.7em)`); targets >= 44 px at 390. | earlab_ui A and F | pass |
| EL-10/11 | Drill strip, Stage tags ("Stage 4-5" for metre), rungs, show all, Reset with inline confirm and Undo. | earlab_items | pass |
| EL-13 | Fixed option grids; bass chips; "Rung" only for drill levels, hand-sign rows are "notes". | earlab_items, earlab_ui | pass |
| R5 | One `.el-tally` (score, of n, streak, best) in the Ear Lab, Keys "Hear it, name it" and "Sing it back"; old inline score text gone. | earlab_ui G | pass |
| Justin 5 | Phone ladder rows 44 px, set by one variable `--lad-row` in `:root` (rows span two tracks, CSS halves it). | earlab_ui E (also changes it to 52 px and checks the rows follow) | pass |
| Justin 7 | Key line under the cadence and blind-analysis answer buttons: "Perfect = US authentic · Imperfect = US half · Interrupted = US deceptive · Plagal is the same in both", 12.5 px muted, built from `termUS()` (shared list) by `elCadKeyHTML`; button `title`s come from the same list. Only names on offer appear. | earlab_ui D | pass |

## Pass counts (final run, this worktree)

| Suite | Result |
|---|---|
| layout_test | 162 views, 0 findings, no page errors |
| pageerrors_test | 153 views, 0 errors |
| score_measure_test | 294 scores, 0 findings |
| transport_test | 42 items, 112 state checks, 0 fails |
| earlab_test | 0 failures |
| earlab_r2_test | 1666 checks, 0 failed |
| earlab_items_test | 0 failures |
| terms_test | 0 failures |
| earlab_ui_test (new) | 367 checks, 0 failed |

Retries: the first runs of pageerrors, transport (a one-off "state end vs last node stop" mismatch at 390 px rhythm rung 1, not reproduced on re-run) and terms failed or were killed while other agents had browsers open and while the harness was broken; each was re-run alone and passed. terms_test failed once for a real reason (below) and passed after the change.

## Fixes made along the way

- `renderEar` drops a question that belongs to another drill (a drill changed from a link or a test), which was throwing in `keyName` and `earDo`.
- Tests moved to the new card: `[data-earnew]` falls back to the Play toggle when no question is open; `[data-earstop]` is the toggle; `.earres`, `.earstat`, `.eartabs` became `.el-result`, `.el-foot`, `.el-drill`; wording expectations follow the teaching sentences; skip tests set `plays=1` (a question is skipped only once played, per spec section 4); `earTips()` no longer exists so earlab_test reads `ELTIPS` and `ELTIPNOTE`. earlab_items_test lacked `import re` (already so in v0.48); added.

## Deviations and why

1. terms_test T2 now skips `.el-key2`. The rule "no US term on its own" would otherwise flag Justin's literal key line "Perfect = US authentic".
2. Nearly is not counted in "answered" (engine and coordinator note) although spec section 4's table says n +1. Followed the coordinator and Justin's "not scored".
3. The key line adds "Plagal is the same in both" (Justin 7, "plus Plagal is the same in both"). Say if that should go.
4. A new suite (`earlab_ui_test`) was added to `run_all`.

## Gaps and open items

- RHYNAMES rung 2-3 names are placeholders (tika-tika, sa, tam-ti, ti-tika, tika-ti, syn-co-pa). `tim-ka` and `ta-a-a-a` from the brief have no cell yet, so they are not in the table.
- Phone ladder is 44 px rows (about 400 px tall at rung 2-3) pending Justin's view of the alternative.
- Not verified on a real phone: the dock position over the tab bar and iOS safe-area (checked only in headless Chrome at 390 x 844).
- The built screenshots set up states through the real app; the Nearly state sets EAR_NEARLY for the one render only.
