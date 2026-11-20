#!/usr/bin/env bash
# producir.sh — de guion a Short revisado, en un paso.
#
# Uso:
#   herramientas/producir.sh 03-guiones/24-algo.json [03-guiones/25-otro.json ...]
#
# Para cada guion: 1) revisa el guion (validar-guion.py), 2) genera el vídeo en 05-videos-finales/,
# 3) comprueba que los subtítulos van con la voz (verificar-sync.py), 4) busca subtítulos de más de
# 14 caracteres (se cortan), 5) hace una hoja de fotogramas para mirarla, 6) prepara una copia webm
# + vtt para revisarla en el navegador con Playwright (este Chromium no lee H.264).
# Al final imprime un resumen; sale con 1 si algún vídeo tiene problemas.
#
# Variables (con valores por defecto pensados para la sesión cloud):
#   PYTHON        python del entorno con kokoro-onnx (por defecto el venv de la sesión, si existe)
#   KOKORO_DIR    modelos de Kokoro
#   TRAILERS_DIR  launch.mp4, t1.mp4, t2.mp4
#   REVISION_DIR  carpeta donde van las hojas de fotogramas y las copias webm
#   PARALELO      vídeos a la vez (3 por defecto; más de 5 satura la máquina)
set -u
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
# Dónde buscar lo instalado: primero lo que diga el entorno, luego ~/voz-tts (instalar-voz.sh),
# luego la carpeta temporal de la sesión (SCRATCH) en la que se montó todo la primera vez.
SCRATCH="${SCRATCH:-/tmp/claude-0/-home-user-youtube-chanell/c1131a47-7b00-5938-b10f-969b1c8a02a8/scratchpad}"
primero() { for x in "$@"; do [ -e "$x" ] && { echo "$x"; return; }; done; echo "$1"; }
PYTHON="${PYTHON:-${VOZ_PY:-$(primero "$HOME/voz-tts/venv/bin/python" "$SCRATCH/tts/coqui/bin/python")}}"
export KOKORO_DIR="${KOKORO_DIR:-$(primero "$HOME/voz-tts/kokoro" "$SCRATCH/kokoro")}"
export TRAILERS_DIR="${TRAILERS_DIR:-$(primero "$HOME/trailers" "$SCRATCH/trailers")}"
REVISION_DIR="${REVISION_DIR:-$SCRATCH/check}"
PARALELO="${PARALELO:-3}"
export GUARDAR_VOZ=1
mkdir -p "$REVISION_DIR/v" "$REVISION_DIR/hojas"

[ $# -ge 1 ] || { sed -n 2,20p "$0"; exit 2; }
for f in "$KOKORO_DIR/kokoro-v1.0.onnx" "$TRAILERS_DIR/t1.mp4"; do
  [ -f "$f" ] || { echo "Falta $f (ver herramientas/instalar-voz.sh y CLAUDE.md, apartado tráileres)"; exit 2; }
done

# 1) revisar todos los guiones antes de gastar tiempo en generar
"$PYTHON" -I "$RAIZ/herramientas/validar-guion.py" "$@" || { echo "Corrige los guiones y vuelve a lanzar."; exit 1; }

# 2) generar (en paralelo)
printf '%s\n' "$@" | xargs -P "$PARALELO" -I{} sh -c '
  n=$(basename "{}" .json)
  "'"$PYTHON"'" "'"$RAIZ"'/herramientas/generar-short.py" "{}" "'"$RAIZ"'/05-videos-finales/$n.mp4" > "'"$REVISION_DIR"'/log_$n.txt" 2>&1 \
    && tail -1 "'"$REVISION_DIR"'/log_$n.txt" || { echo "ERROR generando $n (ver '"$REVISION_DIR"'/log_$n.txt)"; tail -5 "'"$REVISION_DIR"'/log_$n.txt"; }'

# 3-6) comprobar cada vídeo
problemas=0
echo; echo "== Resumen =="
for g in "$@"; do
  n=$(basename "$g" .json); base="$RAIZ/05-videos-finales/$n"
  if [ ! -f "$base.mp4" ]; then echo "$n: NO GENERADO"; problemas=$((problemas+1)); continue; fi
  sync=$("$PYTHON" -I "$RAIZ/herramientas/verificar-sync.py" "$base.srt" "$base.voz.wav" | tail -1)
  largos=$("$PYTHON" -I -c '
import sys
bloques=open(sys.argv[1],encoding="utf-8").read().split("\n\n")
print(" | ".join(b.split("\n")[2] for b in bloques if len(b.split("\n"))>2 and len(b.split("\n")[2])>14))' "$base.srt")
  dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$base.mp4")
  tam=$(ffprobe -v error -select_streams v -show_entries stream=width,height,sample_aspect_ratio -of csv=p=0 "$base.mp4")
  ffmpeg -v error -y -i "$base.mp4" -vf "fps=1/1.5,scale=216:384,tile=12x1" -frames:v 1 "$REVISION_DIR/hojas/$n.png"
  ffmpeg -v error -y -i "$base.mp4" -c:v libvpx-vp9 -b:v 1M -deadline good -cpu-used 4 -row-mt 1 -an "$REVISION_DIR/v/$n.webm"
  ffmpeg -v error -y -i "$base.srt" "$REVISION_DIR/v/$n.vtt"
  estado="OK"
  case "$sync" in *SINCRONIZADO*) ;; *) estado="REVISAR"; problemas=$((problemas+1));; esac
  [ -n "$largos" ] && { estado="REVISAR"; problemas=$((problemas+1)); }
  [ "$tam" = "1080,1920,1:1" ] || { estado="REVISAR"; problemas=$((problemas+1)); }
  # regla del canal: 20-35 s (por debajo de 20 el algoritmo apenas lo empuja)
  awk -v d="$dur" 'BEGIN{exit !(d < 20 || d > 35)}' && { estado="REVISAR(duración)"; problemas=$((problemas+1)); }
  printf '%-45s %s  %5.1fs  %s  %s%s\n' "$n" "$estado" "$dur" "$tam" "$sync" "${largos:+  LARGOS: $largos}"
done
echo
echo "Hojas de fotogramas: $REVISION_DIR/hojas/  (míralas: textos del tráiler que tapen subtítulos, violencia al inicio)"
echo "Copias para Playwright: $REVISION_DIR/v/  (servir con servidor_rangos.py; ver la skill gta6-shorts)"
[ "$problemas" -eq 0 ] || { echo "$problemas problema(s): no entregar hasta corregirlos."; exit 1; }
