# Revelations: Persona DE

Unofficial German translation of Revelations: Persona for the PSP.

This repo is the translation. German `.TXT` files, notes, and the scripts that copy those files into a local tool. The game itself does not belong here.

Persona is Atlus / SEGA. This project is not affiliated with them. You need your own dump. Do not open a pull request that adds an ISO, `EBOOT.BIN`, or extracted UMD files.

## IMPORTANT NOTE

This repo currently works only on Linux. On Windows you need to make many things manual.

## First check if everything is setup correctly

Checks if config, ISO, PersonaFlowReader and the tools are in place.

```bash
./tools/check-setup.sh
```

OK means it is there. FAIL means you cannot work yet. WARN is optional stuff like a test ISO that does not exist until the first patch.

## Requirements to work with this repo

- [`PersonaFlowReader`](https://github.com/TopCape/PersonaFlowReader) (Info: I did not need to use some EBOOT patches they talk about yet)
- p7zip
- python3 -> For scripts (getOffsets.sh, patch-iso.sh)
- java -> Needed for PersonaFlowReader to work
- The Original Persona 1 ISO for the PSP

## Layout

```
script/          German event text, grouped the same way the game packs it
docs/            glossary, style, how far we are
tools/           copy text to/from PersonaFlowReader, patch your ISO
config.example.env
```

What the packs in `script/` are is in `script/README.md`.
How the shell scripts work, how to get the game files, and how to build PersonaFlowReader is in `tools/README.md`.

PersonaFlowReader and the ISO should live next to this repo, not inside it. `config.env` points at them.

## Setup

```bash
cp config.example.env config.env
```

Set three paths in `config.env`:

- `P1_ISO` — your original ISO
- `P1_TEST_ISO` — where a patched copy should be written
- `PFR_ROOT` — the PersonaFlowReader folder that contains `extracted/`, `output/`, and `*.jar`

## What is in git

| In the repo       | Not in the repo                                   |
| ----------------- | ------------------------------------------------- |
| `script/**/*.TXT` | ISOs                                              |
| `docs/`           | `E0.BIN`–`E4.BIN`, `EBOOT.BIN`                    |
| `tools/`          | `.EVS`, audio, maps, textures dumped from the UMD |
| this README       | PersonaFlowReader itself                          |

`git status` should never show an `.iso` or a `.BIN`. If it does, stop and check `.gitignore`.
