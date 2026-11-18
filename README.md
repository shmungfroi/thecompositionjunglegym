# The Composition Jungle Gym

A browser app for learning composition. It runs as one HTML file, with no build step and no install. Open `index.html` or visit the GitHub Pages site.

## What's in it

- **Level 1–2:** chords, keys and scales, voicing, and the Gym, a progression builder. The Gym offers several metres and grooves and exports MIDI.
- **The Climbs (1–13):**
  - Climb 1: drones and modes
  - Climb 2: species counterpoint, first to fifth species, with three voices and C clefs
  - Climbs 3–12: functional harmony, from tonal architecture to reharmonisation
  - Climb 13: imitation and fugue
- **Level 3, Forms:**
  - phrase, period and sentence (with dynamics and articulation)
  - 12-bar, jazz and minor blues
  - rhythm changes
  - rag
  - rondo
  - theme and variations
  - sonata form and sonata-rondo
- **Level 3, Analysis:** ten engraved scores by Bach, Mozart, Joplin and Chopin, with form and cadence layers and playback that follows the score.
- **Level 3, Ear Lab:** seven aural drills. Melodic dictation uses movable do and Curwen hand signs.
- **Syllabus tags:** NSW Music 7–10 (2024) elements of music, Stage 6 (2025) Music language strands and outcome codes, plus a syllabus map in the journal.

## Files

- `index.html`: the whole app. It loads VexFlow from jsDelivr.
- `scores/`: the Analysis room's scores, engraved with Verovio, and `meta.json` (events, sections, cadences). These must be served over HTTP. GitHub Pages does this; opening the file directly from disk does not.

## Credits and licences

Every third-party source, its licence, and the changes made are listed in [NOTICE.md](NOTICE.md) and in the Credits panel in the app's footer (sound credits are also in `audio/CREDITS.md`).

Because some of the score data is CC BY-NC-SA 4.0, the app as a whole is for non-commercial educational use.

© Justin Ossher.
