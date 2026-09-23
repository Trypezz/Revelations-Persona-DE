#!/usr/bin/env bash
# Write every script/eboot/*.txt back into the decrypted EBOOT in OG/.
# Does not patch the ISO. Use ./tools/patch-iso.sh eboot for that.
set -euo pipefail
# shellcheck source=lib.sh
source "$(dirname "$0")/lib.sh"

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "USE: $0"
  echo "Packs script/eboot/*.txt into OG/EBOOT.BIN"
  exit 0
fi

need_dir PFR_ROOT
EBOOT="$PFR_ROOT/OG/EBOOT.BIN"
SRC="$REPO_ROOT/script/eboot"

shopt -s nullglob
files=("$SRC"/*.txt)
shopt -u nullglob
if ((${#files[@]} == 0)); then
  echo "No .txt in $SRC"
  echo "Run ./tools/extract-eboot-options.sh first."
  exit 1
fi

if [[ ! -f "$EBOOT" ]]; then
  echo "No file: $EBOOT"
  echo "Put a decrypted EBOOT.BIN in $PFR_ROOT/OG/"
  exit 1
fi

python3 "$REPO_ROOT/tools/eboot_options.py" pack "$SRC" "$EBOOT"

OUT="$PFR_ROOT/output/EBOOT.BIN"
if [[ -f "$OUT" ]] && [[ "$(head -c 4 "$OUT")" == $'\x7fELF' ]]; then
  python3 "$REPO_ROOT/tools/eboot_options.py" pack "$SRC" "$OUT"
  echo "Also packed into output/EBOOT.BIN"
fi

echo "Next: ./tools/patch-iso.sh eboot"
