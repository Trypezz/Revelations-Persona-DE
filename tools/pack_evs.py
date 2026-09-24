#!/usr/bin/env python3
"""Restore, pad, and check EX.BIN inner files.

Retail packs pad every room to 2048 bytes. PersonaFlowReader encode
does not put that slack back, so later rooms slide and the game loops.
"""

from __future__ import annotations

import argparse
import re
import struct
import subprocess
import sys
from pathlib import Path

DE_MARK = re.compile(r"[äöüÄÖÜß]")
DE_WORD = re.compile(
    r"\b(und|nicht|ich|wir|ist|das|die|der|ein|eine|auch|aber|mit|"
    r"für|auf|dem|den|euch|eure|seelen|willkommen)\b",
    re.I,
)
EN_WORD = re.compile(r"\b(the|you|have|what|will|this|that|with|your)\b", re.I)


def parse_list(data: bytes) -> list[tuple[int, int, int]]:
    start0 = struct.unpack_from("<I", data, 0)[0]
    entries: list[tuple[int, int, int]] = []
    off = 0
    while off + 8 <= start0:
        start, end = struct.unpack_from("<II", data, off)
        if start == 0 and end == 0:
            break
        entries.append((start, end, end - start))
        off += 8
    return entries


def looks_german(text: str) -> bool:
    if DE_MARK.search(text):
        return True
    de = len(DE_WORD.findall(text))
    en = len(EN_WORD.findall(text))
    return de >= 2 and de > en


def inner_sizes(og_bin: Path) -> list[int]:
    return [size for _, _, size in parse_list(og_bin.read_bytes())]


def restore(og_bin: Path, dest: Path) -> int:
    data = og_bin.read_bytes()
    entries = parse_list(data)
    dest.mkdir(parents=True, exist_ok=True)
    prefix = og_bin.stem
    n = 0
    for i, (start, end, _) in enumerate(entries):
        path = dest / f"{prefix}_{i:03d}.EVS"
        path.write_bytes(data[start:end])
        n += 1
    return n


def pad(og_bin: Path, dest: Path) -> list[str]:
    sizes = inner_sizes(og_bin)
    prefix = og_bin.stem
    changed: list[str] = []
    for i, want in enumerate(sizes):
        path = dest / f"{prefix}_{i:03d}.EVS"
        if not path.exists():
            raise SystemExit(f"missing {path.name}")
        data = path.read_bytes()
        if len(data) > want:
            raise SystemExit(
                f"{path.name} is {len(data)} bytes, original is {want}. "
                "Shorten the German in the matching .TXT and encode again."
            )
        if len(data) < want:
            path.write_bytes(data + bytes(want - len(data)))
            changed.append(f"{path.name} {len(data)} -> {want}")
        elif len(data) % 4:
            raise SystemExit(f"{path.name} length {len(data)} is not a multiple of 4")
    return changed


def translated(script_dir: Path) -> list[Path]:
    out: list[Path] = []
    for path in sorted(script_dir.glob("*.TXT")):
        text = path.read_text(encoding="utf-8")
        if looks_german(text):
            out.append(path)
    return out


def check(og_bin: Path, dest: Path) -> list[str]:
    sizes = inner_sizes(og_bin)
    prefix = og_bin.stem
    bad: list[str] = []
    for i, want in enumerate(sizes):
        path = dest / f"{prefix}_{i:03d}.EVS"
        got = path.stat().st_size if path.exists() else -1
        if got != want:
            bad.append(f"{path.name}: {got} (want {want})")
    return bad


def compare_bins(og_bin: Path, out_bin: Path) -> list[str]:
    og = parse_list(og_bin.read_bytes())
    out = parse_list(out_bin.read_bytes())
    bad: list[str] = []
    if len(og) != len(out):
        bad.append(f"file count OG={len(og)} OUT={len(out)}")
    for i, (a, b) in enumerate(zip(og, out)):
        if a != b:
            bad.append(
                f"{og_bin.stem}_{i:03d}: OG {a[0]:#x}-{a[1]:#x} ({a[2]}) "
                f"OUT {b[0]:#x}-{b[1]:#x} ({b[2]})"
            )
    return bad


