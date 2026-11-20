# IC_SONGS2_049: independent check

Checker: independent check. I did not build this work and only read the code. I did not edit `index.html`, `tests/content_lint.py` or the fixtures.
Scope: branch `049-songs`, commits `383a2fd` and `607d707` on top of the previous check's base `4dd72a9`. I used the builder report `tests/reports/C18_C20_049_report.md` section "Gotye and C19 (L104)" only to find the claims. I parsed SONGS as JSON from both commits and compared them entry by entry. I fetched every chord source again myself.
Date: 21 Nov 2026.

## Summary

| # | Entry | Result |
|---|---|---|
| 1 | Gotye, "Somebody That I Used to Know": minor triad, Australian pick | PASS |
| 2 | Tones and I, "Dance Monkey": moved to the major-triad Australian pick | PASS (weak but honest; Shoulds) |
| 3 | Encanto cast, "We Don't Talk About Bruno": minor triad, Musical theatre | PASS on the chord claim; slot fit is a decision for Justin (Should) |
| 4 | Troye Sivan, "Dance to This": minor seventh, Australian pick | FAIL (Must: the second source does not support the m7 claim as stated) |
| 5 | Nothing displaced; Shape of You absent | PASS |
| 6 | `content_lint` | PASS (`"passed": true`, song_rules failures `[]`, exit 0) |

## 5. Displacement and Shape of You: PASS

Entry-by-entry diff of SONGS, `4dd72a9` to `607d707`:
- `m`: Dance Monkey was REMOVED from the Australian pick. Gotye was ADDED to the Australian pick, and "We Don't Talk About Bruno" was ADDED to Musical theatre, which was neither filled nor declared a gap before. The other five `m` entries are unchanged.
- `""` (major triad): Dance Monkey was ADDED to the Australian pick, which was empty. Pop, Rock and the declared Metal gap are unchanged.
- `m7`: "Dance to This" was ADDED to the Australian pick, which was empty. Blues/jazz, Pop, Rock and the declared Musical theatre gap are unchanged.
- No other entry in any chord type was added, removed or modified. SONGGAPS is unchanged, and no slot is both filled and declared a gap.
- The string "Shape of You" occurs 0 times in `index.html`.
- The two new post-2015 songs went into empty slots (Bruno, Dance to This). Dance Monkey went into an empty Australian slot. Nothing was displaced, which matches Justin's rule.
- Out of scope, noted only: `383a2fd` also changes `renderSongs` (gaps sorted into slot order) and the lint (slot-honesty function plus fixtures). I did not re-check those here.

## 1. Gotye: PASS

Card: D minor; Dm alternating with C; i (i–♭VII); 2011; single version; "Gotye grew up in Melbourne".
- Hooktheory: D minor; Intro i VII, Verse i VII, Chorus i VII VI VII. https://hooktheory.com/theorytab/view/gotye/somebody-that-i-used-to-know
- Rebel Music Teacher (Emily Langerholc, Oct 2017; quotes no lyrics): D minor (Aeolian); verse alternates Dm and C; chorus Dm, C, B♭. https://rebelmusicteacher.squarespace.com/blog/2017/10/22/aeolian-mode-jazz-samples-in-goytes-somebody-that-i-used-to-know
- Secrets of Songwriting (Gary Ewer, 2012): verse on Dm and C; chorus adds B♭; the key is not named outright. https://secretsofsongwriting.com/?p=5418
- These are three independent sources and none is a lyric site. The minor-triad claim (Dm tonic) is correct.
- Wikipedia gives the single release as 5 July 2011 (Australia and New Zealand) and calls Gotye an Australian singer-songwriter. https://en.wikipedia.org/wiki/Somebody_That_I_Used_to_Know
- Notes: "Clean break-up lyric" is accurate, and no lyric is quoted.
- Should: the phrase "Gotye grew up in Melbourne" has no source on the card. Wikipedia only says "Australian singer-songwriter". Either cite a source for the Melbourne claim or reword to "Australian singer-songwriter".
- Could: the official music video shows both singers nude, body-painted into the backdrop (Wikipedia, same page). The card lists the audio recording, so no ⚠ tag is required. A one-line note would help a teacher who plans to show the video.

