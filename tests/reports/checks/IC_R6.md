# Independent check: R6 terms, R7 footer, R10 double accidentals, R11 theoretical keys

Checked copy: /home/claude/wt-check-r6 (HEAD 96ebd4b, baseline 0.47 = ef97cdb), read-only.
Method: headless Chrome (/usr/bin/google-chrome) through Playwright with the repo's offline harness (tests/harness/cjg.py). I opened every room, every climb 1–13, every form, all 10 Analysis scores, all 7 Ear Lab drills, the Gym, the Oracle, the journal and Credits, at Stages 4, 5 and 6, at 1440 px and at 390 px (touch emulation). In each view I clicked up to 25 visible buttons and recorded every bracket, every hover title and every unbracketed term (about 1,800 records). I answered questions at every Ear Lab rung, filled the climb 2 species 1–5 and three-voice exercises with faulty counterpoint so the checker messages appeared, and fed the Gym cadence reader I–IV–V–I, I–vi–IV–V, I–ii–V–vi, I–V–IV–I and V6–I.
Scripts, raw JSON and screenshots: /home/claude/checks/r6work/ (screenshots in shots/).
I formed this view before reading tests/reports/R6_R7_R10_R11_report.md. I read it afterwards only to compare.
Note: the builder's tests/terms_test.py crashed for me (the browser closed mid-run while my own sweeps were also running), so I have no pass or fail from it. Everything below comes from my own runs.

## Verdict

| Item | Result |
|---|---|
| R6 term list and helpers (pairings, IAC label, note text) | PASS |
| R6 no US term on its own | PASS with 2 exceptions (W/H step letters, "half–whole diminished") |
| R6 both terms in feedback | **FAIL**: the Gym cadence reader never shows the US term (H1) |
| R6 hovers correct | **FAIL**: hovers are stale and pile up (H1); "crotchet rest" is paired with "quarter note" (M3) |
| R6 wrong pairings | **FAIL**: "12-bar (US: measure) blues", "8-bar (US: measure) phrase" and similar (H2) |
| R6 brackets kept off buttons, chips and scores | PASS (no bracket on any button or chip, and none in any svg) |
| R6 readability, clutter and grammar | Mostly good, with a few fixes (M1, M2, L1–L4) |
| R6 sizes (11 px or more) | PASS: every .tm, .tmus and .tmnote is 14 px or more, and the tap tooltip is 12 px |
| R6 tap on phones | PASS for prose (tapping a term focuses it and shows the tooltip). Buttons are hover-only (see decision b). |
| R7 footer and credits | PASS |
| R10 double accidentals | **FAIL**: "♭♭7" still shows in two places (H3) |
| R11 theoretical keys | PASS (and one nearby spelling error, L6) |

Overall: **R6 and R10 need one more round.** H1–H3 are real bugs that a student will see. The rest is polish.

---

## High priority

**H1. The Gym cadence reader is treated as a button. Feedback gets no US term, and its hover goes stale.**
`<div class="cad" id="cad">` (index.html line 1079) matches `.cad` in `TM_BTN`, which the builder meant for the cadence cards. So:
- the reader's feedback never carries a bracket. The screenshot shows "**Perfect cadence.** V → I, both in root position…" with no "(US: authentic cadence)" and no underline (shots/gym_cad_390.png). On a phone there is no way at all to see the US term here. This breaks the rule that answer feedback carries both terms.
- `dataset.us` only ever grows, so the title keeps every term the box has ever shown. Real readings at 1440 px:
  - "Add two or more chords and I'll read how your phrase ends." has the title **"US: authentic cadence, half cadence, deceptive cadence"**
  - "Plagal cadence. IV → I: the "Amen" ending…" has the title "US: authentic cadence, half cadence, deceptive cadence"
- The same pile-up can hit any button whose text changes. `termWrapNode` adds to `data-us` and never clears it.

Fix: give #cad its own class (or mark it as a feedback box) so that it takes brackets. Then rebuild `data-us` and `title` from the element's current text on every pass, instead of adding to them.

