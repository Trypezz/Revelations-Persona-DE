#!/usr/bin/env bash
# Dump EBOOT text (choice menus, difficulty screen, ...) into script/eboot/.
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
  echo "Reads OG/EBOOT.BIN (must be decrypted) and writes script/eboot/*.txt"
  echo "Existing files are skipped. --force overwrites them."
  exit 0
fi

need_dir PFR_ROOT
EBOOT="$PFR_ROOT/OG/EBOOT.BIN"
DEST="$REPO_ROOT/script/eboot"

if [[ ! -f "$EBOOT" ]]; then
  echo "No file: $EBOOT"
  echo "Put a decrypted EBOOT.BIN in $PFR_ROOT/OG/"
  exit 1
fi

args=(extract "$EBOOT" "$DEST")
if ((FORCE)); then
  args+=(--force)
fi

python3 "$REPO_ROOT/tools/eboot_options.py" "${args[@]}"
echo "Edit the .txt files in script/eboot/"
echo "Then: ./tools/patch-iso.sh eboot"
