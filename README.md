# Revelations: Persona DE

<img align="right" src="https://visitor-badge.laobi.icu/badge?page_id=Trypezz.Revelations-Persona-DE&"  />

_**HEAVILY WIP**_
---

Unofficial German translation of Revelations: Persona for the PSP.

This repo is the translation. German `.TXT` files, notes, and the scripts that copy those files into a local tool. The game itself does not belong here.

Persona is Atlus / SEGA. This project is not affiliated with them. You need your own dump. Do not open a pull request that adds an ISO, `EBOOT.BIN`, or extracted UMD files.

## Important

- This repo is designed to fail on your system. I do not ship the important Python script that patches the EBOOT.BIN, so you are not able to translate anything in there.
- Still heavily WIP. Only the first school scenes are translated yet.
- To make umlauts readable in-game you need the [`HD-UI Mod`](https://gamebanana.com/mods/309876) and paste the `2FontB.png` from PersonaFlowReader into `PSP/TEXTURES/ULUS10432` of your emulator.

## How you work

PersonaFlowReader is still needed. The jar does the encode/archive. You just don't sit in its menu every day. `build-pack.sh` starts it for you. First time you still extract and decode in the menu (see `tools/README.md`). After that, leave it alone.

There are two kinds of text. They use different commands.

### Event text (rooms, NPC talk, cutscenes)

These are `script/E0/*.TXT` (later E1-E4). One file is one room/event.

1. Edit the file in `script/E0/`. Not the copy inside PersonaFlowReader.
2. Build and put it into the test ISO:

   ```bash
   ./tools/build-pack.sh 0
   ```

   `0` is pack E0. Use `1` for E1, and so on.

3. Boot `P1_TEST_ISO` in PPSSPP. Walk the room you changed.
4. If it works, commit the `.TXT` file. Nothing else.

That is the whole event pipeline. `build-pack.sh` copies the German text, puts untouched rooms back to vanilla, encodes only the German scenes (via the PFR jar), keeps every room at its original size, packs `E0.BIN`, and writes it into the test ISO.

Do **not** encode the whole `extracted/E0/` folder in the PersonaFlowReader menu. That rewrites rooms you never translated, later rooms slide, and the game loading-loops.

### Menus / UI (Yes/No, room names, battle text, items)

These are `script/eboot/*.txt`. They live in the decrypted EBOOT, not in E0.BIN.

1. Edit the file in `script/eboot/`. Leave every `=====` header and every `(*TAG*)` alone. A line longer than `BYTES` is refused.
2. Patch:

   ```bash
   ./tools/patch-iso.sh eboot
   ```

3. Boot the test ISO. Commit the `.txt` if it looks right.

Room names (`LocationUI.txt`) use `(*PAD,N*)` for leading spaces. If the banner shows only the end of the name (`nraum` instead of `Klassenraum`), lower `N`.

How a dialogue line should look is in `docs/style.md`. Names in `docs/glossary.md`. What the packs are is in `script/README.md`.

## First time

```bash
cp config.example.env config.env
./tools/check-setup.sh
```

OK means it is there. FAIL means you cannot work yet. WARN is optional stuff like a test ISO that does not exist until the first patch.

Set three paths in `config.env`:

- `P1_ISO` - your original ISO
- `P1_TEST_ISO` - where a patched copy should be written
- `PFR_ROOT` - the PersonaFlowReader folder that contains `extracted/`, `output/`, and `*.jar`

You also need a decrypted `EBOOT.BIN` in `$PFR_ROOT/OG/`, the `EX.BIN` packs in the same folder, and PersonaFlowReader built once. The jar has to stay there. `build-pack.sh` will not work without it. How to dump and build is in `tools/README.md`.

## Requirements

- [`PersonaFlowReader`](https://github.com/TopCape/PersonaFlowReader)
- p7zip
- python3
- java
- An original Persona 1 PSP ISO and a decrypted `EBOOT.BIN`

## Layout

```
script/          German event text, grouped the same way the game packs it
                 script/eboot/ is EBOOT dumps (menus, difficulty, battle UI, ...)
docs/            glossary, style, how far we are
tools/           copy text to/from PersonaFlowReader, patch your ISO
config.example.env
```

PersonaFlowReader and the ISO should live next to this repo, not inside it. `config.env` points at them.

## What is in git

| In the repo       | Not in the repo                                   |
| ----------------- | ------------------------------------------------- |
| `script/**/*.TXT` | ISOs                                              |
| `script/eboot/`   | decrypted `EBOOT.BIN` (keep that in `OG/`)        |
| `docs/`           | `E0.BIN`–`E4.BIN`, `EBOOT.BIN`                    |
| `tools/`          | `.EVS`, audio, maps, textures dumped from the UMD |
| this README       | PersonaFlowReader itself                          |

`git status` should never show an `.iso` or a `.BIN`. If it does, stop and check `.gitignore`.
