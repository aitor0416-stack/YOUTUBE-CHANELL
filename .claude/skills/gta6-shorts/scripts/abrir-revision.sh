#!/usr/bin/env bash
# Deja lista la revisión en navegador de los vídeos que preparó herramientas/producir.sh.
# Uso: abrir-revision.sh 19-bigfoot-existe-en-gta6 20-cuidado-al-abrir-maleteros ...
# Imprime la URL que hay que abrir con Playwright (browser_navigate).
set -u
AQUI="$(cd "$(dirname "$0")" && pwd)"
SCRATCH="${SCRATCH:-/tmp/claude-0/-home-user-youtube-chanell/c1131a47-7b00-5938-b10f-969b1c8a02a8/scratchpad}"
REVISION_DIR="${REVISION_DIR:-$SCRATCH/check}"
PUERTO="${PUERTO:-8765}"
[ $# -ge 1 ] || { echo "Uso: $0 nombre-video [otro ...]"; exit 2; }

# 1) Playwright busca Chrome en /opt/google/chrome; como somos root necesita --no-sandbox
if [ ! -x /opt/google/chrome/chrome ]; then
  CR=$(ls -d /opt/pw-browsers/chromium-*/chrome-linux/chrome 2>/dev/null | head -1)
  [ -n "$CR" ] || { echo "No encuentro Chromium en /opt/pw-browsers"; exit 1; }
  mkdir -p /opt/google/chrome
  printf '#!/bin/sh\nexec %s --no-sandbox "$@"\n' "$CR" > /opt/google/chrome/chrome
  chmod +x /opt/google/chrome/chrome
fi

# 2) que existan las copias webm/vtt
for n in "$@"; do
  [ -f "$REVISION_DIR/v/$n.webm" ] && [ -f "$REVISION_DIR/v/$n.vtt" ] || { echo "Falta $REVISION_DIR/v/$n.webm o .vtt (pasa antes herramientas/producir.sh)"; exit 1; }
done

# 3) página + servidor con Range
cp "$AQUI/revision.html" "$REVISION_DIR/index.html"
if ! curl -s -o /dev/null "http://127.0.0.1:$PUERTO/index.html"; then
  nohup python3 "$AQUI/servidor_rangos.py" "$REVISION_DIR" "$PUERTO" > "$REVISION_DIR/server.log" 2>&1 &
  for _ in 1 2 3 4 5 6 7 8 9 10; do curl -s -o /dev/null "http://127.0.0.1:$PUERTO/index.html" && break; python3 -c "import time; time.sleep(0.3)"; done
fi
LISTA=$(IFS=,; echo "$*")
echo "http://127.0.0.1:$PUERTO/index.html?v=$LISTA&t=$(date +%s)"
