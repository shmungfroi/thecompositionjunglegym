# TRANSPORT 0.49: rhythm transport end (L32) and test robustness

Branch `049-transport` from `origin/049-int` @ 1c5ba27. Not pushed.

## 1. transport_test: "state end vs last node stop" on Ear Lab rhythm rungs

**Cause.** Since the 0.49 ladders merge (4d94d46, "fix playback routing for rhythm"), every rhythm item has `barLen` and plays
through `ladSchedRhy`, not the old `earSchedRhy`. `ladSchedRhy` returned `end = max(line end, ls + barsT*tk)`, which is the
**written barline** at the end of the last bar. `elPlay` takes `max(r.end, SEND.v)`, so the barline always won. The sound stops
earlier than the barline whenever:
- rung 1 (clapped): the clap lasts 0.21 s, so a last note shorter than a beat ends before the barline (seen: 0.22 s early);
- any rung: the line ends on a rest, so the last sound is the last pulse tick (0.08 s long) on the final beat, which is about a
  beat minus 0.08 s before the barline (seen: 0.67-0.83 s; this is the "about 0.6 s").
Rung 3 had the same fault when it ended on a rest (a probe saw 0.83 s at rung 3); the 6-8 failing trials were the draws that ended
this way. `ladSchedRhyBeat` (the "hear that beat" replay) had the same kind of fault: its end included the 0.45 s gap after the
last segment.

**Fix (index.html, engine only).** `ladSchedRhy` and `ladSchedRhyBeat` now measure the last stop time of the nodes they schedule
(every sound function already reports it through `schEnd`/`SEND.v`; the function saves the outer value, resets, schedules, reads,
restores the max) and return that as `end`. The transport state therefore goes idle when the last node stops. Nothing that is
scheduled changed: same nodes, same times, same levels, same count-in, claps, tones, pulse, drums; only the reported end moved.
`elRender` still renders `end + 0.3 s`, which covers every node. The test was not changed.

self-check, probe on rungs 1-3 (4 draws each, 1440 px): end minus last node stop = 0.000 s in all 12 (before: 0.22-0.83 s on 6 of 12).

## 2. terms_test: "Target crashed" on one long run

**Fix (tests/terms_test.py).** Each Stage now runs on a fresh page in its own context (default `TERMS_PAGE=stage`;
`TERMS_PAGE=view` gives every view its own page; `TERMS_PAGE=one` keeps the old single page). T1 and the targeted T6 cases run on
the first page as before; before each fresh page the old page's violations (`window.__TV`) and scan counts (`__TN`) are merged into
the report. Views, clicks, their order and limits, and every check are unchanged; T5 idempotence and the automatic-pass check run
on the last sweep's page, as before.

self-check: the full suite completed in one run (11 min 14 s): 3 fresh pages, 153 views, 2,350 clicks, 2,513 scans, no crash.
It reports **22 failures**, all app content, not the test: 21 T3 (Stage 6 Ear Lab melody rhythm tiles titled "Crotchet",
"Quaver", "Dotted minim", rests etc. without a US hover; the C2 rhythm-card prompt "two bars (US: measures)" flagged at rung 2) and
1 T6 (M3i rhythm tile hovers). self-check: the unchanged 1c5ba27 test with `TERMS_STAGES=6` gives the same 22 failures, so the
page change neither adds nor hides any. These belong to the 049 ladder UI, not this branch.

## 3. earlab_ui_test "detached element" flake

Did not reproduce here (4 clean runs). Fable's verify (FABLE_VERIFY_C6_049, S-3) places it at the V-1 step that scrolls an answer
control into view and clicks it while the Ear Lab may re-render. That step now goes through `real_click()`, which re-finds the
control by selector and retries (up to 4 tries) only on "not attached / detached" errors. It is still one real pointer click on the
first match; no check changed.

## Runs (one at a time, foreground, this branch)

| suite | result | counts |
|---|---|---|
| transport_test | pass (12 m 41 s) | 198 trials / 198 silent; nav 6/6; Ear Lab 42 items, 112 state checks, 21 natural ends, 42 double taps, 28 variants, 256 stop events; worst end diff 0 ms; 0 fails, 0 page errors |
| terms_test | completes in one run; FAIL 22 (pre-existing content, see 2) | 153 views, 2,350 clicks |
| earlab_ui_test | pass (57 s) | 469 checks, 0 failed |
| earlab_test | pass (3 m 53 s) | 134 counts, 0 failures (L14 renders and L15 swing renders use the changed functions) |
| unit_test | pass (12 s) | 1,164 checks, 0 failures |

Not run here: the rest of run_all (sound_test, earlab_r2_test, earlab_items_test and others).
