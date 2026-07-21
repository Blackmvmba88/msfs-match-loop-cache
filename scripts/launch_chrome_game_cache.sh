#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

USB_VOLUME="$(usb_volume)"
CACHE_ROOT="${CACHE_ROOT:-$USB_VOLUME/ChromeGameCache}"
CACHE_DIR="$CACHE_ROOT/cache"
PROFILE_DIR="${PROFILE_DIR:-$CACHE_ROOT/profile}"
DISK_CACHE_SIZE="${DISK_CACHE_SIZE:-2147483648}"
MEDIA_CACHE_SIZE="${MEDIA_CACHE_SIZE:-1073741824}"
GAME_URL="${1:-}"

require_usb

mkdir -p "$CACHE_DIR" "$PROFILE_DIR"

args=(
  --user-data-dir="$PROFILE_DIR"
  --disk-cache-dir="$CACHE_DIR"
  --disk-cache-size="$DISK_CACHE_SIZE"
  --media-cache-size="$MEDIA_CACHE_SIZE"
  --no-first-run
  --disable-features=Translate
)

if [[ -n "$GAME_URL" ]]; then
  args+=("$GAME_URL")
fi

echo "Abriendo Chrome con cache en: $CACHE_DIR"
echo "Perfil dedicado en: $PROFILE_DIR"
open -a "Google Chrome" --args "${args[@]}"
