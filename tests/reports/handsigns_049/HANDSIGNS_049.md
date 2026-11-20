# Hand signs 0.49: an original set for the Jungle Gym

Design step for approval. Nothing in `index.html` has changed. Branch `049-handsigns`, 20 Nov 2026. Design lead: Fable.

**Round 2 (after Justin, 21:36: "the illustrations are awful. make them much more human").** The round 1 glove-like outlines are gone (git keeps them at `6705031`). All 17 signs are redrawn as naturalistic hands; gestures, viewpoint and heights are unchanged. Sections 1 and 5 describe the new drawings; section 5.3 says what changed per sign and which ones I am still unhappy with.

Justin's brief (20 Nov 21:16): "these are just examples, we must build our own based on these. the principles are common property only the actual art is a possible IP issue."

## 1. What is here

| File | What it is |
|---|---|
| `svg/*.svg` (17) | The full drawings: do re mi fa so la ti, di ri fi si li, te le se me ra. do′ uses `do.svg`. Single colour (`currentColor`: ink line plus one flat tone at 17%), viewBox 80 × 64, about 20 kB each |
| `svg/small/*.svg` (17) | The simplified small-size drawing of each sign, made from the same posed hand: bold contour, the main overlaps, a 20% tint. For the ladder sizes (42 × 34 to about 60 px). About 4 kB each |
| `sheet.html`, `png/sheet_1366.png` | Every sign, labelled, at three sizes, dark and light, plus the look-alike pairs at the phone size |
| `ladder_mock.html`, `png/ladder_mock_1366.png`, `png/ladder_mock_390.png` | Static mock-up of the ladders (major, flats, sharps, la-based minor, Keys room rows) |
| `png/app_earlab_1366.png`, `png/app_earlab_390.png`, `png/app_keys_1366.png`, `png/app_keys_390.png` | The real app at 1366 × 768 and 390 with the new signs swapped in at run time (`build/app_mock.py`; `index.html` untouched) |
| `png/<syllable>.png` (18, incl. `do-high.png`) | Each sign alone (full drawing): 750 × 600, transparent, ink `#1d1a14`, all at the same scale so they keep their relative size when placed in a document |
| `ladder_full.html`, `png/ladder_full.png` | The whole ladder: scale in the centre, lowered signs left, raised signs right, transparent |
| `build/hand3d.py`, `build/poses.py`, `build/ink.py` | The hand model, the seventeen poses, and the drawing derived from them (section 5) |
| `build/build.py`, `build/shots.py`, `build/app_mock.py`, `build/preview.py`, `build/view.py` | Scripts that make the sheet, mock-ups and PNGs. Order: `ink.py` (about 6 minutes), `build.py`, `shots.py`, `app_mock.py` |
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

Proposed slots (shown in the mock-ups, using the small drawings): 55 × 44 on the desktop ladder, 45 × 36 on the phone ladder, 50 × 40 in the Keys rows (42.5 × 34 on phones). Row heights do not change (49 and 44 px), there is no sideways scroll at 390, and no text is below the 11 px floor. The new frame is squarer than the KMEIA strip (80 × 64 against roughly 2 : 1), so a tilted hand gets the same room as a level one and the ladder column gets 20 px back.

## 4. Viewpoint

**One right hand, the wrist entering from the right and the fingers towards the left: the signer's own hand, held across in front of the body.** It is the picture a student sees looking at their own right hand making so (palm towards them, thumb on top), and it is also Curwen's stated view ("as seen from the left of the teacher, not as seen from the front"), so it agrees with the KMEIA chart students already know.

One honest caveat. For the palm-down signs (do, re, mi, la, ti) a student looking down sees more of the back of the hand than the drawing shows; like every chart, the drawing lowers the eye to hand height so the shape reads as a silhouette. A true front view (what the class sees of the teacher) was rejected: do becomes a row of knuckles and mi a thin edge, and re, mi and me can no longer be told apart.

A left-handed mirror set is one transform away if wanted. In round 2 the eye is where the signer's eyes are (above and to the thumb side), so the palm-down signs now show the back of the hand as the signer sees it, which removes most of the caveat above.

## 5. The drawings (round 2), and why they are original

