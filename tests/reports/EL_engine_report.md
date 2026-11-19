# Ear Lab engine, register 0.48: EL-1, EL-3, EL-4, EL-12, R13 and R13+

Branch `048-elengine`, built on the live 0.47 commit ef97cdb. This covers the audio and transport engine only. The visible Play/Stop toggle, its ring, the dock and the card layout are left to the UI build from Fable's spec (`design/earlab_048/SPEC.md` on `048-fable`). Existing buttons now call the new API, and the only visible changes are small ones: a "Loading…" Start button, the rhythm Pulse and Speed controls, and a "show all" button for the Stage filter.

Commits, one per item, in this order: EL-1, EL-3, EL-4, EL-12, R13 + R13+, then the items the coordinator added mid-task (Stage filter, metre rung 3 pool, two cadence models held out, "Nearly" support). Each intermediate state was loaded, and every drill × rung played without page errors. The intermediate EL-3 and EL-4 states also pass their own sound tests.

## Transport API (for the UI builder)

All of it is in `index.html`, in the "audio: the Ear Lab transport and sounds" section of the Ear Lab block. The state object `ELT` sits next to `PLAY`, so `stopAll` can reach it.

| Call | What it does |
|---|---|
| `elPlay(item = EAR.q, variant = 'all', opts)` → info | Plays an item. Anything already sounding is stopped first (it calls `stopAll`). Variants: `'all'`, `'nokey'`, `'bassonly'`, `'first'`, `'beats'` (metre: the same playback, with beat events), and `'tap'` (one solfa-ladder note, `opts.midi`). A second press of the same item and variant within 300 ms is ignored, so a double tap is safe. If the sounds or scores aren't loaded yet, the state goes to `'loading'` and the item plays once they arrive. |
| `elStop()` | Stops the sound. It is `stopAll()`, so it stops everything else too. |
| `elOn(fn)` → unsubscribe | `fn({type:'state', state, id, start, t0, dur, end, lead, variant, beats, elapsed, why})` on every change. `why` is `'end'` (the sound finished), `'stop'` or `'error'`. With the `'beats'` variant it also sends `fn({type:'beat', i, t, a, bar, beat, kind})` live at each beat. |
| `elInfo()` | The current state. `state` is `'idle'`, `'loading'` or `'playing'`. `start` is `performance.now()` (ms) at the press. `t0` is the audio time of the press. `dur` is the seconds from the press to the real scheduled end, lead-in included. `lead` is the silent lead-in (s). `beats` is `[{t (s from the press), a, bar, beat, kind}]`, where `kind` is `'down'`, `'accent'` or `'beat'`; it is filled for `'beats'` only. |
| `elReady(drill)` / `elPreload(drill)` → Promise | Whether the piano (and, for blind analysis, the scores) is loaded, and a call to start loading. `renderEar` already preloads. |
| `elRender(item, variant, opts)` → Promise<{buf, info}> | The same playback rendered offline: same functions, levels and limiter. `opts`: `sr`, `tail`; for rhythm also `bpm`, `pulse`, `clap`. The tests use it. |
| `earPlay(variant)` | The old entry point, kept. It is `elPlay(EAR.q, variant)`. |

For a progress ring, start the arc at `start` and run it for `dur` seconds. The state returns to `'idle'` by itself at the scheduled end. `stopAll` sets `'idle'` from every path: the top-bar Stop, Esc or Space, leaving the room, and any other playback. The Ear Lab's own "■ Stop" button is still there for the UI build to remove (spec 5.1).

Spec section 11 asked for `EAR.play`, `earPlayEnd` and `earPlaySync`. These hooks cover the same ground: `elOn` replaces `earPlaySync` polling, `why:'end'` replaces `earPlayEnd`, and `elInfo()` replaces `EAR.play`. Two hooks are not built (see "Not done"): the per-question play count, and a "count-in" phase marker. The rhythm count-in can be derived: the count-in is beats 0–3 at `60/bpm` s from `lead`.

## EL-1: one Ear Lab transport

- `elPlay`, `elStop`, `elOn`, `elInfo` and `elIdle` are new. `earPlay` became a wrapper, `earSched(item, variant, t0, opts)` holds the scheduling for every drill, and the fixed 20 s timer is gone.
- `SEND` / `schEnd(e)` are new. `c2Tone`, `tone` (synth), `smpTone` and every new sound record their stop time, so the state ends at the last node's real stop time. A watcher re-checks against the audio clock.
- `stopAll` now calls `elIdle('stop')`. The new `PLAY.guard` is the double-tap window.
- Sound stops on Next (`earNew` stops first), rung change, drill change, room change (`room` → `stopAll`), answering (option press and Check), Show me, Esc, the top-bar Stop and the Ear Lab Stop. A ladder tap stops the question and plays its own note, reported as the `'tap'` variant. A variant press while something plays switches straight to it.
- Global transport fix: after a stop, a ▶ button stayed marked "■" for up to 150 ms, so a quick press was taken as Stop. The click handler now un-marks a button when nothing is sounding.
- `earGen` tags each item with its rung (`q.lvl`).
- `ac()` never resumes an `OfflineAudioContext`.

