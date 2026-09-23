#!/usr/bin/env bash
# Write PersonaFlowReader's rebuilt EX.BIN into a local test ISO.
# The ISO is never stored in this repo.
set -euo pipefail
# shellcheck source=lib.sh
source "$(dirname "$0")/lib.sh"

FRESH=0
if [[ "${1:-}" == "--fresh" ]]; then
  FRESH=1
  shift
fi

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "USE: $0 [--fresh] 0     (or 1 2 3 4)"
  echo "     $0 [--fresh] eboot"
  exit 0
fi

need_file P1_ISO
need_var P1_TEST_ISO
need_dir PFR_ROOT

if [[ "${1:-}" == "eboot" ]]; then
  SRC_DIR="$REPO_ROOT/script/eboot"
  OG_EBOOT="$PFR_ROOT/OG/EBOOT.BIN"
  OUT_EBOOT="$PFR_ROOT/output/EBOOT.BIN"
  shopt -s nullglob
  eboot_txt=("$SRC_DIR"/*.txt)
  shopt -u nullglob
  if ((${#eboot_txt[@]} == 0)); then
    echo "No .txt in $SRC_DIR"
    echo "Run ./tools/extract-eboot-options.sh first."
    exit 1
  fi
  if [[ ! -f "$OG_EBOOT" ]]; then
    echo "No file: $OG_EBOOT"
    echo "Put a decrypted EBOOT.BIN in $PFR_ROOT/OG/"
    exit 1
  fi
  python3 "$REPO_ROOT/tools/eboot_options.py" pack "$SRC_DIR" "$OG_EBOOT"
  NEW_EBIN="$OG_EBOOT"
  if [[ -f "$OUT_EBOOT" ]] && [[ "$(head -c 4 "$OUT_EBOOT")" == $'\x7fELF' ]]; then
    python3 "$REPO_ROOT/tools/eboot_options.py" pack "$SRC_DIR" "$OUT_EBOOT"
    NEW_EBIN="$OUT_EBOOT"
  fi
  # Byte offset and original size of EBOOT.BIN inside the US PSP ISO.
  # Recalculate with ./tools/get-offset.sh eboot if your dump differs.
  OFFSET=196608
  EXPECT=3836464
  python3 - "$P1_ISO" "$P1_TEST_ISO" "$NEW_EBIN" "$OFFSET" "$EXPECT" "$FRESH" <<'PY'
import shutil
import sys
from pathlib import Path

orig, test, blob_path, offset, expect, fresh = (
    sys.argv[1],
    sys.argv[2],
    sys.argv[3],
    int(sys.argv[4]),
    int(sys.argv[5]),
    sys.argv[6] == "1",
)

data = Path(blob_path).read_bytes()
if data[:4] != b"\x7fELF":
    print(f"{Path(blob_path).name} is not a decrypted EBOOT (no ELF header).")
    sys.exit(1)
if len(data) != expect:
    print(f"{Path(blob_path).name} is {len(data)} Bytes. Expected: {expect}.")
    print("Pad or dump the EBOOT again so it matches the ISO file size.")
    sys.exit(1)

test_path = Path(test)
test_path.parent.mkdir(parents=True, exist_ok=True)

if fresh or not test_path.is_file():
    shutil.copyfile(orig, test)
    print(f"Copied ISO: {orig} -> {test}")
else:
    print(f"Existing Test-ISO: {test}")

with test_path.open("r+b") as f:
    f.seek(offset)
    f.write(data)

print(f"EBOOT.BIN written to Offset {offset} .")
print(f"Done: {test}")
PY
  exit 0
fi

pack_arg "${1:-}"

NEW_EBIN="$PFR_ROOT/output/E${PACK}.BIN"

# Byte offset and original size inside the US PSP ISO.
# Recalculate with ./tools/get-offset.sh N if your dump differs.
case "$PACK" in
0)
  OFFSET=125665280
  EXPECT=2158592
  ;;
1)
  OFFSET=127827968
  EXPECT=1718272
  ;;
2)
  OFFSET=129564672
  EXPECT=2144256
  ;;
3)
  OFFSET=131727360
  EXPECT=1126400
  ;;
4)
  OFFSET=13287424
  EXPECT=2361344
  ;;
esac

if [[ ! -f "$NEW_EBIN" ]]; then
  echo "No file: $NEW_EBIN"
  echo "In PersonaFlowReader first 2 (encode), then 3 (archive)."
  exit 1
fi

python3 - "$P1_ISO" "$P1_TEST_ISO" "$NEW_EBIN" "$OFFSET" "$EXPECT" "$FRESH" <<'PY'
import shutil
import sys
from pathlib import Path

orig, test, blob_path, offset, expect, fresh = (
    sys.argv[1],
    sys.argv[2],
    sys.argv[3],
    int(sys.argv[4]),
    int(sys.argv[5]),
    sys.argv[6] == "1",
)

data = Path(blob_path).read_bytes()
if len(data) != expect:
    print(f"{Path(blob_path).name} is {len(data)} Bytes. Expected: {expect}.")
    print("Different Dump, or PersonaFlowReader made the file bigger.")
    print("Try to shorten your transalted sentences to make them fit again.")
    sys.exit(1)

test_path = Path(test)
test_path.parent.mkdir(parents=True, exist_ok=True)

if fresh or not test_path.is_file():
    shutil.copyfile(orig, test)
    print(f"Copied ISO: {orig} -> {test}")
else:
    print(f"Existing Test-ISO: {test}")

with test_path.open("r+b") as f:
    f.seek(offset)
    f.write(data)

print(f"E{Path(blob_path).stem[-1]}.BIN written to Offset {offset} .")
print(f"Done: {test}")
PY
