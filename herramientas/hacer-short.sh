#!/usr/bin/env bash
# Convierte un clip horizontal (16:9) en un Short/TikTok vertical 1080x1920.
# Uso:
#   ./hacer-short.sh -i clip.mp4 [-v voz.wav] [-g "TEXTO GANCHO"] [-s subtitulos.srt] [-d 60] [-o salida.mp4]
#   -i  clip de vídeo (obligatorio)
#   -v  tu voz ya limpia (limpiar-voz.sh). El audio del juego baja solo cuando hablas
#   -g  texto grande arriba durante los 3 primeros segundos
#   -s  subtítulos .srt quemados en el vídeo
#   -d  duración máxima en segundos (por defecto 60)
#   -o  archivo de salida (por defecto <clip>-short.mp4)
set -euo pipefail

voz="" gancho="" subs="" dur=60 salida=""
while getopts "i:v:g:s:d:o:" opt; do
  case $opt in
    i) clip="$OPTARG" ;; v) voz="$OPTARG" ;; g) gancho="$OPTARG" ;;
    s) subs="$OPTARG" ;; d) dur="$OPTARG" ;; o) salida="$OPTARG" ;;
    *) sed -n '2,10p' "$0"; exit 1 ;;
  esac
done
: "${clip:?Falta -i clip.mp4}"
salida="${salida:-${clip%.*}-short.mp4}"

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

# Fuente: DejaVu Sans Bold si existe (Linux); si no, la que encuentre el sistema
fuente_ttf="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if [[ -f "$fuente_ttf" ]]; then fuente="fontfile=$fuente_ttf"; else fuente="font=Arial"; fi

# Vídeo: fondo = el mismo clip ampliado y difuminado; encima, el clip original centrado
v="[0:v]split[a][b];\
[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30[fondo];\
[b]scale=1080:-2[frente];\
[fondo][frente]overlay=(W-w)/2:(H-h)/2"

if [[ -n "$gancho" ]]; then
  # textfile evita problemas con tildes, comillas y dos puntos
  printf '%s' "$gancho" > "$tmp/gancho.txt"
  v+=",drawtext=$fuente:textfile=$tmp/gancho.txt:fontsize=78:fontcolor=white:borderw=7:bordercolor=black:x=(w-text_w)/2:y=h*0.14:enable='lt(t,3)'"
fi
if [[ -n "$subs" ]]; then
  cp "$subs" "$tmp/subs.srt"
  v+=",subtitles=$tmp/subs.srt:force_style='FontName=DejaVu Sans,Bold=1,FontSize=12,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=3,Alignment=2,MarginV=70'"
fi
v+="[v]"

if [[ -n "$voz" ]]; then
  # Audio: el juego baja de volumen automáticamente cuando suena tu voz (ducking)
  a="[0:a]volume=0.5[juego];[1:a]asplit[voz1][voz2];\
[juego][voz1]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=300[juego_bajo];\
[juego_bajo][voz2]amix=inputs=2:duration=longest:normalize=0[a]"
  ffmpeg -hide_banner -loglevel error -y -i "$clip" -i "$voz" \
    -filter_complex "$v;$a" -map "[v]" -map "[a]" -t "$dur" -shortest \
    -c:v libx264 -preset medium -crf 20 -r 30 -pix_fmt yuv420p -c:a aac -b:a 192k "$salida"
else
  ffmpeg -hide_banner -loglevel error -y -i "$clip" \
    -filter_complex "$v" -map "[v]" -map 0:a? -t "$dur" \
    -c:v libx264 -preset medium -crf 20 -r 30 -pix_fmt yuv420p -c:a aac -b:a 192k "$salida"
fi
echo "Listo: $salida"
