#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

while true; do
  cat <<'MENU'

Kit MSFS / USB
1) Abrir Microsoft Flight Simulator Cloud
2) Abrir modo Match Loop
3) Optimizar post-juego Match Loop
4) Estado cache Match Loop
5) Chequeo de red Xbox
6) Diagnostico
7) Buscar archivos pesados
8) Limpiar metadata ._ de la USB
9) Crear atajos en el Escritorio
10) Salir
MENU

  read -r -p "Elige una opcion: " option
  case "$option" in
    1) "$SCRIPT_DIR/launch_msfs_cloud.sh" ;;
    2) "$SCRIPT_DIR/launch_msfs_match_loop.sh" ;;
    3) "$SCRIPT_DIR/post_play_optimize.sh" ;;
    4) "$SCRIPT_DIR/cache_status.sh" ;;
    5) "$SCRIPT_DIR/network_check.sh" ;;
    6) "$SCRIPT_DIR/doctor.sh" ;;
    7) "$SCRIPT_DIR/scan_large_files.sh" ;;
    8) "$SCRIPT_DIR/clean_usb_metadata.sh" ;;
    9) "$SCRIPT_DIR/create_desktop_shortcuts.sh" ;;
    10) exit 0 ;;
    *) echo "Opcion no valida." ;;
  esac
done
