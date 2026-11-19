# Ear Lab 0.48: teaching-text fixes from the independent check (IC_EAR_048 S4, S5, S6, C1, C4)

Branch `048-eartext` (from 048-int 11799b6). Single file `index.html`; tests in `tests/earlab_items_test.py` (new sections B and T2,
extended P, S, Q and I). Builder: Opus. Not touched: voice leading and realisation (S1 to S3, for Justin), the metre answer grid (M1,
another branch), the grid markup and CSS.

## Finding to change to test

| Finding | Change in `index.html` | Test that would have caught it | Result |
|---|---|---|---|
| S4: the cadential 6/4 chip inside "the cadence" bracket read "bass so" / "bass mi" | `earChordRowHTML`: a 6/4 followed by V reads "cadential 6/4" wherever it is (in or before the bracket); its bass solfa moves to the title, which still gives both readings (tonic in second inversion, Ic, as Analysis labels it; part of the dominant, as many harmony texts hear it) | P: every 6/4-then-V chip at rungs 1 to 3 (944) reads "cadential 6/4", title has "second inversion", "Ic"/"ic", "part of the dominant" and "(bass so)" / "(bass mi)". S: the rung 3 chip in the bracket, major and minor | pass. On 11799b6: 691 bracket chips fail (345 "bass mi", 346 "bass so") |
| S5: blind analysis said "the leading note rises to the home note" (false for chorale bar 14 and Jesu bar 6) and "V to I" for four minor V–i excerpts | new `earBlindTxt` (blind items only; `earTeachCad` calls it when `q.d==='blind'`). Nothing is said about a single voice. The numerals are the excerpt's own (`meta.json` "ch", figures set as ⁶₄ ⁶₅ ⁶), so V–i says "V7 – i"; the key it cadences in comes from its label ("for a moment the music is in C major (a tonicisation)"); a minor-key excerpt ending on I says "made major (a Picardy third)"; "the bass lands on its root" | B (new): 30 excerpts x every option (90 sentences): no "leading note"; no "V to I" unless the last chord is I; no "I" in a minor V–i excerpt; the last chord named; the tonicised key named exactly when the label gives one; Picardy only for a minor key ending on I; for all 18 perfect excerpts the lowest note sounding at the arrival (`meta.json` events) is the root of the last chord (music21 RomanNumeral in the excerpt's key) | pass. On 11799b6: fails (leading note, V to I on V–i and on V7/IV–IV, tonicised key not named) |
| S6: "You heard six quavers in every bar" (split clicks sound 75% of the time) | "Each bar holds six quavers, and so does a bar of {given}: that much is right." The same problem in two more sentences: "You heard each beat split in two" -> "You heard the beats split in two"; "listen inside one beat: it splits in three" -> "listen inside the beats: where a beat splits, it splits in three" (two places). The metric definitions ("two beats in a bar, each one splitting in three") are kept as statements about the metre | T2 (new): 1,800 items x every option (12,000 sentences); any "You heard ... every/each bar/beat/one" or "inside one beat: it splits" fails unless every split click in the item sounded | pass. On 11799b6: 334 "six quavers in every bar", 2,459 "each beat", 5,185 "inside one beat" |
| C1: "stays on it" where the 6/4 bass drops an octave into V | `earCadFacts` gets the bass move from the 6/4 into V; the sentences say "stays on so" (mi in minor, la-based) and add ", dropping an octave into V" (or rising) when the pitch changes. Cadence right/shown and wrong-answer (answer cadential 6/4) sentences. "the bass is already on the dominant" (Nearly text) is true of the degree and is kept | P: any "stays on it" fails; "stays on so/mi" must match the actual 6/4 -> V bass move (0, -12, +12) | pass: 8,292 sentences checked, 96 say the octave move. On 11799b6: 8,292 "stays on it" |
| C4: dead `earAnsTxt` with stale cadence text | removed `earAnsTxt`, `CADFAM` (its stale "decorated approach to V in a perfect or imperfect cadence" text), and the then-unused `CADL3`, `QINV`. `grep` finds no caller in `index.html` | the four test sites that called `earAnsTxt` now read the live result panel: Q (chord quality text from `earTeachQual`), S (family text answered with the family, Nearly off; Phrygian solfa "fa to mi"; 6/4 chip solfa in the title), I (interrupted-after-6/4 shown text and the plain interrupted text from `earTeachCad`) | pass |
| C3: "Shown" uses the same gold as "Nearly" | not changed (design) | | listed below |

## Self-checks

- Ran the new `earlab_items_test.py` against the base commit (11799b6, a detached worktree outside the branch): it fails P (6/4 chips,
  "stays on it"), S (6/4 chip solfa), B (25+ blind sentences) and T2 (three sentence types), so each new check catches its finding.
- Every blind sentence read by eye for all 30 excerpts (the dump is the same as section B's). Tonicisations: chorale bar 14 V7/IV–IV
  (C major), O Haupt bar 4 V(7)/vi–vi (B minor), Jesu bar 8 VII–III (G major: VII in E minor is V of G); O Haupt bar 8 ii⁶–V/ii, an
  imperfect cadence in E minor, now says "it stops on V/ii, the dominant of E minor". Jesu bar 13 V(7)–I in E minor: "made major (a
  Picardy third)". K331 finale bars 8 and 18 read "i⁶₄ – V – i".
- The S6 sentence for 3/4 given 6/8: "Each bar holds six quavers, and so does a bar of 6/8: that much is right. In 6/8 they fall in
  threes, making two beats. Here they fall in twos, so there are three beats in a bar."
- `terms_test` was run alone, after the other suites.

## Suites

| Suite | Result |
|---|---|
| earlab_items_test | pass, 0 failures (P 76,506 sentences + 944 chips, B 90 sentences + 18 bass checks, T2 12,000 sentences) |
| earlab_ui_test | pass, 467 checks |
| earlab_r2_test | pass, 1,666 checks |
| earlab_test | 1 failure, the same as on 11799b6: the known rung 1 register tell ("lowest and highest note (6-semitone bands) 32% vs chance 26%") |
| terms_test (alone) | pass, 0 failures |
| unit_test | pass, 640 checks |
| content_lint | pass |

## Open (for Justin)

1. S1 to S3 (rung 2 and bass-drill strict rules, ii⁶–IV) were not touched, as asked.
2. C3: "Shown" and "Nearly" share the gold border; left as design.
3. EL-6 said the augmented and diminished 7th answers "say the chord is symmetrical". That sentence (`QSYM`) was only ever shown by the
   removed, never-called `earAnsTxt`; the live result panel omits "root position" for these chords but does not say "symmetrical".
   The Q check now tests the live panel (no inversion or root position named). Adding the `QSYM` sentence to the panel is a small
   text change if wanted.
4. Blind "the bass lands on its root" is checked against the score data in the test; if a blind excerpt is added whose bass arrives
   on another chord note, section B fails and the sentence must change.
5. Metre: a beat is heard split "where a beat splits"; the chance that no split sounds at all in an item is about 0.25^8 for 2/4
   (negligible), so "You heard the beats split in two" is kept.
6. C2, C5, C6 of the check were outside this brief and are unchanged.
