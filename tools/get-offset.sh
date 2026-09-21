#!/usr/bin/env bash
# Find where EX.BIN sits inside your ISO. Needs 7z.
set -euo pipefail
# shellcheck source=lib.sh
source "$(dirname "$0")/lib.sh"

pack_arg "${1:-}"
need_file P1_ISO

if ! command -v 7z >/dev/null 2>&1; then
  echo "7z missing."
  exit 1
fi

INNER="PSP_GAME/USRDIR/pack/E${PACK}.BIN"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

7z e -y "$P1_ISO" "$INNER" -o"$TMP" >/dev/null

python3 - "$P1_ISO" "$TMP/E${PACK}.BIN" "$PACK" <<'PY'
import sys
from pathlib import Path

iso_path, bin_path, n = sys.argv[1], sys.argv[2], sys.argv[3]
iso = Path(iso_path).read_bytes()
blob = Path(bin_path).read_bytes()
off = iso.find(blob)
if off < 0:
    print(f"E{n}.BIN not found in ISO.")
    sys.exit(1)
print(f"N={n}")
print(f"FILE=E{n}.BIN")
print(f"OFFSET={off}")
print(f"EXPECT={len(blob)}")
print(f"case-Line:  {n}) OFFSET={off}; EXPECT={len(blob)} ;;")
PY
