# C18 and C20 report, 0.49 (songs)

Branch `049-songs`, worktree `/home/claude/wt/songs`. Not pushed. All checks below are self-check; an independent checker reviews sources afterwards.

## C18: Metal slot honesty

Survey of every chord type's Metal slot (data read from `SONGS`):

| Chord | Metal slot song | Verdict |
|---|---|---|
| Power chord (5) | Enter Sandman, Metallica 1991 | Metal. Kept. |
| Major triad | Highway to Hell, AC/DC 1979 | Hard rock, carried an honest fallback note. MOVED OUT, now a declared gap |
| Minor triad (m) | Nothing Else Matters, Metallica 1991 | Metallica ballad; kept (single Hooktheory source, already labelled). Flag for Justin: a metal band, but a ballad |
| 7 | Nothing Else Matters, Metallica 1991 | Kept (two non-lyric sources) |
| sus4 | Wonderwall, Oasis 1995 | Britpop. MOVED OUT, now a declared gap |
| maj7 | Misty, Erroll Garner 1954 | Jazz. MOVED OUT, now a declared gap |
| add9 | Nothing Else Matters, Metallica 1991 | Kept (labelled Hooktheory-only for the placement) |

Slots changed in `index.html`:
1. Major triad, Metal: entry removed; `SONGGAPS[""]=["Metal"]`.
2. sus4, Metal: entry removed; `SONGGAPS["sus4"]` now `["Metal"]`.
3. maj7, Metal: entry removed; `SONGGAPS["maj7"]` now `["Metal"]`.
4. The now-unused content-warning entry for "Highway to Hell" was removed from `WARN`.
No other slot was touched (Gotye/Dance Monkey and all other chords unchanged). Gap cards use the existing SONGGAPS rendering ("Gap: no verified example yet").

Lint (`tests/content_lint.py`, section "song rules"): new checks
- a song in the Metal slot may not carry a fallback note (any fallback means it is a stand-in);
- a slot cannot be both filled and declared a gap;
- every SONGGAPS chord type and slot name must exist.
Self-check: run against the 049 `index.html` it fails on exactly the three removed entries ("Metal slot holds a genre fallback"); on the new file it passes.

