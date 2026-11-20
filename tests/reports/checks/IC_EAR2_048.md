# IC_EAR2_048: independent check of Ear Lab B / H / L (0.48)

Build checked: `/home/claude/wt-check-int` @ `cd3bbb4` (read-only, detached). Scratch: `/home/claude/checks/ear2/`.
Spec: Justin's decisions L91 (B, H, L). I formed the verdicts from the spec and the running app, then read
`tests/reports/EL_BHL_048_report.md` (agreements and disagreements at the end).
Tradition for every voice-leading judgement: common practice, strict four-part chorale style.

## Verdict table

| Item | Verdict | Basis |
|---|---|---|
| B: "Cadential 6/4" on the two I⁶₄–V–vi phrases is Nearly | **PASS** | Real clicks on the rung 3 card, major and minor. Gold "Nearly" (rgb 201,162,74), n and ok unchanged, streak kept (2 → 2), nearly +1, the log says "nearly". "Interrupted" is Correct. Perfect, imperfect, plagal and Phrygian are wrong (streak 0, n+1). |
| B: existing Nearly cases unchanged, reverse cases wrong | **PASS** | Phrygian item answered Imperfect: Nearly. Cad64 item answered Perfect: Nearly. Imperfect answered Phrygian: wrong. Perfect answered Cadential 6/4: wrong. A plain interrupted item answered Cadential 6/4: wrong. Cad64 answered Interrupted: wrong. The judge agrees on all 21,000 judged answers in my 3,000-item rung 3 sample. |
| H: lowest/highest/span not predictive at rung 1 | **PASS** | Exact Bayes-optimal accuracy over the app's weighted pool, chance 25%: lowest+highest pair 27.3–27.7%, span 25.2%, lowest note 27.2–27.4%, highest note 26.5–26.8% (bands of 1, 2, 3, 4 and 6 semitones). The 20k-item cross-validated figures agree. Before the change: pair 40.5%, span 38.1%. |
| H: other non-harmonic features | **PASS with a Should (S1, S2)** | The register features are flat. The soprano line is not: a listener who follows only the top line in solfa gets 90.9% at rung 1, up from 79.6%. The imperfect cadence is now 84% I–V, so a first chord of IV means plagal 86% of the time. |
| H: strict voice leading, complete chords, open spacing, leading note rises in V–I | **PASS** | All 631 realisations the app can play were checked exhaustively with my own checker. 0 faults, every chord complete (5th included), all open, and in every V–I the leading note rises a semitone to do in every voice that has it. |
| L: rung 2 cadences strictly voice-led | **PASS** | Exhaustive: every model × key × register on the question grid (4,800 realisations), 0 Must-level faults. 8 contain a descending diminished 4th in the tenor that then resolves inward (C1). |
| L: bass-and-numerals strictly voice-led, applied chords resolve, no bass 7th leaps | **PASS** | Exhaustive: every progression × key × drawn register (13,860 / 21,780 / 29,700 at rungs 1–3), 0 faults. fi (V7/V) and si (V7/vi) always rise a semitone. Applied 7ths fall. No tritone, augmented or 7th leaps. Chromatic notes are approached by chromatic step in the same voice (no cross-relations). |
| L: no ii(⁶)→IV anywhere | **PASS** | Checked across all 40 rung 2 models, 22 rung 3 models, 4 rung 1 models and all 66 bass progressions (exhaustive), plus the sampled items. 0 cases (ii°⁶→iv included). |
| Teaching sentences true of their item | **PASS** | 48,500 cadence sentences (3,000 / 2,500 / 3,000 items × every answer) and 5,000 bass items × 6 answers. 0 false rung 1 and rung 2 sentences, 0 false bass sentences. The int64 Nearly / Correct / wrong texts are true. Rung 3 "6/4 bass not held": these 9 flags are false positives from the old checker's strict same-pitch test, because the sentence itself says "dropping an octave into V". |
| No new tells elsewhere | **PASS** | Rungs 2 and 3, before (`cad7a88`) and after on the same seeds: rung 3 is identical. Rung 2 is equal or better on every feature, within about 1 point (e.g. lowest exact 31.4 → 28.6%, last soprano 39.6 → 35.7%). The rung 2/3 tells that were already there remain (C2). |

