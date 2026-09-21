# Style

The PSP dialog box is short. The English lines already wrap with `(*LINE_BREAK*)`. Keep that wrapping. A German sentence that overruns the box gets cut off in-game, not in the file.

## File format

- One dialog string per line, in double quotes.
- Do not add or remove lines unless you also change the matching `.DEC` (`ld_text` indices).
- Leave every `(*TAG*)` intact, including commas inside tags.
- Comments after a string (`// Shows options: ...`) can stay. Update them if you translate those options. Currently there is no option for me to change these options. So dialogue options stays in english currently.

## Character set

The encoding table does not have `ä ö ü Ä Ö Ü ß`. Don't use them or it will look messed up
Use these instead:

| Symbols | Solution |
| ------- | -------- |
| Ä, ä    | Ae, ae   |
| Ö, ö    | Oe, oe   |
| Ü, ü    | Ue, ue   |
| ß       | ss       |

If you know how to make a font that can use them, provide the info about it.

If a character does not exist in the table, PersonaFlowReader will not encode it cleanly. Stick to letters in that table, ASCII punctuation, and the existing tags.

## Tone

The US script is casual high-school talk mixed with occult jargon. German should stay spoken, not bookish.

- Students: `Du`, `du`
- Most adults (Teachers, Nurses etc) to students: `Du`, `du`
- Students and adults to other adults: `Sie`, unless their are quite familiar

## Names

Canonical forms live in `docs/glossary.md`. In dialogue, use the name the English line used (Mark, not Masao), unless the line is a profile dump that gives the full Japanese name.

## Line length

Aim to match the English line count per box. If German needs an extra `(*LINE_BREAK*)`, you are probably too long. But u can test if u can add `(*LINE_BREAK*)`, the game will automatically scroll the box until now. I don't know how it will affect later moments in the game yet.

## Things that are easy to break

- `(*SHOW_OPTIONS,25*)` IDs are not text. The option strings themselves live elsewhere. The comment at end of line is only a hint. This for example is dialogue option at the ID 25. I don't know yet how to get them and translate them.
- `(*WAIT,16*)` ticks stay numeric.
- `(*SET_COLOR,R*)` and `(*SET_COLOR,_*)` wrap colored words. Keep both.
- `(*PLAYER_FIRST_NAME*)` / `(*PLAYER_NICKNAME*)` are the save-file name. Do not replace them with "Held", or "MC" or something.
