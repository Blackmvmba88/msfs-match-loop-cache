#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

USB_VOLUME="$(usb_volume)"
require_usb

CACHE_ROOT="${CACHE_ROOT:-$USB_VOLUME/ChromeGameCache/match-loop}"
CACHE_DIR="$CACHE_ROOT/cache"
PROFILE_DIR="$CACHE_ROOT/profile"
REPORT_DIR="${REPORT_DIR:-$(repo_root)/reports}"
USB_REPORT_DIR="$USB_VOLUME/ChromeGameCache/reports"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
REPORT_FILE="$REPORT_DIR/cache-status-$TIMESTAMP.txt"
LATEST_FILE="$USB_REPORT_DIR/cache-status-latest.txt"
HISTORY_FILE="$USB_REPORT_DIR/cache-history.tsv"

mkdir -p "$REPORT_DIR" "$USB_REPORT_DIR"

total_bytes="$(dir_size_bytes "$CACHE_ROOT")"
profile_bytes="$(dir_size_bytes "$PROFILE_DIR")"
cache_bytes="$(dir_size_bytes "$CACHE_DIR")"
free_bytes="$(bytes_available "$USB_VOLUME")"
files_total="$(file_count "$CACHE_ROOT")"
metadata_total="$(metadata_count "$CACHE_ROOT")"
recent_files="$(find "$CACHE_ROOT" -type f -mtime -1 2>/dev/null | wc -l | tr -d ' ')"

if [[ ! -f "$HISTORY_FILE" ]]; then
  printf "timestamp\ttotal_bytes\tprofile_bytes\tcache_bytes\tfiles\tmetadata_files\tusb_free_bytes\n" > "$HISTORY_FILE"
fi
printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\n" \
  "$(now_iso)" "$total_bytes" "$profile_bytes" "$cache_bytes" "$files_total" "$metadata_total" "$free_bytes" >> "$HISTORY_FILE"

{
  echo "Estado Match Loop cache"
  echo
  echo "Ruta: $CACHE_ROOT"
  echo "Total guardado: $(human_size "$total_bytes")"
  echo "Perfil Chrome: $(human_size "$profile_bytes")"
  echo "Cache Chrome: $(human_size "$cache_bytes")"
  echo "Archivos guardados: $files_total"
  echo "Archivos recientes (<24h): $recent_files"
  echo "Metadata macOS ._* / .DS_Store: $metadata_total"
  echo "Libre en USB: $(human_size "$free_bytes")"
  echo
  if [[ -f "$CACHE_ROOT/.last-launch" ]]; then
    echo "Ultimo launch:"
    sed 's/^/  /' "$CACHE_ROOT/.last-launch"
    echo
  fi
  echo "Subcarpetas mas grandes:"
  find "$CACHE_ROOT" -maxdepth 2 -mindepth 1 -type d -print0 2>/dev/null \
    | while IFS= read -r -d '' dir; do
        size="$(dir_size_bytes "$dir")"
        printf "%s\t%s\n" "$size" "$dir"
      done \
    | sort -nr \
    | head -20 \
    | while IFS=$'\t' read -r size dir; do
        printf "  %8s  %s\n" "$(human_size "$size")" "$dir"
      done
} | tee "$REPORT_FILE" "$LATEST_FILE"

echo
echo "Reporte local: $REPORT_FILE"
echo "Reporte USB: $LATEST_FILE"
echo "Historial USB: $HISTORY_FILE"
