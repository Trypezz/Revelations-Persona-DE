#!/usr/bin/env python3
"""Extract and pack EBOOT text dumps (choice menus and other UI).

Dumps are separate .txt files in one folder. Pack reads every dump and
writes them back into the decrypted EBOOT.

Usage:
  python3 eboot_options.py extract EBOOT.BIN script/eboot
  python3 eboot_options.py pack script/eboot EBOOT.BIN
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TABLE_START = 0x2C06EC
SAUT = b"\xff\x03"
END = b"\xff\x02"
FFFF = b"\xff\xff"

TERM = {
    "menu": SAUT,
    "script": END,
    "ffff": FFFF,
    "ff01": b"\xff\x01",
}

FILE_ORDER = [
    (35, 2),
    (34, 3),
    (33, 4),
    (32, 4),
    (31, 2),
    (30, 2),
    (29, 2),
    (28, 2),
    (27, 2),
    (26, 2),
    (25, 2),
    (24, 4),
    (23, 4),
    (22, 2),
    (21, 4),
    (20, 4),
    (19, 2),
    (18, 2),
    (17, 2),
    (16, 2),
    (15, 2),
    (14, 4),
    (13, 4),
    (12, 4),
    (11, 2),
    (10, 2),
    (9, 2),
    (8, 2),
    (7, 2),
    (6, 4),
    (5, 4),
    (4, 2),
    (3, 4),
    (2, 2),
    (1, 2),
    (0, 2),
]

DUMPS = [
    {
        "file": "options.txt",
        "kind": "menu",
        "title": "Player choice menus (*SHOW_OPTIONS,N*) in the event .TXT files.",
    },
    {
        "file": "difficulty.txt",
        "kind": "script",
        "start": 0x2D7968,
        "count": 12,
        "title": "Difficulty screen. Prompt, help text, and confirmations.",
    },
    {
        "file": "SystemUI.txt",
        "kind": "ffff",
        "start": 0x264266,
        "count": 3,
        "title": "System data and Memory Stick messages.",
    },
    {
        "file": "BattleUI.txt",
        "kind": "script",
        "start": 0x29AED2,
        "count": 81,
        "title": "Battle commands and in-battle messages.",
    },
    {
        "file": "LevelUpUI.txt",
        "kind": "script",
        "start": 0x2A1EF0,
        "count": 5,
        "title": "Persona rank-up messages.",
    },
    {
        "file": "StatsUI.txt",
        "kind": "script",
        "start": 0x2A4BE4,
        "count": 5,
        "title": "Stat increase messages.",
    },
    {
        "file": "DungeonUI.txt",
        "kind": "script",
        "start": 0x2BFBCE,
        "count": 20,
        "title": "Treasure chests and obtain messages.",
    },
    {
        "file": "DungeonMsg.txt",
        "kind": "script",
        "starts": [0x1EE690, 0x1EE890, 0x1EEA90, 0x292DDC, 0x292E3C],
        "title": "Dungeon overlays: wrong-side chest, empty chest, empty tile, Liftoma/Core Shield worn off.",
        "notes": [
            "chest opened from the wrong side",
            "empty chest",
            "searched an empty tile",
            "Liftoma worn off",
            "Core Shield worn off",
        ],
    },
    {
        "file": "CasinoUI.txt",
        "kind": "script",
        "start": 0x2C7360,
        "count": 266,
        "title": "Casino minigame help.",
    },
    {
        "file": "VelvetUI.txt",
        "kind": "script",
        "start": 0x2CEFA0,
        "count": 128,
        "title": "Velvet Room / Igor tutorials.",
    },
    {
        "file": "LocationUI.txt",
        "kind": "ff01",
        "start": 0x2B1C94,
        "count": 1072,
        "title": "Room names in the corner banner, e.g. 1F Empty Classroom. Door-zone lines like Go to the hallway are not in this table.",
    },
    {
        "file": "NameUI.txt",
        "kind": "fixed",
        "start": 0x2D8282,
        "count": 1,
        "field": 36,
        "stride": 36,
        "pad": "0000",
        "title": "Name entry confirm: Is this all right?",
    },
    {
        "file": "SkillNames.txt",
        "kind": "fixed",
        "start": 0x2675D8,
        "count": 247,
        "field": 32,
        "stride": 48,
        "pad": "FFFF",
        "title": "Skill names (Agi, Bufu, ...). Signature names can stay English.",
    },
    {
        "file": "ItemNames.txt",
        "kind": "fixed",
        "start": 0x26A440,
        "count": 306,
        "field": 32,
        "stride": 64,
        "pad": "FFFF",
        "title": "Item names (Medicine, Bead, weapons, ...).",
    },
    {
        "file": "ItemHelp.txt",
        "kind": "ffff",
        "start": 0x277474,
        "count": 43,
        "title": "Item explanation texts.",
    },
    {
        "file": "SkillHelp.txt",
        "kind": "ffff",
        "start": 0x277CB8,
        "count": 78,
        "title": "Skill explanation texts (damage, heal, status).",
    },
]

HEADER_RE = re.compile(
    r"^===== (?:ID (?P<id>\d+) SLOT (?P<slot>\d+) \| )?"
    r"OFF (?P<off>0x[0-9A-Fa-f]+) \| BYTES (?P<nbytes>\d+)"
    r"(?: \| PAD (?P<pad>FFFF|0000))?"
    r" =====\s*$"
)

PUNCT = {
    " ": 0x00,
    ",": 0x03,
    ".": 0x04,
    ":": 0x06,
    ";": 0x07,
    "?": 0x08,
    "!": 0x09,
    "'": 0x26,
    '"': 0x28,
    "(": 0x29,
    ")": 0x2A,
    "-": 0x3C,
    "/": 0x1E,
    "Ä": 0x71,
    "Ö": 0x90,
    "Ü": 0x95,
    "ä": 0xAA,
    "ö": 0xC9,
    "ü": 0xCE,
}
PUNCT_FROM = {v: k for k, v in PUNCT.items()}
PUNCT_FROM[0x27] = '"'

FF_NAME = {
    0x03: "LINE_BREAK",
    0x04: "CONTINUE",
    0x01: "FF01",
    0xF5: "AWAITING_INPUT",
}
FF_FROM_NAME = {v: k for k, v in FF_NAME.items()}

SPACE_PAIR = (b"\x00\x00", b"\x81\x40")


def decode_letter_or_punct(a: int, b: int) -> str | None:
    if a == 0x81 and b == 0x40:
        return " "
    if a == 0x00 and b in PUNCT_FROM:
        return PUNCT_FROM[b]
    if a == 0x00 and 0xE0 <= b <= 0xF9:
        return chr(ord("A") + (b - 0xE0))
    if a == 0x01 and 1 <= b <= 26:
        return chr(ord("a") + (b - 1))
    if a == 0x00 and 0xCF <= b <= 0xD8:
        return str(b - 0xCF)
    return None


def encode_char(ch: str) -> bytes:
    if ch in PUNCT:
        return bytes([0x00, PUNCT[ch]])
    if "A" <= ch <= "Z":
        return bytes([0x00, 0xE0 + (ord(ch) - ord("A"))])
    if "a" <= ch <= "z":
        return bytes([0x01, ord(ch) - ord("a") + 1])
    if ch.isdigit():
        return bytes([0x00, 0xCF + int(ch)])
    raise ValueError(ch)


def decode_script(payload: bytes) -> str:
    out: list[str] = []
    i = 0
    n = len(payload)
    while i + 1 < n:
        a, b = payload[i], payload[i + 1]
        if a == 0xFF:
            if b == 0x0E and i + 3 < n:
                param = int.from_bytes(payload[i + 2 : i + 4], "little")
                out.append(f"(*SHOW_OPTIONS,{param}*)")
                i += 4
                continue
            out.append(f"(*{FF_NAME.get(b, f'FF{b:02X}')}*)")
            i += 2
            continue
        if payload[i : i + 2] in SPACE_PAIR:
            run = 0
            while i + 1 < n and payload[i : i + 2] in SPACE_PAIR:
                run += 1
                i += 2
            if run >= 4:
                out.append(f"(*PAD,{run}*)")
            else:
                out.append(" " * run)
            continue
        letter = decode_letter_or_punct(a, b)
        if letter is not None:
            out.append(letter)
        else:
            out.append(f"(*{a:02X}{b:02X}*)")
        i += 2
    return "".join(out)


def decode_menu(payload: bytes) -> str:
    return decode_script(payload).strip()


def encode_text(text: str, *, strip_text: bool) -> bytes:
    raw = text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "")
    if strip_text:
        raw = raw.strip()
    out = bytearray()
    i = 0
    n = len(raw)
    while i < n:
        if raw.startswith("(*", i):
            end = raw.find("*)", i + 2)
            if end < 0:
                raise ValueError(f"unclosed tag: {raw[i : i + 20]!r}")
            tag = raw[i + 2 : end]
            i = end + 2
            if tag.startswith("SHOW_OPTIONS,"):
                param = int(tag.split(",", 1)[1])
                out += b"\xff\x0e" + param.to_bytes(2, "little")
                continue
            if tag.startswith("PAD,"):
                out += b"\x00\x00" * int(tag.split(",", 1)[1])
                continue
            if tag in FF_FROM_NAME:
                out += bytes([0xFF, FF_FROM_NAME[tag]])
                continue
            if re.fullmatch(r"FF[0-9A-Fa-f]{2}", tag):
                out += bytes([0xFF, int(tag[2:], 16)])
                continue
            if re.fullmatch(r"[0-9A-Fa-f]{4}", tag):
                out += bytes.fromhex(tag)
                continue
            raise ValueError(f"unknown tag (*{tag}*)")
        out += encode_char(raw[i])
        i += 1
    return bytes(out)


def read_menu(data: bytes) -> list[dict]:
    i = TABLE_START
    strings: list[tuple[int, bytes]] = []
    needed = sum(n for _, n in FILE_ORDER)
    while len(strings) < needed:
        start = i
        j = i
        while j + 1 < len(data) and data[j : j + 2] != SAUT:
            j += 2
            if j - start > 80:
                raise ValueError(f"no terminator at {start:#x}")
        if data[j : j + 2] != SAUT:
            raise ValueError(f"truncated option table at {start:#x}")
        strings.append((start, data[start:j]))
        i = j + 2

    out: list[dict] = []
    idx = 0
    for opt_id, nslots in FILE_ORDER:
        for slot in range(nslots):
            off, payload = strings[idx]
            idx += 1
            out.append(
                {
                    "id": opt_id,
                    "slot": slot,
                    "off": off,
                    "nbytes": len(payload),
                    "text": decode_menu(payload),
                    "kind": "menu",
                }
            )
    out.sort(key=lambda r: (r["id"], r["slot"]))
    return out


def read_fixed(data: bytes, dump: dict) -> list[dict]:
    start = dump["start"]
    count = dump["count"]
    field = dump["field"]
    stride = dump["stride"]
    pad = dump["pad"]
    rows: list[dict] = []
    for n in range(count):
        off = start + n * stride
        payload = data[off : off + field]
        if pad == "FFFF":
            i = 0
            while i + 1 < len(payload) and payload[i : i + 2] != FFFF:
                i += 2
            text = decode_script(payload[:i]).strip()
        else:
            text = decode_script(payload)
        rows.append(
            {
                "off": off,
                "nbytes": field,
                "text": text,
                "kind": "fixed",
                "pad": pad,
            }
        )
    return rows


def read_script_block(
    data: bytes,
    start: int,
    count: int,
    kind: str,
    starts: list[int] | None = None,
) -> list[dict]:
    term = TERM[kind]
    rows: list[dict] = []
    if starts is not None:
        offsets = starts
    else:
        offsets = []
        i = start
        for _ in range(count):
            offsets.append(i)
            j = i
            while j + 1 < len(data) and data[j : j + 2] != term:
                j += 2
                if j - i > 0x800:
                    raise ValueError(f"no terminator at {i:#x} ({kind})")
            if data[j : j + 2] != term:
                raise ValueError(f"truncated block at {i:#x} ({kind})")
            i = j + 2

    for n, i in enumerate(offsets):
        j = i
        while j + 1 < len(data) and data[j : j + 2] != term:
            j += 2
            if j - i > 0x800:
                raise ValueError(f"no terminator at {i:#x} ({kind} #{n})")
        if data[j : j + 2] != term:
            raise ValueError(f"truncated block at {i:#x} ({kind} #{n})")
        payload = data[i:j]
        rows.append(
            {
                "off": i,
                "nbytes": len(payload),
                "text": decode_script(payload),
                "kind": kind,
            }
        )
    return rows


def dump_by_file(name: str) -> dict | None:
    for dump in DUMPS:
        if dump["file"] == name:
            return dump
    return None


def names_from_dump(data: bytes, filename: str) -> list[str]:
    dump = dump_by_file(filename)
    if not dump:
        return []
    return [r["text"] for r in read_fixed(data, dump)]


def find_names(names: list[str], *needles: str) -> list[str]:
    need = [n.lower() for n in needles]
    return [nm for nm in names if nm and all(n in nm.lower() for n in need)]


def annotate_item_help(rows: list[dict], data: bytes) -> None:
    names = names_from_dump(data, "ItemNames.txt")
    if not names:
        return
    # Gems are stored in the same order as "A beautiful gem" lines.
    gem_start = next((i for i, n in enumerate(names) if n == "Alexandrite"), 85)
    rules: dict[int, list[str]] = {
        1: find_names(names, "Repulse Bell"),
        2: find_names(names, "Peak"),
        3: find_names(names, "Mikage") or find_names(names, "Rosetta"),
        5: find_names(names, "Metal Card"),
        6: find_names(names, "Green Compact"),
        7: find_names(names, "Blue Compact"),
        8: find_names(names, "Mirror Piece"),
        9: find_names(names, "Red Compact"),
        10: find_names(names, "Compact Half"),
        11: find_names(names, "Northern Haniwa"),
        13: find_names(names, "Prison Key"),
        14: find_names(names, "Broken Compact"),
        15: find_names(names, "Security Card"),
        16: find_names(names, "Last AqqIe"),
        17: find_names(names, "Last AppIe"),
        18: find_names(names, "Last Apple"),
        19: find_names(names, "Mirror Frame"),
        20: find_names(names, "Ambrosia"),
        21: find_names(names, "Cell Key"),
        22: find_names(names, "Expel Mirror"),
        23: find_names(names, "Snow Queen Mask"),
        24: [n for n in names if n == "AqqIe Pie"],
        25: [n for n in names if n == "AppIe Pie"],
        26: [n for n in names if n == "Apple Pie"],
    }
    for i, row in enumerate(rows):
        hits = rules.get(i, [])
        if 27 <= i <= 42:
            gi = gem_start + (i - 27)
            if gi < len(names):
                hits = [names[gi]]
        if hits:
            row["note"] = "item: " + ", ".join(hits)


def annotate_skill_help(rows: list[dict], data: bytes) -> None:
    names = names_from_dump(data, "SkillNames.txt")
    if not names:
        return

    def have(*parts: str) -> list[str]:
        return find_names(names, *parts)

    # Order in this table is reverse-ish by element. Notes are hints, not 1:1 IDs.
    hints = [
        (0, have("Mediarahan") or have("Media")),
        (4, have("Poisma") or have("Pulinpa")),
        (5, have("Dormina") or find_names(names, "Poison")),
        (6, have("Marin Karin") or have("Paralyse") or have("Stun")),
        (7, have("Petra") or have("Shibaboo")),
        (39, have("Maragidyne")),
        (40, have("Maragion")),
        (41, have("Maragi")),
        (42, have("Agidyne")),
        (35, have("Mabufudyne")),
        (36, have("Mabufula")),
        (37, have("Mabufu")),
        (38, have("Bufudyne")),
        (31, have("Magarudyne") or have("Magarula")),
        (33, have("Magaru")),
        (34, have("Garudyne")),
        (73, have("Diarahan")),
        (74, have("Diarama")),
        (75, have("Dia")),
        (72, have("Recarm")),
        (71, have("Samarecarm")),
        (70, have("Posumudi")),
        (69, have("Paraladi")),
        (68, have("Petradi")),
        (66, have("Patra")),
        (64, have("Recarmdra")),
    ]
    by_i = {i: n for i, n in hints if n}
    for i, row in enumerate(rows):
        hits = by_i.get(i, [])
        t = row["text"].lower()
        if not hits:
            if "light fire" in t and "all" in t:
                hits = have("Maragi")
            elif "medium fire" in t and "all" in t:
                hits = have("Maragion")
            elif "heavy fire" in t and "all" in t:
                hits = have("Maragidyne")
            elif "heavy fire" in t and "area" in t:
                hits = have("Agidyne")
            elif "light ice" in t and "all" in t:
                hits = have("Mabufu")
            elif "medium ice" in t and "all" in t:
                hits = have("Mabufula")
            elif "heavy ice" in t and "all" in t:
                hits = have("Mabufudyne")
            elif "light wind" in t and "all" in t:
                hits = have("Magaru")
            elif "medium wind" in t and "all" in t:
                hits = have("Magarula")
            elif "heavy wind" in t and "all" in t:
                hits = have("Magarudyne")
            elif "light elec" in t and "all" in t:
                hits = have("Mazio")
            elif "medium elec" in t and "all" in t:
                hits = have("Mazionga")
            elif "heavy elec" in t and "all" in t:
                hits = have("Maziodyne")
        if hits:
            row["note"] = "skill: " + ", ".join(hits)


def dump_header_lines(dump: dict) -> list[str]:
    return [
        f"# {dump['title']}",
        "# Edit the body under each header. Do not change ===== header lines.",
        "# Leave every (*TAG*) intact, including (*PAD,N*), (*SHOW_OPTIONS,N*), (*0044*).",
        "# BYTES is the original size in the EBOOT. Longer German is refused.",
        "",
    ]


def write_menu_txt(rows: list[dict], path: Path, dump: dict) -> None:
    lines = dump_header_lines(dump)
    current_id = None
    for row in rows:
        if row["id"] != current_id:
            current_id = row["id"]
            lines.append(f"# --- SHOW_OPTIONS,{current_id} ---")
        lines.append(
            f"===== ID {row['id']} SLOT {row['slot']} | OFF {row['off']:#x} | BYTES {row['nbytes']} ====="
        )
        lines.append(row["text"])
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_script_txt(rows: list[dict], path: Path, dump: dict) -> None:
    lines = dump_header_lines(dump)
    for n, row in enumerate(rows):
        lines.append(f"# --- {n} ---")
        if row.get("note"):
            lines.append(f"# {row['note']}")
        extra = f" | PAD {row['pad']}" if row.get("pad") else ""
        lines.append(f"===== OFF {row['off']:#x} | BYTES {row['nbytes']}{extra} =====")
        lines.append(row["text"])
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_txt(path: Path) -> list[dict]:
    header = None
    body: list[str] = []
    rows: list[dict] = []

    def flush() -> None:
        nonlocal header, body
        if header is None:
            return
        rows.append({**header, "text": "\n".join(body).strip("\n")})
        header = None
        body = []

    for line in path.read_text(encoding="utf-8").splitlines():
        m = HEADER_RE.match(line)
        if m:
            flush()
            header = {
                "off": int(m.group("off"), 16),
                "nbytes": int(m.group("nbytes")),
            }
            if m.group("id") is not None:
                header["id"] = int(m.group("id"))
                header["slot"] = int(m.group("slot"))
                header["kind"] = "menu"
            elif m.group("pad"):
                header["kind"] = "fixed"
                header["pad"] = m.group("pad")
            else:
                header["kind"] = "script"
            body = []
            continue
        if header is None:
            continue
        if line.startswith("#"):
            continue
        body.append(line)
    flush()
    if not rows:
        raise ValueError(f"no entries in {path}")
    return rows


def pack_into(data: bytearray, rows: list[dict], where: str) -> None:
    for row in rows:
        strip = row.get("kind") in ("menu", "fixed")
        encoded = encode_text(row["text"], strip_text=strip)
        nbytes = row["nbytes"]
        if "id" in row:
            label = f"{where} ID {row['id']} SLOT {row['slot']}"
        else:
            label = f"{where} OFF {row['off']:#x}"
        if len(encoded) > nbytes:
            raise ValueError(
                f"{label} is {len(encoded)} bytes, max {nbytes}. Shorten: {row['text']!r}"
            )
        fill = nbytes - len(encoded)
        if fill % 2:
            raise ValueError(f"{label}: encoded length not even")
        pad_word = b"\xff\xff" if row.get("pad") == "FFFF" else b"\x00\x00"
        slot = encoded + (pad_word * (fill // 2))
        off = row["off"]
        if row.get("kind") != "fixed":
            term = bytes(data[off + nbytes : off + nbytes + 2])
            if term not in TERM.values():
                raise ValueError(
                    f"{label}: bad terminator {term.hex()} at {off + nbytes:#x}"
                )
        data[off : off + nbytes] = slot


def require_elf(path: Path) -> bytes:
    data = path.read_bytes()
    if data[:4] != b"\x7fELF":
        print(f"{path} is not a decrypted EBOOT (no ELF header).")
        print("Dump a decrypted EBOOT with PPSSPP and put it in OG/.")
        sys.exit(1)
    return data


def cmd_extract(eboot: Path, dest: Path, force: bool) -> None:
    data = require_elf(eboot)
    dest.mkdir(parents=True, exist_ok=True)
    wrote = 0
    skipped = 0
    for dump in DUMPS:
        path = dest / dump["file"]
        if path.exists() and not force:
            print(f"skip {path.name} (exists). Use --force to overwrite.")
            skipped += 1
            continue
        if dump["kind"] == "menu":
            rows = read_menu(data)
            write_menu_txt(rows, path, dump)
        elif dump["kind"] == "fixed":
            rows = read_fixed(data, dump)
            write_script_txt(rows, path, dump)
        else:
            starts = dump.get("starts")
            count = dump.get("count") or (len(starts) if starts else 0)
            rows = read_script_block(
                data,
                dump.get("start", 0),
                count,
                dump["kind"],
                starts=starts,
            )
            if dump["file"] == "ItemHelp.txt":
                annotate_item_help(rows, data)
            elif dump["file"] == "SkillHelp.txt":
                annotate_skill_help(rows, data)
            for row, note in zip(rows, dump.get("notes") or []):
                row["note"] = note
            write_script_txt(rows, path, dump)
        print(f"Wrote {len(rows)} lines to {path}")
        wrote += 1
    if wrote == 0 and skipped:
        print("Nothing new. All dumps already exist.")


def cmd_pack(src: Path, eboot: Path) -> None:
    data = bytearray(require_elf(eboot))
    files = sorted(src.glob("*.txt"))
    if not files:
        print(f"No .txt in {src}")
        sys.exit(1)
    total = 0
    for path in files:
        rows = parse_txt(path)
        pack_into(data, rows, path.name)
        print(f"Packed {len(rows)} lines from {path.name}")
        total += len(rows)
    eboot.write_bytes(data)
    print(f"Packed {total} lines into {eboot}")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    pe = sub.add_parser("extract")
    pe.add_argument("eboot")
    pe.add_argument("dest")
    pe.add_argument("--force", action="store_true")

    pp = sub.add_parser("pack")
    pp.add_argument("src")
    pp.add_argument("eboot")

    args = p.parse_args()
    if args.cmd == "extract":
        cmd_extract(Path(args.eboot), Path(args.dest), args.force)
    else:
        cmd_pack(Path(args.src), Path(args.eboot))


if __name__ == "__main__":
    main()