**Musts: none.**

## Method (all fresh, new seeds)

- **Exhaustive enumeration** (`enumall.py` → `enum.json`). The app's own `earR1Pool()` (every rung 1 realisation a question can play), `earCadProg` on every rung 2/3 grid register (`BG×SG`, exactly what `earCadReg` chooses from), and `earBassProg` on every drawn register (b 42–52 × s 66–74). In total 2,376 rung 3 + 4,800 rung 2 + 631 rung 1 + 65,340 bass realisations. None was missing (no model/key without a realisation).
- **Fresh strict checker** (`vl2.py`, my own code, spelling from music21 `RomanNumeral`). Per chord it checks pitch content, bass, root/3rd/7th present (and the 5th at rung 1), crossing, spacing (S–A, A–T ≤ 8ve), ranges, doubled leading note, doubled applied leading note, doubled 7th, and that a 6/4 doubles its bass. Per move it checks spelled melodic intervals (any augmented interval, diminished leaps), tritones, 7th and compound-7th leaps, leaps over an octave, overlap, parallel and contrary 5ths/8ves/unisons, and hidden 5ths/8ves in the outer voices with a soprano leap. It also checks leading-note resolution (an inner voice may fall to the 5th of I), that the raised 3rd of an applied dominant rises, that 7ths fall by step, that V→vi doubles the 3rd of vi, and that there is no ii→IV. It was self-tested on hand-made faulty progressions (parallels and an unresolved leading note were flagged).
- **Tells.** First, exact Bayes-optimal accuracy at rung 1 from the app's own `earR1Weights()` (no sampling noise). Second, 20,000 light items per rung (seeds 90001–90003 ×7) through a 2-fold cross-validated lookup classifier, conditioned on mode, against a baseline with labels shuffled within mode (6–12 shuffles). Bands were 1/2/3/4/6 semitones. The same seeds were run on the pre-BHL build `cad7a88` for before/after.
- **UI** (`ui2.py`). The real rung 3 card at Stage 6, with real `[data-earans]` clicks. I recorded the tally, verdict colour, button classes, teaching text, journal log and page errors (none). Screenshot: `int64_nearly.png`.
- **Sentences.** `dump.py` (the earlier check's harness, new seeds 501/502/503, 511–513) feeds `cadcheck2.py`, which is updated for B: it expects Nearly for int64 + Cadential 6/4. `basscheck2.py` checks the bass items.
- No browser crashes occurred, so no retries were needed.

## Findings

### S1 (Should). Rung 1: the soprano line now predicts the answer much more than before
The register features H names are balanced, but the iterative fitting balances absolute pitches and not soprano solfa. The strict filters (complete chords, leading note rising) also narrowed the top lines. Exact figures from the app's weights:

| Soprano feature, rung 1 (chance 25%) | Before (`cad7a88`) | After |
|---|---|---|
| top-line solfa path (e.g. ti–do, so–mi) alone | 79.6% | **90.9%** |
| soprano degree of the first cadence chord | 56.5% | 72.8% |
| soprano degree of the last chord | 50.6% | 68.7% |

The giveaways:
- Soprano so→mi (falling 3rd) is always V–vi (35% of V–vi items). V–I never has so→mi on top, although it is good voice leading.
- Soprano so–so is always V–I.
- Soprano fa→mi is always IV–I.
- Over IV, do or la on top is always plagal.

Some of this is content: the top line of a cadence is part of how it sounds. But "so–mi means interrupted" and "do over IV means plagal" are voicing choices, which is the kind of tell H rules out. **Justin's ruling needed:** does the top line count as harmonic content? If not, add the soprano solfa of each chord to the features the fitting balances, or allow V–I with so→mi and IV–V with do on top.

### S2 (Should). Rung 1: IV–V has almost vanished from imperfect cadences
After the fitting, imperfect items are I–V 84% of the time and IV–V 16% (4% of all rung 1 items; before, the split was about even). The spec names both I–V and IV–V. As a result, hearing IV as the first chord means plagal 86% of the time, so a student can answer without hearing the second chord. "First chord only" accuracy went from 62.4% to 71.0%. Fix: fix the model share within imperfect (e.g. 50/50) before the fitting, or add the model as a balanced feature.

### C1 (Could). Descending diminished 4th leaps to the leading note
- Rung 2: `i VI V i` in A minor, tenor C→G♯ (8 of 4,800 grid realisations).
- Bass drill rung 3: soprano G→D♯ into V7/vi in G major (82 of 29,700).

Every case then resolves inward by step (G♯→A, D♯→E). That is accepted in most chorale texts but avoided in the strictest. It is not an augmented leap, so it does not break L.

### C2 (Could, pre-existing, not new). Rung 2/3 exact-semitone register tells
- Rung 2: last bass absolute 44.5%, lowest+highest exact 38.2%, lowest note of the cadence 42.5% (chance 25%).
- Rung 3: pair exact 36.0% (chance 18.4%).

These shrink to +2–9 points at 6-semitone bands. They are unchanged or better than before; the builder's report lists them as open issue 3. Rung 2 still uses 7 major / 5 minor keys, so the absolute last bass note helps someone with absolute pitch.

### C3 (Could). Rung 1 variety is small
- 238 distinct questions turned up in 20,000 draws (403 before).
- Interrupted: 28 (unchanged). Perfect: 47.
- Effective count per answer (perplexity of the weights): 25–51.
- 391 of the 631 pool entries carry less than 1e-4 of their answer's weight.

Students will meet exact repeats often.

### Note (no action). Rung 3 6/4 bass sometimes drops an octave
In 16 of 648 rung 3 6/4 realisations, the bass drops an octave from I⁶₄ to V. The sentence "dropping an octave into V" matches. Not part of BHL.

## Builder report (`tests/reports/EL_BHL_048_report.md`): agreements and disagreements

**Agree:**
- B works as described, including the tally semantics.
- H: lowest+highest and span are flat (my +2.3–2.7 vs their +1.4 mean / +2.7 max), and the first/last bass edge of about +4 is in line with theirs.
- L, S1–S3: 0 voice-leading faults and no ii→IV, which I confirmed exhaustively rather than by sample.
- Rung 3 tells are identical; rung 2 tells are at or below the old ones.
- Their open issues 1–3 match mine.

**Disagree or add:**
1. **Gap.** The report does not measure the soprano solfa / top-line tell, which rose from 79.6% to 90.9% at rung 1 (S1). Nor does it mention the IV–V share collapsing to 16% of imperfect items (S2).
2. **Variety figures.** The report says "distinct rung 1 items in 2,000: perfect 72, plagal 126, imperfect 193". My 20,000 draws from the same build give 47 / 67 / 96, and only 47 / 68 / 97 pool entries have a weight of 1e-4 or more. Their counts exceed what the weights can produce, so they were probably counted on a different definition or an intermediate build. The variety loss (C3) is larger than the report suggests.
3. **Open issue 4 (IV→vi).** IV→vi is a weak but accepted succession in common-practice texts, not a retrogression like ii→IV. I see no need to change it.

## What I could not check
- Audio: the sound, timing and key-cue playback were not listened to.
- Human perception: whether the soprano tell (S1) is salient to Stage 4–6 students is a judgement for Justin. My figures are idealised (a listener who hears the top-line solfa perfectly).
- Teaching sentences were checked by regex fact rules (the earlier check's rules plus the B update) and by reading every UI case above, not by a human read of all 125 distinct sentences.
- The 6/4 chip label: the old chip check expects "bass X" on every cadence chip, but the 6/4 chip now reads "cadential 6/4" (from an earlier session, S4). I did not judge that change.
- I did not re-run the repo's own suites (`run_all`), because this is a read-only check.

Files: `enumall.py`, `vl2.py`, `vl_extra.py`, `light.py`, `light_old.py`, `tells2.py`, `tells3.py`, `soppath.py`, `r1melo.py`, `ui2.py`,
`cadcheck2.py`, `basscheck2.py`, outputs `vl_enum.json`, `tells2_out.txt`, `tells3_out.txt`, `ui2_log.txt`, `int64_nearly.png`.
