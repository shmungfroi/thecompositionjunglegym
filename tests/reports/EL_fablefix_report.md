# Ear Lab 0.48: Fable review fixes (FR-1 to FR-21)

Branch `048-frfix` (from 048-int 812a9fe, then 048-int merged again at a4df4f2). Single file `index.html`; tests in `tests/earlab_ui_test.py` (new section H, 422 checks).
After-shots: `design/earlab_048/built/png_after/` (script `design/earlab_048/built/shots_after.py`), all viewed at 1440 / 1024 / 390 where listed.

## FR to change to test to result

| FR | Change | Test | Result |
|---|---|---|---|
| 1 | `data-notm` on `.el-answer`; the US gloss now falls at the first mention in `.el-teach` (or nowhere, if the sentence does not use the term) | H: headline has data-notm, no `.tmus`/`abbr.tm`, text exactly "Interrupted cadence" | pass; shot `cad_interrupted_*` |
| 2 | `.melres .el-result>.el-btn{order:9;margin-top:14px}`; `justify-self:stretch` at 760 | H: sentence, replays, then Next; Next full width at 390 | pass; `mel_wrong_*` |
| 3 | `.kqhead{flex-wrap:wrap;row-gap:10px}`, buttons nowrap; at 760 tally on its own line above (kept as a row there) | shot only (`tally_keys_name_390`); Keys is outside the card's test | viewed, ok |
| 4 | 5/4 picture = five beats x two dots, extra 6 px gap after beat 3 (`ELGAP`); wording below | H: 5 large + 5 small dots, spacing 28/28/34/28; 7/8 (3+4) and 12/8 (4 large) unchanged | pass; `metre_r3_54_*`, `metre_r3_78_*` |
| 5 | phone header: `.el-head` gap, tally as a column, `.el-side` as a row, `text-wrap:balance` | H (390): Pulse and metre, Rhythm dictation, Cadences, Melodic dictation on one line at 58 answered / streak 12 | pass; `bass_two_digit_390` |
| 6 | (a) dock ground `#16130d`; (b) the observer watches `#earResult`, so the dock shows only when the whole panel has left the view | (a) H computed colour; (b) ad hoc run (not in the suite): result in view, dock hidden; scrolled away, dock shown | pass |
| 7 | `data-notm` on `.el-mh`, `.el-lbl` (all 5 sites), `.who`, blind provenance note; rhythm tip says "The strip under the notes" | H: headers and labels have data-notm and no gloss; tip wording | pass |
| 8 | `.el-teach/.el-ask/.el-tips .tmus{color:var(--muted)}` | H: computed colour rgb(156,146,124) | pass |
| 9 | Plagal line removed; each pair in a nowrap span; `margin:10px 0 0`; hidden at >= 1180 px | earlab_ui_test section D: no "Plagal", wording as before, display none only at 1440 | pass |
| 10 | "show all rungs" shown whenever a rung is hidden and `EAR.all` is off (no longer only when no drill is hidden) | H: Stage 4 metre has exactly one, "show all rungs" | pass; `metre_stage4_idle_*` |
| 11 | phone `.el-all{min-height:44px;...}` | H (390): that link >= 43.5 px | pass |
| 12 | `holes` option in `earRhySVG`: dashed placeholders drawn in every narrow bar | H: both narrow bar svgs have dashed rects | pass; `rhythm_answering_390` |
| 13 | each caption wrapped with its control in `.grp` (inline-flex, nowrap) | H: two groups | pass |
| 14 | bass headline numerals `.rn` in EB Garamond 500 26 px | H: computed family | pass |
| 15 | `.el-rungs button.on:focus-visible{outline-color:var(--ink)}` | focus test updated: the selected rung must show a 2 px solid ink ring, all others goldhi | pass |
| 16 | at >= 1180 px wide and < 820 px high: room intro hidden, head and strip margins tightened | ad hoc 1366x768: answer-grid bottom metre r2 759 (was 833), cadences r3 680 (was 801), quality 614; all above 768 | pass; `fold_*_1366.png` |
| 17 | `.el-tips li,.el-tips+p{max-width:68ch}` | H: max-width set | pass |
| 18 | rhythm sentence now "In bar N, beat M, you wrote ..." (single bar: "On beat M, you wrote ..."), capitalised; the "(US: eighth notes; ...)" bracket is the glosser's third form and was left | H: regex on the sentence | pass |
| 19 | `#earMain input[type=checkbox]{accent-color:gold;18px}`; label inline-flex, 44 px on phones | H | pass (the unchecked box is still the browser's light box; accent-color only colours the checked state) |
| 20 (could, done) | four quality options in four columns >= 761 px (`.q4`); five numerals in five columns >= 761 px (`.n5`) | H for the quality case | pass |
| 21 (could, done) | Reset score disabled until there is a count | H | pass |

## Wording changes in the 5/4 and 7/8 text (for the theory check)

1. Irregular row sub-label: "beats of unequal length" -> "uneven groupings".
2. 5/4 teaching sentence (was "The beats are not all the same length. Count the quick notes: 3+2."): "Five beats in a bar, each splitting in two. Irregular metres group their beats unevenly, often 3+2 or 2+3. Here the heaviest click is on beat 1 and a lighter one on beat 4: 3+2." (METRES accents are [2,0,0,1,0].)
3. 7/8 teaching sentence (was "... Count the quick notes: 2+2+3."): "Seven quavers in a bar, grouped 2+2+3 here, so the beats are not all the same length. Count the quavers in each group: 2+2+3."
4. Unchanged and for the checker to see: result headline small text "5/4 (3+2)" and "7/8 (2+2+3)"; the tips note "Irregular metres mix groups of 2 and 3: 5/4 here is felt 3+2, 7/8 as 2+2+3"; METL labels "Irregular: 5/4 (3+2)".
5. Other wording: cadence key line loses "Plagal is the same in both" (FR-9); rhythm tip "The bar under the notes" -> "The strip under the notes" (FR-7); rhythm feedback lead (FR-18, above).
Cadence and Nearly teaching text was not touched (earCad* text from the reconcile merge is as merged).

## Not applied
- FR-22 (zero numeral in muted): Fable says only if it bothers Justin.
- FR-23: outside the card, left for the next register.
- FR-8's second half (one US bracket, not two, in the Nearly sentence): text, belongs to the reconcile branch.
- The rhythm tip still hover-glosses "quaver, crotchet, quaver" (dotted underline, no bracket after the first); FR-7 asked only for the "bar" rewording, so I left it.

## Self-checks
- Interrupted test run once failed on my own mistake (a `//` comment swallowing `if(!t)return;` in `earObserve`); fixed to a block comment and re-run.
- Test expectations I changed: focus colour on the selected rung (FR-15); key-line checks (FR-9). Nothing else needed changing.
- No engine flags, rhythm names or `--lad-row` value touched.

## Pass counts (on 048-frfix after merging 048-int a4df4f2)
- layout_test 162 views, 0 findings
- pageerrors_test 0 errors
- earlab_ui_test 422 checks, 0 failed
- transport_test 0 fails
- score_measure_test 294 scores, 0 findings
- earlab_items_test 0 failures
- terms_test 200 failures, identical to 048-int without my changes (200): short cadence buttons in Forms/climbs carry "US: authentic" hovers; no new findings from the Ear Lab card (before my change terms_test had 0 findings on the pre-merge base, 162 views)
- earlab_test 1 failure ("cadences L1: lowest and highest note ... predicts the answer 32%"), identical on 048-int without my changes
No browser crashes needing a retry; one run was slow under load from other agents.
