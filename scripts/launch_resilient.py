#!/usr/bin/env python3
"""Inicio con respaldo local, diagnóstico y registro independiente de la USB."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

URL = 'https://www.xbox.com/play'


def writable(root):
    try:
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
        return True
    except OSError:
        return False


def launch(root):
    profile, cache = root / 'profile', root / 'cache'
    profile.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    subprocess.run(['open', '-na', 'Google Chrome', '--args',
                    f'--user-data-dir={profile}', f'--disk-cache-dir={cache}',
                    '--no-first-run', URL], check=True, timeout=20)
    # Acceptance by LaunchServices is separate from observing a live process.
    for _ in range(10):
        result = subprocess.run(['ps', '-axo', 'args='], capture_output=True,
                                text=True, timeout=5)
        if result.returncode:
            return 'requested-process-check-unavailable'
        if any('/Google Chrome.app/Contents/MacOS/Google Chrome ' in line
               and f'--user-data-dir={profile} ' in line
               for line in result.stdout.splitlines()):
            return 'process-observed'
        time.sleep(.5)
    return 'requested-process-not-observed'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--local', action='store_true', help='Usar directamente el respaldo del Mac')
    parser.add_argument('--status', action='store_true', help='Mostrar el último resultado sin abrir Chrome')
    args = parser.parse_args()
    local = Path.home() / 'Library/Application Support/BlackMambaFlightKit'
    local.mkdir(parents=True, exist_ok=True)
    status = local / 'last-launch.json'
    if args.status:
        print(status.read_text() if status.exists() else 'Todavía no hay un arranque registrado.')
        return 0
    usb = Path(os.environ.get('USB_VOLUME', '/Volumes/ADATA SC740'))
    usb_root = usb / 'ChromeGameCache'
    candidates = []
    if not args.local and usb.is_dir() and writable(usb_root):
        candidates.append(('USB', usb_root))
    candidates.append(('Mac', local / 'browser'))
    report = {'startedAt': datetime.now(timezone.utc).isoformat(),
              'attempts': [], 'pageVerified': False, 'gameVerified': False}

    def save():
        temporary = status.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
        temporary.replace(status)

    save()
    for mode, root in candidates:
        attempt = {'mode': mode, 'profile': str(root / 'profile'), 'state': 'starting'}
        report['attempts'].append(attempt)
        save()
        print(f'Abriendo Xbox · {mode}', flush=True)
        try:
            attempt['state'] = launch(root)
        except (OSError, subprocess.SubprocessError) as exc:
            attempt['state'] = 'failed'
            attempt['error'] = str(exc)
            save()
            print(f'Falló {mode}: {exc}', flush=True)
            continue
        save()
        print('Estado:', attempt['state'])
        print('Perfil:', attempt['profile'])
        print('Busca la ventana de Chrome con Xbox; puede pedir iniciar sesión.')
        print('La apertura no confirma que el juego esté listo.')
        print('Si la ventana no responde, usa «MSFS Respaldo Mac.command».')
        print('No desconectes la USB mientras su perfil esté abierto.')
        print('Registro local:', status)
        return 0 if attempt['state'] == 'process-observed' else 2
    print('No se pudo abrir Chrome. Abre https://www.xbox.com/play en tu navegador.')
    print('Registro local:', status)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