**H2. Wrong pairing: "bar" inside compound adjectives.**
"12-bar blues" and "8-bar phrase" are the same in US usage, and nobody says "12-measure blues". Rendered strings:
- Forms heading: "Level 3 · Forms · **12-bar (US: measure) blues**". The Forms list, "Try · build your own 12-bar (US: measure) blues", and every journal entry "opened the form: 12-bar (US: measure) blues" do the same.
- Climb briefs: "Compose an **8-bar (US: measure)** phrase or period…", "Compose an **8- to 16-bar (US: measure)** melody…", "Compose an 8-bar (US: measure) passage…"
- Chord library song note: "…under a **12-bar (US: measure) blues** in B♭."
- The hover on the buttons is also wrong: "Twelve-bar blues" has the title "US: measure", and the journal chip "Form · 12-bar blues" has the title "US: measure".

Fix: in the `bar` rx, skip a match after a number or number word plus a hyphen (`(?<!\d- ?|\bto |[a-z]+-)`, or simply `(?<!-)` plus a check for "N-bar"). Plain "12 bars" and "Twelve bars (US: measures)" are correct and should stay.

**H3. R10: "♭♭7" still appears.**
The builder fixed the tiles, formula and voicing cards with `degPretty()`, but two code paths still use the old replacement `.replace(/b/g,'♭')`:
- line 1568, the inversion caption: Cdim7 in 3rd inversion reads **"3rd inversion: the ♭♭7 is in the bass"**. The same screen shows "𝄫7" elsewhere (shots/seed_dim7_inv3_*.png).
- lines 1481 and 1514, the `dg` degree labels on the guitar and bass fretboards: the dim7 chord diagrams show **"♭♭7"** on the fret dots, next to other diagrams on the same page that show "𝄫7" (shots/seed_dim7_guitar_1440.png).

Fix: use `degPretty()` in all three places. The spelling test misses these because it reads the root-position piano view only. Add inversion 3 and the guitar and bass views to it.

## Medium priority

**M1. "tone" (US: whole step) is matched only as "whole tone".**
The builder chose this on purpose because of "chord tone" and "tone colour". But the app uses the bare word as an interval often, so those mentions never get the pairing:
- heading/card "**ii–Vs down a tone**" (climb 9, also on its button and a ⤒ card)
- "A major chord **a tone below home**." / "a borrowed chord a tone below home" (♭VII cards)
- "Then to a minor ii–V **a tone lower**." / "(or a tone)" / "(bigger than a tone)" / "Between two chords **a tone apart**…"

Fix: either match `(?<=\b(a|than a|by a|one) )tone\b` and `tone (higher|lower|above|below|apart)`, or change these 8–10 strings to "whole tone". The second is simpler and reads fine.

**M2. The Keys step letters W and H are US abbreviations.**
The legend now reads "W = whole tone (US: whole step) · H = semitone (US: half step)". The letters only make sense in US terms ("H = semitone" is odd for a NSW student), and the tiles show W, H and "W+H" between the notes (shots/S6_keys_scales_1440.png). The Australian convention is **T** and **S** ("T T S T T T S").
Fix: use T, S and "T+S", with a legend like "T = tone (US: whole step, W) · S = semitone (US: half step, H)". Related: the Octatonic chip subtitle "**half–whole diminished**" is a US-derived name standing on its own. Make it "semitone–tone (half–whole) diminished", or leave it as a jazz name with a hover.

**M3. Rests and plurals in the rhythm drill.**
- The "crotchet rest" button has the title "US: quarter **note**". It should be "quarter rest". Feedback renders "crotchet (US: quarter note) rest". It should be "crotchet rest (US: quarter rest)". The same applies to "minim rest", which appears twice in the source.
- The "2 quavers" and "4 semiquavers" buttons have singular titles ("US: eighth note"). `termWrapNode` always calls `termUS(k,false)` for buttons, so the plural is lost.

**M4. Climb 2 checker lists repeat the bracket on every line.**
With faulty species-5 counterpoint you get 20 issues. Each is its own block, so each carries a bracket: "A dissonant minim (US: half note) must be a passing note." appears 3 times and "A dissonant crotchet (US: quarter note)…" 3 times in one list. Each line is correct on its own, but together they read as noise. Suggestion: treat the issue list (`.iss` container) as one block, so the first mention per list carries both and the rest hover.

## Low priority (readability and grammar)