### 5.1 Method: a hand built from measurement, posed, and drawn from what is seen

No chart, photo or other artwork was traced, overlaid or vectorised. The reference for every drawing is a hand I constructed in code.

1. **Bones from anatomical measurement** (`build/hand3d.py`). An adult right hand about 185 mm from wrist to middle fingertip: four metacarpals from the wrist to the knuckles, three phalanges per finger with real lengths (middle finger 48 / 29 / 24 mm, little finger 34 / 19 / 21 mm), the knuckle line in its real arc (index and ring behind the middle, little finger well back), a thumb of three bones rooted at the wrist. Each joint bends only on its real axis.
2. **Flesh.** Tapered rounded segments around the bones, blended where skin is continuous (finger into palm, thumb into its thenar pad, wrist into an elliptical forearm) and kept separate where it is not (finger against finger). Knuckle heads, the thenar and hypothenar pads and the web of the thumb are part of the form. A closed fist is filled where finger pads meet the palm.
3. **Pose** (`build/poses.py`). Each sign is a list of joint angles in degrees. Poses are relaxed, not stiff: no two fingers share an angle, the little finger always curls a little more, the "flat" hand keeps 2° to 13° of bend in every joint.
4. **The signer's eye.** The posed hand is looked at from where the signer's own eyes are: from the thumb side and from above (10° to 40°), slightly turned.
5. **The drawing** (`build/ink.py`) is derived from what that eye sees: the outer contour; every edge where one part passes in front of another; the line between touching fingers; folds at bent joints. Fingernails, knuckle wrinkles, the creases under each finger joint and the three main palm creases are placed on the skin in 3D, so they foreshorten correctly and are drawn only where that skin faces the eye.
6. **Line and tone.** Line weight follows the light (upper left): heavy underneath and on the shadow side, lighter on top, lightest for creases and nails; each line swells and thins along its length. One flat mid-tone lies on the side turned from the light. The forearm ends open, as an illustrator leaves it.
7. **Small sizes.** A second drawing of the same posed hand: bold contour, only the big overlaps, a tint over the whole hand. This is what the ladders use.

Everything is one colour (`currentColor`), so a sign takes the degree colour, gold, or plain ink on paper.

### 5.2 Why it is original

The gestures are Curwen's and common property. The artwork is ours: the hand is our own construction from measurements, the poses are our own numbers, and the lines are computed from our model. The result does not share a contour with any reference: the eye point (above and turned), the proportions, the line and the tone are all different from the KMEIA pencil sketch, Curwen's engraving and the clip-art charts.

### 5.3 What changed per sign, and my own criticism

| Sign | Round 2 | Honest verdict |
|---|---|---|
| do, do′ | A real fist seen from the thumb side and above: knuckle bumps on top, the thumb closed across the front underneath, nail showing | Reads as a human fist, but it is the weakest of the diatonic signs: the thumb is tucked low and the small mark by the index curl is not clear. Small size is a compact shape |
| re | Flat relaxed hand slanting up about 28°, fingers slightly staggered, thumb resting below | Good |
| mi | The same hand, level | Good |
| fa | Loose fist, thumb straight down with its nail | Good; the curled index is a little busy |
| so | Open hand on its edge, palm to the eye with its three creases, thumb up | The best drawing. The thumb is slightly long; one stray patch of tone on the palm |
| la | Hand hanging from a bent wrist, fingers drooping at slightly different angles | Good, a little crowded where the thumb crosses the fingers |
| ti | First finger up and forward, the others closed, thumb across | Good |
| di | The do fist tipped up 28° | As do |
| ri | The re hand at 50° | Good |
| fi | Thumb up, the curled fingers and their nails towards the eye | Good |
| si | The so hand lifted 16°, fingers fanned | Good |
| li | Palm turned up and cupped, fingers curling up | **Unhappy.** The fingers overlap from this eye point and it takes a second to read. A lower eye point would help |
| te | The ti hand pointing down about 36° | Good; the thumb under the finger is slightly awkward |
| le | The la hand dropped further, fingers nearly straight down | **Unhappy.** Hard to tell from la at a glance at card size (clear enough at ladder size by its upright shape); the forearm is cut short to fit the frame |
| se | The so hand tipped down 30°, palm open | Good |
| me | The mi hand sloping down 28°, slightly more relaxed | Good |
| ra | The re hand with the thumb let fall | Good; still the one gesture that needs your confirmation (decision 4) |

