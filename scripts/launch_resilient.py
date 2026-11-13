#!/usr/bin/env python3
"""Inicio con respaldo local, diagnóstico y registro independiente de la USB."""
import argparse
import fcntl
from datetime import datetime, timezone
import json
import os
import shutil
from pathlib import Path
import subprocess
import tempfile
import time

URL = 'https://www.xbox.com/play'
GAME_URL = 'https://www.xbox.com/es-MX/play/launch/microsoft-flight-simulator-2024/9P38D19T7LRV'


def writable(root):
    try:
        root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryFile(dir=root):
            pass
        return True
    except OSError:
        return False


def browser_state(profile):
    """Inspect main processes only; never interpret helpers or command text as Chrome."""
    try:
        result = subprocess.run(['ps', '-axo', 'args='], capture_output=True,
                                text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return 'unknown'
    if result.returncode:
        return 'unknown'
    others = False
    for line in result.stdout.splitlines():
        executable = line.strip().partition(' --')[0]
        installations = ('/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
                         str(Path.home() / 'Applications/Google Chrome.app/Contents/MacOS/Google Chrome'))
        if executable not in installations:
            continue
        if f'--user-data-dir={profile} ' in line + ' ':
            return 'profile-active'
        others = True
    return 'other-browser-active' if others else 'closed'


def launch(root, url=URL, new_session=False):
    profile, cache = root / 'profile', root / 'cache'
    state = browser_state(profile)
    if state == 'profile-active':
        return 'existing-profile-active'
    if state == 'unknown':
        return 'inspection-unavailable-no-launch'
    if state == 'other-browser-active' and not new_session:
        return 'existing-browser-review-needed'
    profile.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(['open', '-na', 'Google Chrome', '--args',
                    f'--user-data-dir={profile}', '--profile-directory=Default', f'--disk-cache-dir={cache}',
                    '--disk-cache-size=2147483648', '--no-first-run', url], check=True, timeout=20)
    except subprocess.TimeoutExpired:
        # LaunchServices may have accepted it: do not open a fallback profile.
        return 'requested-launch-timeout'
    # Acceptance by LaunchServices is separate from observing a live process.
    for _ in range(10):
        try:
            result = subprocess.run(['ps', '-axo', 'args='], capture_output=True,
                                text=True, timeout=5)
        except (OSError, subprocess.SubprocessError):
            return 'requested-process-check-unavailable'
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
    parser.add_argument('--game', action='store_true', help='Abrir directamente Flight Simulator 2024')
    parser.add_argument('--smart', action='store_true', help='Evaluar el equipo y guardar recomendaciones antes del arranque')
    parser.add_argument('--new-session', action='store_true', help='Permitir otro perfil aunque el navegador habitual esté abierto')
    args = parser.parse_args()
    local = Path.home() / 'Library/Application Support/BlackMambaFlightKit'
    local.mkdir(parents=True, exist_ok=True)
    status = local / 'last-launch.json'
    if args.status:
        print(status.read_text() if status.exists() else 'Todavía no hay un arranque registrado.')
        return 0
    try:
        free = shutil.disk_usage(Path.home()).free / (1024 ** 3)
        if free < 15:
            print(f'Aviso: el Mac tiene {free:.1f} GiB libres. Revisa espacio antes de jugar (objetivo práctico: 15 GiB).', flush=True)
    except OSError:
        pass
    usb = Path(os.environ.get('USB_VOLUME', '/Volumes/ADATA SC740'))
    usb_root = usb / 'ChromeGameCache'
    candidates = []
    if not args.local and usb.is_dir() and writable(usb_root):
        candidates.append(('USB', usb_root))
    candidates.append(('Mac', local / 'browser'))
    report = {'startedAt': datetime.now(timezone.utc).isoformat(),
              'attempts': [], 'pageVerified': False, 'gameVerified': False}
    if args.smart:
        from play_check import collect
        report['preflight'] = collect()
        print('Chequeo inteligente local · reglas basadas en el estado del equipo', flush=True)
        for tip in report['preflight']['recommendations']:
            print('•', tip, flush=True)

    def save():
        temporary = status.with_suffix('.tmp')
        temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
        temporary.replace(status)

    save()
    for mode, root in candidates:
        attempt = {'mode': mode, 'profile': str(root / 'profile'), 'state': 'starting'}
        report['attempts'].append(attempt)
        save()
        print(f'Comprobando sesión · {mode}', flush=True)
        try:
            if args.new_session:
                attempt['state'] = launch(root, GAME_URL if args.game else URL, new_session=True)
            else:
                attempt['state'] = launch(root, GAME_URL) if args.game else launch(root)
        except (OSError, subprocess.SubprocessError) as exc:
            attempt['state'] = 'failed'
            attempt['error'] = str(exc)
            save()
            print(f'Falló {mode}: {exc}', flush=True)
            continue
        save()
        print('Estado:', attempt['state'])
        print('Perfil:', attempt['profile'])
        if attempt['state'] in ('existing-profile-active', 'existing-browser-review-needed', 'inspection-unavailable-no-launch'):
            print('No se abrió ninguna pestaña ni ventana adicional.')
            if attempt['state'] == 'existing-profile-active':
                print('El perfil del kit ya está activo. Continúa en su ventana; esto no verifica la partida.')
            elif attempt['state'] == 'existing-browser-review-needed':
                print('Chrome ya está abierto. Revisa primero la pestaña de Xbox existente.')
                print('Solo si necesitas otro perfil, ejecuta con --new-session.')
            else:
                print('No se pudo comprobar Chrome. Revisa la sesión existente antes de reintentar.')
            return 0 if attempt['state'] == 'existing-profile-active' else 2
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
    lock_dir = Path.home() / 'Library/Application Support/BlackMambaFlightKit'
    lock_dir.mkdir(parents=True, exist_ok=True)
    with (lock_dir / 'launch.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print('Ya hay un arranque en curso. Continúa en la ventana existente.')
            raise SystemExit(0)
        raise SystemExit(main())
