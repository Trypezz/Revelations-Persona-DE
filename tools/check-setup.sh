#!/usr/bin/env bash
# Check if config, ISO, PersonaFlowReader and the tools are in place.
set -u

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  echo "USE: $0"
  echo "Checks if everything is in place."
  exit 0
fi

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG="$REPO_ROOT/config.env"

ok=0
fail=0
warn=0

pass() {
  echo "OK: $1"
  ok=$((ok + 1))
}

bad() {
  echo "FAIL: $1"
  fail=$((fail + 1))
}

maybe() {
  echo "WARN: $1"
  warn=$((warn + 1))
}

placeholder() {
  [[ "$1" == /absolute/path/to/* ]]
}

inside_repo() {
  local p="$1"
  [[ "$p" == "$REPO_ROOT" || "$p" == "$REPO_ROOT"/* ]]
}

if [[ ! -f "$CONFIG" ]]; then
  echo "No config.env."
  echo "  cp config.example.env config.env"
  echo "and paste your paths in there."
  exit 1
fi

have_config=0
if ! bash -n "$CONFIG" 2>/dev/null; then
  bad "config.env cannot be sourced. Quote paths that have ( ) or spaces. Example: P1_ISO=\"/foo/P1(OG).iso\""
else
  pass "config.env"
  # shellcheck source=lib.sh
  source "$(dirname "$0")/lib.sh"
  have_config=1
fi

if ((have_config)); then
  if [[ -z "${P1_ISO:-}" ]]; then
    bad "config.env: P1_ISO is empty."
  elif placeholder "$P1_ISO"; then
    bad "P1_ISO is still the example path. Paste your dump in config.env."
  elif [[ ! -f "$P1_ISO" ]]; then
    bad "P1_ISO not found: $P1_ISO"
  elif inside_repo "$P1_ISO"; then
    bad "P1_ISO sits inside this repo. Put the ISO next to it, not in it."
  else
    pass "P1_ISO ($P1_ISO)"
    size=$(stat -c%s "$P1_ISO")
    if ((size < 100000000)); then
      maybe "P1_ISO is only $size bytes. That does not look like a PSP ISO."
    fi
  fi

  if [[ -z "${P1_TEST_ISO:-}" ]]; then
    bad "config.env: P1_TEST_ISO is empty."
  elif placeholder "$P1_TEST_ISO"; then
    bad "P1_TEST_ISO is still the example path."
  elif inside_repo "$P1_TEST_ISO"; then
    bad "P1_TEST_ISO sits inside this repo. Keep test ISOs outside."
  elif [[ -f "$P1_TEST_ISO" ]]; then
    pass "P1_TEST_ISO ($P1_TEST_ISO)"
  else
    maybe "No test ISO yet at $P1_TEST_ISO. patch-iso.sh will copy it."
  fi

  if [[ -z "${PFR_ROOT:-}" ]]; then
    bad "config.env: PFR_ROOT is empty."
  elif placeholder "$PFR_ROOT"; then
    bad "PFR_ROOT is still the example path."
  elif [[ ! -d "$PFR_ROOT" ]]; then
    bad "PFR_ROOT not found: $PFR_ROOT"
  elif inside_repo "$PFR_ROOT"; then
    bad "PFR_ROOT sits inside this repo. PersonaFlowReader should live next to it."
  else
    pass "PFR_ROOT ($PFR_ROOT)"
  fi
fi

if command -v python3 >/dev/null 2>&1; then
  pass "python3"
else
  bad "python3 missing. patch-iso.sh, get-offset.sh and the eboot scripts need it."
fi

if command -v 7z >/dev/null 2>&1; then
  pass "7z"
  if [[ -n "${P1_ISO:-}" && -f "$P1_ISO" ]]; then
    if 7z l "$P1_ISO" "PSP_GAME/USRDIR/pack/E0.BIN" 2>/dev/null | grep -q "E0.BIN"; then
      pass "ISO has PSP_GAME/USRDIR/pack/E0.BIN"
    else
      bad "ISO has no PSP_GAME/USRDIR/pack/E0.BIN. Wrong dump?"
    fi
  fi
else
  maybe "7z missing. get-offset.sh needs it."
fi

if command -v java >/dev/null 2>&1; then
  pass "java"
else
  maybe "java missing. You need it to run PersonaFlowReader."
fi

if [[ -n "${PFR_ROOT:-}" && -d "$PFR_ROOT" ]]; then
  shopt -s nullglob
  jars=("$PFR_ROOT"/*.jar)
  shopt -u nullglob
  if ((${#jars[@]} > 0)); then
    pass "jar (${jars[0]##*/})"
  else
    bad "No .jar in $PFR_ROOT. Build PersonaFlowReader first."
  fi

  if [[ -d "$PFR_ROOT/table" ]]; then
    if [[ -f "$PFR_ROOT/table/p1p.tbl" ]]; then
      pass "table/p1p.tbl"
    else
      bad "No table/p1p.tbl in $PFR_ROOT."
    fi
  else
    bad "No table/ in $PFR_ROOT. PersonaFlowReader needs it next to the jar."
  fi

  if [[ -d "$PFR_ROOT/OG" ]]; then
    if [[ -f "$PFR_ROOT/OG/EBOOT.BIN" ]]; then
      magic=$(head -c 4 "$PFR_ROOT/OG/EBOOT.BIN" 2>/dev/null || true)
      if [[ "$magic" == $'\x7fELF' ]]; then
        pass "OG/EBOOT.BIN (decrypted)"
      elif [[ "$magic" == "~PSP" ]]; then
        bad "OG/EBOOT.BIN is still encrypted. Dump a decrypted one with PPSSPP."
      else
        bad "OG/EBOOT.BIN is empty or unknown. Put a decrypted EBOOT.BIN in OG/."
      fi
    else
      bad "No EBOOT.BIN in $PFR_ROOT/OG."
    fi
    shopt -s nullglob
    bins=("$PFR_ROOT/OG"/E[0-4].BIN)
    shopt -u nullglob
    if ((${#bins[@]} > 0)); then
      names=()
      for f in "${bins[@]}"; do
        names+=("${f##*/}")
      done
      pass "OG packs (${names[*]})"
    else
      maybe "No EX.BIN in $PFR_ROOT/OG. Put the pack you want to translate in there."
    fi
  else
    bad "No OG/ in $PFR_ROOT. Put EBOOT.BIN and EX.BIN in there."
  fi

  if [[ -d "$PFR_ROOT/extracted" ]]; then
    pass "extracted/"
  else
    maybe "No extracted/ yet. Decode a pack in PersonaFlowReader first."
  fi

  if [[ -d "$PFR_ROOT/output" ]]; then
    pass "output/"
  else
    maybe "No output/ yet. ./tools/build-pack.sh will create it."
  fi
fi

for n in 0 1 2 3 4; do
  if [[ -d "$REPO_ROOT/script/E${n}" ]]; then
    pass "script/E${n}/"
  else
    bad "No script/E${n}/"
  fi
done

if [[ -d "$REPO_ROOT/script/eboot" ]]; then
  pass "script/eboot/"
else
  bad "No script/eboot/. Run ./tools/extract-eboot-options.sh"
fi

warns=0

for s in lib.sh sync-from-pfr.sh sync-to-pfr.sh build-pack.sh pack_evs.py patch-iso.sh get-offset.sh extract-eboot-options.sh patch-eboot-options.sh eboot_options.py; do
  if [[ -f "$REPO_ROOT/tools/$s" ]]; then
    pass "tools/$s"
  else
    maybe "No tools/$s"
    if [[ $s == "sync-to-pfr.sh" ]]; then
      echo " -> You can't patch EX.BIN files"
      warns=$((warns + 1))
    elif [[ $s == "eboot_options.py" ]]; then
      echo " -> You can't patch EBOOT.BIN"
      warns=$((warns + 1))
    elif [[ $s == "patch-iso.sh" ]]; then
      echo " -> You can't patch your test ISO"
      warns=$((warns + 1))
      bad "Missing for script for testing changes in the ISO"
    fi
  fi
done

echo
echo "Done. $ok ok, $fail fail, $warn warn."

if ((warns >= 3)); then
  fail=$((fail + 1))
fi

if ((fail > 0)); then
  echo "Too many WARN Lines or at least one FAIL Line"
  echo "Reduce WARN lines or Fix the FAIL lines first."
  exit 1
fi
echo "You can work."
exit 0
