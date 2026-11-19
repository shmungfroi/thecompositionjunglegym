# Ear Lab merge, register 0.48: 048-elengine into 048-elmerge (v0.48 + 048-elitems)

`git merge 048-elengine` on `048-elmerge`. 11 conflict blocks in `index.html` (Ear Lab, about lines 6160–6710) and 1 in `tests/earlab_test.py`.
Both builders' reports were read first (`EL_items_report.md`, `EL_engine_report.md`), with Fable's `design/earlab_048/SPEC.md` (read only).

## Resolutions

### One Stage table (EARSTAGE, Fable's SPEC section 3)

The items branch's `ERUNG` table and its range-based filter are gone. The engine branch's `EARSTAGE` is the only table:

| drill | rung 1 | rung 2 | rung 3 | tag |
|---|---|---|---|---|
| Pulse and metre | 4 | 4 | 5 | Stage 4–5 |
| Rhythm dictation | 4 | 4 | 5 | Stage 4–5 |
| Chord quality | 4 | 5 | 6 | Stage 4–6 |
| Cadences | 5 | 5 | 6 | Stage 5–6 |
| Bass and numerals | 5 | 5 | 6 | Stage 5–6 |
| Melodic dictation | 4 | 5 | 6 | Stage 4–6 |
| Blind analysis | 5 | 5 | 6 | Stage 5–6 |

Differences resolved in favour of the SPEC:
1. **Metre rung 3:** items had Stage 4, SPEC has Stage 5. Now Stage 5, and the metre tag is "Stage 4–5". `EDR`'s metre range now reads `4–5` too.
2. **What a Stage offers:** items offered a drill only while the Stage was inside its range, so Stage 5 hid metre and Stage 6 hid metre and
   rhythm. SPEC: a drill or rung shows when its Stage ≤ the selected Stage. Stage 6 now offers all seven drills and all rungs, and Stage 5
   offers metre and rhythm (all rungs).
