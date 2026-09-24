#!/usr/bin/env bash
# Dump dungeon map overlay text (locked doors, levers, riddles) into script/dng/.
set -euo pipefail
# shellcheck source=lib.sh
source "$(dirname "$0")/lib.sh"

FORCE=0
if [[ "${1:-}" == "--force" ]]; then
  FORCE=1
  shift
fi

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "USE: $0 [--force]"
  echo "Reads pack/dng/dXX/dXX.bin from P1_ISO and writes script/dng/*.txt"
  echo "Existing files are skipped. --force overwrites them."
  exit 0
fi

need_file P1_ISO
DEST="$REPO_ROOT/script/dng"

if ! command -v 7z >/dev/null 2>&1; then
  echo "7z missing."
  exit 1
fi

TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

echo "Extracting dungeon maps from ISO..."
7z e -y "$P1_ISO" "PSP_GAME/USRDIR/pack/dng/*/*.bin" -o"$TMP" >/dev/null

args=(extract "$TMP" "$DEST")
if ((FORCE)); then
  args+=(--force)
fi

python3 "$REPO_ROOT/tools/dng_text.py" "${args[@]}"
echo "Edit the .txt files in script/dng/"
echo "Then: ./tools/patch-iso.sh dng"