def pfr_jar(pfr_root: Path) -> Path:
    jars = sorted(pfr_root.glob("*.jar"))
    if not jars:
        raise SystemExit(f"no .jar in {pfr_root}")
    return jars[0]


PFR_FAIL = (
    "ENCODE FAILED",
    "There was a problem accessing the file",
    "is not usable",
    "File is not formatted correctly",
    "TEXT FORMATTED INCORRECTLY",
    "Could not replace",
)


def run_pfr(pfr_root: Path, lines: list[str]) -> str:
    payload = "\n".join(lines) + "\n"
    proc = subprocess.run(
        ["java", "-jar", str(pfr_jar(pfr_root))],
        input=payload,
        cwd=pfr_root,
        capture_output=True,
        text=True,
    )
    text = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        sys.stderr.write(text)
        raise SystemExit(f"PersonaFlowReader exited {proc.returncode}")
    for needle in PFR_FAIL:
        if needle in text:
            sys.stderr.write(text)
            raise SystemExit(f"PersonaFlowReader failed ({needle}).")
    return text


def encode_files(pfr_root: Path, decs: list[Path]) -> str:
    chunks: list[str] = []
    for dec in decs:
        chunks.append(run_pfr(pfr_root, ["2", "n", str(dec.resolve()), "99"]))
    return "\n".join(chunks)


def archive_pack(pfr_root: Path, pack: int) -> str:
    out = pfr_root / "output"
    out.mkdir(exist_ok=True)
    for name in (f"E{pack}.BIN", "EBOOT.BIN"):
        path = out / name
        if path.exists():
            path.unlink()
    return run_pfr(pfr_root, ["3", "n", "", str(pack), "99"])


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "cmd",
        choices=["restore", "pad", "check", "translated", "compare", "encode", "archive"],
    )
    p.add_argument("pack", type=int)
    p.add_argument("--og")
    p.add_argument("--extracted")
    p.add_argument("--script")
    p.add_argument("--out")
    p.add_argument("--pfr")
    args = p.parse_args()

    def need(name: str) -> Path:
        val = getattr(args, name)
        if not val:
            raise SystemExit(f"--{name} is required")
        return Path(val)

    if args.cmd == "restore":
        n = restore(need("og"), need("extracted"))
        print(f"Restored {n} EVS files from {need('og').name}")
    elif args.cmd == "pad":
        changed = pad(need("og"), need("extracted"))
        if changed:
            print("Padded:")
            for line in changed:
                print(f"  {line}")
        else:
            print("All EVS files already match original sizes.")
    elif args.cmd == "check":
        bad = check(need("og"), need("extracted"))
        if bad:
            print("Size mismatch:")
            for line in bad:
                print(f"  {line}")
            sys.exit(1)
        print("All EVS sizes match the original pack.")
    elif args.cmd == "translated":
        files = translated(need("script"))
        for path in files:
            print(path.name)
    elif args.cmd == "encode":
        extracted = need("extracted")
        names = translated(need("script"))
        if not names:
            raise SystemExit("No German .TXT files found. Nothing to encode.")
        decs: list[Path] = []
        for txt in names:
            dec = extracted / (txt.stem + ".DEC")
            if not dec.exists():
                raise SystemExit(f"No {dec.name}. Decode the pack in PersonaFlowReader first.")
            decs.append(dec)
            print(f"encode {dec.name}")
        out = encode_files(need("pfr"), decs)
        if "ENCODE FAILED" in out:
            sys.stderr.write(out)
            raise SystemExit("encode failed")
        print(f"Encoded {len(decs)} scene(s).")
    elif args.cmd == "archive":
        archive_pack(need("pfr"), args.pack)
        print(f"Wrote output/E{args.pack}.BIN")
    else:
        bad = compare_bins(need("og"), need("out"))
        if bad:
            print(f"{len(bad)} inner-file offset mismatch(es):")
            for line in bad[:20]:
                print(f"  {line}")
            if len(bad) > 20:
                print(f"  ... {len(bad) - 20} more")
            sys.exit(1)
        print("Inner file offsets match the original pack.")


if __name__ == "__main__":
    main()
