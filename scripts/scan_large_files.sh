#!/usr/bin/env bash
set -euo pipefail

MIN_SIZE="${MIN_SIZE:-500M}"
REPORT_DIR="${REPORT_DIR:-reports}"
TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
REPORT_FILE="$REPORT_DIR/large-files-$TIMESTAMP.tsv"

SEARCH_DIRS=(
  "$HOME/Desktop"
  "$HOME/Downloads"
  "$HOME/Documents"
  "$HOME/Movies"
  "$HOME/Music"
  "$HOME/Pictures"
)

mkdir -p "$REPORT_DIR"

{
  printf "size_bytes\tsize_human\tpath\n"
  for dir in "${SEARCH_DIRS[@]}"; do
    [[ -d "$dir" ]] || continue
    find "$dir" -type f -size +"$MIN_SIZE" -print0 2>/dev/null
  done | while IFS= read -r -d '' file; do
    size_bytes="$(stat -f %z "$file")"
    size_human="$(du -h "$file" | awk '{print $1}')"
    printf "%s\t%s\t%s\n" "$size_bytes" "$size_human" "$file"
  done | sort -nr
} > "$REPORT_FILE"

echo "Reporte creado: $REPORT_FILE"
echo
head -20 "$REPORT_FILE"
