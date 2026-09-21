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
```

E0 has 223 scenes. E1-E4 are empty except `.gitkeep` until we extract them.

## Note

E0_001, E0_002 and E0_003 have the same entries for the `Agastya-Tree` (The tree where you save your game). I do not know why but I translated them anyways in case they are used somewhere in the game.

## Files

One file is one event. The name looks like `E0_000.TXT`, `E0_001.TXT` and so on.

We count scenes, not binaries. If `docs/completion.md` says `004/223` that means E0_000 through E0_003.
