# IC_REG_049: independent check of the 0.49 register fixes C3, C4, C7, C8, C9, C11

Checker: independent (did not build any of this). Branch `049-ic-reg` at `93bf5ce`. I worked from the spec in REGISTER_049.md, the code and the running app (headless Chrome, the repo harness). I read the builder reports (C_THEORY_049, C_CONTENT_049) only after my verdicts were set. I fixed nothing.

## Verdicts

| item | verdict | one-line evidence |
|---|---|---|
| C3 rungs 2–3 register tells; strict voice leading; rung 2 on 24 keys | **PASS** (2 Shoulds) | Exact lowest+highest pair, held out, with mode: rung 2 **+14.1 → +0.1** points, rung 3 **+16.8 → +4.8** (same probe on the pre-fix app, then 0.49). 0 voice-leading (motion) faults in all 4,966 distinct realisations. Rung 2 draws 12 major + 12 minor keys. |
| C4 rung 1 V–vi maximum is 28 | **PASS** | My own enumeration (no app code) finds 28 in the twelve keys. It is the same set as the app's `earR1Pool`, and all 28 are drawn. The builder's "108 with close spacing" also checks out: 28 open + 58 close + 22 mixed. |
| C7 counterpoint wording | **PASS** (1 Could) | `c2IvA` matches music21 on all doubly and triply altered names (30,625 pairs, ♭♭ to ♯♯). Over 52,535 checker messages there were 0 "Bars N–N", 0 "altered", 0 bare "15th". S3d wording is right by species. The diff changes only message text: no rule, condition or severity. |
| C8 aug / dim7 sentences | **PASS** | Each sentence checked and true (details below). |
| C9 Ear Lab function map | **PASS** | `earNumFn` equals Analysis `analyse().f` for minor v, v7, VII, VII7 (MD), and for borrowed v, v7, ♭VII, ♭VII7 in major (MD, MD_MAJOR on), in all 24 keys. V, V7, vii°, vii°7 stay D. Every call passes the mode. |
| C11 Dance Monkey | **PASS** | Two independent non-lyric chord sources (Hooktheory, Skoove) agree on F♯ minor and on F♯m, D and E being in the loop. Wikipedia confirms 10 May 2019 and that Tones and I is Australian. The card names only the chords both sources agree on. No ⚠, correctly. |

**Musts: none.**

Suites, run once each on this branch: earlab_test 0 failures (147 s); counterpoint_test 0 failures (192 s); unit_test 959 checks, 0 failures (13 s).

## Evidence

### C3

**Method.** `dump_cad23.py` reads, from the app, every weighted rung 2 entry (9,600) and rung 3 entry (6,600), with the realisation `earCadM` gives each one. It also draws a seeded sample of 12,000 real questions per rung with `earGen('cad', l)`, using a different RNG and seed from the suites.

`tells_cad23.py` measures each tell two ways:
- **Exact:** the advantage of someone who has memorised the whole weighted table. Answers are uniform within a mode, so this is the best possible accuracy from mode + feature, minus chance.
- **Held out:** a lookup table is learned on half the sample and scored on the other half.

`baseline_cad23.py` runs the same held-out measure on the pre-fix `index.html` (6fc4392), served from a scratch folder.

Points above chance, using mode + feature:

| feature | rung 2 before | rung 2 after (held out / exact maj, min) | rung 3 before | rung 3 after (held out / exact maj, min) |
|---|---|---|---|---|
| lowest + highest, exact pair | +14.1 | +0.1 / +1.1, +1.7 | +16.8 | +4.8 / +6.7, +4.9 |
| lowest | +3.7 | +1.0 / +0.3, +0.6 | +3.1 | +1.4 / +2.5, +0.8 |
| highest | +4.2 | +0.6 / +0.5, +1.0 | +3.8 | +2.1 / +3.1, +2.7 |
| span | – | −0.2 / +0.8, +1.2 | – | +3.1 / +5.1, +3.7 |
| last bass | +18.7 | +0.0 / +0.7, +1.1 | +2.4 | +3.0 / +4.5, +2.7 |
| last soprano | +10.1 | +0.3 / +0.5, +1.3 | +9.0 | +3.0 / +3.4, +3.3 |
| opening voicing | – | −0.4 / +0.4, +1.2 | – | +4.6 / +5.9, +5.5 |

Features that combine two exact pitches inside the cadence predict 20–57 points: first and last bass together, the last chord's outer voices, the last chord's full voicing. Those pairs carry the bass motion and chord, which is the cadence the student is meant to hear, so I don't count them as register tells.

Other checks:
- Rung 2 uses 12 major and 12 minor keys, both in `earCadKeys(2, ·)` and in the sample.
- No weighted entry lacks a realisation (0 nulls), so the old fallback draw never runs.
- Answers are evenly drawn within each mode.
- The sample has 2,142 distinct rung 2 voicings and 1,137 distinct rung 3 voicings.

