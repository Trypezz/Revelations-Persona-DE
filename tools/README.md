# tools/

Scripts that copy text, rebuild a pack, and patch your test ISO.

`lib.sh` is used by the other scripts. Do not run it. It just loads `config.env`.

PersonaFlowReader and the ISO should live next to this repo, not inside it. `config.env` points at them.

The number you pass is the pack. `0` = E0, `1` = E1, `2` = E2, `3` = E3, `4` = E4.

PersonaFlowReader is still required. `build-pack.sh` calls `java -jar` for encode and archive. You need the jar, `table/`, `OG/` and `extracted/`. You just don't have to click the menu after the first extract/decode.

## Daily work

You already finished setup. You are translating.

### Event text (rooms)

Edit `script/E0/E0_XXX.TXT` (keep the quotes and every `(*TAG*)`). Then:

```bash
./tools/build-pack.sh 0
```

Boot the test ISO. If the room loads and the text is right, commit that `.TXT`.

`build-pack.sh` does all of this:

1. Copy German `.TXT` from `script/E0/` into PersonaFlowReader.
2. Restore every room `.EVS` from `OG/E0.BIN`. Untouched rooms go back to vanilla.
3. Encode only the scenes that look German.
4. Pad each `.EVS` to the original size. This is the important part. Retail rooms are padded to 2048-byte blocks. If a file shrinks, every later room slides, the EBOOT still points at the old offsets, and the game loading-loops.
5. Archive `output/E0.BIN`.
6. Write it into `P1_TEST_ISO`.

Do **not** open PersonaFlowReader and encode the whole `extracted/E0/` folder. Do not encode English files "to be safe". Restore + encode-German-only + pad is the safe path. That is why this script exists.

If encode fails, it will print why (unknown character, broken quotes, missing `.DEC`). Fix the `.TXT` and run `build-pack.sh` again.

If a German scene grows past the original `.EVS` size, the pad step refuses. Shorten the line and try again.

### Menus / UI

Edit `script/eboot/*.txt`. Then:

```bash
./tools/patch-iso.sh eboot
```

Do not change `=====` header lines. Leave every `(*TAG*)` in place, including `(*PAD,N*)`. A German line longer than `BYTES` is refused.

`Ja` fits where `Yes` was. `Nein` does not fit where `No` was, so we use `Ne`. Same idea for location names.

This does not rebuild rooms. You can patch eboot and event packs independently. Later patches write into the existing test ISO. Use `--fresh` only if you want to throw the test ISO away and copy from the original again:

```bash
./tools/patch-iso.sh --fresh 0
./tools/patch-iso.sh eboot
```

`--fresh` on eboot also recopies the original ISO first, so you would lose the event pack until you run `build-pack.sh` again.

## First time: game files

I will not provide the game files or an ISO. Dump it yourself.

Extract so you can copy packs out:

```bash
7z x P1.iso -oiso
```

You get:

```
iso/PSP_GAME/SYSDIR/EBOOT.BIN
iso/PSP_GAME/SYSDIR/BOOT.BIN
iso/PSP_GAME/USRDIR/pack/E0.BIN   (and E1-E4)
```

The ISO `EBOOT.BIN` is encrypted (`~PSP`). PersonaFlowReader and the UI scripts need a **decrypted** one (starts with `ELF`). In PPSSPP: Settings → Tools → Developer tools → Dump decrypted EBOOT.BIN. Launch the game once. Copy that file to `$PFR_ROOT/OG/EBOOT.BIN`. Size must stay 3836464 bytes so it still fits in the ISO.

Copy the packs you want to translate into `$PFR_ROOT/OG/` as well (`E0.BIN`, later E1-E4).

## First time: PersonaFlowReader

This is the only time you use the PFR menu on purpose. After this, `build-pack.sh` starts the jar itself.

Build the jar in their `PersonaFlowReader/` subdirectory (the one with `src/`):

```bash
kotlinc $(find src -name '*.kt') -include-runtime -d pfr.jar
```

That folder is `PFR_ROOT` in `config.env`. It must contain `pfr.jar`, `table/p1p.tbl`, and `OG/`.

Once:

1. Put decrypted `EBOOT.BIN` and `E0.BIN` in `OG/`.
2. Run `java -jar pfr.jar` from `PFR_ROOT`.
3. Option `0`, extract `0` (or `0-4`).
4. Option `1`, not Japanese (`n`), then the folder `extracted/E0/` (path must end in `/`).

That gives you `.EVS` / `.DEC` / `.TXT` per scene. Pull the English `.TXT` into this repo:

```bash
./tools/sync-from-pfr.sh 0
```

After that you translate in `script/E0/` and only run `build-pack.sh`. The jar still runs in the background. You should not need the PFR **menu** again unless you extract a new pack (E1, E2, ...).

```bash
./tools/check-setup.sh
```

## If the game loading-loops

You encoded or archived by hand and a room `.EVS` shrank. Run:

```bash
./tools/build-pack.sh 0
```

That restores vanilla rooms, re-encodes only German, and puts every file back to the original size. Do not keep a dead `output/EBOOT.BIN`. If the first 4 bytes are not `ELF`, delete it. `build-pack.sh` already deletes it before archive.

## The other scripts

You normally do not need these. `build-pack.sh` and `patch-iso.sh eboot` call what they need.

### sync-from-pfr.sh

Copy `.TXT` from PersonaFlowReader into `script/`. Use this after you extract and decode a new pack.

```bash
./tools/sync-from-pfr.sh 0
```

Binary `.EVS` files stay in the tool folder.

Without a number, `sync-to-pfr.sh` and `sync-from-pfr.sh` do all packs that have `.TXT`.

### sync-to-pfr.sh

Copy German `.TXT` from `script/` into PersonaFlowReader. `build-pack.sh` already does this.

### pack_evs.py

Used by `build-pack.sh`. Restore / pad / check inner file sizes. Do not run it unless you are debugging.

### patch-iso.sh

Write `output/EX.BIN` or the decrypted EBOOT into the test ISO. `build-pack.sh` already calls this for event packs.

```bash
./tools/patch-iso.sh 0
./tools/patch-iso.sh eboot
```

If your dump is a different revision and the game ignores the patch, offsets may be wrong:

```bash
./tools/get-offset.sh 0
./tools/get-offset.sh eboot
```

Paste the printed `OFFSET` / `EXPECT` values into `tools/patch-iso.sh`.

### extract-eboot-options.sh

Reads `OG/EBOOT.BIN` and writes dumps into `script/eboot/`. Existing files are skipped.

```bash
./tools/extract-eboot-options.sh
```

`--force` overwrites every dump. That wipes German if you already translated.

### patch-eboot-options.sh

Writes every `script/eboot/*.txt` back into `OG/EBOOT.BIN`. Does not touch the ISO. `patch-iso.sh eboot` already packs and writes the ISO.
