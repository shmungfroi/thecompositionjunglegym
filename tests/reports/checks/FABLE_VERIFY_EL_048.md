# Fable verification — Ear Lab card after the FR fixes (0.48)

Build verified: `/home/claude/wt-check-int`, detached at ff8dba7, read-only (nothing in the repo was edited; `git status` is clean).
Compared against: my review `tests/reports/checks/FABLE_REVIEW_EL_048.md` and the build I reviewed then (38ea640, served from a temporary copy for one old-versus-new comparison).
My screenshots (about 640), scripts and measurements: `/home/claude/checks/fable_el2/` (`png/`, `verify.py`, `extra.py`, `compare.py`, `proposal.py`, `keys.py`, `justin.py`, `metrics*.json`). Paths below are relative to `/home/claude/checks/fable_el2/png/`.
Sizes: 1440×900, 1366×768, 1024×768, 390×844, plus 390×664 for the phone check in V-1. Headless Chrome only; no real phone.
I looked first, then read Sonnet's report (`tests/reports/EL_fablefix_report.md`). Its claims match what I measured, with one small difference noted under FR-16.

## Verdict: NOT YET — one Must, small

Twenty of the twenty-one items are fixed or fixed far enough to carry. The card is better than the one I reviewed: the headline is clean, the 5/4 picture is right, the melody result reads in order, the header holds its title on one line, the dock is opaque, and the labels are free of stray underlines.

One thing stops the sign-off, and it comes from two of my own instructions (FR-2 and FR-6b) acting together, not from Sonnet's work: **after an answer, the Next button is often not on the screen.** Fix V-1 and I sign off with the Shoulds below carried.

## Must

**V-1. After an answer, Next is off the screen and the dock no longer supplies it.**
`cmp_new_cad_after_answer_390x664_view.png`, `realclick_mel_after_check_390_view.png`, `realclick_rhy_after_check_390_view.png`, `nearly_cad_r3_390_view.png`, `focus_after_mel_check_1366_view.png`; numbers in `metrics_compare.json` and `metrics_extra.json`. All by real taps and clicks.

| After answering | This build | Build I reviewed |
|---|---|---|
| Phone 390×844, cadences rung 3 (Nearly) | Next cut by the tab bar (15 px hidden), no dock | Next just visible |
| Phone 390×844, rhythm, melody | Next below the tab bar, no dock | same |
| Phone 390×664 (a phone with browser bars), cadences, rhythm, melody | Next off screen, no dock | dock shown, with Next |
| Phone 390×664, metre | Next off screen, no dock | same |
| Desktop melody, 1440×900, 1366×768, 1024×768 | Next off screen (it is now the last thing in the panel); at 1366×768 the headline is off screen too | visible at 1024, cut at 1440, off at 1366 |

Causes: FR-6b (as I wrote it) hides the dock while any part of the result is in view; FR-2 (as I wrote it) moves the melody Next to the bottom of a panel that already opened below the fold; FR-5 made the phone header 17 px taller, which is what pushes the cadence Next under the tab bar. Focus does go to Next, but with `preventScroll`, so the focused button is invisible.

Change (tested by injection at five sizes and four drills, `proposal_v1_*_view.png`, `metrics_proposal.json`; before and after side by side in `sheet_v1.png`):
1. After an answer, bring the result panel into view once: if it fits between the top bar and the tab bar, scroll so its bottom edge sits 12 px above the tab bar (or the window bottom on desktop); if it does not fit, scroll its top to 12 px under the top bar. No smooth scrolling under reduced motion.
2. After an answer, the dock observes the panel's own Next button (threshold 1), not the whole panel: the dock shows whenever that button is not fully visible above the tab bar.
Result in the test: Next is on screen, or in the dock, in all 20 cases, and the dock never covers the teaching sentence (which was the reason for FR-6b).

## FR by FR

