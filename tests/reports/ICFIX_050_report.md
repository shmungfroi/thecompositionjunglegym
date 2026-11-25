# ICFIX 0.50: fixes for IC_050_B0 (Batch 0, engine and data)

Opus engine/data agent, clone `/home/claude/opusfix`, branch `050-icfix` from `050-levels` at `f08f1cc` (V1/V2/V8/V9/V11/V12 + V3-V7 UI + V10 picker, merged). Single file `index.html`, edited with Python scripts that assert exact match counts. Nothing pushed.

**Every check below is a self-check by the agent that made the fixes. None is an independent review.**

## Findings: what happened to each

| IC id | Result | What was done |
|---|---|---|
| V1-1 | **Fixed** | `It+6`, `Fr+6`, `Ger+6` are `l:6, stp:20` (table 1). The forced jumps (`lvlSet(Q.find(...).l)`) had already been removed by the UI build. New `lvClamp`: every write through `lvlSet` / `lvlChange` is a whole number 1-7, or is ignored if it is not a number. New `lvLoad`: a stored `cjg_level` that is a number is clamped into 1-7 and rewritten (so 9 becomes 7, 3.5 becomes 4); the old `cjg_stage` is converted only when `cjg_level` is absent, empty or not a number. A learner who chose Level 6 can no longer come back at Level 2. The augmented sixths stay out of the Chord Library list (they have no `QSHORT` entry, as before). |
| V1-2 | **Fixed** | Climb 2 runs on levels: floor 3 (`Math.max(S.level,3)`), Level 3 first species above the cantus; 4 second and third, above or below; 5 fourth and fifth; 6 three voices. Modes per table 2: Dorian, Aeolian, Ionian, Mixolydian at 3; Lydian and Phrygian at 4 (they were 4 / 5 / 5). `c2Settable`, the position chips, the tier line (`c2Tier`) and the Make text all use the same thresholds. Nothing the UI build un-hid is hidden again: the mode and species lists still show every item in its band; only what the climb teaches inside (position, the "can be set" table, the wording) is gated. |
| V1-3 | **Fixed** (approved stand-in, 25 Nov) | Aeolian `l:1`, Ionian 1, Dorian and Mixolydian 3, Lydian and Phrygian 4, Locrian 5. The climb opens on Ionian at Levels 1-2 and Dorian from 3 (`c1DefMode`); a mode the learner picks stays (`C1.pick`). The quiz at Levels 1-2 asks Ionian or Aeolian. |
| V1-4 | **Fixed** | `colourRomans` reads a table (`COLR`) of chord and level: borrowed iv and ♭VII at 3, ♭VI at 4; V/V and V/vi at 4, V/IV and V/ii at 5 (climbs 7 and 8). To keep migrated learners whole: ♭III and the minor-key Picardy I sit with ♭VI at 4 (old Stage 5 had them), V/iii and vii°7 at 5 (old Stage 6 had every secondary dominant); ♭II (Neapolitan) at 6. Minor-key IV at 3. `deck()` takes sevenths from Level 3, where the switch shows, so the switch works wherever it shows. The Oracle colour switch shows whenever the level has a colour chord (Level 3 up). |
| V1-5 | **Fixed** | `c11Opts` uses `lvAt(C11VOCSET)`, so Level 1 gets the Level 2 set. The three vocabulary sets now carry level and step (`C11VOCSET`, table 5). |
| V1-6 | **Already closed by the UI build** | The global `[data-l]` click branch is gone. Unit check added: a click on an element with `data-l="the cadence"` leaves the level and storage unchanged. `lvClamp` would also reject the value. |
| V1-7 | Already closed by the UI build | `content_lint` stage_wording passes (after the fix below). |
| V1-8 | Already closed by the UI build (V5 area names) | not touched |
| V1-9 | **Fixed** | 3.5 is rounded to 4 by `lvClamp` on load and on write. |
| V1-10 | Not fixed (Could) | `LADSTG`'s fallback is never used (EARSTAGE is always defined first). Left. |
| V2-1 | **Fixed** | `ANLV` replaced with table 7: Chopin No. 7 3, K. 331 theme 3, K. 331 Var. III 3, BWV 269 4, Jesu 5, Befiehl 5, K. 545 5, The Entertainer 5, Maple Leaf Rag 5, Chopin No. 20 5; steps 1-10 in the table's order. Chopin No. 20's chromatic chords are labelled Level 6 (`ANCHROM`): each colour-function numeral in the chord layer carries `data-lv="6"` and an SVG title "Level 6: chromatic chord", and a note under the score says so. The three layer switches carry levels (`ANLAY`: form 1, cadences 1, chord on every beat 3); a layer above the learner's level can still be switched on and shows the dashed level mark (`lvm ahead`) on its switch. Sonnet's provisional pairs are gone. |
| V2-2 | **Fixed** | as V1-1 |
| V2-3 | **Fixed** | Forms per table 6: phrase and period **1** (was 2), 12-bar blues 2, rondo 3, theme and variations 3, jazz and minor blues 4, rag and sonata 5, rhythm changes, sonata-rondo and fugue 6. Steps 1-11 in the table's order. |
| V2-4 | **Fixed** (approved 25 Nov) | `stp` added in each table's listed order within the level (data order where the table does not list the items): C1M, C2M, C2SP, C4EX, C5FAM, C6EX, C6Q, C7EX, C8EX, C8Q, C9EX, C10EX, C11V, C11TOOLS, C11VOCSET, C12MODES, C12SHAPES, VTYPES (table 9 order), FORMS, Analysis. Ear Lab: N/A. No property named `s` was added anywhere (checked on the diff; interval semitones unchanged). Not given steps: the swap alternatives inside climb 8 (`C8SW`), which are choices inside one chord slot, not list items. |
| V2-5 | Decided by Justin (25 Nov) | see V1-3 |
| V2-6 | Already closed by the UI build | voicing types are banded by level |
| V2-7 | Not fixed | Climb 12's Chromatic mediants and Static harmony tabs still show from Level 5. Not in this brief; with "nothing is hidden" they would stay reachable anyway, perhaps with a level mark. Needs a decision. |
| V8-1 | **Fixed** | `LADKEYS[5..7]` has 12 keys (do on F♯ added). |
| V8-2 | Not fixed | Bass and numerals `BKEYS` (listening drill, 10 keys) is unchanged; listening drills keep their keys (0.49 C3). |
| V8-3 | Not fixed (Could) | `earGenMel` is unused; left. |
| V9-1 | **Fixed** (approved 25 Nov) | Melody internal rung 5 keeps its la-pentatonic items at place 6 (Level 2). A new internal rung 13, appended at the end of the internal list, runs rung 5's own generator with the natural-minor variant at place 7 (Level 3, key band 3). Review items are the rung's existing major items. |
| V9-2 | **Fixed** (approved 25 Nov) | Cadences internal rung 2 keeps its major-key items at place 5. A new internal rung 4, appended, runs rung 2's generator in minor keys only at place 7 (12 minor keys, the same balanced weights). |
| V9-3 | Not fixed | Blind analysis contents and scores need Justin's decision. |
| V9-4 | **Already closed by V10** | the picker draws "not yet" cells for every empty place; `rungs_picker_test` checks every one (labels and text) |
| V9-5 | **Fixed** | Ear Lab help and tip text now give displayed places and levels through `rn()` and `EARSTAGE`: "clapped at rung 2, on one note from rung 4"; "At rung 4 ... at rungs 5, 7 (in minor keys) and 13"; "Rung 13 (Level 5) adds ..."; melody "at rung 2", "from rung 6"; chord quality "the 7th (rung 13)". The stale `EAR.all` / Stage comment above `earRungs` is rewritten. |
| V9-6, V9-7 | Notes for Justin | unchanged |
| V11-1 | **Fixed** (table 9 split) | `double` split: basic doubling 3 (`double`), doubling in inversions 4 (`dblinv`), doubled 7th and doubled leading note 5 (`dbl7`, `dbllt`, also the leading note of a secondary dominant), doubling in augmented 6ths and the Neapolitan 6 (`dblchrom`). The checker today finds only the three level-5 doublings; `double`, `dblinv` and `dblchrom` have levels ready but no checker rule yet (V11-4). |
| V11-2 | **Fixed** (approved 25 Nov) | A finding above the learner's level still counts as an error or warning, but its text is now the short form "*name* (*voices*): comes at Level n." The full explanation is kept in `.full`. |
| V11-3 | Not changed | Builder-assigned levels for the rules table 9 does not name need Justin's tick. |
| V11-4 | Not fixed (Could) | see V11-1 |
| V12-1 | **Fixed** | Climb 9 opens on shells below Level 5 and on rootless voicings from 5 (`c9VtDef`); a voicing the learner picks stays. The rootless chip says "· Level 5" below Level 5; nothing is hidden. |

