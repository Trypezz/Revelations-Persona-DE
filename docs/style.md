# Style

The PSP dialog box is short. The English lines already wrap with `(*LINE_BREAK*)`. Keep that wrapping. A German sentence that overruns the box gets cut off in-game, not in the file.

## File format

- One dialog string per line, in double quotes.
- Do not add or remove lines unless you also change the matching `.DEC` (`ld_text` indices).
- Leave every `(*TAG*)` intact, including commas inside tags.
- Comments after a string (`// Shows options: ...`) can stay. Update them if you translate those options. The real option text is `script/eboot/options.txt`, not this comment. The difficulty screen prompt is `script/eboot/difficulty.txt`.

## Character set

The encoding table **does** have `ä ö ü Ä Ö Ü`. `ß` is still missing, use `ss`.

Without the HD-UI font they look wrong in-game. That is why the root README tells you to paste `2FontB.png` into the emulator texture folder if you have the HD-UI Mod. If you do not have the Mod please still use umlauts, they appear like a dot, a simple placeholder.

If a character does not exist in the table, PersonaFlowReader will not encode it. Stick to letters in that table, ASCII punctuation, and the existing tags.

## Tone

The US script is casual high-school talk mixed with occult jargon. German should stay spoken, not bookish.

- Students to other studens: `Du`, `du`
- Most adults (Teachers, Nurses etc) to students: `Du`, `du`
- Students and adults to other adults: `Sie`, unless their are quite familiar

## Names

Canonical forms live in `docs/glossary.md`. In dialogue, use the name the English line used (Mark, not Masao), unless the line is a profile dump that gives the full Japanese name.

## Line length

Aim to match the English line count per box. If German needs an extra `(*LINE_BREAK*)`, you are probably too long. But u can test if u can add `(*LINE_BREAK*)`, the game will automatically scroll the box until now. I don't know how it will affect later moments in the game yet.

## Things that are easy to break

- `(*SHOW_OPTIONS,25*)` IDs are not text. The strings are in `script/eboot/options.txt`. Other leftover English (difficulty prompt, and later more UI) is other files in `script/eboot/`. The comment at the end of an event line is only a hint.
- `(*WAIT,16*)` ticks stay numeric.
- `(*SET_COLOR,R*)` and `(*SET_COLOR,_*)` wrap colored words. Keep both.
- `(*PLAYER_FIRST_NAME*)` / `(*PLAYER_NICKNAME*)` are the save-file name. Do not replace them with "Held", or "MC" or something.
