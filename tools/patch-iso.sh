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

pack_arg "${1:-}"
need_file P1_ISO
need_var P1_TEST_ISO
need_dir PFR_ROOT

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
