#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

USB_VOLUME="$(usb_volume)"
DEST_ROOT="${DEST_ROOT:-$USB_VOLUME/OffloadedFiles}"
MOVE=false

usage() {
  echo "Uso: $0 [--move] <archivo-o-carpeta> [mas-rutas...]"
  echo
  echo "Variables:"
  echo "  USB_VOLUME='/Volumes/ADATA SC740'"
  echo "  DEST_ROOT='/Volumes/ADATA SC740/OffloadedFiles'"
}

if [[ "${1:-}" == "--move" ]]; then
  MOVE=true
  shift
fi

if [[ "$#" -lt 1 ]]; then
  usage >&2
  exit 1
fi

require_usb

mkdir -p "$DEST_ROOT"

for source_path in "$@"; do
  if [[ ! -e "$source_path" ]]; then
    echo "No existe: $source_path" >&2
    exit 1
  fi

  destination="$(safe_destination "$DEST_ROOT" "$source_path")"
  ensure_space_for "$source_path" "$DEST_ROOT"

  echo "Copiando:"
  echo "  origen:  $source_path"
  echo "  destino: $destination"
  if [[ -d "$source_path" ]]; then
    mkdir -p "$destination"
    rsync -aEh --progress --exclude '._*' --exclude '.DS_Store' "$source_path/" "$destination/"
  else
    rsync -aEh --progress --exclude '._*' --exclude '.DS_Store' "$source_path" "$destination"
  fi

  if ! verify_copy "$source_path" "$destination"; then
    echo "La copia no paso verificacion. No se borrara nada." >&2
    exit 1
  fi

  echo "Copia verificada."

  if [[ "$MOVE" == true ]]; then
    echo
    read -r -p "Confirmas borrar el original '$source_path'? Escribe MOVE para continuar: " confirm
    if [[ "$confirm" == "MOVE" ]]; then
      rm -rf -- "$source_path"
      echo "Original eliminado: $source_path"
    else
      echo "No borre el original."
    fi
  fi
done
