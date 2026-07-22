#!/usr/bin/env bash
set -euo pipefail

TARGET_URL="${TARGET_URL:-https://www.xbox.com/play}"

echo "Chequeo de red para Xbox Cloud"
echo "URL: $TARGET_URL"
echo

if ! command -v curl >/dev/null 2>&1; then
  echo "curl no esta disponible."
  exit 1
fi

curl -L -s -o /dev/null \
  -w "DNS: %{time_namelookup}s\nConectar: %{time_connect}s\nTLS: %{time_appconnect}s\nPrimer byte: %{time_starttransfer}s\nTotal: %{time_total}s\nHTTP: %{http_code}\n" \
  "$TARGET_URL"

echo
echo "Guia rapida:"
echo "- Total menor a 1.5s suele sentirse bien para abrir Xbox Cloud."
echo "- Si primer byte/total sube mucho, cierra descargas, usa 5 GHz o Ethernet."