**Voice leading (`vl_cad23.py`).** Each chord's notes and bass come from music21 `RomanNumeral`, not from the app's tables. The rules are written in the probe:
- ranges B 40–62, T 48–67, A 55–74, S 60–79; no crossing; S–A and A–T within an octave
- no parallel or contrary 5ths/8ves/unisons; no overlap; no hidden 5th/8ve in the outer voices with a soprano leap
- no leap of a 7th, a tritone or more than an octave; no augmented 2nd
- the leading note rises (an inner voice may fall to the 5th of I); it always rises into vi/VI
- 7ths fall by step; the secondary leading note rises
- a 6/4 doubles its bass, and its 6th and 4th fall by step
- no doubled leading note or 7th; chords complete except a root-position 5th

Results:
- Rung 2: 3,457 distinct realisations, 0 motion faults. 6 doubling/completeness flags, all the same shape (S1).
- Rung 3: 1,509 distinct realisations, 0 motion faults. 8 flags, all a cadential 6/4 whose bass drops an octave into V (Could C-2).
- I also checked all 24,000 generated questions: 37 rung 2 questions carry S1 and 118 rung 3 questions carry C-2. Nothing else.

### C4

`c4_vvi_enum.py` writes its rules from the rule text only:
- the app's SATB ranges
- open spacing (S−T > 12)
- complete triads; V with one leading note; vi with its 3rd doubled
- the leading note rises in every voice
- no parallel or contrary perfects; no overlap; no hidden outer 5th/8ve with a soprano leap
- no leap of a 7th, a tritone or more than an octave

Results:
- **28** voicings: per key, C 4, D♭–G 2 each, A♭ 1, A–B 3 each.
- Relaxing vi's doubling, or allowing contrary 5ths/8ves, still gives 28. Open spacing is the binding rule.
- Close spacing only gives 58; any spacing gives 108, matching the builder's figure.
- `c4_app_pool.py`: the app's 28 V–vi entries are the same set as mine. 10,000 drawn interrupted questions use all 28, each at least 35 times.

### C7

- **Names (`c7_names.py`).** I compared `c2IvA` with music21 for every ordered pair from C2 to B6 with ♭♭, ♭, ♮, ♯, ♯♯ (30,625 pairs).
  - Every augmented, diminished, doubly and triply altered name matches music21, including letter-crossing pairs (E♯/F♭ → "doubly diminished 2nd") and "double octave".
  - The 1,770 differences are all 4-fold or more: the app says "a 4-fold augmented 4th" where music21 says "quadruply" (Could C-1). In 20 cases music21 itself is wrong because it wraps the semitones (B♯♯2–F♭♭3 is quintuply diminished, as the app says).
  - `c2Span` gives "a double octave", "an 11th" and "an 18th" correctly. `c2Bars(9,9)` gives "Bar 10".
- **Messages (`c7_messages.py`).** I ran `c2Check` 8,850 times on mutated models: every mode, species 1–5, above and below. That produced 52,535 messages.
  - 0 hits for "Bars N–N", "altered", "N-fold", a bare "15th", a wrong article, undefined/NaN, or a thrown error.
  - 986 M6 outline messages, 203 of them in the one-bar form "Bar 10: …".
  - S3d: species 3 always says "The crotchets in between", species 5 "The notes in between". Octave to unison reads "an octave and a unison"; two unisons read "unisons".
- **Diff (6fc4392 → 93bf5ce).** Only message strings and naming helpers changed. No `add(` condition, severity or rule code changed.

### C8

The two Chord Library sentences (`Q`, lines 1646 and 1654) and the Ear Lab `QSYM` lines:
- Augmented triad: from the top note up to the root again is a diminished 4th (G♯–C: four letters, 4 semitones), enharmonic with a major 3rd. In equal temperament it splits the octave into three equal parts, so each inversion sounds like another augmented triad in root position. True.
- Diminished 7th: from the 7th up to the root again is an augmented 2nd (A♭–B: two letters, 3 semitones), enharmonic with a minor 3rd. It splits the octave into four equal parts. True.
- "Leading-note 7th (vii°7) of four different minor keys a minor 3rd apart": B–D–F–A♭ is vii°7 of C minor; respelled, it is vii°7 of E♭ minor, G♭/F♯ minor and A minor. True.
- No other aug/dim7 symmetry sentence in the app is false. The only other "symmetrical" is the octatonic scale, which is true.

### C9

`c9_fnmap.py` compares `earNumFn(rn, mode)` with `analyse()` on `cadList(rn)` in all 12 major and all 12 minor keys.
- Every numeral in scope matches (listed in the verdict table).
- Mismatches remain only for numerals no Ear Lab question uses: major iv, ii°, II, III, i; minor ii, IV, I. Ear Lab colours them PD/T where Analysis colours them chromatic. This is register row C24 (Drafted) and was left alone correctly.
- ELFN.MD and Analysis FN.MD are the same colour (`var(--md)`).

### C11

