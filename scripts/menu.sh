#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

while true; do
  cat <<'MENU'

Kit MSFS / USB
1) Abrir Microsoft Flight Simulator Cloud
2) Abrir modo Match Loop
3) Diagnostico
4) Buscar archivos pesados
5) Limpiar metadata ._ de la USB
6) Crear atajos en el Escritorio
7) Salir
MENU

  read -r -p "Elige una opcion: " option
  case "$option" in
    1) "$SCRIPT_DIR/launch_msfs_cloud.sh" ;;
    2) "$SCRIPT_DIR/launch_msfs_match_loop.sh" ;;
    3) "$SCRIPT_DIR/doctor.sh" ;;
    4) "$SCRIPT_DIR/scan_large_files.sh" ;;
    5) "$SCRIPT_DIR/clean_usb_metadata.sh" ;;
    6) "$SCRIPT_DIR/create_desktop_shortcuts.sh" ;;
    7) exit 0 ;;
    *) echo "Opcion no valida." ;;
  esac
done
