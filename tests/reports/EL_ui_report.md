# EL UI report (branch 048-elui, from v0.48 7ffc692)

Fable's Ear Lab card redesign built into `index.html` on top of the existing engine. No engine, item-generation or marking logic was changed.
Spec: `design/earlab_048/SPEC.md`. Screenshots of the built card (same states and widths as Fable's png/): `design/earlab_048_built/png/` (39 images, script `design/earlab_048_built/shots.py`).

## What was built
- EL-1: one Play/Stop toggle with a progress ring (CSS `--dur` and a negative `--del` for elapsed time), driven by `elInfo()` and `elOn`. Variants are secondary pills. The Ear Lab's own Stop is gone. `earSync()` updates toggles and state text without re-rendering.
- EL-2: 56px toggle; phone dock above the tab bar when the stage has scrolled up out of view (IntersectionObserver); global Stop hidden while the Ear Lab sounds; all Ear Lab targets at least 44px at 390px; hand-sign ladder keeps the stave pinned (rows 24px high with 48px steps).
- EL-3: metre progress is time-only; simple/compound by duple/triple/quadruple grid; "Hear it again with the beats shown" uses variant `beats` with a beat lane.
- EL-5: one-line rhythm stave (stick notation at rung 1, stave from rung 2) in inline SVG with Bravura outlines, final barline, visible count-in, tiles whose width equals duration, sound strip, "You wrote" above "It was", Pulse and Speed options. Time names appear at rung 1 only (one constant).
- EL-8: per-drill teaching feedback from Fable's templates, Nearly styled but still off (`EAR_NEARLY=false`).
- EL-9: persistent polite live region (`#earLive`), focus management (`EAR.focus`), aria-pressed on toggles, rung and option groups, visible focus.
- EL-10/11: stats line, inline Reset with Undo (Esc cancels), Stage tags, drill tabs scrolling in one row.
- EL-13: function-coloured numerals, fixed option grids, short instruction plus "Listening for it" panel, one radius scale, desktop width cap.
- R5: prominent tally (n, ok, streak, best) at the top of the card; the same tally in the Keys interval quiz and in Sing it back. Keys stats persist in `cjg_kgym`.
- Terminology: Australian terms on buttons with US terms in `title`; US terms in brackets at first mention in feedback. No text under 11px.

## Deviations from the spec, and why
- The live region is persistent and the answer panel is `role=group` (a live region that is re-rendered is not reliably announced).
- Ladder rows stay 24px with 48px steps: the earlier melody test requires steps of at least 47px and the step is the tap target.
- Narrow layout swap at 800px (spec 760px) so tablets in portrait take the narrow stave.
- The terms pass brackets some words automatically ("bar (US: measure)"); the rhythm teaching text wraps "bar x" in `data-notm` to avoid "Bar (US: measure) 1".
- Cadence buttons use short names (Perfect, Plagal, ...) with the US name in `title`. The US names live in a `{us:'...'}` record so `content_lint` accepts them.
- Dock appears only when the stage is fully scrolled out above the viewport, never when it is merely below the fold (it covered text at the top of the page otherwise).
- Default tempo per rung (`earRhyBpm`) instead of a single default.
- Keys: `KS.gym.st` stores streak and best per mode.
- Letter-name checkbox in the melody desk is wrapped in a 44px label so the phone target passes.

## Tests changed
- earlab_test: blind tip read from `ELTIPS` / `ELTIPNOTE` (earTips is replaced by `earTipsHTML`).
- earlab_r2_test: `.el-result` for the result strip; new feedback wording.
- earlab_items_test: toggle starts questions; cadence button labels; family feedback; `.el-foot`; reset text; Stage tags.
- transport_test: toggle replaces `[data-earstop]`; new `check_toggle` (class, aria-pressed, label, ring duration against `elInfo().dur`, checked at 100ms and at the natural end).
- layout_test: also runs at 1366; new per-drill asked and answered Ear Lab states (overlap, sideways scroll, targets >=44px on phones, nothing under tab bar or dock). `layout_detect.js` ignores visually hidden `.el-sr` regions.
- score_measure_test: rhythm stave checks (text >=11px, fits its frame, no text on text, stave line except in stick notation at rung 1, final barline).

## Suite results (all pass)
| Suite | Result |
|---|---|
| content_lint | passed |
| unit_test | 637 checks, 0 failures |
| earlab_test | 0 failures |
| earlab_r2_test | 1666 checks, 0 failed |
| earlab_items_test | 0 failures |
| terms_test | 153 views, 2328 clicks scanned, 0 failures |
| transport_test | 0 failures; 199 trials, 42 items, 112 state checks, 63 toggle checks, 21 natural ends (end difference 0 ms) |
| layout_test | 272 views (1440/1366/1024/390), 0 with findings, no page errors |
| pageerrors_test | 153 views, 4192 clicks, 881 random clicks, 0 errors |
| score_measure_test | 300 scores measured, 0 with findings, no page errors |

Browser suites were run one at a time; other worktrees were running suites on the same machine, which caused one earlab_r2 click timeout that passed on re-run.
