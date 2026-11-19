# NESA syllabus cross-check, Composition Jungle Gym 0.48 (R15)

**Status: self-check by the Sonnet researcher.** An independent reviewer and Justin's teacher check follow. Nothing here is a ruling on syllabus compliance.

App inspected: `/home/claude/wt-check-int`, detached at fde5842, run headless (Chrome + Playwright harness). Rooms, climbs, forms, the Ear Lab drill table, the song data, the scale and chord lists and the syllabus tag tables were read from the running page and the source.

---

## 1. Scope and sources

**Courses:** Music 7–10 (2024) Stages 4 and 5; Music 1, Music 2 and Music Extension 11–12 (2025). Stage 6 is read at Year 11 / Year 12 level.

**Previous check (0.33, updated to 0.36):** not available. It is not on disk, and this session has no Projects tool to read `claude/cjg/CJG_NESA_Crosscheck.md`. This version is built from scratch. The "what changed" list in section 3 relies on the staleness list in drift audit D18, not on the old document's wording. A reader holding the old file should re-strike its lines against section 3.

**NESA pages read** (all on curriculum.nsw.edu.au unless noted):
- Music 7–10 (2024) outcomes: `learning-areas/creative_arts/music-7-10-2024/outcomes`
- Stage 4 Listening content: `.../music-7-10-2024/content/stage-4/faee97b12e`
- Stage 4 elements of music: `.../content/stage-4/fa0e9b0d22`
- Stage 5 Listening and Composing content: `.../content/stage-5/fad56543a9`, `.../fac7101b97`
- Elements of music posters (NSW Department of Education PDF), `creative-arts-7-10-elements-of-music-posters-combined.pdf`
- Music 2 outcomes, overview and Year 11 and Year 12 content: `music-2-11-12-2025/outcomes`, `.../overview`, `.../content/year-11/fa01bd71dc` (drama, movement and entertainment), `fab62d43ac` (20th and 21st centuries), `fa10a3e6b1` (Western art traditions 1), `.../content/year-12/fa2bd248c4` (Western art traditions 2)
- Music 1 outcomes, course structure, Year 11 and Year 12 content: `music-1-11-12-2025/outcomes`, `.../overview/course`, `.../content/year-11/fa0e200b89`, `.../content/year-12/fa18170178`
- Music Extension overview, rationale and outcomes: `music-extension-11-12-2025/overview`, `/rationale`, `/outcomes`

**Could not open or only partly loaded:**
- A first guessed URL (`music-7-10-2023`) was refused by the fetch allowlist. Later URLs, taken from search results, worked.
- Several NESA content pages returned "Loading" placeholders. Stage 5 element names, parts of the Music 2 Year 11 and Year 12 pages, and parts of the Music 1 pages did not render.
- Not read at all: Stage 5 Performing, Stage 4 Performing and Composing detail, Life Skills, Music Extension content pages, Music 2 Year 12 "Music of the last 25 years" and "Elective project" pages, Music 1 Year 12 other two focus areas, assessment and HSC pages.

---

## 2. Coverage by course and stage

Key: **Covered**, **Partly**, **Not covered**, **Teacher-led** (belongs in the classroom, the app only supports it). Judgements are mine from the code and the running page, not from classroom use.

### Stage 4 (MU4-PER-01, MU4-LIS-01, MU4-COM-01)