Also fixed: the `curHint` fallback line added in the V10 merge was dead code (the real `curHint` is a hoisted function declaration) and its "Stage" strings failed `content_lint` stage_wording on `f08f1cc` itself (checked in a worktree). Removed.

### Saved progress and the split rungs (brief item 12)

Rule chosen: **append, no renumbering, no migration map.** `EARSLOT.mel` is `[2,3,4,5,6,9,10,12,13,15,16,18,7]` and `EARSLOT.cad` is `[4,5,13,7]`. Every saved internal number (`cjg_ear` lvl, rd, reached) still names the same rung at the same place; internal 5 and 2 now hold only half of their old content. Because `EARSLOT` is no longer in place order, the place-order code moved to `earByPlace` / `earNextRung`: first visit (`earFirstRung`), the readiness suggestion (`ladRdState`), and the card tag (min and max place). A generated item keeps its content rung in `.l` (all the marking and desk code keys on it) and carries the rung asked for in `.rung`; `earLvl()` reads `.rung`, and `renderEar` hands the content rung to the ask, stage and answer areas (`earBase`, `ELSPLIT`).

Item counts (self-checks): melody 5 and 13: 4,711 and 4,706 distinct items in 5,000 seeded draws, new-thing share 0.673 and 0.682, all tells pass (`earlab_test`). Cadences 2 and 4: 843 and 819 distinct items in 1,500 draws (smoke run), each answer about a quarter; 300-draw unit check ≥ 100 each; every cadence tell that runs at rung 2 also runs at rung 4 and passes.

