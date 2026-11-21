# Correction register 0.49 (carried items)

Approved by Justin 20 Nov 2026 20:59 ("8 approve carried items, flag things for fixing"). R19–R22 deferred again ("6 later"). New findings during the 0.49 work are flagged here as new rows (status Drafted) for the next approval; they are not fixed without approval unless they are a Must regression of something already approved.

Columns: id · finding (evidence) · rule or standard · proposed change · impact · regression test · priority · owner · status

| id | finding (evidence) | rule | proposed change | impact | regression test | pri | owner | status |
|---|---|---|---|---|---|---|---|---|
| C1 | Content lint misses 7 US-only probes ("8th note", "16th note", "measure one" …) and over-flags 5, incl. "authentic Baroque" (IC_R2_048 S-T2) | L63 terms | Extend and tighten the lint patterns; add the 31 probes as fixtures | Lint only | content_lint with positive and negative probe fixtures | Should | Sonnet | Confirmed |
| C2 | Ear Lab rhythm card never shows "bar (US: measure)" at first mention (handover 0.48) | L63 clutter rule; L88 (6) | First mention per room shows both terms | Rhythm card copy | terms_test first-mention check | Should | Sonnet | Confirmed |
| C3 | Cadence rungs 2–3: register tells (+9–11 points on one exact pair) (IC_EAR2_048) | Ladder rule: no tells | Rebalance registers so no answer is predictable from register | Ear Lab items | earlab_test tell checks for rungs 2–3 | Should | Opus | Confirmed |
| C4 | Rung-1 interrupted cadence has only 28 voicings (IC_EAR2_048) | ≥ 100 pool / variety | Widen voicings within strict rules | Ear Lab items | pool-size and SATB checker | Should | Opus | Confirmed |
| C5 | Fable's carried Shoulds: header growth, unticked checkbox, Keys tally at 1024, FR-23 song-starter link colour, Keys interval buttons on phones, top-bar search at 1024 (FABLE_VERIFY_EL_048) | Charter design standard; 11 px floor | Fable specifies, Sonnet implements, Fable verifies | UI | layout_test (1440/1366/1024/390) | Should | Fable → Sonnet | Confirmed |
| C6 | Colour-blind pairs: tonic/predominant; dominant red 3.9:1 on darkest panel; rose vs red/violet not yet simulated (handover 0.48) | Accessibility (contrast ≥ 4.5:1 text, distinguishable functions) | Simulate deutan/protan/tritan; adjust within the Garden palette; add a non-colour cue where needed | Function colours app-wide | contrast + simulation script in tests | Should | Fable → Sonnet | Confirmed |
| C7 | IC_CP_048 Coulds (counterpoint wording and checker clean-ups) | Climb 2 rule cards | Apply the Coulds that do not change rules | Climb 2 messages | counterpoint_test | Could | Opus | Confirmed |
| C8 | "Symmetrical" sentence for aug/dim7 needs correcting (handover 0.48) | Theory accuracy | Rewrite to a true statement | Chord Library copy | content check by independent checker | Should | Opus | Confirmed |
| C9 | Ear Lab function map treats minor v / VII as dominant (no item uses them yet) (handover 0.48) | L91 (12) modal dominant | Map them to MD (modal dominant) to match the Analysis colours | Ear Lab feedback | unit_test on function map | Should | Opus | Confirmed |
| C10 | Syllabus tag gaps: MU2-11C-02, MU2-11L-01; unused MU2-12L-01 / MU2-12C-01; Music 1 / Extension codes; Melody/Harmony elements (NESA_Crosscheck_048) | Tag accuracy (reference only) | Add or correct tags | Collapsed chips | content_lint tag check | Could | Sonnet | Confirmed |
| C11 | Too few songs after 2015 (L70: span up to the present, weighted to recent decades) | L05, L70 | Add verified post-2015 picks within the 5-per-type rule (two sources or one authoritative; ⚠ notes) | Song cards | content_lint source rule; independent source check | Should | Sonnet + IC | Confirmed |
| C12 | IC_SELF_048 S1: the incomplete tonic (5th omitted) is on 66% of rung-1 perfect cadences and never on any other cadence, so a hollow final chord predicts "perfect" (42% vs 26% chance) | Ladder rule: no tells; OQ21 O kept it on "for variety" | Cap its share and/or balance "final chord complete" across all four cadences | Ear Lab rung 1 items | earlab_test tell check on final-chord completeness | Should | Opus | Drafted (needs Justin) |
| C13 | IC_SELF_048 S2: other rhythm tile hovers drop the count on the US side ("2 quavers · US: eighth notes") | L63 one-to-one terms | Name every component on both sides | Hover text | terms_test hover check | Should | Sonnet | Drafted |
| C14 | IC_SELF_048 S3: hovers read "Australian · US: American", not "Australian (US: American)" as L63 specifies; app-wide format | L63 brackets | Switch all hovers to the bracket form, or confirm the dot form for hovers | All hovers | terms_test | Could | Sonnet | Drafted (needs Justin) |
| C15 | Fable N-1: Keys piano labels are 10 px | Charter 11 px floor | Raise to 11 px | Keys room | layout_test font floor | Must | Sonnet | Drafted |
| C16 | Fable N-2: song-card links in other rooms are 26 px tall on phones | 44 px targets | Apply the C5 pill at 44 px | Song cards | layout_test targets | Should | Sonnet | Drafted |
| C17 | Fable N-3: `--red` serves both the dominant function and "wrong" | Colour carries one meaning | Depends on D2 (shared lift vs separate status tokens) | App-wide | contrast script | Should | Fable → Sonnet | Drafted (needs Justin) |
| C18 | Metal slot holds songs that are not metal: maj7 "Misty" (jazz), sus4 "Wonderwall" (Britpop), "Highway to Hell" in the major triad list (hard rock). Each carries an honest fallback note, but the slot label still says Metal (0.49 C11 survey) | L05 one per genre; honest gaps | Show these as declared gaps (SONGGAPS) and look for a real metal example, or relabel the slot | Song cards | content_lint slot-honesty check | Should | Sonnet + IC | Drafted |
| C19 | Post-2015 coverage is still thin: only Dance Monkey (2019) is after 2015. Candidates checked this round could not meet the two-source rule (Shape of You, Waving Through a Window, Leave the Door Open, Blinding Lights; see C_CONTENT_049_report.md) | L70 span to the present | Source more recent songs from lesson or analysis pages (not lyric sites); Hooktheory alone is one source | Song cards | content_lint post-2015 count | Should | Sonnet + IC | Drafted |
| C20 | Shape of You chord sources disagree: Wikipedia gives C♯m–F♯m–A–B (D♭/C♯ minor), roadiemusic gives Am, Dm, F, G (a capo or lowered chart, not stated) | Two independent sources must agree | Settle which chart is the recording's sounding key before using it | Song data | independent source check | Could | IC | Drafted |
| C21 | The Chords room tag bar carries MU4-PER-01 (performance) although the room is a reference room (NESA_Crosscheck_048 3b item 7) | Tag accuracy | Teacher to decide whether to keep it | Collapsed chips | none | Could | Justin | Drafted |
| C22 | Stage 5 MU5-PER-01/02 and Music Extension codes other than MUE-12L-01 are not carried; Stage 4 Melody and Harmony were read from a flattened page whose nesting is inferred (NESA page shows "Loading" for some labels) | Tag accuracy | Teacher check of the NESA Stage 4 elements page; add codes only where content matches | Collapsed chips | content_lint tag check | Could | Justin | Drafted |
| C23 | Rung 1 interrupted (V–vi) cannot reach 100 voicings: with open spacing and complete chords the strict maximum is 28 in the twelve keys (app pool = independent exhaustive enumeration, earlab_test D). Allowing close spacing too (still strict, vi doubling its 3rd) gives 108 (C_THEORY_049_report, C4) | EL-7 / BHL H open spacing; ≥ 100 variety | Justin to rule: allow close spacing at rung 1 for all five models together (only V–vi close would make spacing a tell); then refit earR1Weights | Ear Lab rung 1 items | earlab_test D (pool = enumeration), earlab_items_test K tells | Should | Opus | Drafted |
| C24 | Ear Lab earNumFn still reads other numerals by letter, ignoring case and mode: a borrowed iv, a major II or III, or i in a major key would be coloured PD / T, where Analysis colours them chromatic (violet). No Ear Lab item uses them yet (found doing C9) | Function colours match Analysis | Map every numeral outside the key to X (as analyse() 'C') when items need them | Ear Lab feedback colours | unit_test C9 extended | Could | Opus | Drafted |
| C25 | IC_REG_049 S1: rung 2, models I–I⁶–vi–IV–I/V in C, E♭, B major: I⁶ has no 5th and a doubled 3rd in bass and soprano (6 realisations, ~0.3%) | Strict SATB doubling (note: many texts permit doubling the 3rd in a first-inversion major chord) | Prefer root or 5th doubling in those 6; or accept as allowed | Ear Lab rung 2 | earlab_test doubling check | Should | Opus | Drafted |
| C26 | IC_REG_049 S2: rung 3 residual register tell +4.8 (worst pair +11 on 1.3% of items) | Ladder rule: no tells | Re-weight rung 3 registers further | Ear Lab rung 3 | earlab_test tell threshold | Should | Opus | Drafted |