## EL-3: metre playback

`earSchedMetre`: 0.6 s of silence, no count-in, then whole bars (the generated four-bar pattern repeats) until at least 10 s have sounded, then one closing downbeat. `earClick` levels drop 5 dB per step: downbeat > secondary accent > beat > subdivision. The `'beats'` variant reports the beats.

## EL-4: rhythm sound

- `elRhyNote`: a tone (C5) with a 3 ms attack and a hard release, falling over 10 ms and silent 6 ms before the written end.
- `elBlock`: the count-in and pulse, a low woodblock around 200 Hz.
- `elClap`: three filtered noise bursts, high-passed at 800 Hz so it stays out of the woodblock's band. Rung 1 is clapped; from rung 2 it is the tone.
- `earSchedRhy`: one bar of count-in, then the rhythm, with the pulse switchable.
- Options in `EAR.rhy = {pulse, bpm}`, saved in `cjg_ear`. Minimal controls sit in the rhythm card (`#earPulse`, `#earSpd`: steady 72 / normal 100).
- The `EARHOW` rhythm text was updated.

## EL-12: levels, loading and timbre

- Ear Lab sound now goes through its own limiter (`elLim`: threshold −2 dB, ratio 20, 1 ms attack) instead of the app compressor. With the compressor, the accent steps and drill levels didn't hold. `MAST` returns to the compressor at the end and on `stopAll`.
- Per-drill levels in `ELG` come from measured loudness (BS.1770, K-weighted and gated). Metre is evened out per item for density and tempo, and claps for the number of claps.
- Chord quality, cadences, bass and every key chord (including the blind-analysis tonic) now use the sampled piano (`pn` → `tone(..., 'piano')`), with the synth as fallback. The melody line and ladder taps keep the synth tone. `earlab_r2_test` relies on that, and the register only asked for chords, cadences and bass.
- Preloading: `SLOADED` marks a finished sample set. `elReady` and `elPreload` are new. `renderEar` preloads the piano for the drill (and the scores for blind analysis), and Start shows "Loading…", disabled, until they are ready. A press while loading plays as soon as they arrive.

## R13 and R13+

- `smpTone` holds a note to its written length. When the written length is longer than the steady part of the sample, it plays a looped copy from `smpLoop`. The loop sits before the 1 s fade, while the note is still within 20 dB of its peak. The level inside the loop is evened out, the end crossfades (0.25 s, equal power) into the audio just before the loop start, and the gain decays gently (τ 3.5 s, to 40%) up to the written end.
- Below the lowest piano sample (C2), the C2 sample is pitched down as far as A0, so there is no synth fallback. The scores go down to MIDI 24.
- The synth fallback is no longer cut at 2.6 s.
- **Cadence registers: `earCadReg(rns, key, r)`.** This is a separate helper because another agent is editing `earGenCad`, and `earGenCad` only calls it. A target lowest note and highest note are drawn independently of the category. Of nine realisations (a 3 × 3 grid of bass and soprano preferences), the one nearest the targets is used. Realisations are memoised, which takes about 6 ms per new progression. The prediction tell from 6-semitone register bands at rung 1 fell from +4.0 to about +1.3 points over chance for the lowest note (it is at or below chance at rungs 2–3).
  - **What remains:** the exact lowest or highest note still predicts the answer 3–6 points above chance. That is harmonic content, not register: which pitch classes sound depends on the cadence chords. A 4 × 4 grid did no better. The test checks the 6-semitone bands, alone and together.
  - **Coordinate with whoever edits `earGenCad`:** keep its last line as `const{reg,P}=earCadReg(rns,key,r);`.

## Added mid-task at the coordinator's request (from Fable's SPEC)

1. **Tell tests.** `earlab_test.py` section C now also checks mode, mode with number of chords, and both register bands together, for every cadence rung. If rung 3 is ever marked with refined answers (`phrygian`, `cad64`), it checks mode and length against those too. Today it only reports them. Measured on today's rung-3 pool with the refined labels: mode 26% against 26% chance; length 26% against 26%; mode with length 26% against 26%. The best-guess predictor gains nothing, because Phrygian and the cadential 6/4 are minority answers within every mode and length. The constraint is still there, though: Phrygian is only possible in minor, and the cadential 6/4 only in five-chord phrases. A student who knows that can rule options out. Whoever adds the refined answers should balance them; once those answers exist, this check becomes a hard failure.
2. **Two rung-3 models held out:** `I IV I:2 V vi` and `i VI i:2 V VI` (interrupted after a cadential 6/4), pending Justin's ruling. They are listed in `CAD3_HELD`; empty the list to restore them. The test checks they stay out.
3. **Stage filter (EL-11).** `EARSTAGE` holds Fable's table. `earRungShown`, `earDrillShown` and `earStageTag` are new, and `EAR.all` is saved and cleared when the Stage changes. `renderEar` hides drills and rungs above the Stage, and one "show all" button sets `EAR.all`. The saved drill and rung always show. Metre rung 3 now offers all eight metres (`earMetreOpts(3)` gains 2/4 and 12/8).
4. **"Nearly".** `earJudge(q, given)` returns `'correct'`, `'nearly'` or `'wrong'`. `earMark` accepts `'nearly'`: the streak is kept, it isn't scored, and it is counted in the new stats field `nearly`. It is off by default (`EAR_NEARLY = false`). It only applies once rung 3 answers are the refined ones.
5. Every `data-ear*` attribute is kept.