- **L1. Brackets placed back to back:** "a semitone (US: half step) (K1)", "an imperfect cadence (US: half cadence) (the question)", "Perfect cadence (US: authentic cadence) (V–I)" (every Analysis cadence row), "Span: 7 semitones (US: half steps) (0.6 octaves)" (Voices). Nested brackets: "(an imperfect cadence (US: half cadence) in minor, iv⁶–V)" (Ear Lab cadences), "(…one chord per bar (US: measure))", "(the tempo is the dotted crotchet (US: quarter note))", "(quavers (US: eighth notes))". Fix by rewording the source (for example "Perfect cadence (US: authentic cadence): V–I", or "Span: 7 semitones (US: half steps), 0.6 octaves"). Alternatively, make the pass use a dash or comma when the next character is "(".
- **L2. The bracket breaks idioms:** "choose, **bar (US: measure) by bar**, when to use it" (climb 12), "chosen bar (US: measure) by bar" (climb 2 florid). Skip `bar by bar`.
- **L3. Capital letter mid-sentence:** `TERM_IAC` is capitalised, so the Gym reads "This one is a **Perfect** cadence, less final (US: imperfect authentic)." and the progression report reads "…perfect cadence at the end of bar 4; Perfect cadence, less final (US: imperfect authentic) at…". Use a lower-case variant in running text.
- **L4. Climb 3 "In the US" row:** "In the US · perfect cadence = US authentic cadence". "US" appears twice. Write "authentic cadence".
- **L5. Hovers on the IAC chip:** "Perfect cadence, less final" (Forms phrase builder) has the hover "US: imperfect authentic" without the one-line note. That is arguably fine because a hover has no room, but strictly "wherever both appear". The journal export line also carries "(US: imperfect authentic)" without the note.
- **L6. In passing (R11 screen, probably older than R6):** the circle's "Neighbours" row spells keys from the wheel labels. D♭ major gives "F♯ (one step back: the subdominant key)". It should be **G♭**. Likewise B♭ minor's subdominant shows as "d♯" instead of e♭ minor.
- **L7.** Every term in prose gets a dotted underline, including ones already bracketed. On bar-heavy pages (Forms blues has 33–39 underlined terms) this adds visual noise. Consider no underline when the bracket is present.

## Checked and fine

- No US term on its own anywhere in rendered text, titles or aria-labels across all views and stages, apart from M2. The only US words are in brackets, the note, "measure every interval" (a verb) and the climb 3 "In the US" row.
- Buttons, chips and options: no bracket anywhere, and the US term is in the title. Scores (svg): Australian only.
- False friends are correctly left alone: "barre" ("F (full barre)"), "barline"/"bar line", "whole-tone scale", "half-diminished", "chord tones", "staff-space" (code only).
- Plurals: "staves (US: staffs)", "bars (US: measures)" and "semibreves (US: whole notes)" are all correct.
- Ear Lab cadences: answer buttons read "Perfect cadence" and similar, with titles. Feedback reads "Here it is. Perfect cadence (US: authentic cadence) · V – I in E major". The "Listening for it" panel lists all four cadences with brackets.
- The IAC label and note appear correctly in Forms (phrase), the Gym reader and the phrase checker PM3.
- Sizes: brackets inherit 14 px or more, the note is 14 px, and the focus tooltip is 12 px. At 390 px, tapping "semitone" focused the abbr and showed "US: half step" without clipping (shots/tap_tooltip_390.png).
- Clutter, measured at 1440 px Stage 6: most views have 0–6 brackets on screen. The heaviest paragraph has 3 (the Ear Lab cadence key and the Forms phrase intro), which is acceptable for a definitions paragraph.

## R7, R10, R11 detail

