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

curl --connect-timeout 10 --max-time 30 --fail -L -sS -o /dev/null \
  -w "DNS: %{time_namelookup}s\nConectar: %{time_connect}s\nTLS: %{time_appconnect}s\nPrimer byte: %{time_starttransfer}s\nTotal: %{time_total}s\nHTTP: %{http_code}\n" \
  "$TARGET_URL"

echo
echo "Alcance: estos tiempos corresponden a HTTP, no al stream ni a la carga del simulador."
echo "Conectar, TLS y primer byte son tiempos acumulados desde el inicio."
echo "Comparalos entre sesiones equivalentes; no hay un umbral que garantice una buena sesion."
