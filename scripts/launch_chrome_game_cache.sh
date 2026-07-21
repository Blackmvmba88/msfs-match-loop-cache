#!/usr/bin/env bash
set -euo pipefail

USB_VOLUME="${USB_VOLUME:-/Volumes/ADATA SC740}"
CACHE_ROOT="${CACHE_ROOT:-$USB_VOLUME/ChromeGameCache}"
CACHE_DIR="$CACHE_ROOT/cache"
DISK_CACHE_SIZE="${DISK_CACHE_SIZE:-2147483648}"
MEDIA_CACHE_SIZE="${MEDIA_CACHE_SIZE:-1073741824}"
GAME_URL="${1:-}"

if [[ ! -d "$USB_VOLUME" ]]; then
  echo "No encuentro la USB: $USB_VOLUME" >&2
  echo "Conecta la USB o usa: USB_VOLUME='/Volumes/NOMBRE USB' $0" >&2
  exit 1
fi

mkdir -p "$CACHE_DIR"

args=(
  --disk-cache-dir="$CACHE_DIR"
  --disk-cache-size="$DISK_CACHE_SIZE"
  --media-cache-size="$MEDIA_CACHE_SIZE"
)

if [[ -n "$GAME_URL" ]]; then
  args+=("$GAME_URL")
fi

echo "Abriendo Chrome con cache en: $CACHE_DIR"
open -a "Google Chrome" --args "${args[@]}"
