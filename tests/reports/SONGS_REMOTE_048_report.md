# SONGS_REMOTE_048 report (branch 048-songs, from 048-int a24d936)

Two items: (E) label every single-source Hooktheory song entry; (I) compare the other session's branches (`origin/048-elui` 0480479, `origin/v0.48` f68294b) with this build and fold in what is only there. All checks below are the builder's self-checks; an independent check is still needed.

## E. Single-source Hooktheory labels (IC_LIC_048 item 9, S1, S2, S3)

17 of the 56 SONGS entries have exactly one source and it is a Hooktheory page. Three were already labelled (Gotye, Let It Happen, Weather With You). The other **14** now carry the same label, in the same words:

* where-text ends "(as transcribed on Hooktheory)";
* source note ends "a single community transcription, no second non-lyric source found yet" (added inside the existing bracket, or as a new bracket when the source had no note).

Newly labelled: Wild Thing (major); Hello (minor, and add9); Nothing Else Matters (minor); Defying Gravity (sus2); Wait For It (sus4); Wonderwall (sus4, m7, 7sus4); Don't You Worry 'bout a Thing (aug); Isn't She Lovely (the "9" and "m7" entries); You Are the Sunshine of My Life (add9 and 7sus4).

**S2, Nothing Else Matters add9.** Where-text now reads "Verse: the third chord of the Em–D–C loop (placement as transcribed on Hooktheory)". The Hooktheory source note now ends "the placement in the verse is from this single community transcription, not confirmed by the second source". The second source (guitargpsmethod) is unchanged: it confirms Cadd9 is in the song, not where.

No song was added or removed (56 before and after). Only `where` and `sources` text changed.

**content_lint.** New checks (section 3, sources): any SONGS entry with exactly one source containing hooktheory.com fails unless its where-text contains "as transcribed on Hooktheory" and its source contains "single community transcription"; and the Nothing Else Matters add9 where-text must carry the label. Lint passes on the new data. I did not run the lint against the old data to demonstrate it failing, but by construction it would have flagged the 14 entries.

**Not done, for Justin.** SCSONGS (the Keys-room scale songs, a separate table) also has single-source Hooktheory entries: What a Wonderful World, Count On Me and Don't Stop Believin' (each listed under both major and Ionian), Rolling in the Deep (natural minor) and Hotel California (harmonic minor). They are not in the 56 SONGS entries and were out of scope; same rule, same label, would apply. The lint check is on SONGS only.

## I. Comparison with the other session's branches

### 048-elui (0480479), "Ear Lab UI"

