#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

USB_VOLUME="$(usb_volume)"
CACHE_ROOT="${CACHE_ROOT:-$USB_VOLUME/ChromeGameCache}"
CACHE_DIR="$CACHE_ROOT/cache"
PROFILE_DIR="${PROFILE_DIR:-$CACHE_ROOT/profile}"
DEST_ROOT="${DEST_ROOT:-$USB_VOLUME/OffloadedFiles}"
MATCH_ROOT="$USB_VOLUME/ChromeGameCache/match-loop"

echo "Diagnostico del kit"
echo

if [[ -d "$USB_VOLUME" ]]; then
  echo "USB: OK ($USB_VOLUME)"
  echo "Espacio USB disponible: $(human_size "$(bytes_available "$USB_VOLUME")")"
else
  echo "USB: NO encontrada ($USB_VOLUME)"
fi

if [[ -d "/Applications/Google Chrome.app" ]]; then
  echo "Chrome: OK"
else
  echo "Chrome: no encontrado en /Applications/Google Chrome.app"
fi

mkdir -p "$CACHE_DIR" "$PROFILE_DIR" "$DEST_ROOT"
echo "Cache: $CACHE_DIR"
echo "Perfil Chrome: $PROFILE_DIR"
echo "Match Loop guardado: $(human_size "$(dir_size_bytes "$MATCH_ROOT")")"
echo "Archivos pasados a USB: $DEST_ROOT"
echo "Disco interno disponible: $(human_size "$(bytes_available "$HOME")")"

if command -v git >/dev/null 2>&1 && git -C "$(repo_root)" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Repo Git: OK"
else
  echo "Repo Git: no inicializado"
fi
