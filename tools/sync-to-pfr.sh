#!/usr/bin/env bash
# Copy German .TXT files from this repo into PersonaFlowReader's extracted/ folder.
set -euo pipefail
# shellcheck source=lib.sh
source "$(dirname "$0")/lib.sh"

need_dir PFR_ROOT

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "USE: $0 [0-4]"
  echo "Without number: all Pack, that are inside script/"
  exit 0
fi

if [[ -n "${1:-}" ]]; then
  pack_arg "$1"
  packs=("$PACK")
else
  packs=(0 1 2 3 4)
fi

copied=0
for n in "${packs[@]}"; do
  src="$REPO_ROOT/script/E${n}"
  dest="$PFR_ROOT/extracted/E${n}"
  shopt -s nullglob
  files=("$src"/*.TXT)
  shopt -u nullglob
  if ((${#files[@]} == 0)); then
    echo "E${n}: No .TXT in script/E${n}/"
    continue
  fi
  mkdir -p "$dest"
  cp -v "${files[@]}" "$dest/"
  copied=$((copied + ${#files[@]}))
done

echo "Done. $copied file(s) to $PFR_ROOT/extracted/"
echo "Next use PersonaFlowReader and use: 2 (encode), than 3 (archive)."
