#!/bin/bash
# Instala lo necesario para limpiar el audio con IA y sacar el tiempo de cada palabra. Se corre UNA vez por computador o sesión.
# Uso: bash instalar_modelos.sh            (modelos en $VIDEO_JEILER_MODELOS o ~/.cache/video-jeiler/modelos, ~520 MB)
# Crea un entorno de Python propio en ese mismo lugar (venv) para no tocar el Python del sistema.
# Necesita internet, python3, curl y tar con bzip2. Descarga solo desde github.com (k2-fsa/sherpa-onnx y microsoft/DNS-Challenge).
set -euo pipefail
BASE="${VIDEO_JEILER_MODELOS:-$HOME/.cache/video-jeiler}"
M="$BASE/modelos"; mkdir -p "$M"
if [ ! -x "$BASE/venv/bin/python" ]; then python3 -m venv "$BASE/venv"; fi
"$BASE/venv/bin/pip" install --quiet sherpa-onnx numpy onnxruntime 2>&1 | grep -v "notice" || true
R=https://github.com/k2-fsa/sherpa-onnx/releases/download
dl(){ [ -s "$M/$2" ] || { echo "bajando $2 ..."; curl -fsSL --retry 3 -o "$M/$2.tmp" "$1" && mv "$M/$2.tmp" "$M/$2"; }; }
dl $R/asr-models/silero_vad.onnx silero_vad.onnx                                   # detecta dónde hay voz
dl $R/speech-enhancement-models/dpdfnet_baseline.onnx dpdfnet_baseline.onnx         # quita el ruido de fondo
dl https://raw.githubusercontent.com/microsoft/DNS-Challenge/master/DNSMOS/DNSMOS/sig_bak_ovr.onnx sig_bak_ovr.onnx   # mide qué tan limpio quedó
if [ ! -d "$M/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8" ]; then
  dl $R/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2 parakeet.tar.bz2   # transcribe en español con tiempo por palabra
  tar xjf "$M/parakeet.tar.bz2" -C "$M" && rm "$M/parakeet.tar.bz2"
fi
echo "LISTO. Python: $BASE/venv/bin/python | modelos: $M"
