#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
DESKTOP="$HOME/Desktop"

cat > "$DESKTOP/MSFS Match Loop.command" <<EOF
#!/usr/bin/env bash
cd "$SCRIPT_DIR/.."
./scripts/launch_msfs_match_loop.sh
EOF

cat > "$DESKTOP/MSFS USB Kit.command" <<EOF
#!/usr/bin/env bash
cd "$SCRIPT_DIR/.."
./scripts/menu.sh
EOF

chmod +x "$DESKTOP/MSFS Match Loop.command" "$DESKTOP/MSFS USB Kit.command"

echo "Atajos creados:"
echo "$DESKTOP/MSFS Match Loop.command"
echo "$DESKTOP/MSFS USB Kit.command"
