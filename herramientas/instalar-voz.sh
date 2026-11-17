#!/usr/bin/env bash
# Instala la voz sintética en español (Coqui TTS, modelo VITS css10) para generar-short.py.
# Uso: source herramientas/instalar-voz.sh [carpeta]   (por defecto ~/voz-tts)
# Después: python generar-short.py usa COQUI_MODEL_DIR y el python del venv ($VOZ_PY).
set -euo pipefail
D="${1:-$HOME/voz-tts}"
mkdir -p "$D"
[[ -d "$D/venv" ]] || python3 -m venv "$D/venv"
"$D/venv/bin/pip" install -q coqui-tts "coqui-tts[codec]" torch torchaudio six
M="$D/tts_models--es--css10--vits"
if [[ ! -f "$M/model_file.pth" ]]; then
  curl -sL -o "$D/css10.zip" https://github.com/coqui-ai/TTS/releases/download/v0.8.0_models/tts_models--es--css10--vits.zip
  unzip -oq "$D/css10.zip" -d "$D"
  cp "$M/model_file.pth.tar" "$M/model_file.pth"
  # el config trae una ruta absoluta de la máquina del autor: la apuntamos al archivo local
  sed -i "s#\"speakers_file\": \"[^\"]*\"#\"speakers_file\": \"$M/speaker_ids.json\"#" "$M/config.json"
fi
export COQUI_MODEL_DIR="$M"
export VOZ_PY="$D/venv/bin/python"
echo "Voz lista. Ejemplo: \$VOZ_PY herramientas/generar-short.py 03-guiones/01-gta6-sale-en-2-dias.json 05-videos-finales/01.mp4"