- **R7 PASS.** The footer reads "Composition Jungle Gym · preview 0.47 · no accounts, no tracking · a sister to *The Garden of Earthly Sounds* · suggestions and corrections: …", with no sample credits. Credits → Sound still names VCSL Steinway B (CC0) and FluidR3_GM by Frank Wen (CC BY 3.0), at both widths (shots/footer_credits_*.png). The footer still says "preview 0.47", which is presumably updated at release.
- **R10 FAIL (H3 only).** Everything else checked shows 𝄪/𝄫: G♯/D♯/A♯ harmonic minor (F𝄪, C𝄪, G𝄪, plus F𝄪dim7 and similar), D♭ natural minor and F♭ major (B𝄫), G♯aug (D𝄪), Cdim7 (B𝄫), C♭dim7 (E𝄫, G𝄫, and the triple flat as "B♭𝄫"), the Ear Lab "E♭ G♭ B𝄫 D𝄫", and the 𝄫7 formula. No "bb", "##", "♭b" or "♯♯" in text or svg.
- **R11 PASS.** All 24 circle keys checked. D♭ major → parallel "D♭ minor · a theoretical key (8 flats); musicians write C♯ minor". G♯ minor → "G♯ major · a theoretical key (8 sharps); musicians write A♭ major". D♯ minor → "D♯ major · a theoretical key (9 sharps); musicians write E♭ major". No other key is flagged (A♭ minor at 7 flats and C♯ major at 7 sharps are correctly not flagged). Shown in red under the Parallel row (shots/circle_Db_390.png).

## The two builder decisions

**(a) "bar" and "stave" scoped (both terms in headings and at the first mention per room, hover elsewhere): agree, with conditions.** Checker and Analysis feedback is full of locators ("Bar 7: G5 is a dissonant m7…", "Bars 6–7: 5ths on two downbeats", "from bar 14"). Bracketing each would bury the musical point. The first mention per room carries the pairing, and every later "bar" is underlined and tappable. That is a sensible reading of the clutter rule. Conditions:
1. Fix H2 and L2 first. As it stands, scoping still puts the bracket on the *wrong* "bar" ("12-bar (US: measure) blues" is often the first mention in a room).
2. Teacher sign-off is needed, because this departs from the letter of the rule ("both terms in feedback").
3. On phones the per-room first mention is often far up the page from the feedback. Consider also bracketing the first "bar" inside each checker list or feedback box (the M4 change does this).

**(b) On phones the US term on buttons and chips is hover-only, seen only once feedback appears: acceptable in principle, but not yet true in practice.** The premise is that the feedback always names the term with its bracket. That holds in Ear Lab cadences and rhythm ("Here it is. crotchet (US: quarter note) · …"). It fails in the Gym cadence reader, the main place a student meets cadence names (H1). It is also weak for the Forms phrase builder and section chips: "bars 3–4 / Imperfect cadence" and the cadence and bar choices have no feedback that repeats the term. Two cheap improvements, without a second tap behaviour on the buttons:
1. Fix H1 so the reader brackets.
2. Under each group of answer buttons that names terms (Ear cadences, rhythm values, phrase-builder cadences), add one small key line (11 px or more), for example "Perfect = US authentic · Imperfect = US half · Interrupted = US deceptive". The Ear Lab "Listening for it" panel already does this. It keeps the buttons clean and gives phone users the pairing before they answer, which matters in a drill where the student is meant to learn the name.

Desktop note: native `title` hovers take about 1 s to appear and keyboard users never see them on buttons. That is acceptable as a supplement, but it is another reason to add the key line.

## Prioritised fix list

1. H1: take #cad out of `TM_BTN` so it brackets like feedback, and rebuild `data-us`/`title` from the current text on every pass (stale hovers).
2. H3: use `degPretty()` at lines 1568, 1481 and 1514 ("♭♭7"). Add inversion 3 and the guitar and bass views to the spelling test.
3. H2: don't bracket "bar" in "N-bar" compounds (12-bar blues, 8-bar phrase, 8- to 16-bar melody), on text or on hover.
4. M3: "crotchet rest" and "minim rest" should pair with "quarter rest" and "half rest". Keep plurals in button titles.
5. M2: change the W/H/W+H step letters to T/S/T+S. Fix the Octatonic "half–whole" subtitle.
6. M1: pair the bare interval "tone" (or rewrite those strings as "whole tone"), including the heading "ii–Vs down a tone".
7. M4: one bracket per checker list, not per line.
8. L1–L4: back-to-back and nested brackets, "bar by bar", lower-case IAC mid-sentence, the duplicated "US" in the climb 3 row.
9. Decision (b): add a key line under the term-bearing answer-button groups.
10. L6 (outside R6 scope): the circle's subdominant spelling for D♭ major and B♭ minor.