Deferred: R19–R22 (counterpoint) — Justin 20 Nov "later".

## Justin's answers, 21 Nov 2026 05:53 (decision log L101)
| id | answer | status |
|---|---|---|
| C12 | "always use the complete chord": incomplete tonic off on every cadence (supersedes L95 O) | Approved → building (Opus) |
| C13 | (a) fix: count on both sides | Approved → building (Sonnet) |
| C14 | (a) brackets in every hover, app-wide | Approved → building (Sonnet) |
| C3 follow-up | rung 2 keeps all 24 keys | Approved (as built) |
| C23 | (a) close spacing at rung 1 for all five models | Approved → building (Opus) |
| C6 | Fable D1 (a) colours moved + function letters; D2 (a) shared red/green | Approved → building (Sonnet), Fable verify |
| C15 | (a) fix in 0.49 | Approved → building (Sonnet) |
| C16 | (a) fix in 0.49 | Approved → building (Sonnet) |
| C17 | closed by Fable D2 (a) | Approved |
| C18 | (a) honest gaps + search for real metal examples | Approved → building (Sonnet), IC after |
| C19 | (a) source more post-2015 songs in 0.49, IC after; Gotye restored to the minor-triad Australian slot (L104); Shape of You listening only | Approved → building (Sonnet) |
| C20 | (a) settle in the 0.49 source check | Approved → research (Sonnet), IC after |
| C21–C22 | (a) defer, no action (tags reference only, L94) | Deferred |
| C24 | (a) fix in 0.49 | Approved → building (Opus) |
| C25 | (a) re-voice with root or 5th doubled | Approved → building (Opus) |
| C26 | (a) defer to the 0.51 cadence ladder | Deferred |
| Tally | (b) build the link hidden; switch on when the URL arrives | Approved |