| Focus area / element | How 0.48 covers it | Status |
|---|---|---|
| Duration: beat, tempo, note values, simple and compound metre, syncopation, ostinato, backbeat | Ear Lab pulse and metre (2/4 to 12/8, 5/4, 7/8) and rhythm dictation (crotchet to semiquaver, dotted, syncopation); Gym metres and grooves (pulse, block, arpeggio, backbeat, swing, hemiola) | Covered |
| Pitch: contour, steps and leaps, tonality (pentatonic, modal, major, minor) | Keys: 17 scales incl. modes, pentatonics, blues; melodic dictation; Climb 1 | Covered |
| Melody (listed as its own element on the Stage 4 page) | Phrase, period and sentence builder; melodic dictation. Not tagged as an element (see section 3b) | Partly |
| Harmony: progressions (I, IV, V, V7), devices (riff, drone, ostinato), notation of pitch (graphic, clefs, tablature) | Chords room (23 qualities, 46 songs), Climbs 1, 3, 4, 5, Gym, Ear Lab chord quality. Staff notation in treble and bass clef. No tablature, no graphic notation | Partly |
| Texture: density, layers and roles, mono/homo/polyphonic | Voices, Climb 2 (polyphony), Analysis scores. No density or layer-role activity for pop or ensemble texture | Partly |
| Performing media and timbre: media, sound-producing techniques, timbral description | Playback: piano, steel and nylon guitar, bass samples, drum parts in Gym grooves. Fret diagrams for guitar, ukulele and bass. No voices, electronic or natural sources; no timbre vocabulary activity | Partly (weak) |
| Dynamics and expression: gradations, articulation, expressive techniques, electronic manipulation | Phrase builder: pp to ff, hairpins, staccato, accent, tenuto. No pizzicato-type techniques, no effects (distortion, delay), no expressive-direction vocabulary | Partly |
| Structure: macro and micro | Forms room (phrase, blues, rag, rondo, theme and variations), riffs and phrases. Verse–chorus and cyclic form not built | Partly |
| Listening: transcribe patterns, use terminology | Ear Lab (rhythm, melody, chords), Australian-first terms (R6) | Covered |
| Music in context: time, culture, purpose, comparing versions, ethical approaches to Aboriginal and Torres Strait Islander music | Song and score metadata (artist, year, period). No cultural or purpose content. The app carries no Aboriginal or Torres Strait Islander material | Teacher-led |
| COM-01 improvise, arrange, compose | Gym, Oracle, Phrase builder, Voices. No improvisation activity | Partly |
| PER-01 performance | Mic singing in Keys, tap rhythm in Ear Lab, guitar and ukulele shapes. Not a performance tool | Teacher-led (support only) |

### Stage 5 (MU5-LIS-01, LIS-02, COM-01, COM-02; PER-01, PER-02 not tagged)

| Outcome / focus | How 0.48 covers it | Status |
|---|---|---|
| LIS-02 evaluate how elements are manipulated and combined | Analysis (10 scores, form and cadence layers), Ear Lab blind analysis, theme and variations techniques | Covered |
| LIS-01 analyse in stylistic, cultural, historical, social contexts | Score notes give period and style. Social and cultural context is not built | Partly / Teacher-led |
| COM-02 manipulate and combine elements | Theme and variations, Climbs 3 to 13, Voices | Covered |
| COM-01 improvise, arrange or compose with stylistic understanding | Forms (blues, rag, rondo, sonata), Climbs, Voices (arranging for four voices). No improvisation | Partly |
| Music of Aboriginal and Torres Strait Islander Cultures; Australian music across contexts | 4 "Australian pick" songs only. No Aboriginal or Torres Strait Islander content, and no cultural-protocol note | Teacher-led / Partly |
| PER-01, PER-02 | Not tagged and not addressed | Teacher-led |

### Music 2, Year 11 (MU2-11P-01/02, 11L-01/02, 11C-01/02)

| Focus area | How 0.48 covers it | Status |
|---|---|---|
| Western art traditions 1 (Baroque, Classical, Romantic): transcribe melodic, harmonic and rhythmic patterns; arrange with diatonic harmony incl. inversions, dominant and secondary sevenths; notate dynamics, articulation | Analysis (Bach, Mozart, Joplin, Chopin), Climbs 2, 3, 7, 13, Forms (sonata, rondo, variations), Voices (SATB), Ear Lab. Ornamentation and period performance practice absent | Covered (analysis, harmony, composing); Not covered (ornamentation); Teacher-led (performing) |
| Music for drama, movement and entertainment: motifs for character and mood, word–music links, one substantial work | 2 musical theatre songs in the chord library. No motif, character or word-setting tool | Not covered / Teacher-led |
| Music of the 20th and 21st centuries: extended techniques, open scores, technology, live plus pre-recorded, post-tonal language | Octatonic and whole-tone scales, Climb 12 (beyond function), jazz harmony and rhythm changes. Latest engraved score is 1839 | Partly (jazz and scales only); Not covered (extended technique, open score, technology) |
| Music language: theoretical, compositional, notational | Theoretical and compositional strong. Notational: staff, key signatures, C clefs in counterpoint only; no alto or tenor clef reading in Keys or Ear Lab | Covered / Covered / Partly |
| Creating: document the creative process | Process log with outcome codes, text export | Covered |
| Performing | Not an app function | Teacher-led |

### Music 2, Year 12 (MU2-12P/L/C)

