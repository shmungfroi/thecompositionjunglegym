# C6 UI, 0.49 (Sonnet implementer): self-check report

Branch `049-c6` (worktree `/home/claude/wt/c6`, from `049` at c49222f). Not pushed, not merged. Approved by Justin 21 Nov 2026 (L101). All checks below are self-check; Fable verifies from the PNGs.

## Changes (all in index.html unless named)
1. **C6 / D1(a).** Tokens in the first `:root` (the one `cvd_sim.py` reads): T `#9dc995`, D `#d15e5d`, MD `#b1729d`, MD-on-ivory `#8b4978`; PD and C unchanged. `fn049.css` lifted verbatim at the end of the main style block, except its `:root{...}` override line, which is replaced by a comment (the values live once, in the first `:root`).
   - Letter cue (`data-fn` via new `FNL()`): bar grids in climbs 4, 5, 6, 7, 8 (two grids), 9, 10, 11 and the modal vamp (9 and 10 map chord kind to T/PD/D); Analysis numeral strip; circle-of-fifths nodes (climb 5 wheel, `<text class="f">`, filled in the function colour); Ear Lab chord chips (both result chip builders; outside-the-key reads C).
   - `.fnkey` legend (`FNKEY`) once under each bar grid / the numeral strip, and under the Ear Lab chord row (cadence and bass/blind results). The Analysis "Functions" row lost its now-duplicate "(T tonic, PD predominant ...)" note.
   - `ELFN` already carried MD (C9 landed); the chips use `earNumFn`, so Ear Lab and Analysis agree.
2. **D2(a) / C17.** `--red` / `--green` stay shared. I also lifted every hard-coded copy of the same colours so there is one red and one green: `#c8473b`, `#8fbf6a`, `#bd6b97`, `#9e4776` and their `rgba()` washes (FNHEX, COLS, earMelMount RED, `.gans .chip.wrong`, `.el-opt.is-mine`, score strokes, etc.). No other colour or layout change.
3. **cvd_sim in run_all.** `tests/run_all` runs `reports/fable_049/cvd_sim.py --check` as suite `cvd_sim`. The script already reads the tokens from index.html, so no change to it.
4. **C13.** Rhythm-tile hovers carry the count on both sides: "2 quavers (US: 2 eighth notes)", "quaver, 2 semiquavers (US: eighth note, 2 sixteenth notes)".
5. **C14.** Hovers read "Australian (US: American)" (`termBtnSync`). A hover with no app title of its own is unchanged ("US: quarter note": the Australian word is the visible label or hovered word). The L5 note is still joined with " · " after the bracket.
6. **C15.** `.piano .c` 11 px.
7. **C16.** `.song .sb a, .c6h .sb a` get the C5-4 44 px phone pill (max-width 760).

## Test expectation updates
- `terms_test.py`: hover parsing and expectations for the bracket form and counts (the generic scan ignores the count; the tile table checks it).
- `unit_test.py`: new MD hexes, bracket form, plus a new count-on-both-sides check per tile (C13); `import re`.
- `earlab_r2_test.py`: red `#d15e5d`.
- `content_lint.py`: no change needed (no hover-format expectation in it).

## Tests (self-check)
| Suite | Result |
|---|---|
| content_lint | passed (0 failures) |
| unit_test | 960 checks, 0 failures |
| terms_test | 0 failures (n_failures 0; about 15 min run) |
| layout_test | 272 views, 0 findings, 0 page errors |
| pageerrors_test | 0 errors on the third run (see gaps) |
| earlab_ui_test | 469 checks, 2 failed: FR-19 letter-names checkbox at 1440 and 390 (`accent-color: auto`, 18 px). Identical on the unmodified 049 base, so not caused by C6 |
| cvd_sim --check | all rules pass (worst pair now 12.6; worst text contrast above 4.5) |

Not run: the other run_all suites (score_ids, sound, earlab, earlab_r2, earlab_items, chordshape, spelling, counterpoint, transport, score_measure, analysis_engrave). The red/green literal changes touch earlab_r2_test's expectation, which I edited but did not run.

## PNGs
`tests/reports/c6_049/png/` : `before_*` and `after_*`, at 1366 and 390 wide (2x): `bargrid` (climb 4), `numerals` (Analysis), `wheel` (climb 5), `earlab_bass`, `earlab_cad`. Script: `tests/reports/c6_049/shots.py` (`before` was rendered from `git archive 049`).

## Gaps and things for Fable
- **Wheel, IV node:** the two-letter "PD" at `x+25, y-21` touches the node's stroke (the "D" and "T" clear it). Fable's CSS and markup were followed as written; a nudge for two-letter letters may be wanted.
- **pageerrors_test crashed twice** ("Target crashed", about 11 min in) while other agents were running heavy suites on the same 8 GB machine; the unmodified base completed, and a third run of mine completed with 0 errors. I read it as memory pressure, not a defect, but it was not reproduced either way.
- earlab_ui_test FR-19 failure pre-exists (above).
- Term-only hovers ("US: quarter note") are not in bracket form by design; say if you want "crotchet (US: quarter note)" there too.
- No real phone or colour-blind reader.
