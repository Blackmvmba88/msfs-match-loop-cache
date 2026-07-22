#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=scripts/lib.sh
source "$SCRIPT_DIR/lib.sh"

USB_VOLUME="$(usb_volume)"
MATCH_ROOT="${MATCH_ROOT:-$USB_VOLUME/ChromeGameCache/match-loop}"
MATCH_LOOP_URL="${MATCH_LOOP_URL:-https://www.xbox.com/play}"
export CACHE_ROOT="$MATCH_ROOT"

cat <<'EOF'
Modo Match Loop

1. Se abrira Xbox Cloud Gaming con cache/perfil dedicado en la USB.
2. Entra a Microsoft Flight Simulator.
3. Carga el stage "Match Loop" una vez y dejalo 2-3 minutos.
4. Mientras no cierres esa sesion, volver a ese stage normalmente sera mas rapido/estable.

Nota: en cloud gaming no podemos guardar los paquetes internos del stage en la Mac;
esto conserva lo que Chrome/Xbox si permiten guardar localmente.

EOF

"$SCRIPT_DIR/launch_chrome_game_cache.sh" "$MATCH_LOOP_URL"