## New rows from IC_C18_C20_049 (21 Nov, independent check), status Drafted
| id | finding (evidence) | rule | proposed change | impact | regression test | pri | owner | status |
|---|---|---|---|---|---|---|---|---|
| C27 | "Nothing Else Matters" fills three Metal slots (minor, 7, add9) but is listed as soft rock / power ballad (Wikipedia; Louder: "metal power ballad") | L05 one per genre | Justin: keep (L104) | Song cards | content_lint slot honesty | Should | Justin | Closed: keep |
| C28 | Slot-honesty lint covers the Metal slot only; rock fillers in Blues/jazz (Learn to Fly sus2, Free Fallin' sus4) are not flagged | L05 honest gaps | Apply the check to every genre slot | Song cards | content_lint | Should | Sonnet | Drafted |
| C29 | 17 chord types have empty genre slots not declared as gaps, so no gap card shows | Honest gaps | Lint that every slot is filled or a declared gap; add the cards | Song cards | content_lint | Should | Sonnet | Drafted |
| C30 | Two Nothing Else Matters entries (minor, add9) rest on Hooktheory alone | Two sources or one authoritative | Find a second source or label honestly | Song cards | content_lint source rule | Could | Sonnet + IC | Drafted |

## New rows from IC_C_ENG_049 (21 Nov, independent check: C12 C23 C24 C25 all PASS), status Drafted
| id | finding (evidence) | rule | proposed change | impact | regression test | pri | owner | status |
|---|---|---|---|---|---|---|---|---|
| C31 | Rung 1 top line gives the answer away: final soprano note guesses perfect vs plagal 85% (65% before); soprano line +66 over chance; tenor–soprano gap +30. Cause is weighting (perfect ends so–so 73%, re–mi 1%), not the pool | Ladder rule: no tells (5 points) | Rebalance rung-1 weights so the top line and the outer-voice gap are spread evenly across answers as far as strict rules allow; report any residue the rules force | Ear Lab rung 1 | earlab_items_test K (soprano, gap) | Must | Opus | Approved (L108) → building (Opus) |
| C32 | Close/open boundary: app counts exactly an octave (S–T) as close; with "less than an octave" spacing predicts +6.1 | Ladder rule | Use "less than an octave" for close and balance | Ear Lab rung 1 | earlab_test C | Should | Opus | Approved (L108) → building (Opus) + research pass (Sonnet) |
| C33 | Rungs 2–3 older tells: spacing pattern +7.9 (rung 2), +15.0 (rung 3); final-chord completeness +9.3 (rung 3). Present on 049 before this work | Ladder rule | Rebalance (fix now) or with the 0.51 cadence ladder (with C26) | Ear Lab rungs 2–3 | earlab_test C | Should | Opus | Approved (L108) → building (Opus) |
| C34 | Rung 2: root-position IV, vi, III, VI with a doubled 3rd and no 5th mid-phrase (1.9% of items) | Strict SATB doubling (C25) | Extend the C25 rule to these | Ear Lab rung 2 | earlab_test doubling | Should | Opus | Approved (L108) → building (Opus) |
| C35 | Analysis reads 17 minor-key numerals by sound, not spelling (iv°, ii°7, V+, vii+ with C♭, D♯…): Ear Lab map right, Analysis wrong | Theory accuracy | Make Analysis check spelling; add the 17 to unit_test | Analysis colours | unit_test | Should | Opus | Approved (L108) → building (Opus) |

## New rows from FABLE_VERIFY_C6_049 (21 Nov; C6 SIGN OFF at ec50111), status Drafted
| id | finding | proposed change | pri | status |
|---|---|---|---|---|
| C36 | Function colour without the letter cue in places the C6 table missed: Gym progression cards and palette, Oracle cards, Keys chord and key chips | Add the letter cue there | Should | Drafted |
| C37 | Climb 6 grid at 1024 squeezed beside the wheel, 20 px past the card edge (pre-existing) | Re-flow at tablet width | Should | Drafted |
| C38 | Test robustness: terms_test needs a fresh page per Stage; earlab_ui_test detached-element flake | Fix the harness | Should | Drafted |
| C39 | Keys piano solfa names run together at 390 (pre-existing) | Spacing fix | Could | Drafted |
| C40 | Cadence chips say "T tonic" right above a legend that repeats it | Drop the duplicate | Could | Drafted |

## From the IC re-check of C31–C35 (21 Nov, IC_C_ENG_049 "Re-check", ed5495f: all five PASS, no Musts), status Drafted
| id | finding | proposed change | pri | status |
|---|---|---|---|---|
| C41 | Rung-1 top-line residue (+56 line, +20 last gap) is the floor only because rung 1 requires the leading note to rise in every voice. Allowing the textbook exception (inner-voice leading note falls to so in V–I, already allowed at rungs 2–3) gives +46.7 line, +2.8 last gap, register < 4 | Allow the exception at rung 1 and reword the rung-1 feedback sentence; or accept the residue in the log | Should | Drafted (needs Justin) |
| C42 | Exact pitches of a shared chord still just over 5: final I bass+soprano (perfect vs plagal) +6.9; exact V voicing (perfect vs interrupted) +5.8 | Cap in the weight solver | Should | Drafted |
| C43 | Rungs 2–3 last-chord soprano and S–T gap tells about +20 to +26 (outside C33's scope) | Balance with the solver | Should | Drafted |
