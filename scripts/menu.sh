#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

while true; do
  cat <<'MENU'

Kit MSFS / USB
1) Abrir Microsoft Flight Simulator Cloud
2) Abrir modo Match Loop
3) Estado cache Match Loop
4) Chequeo de red Xbox
5) Diagnostico
6) Buscar archivos pesados
7) Limpiar metadata ._ de la USB
8) Crear atajos en el Escritorio
9) Salir
MENU

  read -r -p "Elige una opcion: " option
  case "$option" in
    1) "$SCRIPT_DIR/launch_msfs_cloud.sh" ;;
    2) "$SCRIPT_DIR/launch_msfs_match_loop.sh" ;;
    3) "$SCRIPT_DIR/cache_status.sh" ;;
    4) "$SCRIPT_DIR/network_check.sh" ;;
    5) "$SCRIPT_DIR/doctor.sh" ;;
    6) "$SCRIPT_DIR/scan_large_files.sh" ;;
    7) "$SCRIPT_DIR/clean_usb_metadata.sh" ;;
    8) "$SCRIPT_DIR/create_desktop_shortcuts.sh" ;;
    9) exit 0 ;;
    *) echo "Opcion no valida." ;;
  esac
done