| Focus area | How 0.48 covers it | Status |
|---|---|---|
| Music of the last 25 years (Australian focus) | Of 46 unique songs, 9 are 2001 or later and none is after 2015. 2 of the 4 Australian picks are in range (Gotye 2011, Tame Impala 2015). Listening map lets a student chart any recording. No analysis of electronic or sound-manipulation techniques, no digital-media or distribution content | Partly (thin) |
| Western art traditions 2 (compare a Western work, 1600 to 25 years ago, with another style; notation methods) | Western side covered. Comparison with another style and non-Western or cultural notations absent | Partly |
| Elective project | Climbs, Forms and Voices support composing; process log supports documentation. Project itself | Teacher-led |
| MU2-12L-01 / 12C-01 (evaluate) | Analysis and Forms feed these, but the codes are never attached (section 3b) | Partly |
| Composing for small mixed ensembles | Voices is SATB only (soprano to bass ranges); no instrument ranges or mixed-ensemble layouts | Partly |

### Music 1, Years 11 and 12 (MU1-11P/L/C, MU1-12P/L/C)

Music 1 is mapped only by Music language strand, as before. Its codes are now published and are not carried (section 3b).

| Focus area / mandatory content | How 0.48 covers it | Status |
|---|---|---|
| Creative practice (Y11): Dorian, Lydian, Mixolydian; cadences; ii/ii° and V7; articulation, dynamics, phrasing | Keys modes, Climb 1, Climbs 4 to 9, Ear Lab cadences; phrase builder expression. Modes are not tested by ear | Covered (harmony, cadence); Partly (modes by ear, expression) |
| Creative practice: DAWs, virtual instruments, effects, graphic scores and DAW visualisations; digital sound sources | Gym exports MIDI. Nothing else | Not covered |
| Songwriting and improvisation | Gym and Oracle. No improvisation | Partly |
| Music of the last 25 years (Y12, Australian focus) | As Music 2 | Partly (thin) |
| Music across cultures, traditions and time; Music for screen, stage and story (Y12) | Not covered. Global music culture and electronic music are mandatory repertoire categories; the app has neither | Not covered |
| Mandatory repertoire: Aboriginal and Torres Strait Islander; contemporary popular; Western art; jazz; global; electronic | Popular, Western art and jazz present. Aboriginal and Torres Strait Islander teacher-led. Global and electronic absent | Partly |
| Y12 composition log (research, experimentation, creative risk, compositional language, link to audio) | Free-text process log, timestamped, tagged with outcome codes, exportable. No audio link and no prompts for the listed log headings | Partly |

### Music Extension, Year 12 (MUE-12L/P/M/C)

The syllabus page says implementation starts in 2027 and the first HSC exam is 2028. Focus areas read: Interpretative practices (musical sources, practices, contexts) and Major work (performance, composition or musicology). I found no Year 11 Extension outcomes.

| Outcome group | How 0.48 covers it | Status |
|---|---|---|
| MUE-12L-01/02 score study, musical intent and effect | Analysis scores and layers | Partly |
| MUE-12C-01/02 composed and notated pieces, influences on composing | Climb 13, Forms, process log | Partly |
| MUE-12P-01/02 performance interpretation | Not an app function | Teacher-led |
| MUE-12M-01/02 research on primary and secondary sources; assumptions in practices | Not addressed | Teacher-led |

---

## 3. What changed since 0.36

Struck lines are the staleness items named in drift audit D18. I could not check them against the old document's own text.

- ~~Playback is one synthesised tone.~~ Sampled piano, steel and nylon guitar and bass since 0.40. Still no voice, electronic or natural-sound timbres.
- ~~No dynamics or articulation.~~ Phrase builder has pp to ff, hairpins, staccato, accent and tenuto (0.36).
- ~~Not covered: augmentation and diminution.~~ In Climb 13 (0.35).
- ~~Not covered: hemiola and backbeat.~~ Gym grooves (0.35).
- ~~Not covered: alto and tenor clefs.~~ C clefs in Climb 2 counterpoint (0.36). Not in Keys or Ear Lab.
- ~~Not covered: irregular metre.~~ Ear Lab pulse and metre includes 5/4 and 7/8; Gym offers both.
- ~~No content covers the last 25 years.~~ 9 of 46 songs are 2001 or later (Gotye 2011, Tame Impala 2015). **Newest song in 0.48 is 2015**, so the app does not yet reach the present. "Songs spanning to the present" is not true at this commit.
- Still true: Aboriginal and Torres Strait Islander repertoire is teacher-led. The source has no Aboriginal or Torres Strait Islander content at all, only the word "Australian" in four song slots.
- New since 0.36 (verified in this build): Ear Lab with seven drills and Stage-gated rungs; Australian-first terms (R6); Analysis listening map for any recording; Stage 4/5/6 switch; syllabus tag bar and journal map.

### 3b. Syllabus codes and tags carried by the app (checked against NESA)

