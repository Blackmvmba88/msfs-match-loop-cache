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
MIN_USB_FREE_BYTES="${MIN_USB_FREE_BYTES:-5368709120}"
GAME_URL="${1:-}"

require_usb
[[ -d "/Applications/Google Chrome.app" ]] || fail "No encuentro Google Chrome en /Applications."

mkdir -p "$CACHE_DIR" "$PROFILE_DIR"

available_bytes="$(bytes_available "$USB_VOLUME")"
if (( available_bytes < MIN_USB_FREE_BYTES )); then
  echo "Aviso: queda poco espacio en la USB: $(human_size "$available_bytes")." >&2
fi

if [[ -e "$PROFILE_DIR/SingletonLock" ]]; then
  echo "Aviso: parece que este perfil ya esta abierto en Chrome. Si algo falla, cierra esa ventana y vuelve a intentar." >&2
fi

args=(
  --user-data-dir="$PROFILE_DIR"
  --disk-cache-dir="$CACHE_DIR"
  --disk-cache-size="$DISK_CACHE_SIZE"
  --media-cache-size="$MEDIA_CACHE_SIZE"
  --no-first-run
  --disable-background-timer-throttling
  --disable-backgrounding-occluded-windows
  --disable-features=CalculateNativeWinOcclusion,Translate
  --disable-renderer-backgrounding
)

if [[ -n "$GAME_URL" ]]; then
  args+=("$GAME_URL")
fi

echo "Abriendo Chrome con cache en: $CACHE_DIR"
echo "Perfil dedicado en: $PROFILE_DIR"
{
  echo "timestamp=$(now_iso)"
  echo "cache_root=$CACHE_ROOT"
  echo "profile_dir=$PROFILE_DIR"
  echo "cache_dir=$CACHE_DIR"
  echo "url=$GAME_URL"
} > "$CACHE_ROOT/.last-launch"
open -a "Google Chrome" --args "${args[@]}"
