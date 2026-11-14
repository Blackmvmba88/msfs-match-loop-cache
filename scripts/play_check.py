#!/usr/bin/env python3
"""Chequeo de juego sin cambiar ajustes, cerrar apps ni borrar datos."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

GIB = 1024 ** 3


def command(args, timeout=10):
    try:
        result = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout + result.stderr
    except (OSError, subprocess.SubprocessError) as exc:
        return None, str(exc)


def ping_summary(output):
    loss = re.search(r'([\d.]+)% packet loss', output)
    timing = re.search(r'= ([\d.]+)/([\d.]+)/([\d.]+)/([\d.]+) ms', output)
    return {'lossPercent': float(loss[1]) if loss else None,
            'averageMs': float(timing[2]) if timing else None,
            'variationMs': float(timing[4]) if timing else None}


def storage(path):
    try:
        return round(shutil.disk_usage(path).free / GIB, 2)
    except OSError:
        return None


def collect(network=False):
    usb = Path(os.environ.get('USB_VOLUME', '/Volumes/ADATA SC740'))
    report = {'checkedAt': datetime.now(timezone.utc).isoformat(),
              'internalFreeGiB': storage(Path.home()),
              'usbConnected': usb.is_dir(),
              'usbFreeGiB': storage(usb) if usb.is_dir() else None,
              'chromeInstalled': any(p.exists() for p in (
                  Path('/Applications/Google Chrome.app'),
                  Path.home() / 'Applications/Google Chrome.app')),
              'recommendations': []}
    tips = report['recommendations']
    if report['internalFreeGiB'] is not None and report['internalFreeGiB'] < 15:
        tips.append('Libera espacio del Mac antes de jugar; objetivo práctico: 15 GiB libres. Revisa archivos grandes y verifica sus copias antes de borrarlos.')
    if not report['usbConnected']:
        tips.append('Conecta la ADATA para usar tu perfil habitual; el respaldo del Mac usa otra sesión.')
    elif report['usbFreeGiB'] is not None and report['usbFreeGiB'] < 5:
        tips.append('La ADATA tiene menos de 5 GiB libres; revisa su espacio antes de jugar.')
    code, battery = command(['pmset', '-g', 'batt'])
    report['power'] = 'AC' if code == 0 and 'AC Power' in battery else 'battery' if code == 0 and 'Battery Power' in battery else 'unknown'
    if report['power'] == 'battery':
        tips.append('Conecta el cargador para una sesión larga.')
    code, route = command(['/sbin/route', '-n', 'get', 'default'])
    interface = re.search(r'interface:\s+(\S+)', route) if code == 0 else None
    gateway = re.search(r'gateway:\s+([\d.]+)', route) if code == 0 else None
    report['interface'] = interface[1] if interface else None
    report['routerProbe'] = {'state': 'not-requested'}
    if network:
        if gateway:
            code, output = command(['/sbin/ping', '-n', '-c', '8', '-i', '0.25', '-W', '1000', gateway[1]], timeout=15)
            probe = ping_summary(output)
            probe['state'] = 'measured' if probe['lossPercent'] is not None else 'unavailable'
            report['routerProbe'] = probe
            if probe['lossPercent'] is not None and probe['lossPercent'] > 0:
                tips.append('El router no respondió a todos los pings. Repite con Ethernet; ICMP puede ser filtrado o limitado y no demuestra pérdida del stream.')
            if probe['averageMs'] is not None and probe['averageMs'] > 20:
                tips.append('La respuesta del router es elevada en esta muestra. Prueba Ethernet y pausa descargas que controles antes de comparar.')
        else:
            report['routerProbe'] = {'state': 'unavailable'}
    return report


def build_plan(report):
    """Reglas explicables; nunca confundir preparación con calidad del stream."""
    issues = []
    def add(priority, code, action):
        issues.append({'priority': priority, 'code': code, 'action': action})
    if not report['chromeInstalled']:
        add('block', 'chrome-missing', 'Instala Google Chrome antes de iniciar.')
    free = report.get('internalFreeGiB')
    if free is None:
        add('review', 'disk-unknown', 'No se pudo medir el espacio interno.')
    elif free < 2:
        add('block', 'disk-critical', 'Libera espacio interno; el kit requiere un margen operativo de 2 GiB para arrancar.')
    elif free < 15:
        add('review', 'disk-low', 'Revisa espacio interno; objetivo operativo: 15 GiB.')
    if not report['usbConnected']:
        add('review', 'local-profile', 'Se usará el perfil del Mac; puede pedir iniciar sesión.')
    elif report.get('usbFreeGiB') is None:
        add('review', 'usb-space-unknown', 'No se pudo medir el espacio de ADATA.')
    elif report['usbFreeGiB'] < 5:
        add('review', 'usb-low', 'Revisa espacio de ADATA antes de una sesión larga.')
    if report.get('power') == 'battery':
        add('review', 'battery', 'Conecta el cargador.')
    probe = report.get('routerProbe', {})
    if probe.get('state') != 'measured':
        add('info', 'network-unmeasured', 'Red sin medir; usa MSFS Diagnóstico para comprobar el router.')
    elif (probe.get('lossPercent') or 0) > 0 or (probe.get('averageMs') or 0) > 20:
        add('review', 'router-review', 'Compara con Ethernet; esta muestra ICMP no mide el stream de Xbox.')
    return {'readiness': 'blocked' if any(x['priority'] == 'block' for x in issues)
            else 'review' if any(x['priority'] == 'review' for x in issues) else 'ready',
            'issues': issues, 'streamQuality': 'unmeasured'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--network', action='store_true', help='Medir ocho pings al router, sin prueba de velocidad')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--save', action='store_true', help='Guardar informe local sin cookies ni historial')
    args = parser.parse_args()
    report = collect(args.network)
    if args.save:
        folder = Path.home() / 'Library/Application Support/BlackMambaFlightKit/checks'
        folder.mkdir(parents=True, exist_ok=True)
        name = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ.json')
        (folder / name).write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print('MSFS · Antes de jugar')
        print(f"Mac libre: {report['internalFreeGiB']} GiB")
        print(f"ADATA: {'conectada' if report['usbConnected'] else 'no encontrada'} · libre: {report['usbFreeGiB']} GiB")
        print(f"Chrome: {'instalado' if report['chromeInstalled'] else 'no encontrado'} · Energía: {report['power']}")
        print('Red local:', report['routerProbe'])
        for tip in report['recommendations']:
            print('•', tip)
        print('Para jugar: usa Ethernet si puedes, pausa descargas y mantén la ADATA conectada.')
        print('En Chrome revisa chrome://gpu: Video Decode indica el estado de aceleración; la decodificación del stream requiere comprobarse durante la partida.')
        print('Este chequeo no mide FPS, velocidad de Internet ni latencia del servidor Xbox.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
