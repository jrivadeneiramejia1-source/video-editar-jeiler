#!/usr/bin/env python3
"""Revisa los subtítulos SIN escuchar el video: vuelve a transcribir su audio y compara.
Uso:  python verificar_subtitulos.py VIDEO_O_AUDIO subtitulos.srt
Comprueba: (1) cada subtítulo aparece cuando se dice su primera palabra (puede salir hasta 0,45 s ANTES de la voz o hasta 0,3 s DESPUÉS),
           (2) el texto de los subtítulos coincide con lo que se oye (> 93 %).
Sale con código 1 si algo falla. Claude no oye el audio: esto mide, no escucha."""
import difflib, sys
import numpy as np
from _comun import audio_16k, leer_srt, norm, palabras

if len(sys.argv) != 3: sys.exit(__doc__)
cues = leer_srt(sys.argv[2]); H = palabras(audio_16k(sys.argv[1]))
Hf = [(n, o["a"]) for o in H for n in norm(o["w"])]
bad = []; offs = []
for c in cues:
    pal = norm(" ".join(c["lines"]))
    if not pal: continue
    for k in range(min(3, len(pal))):   # si el reconocedor falla en la 1a palabra, se prueba con la 2a o la 3a (~0,38 s cada una)
        esperado = c["a"] + 0.38 * k
        cand = [t for n, t in Hf if n == pal[k] and esperado - 0.8 <= t < esperado + 1.2]
        if cand: break
    else:
        bad.append((round(c["a"], 2), f'no se oye "{pal[0]}"')); continue
    t = min(cand, key=lambda z: abs(z - esperado)); d = esperado - t; offs.append(d)
    if d > 0.3 or d < -0.45: bad.append((round(c["a"], 2), f"el subtítulo sale {abs(d):.2f} s {'después' if d > 0 else 'antes'} de la voz"))
ok1 = not bad
print("1) tiempos: %d subtítulos revisados | desfase medio %+.2f s (+ = el subtítulo sale después), máx %.2f s | fuera de rango: %s  %s" % (
    len(offs), np.mean(offs) if offs else 0, np.max(np.abs(offs)) if offs else 0, bad, "OK" if ok1 else "<-- REVISAR"))
heard = [n for n, _ in Hf]; sub = [n for c in cues for n in norm(" ".join(c["lines"]))]
sm = difflib.SequenceMatcher(None, sub, heard, autojunk=False); ratio = sm.ratio() * 100; ok2 = ratio > 93
print("2) texto de los subtítulos vs voz re-transcrita: %.1f%% de coincidencia  %s" % (ratio, "OK" if ok2 else "<-- REVISAR"))
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag != "equal": print("     ", tag, "SUBT:", " ".join(sub[i1:i2]), "| VOZ:", " ".join(heard[j1:j2]))
sys.exit(0 if ok1 and ok2 else 1)
