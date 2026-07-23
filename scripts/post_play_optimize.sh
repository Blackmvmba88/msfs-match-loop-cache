#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

USB_VOLUME="$(usb_volume)"
require_usb

MATCH_ROOT="${MATCH_ROOT:-$USB_VOLUME/ChromeGameCache/match-loop}"
PROFILE_DIR="$MATCH_ROOT/profile"
USB_REPORT_DIR="$USB_VOLUME/ChromeGameCache/reports"
REPORT_DIR="${REPORT_DIR:-$(repo_root)/reports}"

[[ -d "$MATCH_ROOT" ]] || fail "No existe Match Loop cache: $MATCH_ROOT"

if chrome_profile_in_use "$PROFILE_DIR"; then
  fail "Chrome todavia esta usando el perfil Match Loop. Cierra esa ventana de Chrome y vuelve a correr este script."
fi

mkdir -p "$USB_REPORT_DIR" "$REPORT_DIR"

before_bytes="$(dir_size_bytes "$MATCH_ROOT")"
before_metadata="$(metadata_count "$MATCH_ROOT")"

echo "Optimizando Match Loop post-juego"
echo "Antes: $(human_size "$before_bytes")"
echo "Metadata antes: $before_metadata"
echo

echo "Guardando snapshot de estado..."
"$SCRIPT_DIR/cache_status.sh" >/dev/null

echo "Limpiando metadata macOS del cache Match Loop..."
find "$MATCH_ROOT" \( -name '._*' -o -name '.DS_Store' \) -type f -delete 2>/dev/null || true

echo "Quitando modelos Chrome no necesarios para Xbox Cloud..."
rm -rf -- \
  "$PROFILE_DIR/OptGuideOnDeviceModel" \
  "$PROFILE_DIR/optimization_guide_model_store" \
  "$PROFILE_DIR/GrShaderCache" \
  "$PROFILE_DIR/ShaderCache" \
  "$PROFILE_DIR/GraphiteDawnCache" \
  2>/dev/null || true

echo "Recortando reportes viejos..."
for report_root in "$REPORT_DIR" "$USB_REPORT_DIR"; do
  tmp_reports="$(mktemp)"
  find "$report_root" -name 'cache-status-*.txt' -type f | sort > "$tmp_reports"
  old_count="$(wc -l < "$tmp_reports" | tr -d ' ')"
  if (( old_count > 20 )); then
    remove_count=$((old_count - 20))
    head -n "$remove_count" "$tmp_reports" | xargs rm -f 2>/dev/null || true
  fi
  rm -f "$tmp_reports"
done

after_bytes="$(dir_size_bytes "$MATCH_ROOT")"
after_metadata="$(metadata_count "$MATCH_ROOT")"
freed_bytes=$((before_bytes - after_bytes))
if (( freed_bytes < 0 )); then
  freed_bytes=0
fi

{
  echo "timestamp=$(now_iso)"
  echo "match_root=$MATCH_ROOT"
  echo "before_bytes=$before_bytes"
  echo "after_bytes=$after_bytes"
  echo "freed_bytes=$freed_bytes"
  echo "metadata_before=$before_metadata"
  echo "metadata_after=$after_metadata"
} > "$USB_REPORT_DIR/post-play-last.txt"

echo
echo "Despues: $(human_size "$after_bytes")"
echo "Liberado: $(human_size "$freed_bytes")"
echo "Metadata despues: $after_metadata"
echo "Libre en USB: $(human_size "$(bytes_available "$USB_VOLUME")")"
echo
echo "Reporte post-juego: $USB_REPORT_DIR/post-play-last.txt"