## Tests

| Suite | Result | What was added |
|---|---|---|
| `transport` | pass (796 s) | The Ear Lab section: 7 drills × 3 rungs × 2 widths = 42 items; 114 state checks (state end vs last node stop: worst 0 ms); 21 natural-end checks (playing 150 ms before the end, idle 150 ms after, no node sounding); 42 double taps; 42 play-while-playing; 30 variants while playing; 256 stop events (Ear Lab Stop, top-bar Stop, Esc, Next, Show me, option answer or Check, ladder tap, rung, drill and room change), 0 overlapping sources; 3 live beat events within 60 ms; the global toggle (a second tap within 300 ms ignored, after that it stops). The existing room and climb checks still pass. |
| `sound` | pass | **EL-3:** 24 renders (8 metres × 60, 90, 120 bpm). The lead-in is 0.6 s; there are whole bars totalling at least 10 s; the last event is a downbeat; the beats hook matches. Smallest accent steps (dB): down > accent 6.5, accent > beat 7.0, beat > subdivision 5.1, and every event is louder than every event in the class below. **EL-4:** every one-bar answer per rung (25, 196, 1089 = 1,310) at 72 and 100 bpm with the pulse on = 2,620 renders. Onsets recover the written rhythm exactly (worst onset error 7.3 ms; worst note-off error 1.7 ms against the ±20 ms limit); every count-in and pulse beat is detected. Masking, each sound alone, per event: tone in the woodblock band −21.8 dB, woodblock in the tone band −22.4 dB, clap in the woodblock band −24.9 dB, woodblock in the clap band −33.1 dB (limit −20). **EL-12:** loudness (LUFS mean, min, max): metre −25.8 (−27.5, −24.5); rhythm −25.7; chord quality −26.0; cadences −25.9; bass −26.0; melody −26.2; blind −26.3; ladder tap −26.0. All are within ±0.3 of the −26 target. Metre was 16 dB and rhythm 8 dB quieter before. **R13:** 19,104 Analysis notes (10 scores × 0.75, 1, 1.25 speed), all sampled, none synth, each held to its written length + 0 to 150 ms; 18 notes are over 2.6 s at 0.75 speed (Jesu 8, K. 545 4, Chopin 20 6; Chopin 20's 6 are over 2.6 s at every speed). Held 6 s notes at MIDI 24–92 are at most 8.8 dB down at 5.5 s from where the hold begins, with at most 1.6 dB at a loop seam. |
| `earlab` (`earlab_test` + `earlab_r2_test`) | pass (256 s + 106 s; 33 tell checks, 0 failures) | Section C: mode, mode with length, register bands together, refined-answer report, held-out models. The original tells still pass. |
| `unit` | pass (142 checks) | none |
| `content_lint` | pass | none |
| `pageerrors` | pass (153 views, 4,241 clicks, 881 random clicks, 0 errors) | none |

## Not done, and things to flag

- **Rhythm answer count.** The brief says "all 1,870 one-bar rhythm answers". The app's own rules (`earCells` / `RCELL` / `earFill`) produce 25 + 196 + 1,089 = 1,310 distinct one-bar answers per rung, and the test enumerates them from the app, so it follows any change to the cells. 1,870 may count something else, such as another agent's cell set; that is worth checking.
- **Hooks in Fable's §11 not built here:** the per-question play count ("played twice"); the count-in phase marker (derivable, as above); the new replays (rhythm one-beat A/B, chord quality interval-then-chord, cadence last two or three chords slowly, bass per-chord callback, melody fragment A/B, "hear 3/4 at the same speed"); `earRhyBeats`; and the refined cadence answers `q.a = 'phrygian' | 'cad64'`. `earSched` is the place to add replays. Each can be a new variant name; the transport and state handling then come for free.
- **Two rung-3 cadence models held out**, pending Justin's ruling (above).
- **The "Nearly" outcome** is supported but off, pending Justin.
- The Stage filter UI is a plain chip strip with one "show all" mini button. Fable's `.el-drills` / `.el-rungs` design is for the UI build. The rung buttons still say "Level n", and the copy says "level" in places. Fable's rename to "rung" is for the UI build.
- High piano notes (MIDI 84 and up) decay fast in the samples. They are held in a quiet loop around −30 dB below the attack, which is faithful to a piano but faint. Nothing in the scores sits there for long.
- Test run times: `transport` is now about 13 min (the Ear Lab section waits for 21 natural ends); `sound` is about 5 min (it opens a fresh page per 250 rhythm renders, because a single page crashed after about 2,000 offline renders).