## Commits (branch `050-icfix`)

- `e54dcc6` 0.50 ICfix: level engine, aug 6ths, colour chords / Oracle, climbs 1, 2, 9, 11, 12 dictation keys
- `b5468f3` 0.50 ICfix: SATB coach doubling split; short note above the level
- `67b2a57` 0.50 ICfix: Analysis and form tags, steps for tables 5-9
- `b373c1e` 0.50 ICfix: Ear Lab splits, order by place, help text
- `a8bc24e` 0.50 ICfix: tests; dead curHint fallback removed
- this report and the regenerated `tests/reports/rungs_050/` screenshots (the picker now shows cadences 4, 5, 7, 13 and melody place 7)

## Tests (self-checks, one headless Chrome at a time)

| Test | Result |
|---|---|
| `content_lint.py` | pass (all sections 0 failures; stage_wording 0, was 7 on `f08f1cc`) |
| `unit_test.py` | **1,229 checks, 0 failures** (1,164 before + 65 new ICfix checks: lvClamp, lvlSet, the data-l click, 8 load cases incl. stored 9 with an old stage, aug 6ths, colour chords per level incl. migrated Stage 5 and 6 learners, Oracle sevenths and switches, climb 1 modes and quiz per level, climb 2 tier / species / position per level, climb 11 at Level 1 = Level 2 set, climb 9 opening voicing, 12 keys, SATB doubled leading note at Levels 3 and 5, Analysis tags and layer marks, forms, split rung contents / places / levels / distinct items / saved numbers / next by place, help text, a level and a rising step in 24 tagged sets, interval semitones) |
| `ordering_test.py` | 147 list checks, 0 failures, 0 page errors |
| `spelling_test.py` | 168,895 checks, 0 failures |
| `chordshape_test.py` | 0 failures (54,129 counted checks). Test changed: it took the library list as `Q.filter(l<=6)`, which now includes the augmented sixths; it reads `qualItems()`, the app's own list, instead. |
| `counterpoint_test.py` | 0 failures, 40 of 40 regression cases |
| `earlab_test.py` | 0 failures (104 tell checks; melody rung 13 and cadences rung 4 included). Test changes: expected EARSLOT / rungs lists add the appended rungs; M9 keys expect 12 (table 2); cadence generation and every rung-2 tell also run at rung 4; melody loops add 13. |
| `earlab_items_test.py` | 0 failures. Test changes: it clicked the old `#lvl` buttons (hidden since V4; it timed out on `f08f1cc` too), now the real level control; rung counts cad 4, mel 13, listed in place order. |
| `ladder_ui_test.py` | 242 checks, 0 failures. One expectation changed: after melody place 6 the suggestion is now place 7 (natural minor, Level 3), not place 9. |
| `rungs_picker_test.py` | 3,753 checks, 0 failures. Test changes: slots in internal order with the appended rungs, place order for first visit and the suggestion walk, sub-labels "4 rungs" / "13 rungs", tag "13 written". "Not yet" cells checked at every empty place (closes V9-4). |
| `pageerrors_test.py` | see below |

`pageerrors_test.py`: **357 views, 10,142 clicks, 0 page errors; P2-5 audit sequence clean, 881 of 881 random climb 2 ladder clicks, 0 errors** (exit 0). The first run ended its random climb 2 walk at click 300 (no errors, but the test wants 881): with the re-tagged chip order the seeded walk picked Three voices, whose page has no two-voice ladder cells. On `f08f1cc` the same walk (run in a worktree) never picked it and reached 881. The walk now skips the Three voices chip; the run took about 25 minutes in the background, alone.

## Not checked

- How the new Analysis level marks and the Chopin No. 20 "Level 6" titles look on the page (checked by data and unit check only, no screenshot).
- Sound.
- The climb 2 three-voice pages beyond page errors.
