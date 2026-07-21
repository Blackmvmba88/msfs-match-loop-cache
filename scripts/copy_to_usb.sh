#!/usr/bin/env bash
set -euo pipefail

USB_VOLUME="${USB_VOLUME:-/Volumes/ADATA SC740}"
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

if [[ ! -d "$USB_VOLUME" ]]; then
  echo "No encuentro la USB: $USB_VOLUME" >&2
  exit 1
fi

mkdir -p "$DEST_ROOT"

for source_path in "$@"; do
  if [[ ! -e "$source_path" ]]; then
    echo "No existe: $source_path" >&2
    exit 1
  fi

  base_name="$(basename "$source_path")"
  destination="$DEST_ROOT/$base_name"

  if [[ -e "$destination" ]]; then
    destination="$DEST_ROOT/${base_name%.*}-$(date +%Y%m%d-%H%M%S)"
  fi

  echo "Copiando:"
  echo "  origen:  $source_path"
  echo "  destino: $destination"
  rsync -ah --progress "$source_path" "$destination"

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
