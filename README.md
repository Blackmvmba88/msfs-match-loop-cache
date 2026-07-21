# Game cache and disk cleanup tools

Herramientas locales para jugar desde Chrome con cache persistente y para pasar archivos pesados a una USB sin borrar nada por accidente.

## USB detectada

Por defecto los scripts usan:

```bash
/Volumes/ADATA SC740
```

Si conectas otra USB, cambia la variable `USB_VOLUME`.

## Uso rapido

Desde la USB:

```bash
cd "/Volumes/ADATA SC740/GameCacheCleanupRepo"
./scripts/menu.sh
```

El menu permite abrir el simulador, correr diagnostico, buscar archivos pesados y limpiar metadata de macOS en la USB.

## Abrir Chrome con cache grande en la USB

```bash
./scripts/launch_chrome_game_cache.sh "https://URL-DEL-JUEGO"
```

Tambien puedes dejar la URL vacia y pegarla manualmente:

```bash
./scripts/launch_chrome_game_cache.sh
```

Esto no modifica el juego. Solo abre Chrome usando un directorio de cache en la USB:

```text
/Volumes/ADATA SC740/ChromeGameCache/cache
```

Tambien usa un perfil dedicado de Chrome en la USB:

```text
/Volumes/ADATA SC740/ChromeGameCache/profile
```

Ese perfil ayuda a conservar sesion, cookies y cache de Xbox Cloud Gaming sin mezclarlo con tu Chrome normal.

## Microsoft Flight Simulator desde Chrome

Si lo juegas desde Chrome por Xbox Cloud Gaming, la PC no descarga el simulador completo. El juego corre en servidores de Xbox y Chrome recibe video/controles. Por eso la cache local solo ayuda con la pagina web, cookies, sesion y algunos recursos del navegador; no puede guardar todos los "paquetes" internos del simulador.

Para abrir Xbox Cloud Gaming con la cache en USB:

```bash
./scripts/launch_msfs_cloud.sh
```

Recomendaciones para que cargue mas estable:

- Usa siempre el mismo perfil de Chrome.
- No uses modo incognito.
- No borres cookies ni datos del sitio de `xbox.com`.
- Conecta la Mac por Ethernet o usa Wi-Fi 5 GHz cerca del modem.
- Cierra pestañas, descargas y apps pesadas antes de abrir el simulador.

## Buscar archivos pesados

```bash
./scripts/scan_large_files.sh
```

El reporte se guarda en `reports/` y lista archivos grandes en Desktop, Downloads, Documents, Movies, Music y Pictures.

Puedes cambiar el tamano minimo:

```bash
MIN_SIZE=1G ./scripts/scan_large_files.sh
```

## Copiar o mover cosas a la USB

Primero copia, no borres:

```bash
./scripts/copy_to_usb.sh "/ruta/al/archivo-o-carpeta"
```

Cuando ya confirmes que se copio bien, puedes mover:

```bash
./scripts/copy_to_usb.sh --move "/ruta/al/archivo-o-carpeta"
```

El destino por defecto es:

```text
/Volumes/ADATA SC740/OffloadedFiles
```

El script ahora revisa que haya espacio disponible y verifica la copia antes de permitir borrar el original con `--move`.

## Diagnostico

```bash
./scripts/doctor.sh
```

Revisa si la USB esta montada, cuanto espacio queda, si Chrome existe, donde queda la cache y si el repo Git esta bien.

## Limpiar metadata de la USB

macOS puede crear archivos `._*` y `.DS_Store` en unidades externas. Para limpiarlos:

```bash
./scripts/clean_usb_metadata.sh
```

El script pide confirmacion antes de borrar.

## Flujo recomendado

1. Corre `./scripts/doctor.sh`.
2. Abre MSFS con `./scripts/launch_msfs_cloud.sh`.
3. Corre `./scripts/scan_large_files.sh`.
4. Revisa el reporte en `reports/`.
5. Copia primero lo pesado con `./scripts/copy_to_usb.sh`.
6. Abre y confirma que los archivos estan bien en la USB.
7. Solo despues usa `--move` si quieres liberar espacio del disco interno.