3. **Nothing hidden means no "Show all" chip:** at Stage 6 nothing is hidden, so the chip does not appear (unless Show all is already on).
4. **Saved rung above the Stage:** items moved `earLvl()` to the first shown rung. SPEC says never strand a student: the chosen rung is now
   kept and shown even when it is above the Stage. The items rule "a drill outside the Stage offers all its rungs" is kept (it matches the
   SPEC's "treat EAR.all as on").
5. **Stage tags:** written out from `EARSTAGE` ("· Stage 4–5"), not the engine's short "S4–5". Rung tooltips run from the rung's Stage to the
   drill's top Stage (metre rung 3 "Stage 5", cadence rung 3 "Stage 6").
6. **One "Show all" control:** the items chip (`data-earall`, toggles; reads "Show Stage n only" when on), wired to `EAR.all`. The engine's
   separate "show all" mini button is removed. Changing the Stage clears `EAR.all` (engine code, SPEC).
7. Engine helpers kept as thin wrappers over the one table, for the UI builder: `earDrillShown`, `earRungShown`, `earStageTag`; plus `earHidden()`.

### Rung-3 cadence generation

* Items branch's R4 generator: six answers, mode drawn first, five-chord models opening I–IV / i–iv, `opts`, `CADL3`, `CADFAM`, `CADPARENT`, `sub` empty at rung 3.
  The engine's rung-3 pool (rung 2 models plus `CAD3`) is dropped.
* `earGenCad` ends `const{reg,P}=earCadReg(rns,key,r,l);`. `earCadReg` is now the only register path:
  * rung 1: the items branch's `earSATBPair` path (open spacing, no warnings). Its draw (lowest, highest, first bass, last soprano) is used on
    a 3 × 3 grid around the drawn lowest/highest targets, and the realisation nearest the targets is kept (the engine's method). Without this,
    the engine's new combined tell "lowest and highest note (6-semitone bands)" failed at rung 1 (32% vs 26% chance).
  * rungs 2–3: the engine's 3 × 3 grid. Rung 3 uses the wider range the items branch needed for the minor-only Phrygian (targets bass 41–53,
    soprano 64–76; grid 41/47/53 × 64/70/76).
* **Held out:** the two interrupted-after-cadential-6/4 models stay out. They are now written in R4's rung-3 shape: `I IV I:2 V vi` and
  `i iv i:2 V VI` (the engine's minor form `i VI i:2 V VI` does not open i–iv). One switch: `CAD3_HOLD=true`; set false to append them to the
  interrupted models (they would then need fixture rows and the one-right-answer rule relaxed).

### Stats

The items model `{n, ok, streak, best, shown, skipped}` (`EARST0`, `earStatNext`), plus "Nearly" from the engine branch, OFF by default:
* `EAR_NEARLY=false`. `earJudge(q, given)` returns `'nearly'` only when it is on, at cadences, and the given answer is the family of a Phrygian
  or cadential 6/4 answer (`CADPARENT`). The engine's reverse mapping (Phrygian given for an imperfect answer) was dropped; SPEC names one direction only.
* `earStatNext(s,'nearly')` keeps the streak, leaves `n` alone and adds a `nearly` field only when it happens, so the six-field record is
  unchanged while Nearly is off. The result banner reads "Nearly." (class `near`) and the stats/journal lines show "nearly n" when non-zero.
* With Nearly off, family answers are marked wrong with the items branch's family sentence (unchanged).

### Transport

* `elPlay`/`elStop` is the only path that sounds. Every items-branch handler now uses it: drill and rung change, Check, Show me, Stop and
  `earNew` call `elStop`; ladder taps use `elPlay(q,'tap',…)`. Items behaviours kept: skip recording and toasts, undo/redo locked after
  marking, inline Reset with Undo, Clear guarded after marking.
* `earGen` tags items with both `q.l` (items) and `q.lvl` (engine).
* **Test fix:** earlab_items_test section K read rung-1 playback order by stubbing `c2Tone`. The transport plays chords on the sampled piano via
  `tone()`, so it now preloads the piano, stubs `tone`, and calls `elPlay` (and checks the state is `playing`).

### Other merged copy

`EARHOW`: items text for chord quality and cadences; the engine's rhythm text with "level" changed to "rung". Start shows "Loading…" until
the piano (and scores) are ready; rhythm Pulse and Speed controls kept.

### Tests combined

* `tests/earlab_test.py` section C: both branches' checks. Second-chord and opening-voicing tells run at rungs 2–3 (items: at rung 1 those
  chords are the cadence); mode, mode + length, combined register bands, refined-answer checks and the held-out check (engine) run at every
  rung. Rung 3 now has refined answers, so the refined-answer check is a hard failure (it passes). New: a merge check that `earGenCad` goes
  through `earCadReg`, Nearly is off and the hold switch is on.
* `tests/earlab_items_test.py`: section K playback via `elPlay` (above); section U uses the SPEC Stage table and expects no Show all chip at Stage 6.

## Suite results (merge commit)

| Suite | Result | Counts |
|---|---|---|
| earlab_test | 3 failures, all the known Analysis relabelling ones (`jesu cadence 5`, `ohaupt cadence 2`, `jesu cadence 4`); nothing else | 31 tell checks; 2,940 cadence realisations; fixture rows 573, coverage 573 of 573; rung 3 refined answers: mode 18% vs 19% chance, length 19% vs 19%, mode + length 18% vs 19% |
| earlab_r2_test | pass | 1,666 checks, 0 failed |
| earlab_items_test | pass | 0 failures; 27 tell checks; 12,000 rung-3 items, 1,200 realisations; distinct per button: perfect 113, plagal 227, imperfect 217, interrupted 206, Phrygian 122, cad 6/4 218; rung 1 2,000 items, 19,440 realisations; 9 stats unit cases, 12 flow checks; 3 Stages, 18 drill × Stage renders |
| transport_test | pass | Ear Lab 42 items, 114 state checks, 21 natural ends, 42 double taps, 42 play-while-playing, 30 variants, 256 stop events, end diff 0 ms; 0 fails, no page errors |
| sound_test | pass | 0 failures |
| unit_test | pass | 637 checks |
| content_lint | pass | |
| pageerrors_test | pass | 153 views, 4,222 clicks, 881 random clicks, 0 errors |

Note: rung-3 distinct items per button fell from 150–298 (items branch) to 113–227 with the `earCadReg` grid; all are above the 100 floor.
