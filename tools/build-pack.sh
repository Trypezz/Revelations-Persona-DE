#!/usr/bin/env bash
# Rebuild one EX.BIN from German .TXT without sliding later rooms.
# Restores every room from OG, encodes only the German scenes, pads
# each .EVS back to the original size, archives, then patches the test ISO.
set -euo pipefail
# shellcheck source=lib.sh
source "$(dirname "$0")/lib.sh"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "USE: $0 0     (or 1 2 3 4)"
  echo
  echo "Does: sync German .TXT -> restore vanilla EVS -> encode German"
  echo "scenes only -> pad to original sizes -> archive -> patch test ISO."
  echo "Do not encode the whole extracted/EX folder yourself."
  exit 0
fi

pack_arg "${1:-}"
need_dir PFR_ROOT
need_file P1_ISO
need_var P1_TEST_ISO

OG_BIN="$PFR_ROOT/OG/E${PACK}.BIN"
EXTRACTED="$PFR_ROOT/extracted/E${PACK}"
SCRIPT_DIR="$REPO_ROOT/script/E${PACK}"
PY="$REPO_ROOT/tools/pack_evs.py"

if [[ ! -f "$OG_BIN" ]]; then
  echo "No file: $OG_BIN"
  echo "Put E${PACK}.BIN in $PFR_ROOT/OG/"
  exit 1
fi
if [[ ! -d "$EXTRACTED" ]]; then
  echo "No directory: $EXTRACTED"
  echo "In PersonaFlowReader first 0 (extract), then 1 (decode)."
  exit 1
fi

echo "== 1. copy German .TXT into PersonaFlowReader"
"$REPO_ROOT/tools/sync-to-pfr.sh" "$PACK"

echo
echo "== 2. restore every room from OG/E${PACK}.BIN"
echo "    Untranslated rooms go back to vanilla. That stops leftover"
echo "    encode shrinkage from sliding later rooms."
python3 "$PY" restore "$PACK" --og "$OG_BIN" --extracted "$EXTRACTED"

echo
echo "== 3. encode German scenes only"
python3 "$PY" encode "$PACK" --og "$OG_BIN" --extracted "$EXTRACTED" --script "$SCRIPT_DIR" --pfr "$PFR_ROOT"

echo
echo "== 4. pad .EVS files back to original sizes"
python3 "$PY" pad "$PACK" --og "$OG_BIN" --extracted "$EXTRACTED"
python3 "$PY" check "$PACK" --og "$OG_BIN" --extracted "$EXTRACTED"

echo
echo "== 5. archive E${PACK}.BIN"
python3 "$PY" archive "$PACK" --pfr "$PFR_ROOT"
python3 "$PY" compare "$PACK" --og "$OG_BIN" --extracted "$EXTRACTED" --out "$PFR_ROOT/output/E${PACK}.BIN"

echo
echo "== 6. write E${PACK}.BIN into the test ISO"
"$REPO_ROOT/tools/patch-iso.sh" "$PACK"

echo
echo "Done. Boot $P1_TEST_ISO and try the rooms that looped."
echo "Menus/UI are a separate step: ./tools/patch-iso.sh eboot"