General limits. (1) These are drawings computed from a model, not drawn by a person with a pen from a sitter; they read as fine-ink life drawings, but the model's skin is smooth: no veins, tendons or wrinkles beyond the main creases. (2) Hatching was not used; the form is carried by line weight and one flat tone. (3) A full drawing is about 20 kB of path data (about 340 kB for the set, 65 kB for the small set). The app today carries the KMEIA PNGs as data URIs, so this is a like-for-like weight, but it should be a conscious choice at build time: the ladders need only the small set.

**Small sizes.** Checked at 42 × 34 on the sheet ("signs that must not be confused") and in `png/ladder_mock_390.png`, small drawings: re and ti differ in mass (flat hand against fist with a finger); fa and ti in direction; re, ri, me by slope, ra by its thumb; so, si, se by fan and tilt; la is a slanting droop, le upright, li cupped upward; fa and fi, ti and te point opposite ways; do and di differ only by tilt, which is the weakest pair.

## 6. Decisions for Justin

1. **Replace the KMEIA drawings everywhere, or use ours only for the chromatic signs?** Recommend **replace everywhere**: one look across all 18 signs, no join between two drawing styles on a ladder that has both (every minor ladder has si), single-colour SVG that takes the degree colour and stays sharp on a teaching screen, about 20 px more room in the ladder, and no third-party artwork left in the app. The KMEIA credit in the Ear Lab note, the Credits panel and `NOTICE.md` would then come out, replaced by a line that the signs are Curwen's and the drawings are the app's own. The cost is that the KMEIA sketches are the ones Australian students already know; if you would rather keep them, ours still fills the chromatic gaps, with a visible change of style.
2. **Approve the convention for the chromatic signs** as drawn from your chart: each is its parent turned up (raised) or down (lowered), with fi = thumb up, te = ti finger down, not Curwen's sideways pointing. Recommend **yes**.
3. **si.** So lifted with the fingers opening (drawn), or so simply slanted up with the fingers together. Recommend **fingers opening**; it replaces today's so-plus-♯.
4. **ra.** The re slant with the thumb let fall (drawn, my reading of your chart), or another form you teach. Recommend **as drawn**, but this is the one sign I would like you to make with your own hand and confirm.
5. **Heights.** do waist, ti eye level, do′ forehead, the rest evenly between, chromatic signs between their neighbours. The Keys room sentence "high do at eye level" changes to match. Recommend **yes**.
6. **Spellings.** Your chart has me and te; the app's scale data has `ma` and `ta`. Recommend **me and te app-wide** (le, se, ra are already so), as a register item with a test, since the Ear Lab and the Keys room both read that data. so stays "so" (not "sol").
7. **Viewpoint.** One right hand, wrist from the right, as in section 4. Recommend **yes**. Say if you want the left-hand mirror offered as a setting.
8. **Where the signs appear.** Recommend the Ear Lab ladder (as now) **and** the Keys room "Sing it" rows, where today there are only words, beside the words. Sizes as in section 3.
9. **The drawings themselves (round 2).** Approve the naturalistic hands as the direction, with a further pass on do/di, li and le (section 5.3), or name the signs you want redone. Recommend **approve the direction, redo those four**. Two options if you want more: restrained hatching instead of the flat tone, and a sleeve cuff instead of the open forearm.
10. **Two drawings per sign.** Full drawing on cards, teaching screens and print; the simplified small drawing on the ladders (under about 60 px). Recommend **yes**: the full drawing clogs at 34 px.

## 7. Not done in this step

- No change to `index.html`, `NOTICE.md` or the tests. Building it is a register item after approval (Sonnet for the wiring, a unit test that every syllable in `SCALES` has a sign, layout test at 390).
- The Curwen quotations in [C2] come from OCR text and want checking against the page scan.
- No independent check of the drawings by a second model or by a Kodály colleague yet; decision 4 in particular rests on one small picture.
- do/di, li and le want another pass (section 5.3).
- The approval cards in `/home/claude/cards` were re-rendered from the new `png/` files (outside this repository).