All 13 codes in the app exist today and their wording matches NESA's outcomes pages. Problems are in how they are used and in what is missing:

1. **Year 11 composing carries a Year 12 code.** Composing tools (Climbs 2, 8, 10, 11, 12 and 13, Forms sonata and rhythm changes) are tagged `MU2-12C-02` only. **`MU2-11C-02` ("composes music with stylistic understanding of Compositional language and expressive intent") is not in the app.** A Year 11 student sees a Year 12 outcome.
2. **`MU2-11L-01` is missing.** It is the Year 11 outcome for how Music context and Music language shape meaning.
3. **`MU2-12L-01` and `MU2-12C-01` are defined but attached to nothing.** Dead entries.
4. **Outdated note.** The panel says Music 1 outcome codes are "not listed here yet". NESA publishes `MU1-11P-01/02, 11L-01/02, 11C-01/02` and the Year 12 set, so they could now be carried. `MUE-12L/P/M/C` (Extension) are also absent. Stage 5 `MU5-PER-01/02` are absent.
5. **Elements list is short.** The Stage 4 content page lists Melody and Harmony as elements of music alongside Duration, Pitch, Texture, Performing media and timbre, Dynamics and expression, and Structure. The app's list has no Melody or Harmony, so chord content is tagged "Pitch". Caveat: I saw this on the Stage 4 page only; the Stage 5 element names did not load.
6. **Wording note, low priority.** `MU4-LIS-01` matches the outcomes page ("...stylistic, cultural, historical or social contexts and the elements of music"). The Stage 4 Listening content page words it "in relation to its contexts and the elements of music". The two NESA pages differ; the teacher should choose which to show.
7. **Judgement calls on mapping, for the teacher.** Ear Lab is tagged `MU2-11L-02` (analyses music and musical evidence); an aural-skills outcome such as `MU1-11L-02` ("uses aural skills to identify and describe features of music") is a closer fit for Music 1. The Chords room carries `MU4-PER-01` (performance) although it is a reference room. The Fugue form entry (a pointer to Climb 13) has no tag of its own.

---

## 4. Gaps worth building, ranked

1. **Music of the last 25 years, 2016 to the present, Australian focus.** Required in Year 12 of both Music 1 and Music 2. Newest song is 2015; 9 of 46 songs are in range. Add recent songs and recent Australian examples, and extend the listening map prompts. Highest value for the smallest build.
2. **Timbre, performing media and sound manipulation.** Stage 4 and Music 1 and 2 name voices, electronic and natural sources, sound-producing techniques, effects (distortion, delay) and analysis of sound manipulation. The app has four sampled instruments. Candidates: a timbre-description drill, voice and electronic playback options, an effects demo.
3. **Notation breadth.** Alto and tenor clefs in Keys and Ear Lab; tablature; graphic scores and DAW-style visualisations (Music 1 Year 11, Stage 4 pitch notation).
4. **Music for drama, movement and entertainment (Music 2 Year 11).** Motif and leitmotif for character and mood, word–music rhythm and melody links. Only 2 musical theatre songs now.
5. **Improvisation, and 20th and 21st century language.** No improvisation activity at any stage though it appears in Stage 4 and 5 composing and in Music 2 Year 11 performing. Post-tonal and extended-technique content is limited to two scales and a "Beyond function" climb.

Smaller items: ornamentation signs; global and electronic music for Music 1 (mandatory repertoire categories); Year 12 composition-log prompts for Music 1; a short cultural-protocol note for Aboriginal and Torres Strait Islander repertoire (NESA requires ICIP protocols; the app stays teacher-led and should say so); mixed-ensemble ranges beyond SATB.

Code fixes (no new content): items 1 to 4 and 5 in section 3b.

---

## 5. Limits of this check

- Self-check only. No independent review, no teacher check yet, no classroom use.
- The previous cross-check was unavailable, so section 3 rests on the D18 list.
- NESA pages partly failed to load (see section 1). Element names for Stage 5, parts of Music 2 Year 12 and Music 1 pages, and all Extension content pages are unverified. Stage 5 Performing and Life Skills were not read.
- Coverage is judged from source code, data tables and a headless run. I did not review screens for usability, and I did not test teaching effectiveness.
- "Covered" means a feature addresses the content, not that it meets the full syllabus statement or assessment requirements.
- Aboriginal and Torres Strait Islander content is outside what an app can responsibly generate; "Teacher-led" is a recommendation, not a gap to close by building.
- Dates for implementation of the Music 1 and Music 2 syllabuses were not checked. Music Extension's 2027 start is from the NESA overview page.
