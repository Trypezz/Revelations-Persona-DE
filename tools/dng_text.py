#!/usr/bin/env python3
"""Extract and pack dungeon map overlay text (locked doors, levers, riddles).

These live in pack/dng/dXX/dXX.bin, not in the EBOOT or E0-E4 event packs.

Usage:
  python3 dng_text.py extract BIN_DIR script/dng
  python3 dng_text.py pack script/dng BIN_DIR
  python3 dng_text.py patch-iso script/dng P1.iso test.iso [--fresh]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eboot_options as ebo

MARKER = b"\xff\x61\x00\x00\xff\x21\x00\x00"
TERM = b"\xff\x02"
SKIP_PAIRS = {b"\xff\x01", b"\x00\x00", b"\xff\x04"}
INNER_DIR = "PSP_GAME/USRDIR/pack/dng"


def looks_like_text_start(data: bytes, k: int) -> bool:
    if k + 1 >= len(data):
        return False
    a, b = data[k], data[k + 1]
    if a == 0x00 and b in (0x43, 0x44, 0x28):
        return True
    if a == 0x00 and 0xE0 <= b <= 0xF9:
        return True
    if a == 0xFF and b in (0x1B, 0x0F, 0x07):
        return True
    return False


def keep(text: str) -> bool:
    if "(*FF60*)" in text or "(*FF61*)" in text:
        return False
    letters = sum(c.isalpha() for c in text)
    if letters < 8:
        return False
    plain: list[str] = []
    i = 0
    while i < len(text):
        if text.startswith("(*", i):
            end = text.find("*)", i + 2)
            if end < 0:
                break
            i = end + 2
            continue
        plain.append(text[i])
        i += 1
    s = "".join(plain).strip()
    if len(s) < 4:
        return False
    if set(s.upper()) <= set("A /"):
        return False
    return True


def read_until_term(data: bytes, start: int) -> int | None:
    j = start
    while j + 1 < len(data) and data[j : j + 2] != TERM:
        j += 2
        if j - start > 0x400:
            return None
    if data[j : j + 2] != TERM:
        return None
    return j


def find_overlays(data: bytes) -> list[dict]:
    rows: list[dict] = []
    seen: set[int] = set()
    i = 0
    while True:
        i = data.find(MARKER, i)
        if i < 0:
            break
        starts = [i + len(MARKER)]
        first_end = read_until_term(data, starts[0])
        if first_end is None:
            i += 2
            continue
        k = first_end + 2
        for _ in range(8):
            while k + 1 < len(data) and data[k : k + 2] in SKIP_PAIRS:
                k += 2
            if not looks_like_text_start(data, k):
                break
            nxt = read_until_term(data, k)
            if nxt is None:
                break
            starts.append(k)
            k = nxt + 2
        for start in starts:
            if start in seen:
                continue
            end = read_until_term(data, start)
            if end is None:
                continue
            payload = data[start:end]
            text = ebo.decode_script(payload)
            if not keep(text):
                continue
            seen.add(start)
            rows.append(
                {
                    "off": start,
                    "nbytes": len(payload),
                    "text": text,
                    "kind": "script",
                }
            )
        i += 2
    rows.sort(key=lambda r: r["off"])
    return rows


def is_map_bin(path: Path) -> bool:
    name = path.name.lower()
    if not name.endswith(".bin"):
        return False
    if name.endswith("m.bin") or "elv" in name:
        return False
    return True


def write_dump(rows: list[dict], path: Path, stem: str) -> None:
    lines = [
        f"# Dungeon map overlays from pack/dng/{stem}/{stem}.bin.",
        "# Edit the body under each header. Do not change ===== header lines.",
        "# Leave every (*TAG*) intact, including (*0043*), (*004F*), (*LINE_BREAK*).",
        "# BYTES is the original size in the map file. Longer German is refused.",
        "",
    ]
    for n, row in enumerate(rows):
        lines.append(f"# --- {n} ---")
        lines.append(f"===== OFF {row['off']:#x} | BYTES {row['nbytes']} =====")
        lines.append(row["text"])
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def cmd_extract(src: Path, dest: Path, force: bool) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    bins = sorted(p for p in src.glob("*.bin") if is_map_bin(p))
    if not bins:
        print(f"No dungeon .bin in {src}")
        sys.exit(1)
    wrote = 0
    skipped = 0
    empty = 0
    for path in bins:
        out = dest / f"{path.stem}.txt"
        if out.exists() and not force:
            print(f"skip {out.name} (exists). Use --force to overwrite.")
            skipped += 1
            continue
        rows = find_overlays(path.read_bytes())
        if not rows:
            empty += 1
            continue
        write_dump(rows, out, path.stem)
        print(f"Wrote {len(rows)} lines to {out}")
        wrote += 1
    if wrote == 0 and skipped:
        print("Nothing new. All dumps already exist.")
    elif wrote == 0:
        print(f"No overlay text in {src} ({empty} bins had none).")


def cmd_pack(src: Path, dest: Path) -> None:
    files = sorted(src.glob("*.txt"))
    if not files:
        print(f"No .txt in {src}")
        sys.exit(1)
    total = 0
    for path in files:
        bin_path = dest / f"{path.stem}.bin"
        if not bin_path.is_file():
            print(f"No file: {bin_path}")
            sys.exit(1)
        data = bytearray(bin_path.read_bytes())
        rows = ebo.parse_txt(path)
        ebo.pack_into(data, rows, path.name)
        bin_path.write_bytes(data)
        print(f"Packed {len(rows)} lines into {bin_path.name}")
        total += len(rows)
    print(f"Packed {total} lines into {dest}")


def extract_maps_from_iso(iso: Path, dest: Path, stems: list[str] | None) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    if stems:
        inners = [f"{INNER_DIR}/{s}/{s}.bin" for s in stems]
    else:
        inners = [f"{INNER_DIR}/*/*.bin"]
    cmd = ["7z", "e", "-y", f"-o{dest}", str(iso), *inners]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout)
        print(r.stderr)
        print(f"7z failed extracting dungeon maps from {iso}")
        sys.exit(1)


def cmd_patch_iso(src: Path, orig_iso: Path, test_iso: Path, fresh: bool) -> None:
    files = sorted(src.glob("*.txt"))
    if not files:
        print(f"No .txt in {src}")
        print("Run ./tools/extract-dng-text.sh first.")
        sys.exit(1)
    stems = [p.stem for p in files]
    test_iso.parent.mkdir(parents=True, exist_ok=True)
    if fresh or not test_iso.is_file():
        shutil.copyfile(orig_iso, test_iso)
        print(f"Copied ISO: {orig_iso} -> {test_iso}")
    else:
        print(f"Existing Test-ISO: {test_iso}")

    with tempfile.TemporaryDirectory() as tmp:
        orig_dir = Path(tmp) / "orig"
        work_dir = Path(tmp) / "work"
        extract_maps_from_iso(orig_iso, orig_dir, stems)
        shutil.copytree(orig_dir, work_dir)
        cmd_pack(src, work_dir)

        iso_bytes = orig_iso.read_bytes()
        with test_iso.open("r+b") as out:
            for stem in stems:
                orig_bin = (orig_dir / f"{stem}.bin").read_bytes()
                work_bin = (work_dir / f"{stem}.bin").read_bytes()
                if len(work_bin) != len(orig_bin):
                    print(f"{stem}.bin changed size {len(orig_bin)} -> {len(work_bin)}")
                    sys.exit(1)
                off = iso_bytes.find(orig_bin)
                if off < 0:
                    print(f"{stem}.bin not found in {orig_iso}")
                    sys.exit(1)
                out.seek(off)
                out.write(work_bin)
                print(f"{stem}.bin written to offset {off}")
    print(f"Done: {test_iso}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    pe = sub.add_parser("extract")
    pe.add_argument("src")
    pe.add_argument("dest")
    pe.add_argument("--force", action="store_true")

    pp = sub.add_parser("pack")
    pp.add_argument("src")
    pp.add_argument("dest")

    pi = sub.add_parser("patch-iso")
    pi.add_argument("src")
    pi.add_argument("orig_iso")
    pi.add_argument("test_iso")
    pi.add_argument("--fresh", action="store_true")

    args = p.parse_args()
    if args.cmd == "extract":
        cmd_extract(Path(args.src), Path(args.dest), args.force)
    elif args.cmd == "pack":
        cmd_pack(Path(args.src), Path(args.dest))
    else:
        cmd_patch_iso(
            Path(args.src), Path(args.orig_iso), Path(args.test_iso), args.fresh
        )


if __name__ == "__main__":
    main()