| FR | Status | Evidence | Note |
|---|---|---|---|
| 1 Headline gloss | Fixed | `sheet_fr1.png`, `fr1_cad_interrupted_wrong_1440_crop.png`, `fr1_blind_wrong_390_crop.png` | Headline is the name only, one line at all four sizes. |
| 2 Melody result order | Fixed; see V-1 | `sheet_fr2.png`, `fr2_mel_result_1440_crop.png`, `fr2_mel_result_390_view.png` | Headline, sentence, replays, Next. Next is full width on phones (302 px). Tab order still reaches Next before the replays above it; minor. |
| 3 Keys tally and mode buttons | Fixed on phones; new wrinkle at 1024 | `sheet_fr3.png`, `fr3_keys_name_40of48_390_view.png`, `fr3_kqhead_name_40of48_1024_crop.png` | Phone: tally on its own line, buttons on one line at every score. At 1024 a two-digit score drops the tally to a second row, left-aligned (S-4). |
| 4 5/4 picture | Fixed | `fr4_cell_54_390_crop.png`, `fr4_metre_54_wrong_1440.png`, `sheet_fr4.png` | Five beats of large-plus-small, wider gap after beat 3; it now agrees with the beat lane. Fits its cell at 390 (82 px picture in a 104 px cell). |
| 5 Phone header | Partly | `sheet_fr5.png`, `fr12_rhy_answering_empty_390_view.png`, `justin_phone_nearly_390_view.png` | Titles on one line up to 99 of 99; "Bass and numerals" breaks evenly at two-digit scores, as expected. The header still grows at the first answer: 104 to 122 px (was 26 px, now 18) (S-1). |
| 6 Dock | (a) Fixed. (b) Fixed as I specified it, and my specification was wrong | `dock_crop_390.png`, `sheet_d.png`, `fr6_result_half_390_view.png` | Ground is solid `#16130d`; nothing shows through. (b) is the main cause of V-1. |
| 7 Glossary underlines | Partly | `fr7_metre_r2_idle_390_view.png`, `fr18_rhy_checked_2bar_390_crop.png`, `fr7_rhy_tips_1024_crop.png` | Column headers, caps labels, "It was · bar 1" and the provenance line are clean (zero glosses measured in any state). Tip says "The strip". Left: the rhythm tip note still underlines "quaver, crotchet, quaver" (S-6). |
| 8 Muted US brackets | Partly | `nearly_cad_r3_1440_crop.png`, `justin_phone_nearly_390_view.png` | Glosser brackets are muted. The hand-written "(US: half)" in the Nearly sentence is still ivory, so one sentence carries one ivory and one muted bracket (S-2). Second half (one bracket, not two) not done. |
| 9 Cadence key line | Fixed | `fr9_keyline_390_view.png`, `fr6_result_half_390_view.png` | No Plagal clause; breaks only between pairs; hidden from 1180 px, shown at 1179 (checked at the edge). |
| 10 show all rungs | Fixed | `fr10_stage4_rungrow_1440_crop.png`, `fr10_stage4_metre_390_view.png` | Present at Stage 4, gone once used. On phones it sits on its own line and the row grows from 46 to 100 px (S-5). |
| 11 Strip "show all" target | Fixed | `fr11_strip_end_390_view.png` | 44 px high. No Ear Lab target under 44 px on the phone in any state measured. |
| 12 Rhythm bar-2 placeholders | Fixed | `fr12_rhy_390_crop.png` | Dashed outlines in every narrow bar. |
| 13 Pulse / Speed captions | Fixed | `fr12_vars_390_crop.png` | Each caption stays with its control. |
| 14 Bass headline numerals | Fixed | `fr14_bass_r2_result_1440_crop.png`, `fr14_bass_r3_result_390_crop.png` | EB Garamond 500, 26 px, loaded. |
| 15 Focus on the selected rung | Fixed | `fr15_focus_rung_on_390_crop.png`, `fr15_focus_rung_on_1440_crop.png` | Ink ring inside the gold; quiet but visible. |
| 16 Fold at 1366×768 | Fixed | `fr16_fold_metre2_1366_view.png`, `fr16_fold_cad3_1366_view.png` | Last answer control ends at 759 (metre rung 2), 727 (cadences rung 3; Sonnet's report says 680, I measured with "Without the key chord" showing), 680 (quality rung 3), window 768. Metre has 9 px to spare. Rule switches exactly at 1180 px and 820 px. 1024×768 is outside the rule, as I scoped it. |
| 17 Tips width at 1024 | Fixed | `fr17_tips_cad_1024_crop.png` | List 625 px, note 558 px. |
| 18 Rhythm feedback sentence | Partly | `fr18_rhy_checked_2bar_1440_crop.png`, `fr18_rhy_checked_1bar_1440_crop.png` | Lead is right: "In bar 2, beat 1, you wrote…", "On beat 1, you wrote…". The merged bracket "(US: quarter note; one sound)" remains and is now half muted, half ivory (S-3). |
| 19 Checkbox | Partly | `fr19_checkbox_row_390_crop.png`, `fr19_checkbox_row_checked_390_crop.png` | 18 px, gold when ticked, 44 px row on phones, focus ring present. Unticked it is still a white browser box (S-7). |
| 20 Orphan options | Fixed | `fr20_qual_r2_ready_1440_view.png`, `fr20_bass_r2_ready_1440.png` | Four qualities in one row, five numerals in one row on desktop. |
| 21 Reset score | Fixed | `fr21_foot_idle_390_crop.png`, `fr21_foot_after_1440_crop.png`, `fr21_reset_undo_390_crop.png` | Disabled at 40% until there is a count; confirm and Undo still work. |

Nothing regressed outright. FR-22 and FR-23 were not applied, as agreed.

## Shoulds carried (none blocks)

- **S-1 (FR-5).** Reserve the tally's height on phones so the header does not grow at the first answer: give the empty state the counted height (62 px). Not tested.
- **S-2 (FR-8).** Mute the hand-written US brackets in the cadence sentences (wrap them in the same class the glosser uses), and cut the Nearly sentence to one bracket. Text is with the theory checker and the reconcile branch.
- **S-3 (FR-18).** Split the merged bracket so the US term and the description are separate: "a crotchet (US: quarter note), one sound."
- **S-4 (FR-3).** Keys at 1024: keep the wrapped tally right-aligned (`margin-left:auto`). The Keys mode buttons are 28 px high on phones now that they no longer wrap; that belongs with the other Keys targets in FR-23.
- **S-5 (FR-10).** Phone, Stage 4: let "show all rungs" share the line with the two rungs instead of taking a 54 px row of its own.
- **S-6 (FR-7).** One underline per card in the tips: drop the dotted underline on repeats.
- **S-7 (FR-19).** Draw the unticked box in the card's own style (transparent, 1 px line border).
- **S-8 (7/8 text).** See below.
- **S-9.** Seen while testing V-1, and the same in the build I first reviewed: after an answer on a phone the page jumps so the card's top sits under the sticky top bar, and the top 12 px of the score is hidden. The scroll in V-1 removes most cases.

## The three items Sonnet left

- **FR-8 second half (two US brackets in the Nearly sentence).** Does not block. It costs a line (three lines at 1440, five at 390) and the two brackets are different colours (S-2).
- **Rhythm tip glosses.** Does not block. Three dotted underlines in one small grey paragraph; cosmetic (S-6).
- **FR-19 unticked box.** Does not block. It is the one bright white shape on the melody card, so it should be done, but it works and is the right size (S-7).

## How the new 5/4 and 7/8 text reads and sits (not a theory judgement)

`fr4_metre_54_wrong_1440_crop.png`, `fr4_metre_78_ok_1440_crop.png`, `justin_phone_metre_54_correct_390_view.png`, `fr4_metre_78_ok_390_view.png`.
- Row label "uneven groupings" fits beside "Irregular" at every size.
- 5/4: three sentences, two lines at 1440, four at 390. It is the longest metre sentence but it sits inside the panel without pushing Next off a 390×844 screen. It reads well: what the bar is, what "irregular" means, what you heard. The picture, the lane and the sentence now say the same thing.
- 7/8: two lines at 1440, four at 390. "2+2+3" appears three times in one panel (headline, first sentence, last sentence). End the last sentence at "Count the quavers in each group." (S-8).
- In both, "bar" carries a dotted underline with no bracket (the bracket is on the question line above). Acceptable.

## Measured and passed, all four sizes
- No text under 11 px in any state; no sideways scroll; no page errors.
- Focus: every control reached by Tab shows a 2 px ring; the new link and the checkbox included.
- Reduced motion: only the play ring animates; dock and tally are still.
- Nearly: gold panel, wave mark, streak kept, foot reads "14 answered · 2 nearly · 2 shown · 1 skipped".

## For Justin
`/home/claude/checks/fable_el2/for_justin/`
1. `1_desktop_cadences_nearly_1440.png` — Nearly, desktop.
2. `2_desktop_metre_grid_5-4_1440.png` — the metre grid with the corrected 5/4 cell, answered.
3. `3_desktop_rhythm_checked_1440.png` — rhythm, You wrote / It was.
4. `4_phone_cadences_nearly_390.png` — Nearly on a phone. Next is cut by the tab bar here: that is V-1, shown as built.
5. `5_phone_metre_grid_390.png` — the metre grid on a phone, with the dock.
6. `6_phone_metre_5-4_correct_390.png` — a 5/4 answer on a phone.

---

## V-1 re-check (commit 2a12353)

Build: `/home/claude/wt-check-int`, detached at 2a12353, read-only. Scripts `recheck.py`, `recheck2.py`, `recheck3.py`; numbers in `metrics_recheck.json`, `metrics_recheck2.json`; shots `recheck_v1_*_view.png` (in `/home/claude/checks/fable_el2/png/`).

**V-1 is fixed.** Same test as before, with nothing injected: five sizes (390×844, 390×664, 1366×768, 1440×900, 1024×768) × four drills (cadences rung 3 Nearly, metre, rhythm, melody), real taps and clicks.
- Next is fully on screen in 18 of 20 cases. In the other two (390×664, cadences and rhythm, where the panel is taller than the room) the dock is showing with Next in it.
- The dock never covers the teaching sentence. Focus is on Next every time.
- The positions are the same, to the pixel, as my injected proposal.

Glance for regressions, at 390×844, 390×664 (reduced motion on) and 1366×768:
- Three questions in a row: the result is brought into view each time, and Next (panel or dock) starts the next question.
- After scrolling away and pressing play, the page does not jump back (scroll position unchanged before, during and after playback).
- Before answering, scrolled to the end, the dock still shows, without Next.
- "Show me" brings its panel into view the same way.
- No page errors.
- 7/8 now reads "Seven quavers (US: eighth notes) in a bar, grouped 2+2+3 here, so the beats are not all the same length. Count the quavers in each group." "2+2+3" appears twice in the panel (headline and sentence). S-8 is closed.

Not re-run: the full FR-1 to FR-21 sweep. The commit changes one sentence and the one observer function, so I re-tested only what they touch.

### Final verdict: SIGN OFF, with these Shoulds carried

Must list: empty.
Carried to the next register (none blocks): S-1 header grows 18 px at the first answer on phones; S-2 ivory "(US: half)" beside a muted bracket, and two brackets in the Nearly sentence; S-3 merged, half-muted bracket in the rhythm sentence; S-4 Keys tally alignment at 1024 and 28 px Keys mode buttons on phones; S-5 "show all rungs" row on phones at Stage 4; S-6 repeated underlines in the rhythm tip; S-7 unticked checkbox; S-9 the card's top (12 px of the score) under the sticky bar when the result needs no scroll. FR-22 and FR-23 stay open as before.