**Web check:**
- Skoove: "played in the key of F# minor"; progression F♯m – D – A – E.
- Hooktheory: F♯ minor in every section; verse v–i–VI–VII, chorus i–VI–VII–v (F♯m, D, E, C♯m).
- Wikipedia: released 10 May 2019, "a song by Australian singer Tones and I". It gives no key or chords.
- The two chord sources differ on the fourth chord (A vs C♯m). The card claims only F♯m, D and E, which both agree on. These are two independent lesson/analysis sources, not lyric sites.

**Rendered card (`c11_card.py`)**, Chord Library minor triad:
- It reads "Australian pick · Dance Monkey · Tones and I · 2019 … Chord heard: F♯m (tonic minor triad), with D and E in the loop · key F♯ minor", with no ⚠.
- It links all three sources.
- The data lists the recording as the "Original 2019 single (released 10 May 2019)".

## Findings

**Must:** none.

**Should**
- **S1 (C3, rung 2): incomplete I⁶ with a doubled major 3rd.** In `I I:1 vi IV I` (plagal) and `I I:1 vi IV V` (imperfect), in C, E♭ and B major, the I⁶ is voiced with no 5th and its 3rd doubled in bass and soprano. In C it is E3–C4–C5–E5. That is 6 realisations, 37 of 12,000 questions (29 of 1,935 plagal, 8 of 2,007 imperfect).
  - The motion is fine, and the app's own rules allow it: `satbCandidates` lets the 5th drop in any inversion.
  - But strict common-practice doubling keeps first-inversion triads complete and avoids doubling a major triad's 3rd in the outer voices.
  - Suggest: in strict rungs, require complete chords in inversion, or forbid a doubled major 3rd in the outer voices. Then refit EAR23W.
- **S2 (C3, rung 3): the remaining register tell is small but not zero.**
  - Mode + exact lowest/highest pair: +4.8 points held out, and +6.7 (major) / +4.9 (minor) for someone who memorised the full table.
  - Span: up to +5.1 exact. Opening voicing: up to +5.9 exact.
  - The worst single pair is (43, 67) in major: +11 points over chance, on 1.3% of questions.
  - This is a large improvement (+16.8 → +4.8) and sits inside the suite's 5-point margin. But "a few points" is only just met, and the exact optimum exceeds 5 points in major. Over a whole term a careful student could still pick some of it up.
  - Suggest: more fitting iterations or a smaller `mix` for rung 3, or a finer bass/soprano grid, then re-measure with the exact method in `tells_cad23.py`.

**Could**
- **C-1 (C7):** four or more alterations print as "4-fold augmented …"; "quadruply" is the usual word. Students can't reach these (no double sharps or flats in the input), so this is cosmetic.
- **C-2 (C3, rung 3):** in A and B♭ major and minor, the cadential 6/4 bass drops an octave into V: for example I⁶₄ E3 (tenor in unison on E3) to V E2. Many textbooks accept an octave bass leap at the 6/4, but a held bass is the stricter model. This affects 8 realisations, about 1% of rung 3 questions.
- **C-3 (C7):** "an octave and a unison" is used for both orders (unison then octave as well). The S2c and parallel/consecutive errors still say "octaves" for octave → unison. That is outside C-3's scope; it would be tidier to use `c2PerfPair` there too.
- **C-4 (C11):** the card doesn't show the recording line ("Original 2019 single"). It is in the data only, as on the other song cards.

## Probes (tests/reports/checks/ic_reg/)

All probes write scratch output to /tmp/icreg.

| probe | what it does |
|---|---|
| `dump_cad23.py` | dumps the rung 2/3 pools with their realisations and 12,000 seeded questions per rung |
| `tells_cad23.py` | exact and held-out register tells per mode |
| `baseline_cad23.py <app_dir> <N>` | the same held-out measure on any app copy (used for the 6fc4392 baseline) |
| `vl_cad23.py` | independent music21-based strict SATB check of every realisation and every sampled question |
| `c4_vvi_enum.py` | independent V–vi enumeration and its variants |
| `c4_app_pool.py` | the app pool and draws against my enumeration |
| `c7_names.py` | `c2IvA`, `c2Span`, `c2Bars` and `c2PerfPair` against music21 |
| `c7_messages.py` | scan of 52,535 checker messages |
| `c9_fnmap.py` | `earNumFn` against `analyse()` |
| `c11_card.py` | the rendered Dance Monkey card |

## Comparison with the builder reports (read after my verdicts)

- **C3:** the builder measured mode + exact pair at rung 3 as +4.3 (2-fold cross-validated). Mine is +4.8 held out, which agrees; my exact-optimum figures (+6.7 / +4.9) are new. The builder's strict check reports 0 faults with the app's rules. My S1 and C-2 come from stricter textbook doubling and 6/4 rules, not from a disagreement about the motion rules.
- **C4:** 28 and 108 both confirmed. I add the breakdown of 108 (28 + 58 + 22 mixed).
- **C7, C8, C9:** the builder's claims all agree with my findings. The builder doesn't mention the 4-fold wording (C-1).
- **C11:** the builder's account of the sources, including the disagreement on the fourth chord, agrees with my web check.
