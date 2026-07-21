#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

while true; do
  cat <<'MENU'

Kit MSFS / USB
1) Abrir Microsoft Flight Simulator Cloud
2) Diagnostico
3) Buscar archivos pesados
4) Limpiar metadata ._ de la USB
5) Salir
MENU

  read -r -p "Elige una opcion: " option
  case "$option" in
    1) "$SCRIPT_DIR/launch_msfs_cloud.sh" ;;
    2) "$SCRIPT_DIR/doctor.sh" ;;
    3) "$SCRIPT_DIR/scan_large_files.sh" ;;
    4) "$SCRIPT_DIR/clean_usb_metadata.sh" ;;
    5) exit 0 ;;
    *) echo "Opcion no valida." ;;
  esac
done
