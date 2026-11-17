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

# --- Opcional: convertir la voz al timbre de Aitor (FreeVC + WavLM, ~2,6 GB) ---
# Uso: CON_FREEVC=1 source herramientas/instalar-voz.sh ; luego VOZ_REFERENCIA=mi-voz.wav
if [[ "${CON_FREEVC:-0}" == "1" ]]; then
  F="$D/voice_conversion_models--multilingual--vctk--freevc24"
  if [[ ! -f "$F/model.pth" ]]; then
    curl -sL -o "$D/freevc.zip" https://github.com/coqui-ai/TTS/releases/download/v0.13.0_models/voice_conversion_models--multilingual--vctk--freevc24.zip
    unzip -oq "$D/freevc.zip" -d "$D"
  fi
  mkdir -p "$HOME/.local/share/tts"
  [[ -f "$HOME/.local/share/tts/WavLM-Large.pt" ]] || curl -sL -o "$HOME/.local/share/tts/WavLM-Large.pt" \
    https://github.com/coqui-ai/TTS/releases/download/v0.13.0_models/WavLM-Large.pt
  export FREEVC_DIR="$F"
  echo "FreeVC listo. Exporta VOZ_REFERENCIA=/ruta/a/tu-voz.wav antes de generar."
fi

# --- Voz Kokoro (por defecto en generar-short.py; licencia Apache-2.0) ---
K="$D/kokoro"
mkdir -p "$K"
"$D/venv/bin/pip" install -q kokoro-onnx soundfile
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [[ -f "$K/$f" ]] || curl -sL -o "$K/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
export KOKORO_DIR="$K"
echo "Kokoro listo (KOKORO_VOZ=em_santa por defecto; también em_alex, ef_dora)."

# --- Playwright MCP: Chromium donde lo busca, sin sandbox (somos root en el contenedor) ---
if [[ -x /opt/pw-browsers/chromium-1194/chrome-linux/chrome && ! -x /opt/google/chrome/chrome ]]; then
  mkdir -p /opt/google/chrome
  printf '#!/bin/sh\nexec /opt/pw-browsers/chromium-1194/chrome-linux/chrome --no-sandbox "$@"\n' > /opt/google/chrome/chrome
  chmod +x /opt/google/chrome/chrome
fi
