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

Deferred: R19–R22 (counterpoint) — Justin 20 Nov "later".
