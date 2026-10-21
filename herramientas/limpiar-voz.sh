#!/usr/bin/env bash
# Limpia una grabación de voz para YouTube.
# Uso: ./limpiar-voz.sh entrada.(wav|mp3|m4a|ogg) [salida.wav]
set -euo pipefail

entrada="${1:?Uso: $0 entrada [salida.wav]}"
salida="${2:-${entrada%.*}-limpio.wav}"

# 1. highpass 80Hz      -> quita zumbidos graves (mesa, ventilador, golpes)
# 2. afftdn             -> reduce ruido de fondo constante
# 3. silenceremove      -> recorta pausas de más de 0,6 s dejando 0,3 s (ritmo más ágil)
# 4. equalizer 3kHz     -> un poco más de claridad en la voz
# 5. deesser            -> suaviza las "s" fuertes
# 6. acompressor        -> iguala partes flojas y fuertes
# 7. loudnorm -14 LUFS  -> volumen estándar de YouTube
ffmpeg -hide_banner -loglevel error -y -i "$entrada" -af "\
highpass=f=80,\
afftdn=nf=-25,\
silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.6:stop_threshold=-45dB:stop_silence=0.3,\
equalizer=f=3000:t=q:w=1:g=2,\
deesser,\
acompressor=threshold=-20dB:ratio=3:attack=10:release=200:makeup=2,\
loudnorm=I=-14:TP=-1.5:LRA=11" \
  -ar 48000 -ac 1 "$salida"

echo "Listo: $salida"