## 2. Dance Monkey (major-triad Australian pick): PASS, weak but honest

Card: F♯ minor; D and E major triads (VI, VII) around the F♯m home chord; show `D|`; 2019; original single.
- Hooktheory: F♯ minor; Verse v i VI VII; Pre-chorus and Chorus i VI VII v. https://www.hooktheory.com/theorytab/view/tones-and-i/dance-monkey
- Hit Songs Deconstructed (an independent analysis I found): "Key: F# minor"; "F#m – D – E – C#m (F# minor: i-VI-VII-v)" throughout. https://reports.hitsongsdeconstructed.com/?p=48414
- Skoove: "played in the key of F# minor"; "F#m – D – A – E". It prints no lyrics. https://skoove.com/blog/dance-monkey
- Wikipedia: released 10 May 2019 in Australia; Tones and I is an "Australian singer". https://en.wikipedia.org/wiki/Dance_Monkey

Is it an honest major-triad exemplar? Yes:
- D and E really are major triads, they sound in every loop of the original recording, and the card frames them correctly as VI and VII in a minor key ("lift the loop away from the minor home chord").
- Nothing on the card claims the song is in a major key.
- It is a weak teaching example of the major-triad sound, because students hear a minor-key song overall. The spec asks only that the song genuinely use the chord type, and this one does.
- Should (Justin's call): keep it as an honest "major chords inside a minor key" example, or replace it later with a major-key Australian song.
- Should: Skoove's progression (F♯m–D–A–E) does not match the recording as given by Hooktheory and Hit Songs Deconstructed (F♯m–D–E–C♯m). There is no A chord in the loop. Skoove still contains D and E, so the claim holds, but it is an inaccurate source. Replace it with the Hit Songs Deconstructed report, or annotate the discrepancy.
- Notes: "Clean", with a busking-pressure theme. That is accurate; there are no ⚠ tags and no lyric quote.

## 3. We Don't Talk About Bruno (minor triad, Musical theatre): PASS on the chord claim; slot is Justin's call

Card: C minor; Cm (i) and Fm (iv), with A♭ and G7; 2021; original Encanto soundtrack recording; "from a Disney animated film musical, not a stage show".
- Hooktheory: Verse C harmonic minor i iv V; Verse/Pre-chorus i iv6 V; Chorus VI V; Bridge E♭ major. https://hooktheory.com/theorytab/view/encanto/we-dont-talk-about-bruno
- Ethan Hein: "nominally in C minor"; names Cm, Fm, A♭ and G7, with E♭ and D♭7 in the bridge. https://ethanhein.substack.com/p/we-dont-talk-about-bruno
- These are two independent non-lyric sources, and both name Cm and Fm minor triads. The chord claim is correct.
- Hein's article quotes a few short lyric fragments in the course of analysis. It is not a lyric site, so it still counts, and the card itself quotes no lyrics.
- Wikipedia: single released 19 November 2021 on Walt Disney Records; the named cast perform it; music and lyrics by Lin-Manuel Miranda. https://en.wikipedia.org/wiki/We_Don%27t_Talk_About_Bruno
- Notes: "No content tag raised" is accurate. The theme is described, not quoted.
- Should, wording: Hein says the song "spends very little time on Cm itself" and treats G7 as almost a second tonic. The card's listen-for line "A minor home chord…" overstates how much Cm you hear. Suggest that Listen-for name the Fm–Cm minor colour and the G7 pull rather than a settled home chord.
- Should, slot fit (Justin's decision): it is a film-musical song by a Broadway composer, written as a Broadway-style ensemble number. It is not yet staged.
  - On 7 Oct 2026 Disney announced the first Encanto stage musical, for the Walt Disney Theatre aboard the cruise ship Disney Believe, debuting with the maiden voyage on 18 Dec 2027. https://www.goodmorningamerica.com/travel/story/disney-cruise-ship-feature-1st-encanto-musical-137039370 and https://www.laughingplace.com/disney-parks/encanto-show-disney-believe/ (GMA says Bruno is in the show; Laughing Place does not confirm the song list).
  - Miranda said in July 2026 that a Broadway version is not green-lit. https://www.rova.nz/articles/lin-manuel-miranda-teases-possible-stage-adaptation-of-encanto
  - MTI's Disney licensing list has no Encanto JR. https://www.mtishows.com/disney-shows
  - The card's "not a stage show" is accurate today but will date in Dec 2027. If kept, reword it to something like "film musical; first stage version announced for 2027".
- Could: a dedicated "Film musical" slot label or note, if Justin wants the Musical theatre slot kept for stage works only.

## 4. Dance to This (minor seventh, Australian pick): FAIL

Card: G♯ minor; G♯m7 (i7) with C♯m7, F♯, E; 2018; original single. The Soundfly source is annotated "loop of C♯m9, F♯6, G♯m7(9) and E9, unchanged throughout".
- Hooktheory: chorus only, G♯ minor, 117 BPM; iv7 VII i7 VI (the summary text shows just "i iv VI"). This is a single community transcription. https://www.hooktheory.com/theorytab/view/troye-sivan/dance-to-this
- Soundfly Flypaper https://flypaper.soundfly.com/produce/on-voice-leading-and-tresillo-in-troye-sivan-ariana-grandes-dance-to-this/
  - The "basic chord changes we have throughout the song" are given as plain triads, IV– ♭VII I– ♭VI (C♯m, F♯, G♯m, E): "The chord progression remains the same throughout the piece".
  - G♯m7(9) is introduced as the author's construction: "instead of G#m, we can use extensions to recreate it as G#m7(9)". It is built from notes in the intro guitar melody, and the article says "we can experiment a little bit with reharmonizing it".
  - E9 is likewise "we can add a 9th".
  - I found no C♯m9 or F♯6 in the article text. If they appear in images I could not see them.
- Must:
  - The second source does not independently state that the recording's tonic is a minor-seventh chord. It gives a triad and then proposes the seventh and ninth as an analytical extension.
  - The card's Soundfly annotation therefore misstates the source.
  - On the house rule, the m7 claim rests on one community transcription.
  - Either (a) relabel the entry the way other single-source entries are labelled ("a single community transcription, no second non-lyric source found yet") and correct the Soundfly annotation to "basic loop C♯m–F♯–G♯m–E; the author derives G♯m7(9) from the intro melody", or (b) find a second independent non-lyric source that names G♯m7 or i7, or (c) remove the entry and leave the slot empty.
  - The other web hits are chord-and-lyric sites (guitartabsexplorer, cifraclub), which do not count.
- Other fields pass. Wikipedia: released 13 June 2018 by EMI Music Australia, fourth single from *Bloom*; Sivan is Australian; no explicit content or controversy. https://en.wikipedia.org/wiki/Dance_to_This
- Notes: no content tag. That is accurate, and nothing is quoted.

## 6. content_lint: PASS

Command (as `tests/run_all` calls it): `python3 tests/content_lint.py /home/claude/wt/songs`.
- Result: `"passed": true`, `song_rules.failures: []`, post_2015 = Dance Monkey (2019), Dance to This (2018), We Don't Talk About Bruno (2021). Exit 0.
- The lint does not check source counts or source content, so it cannot catch the Dance to This problem.

## Musts / Shoulds / Coulds

Must
1. Dance to This: fix the m7 sourcing. Correct the Soundfly annotation, then relabel as single-source, find a genuine second source, or remove (section 4).

Should
1. Dance Monkey: replace or annotate Skoove, whose F♯m–D–A–E does not match the recording. Use Hit Songs Deconstructed (F♯m–D–E–C♯m) instead.
2. Dance Monkey: Justin to confirm that a "major chords inside a minor-key song" example is acceptable for the major-triad Australian pick.
3. Bruno: Justin to decide whether a film musical fits "Musical theatre". Reword "not a stage show", given the stage version announced for Dec 2027.
4. Bruno: soften the "minor home chord" wording in Listen-for (Hein: little time on Cm; G7 is almost a second tonic).
5. Gotye: source "grew up in Melbourne" or reword to "Australian singer-songwriter".

Could
1. Gotye: a note that the official video contains body-painted nudity, for teachers who show the video.
2. A "film musical" label if the Musical theatre slot should stay for stage works.
