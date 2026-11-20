# 0.48 items F and 12: interval names in climb 13 and the climb 2 ladder; the modal dominant colour

Branch `048-cp13col`, from `048-int` @ `a24d936`. Worktree `/home/claude/wt-cp13col`. All checks below are **self-checks** by the builder; nothing here has been independently checked yet.

## F. Interval names in words (climb 13 and the climb 2 ladder)

| | |
|---|---|
| **Change** | `c13Pair` (climb 13's beat-by-beat checker, used by canon, countersubject, stretto finder, the transformation tables and the fugue draft) now names intervals with climb 2's `c2IvA` / `c2IvName`: "is a perfect 4th", "both voices move into a dissonance (a major 2nd)", "an augmented 4th on a weak beat", "a held note clashes (a minor 7th)". Unison and octave are plain, as in climb 2. The climb 2 ladder hover reads "D5 against G4: perfect 5th" (was "P5"). |
| **Refactor** | `c13Pair` attaches the interval object (`iv`) to every I1/I2 issue. `c13CSCheck` used to test the message text (`/a P4\|4th/`) to recode an inverted strong-beat 4th as IC1 and to append the "5th that became a 4th" note; it now calls `c13P4(x)` = `x.iv.g7===4 && x.iv.q==='P'`. **Behaviour change, deliberate:** the old text match also caught an augmented 4th in the I1 message (because "4th" appeared in its "(a 4th is a dissonance …)" aside). An A4 below comes from a d5 above, which is already flagged as a dissonance above, and the note ("avoid 5ths on strong beats") is about perfect 5ths, so IC1 and the note are now for perfect 4ths (and 11ths) only; an A4 stays I1. The I2 note was already P4-only. |
| **Test** | `counterpoint_test.py` section **O** (new): 500 random subjects, countersubjects and canons (tonal in all keys and both modes, and the six modes), plus stretto pairs at 3 delays × 5 intervals. `c13Pair` is wrapped in the page to record the two pitches of each issue. O-1: no abbreviation (`P4`, `M2` …, after removing the exercise's pitch names), none in brackets ("(M2)"), right a/an, and the named interval equals the one built from **music21's** interval between the two pitches; inverted-countersubject issues get IC1 and the note exactly when music21 calls the interval a perfect 4th/11th. O-2: the source no longer contains the text tests. O-3: the rendered issue lists of both climb 13 tabs (40 random cases each). O-4: every ladder hover in climb 2 (all modes, species 1–5, above and below) parsed and compared with music21. |
| **Result** | Pass. 43,606 climb 13 messages read (4,052 canon, 5,865 countersubject, 33,689 stretto), 38,430 interval names against music21, 2,577 inverted-countersubject issues checked for IC1; 839 rendered issue lines; 16,952 ladder hovers. Whole suite: 0 failures (3 min). |

Not verified: that section O fails on the unchanged 0.48 (I did not run it against `a24d936`); the regexes catch every form the old messages used ("is a P4", "(M2)", "P5" in the hover).

## 12. Modal dominant (MD), "soft pull", madder rose

| | |
|---|---|
| **Engine** | One category, `MD`, replaces the two blue-grey codes W (minor v) and S (subtonic). `isMD(rpc,pcs,k)`: root on the 5th with no leading note (v, v7, also the bare 5th and sus chords there), or root on the unraised 7th (VII, VII7). `homes()` (Keys room) and `analyse()` (everything else) both use it, so they agree: minor v / v7 and minor-key VII / VII7 = MD; V, V7, vii°, vii°7 = D. In a major key the **borrowed** v and ♭VII (♭VII7) are MD too (they keep `borrowed:true`, so Analysis still lists them as borrowed); other borrowed chords stay colour. `chordInfo().dom` (part-writing) is unchanged and already false for all MD chords. |
| **What Fable reported, checked** | In this branch `homes()` did *not* give minor v the dominant colour: it already returned W. The real faults were in the drawing: the SATB score numerals (`FC`), the climb 11 numerals and the Gym frame numerals (`COLS[FN[…]]`) had no entry for W or S and fell back to **violet**, so minor v and VII were drawn as chromatic chords. All three now draw MD. |
| **Colour** | `--md:#bd6b97`, `--md-ivory:#9e4776` in `:root`; `FN.MD='var(--md)'` (S and W kept as aliases for old saved data); new `FNHEX` used by the SATB and climb 11 numerals; `COLS['var(--md)']`. Blue-grey `#7fb3c8` no longer appears in any function colour (it remains in the form-section strips, which are not functions). |
| **Words** | `FNAME.MD` "soft pull · modal dominant"; Oracle suit "Soft pull", hint "no leading note: a softer pull home, a modal sound"; Keys explanation, one text for v and one for VII, both tagged by tradition ("In common-practice minor it lacks the leading note … so it pulls to the tonic more softly than V … In modal, folk and rock harmony v–i is an ordinary close"); Keys legend adds "MD modal dominant: soft pull (minor v, VII; no leading note)"; Analysis numeral key and function row ("MD modal dominant"); climb 3's minor-key paragraph adds one sentence. |
| **Data** | `scores/meta.json`: the three Jesu, meine Freude labels (VII, v⁶, v⁶) W/S → MD. `tests/numeral_reread.py` generates MD; it re-reads 135 labels and 18 cadences with 0 differences. |
| **Oracle** | Ordinary draws used to exclude `f==='C'`; ♭VII in a major key is now MD, so the filter is "not colour, not borrowed, not applied" and the colour-card draw uses the same test. The decks are otherwise unchanged. |
| **Test** | `unit_test.py` D12 (new) and R9 (updated W/S → MD, name "soft pull · modal dominant"): `homes()` and `analyse()` on v, v7, VII, VII7, V, V7, vii°, vii°7, i, iv in 7 minor keys and v, ♭VII, ♭VII7, V, iv, ♭VI in 5 major keys; colour values (`--md`, `--md-ivory`, `FNHEX`, `COLS`); Keys legend; the SATB score numerals of E minor i–v⁶–iv⁶–V–i and i–VII–III… drawn in `#bd6b97`; a contrast scan of every visible element drawn in either MD colour in the Voicing lab, Gym, Keys, Analysis (my progression, and the Jesu score with the harmony layer), composited over the actual ground. |
| **Result** | Pass, 761 checks. Contrast: lowest found in the app 5.05:1 (15 elements across 5 views). Computed: `#bd6b97` on `#0b0906` 5.41, `#0e0c08` 5.32, `#12100b` 5.17, `#17140e` 5.00; `#9e4776` on ivory `#ece2c8` 4.50 (4.501). MD never sits on ivory in the app today (the scan found none), so `--md-ivory` is defined but unused. |

Screenshots (looked at): `/tmp/md_satb_1440.png`, `/tmp/md_satb_390.png` (Voicing lab, E minor, i VII III iv⁶ v⁶ iv⁶ V i: VII and v⁶ in rose, V in red, readable apart at both widths), `/tmp/md_keys_1440.png` (Keys, Em in A minor: chip, text and legend).

## Suites

| Suite | Result |
|---|---|
| unit_test | pass, 761 checks |
| content_lint | pass |
| counterpoint_test | pass, 0 failures (new section O) |
| spelling_test | pass, 49,190 checks |
| layout_test | pass, 162 views, 0 findings |
| pageerrors_test | pass, 153 views + 881 random clicks, 0 errors |
| terms_test (run alone) | pass, 153 views, 0 failures |
| numeral_reread (not in run_all) | 135 labels, 18 cadences, 0 differences |

## Open

1. **Ear Lab** keeps its own function map (`earNumFn`, `ELFN`): it would call a minor-key `VII` or a minor `v` dominant. No Ear Lab item uses either chord today, and other agents are editing Ear Lab, so I left it. When it next changes it should map them to MD.
2. The Gym frame and Voice-coach numerals above the voice-leading curves are always gold (labels, not function colours); unchanged.
3. Fable's other findings stand, outside this item: dominant red `#c8473b` is 3.9:1 on `#17140e` and 4.2:1 on `#0b0906` (under 4.5); tonic green and predominant gold are ΔE 5 apart under deuteranopia. Rose is ΔE 9 from the decorative `--pink`; in the screenshots they do not meet.
4. ♭VII and v in a **major** key as MD is my reading of "other subtonic / modal-dominant uses". It changes their colour from violet to rose in the Gym, Oracle, Analysis and climbs 4, 5 and 11. If Justin wants MD for minor keys only, it is one condition in `analyse()`.