Its merge-base with this build is 51cf3cf. Since then it changed `index.html` in only 11 lines (two commits), plus tests. This build was built from the same Ear Lab card (048-elmerge) and has gone far past it (Fable's FR-1..21, V-1, key line, tally, etc.), so almost everything in `EL_ui_report.md` is already here (checked by identifier: earLive, EAR.focus, EAR_NEARLY, earRhyBpm, el-sr, ELTIPNOTE, earTipsHTML, KS.gym.st, el-foot, ELRING, earSync, el-seg, 800 px swap, data-notm on rhythm "bar x" all present in both).

Its delta, item by item:

| Item | In this build? | Action |
|---|---|---|
| Dock only when the stage is above the view (IntersectionObserver also tests `boundingClientRect.bottom <= rootBounds.top+2`) | No: this build showed the dock whenever the stage was not intersecting, including when it was merely below the fold | **Ported** (before the answer only; the V-1 rule after the answer, "dock watches the Next button, shows when Next is not fully visible", is untouched) |
| 44 px letter-names target: label `min-height:44px`, 20 px checkbox, gold accent, pointer cursor, at all widths | Partly: 44 px min-height on phones only, default checkbox size | **Ported** the 20 px gold checkbox and pointer cursor; kept the phone-only min-height (desktop unchanged; Fable signed off the card) |
| `ELCADUS` as `{us:'...'}` records so lint accepts US names | Superseded: this build has no `ELCADUS`; the cadence buttons declare their term (data-tk) | Nothing to port |
| Stale-question guard in `renderEar` (`EAR.q.d !== EAR.drill`) | Yes (7890b4c) | Nothing to port |
| Ladder rows 24 px / step margin .5 px | Superseded: this build sets the phone ladder rows from `--lad-row` (44 px steps) | Not ported (would regress E) |
| `layout_detect.js` ignores `.el-sr` / `.sr-only` | No | **Ported** (test only) |
| `layout_test.py`: 1366 px width and a per-drill asked/answered Ear Lab state check (overlap, sideways scroll, 44 px targets on phones, nothing under tab bar or dock) | No | **Ported** (test only), with one change: the dock is hidden (visibility) while the card is measured. Reason: at scroll 0 in an answered state this build's V-1 dock (correctly) sits over the panel until Next is visible; without the change the test reported 3 "overlaps" at 390 (cad, mel, blind) that are the dock itself, checked on screenshots. Result 272 views, 0 findings |
| `score_measure_test.py`: rhythm stave checks (text >= 11 px, fits frame, no text on text, stave line except stick notation at rung 1, final barline) | No | **Ported** (test only) |
| `transport_test.py`: `check_toggle` (class, aria-pressed, label, ring duration vs `elInfo().dur`, at 100 ms and at the natural end) | No, but this build's transport_test already drives the toggle (`earplay`) | **Not ported**: the diff does not apply cleanly on this build's version of the file and would need rework; recommend a later small task |
| earlab_test, earlab_r2_test, earlab_items_test edits | Already adapted in this build | Nothing to port |

### Two glitches the other session saw

Checked in the browser (1440 and 390 px; two-bar rhythm questions at rungs 3, 4, 5, with errors in bar 1 and in bar 2 only):

1. "Bar 1 is exactly right. bar 2, beat 1…" does **not** occur. The feedback reads "Bar 1 is exactly right. In bar 2, beat 4, you wrote …": the sentence after the full stop starts with "In", and "bar 2" sits in a `data-notm` span. No change.
2. "You wrote · Bar (US: measure) 1" does **not** occur. The small labels read "You wrote · bar 1" / "It was · bar 1"; the `.who` label is `data-notm`, so the term pass leaves it alone. No change.

Observation, not changed: because every rhythm-card "bar" is `data-notm`, the Ear Lab never shows "(US: measure)" at all. That follows the other session's approach too; it is a decision for the terms owner (answer 6 says both terms at the first mention in each room).

### v0.48 (f68294b), "R6 fix round"

This is a parallel implementation of the same IC_R6 fixes that 048-int already has (c67a252, merged as 6f5a600), from the same base (96ebd4b). `git diff c67a252 b151fe2 -- index.html` is 135 lines. Both fix H1-H3, M1-M4, L1-L7 and the circle neighbours. This build is the more complete one (shared-term observer, three bracket forms including the merge "(US: authentic cadence; V–I)" and the square form, `TM_LIST`, `termUSw` plurals, T/S legend with the US letters kept in the bracket, tests T6). Differences, and what I did:

| Behaviour in f68294b | This build | Action |
|---|---|---|
| Bare "tone" pairs after "one" as well as "a", before away/from/sharper/flatter, and at "a tone." | Narrower: only "a", before higher/lower/above/below/apart/up/down, ")" or end of text | **Not ported.** It is a judgement call (R6fix_report judgement 2) and a wider match risks the Ear Lab's pitched "a tone, because…". Recommend Justin decides; if wanted, add `one` and `away|from` to the lookahead |
| Rests as five separate TERMS entries (crest, qrest, …) | One entry per note value with optional "rests" in the pattern and `termUSw()` | Not ported: same behaviour, the existing approach also keeps plurals |
| Hand-reworded sources to avoid collisions (scores/meta.json "Perfect cadence: V–I", Climb sentences, Forms text, "Span: 7 semitones, or 0.6 octaves") | Collisions solved in the pass (merge/square forms), source strings left as they were | Not ported: would conflict with the approved terms design and the IC_TERMS M2 meta.json fix |
| Circle neighbours via `fifthFrom()` and "major/minor" after each neighbour | Neighbours from the key signature (n+1 / n−1 accidentals), and the same " major/minor" is already printed | Same output; nothing to port |
| `cadWord(c,lc)` first-mention capital in the progression report | `TERM_IAC_LC` always lower case in mid-sentence | Not ported (this build's rule is what IC_R6 L3 asked for) |
| Step labels T/S/T+S with per-step hover; octatonic "semitone–tone diminished" | Same, plus the hover shows on steps and the octatonic US name sits in the chip hover | Nothing to port |

Net: nothing from v0.48 is ported. Its report file name differs (`R6_R7_R10_R11_report.md`, section "Fix round"), which is why `R6fix_report.md` is absent there.

## Changes made (files)

* `index.html`: 14 SONGS entries labelled, NEM add9 label; dock rule; letter-names checkbox.
* `tests/content_lint.py`: single-source Hooktheory label check, NEM add9 check.
* `tests/layout_detect.js`, `tests/layout_test.py`, `tests/score_measure_test.py`: ported from 048-elui, layout_test adapted as above.

## Self-checks

See the commit message and final summary for pass counts: content_lint pass (56 song entries); unit_test 640 checks, 0 failures; earlab_ui_test 469 checks, 0 failed; layout_test 272 views, 0 findings, no page errors (it was 3 findings on the unadapted ported test, all the V-1 dock); pageerrors_test 153 views, 4196 clicks, 881 random clicks, 0 errors; score_measure_test 0 scores with findings, including the ported rhythm stave checks.

## Open

* The Ear Lab's `bar` gloss (above).
* SCSONGS single-source Hooktheory entries (above).
* The transport toggle check from 048-elui (above).
