# script/

German event text, grouped the same way the game packs it.

These are the `.TXT` files we translate. The matching `.EVS` and `.DEC` stay in PersonaFlowReader. Do not put those in git.

Edit the copies in here. Not the ones inside PersonaFlowReader.

How a line should look is in `docs/style.md`. Names and terms in `docs/glossary.md`. How far we are is in `docs/completion.md`.

## Packs

The number you pass to the tools is the pack. `0` = E0, `1` = E1, `2` = E2 and so on.

```
E0/            SEBEC-route events
E1/            Snow Queen events
E2/
E3/
E4/
eboot/         EBOOT dumps: choice menus, difficulty screen, ...
```

E0 has 223 scenes. E1-E4 are empty except `.gitkeep` until we extract them.

## Note

E0_001, E0_002 and E0_003 have the same entries for the `Agastya-Tree` (The tree where you save your game). I do not know why but I translated them anyways in case they are used somewhere in the game.

## Files

One file is one event. The name looks like `E0_000.TXT`, `E0_001.TXT` and so on.

We count scenes, not binaries. If `docs/completion.md` says `004/223` that means E0_000 through E0_003.

## eboot/

PersonaFlowReader does not extract these. They live in a decrypted `EBOOT.BIN`. Each `.txt` is one dump. `patch-iso.sh eboot` packs every file in this folder back into the EBOOT.

| File             | What it is |
| ---------------- | ---------- |
| `options.txt`    | Yes/No boxes, shops, Velvet Room, Mark vs Brown (`*SHOW_OPTIONS*`) |
| `difficulty.txt` | Difficulty screen prompt and help text |
| `SystemUI.txt`   | Memory Stick / system data loaded |
| `BattleUI.txt`   | Battle commands and battle messages |
| `LevelUpUI.txt`  | Persona rank-up messages |
| `StatsUI.txt`    | Strength / Vitality / ... increased |
| `DungeonUI.txt`  | Treasure chests and obtain messages |
| `CasinoUI.txt`   | Casino minigame help |
| `VelvetUI.txt`   | Igor / Velvet Room tutorials |
| `LocationUI.txt` | Room names in the corner, e.g. 1F Empty Classroom |
| `NameUI.txt`     | Name entry: Is this all right? |
| `ItemNames.txt`  | Item names |
| `ItemHelp.txt`   | Item descriptions |
| `SkillNames.txt` | Skill names (Agi, Bufu, ... can stay English) |
| `SkillHelp.txt`  | Skill descriptions |

```bash
./tools/extract-eboot-options.sh   # writes missing dumps only
# edit script/eboot/*.txt
./tools/patch-iso.sh eboot
```

Do not change the `=====` header lines. Leave every `(*TAG*)` in place, including `(*PAD,N*)` and `(*0044*)`. A German line that is longer than `BYTES` is refused. Details in `tools/README.md`.

The opening line "I dreamed I was a butterfly" is not in the EBOOT or the event `.TXT` files. It is almost certainly a title/opening texture or movie, not editable text.

The pause menu labels (Skills, Items, Command, Use skills, Confirm, Back, NEW MOON, Time) are images in `cm_menu.bin` / `ch_menu.bin` / `bt_menu.bin`, not EBOOT strings. This pipeline cannot edit them.
