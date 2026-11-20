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
