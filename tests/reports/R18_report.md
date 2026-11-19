# R18 report: Night and Day song exemplars (branch 048-r18, from live 0.47)

## Outcome
All four "Night and Day" (Cole Porter) exemplars were replaced with visible gap cards (existing SONGGAPS pattern,
"Gap: no verified example yet"). No lyrics were quoted. No new unverified text was added.

## Verification findings
- jazzstandards.com (https://www.jazzstandards.com/compositions-0/nightandday.htm) states original key E-flat major, but gives
  no key for any recording (Astaire/Reisman 1932, Sinatra/Stordahl 1942, Sinatra 1957 "A Swingin' Affair!"); it does not list
  Ella Fitzgerald among chart recordings (only soundtrack uses).
- learnjazzstandards.com (https://www.learnjazzstandards.com/?p=2479): "most commonly played in C, E-flat or F" (supports the
  reworded key, but only for the song, not for any recording).
- Searches for a source that gives the key or chord at a bar for a named recording (Sinatra 1942, Sinatra 1957, Ella Fitzgerald
  Cole Porter Song Book 1956, Astaire/Reisman 1932) found only existence/discography pages and lead sheets; none confirm the
  chord at the stated place in the recording. The brief requires two sources or one authoritative source per recording, so no
  recording could be named. "Any standard jazz reading" and "Fred Astaire stage original 1932" (a stage show, not a recording) were
  therefore removed rather than reworded.

## Entries (before / after / sources)
| Chord | Before | After |
|---|---|---|
| 7 (Musical theatre) | Night and Day; key "charted in C, E-flat and F"; recording "Fred Astaire stage original 1932 (standard jazz readings share the changes)"; G7 to Cmaj7 as charted in C. Sources: guitarcomposerstoolbox (chart in C), learnjazzstandards | Gap card, Musical theatre slot |
| m7 (Musical theatre) | key "E-flat (original key per jazzstandards.com; chart in C)"; recording as above; Am7b5-Ab m7-Gm7-Gb dim7-Fm7-Bb7 chain "original key E-flat". Sources: guitarcomposerstoolbox, Wikipedia half-diminished, jazzstandards | Gap card, Musical theatre slot |
| m7b5 (Musical theatre) | key "E-flat (original key per jazzstandards.com; chart in C)"; Am7b5 opening the chain. Same sources | Gap card, Musical theatre slot |
| dim7 (Blues/jazz) | recording "Any standard jazz reading; original key E-flat"; Gb dim7 fourth chord of chain; key "E-flat (original key per jazzstandards.com...)". Sources: jazzstandards, guitarcomposerstoolbox, Wikipedia | Gap card, Blues/jazz slot |

Other entries in those chord pages are untouched. Chart-level facts (changes in C/E-flat/F) remain supportable and could be
reinstated as an entry once a named recording is verified (candidates to check with a transcription or a score: Sinatra 1942
Columbia/Stordahl, Ella Fitzgerald 1956 Verve).

## Code change
index.html: removed the four entries from `SONGS`; `SONGGAPS` gained `"7"`, `"m7"`, `"m7b5"` (Musical theatre) and `"dim7"` (Blues/jazz).

## Tests
content_lint: pass. pageerrors: pass (1053 s).
