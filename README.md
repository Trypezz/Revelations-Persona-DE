# Revelations: Persona DE

<img align="right" src="https://visitor-badge.laobi.icu/badge?page_id=Trypezz.Revelations-Persona-DE&"  />

Unofficial German translation of Revelations: Persona for the PSP.

This repo is the translation. German `.TXT` files, notes, and the scripts that copy those files into a local tool. The game itself does not belong here.

Persona is Atlus / SEGA. This project is not affiliated with them. You need your own dump. Do not open a pull request that adds an ISO, `EBOOT.BIN`, or extracted UMD files.

## IMPORTANT NOTE

- This Repo is designed to fail on your System. I do not ship the important Python Script that patches the EBOOT.BIN so you are not able to translate anything in there.

## First check if everything is setup correctly

Checks if config, ISO, PersonaFlowReader and the tools are in place.

```bash
./tools/check-setup.sh
```

OK means it is there. FAIL means you cannot work yet. WARN is optional stuff like a test ISO that does not exist until the first patch.

## Requirements to work with this repo

- [`PersonaFlowReader`](https://github.com/TopCape/PersonaFlowReader)
- p7zip
- python3 -> For scripts (get-offset.sh, patch-iso.sh, eboot options)
- java -> Needed for PersonaFlowReader to work
- The Original Persona 1 ISO for the PSP

## Layout

```
script/          German event text, grouped the same way the game packs it
                 script/eboot/ is EBOOT dumps (menus, difficulty, battle UI, ...)
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

Put a **decrypted** `EBOOT.BIN` in `$PFR_ROOT/OG/`. The ISO one is encrypted and cannot be edited. How to dump it is in `tools/README.md`.

## What is in git

| In the repo       | Not in the repo                                   |
| ----------------- | ------------------------------------------------- |
| `script/**/*.TXT` | ISOs                                              |
| `script/eboot/`   | decrypted `EBOOT.BIN` (keep that in `OG/`)        |
| `docs/`           | `E0.BIN`–`E4.BIN`, `EBOOT.BIN`                    |
| `tools/`          | `.EVS`, audio, maps, textures dumped from the UMD |
| this README       | PersonaFlowReader itself                          |

`git status` should never show an `.iso` or a `.BIN`. If it does, stop and check `.gitignore`.
