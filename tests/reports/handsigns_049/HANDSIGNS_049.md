# Hand signs 0.49: an original set for the Jungle Gym

Design step for approval. Nothing in `index.html` has changed. Branch `049-handsigns`, 20 Nov 2026. Design lead: Fable.

Justin's brief (20 Nov 21:16): "these are just examples, we must build our own based on these. the principles are common property only the actual art is a possible IP issue."

## 1. What is here

| File | What it is |
|---|---|
| `svg/*.svg` (17) | The signs at ladder weight: do re mi fa so la ti, di ri fi si li, te le se me ra. do′ uses `do.svg`. Single colour (`currentColor`), viewBox 80 × 64 |
| `svg/display/*.svg` (17) | The same drawings with a lighter line, for cards and a teaching screen |
| `sheet.html`, `png/sheet_1366.png` | Every sign, labelled, at three sizes, dark and light, plus the look-alike pairs at the phone size |
| `ladder_mock.html`, `png/ladder_mock_1366.png`, `png/ladder_mock_390.png` | Static mock-up of the ladders (major, flats, sharps, la-based minor, Keys room rows) |
| `png/app_earlab_1366.png`, `png/app_earlab_390.png`, `png/app_keys_1366.png`, `png/app_keys_390.png` | The real app at 1366 × 768 and 390 with the new signs swapped in at run time (`build/app_mock.py`; `index.html` untouched) |
| `png/<syllable>.png` (18, incl. `do-high.png`) | Each sign alone: 750 × 600, transparent, ink `#1d1a14`, all in the same frame so they keep their relative size when placed in a document |
| `ladder_full.html`, `png/ladder_full.png` | The whole ladder: scale in the centre, lowered signs left, raised signs right, transparent |
| `build/gen.py`, `build/build.py`, `build/shots.py`, `build/app_mock.py` | The source of the drawings and the scripts that make everything above |
| `refs/` | Justin's reference images (gesture evidence only). **Left out of the commit**: they are other people's artwork and full-screen screenshots that show browser tabs and bookmarks, and this repository publishes to GitHub Pages. They stay in the worktree, untracked |

## 2. The gestures

One right hand. Heights: do at the waist, ti at eye level, do′ at the forehead, the others evenly between; a raised or lowered sign sits between its two neighbours. La-based minor uses exactly the same signs (la is home; si is the raised 7th).

| Syllable | Hand shape, palm and fingers | Height | Evidence |
|---|---|---|---|
| do′ | The do fist again | forehead | [C1] [K] [J] |
| ti | Fist with the first finger pointing up and forward (about 40° above level) | eye level | [C1] [C2] "the upturned hand, pointing with the forefinger" [K] [J] |
| la | Hand hangs loose from the wrist, palm down, all fingers drooping | chin | [C1] [K] [J] |
| so | Open hand on its edge, fingers together pointing across, palm towards the signer, thumb on top | shoulder | [C2] "the open hand, pointing outwards, with the thumb upwards" [K] [J] |
| fa | Loose fist, thumb pointing down (towards mi) | upper chest | [C1] [K] [J] [T] |
| mi | Flat hand, level, palm down | lower chest | [C2] "the open hand with the palm downwards" [K] [J] |
| re | Flat hand slanting upward (about 30°), palm down | stomach | [K] [J] [T]; Curwen differs, see 2.1 |
| do | Closed fist, palm down, knuckles forward | waist | [C2] "the closed hand" [K] [J] |
| di | The do fist tipped up | between do and re | [J] |
| ri | The re slant, steeper (about 50°) | between re and mi | [J] |
| fi | The fa hand turned over: thumb up | between fa and so | [J] [CK] "Flip fa around" |
| si | The so hand lifted, fingers opening | between so and la | [J] [CK] |
| li | The la hand turned up: palm cupped upward, fingers curling up | between la and ti | [J] |
| te | The ti finger pointing down and forward | between la and ti | [J]; Curwen differs, see 2.1 |
| le | The la hand dropped further: fingers hang straight down | between so and la | [J] |
| se | The so hand tipped down, palm open | between fa and so | [J] |
| me | The mi hand sloping down | between re and mi | [J] |
| ra | The re hand with the thumb let fall (pointing down) | between do and re | [J], my reading of a small drawing: decision 4 |

