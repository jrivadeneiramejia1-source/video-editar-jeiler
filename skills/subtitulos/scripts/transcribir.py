#!/usr/bin/env python3
"""Voz -> palabras.json con el segundo en que empieza cada palabra (sin internet; usa los modelos de instalar_modelos.sh).
Uso:  python transcribir.py AUDIO_O_VIDEO palabras.json
Lista: [{"w": palabra, "a": inicio en s, "l": último trozo en s}]. También imprime el texto completo para leerlo contra el guion.
Usar el Python de la instalación (~/.cache/video-jeiler/venv/bin/python)."""
import json, sys
from _comun import audio_16k, palabras

if len(sys.argv) != 3: sys.exit(__doc__)
W = palabras(audio_16k(sys.argv[1]))
json.dump(W, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(" ".join(w["w"] for w in W)); print(f"\n{len(W)} palabras; primera en {W[0]['a']:.2f} s, última en {W[-1]['a']:.2f} s -> {sys.argv[2]}" if W else "\nNo se oyó ninguna palabra.")
