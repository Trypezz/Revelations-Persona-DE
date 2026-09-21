# Shared by the other tools. Do not run it!

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CONFIG="$REPO_ROOT/config.env"

if [[ ! -f "$CONFIG" ]]; then
  echo "No config.env."
  echo "  cp config.example.env config.env"
  echo "and paste your paths in there."
  exit 1
fi

# shellcheck disable=SC1090
set -a
source "$CONFIG"
set +a

need_var() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    echo "config.env: $name is empty."
    exit 1
  fi
}

need_file() {
  local name="$1"
  need_var "$name"
  if [[ ! -f "${!name}" ]]; then
    echo "Not found ($name): ${!name}"
    exit 1
  fi
}

need_dir() {
  local name="$1"
  need_var "$name"
  if [[ ! -d "${!name}" ]]; then
    echo "No directory ($name): ${!name}"
    exit 1
  fi
}

pack_arg() {
  local n="${1:-}"
  if [[ ! "$n" =~ ^[0-4]$ ]]; then
    echo "USE: $0 0     (or 1 2 3 4)"
    exit 1
  fi
  PACK="$n"
}
