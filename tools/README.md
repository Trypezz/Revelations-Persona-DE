# tools/

Copy text to/from PersonaFlowReader, patch player choice menus, and patch your ISO.

`lib.sh` is used by the other scripts. Do not run it. It just loads `config.env`.

PersonaFlowReader and the ISO should live next to this repo, not inside it. `config.env` points at them.

X -> Means any number of an event like E0, E1 etc.
`0` = E0, `1` = E1, `2` = E2 and so on.

Without a number, `sync-to-pfr.sh` and `sync-from-pfr.sh` do all packs that have `.TXT`.

## How to get the games files

I won't provide the game files or an ISO. You need to dump the ISO yourself.
If you have an original dumped ISO of the game then we need to extract the game files to be able to translate them.

I did it like this:

```bash
7z x P1.iso -oiso
```

Where your ISO sits. <br>
It will create a directory `iso` where the structure looks like this:

```bash
iso/PSP_GAME/SYSDIR/EBOOT.BIN
iso/PSP_GAME/SYSDIR/BOOT.BIN
iso/PSP_GAME/USRDIR/
```

The needed files are <br>
`EBOOT.BIN` inside `PSP_GAME/SYSDIR/EBOOT.BIN` <br>
`EX.BIN` inside `PSP_GAME/USRDIR/pack/EX.BIN`

The default ISO `EBOOT.BIN` is encrypted (`~PSP`). PersonaFlowReader and the choice-menu scripts need a **decrypted** one (starts with `ELF`). Dump it in PPSSPP: Settings → Tools → Developer tools → Dump decrypted EBOOT.BIN. Launch the game once. Copy that file to `PersonaFlowReader/PersonaFlowReader/OG/EBOOT.BIN`. Size should stay 3836464 bytes so it still fits in the ISO. <br>

## PersonaFlowReader

For this to have a .jar file you need to build it first.
I used this in their `PersonaFlowReader/`-Subdirectory

```bash
kotlinc $(find src -name '*.kt') -include-runtime -d pfr.jar
```

then u can run this tool with:

```bash
java -jar pfr.jar
```

inside of the directory where you built it. It needs to be in the same directory as the `table`-Directory and the `OG`-Directory which you need to add yourself.
In the `OG`-Directory goes the decrypted `EBOOT.BIN` and the `EX.BIN` you want to translate.

## The scripts

### sync-from-pfr.sh

Copy `.TXT` from PersonaFlowReader into `script/`. Use this after you extract and decode in PFR.

```bash
./tools/sync-from-pfr.sh 0 # <- This is the event tree we want to edit (0 = E0, 1 = E1, 2 = E2 and so on)
```

That copies `.TXT` only. Binary `.EVS` files stay in the tool folder.

### sync-to-pfr.sh

Copy our German `.TXT` from `script/` into PersonaFlowReader's `extracted/` folder.

```bash
./tools/sync-to-pfr.sh 0
```

After that, in PersonaFlowReader: encode (2), then archive (3). That writes `output/E0.BIN`.

### patch-iso.sh

Write that `EX.BIN` into your test ISO.

```bash
./tools/patch-iso.sh 0
```

Later packs patch the existing test ISO in place. Use `./tools/patch-iso.sh --fresh 0` if you want to start from the original again.

If your dump is a different revision and the game ignores the patch, offsets may be wrong. Recalculate them:

```bash
./tools/get-offset.sh 0
```

Paste the printed `OFFSET` / `EXPECT` values into `tools/patch-iso.sh`.

### extract-eboot-options.sh

Reads the decrypted `OG/EBOOT.BIN` and writes dumps into `script/eboot/`. One `.txt` per dump (`options.txt`, `difficulty.txt`, `BattleUI.txt`, ...). Existing files are skipped.

```bash
./tools/extract-eboot-options.sh
```

`--force` overwrites every dump. That wipes German if you already translated.

### patch-eboot-options.sh

Writes every `script/eboot/*.txt` back into `OG/EBOOT.BIN`. Does not touch the ISO.

```bash
./tools/patch-eboot-options.sh
```

### patch-iso.sh eboot

Packs every `script/eboot/*.txt` into the decrypted EBOOT and writes that EBOOT into the test ISO.

```bash
./tools/patch-iso.sh eboot
```

`--fresh` still copies from the original ISO first: `./tools/patch-iso.sh --fresh eboot`.

If your dump is a different revision:

```bash
./tools/get-offset.sh eboot
```

Paste `OFFSET` / `EXPECT` into the eboot branch in `tools/patch-iso.sh`.

## Work

1. Translate a file in `script/EX/` (or E1 -> any event).
2. Copy it into PersonaFlowReader:

   ```bash
   ./tools/sync-to-pfr.sh 0
   ```

3. In PersonaFlowReader: encode (2), then archive (3). That writes `output/E0.BIN`.
4. Patch your test ISO:

   ```bash
   ./tools/patch-iso.sh 0
   ```

5. Commit the `.TXT` files if everything works correctly. Nothing else.

To pull newly decoded English files _into_ the repo after you extract them in PersonaFlowReader:

```bash
./tools/sync-from-pfr.sh 0
```

### EBOOT dumps (menus, difficulty, ...)

PersonaFlowReader does not own these. They sit in the decrypted EBOOT. Each dump is its own `.txt` in `script/eboot/`. Packing reads all of them.

1. Decrypt the EBOOT once and put it in `OG/` (see above).
2. If a dump is missing:

   ```bash
   ./tools/extract-eboot-options.sh
   ```

3. Translate the bodies in `script/eboot/*.txt`. Leave the `=====` headers and every `(*TAG*)` alone.
4. Patch the test ISO:

   ```bash
   ./tools/patch-iso.sh eboot
   ```

A line longer than `BYTES` is refused. `Yes` is 3 letters. `Ja` fits. `No` are 2 letters `Nein` does not work, thats why we use `Ne`.
Same goes for Locations and other UI-Elements
