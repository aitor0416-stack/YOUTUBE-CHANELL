# Montar el entorno en una sesión nueva

El contenedor cloud empieza vacío en cada sesión: solo está el repo. Esto deja listo todo lo que
necesita `herramientas/producir.sh`. Orden recomendado (unos 5–10 minutos).

## 1. Voz (Kokoro, y Coqui de reserva)
```bash
SOLO_KOKORO=1 source herramientas/instalar-voz.sh   # ~2 min: venv + Kokoro en ~/voz-tts (sin Coqui/torch)
# source herramientas/instalar-voz.sh              # completo, con Coqui de reserva (varios GB)
```
- Kokoro (`~/voz-tts/kokoro/kokoro-v1.0.onnx` + `voices-v1.0.bin`) es la voz por defecto,
  `em_santa`. Licencia Apache-2.0 (sirve para monetizar).
- HuggingFace está bloqueado en el entorno: por eso todo se baja de releases de GitHub.
- El índice de PyTorch CPU también está bloqueado: torch se instala desde PyPI normal (ya lo hace
  el script).
- `CON_FREEVC=1` añade la conversión al timbre de Aitor (~2,6 GB). Solo si hay grabación suya
  (`VOZ_REFERENCIA=grabacion.wav`).

## 2. Tráileres oficiales en 4K → `~/trailers/` (pide los 3 en una sola llamada, ~27 créditos)
YouTube está bloqueado para descargas directas. Firecrawl devuelve un enlace firmado de
storage.googleapis.com que **caduca en 1 hora** (descárgalo enseguida).

```
alexandria_library_read  calls=[{"provider":"youtube","capability":"read",
  "options":{"url":"https://www.youtube.com/watch?v=<ID>","formats":["video"]}}]
```
Coge `data.document.video` de cada resultado (si la respuesta es muy grande queda en un archivo: sácalo con python/jq) y `curl -sS -o ~/trailers/<nombre>.mp4 '<url>'`.

| Archivo | ID | Recorte (franjas negras) |
|---|---|---|
| launch.mp4 | rz1B4B2yBZY | 3840x1920 desde y=120 |
| t1.mp4 | QdBZY2fkU-0 | sin franjas (3840x2160) |
| t2.mp4 | VQRLujxTm3c | 3840x1728 desde y=216 |
| gtav.mp4 (opcional, comparativas) | hvoD7ehZPcM | 720p, 60 s, sin catalogar |

Cuesta ~9 créditos por vídeo. Comprueba con `ffprobe` que miden 3840 de ancho.

## 3. Playwright (revisión en navegador)
`scripts/abrir-revision.sh` ya crea el lanzador si falta. Lo que hace, por si hay que repetirlo
a mano: Playwright busca `/opt/google/chrome/chrome`; se crea un script que ejecuta
`/opt/pw-browsers/chromium-*/chrome-linux/chrome --no-sandbox "$@"` (somos root: sin
`--no-sandbox` no arranca). No instales otro Playwright ni otro navegador.

## 4. Comprobar
```bash
herramientas/producir.sh 03-guiones/23-4-secretos-en-24-horas.json
```
Debe acabar con `OK  20.7s  1080,1920,1:1  RESULTADO: SINCRONIZADO`. Si `producir.sh` no
encuentra algo, dice qué archivo falta. Variables para rutas propias: `PYTHON`, `KOKORO_DIR`,
`TRAILERS_DIR`, `REVISION_DIR`.

## Red: qué se puede y qué no
- Se puede: GitHub, PyPI/npm, storage.googleapis.com, Firecrawl.
- Bloqueado: YouTube (descarga directa), rockstargames.com (descarga directa; Firecrawl sí puede
  leer la página, pero no capturar imágenes sueltas), HuggingFace, índice CPU de PyTorch.
- Si algo nuevo da 403 del proxy, lee `read_documentation` (environment.network) antes de pedir
  cambios.
