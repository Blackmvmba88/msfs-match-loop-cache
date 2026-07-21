#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

USB_VOLUME="$(usb_volume)"
require_usb

echo "Buscando archivos de metadata de macOS en: $USB_VOLUME"
count="$(find "$USB_VOLUME" \( -name '._*' -o -name '.DS_Store' \) -print 2>/dev/null | wc -l | tr -d ' ')"

if [[ "$count" == "0" ]]; then
  echo "No hay metadata para limpiar."
  exit 0
fi

echo "Encontrados: $count"
read -r -p "Escribe CLEAN para borrarlos: " confirm
if [[ "$confirm" != "CLEAN" ]]; then
  echo "Cancelado."
  exit 0
fi

find "$USB_VOLUME" \( -name '._*' -o -name '.DS_Store' \) -delete 2>/dev/null
echo "Metadata eliminada."
