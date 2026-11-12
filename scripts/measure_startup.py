#!/usr/bin/env python3
"""Cronómetro manual por etapas; no controla el juego ni lee el perfil."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
STAGES = (
    ('xbox_visible', 'Xbox muestra su interfaz'),
    ('session_requested', 'Acabas de pulsar Jugar para iniciar la sesión cloud'),
    ('stream_visible', 'Terminó la cola y apareció la transmisión del juego'),
    ('game_menu', 'El menú del simulador está listo'),
    ('flight_requested', 'Acabas de confirmar el inicio del vuelo'),
    ('flight_controllable', 'Ya puedes controlar el vuelo'),
)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', action='store_true',
                        help='Mide la sesión habitual sin abrir otro Chrome')
    args = parser.parse_args()
    mode = 'reference' if args.reference else 'usb-cache'
    print('Vuelve a esta Terminal y pulsa Enter al alcanzar cada etapa.')
    print('Es una medición manual: incluye el tiempo que tardas en marcar.')
    input('Pulsa Enter para comenzar; en referencia, abre Xbox inmediatamente después. ')
    started = time.monotonic()
    data = {'id': str(uuid.uuid4()), 'mode': mode,
            'startedAt': datetime.now(timezone.utc).isoformat(),
            'method': 'manual monotonic stage markers', 'markers': [],
            'complete': False}
    reports = ROOT / 'reports'
    reports.mkdir(exist_ok=True)
    path = reports / ('startup-' + data['id'] + '.json')

    def save():
        temporary = path.with_suffix('.tmp')
        temporary.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n')
        temporary.replace(path)

    save()
    try:
        if not args.reference:
            result = subprocess.run(['bash', str(ROOT / 'scripts/launch_msfs_cloud.sh')])
            data['launcherExitCode'] = result.returncode
            save()
            if result.returncode:
                print('Falló el launcher. Registro:', path)
                return result.returncode
        for event, label in STAGES:
            input(label + ' → Enter ')
            elapsed = round(time.monotonic() - started, 3)
            data['markers'].append({'event': event, 'elapsedSeconds': elapsed})
            save()
            print(f'  {elapsed:.3f} s desde el inicio')
        data['complete'] = True
    except (KeyboardInterrupt, EOFError):
        data['interrupted'] = True
        print('\nMedición incompleta; se conservan las marcas registradas.')
    finally:
        save()
    print('Registro:', path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
