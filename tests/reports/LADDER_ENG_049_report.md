# LADDER_ENG_049: Ear Lab ladders, engine build report

Opus engine builder, 21 Nov 2026. Branch `049-ladder-eng` (worktree `/home/claude/wt/ladder-eng`, from `origin/049` at 7b0b947). Not pushed, not merged.
Spec: `tests/reports/ladder_049/LADDER_REGISTER_049.md` (section 8: Justin's answers, L101–L104) and its reference model `ladder_proto.py`.
API for the Sonnet implementer: `tests/reports/ladder_049/ENGINE_API.md`.

All checks below are the build's own (**self-check**); none is an independent check. The M12 excerpt list and the M11 harmony need the
independent theory check before release.

## 1. What is built (engine only)

One block in `index.html` (`EAR LAB LADDERS 0.49 · ENGINE` … `END EAR LAB LADDERS ENGINE`), wired into the existing Ear Lab:

| area | built |
|---|---|
| units | rule U: 420 ticks a crotchet; one cell table `LCELL` (all cells of R1–R10 and the melody rhythms, with ties, tuplet groups, the anticipation over the barline) |
| melody generators | `ladGenMel(l)` M1–M12: M1 as built; M2–M11 per the register (rule N 2/3, MK keys by Stage, MR1 do = 60 + pc, MR2 G3–B5, tempo 72–96, MU1 data), D5 (fa–si once, flagged `aug2`), D6 (3rds–6ths and octave from any note, tritone only f–t resolving, no 7ths), D7 (modal cue, mode name), D8 (all four modulation kinds; both readings; pivot window), D9 (anacrusis; last bar shortened), M10 chromatic insertion, M11 bass, M12 curated excerpts |
| rhythm generators | `ladGenRhy(l)` R1–R10: RF fill rules; R1 one bar, 99 items, no repeat within 30 (D1); R2–R9 per the register incl. 12/8, anacrusis, swing, backbeat context (D14), tresillo, Charleston, 5/4 and 7/8 groupings, quintuplets and septuplets in 4/4 and 5/4 (one a bar at most); R10 kick/snare + riff |
| marking | `ladMelMark` (D4: right only when every note's pitch and rhythm are right; per-note detail; Nearly only for the M10 spelling; M9 by sound, pivot only under Move do; M11 per part), `ladRhyMark` (D11 tied syncopation, R8 swing, R9 septuplet grouping as the only Nearly cases; per-beat ticks; R10 per part) |
| entry API (L103) | `ladPalette` (legal lengths at the current position: bar fit, the rung's beat grouping, rests, anacrusis, short last bar), `ladBeams`, `ladEntriesToLine`, `ladTruthEntries`, names for the reveal (`ladMelNames`, `ladRhyNames`) |
| readiness (D10) | `ladRdPush` / `ladRdState`; `earMark` records answered items only (mel, rhy) in `EAR.rd`, saved |
| settings | `EAR.names` ('k' / 'kk', D12), `EAR.mod` ('home' / 'move', D8), saved in `cjg_ear` |
| names | `RHYNAMES = LADNAMES` (approved 0.48 names unchanged, 21:24 extension, D12: 5- and 7-tuplets konnakol in both settings; triplet tri-o-la / ta-ki-ta) |
| playback | `ladSched*`: key cue (mode's tonic triad at do = 60 + pc), count-in bar with the anacrusis on its own beat, ticks, tuplet group accents +3 dB, swing 2:1, backbeat context, R10 drums and riff, M11 bass samples, M12 melody alone / with the accompaniment |
| Stage table | `EARSTAGE.mel = [4,4,4,4,5,5,5,5,6,6,6,6]`, `.rhy = [4,4,4,5,5,5,5,6,6,6]`; `earRungs(d)` replaces the hard-coded `[1,2,3]` in `earRungsShown` / `earHidden`; the rung strip sorts numerically; rhythm EDR tag 4–6. Saved `EAR.lvl` keep their numbers (register 0.3) |
| data | `LADM12` (46 excerpts, section 4), `LADREC` (D13 structure, empty pending the recordings check) |
| compatibility | the 0.48 desks still render every rung without page errors: `RCELL` gains every new cell, `ESOL` the chromatic syllables, `ELCN`/`ELW` the new cells, `elTitle()` for tile titles; `earCells(l)` = `ladRhyTiles(l)` |

Not touched: the other drills (cadences, bass, quality, metre, blind analysis) and their generators, `earDo`, `earKeyCue`, CKEYS2.

## 2. Commits

| commit | stage |
|---|---|
| `35dec2a` | 0.49 ladders engine: melody M1-M12 and rhythm R1-R10 generators, marking, readiness, settings, playback; M12 curated excerpts |
| `8e35246` | 0.49 ladders: palette fixes (RF last bar, M11 bass lengths), ladTruthEntries, M12 picks 46 (barline ties cut, transposition-free dedup) |
| `71ba2b2` | 0.49 ladders: earlab_test section L (self-checks ported from the reference model), items test Stage table, ENGINE_API.md, R10 marking fix |
| `26c2624` | 0.49 ladders: earMark readiness line fix; earlab_test L tells baseline includes the shown anacrusis (D9) |
| `08cbaf4` | 0.49 ladders: rung strip in numeric order, show-all test against the drill's rung count |
| (this commit) | build report |

## 3. Counts against the reference model's targets

Pools: distinct items in 20,000 draws (node run of the app's own engine block, seed 7; the reference model's numbers from `proto_output.txt`).
Shares, ranges and tells: `earlab_test` section L, 5,000 seeded items a rung (self-check).

| rung | pool 20k (target) | new share (0.60–0.73) | MIDI (55–83) | tells checked / failed |
|---|---|---|---|---|
| M1 | 256 (256; exact 274) | – | 60–77 | 25 / 0 |
| M2 | 1,090 (1,091) | 0.661 | 55–79 | 30 / 0 |
| M3 | 10,984 (10,948) | 0.671 | 55–82 | 30 / 0 |
| M4 | 15,383 (15,334) | 0.665 | 55–82 | 41 / 0 |
| M5 | 17,288 (17,348) | 0.657 | 55–82 | 41 / 0 |
| M6 | 19,999 (20,000) | 0.676 | 55–82 | 41 / 0 |
| M7 | 20,000 (20,000) | 0.677 | 55–79 | 41 / 0 |
| M8 | 20,000 (20,000) | 0.662 | 55–82 | 41 / 0 |
| M9 | 20,000 (20,000) | 0.664 | 55–83 | 41 / 0 |
| M10 | 20,000 (20,000) | 0.679 | 55–83 | 41 / 0 |
| M11 | 20,000 (20,000) | 0.672 | 55–83 | 45 / 0 (incl. bass first / last note) |
| M12 | 46 curated (40–60) | – | score register | – |
| R1 | **99 (99)**; no repeat within 30 in 3,000 draws | – | – | 11 / 0 |
| R2 | 2,853 (5,658) | 0.669 | – | 15 / 0 |
| R3 | 7,565 (7,649) | 0.683 | – | 15 / 0 |
| R4 | 12,509 (12,311) | 0.661 | – | 15 / 0 |
| R5 | 7,137 (6,981) | 0.663 | – | 15 / 0 |
| R6 | 13,894 (13,795) | 0.664 | – | 15 / 0 |
| R7 | 15,875 (16,589) | 0.657 | – | 15 / 0 |
| R8 | 18,951 (18,935) | 0.667 | – | 15 / 0 |
| R9 | 19,997 (19,989) | 0.655 | – | 19 / 0 (incl. tuplet presence) |
| R10 | 19,997 (4,096 drum parts × riffs) | – | – | 15 / 0 (incl. kick density) |

R2 is lower than the model because the model counted the new metres (2/4, 3/4) as R2's new thing, against the register's own text ("the new
metres are on screen, so they are not a hidden new thing"); the build follows the register (2/3 of items hold a semibreve or dotted minim).
Still 28 times the floor.

## 4. Tests run (one at a time, after the last engine change unless noted)

| suite | result | checks |
|---|---|---|
| `earlab_test` | **pass, 0 failures** (3 m 45 s, rerun after the last change) | 118 count keys; section L (new, all self-check): 22 rungs × pools, shares, ranges; 567 tell checks at 5,000 items a rung; 8,000 melody and 15,000 rhythm items against RF and the anacrusis rule; 5,000 M7 items for D5; 2,000 M9 items (both readings, pivot names, window re-derived); **2,000 M11 items through an independent outer-voice checker (music21 chords)**; 1,800 melody answers marked right and 1,800 with one wrong pitch marked wrong; 50/50 M10 enharmonic spellings Nearly; M9 pivot only under Move do; rhythm Nearly cases (D11, R8, R9); R10 per part; D10 readiness; beaming; the palette walks every right answer of 1,800 items (both parts at M11); 22 rungs rendered offline; 203 name checks |
| `earlab_items_test` | **pass, 0 failures** (5 m 27 s) | 96 count keys; section U updated for the 12 / 10-rung Stage table (every rung at Stages 4, 5, 6 rendered, answered or shown, no page errors) |
| `unit_test` | **pass** | 959 checks |
| `content_lint` | **pass** | – |

Not run (not asked; may need updating by the UI build): `earlab_ui_test` (rhythm desk at 16 units a bar), `earlab_r2_test`, `sound_test`, `transport_test`.

## 5. Where the build departs from the reference model (deliberately)

1. **The last bar is shortened by the anacrusis** (register M6/R7, D9). The model added the upbeat note without shortening. Melody ending figures for a short
   last bar: 4/4 − crotchet = dotted minim (RF: no minim across the bar's middle), 4/4 − quaver = X X dotted crotchet, 3/4 = minim or X crotchet / X dotted
   crotchet, 2/4 = crotchet / dotted crotchet, 6/8 = X + crotchet. A rhythm line with a quaver upbeat ends its short last bar on a quaver. Because the outline
   shows the short bar, the rhythm tell baseline is (metre, anacrusis); with metre alone, "anacrusis → last cell" reads 30% against 20% (R7) and 22% against
   15% (R8): a consequence of D9, not hidden information.
2. **M10 insertions split the right note** (the crotchet before the chromatic note; in 6/8 the crotchet of ta-ti or a dotted crotchet). The model split random
   crotchets, so the chromatic note's rhythm did not belong to it.
3. **M9 review items do not modulate** (rule N: 1/3 review in the same 8-bar format). The model labelled a third "not new" but modulated every item.
   Phrase 1 is the first four bars (the model split by note count), and the join into phrase 2 must be a singable move.
4. **M11 new thing** = first inversions, ii (ii°6) and vi (VI); review items use root-position I IV V (i iv V) only. The model's bass was a placeholder.
5. **Interval quality**: every leap is a major / minor / perfect 3rd–6th or octave; the only augmented or diminished intervals are f–t (resolving, D6) and
   fa–si as a step (D5). The model allowed e.g. do–si (augmented 5th) in harmonic minor.
6. **Anticipation into the next bar** (R6: a quaver on 4& tied over the barline, cell `antB`) is generated; the model's fill could never place it.
7. **7/8 groups use real cells** (2: ti-ti, ta, ti sa, sa ti; 3: ti-ti-ti, tam, ta ti, ti ta); the model used placeholder tokens.

## 6. Not done, open or uncertain

* **The climb-2 checker (`c2Check`) is not reused** for M11: it is a first-to-fifth-species modal checker (cantus, species layouts, modal cadence) and reports
  species dissonance and spacing rules on any tonal bass. The engine has its own outer-voice checker (`ladOuterCheck`: parallels, direct 5ths/octaves with a
  soprano leap, crossing, leading note in the bass rises, bass leaps) and `earlab_test` L8 re-checks 2,000 items with an independent Python checker.
* **M12 (46 excerpts) needs the independent theory check** (section 7 table). Notes: The Entertainer gives none (its syncopations are ties across the beat,
  which the palette does not offer); Maple Leaf gives 4. 25 of 46 use semiquavers or dotted quavers (beyond the generated rungs' rhythm); k331d excerpts
  reach 24 notes of semiquavers. The piano top lines are the highest note at each onset (chord tops): checked by ear only through the solfa. Chorale phrases
  that tonicise (e.g. the C major phrase of BWV 269) are written in the home key's solfa (fi, te). Keys come from meta.json (score key or the section's key
  text), not the scan's automatic keys. Picks out by hand are listed in `m12_curate.py` (`PICK_OUT`: recapitulation transpositions, repeats, a broken-octave
  figure).
* **Contemporary items (M12 recordings, R10 grooves)**: `LADREC` holds the D13 data structure, empty pending the recordings check.
* **Names not in the approved table**, used only where the engine needs a label: `antB` "ti ti-" with the next note held as "i…" (tie rule); `trq`
  (triplet crotchet–quaver, only ever an answer for the swing Nearly case) "ta ti (triplet)"; `e` / `qd` / `cq` single values ti / tam / ta (anacrusis and
  short last bars). To confirm with Justin.
* **The 0.48 desks** still do the entry for rungs 4+: the melody desk enters crotchets only, so rung 4+ answers through it are marked wrong (no durations);
  the rhythm desk counts 16 semiquavers a bar, so 3/4, 6/8 and 7/8 answers cannot be completed there. "Show me" works at every rung. These are for the UI build.
* **Speed**: M11 takes 10–25 ms an item (the bass search), M7 about 5 ms; fine for one question, it is what makes section L about 4 minutes.
* Readiness is recorded for melody and rhythm only; the other drills' records are unchanged.
* Rhythm tempo counts crotchets in every metre (a 6/8 dotted-crotchet beat runs at 2/3 of the drawn tempo), as in the model's playing-time tells.
* `EAR.pivot` (the student's "Mutation here" note) has to be set by the UI; `earCheck` reads it.

## 7. M12 excerpts (data table; each needs the independent theory check)

| # | id | score | bars | key | metre | rung level (pitch) | semiquavers / dotted quavers | notes | solfa (do from the key signature; la-based minor) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | chorale_upbeat-4 | chorale | upbeat-4 | G major | 3/4 | 6 |  | 10 | d d s m r d d r m r |
| 2 | chorale_4-7 | chorale | 4-7 | G major | 3/4 | 6 |  | 6 | m s f m r d |
| 3 | chorale_upbeat-10 | chorale | upbeat-10 | G major | 3/4 | 6 |  | 8 | m m f s s f m r |
| 4 | chorale_10-14 | chorale | 10-14 | G major | 3/4 | 6 |  | 7 | d m f s f m d |
| 5 | chorale_14-18 | chorale | 14-18 | G major | 3/4 | 6 |  | 9 | m s f m r d r m r |
| 6 | ohaupt_upbeat-2 | ohaupt | upbeat-2 | D major | 4/4 | 6 |  | 7 | m l s f m r m |
| 7 | ohaupt_2-4 | ohaupt | 2-4 | D major | 4/4 | 6 |  | 7 | t d' d' t l t l |
| 8 | ohaupt_upbeat-6 | ohaupt | upbeat-6 | D major | 4/4 | 6 |  | 8 | d' t l s l t d' d' |
| 9 | ohaupt_6-8 | ohaupt | 6-8 | D major | 4/4 | 6 |  | 6 | s l s f f m |
| 10 | ohaupt_8-10 | ohaupt | 8-10 | D major | 4/4 | 6 |  | 8 | d' t d' r' d' t l t |
| 11 | ohaupt_10-12 | ohaupt | 10-12 | D major | 4/4 | 6 |  | 6 | m f m r s m |
| 12 | jesu_1-2 | jesu | 1-2 | E minor | 4/4 | 6 |  | 6 | m m r d t, l, |
| 13 | jesu_3-4 | jesu | 3-4 | E minor | 4/4 | 7 |  | 6 | m m fi si l si |
| 14 | jesu_5-6 | jesu | 5-6 | E minor | 4/4 | 6 |  | 5 | l d' t l l |
| 15 | jesu_7-8 | jesu | 7-8 | E minor | 4/4 | 6 |  | 7 | m m f m r d d |
| 16 | jesu_9-11 | jesu | 9-11 | E minor | 4/4 | 7 |  | 8 | m fi s m l s fi m |
| 17 | k545_1-4 | k545 | 1-4 | C major | 4/4 | 6 | yes | 15 | d' m' s' t d' r' d' l' s' d'' s' f' m' f' m' |
| 18 | k545_18-19 | k545 | 18-19 | G major | 4/4 | 6 | yes | 16 | s' s' m' d' l l d' l f' f' r' t s s t s |
| 19 | k545_20-21 | k545 | 20-21 | G major | 4/4 | 6 | yes | 16 | m' m' d' l f f l f r' r' t s m d' s m |
| 20 | k545_24-25 | k545 | 24-25 | G major | 4/4 | 6 | yes | 8 | m' d' s' f' m' r' d' r' |
| 21 | k545_50-53 | k545 | 50-53 | C major | 4/4 | 4 |  | 8 | l' l' s' s' f' f' m' m' |
| 22 | k545_56-57 | k545 | 56-57 | C major | 4/4 | 4 |  | 11 | t s' m' d' r' s' m' d' r' s' s |
| 23 | k545_69-70 | k545 | 69-70 | C major | 4/4 | 6 | yes | 16 | s' l' t' d'' r'' m'' r'' d'' t' l' s' f' m' r' d' r' |
| 24 | k331a_1-4 | k331a | 1-4 | A major | 6/8 | 6 | yes | 19 | m f m s s r m r f f d d r r m s f m r |
| 25 | k331a_5-8 | k331a | 5-8 | A major | 6/8 | 6 | yes | 17 | m f m s s r m r f f d r m f m r d |
| 26 | k331a_9-12 | k331a | 9-12 | A major | 6/8 | 6 | yes | 22 | s l s l l d' t l l s s s m d s f r s m d m r |
| 27 | k331a_15-16 | k331a | 15-16 | A major | 6/8 | 6 |  | 8 | d r m f m r r m |
| 28 | k331d_3-4 | k331d | 3-4 | A minor | 6/8 | 10 | yes | 20 | l m' ri' m' d' l si m' f' m' r' t t l si l t d' d' t |
| 29 | k331d_7-8 | k331d | 7-8 | A minor | 6/8 | 10 | yes | 19 | l' si' l' d'' t' r'' d'' t' d'' m'' r'' f'' m'' ri'' m'' m' fi' si' l' |
| 30 | k331d_9-10 | k331d | 9-10 | A minor | 6/8 | 10 | yes | 24 | l si l l' si' s' s' f' m' f' m' f' l' si' l' si' l' f' f' m' ri' m' ri' m' |
| 31 | k331d_11-12 | k331d | 11-12 | A minor | 6/8 | 7 | yes | 20 | m' r' d' t l m' f' r' t l si t t l d' t r' d' d' t |
| 32 | k331d_15-16 | k331d | 15-16 | A minor | 6/8 | 10 | yes | 24 | l si l d' t r' d' t d' m' r' f' m' ri' m' m fi si l si l m d m |
| 33 | maple_11-12 | maple | 11-12 | A♭ major | 2/4 | 10 | yes | 11 | r' me' d' r' m' d' m' d' r' d' d' |
| 34 | maple_15-16 | maple | 15-16 | A♭ major | 2/4 | 10 | yes | 10 | r me d r m d m d r d |
| 35 | maple_30-33 | maple | 30-33 | A♭ major | 2/4 | 10 | yes | 20 | l, di m l m ra l, l, r f l f m m r s, d s s s |
| 36 | maple_82-83 | maple | 82-83 | A♭ major | 2/4 | 6 | yes | 9 | r m d r s, d s s s |
| 37 | chopin7_upbeat-2 | chopin7 | upbeat-2 | A major | 3/4 | 6 | yes | 6 | s, m f r r r |
| 38 | chopin7_2-4 | chopin7 | 2-4 | A major | 3/4 | 10 | yes | 6 | l fi s d' d' d' |
| 39 | chopin7_4-5 | chopin7 | 4-5 | A major | 3/4 | 10 | yes | 5 | m di r f f |
| 40 | chopin7_6-8 | chopin7 | 6-8 | A major | 3/4 | 6 | yes | 6 | t, t, d m m m |
| 41 | chopin7_10-12 | chopin7 | 10-12 | A major | 3/4 | 6 | yes | 6 | l f s m' m' m' |
| 42 | chopin7_14-15 | chopin7 | 14-15 | A major | 3/4 | 6 | yes | 5 | t, r d d' d' |
| 43 | chopin20_1-2 | chopin20 | 1-2 | C minor | 4/4 | 10 | yes | 10 | m f m r d d r d te, l, |
| 44 | chopin20_3-4 | chopin20 | 3-4 | C minor | 4/4 | 10 | yes | 10 | t, di m r ra t, m si f m |
| 45 | chopin20_5-8 | chopin20 | 5-8 | C minor | 4/4 | 10 | yes | 20 | d' d' t ri t l t si fi m l f m r d d r d t, l, |
| 46 | chopin20_11-12 | chopin20 | 11-12 | C minor | 4/4 | 6 | yes | 10 | l f m r d d r d t, l, |

---

## After IC_LADDER_ENG (independent check e387974: FAIL on items 1, 2, 3, 5)

All 12 Musts and all 8 Shoulds fixed as deviations from the approved register and decisions; no new decisions taken. Commits after e387974:
`5f8cd97` engine fixes · `2a9f869` M12 · `9e9872f` follow-ups, regression section L15, ENGINE_API · `22e65be` R9 tuplets under a tie · `bc19645` M9 Keep home do, M12 line end ·
`3223fa0` M12 answer end · `6ed7af8` palette grammar · `2ef4505` test fixes.

| IC item | fix | regression check (earlab_test, all self-check) |
|---|---|---|
| M-1 M7 melodic si | fa and so are raised only when rising by step (f→fi→si→l); natural fa and so only fall or repeat; si always to la by step | L15: every si → la and fi → si by step in 3,000 M7 items |
| M-2 M8 kinds | the variant is drawn once per item (redraws keep it), so Dorian, Mixolydian, te, fi are a quarter each | L15: each kind 0.20–0.30 of the new items |
| M-3 M11 consecutives | `ladOuterCheck` also judges the melody note sounding just before each bass change against the bass change (consecutive and direct 5ths / 8ves); the line is redrawn when the note before the final V–I is V's root | L8: 11,628 bass changes in 2,000 items through the independent checker, 0 consecutives |
| M-4 R6 anticipation of beat 3 | `antA` ("ti ti-i") allowed at beat 2 of 4/4 (its tie shows the bar middle) | L15: generated (≥ 50 in 3,000 R6 items), only at beat 2 of 4/4 |
| M-5 tie-in names | a note tied in over the barline is held on the vowel ("-i", one per syllable it would have had); the cell's other notes keep their own syllables: ta-a → "-i-i", tika-tika → "-i-ka-ti-ka", tika-ti → "-i-ka-ti" (`LSYLG`, `ladTiedName`). A tuplet never starts under such a tie (its accent would be lost) | L15: names for nine cells against the rule |
| `trq` label | "tri-i-la" (Kodály), "ta-a-ta" (konnakol): tri-o-la with the first two notes tied, held on the vowel; documented in ENGINE_API | L0 |
| M-6 M9 Move do | entries after the marked mutation are read against the new do (old do + 7, the frame of `readings.move`), the pivot in either key; under Keep home do a note in the new key's syllables after the true pivot is the same sound and right too | L9: home and move readings right, pivot required under Move do (dominant kinds, 193 items) |
| M-7 M9 relative kinds | no mutation in a relative modulation: right with none marked; a needless mark with every note right is right with the L107 sentence (`note`); minor → relative major window uses the harmonic minor as the old key, so the major's so is the new note | L9 (194 relative items); L7 re-derives the window (all 501 m-III windows now narrower than the item) |
| M-8 5/4, 7/8 | `ladRhyLegal`: 5/4 fills each group as a 3/4 / 2/4 half; 7/8 one group cell per group | L15: ti-ti written as two quavers is never right (300 items) |
| M-9 false Nearly | Nearly only when the register's case is the only difference, cell for cell at the same place | L15: the syn-co-pa Nearly with any other error is wrong |
| M-10 palette | the grammar is every legal RF filling of the bar (inner bars from the rung's cells, the last bar with its extra values, the upbeat bar; M11 bass: minims, crotchets, dotted minim in 3/4, never a dotted crotchet; M11 upbeats are crotchets) | L15: 1,350 random walks always reach a full line; no dotted minim inside 4/4, no dotted crotchet at M4–M5, no minim in 6/8, no dotted crotchet or rest in the bass |
| M-11, M-12 M12 | `k545_50-53` out; an inner voice under a held top note is skipped (chopin20_5-8 holds D5); chromatic syllables from the score's own letters (chopin20_3-4 "di"); credits: composer in full, the work, encoder and licence | L15: table, credits, chopin20 spellings |
| S1 M9 | kind drawn once; phrase 2 placed with the new do a 5th above or a 4th below, whichever keeps s,..d' (no range rejections, so keys even) | L15: kinds 0.20–0.30, no note outside s,..d', key counts within sampling noise |
| S2 M10 | no lower neighbour below s, | L15 |
| S3 M11 | a new item must hold an inversion, ii or vi | L15: content share ≥ 0.60 |
| S4 R7, R8 | the new thing is hidden content only (R7 triplet, tim-ka; R8 tresillo, Charleston, swing) | L15: hidden share ≥ 0.60 (R7 0.665, R8 0.664 in L3) |
| S5 swing | every off-beat quaver point is moved to two thirds of the beat (onsets and ends) | L15: 40 swing items rendered, every note at its swung place |
| S6–S8 M12 | spellings from the score; levels by the register's material (jesu 1-2 → 5, k545_56-57 → 6 …); D9 outlines (every bar full, the last shortened by the upbeat; a phrase that ends earlier finishes with rests; excerpts that cannot meet D9 dropped) | L15: every outline is D9 |

**M12 now holds 40 excerpts** (40–60 asked): the D9 outline rule removed most Maple Leaf windows (their 7-semiquaver upbeats leave last bars too long) and two Chopin 7 phrases. The list is in `m12_excerpts.json` / `m12_curate.py --js`.

### The checker's scripts, re-run on this build (copies in /tmp/lad/ic, 5,000 items a rung)

| script | result |
|---|---|
| `check_mel.py` | 5,439,325 checks; 1 failing key: the M9 pivot window, 810 items: all minor → relative-major items, where the script still uses the old window (whole item) that M-7 asked to fix |
| `check_rhy.py` | 1,942,063 checks; R7 and R8 "new flag" and share: the script counts 12/8, anacrusis and backbeat as new, which S4 asked to stop. Tuplet accents: 0 failures after `22e65be` |
| `mark.py` (148 kinds) | all match except "Charleston written tam-ti + two crotchet rests" (marked wrong: rest onsets count, as the register defines the sound; the checker's own Coulds note this) |
| `pal_check.py` | 0 illegal offers, 0 legal lengths blocked, no dead ends, M1–M11 |
| `m12_check.py` | chopin20_5-8: the script's top line still takes the alto F♯ (the change it recommended); jesu_9-11: the D9 rest after the fermata spans the next phrase's opening notes in the source |

Note: my first runs of the checker's scripts wrote into `/home/claude/scratch_ic/` (absolute paths in the scripts). I restored the checker's original output files there from my copy taken before the runs (file times are not the originals) and pointed my copies at `/tmp/lad/icout/`.

### Suites (one at a time, after the last change)

| suite | result |
|---|---|
| `earlab_test` | pass, 0 failures, 125 count keys (section L incl. the new L15 regressions) |
| `earlab_items_test` | pass, 0 failures, 96 count keys |
| `unit_test` | pass, 959 checks |
| `content_lint` | pass |

### Still open
* Tie-in names: the coordinator's note said "a held minim stays -a"; I followed the stated rule "held on the vowel of the first note", so a tied-in minim is "-i-i". If "-i-a" was meant, it is one line in `ladTiedName`.
* Charleston as tam-ti + two crotchet rests stays wrong (register sound definition); the feedback could say so.
* M12 has 40 excerpts and no Entertainer or Maple Leaf beyond one; every excerpt still needs the independent theory check.