Sources
- **[C1]** John Curwen, "Manual signs of tone in key", plate in *The Standard Course* (1870s), Wikimedia Commons `File:Curwen Hand Signs MT.jpg` (public domain; seen in Justin's screenshot `refs/73abacfa-image.png`). Its notes read: "The diagrams show the hand as seen from the left of the teacher, not as seen from the front" and "For fe, let the teacher point his first finger horizontally to the left. For ta, ditto to the right. To the class these positions will be reversed, and will correspond with the Modulator. For se, let the teacher point his forefinger straight towards the class."
- **[C2]** John Curwen, *The Standard Course*, 10th edition, text at archive.org (`10thedstandardco00curwuoft`): the verbal descriptions quoted above, and "The teacher makes his signs in front of his ribs, chest, face, and head". (I read the first tenth of the scan through a text tool; the OCR is rough, so the quotations should be checked against the page images before they are printed anywhere.)
- **[K]** KMEIA, "Curwen Hand Signs" chart, © 2003 (`refs/kmeia_handsign_chart.pdf`), the chart now in the app; and KMEIA, "Musicianship tools", https://kodaly.org.au/kodaly-concept/musicianship-tools/ : signs are made "in front of the body and in line with the centre of the body", one hand or both; movable do, la-based minor, so raised to si for the harmonic minor.
- **[J]** The one-page chart Justin supplied (`refs/curwen_hand_signs_doc.pdf`): flats point down, sharps point up; do at the waist, ti at eye level; Te Le Se Me Ra and Li Si Fi Ri Di drawn beside the scale. Taken as Justin's preferred convention.
- **[CK]** Colourful Keys, "Curwen hand signs", https://colourfulkeys.ie/curwen-hand-signs/ : fi is fa flipped; si is so slanted slightly upward, "sometimes shown with all the fingers open, or just the thumb away from the rest of the hand".
- **[T]** Teach Beside Me chart text, https://teachbesideme.com/solfege-hand-signs-chart-printable-cards-for-music-learning/ : do waist, mi mid-chest, sol shoulder, ti near the forehead, high do above the head; la as a "curved palm, as if holding a ball".
- **[L]** LibreTexts, *Equipping the Musical Ear* 1.4, https://human.libretexts.org/Courses/Sierra_College/Equipping_the_Musical_Ear/01%3A_Pitch/1.04%3A_Curwen_Hand_Signs : low do at the waist, upper do "at about eye-level", the rest evenly between.
- **[W]** Helen Winter, *Chromatic Hand Signs* (publisher's description), https://leanpub.com/chromatic-hand-signs : a chromatic sign sits "at the level between the diatonic note that is before it and after it".

### 2.1 Where the sources disagree

| Point | Versions | Recommended |
|---|---|---|
| fi | Curwen [C1]: first finger pointing sideways (his "fe"). Modern [J] [CK]: fa turned over, thumb up | Thumb up [J]. It follows the one rule (raised = parent turned up) and reads at any size |
| te | Curwen [C1]: first finger pointing sideways the other way (his "ta"). Modern [J]: the ti finger pointing down | Finger down [J] |
| si | Curwen [C1]: forefinger straight at the class (his "se", which is the **raised** so in tonic sol-fa spelling, not our lowered se). Modern [J] [CK]: so lifted, fingers open or thumb away. The app today: the so drawing with a ♯ | So lifted with the fingers opening [J]. Slant alone is too close to so at 34 px; the open fingers make it unmistakable |
| re | Curwen [C2]: "the upturned hand, open, and shewing the palm". KMEIA [K], [J], [T]: flat hand slanting up, palm down | Palm down [K] [J], the form taught in Australia |
| la | KMEIA [K] and [J]: relaxed, hanging from the wrist. [T]: "curved palm, as if holding a ball" | Drooping from the wrist (also the coordinator's convention) |
| ra | [J] shows the re slant with the thumb dropped. The plain rule would give "re turned down", which would look like me | Thumb let fall: decision 4 |
| Height of do′ | [J]: ti at eye level (so do′ above). [L]: upper do at eye level. [T]: above the head. The app's Keys room says "high do at eye level" | ti eye level, do′ forehead; change the app sentence when this is built: decision 5 |
| Viewpoint | Curwen [C1]: seen from the teacher's left, not from the front. Charts [K] [J] draw the same picture | Section 4 |
| Spellings | The app's scale data has `ma` and `ta` (and `le`, `se`, `ra`). [J] has me, te, le, se, ra | me and te: decision 6 |

Nothing in [J] looks wrong. The one place I am reading rather than quoting is ra.

## 3. How the app draws the ladder today (measured, headless Chrome)

- **Ear Lab melody desk.** A column of buttons, one per solfa step. 1366 × 768: ladder 292 px wide, row 49 px, the KMEIA picture in a 76 × 40 box (drawn about 76 × 34), then the syllable letter at 16 px, "home" at the right; the stave sits to the right of the ladder. 390: ladder 328 px wide under the stave, row 44 px, picture box 64 × 34 (drawn about 64 × 29). The pictures are PNG data URIs, pre-tinted gold. si is the so picture with a small ♯.
- **Keys room, "Sing it · hand signs".** Rows of syllable, degree, note name and a written description ("closed fist"); no picture. Chromatic steps read "chromatic syllable: raised fi".
- The app has one theme (dark). The light renders on the sheet are for print and booklets.

Proposed slots (shown in the mock-ups): 55 × 44 on the desktop ladder, 45 × 36 on the phone ladder, 50 × 40 in the Keys rows (42.5 × 34 on phones). Row heights do not change (49 and 44 px), there is no sideways scroll at 390, and no text is below the 11 px floor. The new frame is squarer than the KMEIA strip (80 × 64 against roughly 2 : 1), so a tilted hand gets the same room as a level one and the ladder column gets 20 px back.

## 4. Viewpoint

**One right hand, the wrist entering from the right and the fingers towards the left: the signer's own hand, held across in front of the body.** It is the picture a student sees looking at their own right hand making so (palm towards them, thumb on top), and it is also Curwen's stated view ("as seen from the left of the teacher, not as seen from the front"), so it agrees with the KMEIA chart students already know.

One honest caveat. For the palm-down signs (do, re, mi, la, ti) a student looking down sees more of the back of the hand than the drawing shows; like every chart, the drawing lowers the eye to hand height so the shape reads as a silhouette. A true front view (what the class sees of the teacher) was rejected: do becomes a row of knuckles and mi a thin edge, and re, mi and me can no longer be told apart.

A left-handed mirror set is one transform away if wanted.

## 5. The drawings, and why they are original

- **Made from nothing but our own coordinates.** Every outline is a Bezier path typed by hand in `build/gen.py`. No reference image was traced, vectorised, overlaid or opened in a drawing tool; the references were read once for the gesture and described in words (section 2) before any drawing began.
- **A system the references do not have.** Seven base hands only (fist, blade, fa, so, open so, la, ti). Each chromatic sign is its parent placed again by rotation or by turning it over, which is the teaching rule itself (raised = turned up, lowered = turned down) made visible. ra has the blade with the thumb let fall.
- **Our own line.** Two weights of one round-nib line (outline and inner lines), a 10% tint of the same colour inside the silhouette so the hand has body at 34 px, the wrist left open and closed by a single cuff arc borrowed from the Garden's corner curl. Fingers are simplified to what a sign needs: no nails, no knuckle shading, no sleeve.
- **Unlike each reference.** The KMEIA chart is a fine naturalistic pencil sketch; Curwen's plate is a cross-hatched engraving with shirt cuffs; Classics for Kids is a loose realistic outline; Teach Beside Me and Midnight Music are flat-colour clip art. Ours is a constructed monoline with a tinted silhouette and a cuff arc, in a different frame (80 × 64), with different proportions. What is shared is only what the gesture dictates: a fist is a fist, and the hand comes in from the right as in Curwen's 1870s public-domain plate.
- **Colour.** Each drawing is one colour (`currentColor`): gold on the Ear Lab ladder, the degree colour in the Keys room, ink on paper.

**Small sizes.** Checked at 42 × 34 (sheet, "signs that must not be confused", and `png/ladder_mock_390.png`): re and ti differ in mass (blade against fist with a finger); fa and ti differ in direction (thumb down against finger up); re, ri, me and ra differ by slope and by ra's thumb; so, si and se differ by fan and tilt; la, le and li by the direction of the fingers; fa and fi, ti and te are each other upside down.

**My own criticism, so you can judge it with me.** (1) The do fist is the weakest drawing: it reads a little like a mitten at large size. (2) li (la turned up) is the least natural hand. (3) The line is clean rather than rough: it is pen-like, not sketchy. If you want more of the hand in it (a drier, slightly uneven ink line), that is a second pass on the same shapes, not a redraw. I would take one round of your corrections on the shapes before anything is built.

## 6. Decisions for Justin

1. **Replace the KMEIA drawings everywhere, or use ours only for the chromatic signs?** Recommend **replace everywhere**: one look across all 18 signs, no join between two drawing styles on a ladder that has both (every minor ladder has si), single-colour SVG that takes the degree colour and stays sharp on a teaching screen, about 20 px more room in the ladder, and no third-party artwork left in the app. The KMEIA credit in the Ear Lab note, the Credits panel and `NOTICE.md` would then come out, replaced by a line that the signs are Curwen's and the drawings are the app's own. The cost is that the KMEIA sketches are the ones Australian students know and are, frankly, more lifelike than mine; if you would rather keep them, ours still fills the chromatic gaps, with a visible change of style.
2. **Approve the convention for the chromatic signs** as drawn from your chart: each is its parent turned up (raised) or down (lowered), with fi = thumb up, te = ti finger down, not Curwen's sideways pointing. Recommend **yes**.
3. **si.** So lifted with the fingers opening (drawn), or so simply slanted up with the fingers together. Recommend **fingers opening**; it replaces today's so-plus-♯.
4. **ra.** The re slant with the thumb let fall (drawn, my reading of your chart), or another form you teach. Recommend **as drawn**, but this is the one sign I would like you to make with your own hand and confirm.
5. **Heights.** do waist, ti eye level, do′ forehead, the rest evenly between, chromatic signs between their neighbours. The Keys room sentence "high do at eye level" changes to match. Recommend **yes**.
6. **Spellings.** Your chart has me and te; the app's scale data has `ma` and `ta`. Recommend **me and te app-wide** (le, se, ra are already so), as a register item with a test, since the Ear Lab and the Keys room both read that data. so stays "so" (not "sol").
7. **Viewpoint.** One right hand, wrist from the right, as in section 4. Recommend **yes**. Say if you want the left-hand mirror offered as a setting.
8. **Where the signs appear.** Recommend the Ear Lab ladder (as now) **and** the Keys room "Sing it" rows, where today there are only words, beside the words. Sizes as in section 3.
9. **Line.** Keep the clean pen line, or ask for a rougher ink pass. Recommend **approve the shapes first**, then decide.

## 7. Not done in this step

- No change to `index.html`, `NOTICE.md` or the tests. Building it is a register item after approval (Sonnet for the wiring, a unit test that every syllable in `SCALES` has a sign, layout test at 390).
- The Curwen quotations in [C2] come from OCR text and want checking against the page scan.
- No independent check of the drawings by a second model or by a Kodály colleague yet; decision 4 in particular rests on one small picture.
