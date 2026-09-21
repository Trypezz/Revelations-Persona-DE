#!/usr/bin/env bash
# Copy .TXT files from PersonaFlowReader into this repo.
# Binary .EVS / .DEC files stay in the tool folder.
set -euo pipefail
# shellcheck source=lib.sh
source "$(dirname "$0")/lib.sh"

need_dir PFR_ROOT

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "USE: $0 [0-4]"
  echo "Without: all packs, that have .TXT in extracted/"
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
  src="$PFR_ROOT/extracted/E${n}"
  dest="$REPO_ROOT/script/E${n}"
  if [[ ! -d "$src" ]]; then
    echo "E${n}: No Directory $src"
    continue
  fi
  shopt -s nullglob
  files=("$src"/*.TXT)
  shopt -u nullglob
  if ((${#files[@]} == 0)); then
    echo "E${n}: No .TXT in $src"
    continue
  fi
  mkdir -p "$dest"
  cp -v "${files[@]}" "$dest/"
  copied=$((copied + ${#files[@]}))
done

echo "Done. $copied file(s) to script/"
echo "Only .TXT"
echo ".EVS and .DEC stay inside PersonaFlowReader."