### Search for genuine metal replacements: none met the rule, so the slots stay gaps
Checked and rejected (all self-check):
- Metallica "Fade to Black" (1984), major triads: Wikipedia (https://en.wikipedia.org/wiki/Fade_to_Black_(Metallica_song)) confirms heavy metal but gives no key or chords; blog analysis (https://intenseproductions.blogspot.com/2025/06/deconstructing-metallicas-masterful.html) gives Em-C-G-D and E major in the solo, while Hooktheory (https://www.hooktheory.com/theorytab/view/metallica/fade-to-black) gives B minor / A minor / E minor sections. The two disagree, so not high confidence. https://musictheoryforguitar.com/Fade-To-Black-Metallica-Modulation.html names no chords.
- Metallica "Enter Sandman" verse (D and C major triads per the same blog): conflicts with the app's own Hooktheory note that the verse riff has no thirds. Rejected.
- Ghost "Mary on a Cross" (2019), major triads (https://hooktheory.com/theorytab/view/ghost/mary-on-a-cross, B major, vi-I-V / IV-V / I-vi-iii-V): one chord source only, and the song is hard rock leaning rather than clearly metal. Rejected.
- Ghost "Square Hammer" (https://hooktheory.com/theorytab/view/ghost/square-hammer, D minor) and "From the Pinnacle to the Pit" (https://www.hooktheory.com/theorytab/view/ghost/from-the-pinnacle-to-the-pit, E minor): minor keys, no sus4 or maj7 named. Rejected.
- Sabaton "Steel Commanders", Helloween "Forever and One", Manowar "Heart of Steel" (Hooktheory pages): all minor-key, no clean major-triad or sus example. Rejected.
- Metallica chord lesson (https://musicradar.com/how-to/metallica-chords-guitar-lesson): names Emadd9, Dm#5, E5add b9, C5/G only; no sus4, maj7 or major triad. (Welcome Home (Sanitarium) / Emadd9 could be a candidate for the existing madd9 Metal gap; not in scope here, flagged.)
- sus4: Guitar World metal sus article (https://www.guitarworld.com/lessons/metal-life-metal-mike-incorporating-suspended-chords-metal-rhythm-parts) uses the author's own examples; Guitar Player sus article (https://www.guitarplayer.com/lessons/sus-suspended-guitar-chords-lesson-sus2-sus4-7sus4) names only Pantera "Floods" for sus2, no chord or place. Guitar World sus guide (https://www.guitarworld.com/lessons/artist-lessons/the-ultimate-guide-to-sus-chords) names no metal songs. No sus4 metal song found with a source.
- maj7: Heavy Blog Is Heavy (https://www.heavyblogisheavy.com/2016/08/25/beyond-the-veil-seventh-chord-of-a-seventh-chord-or-how-major-seventh-chords-work/) names Opeth "Dirge for November" (2001, stark maj7 near 5:43 in the clean closing section), Animals as Leaders "Tooth and Claw" (2014, intro motif alternates low notes with a maj7), Gorod "Celestial Nature". Genuine metal, but one source only and no key or root given, and no second non-lyric source was found (tab sites carry lyrics or are user transcriptions). Best leads for a later pass: Opeth "Dirge for November" and Animals as Leaders "Tooth and Claw"; each needs a second source naming the chord.

## C20: Shape of You (Ed Sheeran, 2017)

Finding: the recording's sounding key is C-sharp minor; the Am-Dm-F-G chart is the same four chords written 4 semitones lower (C#m-F#m-A-B down a major third = Am-Dm-F-G). It is an easier transposed chart, not a different harmony (a capo on fret 4 over Am shapes sounds C#m).
Sources (none are lyric sites):
1. https://hooktheory.com/theorytab/view/ed-sheeran/shape-of-you : C-sharp minor, 96 BPM, 4/4; intro and chorus i-iv-VI-VII = C#m-F#m-A-B; verse and pre-chorus i-iv-VI-VIIsus4 (ends on Bsus4).
2. https://www.8notes.com/scores/25594.asp : play-along publisher; four chords C#m, F#m, A, B repeated through the intro (no key stated on the page).
3. https://www.musicnotes.com/sheetmusic/dpsm/shape-of-you/MN0173622 : publisher listing; original published key C# minor, quarter note = 96 (Musicnotes states key and tempo only, no chords on the page).
4. https://musicradar.com/news/hits-decoded-how-ed-sheerans-shape-of-you-topped-the-charts : "written in C# minor", 96 bpm; no chords.
5. https://splice.com/blog/how-ed-sheerans-shape-of-you-topped-the-charts/ : C# minor; no chords.
6. https://en.wikipedia.org/wiki/Shape_of_You : C-sharp minor, 96 BPM, C#m-F#m-A-B (i-iv-VI-VII); cites a Musicnotes C# minor listing.
7. https://medium.com/that-good-you-need/weekly-billboard-theory-shape-of-you-bfe15ee92756 : C# minor; four-chord loop; chords not named.
Not used: songs.klang.io (automatic detection said F# minor, an unreliable machine analysis) and the roadiemusic Am-Dm-F-G chart (a transposition).

Does it meet the rule? Chord claim: Hooktheory and 8notes agree on C#m-F#m-A-B, key confirmed by Musicnotes, MusicRadar, Splice, Wikipedia. That is two independent chord sources, so yes. It was NOT added: the only chord types it could illustrate are the minor triad (Pop slot held by "Hello", 2015) and sus4 (Bsus4 in the verse, Pop slot held by "Crazy Little Thing Called Love"), and replacing either is a change to another slot, which this task excludes. Decision for Justin: replace a Pop pick (for example sus4 Pop, to add a 2017 song), or leave it. If added, the card should name C#m, F#m, A and B (Bsus4 in verse), key C-sharp minor, and carry no content tag (clean).

## Gaps now shown
Major triad: Metal. sus4: Metal. maj7: Metal. Existing gaps unchanged: 5, 7, m7, m7b5 Musical theatre; dim7 and maj9 Blues/jazz; madd9 Metal.

## Tests (self-check)
- `python3 tests/content_lint.py .`: passed, 0 failures (53 song entries, 25 scale-song entries, song-rule checks including the new Metal and gap checks; 32 rooms, 21 syllabus codes).
- `python3 tests/unit_test.py .`: 959 checks, 0 failures (needed `npm install` in tests/harness first; node_modules is untracked).
- Other suites not run (content-only change).

## After independent check (IC_C18_C20_049, commit 4dd72a9)
Fixed, within C18 scope only (self-check):
1. Dead regex. `metal_slot_dishonest()` in `tests/content_lint.py` now fails a Metal-slot entry if it has a fallback note, or if its fallback, recording and suitability text together match the not-metal pattern (adds "not metal", "not a metal", "hard rock", "Britpop", "jazz", "stand-in", "fallback"). New fixture file `tests/fixtures/slot_honesty.json`: 4 must-fail cases (Wonderwall with "(Britpop rock, not metal)" and no fallback note; Highway to Hell with "hard rock" text; Misty with "jazz" recording; any entry with a fallback note) and 1 must-pass case (Enter Sandman). The lint checks every fixture gives its stated verdict on each run. Mutation re-run: Wonderwall in the `aug` Metal slot with `fallback: null` and "(Britpop rock, not metal)" now fails (exit 1).
2. Gap cards render in slot order. `renderSongs()` merges song cards and SONGGAPS cards and sorts by the slot order. Checked in the page: sus4 shows Blues/jazz, Pop, Rock, Musical theatre, Metal (gap), Australian pick; major triad shows Pop, Rock, Metal (gap); maj7 shows Blues/jazz, Pop, Rock, Metal (gap); 5 shows the Musical theatre gap between Rock and Metal. No page errors.
Not done, by instruction (for Justin first): other genre slots, gap cards for the 17 other unfilled slots, Nothing Else Matters (checker M1: infobox genre soft rock, power ballad), Gotye / Dance Monkey. Checker S4 (single-source Nothing Else Matters in m and add9) also left as is.
Tests: content_lint passed; unit_test 959 checks, 0 failures; pageerrors_test: 881 random clicks, 0 errors (n_errors 0).

## Gotye and C19 (L104)
All checks self-check.

### 1. Gotye restored (minor triad, Australian pick)
"Somebody That I Used to Know", Gotye (feat. Kimbra), 2011, single version, restored from commit 6d8449d (the last version before the C11 swap). That entry never carried a capo claim or capo link, so nothing was dropped; the key is D minor and the chord is Dm alternating with C. Its single-Hooktheory labels are removed because it now has three sources:
1. https://hooktheory.com/theorytab/view/gotye/somebody-that-i-used-to-know : D minor, i VII in the intro and verse.
2. https://rebelmusicteacher.squarespace.com/blog/2017/10/22/aeolian-mode-jazz-samples-in-goytes-somebody-that-i-used-to-know : D minor; verses move between Dm and C; the chorus adds B-flat.
3. https://secretsofsongwriting.com/?p=5418 : verse on two chords, Dm and C; chorus adds B-flat (key implied, not named outright).
Rejected: https://digitalspace.bradfordcollege.ac.uk/10626277/somebody-that-i-used-to-know-song-analysis/ (gives the key as C, no chords); https://www.thestranger.com/pullout/ask-a-musicologist-14596738/ (key only, a stand-in C; no chords).

### 2. Dance Monkey
It qualifies for another slot: the major-triad Australian pick (that slot was empty). The sources agree on D and E (VI and VII) as major chords in the F-sharp minor loop: Hooktheory (https://www.hooktheory.com/theorytab/view/tones-and-i/dance-monkey) and Skoove (https://skoove.com/blog/dance-monkey), plus Wikipedia (https://en.wikipedia.org/wiki/Dance_Monkey) for release date and nationality. Its card text was rewritten for that chord claim (D and E major triads), not the F-sharp minor tonic. Caveat for the checker: this is a minor-key song, so it is a modest major-triad example (VI and VII only); if that is not acceptable the entry should simply be deleted and the slot stays open.

### 3. C19 additions (empty or Australian slots only; nothing displaced)
Post-2015 songs in the data: 3 (Dance Monkey 2019, Dance to This 2018, We Don't Talk About Bruno 2021), up from 1.
- Minor triad, Musical theatre (was empty): "We Don't Talk About Bruno", Encanto cast, 2021. Sources: https://hooktheory.com/theorytab/view/encanto/we-dont-talk-about-bruno (C harmonic minor; i iv V verse); https://ethanhein.substack.com/p/we-dont-talk-about-bruno (nominally C minor; Cm and Fm triads, Ab, G7); https://en.wikipedia.org/wiki/We_Don%27t_Talk_About_Bruno (19 Nov 2021 release, cast). Caveat: from a Disney animated film musical, not a stage show; the card says so. No content tag (none raised in the sources; described, no lyric quoted).
- Minor seventh, Australian pick (was empty): "Dance to This", Troye Sivan feat. Ariana Grande, 2018. Sources: https://www.hooktheory.com/theorytab/view/troye-sivan/dance-to-this (G-sharp minor, iv7 VII i7 VI); https://flypaper.soundfly.com/produce/on-voice-leading-and-tresillo-in-troye-sivan-ariana-grandes-dance-to-this/ (G-sharp minor, loop C#m9, F#6, G#m7(9), E9); https://en.wikipedia.org/wiki/Dance_to_This (13 June 2018, EMI Music Australia, Bloom; Troye Sivan Australian). The two chord sources agree on the minor-seventh home chord; the card names G#m7, C#m7, F#, E and does not claim the added ninths. https://www.sbs.com.au/voices/article/watch-troye-sivan-debuts-new-music-video-featuring-ariana-grande/8zr4rx68x also calls him an Australian pop singer.
- Shape of You was not added (listening example only, per L104).

### Candidates checked and rejected
- Bruno Mars "24K Magic" (2016): MusicRadar article names Fm9/Fm11 and Bbm9; Hooktheory has i11 and iv7, so no agreement on m9 (https://www.musicradar.com/artists/we-wrote-24k-magic-when-uptown-funk-was-no-1-so-if-you-hear-the-same-spirit-in-that-song-thats-why-a-decade-on-we-look-back-at-the-musical-theory-and-retro-gear-that-shaped-bruno-mars-2016-classic; https://www.hooktheory.com/theorytab/view/bruno-mars/24k-magic); themixreview names no chords.
- Silk Sonic "Leave the Door Open" (2021): robinfrederick.com names no chords; earlier finding stands.
- Silk Sonic "Blast Off" (2021): Stereogum names maj7, 13sus and 7sus chords (https://stereogum.com/2168033/silk-sonic-blast-off-music-theory-explained/columns), one source, and its slots are filled except where it would displace.
- Tame Impala "The Less I Know the Better" (2015): Hooktheory (https://hooktheory.com/theorytab/view/tame-impala/the-less-i-know-the-better) names no maj7, 9 or sus chord.
- Greatest Showman "This Is Me" (2017): ClassicFM (https://www.classicfm.com/discover-music/music-theory/this-is-me-greatest-showman-analysis/) names only a D major final chorus, no chords.
- Hamilton and Dear Evan Hansen songs: only Hooktheory pages located, no second source.
- Kylie Minogue "Padam Padam" (2023): Hooktheory page only, not opened further; no second source found.

### Tests
- content_lint: passed, 56 song entries, 0 failures.
- unit_test: 959 checks, 0 failures.
- pageerrors_test: 0 errors (n_errors 0).

## After IC_SONGS2 (IC_SONGS2_049, commit 28589d2)
Self-check. Only these four items changed.
1. Gotye: "grew up in Melbourne" removed (unsourced). The card now says "Gotye is an Australian singer-songwriter" (the wording used for the other Australian cards; no new source added for it).
2. Dance Monkey: the Skoove source (F#m-D-A-E, an A chord not in the recording) is replaced by https://reports.hitsongsdeconstructed.com/?p=48414 (fetched again: F# minor, F#m-D-E-C#m, one bar each, i-VI-VII-v, D and E major). Hooktheory and Wikipedia stay. Listen-for now reads "Two major chords, D then E, sit inside a minor-key loop...". The slot stays; it remains Justin's decision.
3. Bruno: the "minor home chord" wording is gone. The card now says minor colour from Fm and Cm, G7 pulling back so the key feels as much like G7 as C minor, and little time on C minor itself (follows Ethan Hein). "not a stage show" is replaced by "from the 2021 animated film musical Encanto". The slot stays; Justin decides.
4. Dance to This: searched once more (Hooktheory, Soundfly, Musicnotes transcriber listing, Klang auto-detection, tab sites; none usable as a second non-lyric source for G#m7: Klang is machine detection, Musicnotes' listing and tab sites give no checkable chords or carry lyrics). No second source found, so the entry is labelled single-source as other cards are: where-text says "as transcribed on Hooktheory", the Hooktheory note says the sevenths rest on a single community transcription with no second non-lyric source found yet, chordAsHeard says "per one transcription". The Soundfly note now states only what the article says: basic loop of plain triads C#m, F#, G#m, E; the sevenths and ninths are the author's own suggestions. Wikipedia still supports date, label and nationality.
Tests: content_lint passed (0 failures); unit_test 959 checks, 0 failures. pageerrors_test not re-run (card text only; no rendering code changed).

## Card labels (L106)
Self-check. Dance Monkey (major-triad Australian pick) now carries `label: "Major chords in a minor-key song"` and We Don't Talk About Bruno (minor-triad Musical theatre) carries `label: "Film musical"`. `renderSongs()` shows the label as a chip in the card's genre line, reusing the existing `.lw.th` chip (the ⚠ Themes chip component and its CSS; no new colours or rules). The lint now fails any entry whose `label`, where present, is empty or longer than 40 characters. Checked in the page at 1366 and 390 wide: chip font 11 px (smallest font in the genre line 11 px), no sideways scroll (document width equals window width, card not wider than its box), no page errors. At 390 the long Dance Monkey label wraps to two lines inside the rounded chip; the short one stays on one line.
PNGs (and the script that makes them, `tests/reports/songs_049/render_cards.py`): tests/reports/songs_049/png/dance-monkey_1366.png, dance-monkey_390.png, bruno_1366.png, bruno_390.png.
Tests: content_lint passed; unit_test 959 checks, 0 failures; layout_test 272 views, 0 findings, 0 page errors; pageerrors_test 153 views, 4,196 clicks, 881 random clicks, 0 errors (the first two attempts were killed by the machine, a browser crash and a timeout, and the third completed cleanly).
