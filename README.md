# ⚡ MSFS Match Loop Cache

> **Persistent Chrome cache, diagnostics and USB utilities for Xbox Cloud Gaming and Microsoft Flight Simulator.**

![Platform](https://img.shields.io/badge/platform-macOS-black)
![Language](https://img.shields.io/badge/language-Shell-89e051)
![Cloud Gaming](https://img.shields.io/badge/Xbox-Cloud_Gaming-107C10)
![Chrome](https://img.shields.io/badge/Chrome-Persistent_Profile-4285F4)
![Safety](https://img.shields.io/badge/storage-copy_first-success)

Una caja de herramientas local para lanzar Xbox Cloud Gaming desde un perfil dedicado de Chrome, conservar cache web en una unidad externa, medir estabilidad de red, revisar el estado del sistema y liberar espacio del disco interno sin borrar archivos por accidente.

---

## 🚀 Qué resuelve

`msfs-match-loop-cache` convierte una USB externa en una pequeña estación operativa para cloud gaming:

- Mantiene un **perfil dedicado de Chrome** separado del navegador principal.
- Conserva sesión, cookies y cache web de Xbox Cloud Gaming.
- Proporciona un launcher especializado para **Microsoft Flight Simulator**.
- Mantiene un entorno dedicado para el stage **Match Loop**.
- Registra tamaño, actividad e historial de cache.
- Mide DNS, conexión, TLS, TTFB y tiempo total contra Xbox Cloud Gaming.
- Detecta archivos grandes en el disco interno.
- Copia y verifica archivos antes de permitir su eliminación con `--move`.
- Limpia metadata creada por macOS en unidades externas.
- Ejecuta un diagnóstico integral mediante `doctor.sh`.

> [!IMPORTANT]
> Microsoft Flight Simulator se ejecuta en servidores de Xbox Cloud Gaming. Este proyecto **no descarga ni almacena los paquetes internos del simulador o del stage**. La cache local mejora la persistencia del navegador, la sesión y ciertos recursos web; no reemplaza la infraestructura del servicio.

---

## 🧠 Arquitectura

```text
                         ┌────────────────────────┐
                         │       menu.sh          │
                         │  centro de operaciones │
                         └───────────┬────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
              ▼                      ▼                      ▼
     ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────┐
     │    Launchers    │   │   Diagnostics    │   │     Storage     │
     ├─────────────────┤   ├──────────────────┤   ├─────────────────┤
     │ Chrome + cache  │   │ doctor.sh        │   │ scan files      │
     │ Xbox Cloud      │   │ network check    │   │ copy to USB     │
     │ MSFS            │   │ cache status     │   │ safe move       │
     │ Match Loop      │   │ reports/history  │   │ metadata clean  │
     └────────┬────────┘   └─────────┬────────┘   └────────┬────────┘
              │                      │                     │
              └──────────────────────┼─────────────────────┘
                                     ▼
                         ┌────────────────────────┐
                         │   External USB volume  │
                         │ profile · cache · logs │
                         │ reports · offloaded    │
                         └────────────────────────┘
```

---

## 🧰 Herramientas incluidas

| Script | Función |
|---|---|
| `menu.sh` | Menú principal del toolkit. |
| `launch_chrome_game_cache.sh` | Abre Chrome con perfil y cache persistentes en USB. |
| `launch_msfs_cloud.sh` | Abre Microsoft Flight Simulator mediante Xbox Cloud Gaming. |
| `launch_msfs_match_loop.sh` | Lanza el entorno dedicado para Match Loop. |
| `cache_status.sh` | Mide tamaño, archivos recientes e historial de cache. |
| `network_check.sh` | Diagnostica latencia de conexión hacia Xbox Cloud Gaming. |
| `doctor.sh` | Verifica USB, espacio, Chrome, rutas y repositorio Git. |
| `scan_large_files.sh` | Busca archivos grandes en directorios del usuario. |
| `copy_to_usb.sh` | Copia o mueve datos con validación previa. |
| `clean_usb_metadata.sh` | Elimina `.DS_Store` y archivos `._*` con confirmación. |
| `create_desktop_shortcuts.sh` | Crea accesos directos ejecutables en el Escritorio. |

---

## ⚙️ Requisitos

- macOS
- Google Chrome instalado
- Bash / shell compatible
- Unidad externa montada
- Conexión activa a Xbox Cloud Gaming

La ruta configurada por defecto es:

```text
/Volumes/ADATA SC740
```

Para otra unidad, define `USB_VOLUME` antes de ejecutar los scripts:

```bash
export USB_VOLUME="/Volumes/MI_USB"
```

---

## ⚡ Inicio rápido

Desde la copia del repositorio almacenada en la USB:

```bash
cd "/Volumes/ADATA SC740/GameCacheCleanupRepo"
chmod +x ./scripts/*.sh
./scripts/doctor.sh
./scripts/menu.sh
```

También puedes generar accesos directos de doble clic:

```bash
./scripts/create_desktop_shortcuts.sh
```

### Flujo recomendado

```text
doctor
  ↓
launch MSFS / Match Loop
  ↓
cache status + network check
  ↓
scan large files
  ↓
copy to USB
  ↓
verify
  ↓
optional safe move
```

---

## 🎮 Launchers

### Chrome con cache persistente

```bash
./scripts/launch_chrome_game_cache.sh "https://URL-DEL-JUEGO"
```

También puedes abrirlo sin URL y navegar manualmente:

```bash
./scripts/launch_chrome_game_cache.sh
```

Rutas utilizadas:

```text
/Volumes/ADATA SC740/ChromeGameCache/cache
/Volumes/ADATA SC740/ChromeGameCache/profile
```

El perfil dedicado conserva sesión, cookies y recursos del navegador sin mezclarlos con tu perfil normal de Chrome.

### Microsoft Flight Simulator

```bash
./scripts/launch_msfs_cloud.sh
```

### Match Loop dedicado

```bash
./scripts/launch_msfs_match_loop.sh
```

Directorio exclusivo:

```text
/Volumes/ADATA SC740/ChromeGameCache/match-loop
```

Registro del último arranque:

```text
/Volumes/ADATA SC740/ChromeGameCache/match-loop/.last-launch
```

Para obtener el entorno más consistente:

1. Entra siempre mediante el mismo launcher.
2. Evita el modo incógnito.
3. No borres cookies ni datos de `xbox.com`.
4. Carga Match Loop y déjalo activo durante 2–3 minutos.
5. Cierra descargas, pestañas y aplicaciones pesadas antes de jugar.
6. Usa Ethernet o Wi-Fi de 5 GHz cerca del router.

Despues de jugar, cierra la ventana de Chrome de Match Loop y corre:

```bash
./scripts/post_play_optimize.sh
```

Esto guarda un snapshot, limpia metadata `._*` / `.DS_Store` y elimina los directorios de modelos opcionales indicados en el script. Conserva las caches de shaders de Chrome para evitar invalidarlas en cada limpieza. El espacio liberado no demuestra una mejora de velocidad; no se han medido tiempos de arranque.

---

## 📊 Estado e historial de cache

```bash
./scripts/cache_status.sh
```

El diagnóstico separa perfil y cache, cuenta archivos recientes y registra crecimiento histórico.

```text
/Volumes/ADATA SC740/ChromeGameCache/reports/cache-history.tsv
/Volumes/ADATA SC740/ChromeGameCache/reports/cache-status-latest.txt
```

Ejemplo conceptual de salida:

```text
MATCH LOOP CACHE STATUS
────────────────────────────────────
Profile size:      428 MB
Cache size:        1.8 GB
Recent files:      317
Last launch:       2026-07-21 21:42
USB available:     612 GB
Status:            READY
```

---

## 🌐 Diagnóstico de red

```bash
./scripts/network_check.sh
```

Mide contra `https://www.xbox.com/play`:

- resolución DNS
- conexión TCP
- negociación TLS
- tiempo hasta el primer byte
- tiempo total

Esto ayuda a distinguir un problema de cache, navegador, almacenamiento o red.

---

## 💾 Buscar archivos grandes

```bash
./scripts/scan_large_files.sh
```

Escanea:

```text
Desktop
Downloads
Documents
Movies
Music
Pictures
```

Puedes modificar el tamaño mínimo:

```bash
MIN_SIZE=1G ./scripts/scan_large_files.sh
```

Los resultados se guardan en `reports/`.

---

## 🛡️ Copia y movimiento seguro

### Copiar primero

```bash
./scripts/copy_to_usb.sh "/ruta/al/archivo-o-carpeta"
```

Destino predeterminado:

```text
/Volumes/ADATA SC740/OffloadedFiles
```

### Mover después de verificar

```bash
./scripts/copy_to_usb.sh --move "/ruta/al/archivo-o-carpeta"
```

Antes de borrar el origen, el script:

1. comprueba que la USB esté disponible;
2. valida el espacio libre;
3. realiza la copia;
4. verifica el resultado;
5. permite eliminar el original únicamente en modo `--move`.

> [!CAUTION]
> Usa `--move` solamente después de abrir y verificar manualmente los archivos copiados. La ruta segura es siempre **copiar → revisar → mover**.

---

## 🩺 Doctor del sistema

```bash
./scripts/doctor.sh
```

Comprueba:

- montaje de la USB;
- espacio disponible;
- instalación de Chrome;
- rutas del perfil y cache;
- directorios de reportes;
- estado básico del repositorio Git.

Ejecuta `doctor.sh` antes de una sesión importante o después de cambiar de unidad externa.

---

## 🧹 Limpieza de metadata macOS

```bash
./scripts/clean_usb_metadata.sh
```

Elimina archivos auxiliares como:

```text
.DS_Store
._*
```

El script solicita confirmación antes de borrar.

---

## 📁 Estructura de datos

```text
/Volumes/ADATA SC740/
├── ChromeGameCache/
│   ├── cache/
│   ├── profile/
│   ├── match-loop/
│   │   └── .last-launch
│   └── reports/
│       ├── cache-history.tsv
│       └── cache-status-latest.txt
├── GameCacheCleanupRepo/
│   ├── scripts/
│   └── reports/
└── OffloadedFiles/
```

---

## 🗺️ Roadmap

### v1.0 — Foundation

- [x] Perfil persistente de Chrome en USB
- [x] Cache web dedicada
- [x] Launcher de Xbox Cloud Gaming
- [x] Launcher de MSFS
- [x] Entorno Match Loop
- [x] Diagnóstico de cache
- [x] Diagnóstico de red
- [x] Búsqueda de archivos grandes
- [x] Copia y movimiento con validación
- [x] Limpieza segura de metadata

### v1.1 — Observability

- [ ] Dashboard de crecimiento de cache
- [ ] Clasificación automática de fallas
- [ ] Métricas por sesión
- [ ] Exportación JSON y CSV
- [ ] Alertas por poco espacio
- [ ] Comparación de latencia entre sesiones

### v1.2 — Multi-profile

- [ ] Detección automática de unidades USB
- [ ] Perfiles por juego
- [ ] Configuración mediante archivo `.env`
- [ ] Backup y restauración de perfiles
- [ ] Rotación automática de reportes

### v2.0 — GameCache Engine

- [ ] Interfaz gráfica
- [ ] Monitor en tiempo real
- [ ] Catálogo de launchers por juego
- [ ] Actualizaciones automáticas
- [ ] Motor de diagnóstico basado en reglas
- [ ] Historial visual de salud y rendimiento

---

## 🔒 Principios de seguridad

- Ningún script debe borrar datos silenciosamente.
- Las operaciones destructivas requieren confirmación o una opción explícita.
- `copy_to_usb.sh` copia por defecto.
- `--move` es una operación intencional y posterior a la validación.
- El proyecto no modifica Microsoft Flight Simulator ni Xbox Cloud Gaming.
- El perfil dedicado evita contaminar el perfil normal de Chrome.

---

## ⚠️ Limitaciones

- No controla los servidores de Xbox ni la disponibilidad del servicio.
- No puede almacenar localmente assets internos transmitidos por cloud gaming.
- La cache del navegador puede ser administrada o invalidada por Chrome o Xbox.
- Una cache grande no compensa una red inestable, pérdida de paquetes o alta latencia.
- El rendimiento de una unidad externa depende de su interfaz, formato y velocidad real.

---

## 🐍 BlackMamba Engineering

Construido como una herramienta operativa: **diagnosticar primero, copiar antes de borrar y convertir tareas repetitivas en un flujo reproducible**.

```text
Persistent profile.
Observable cache.
Safer storage.
One launch path.
```

---

## 📄 Licencia

Agrega una licencia al repositorio antes de distribuir o aceptar contribuciones externas. Para un proyecto abierto y permisivo, MIT es una opción habitual.


## Verificar cambios de arranque

Este toolkit solo controla el navegador local. Separar en cada prueba:

1. Tiempo desde ejecutar el launcher hasta que Xbox muestra su interfaz.
2. Tiempo de espera de la cola del servicio.
3. Tiempo desde iniciar el juego hasta su menú.
4. Tiempo desde seleccionar el vuelo hasta poder controlarlo.

Alternar al menos cinco sesiones de referencia y cinco con el cambio, usando
el mismo equipo, red, perfil, versión de Chrome y escenario. Registrar los
tiempos por separado, errores, mediana y rango. No borrar cookies ni caches
entre sesiones para simular un arranque habitual. Las pruebas en frío deben
registrarse aparte. El tamaño de cache y el TTFB HTTP de network_check.sh
no miden el arranque del simulador, jitter, pérdida de paquetes ni latencia
del stream.

Comparar USB y SSD interno solo con perfiles de prueba y Chrome cerrado.
No asumir que una USB o una cache mayor es más rápida. No copiar perfiles
activos ni publicar cookies, tokens o datos del perfil en el repositorio.

Una instalación local de MSFS requiere diagnóstico en el equipo donde corre
el juego: almacenamiento, complementos, paquetes y tiempos por fase.
Este proyecto no cambia esos ajustes ni expone SimConnect del servidor cloud.
