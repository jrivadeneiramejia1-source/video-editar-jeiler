#!/usr/bin/env python3
"""Convierte subtítulos a .srt y .vtt. Dos formas de partir:
  1) con guion:   python a_srt.py --cues cues.json SALIDA        (cues.json de alinear_guion.py)
  2) sin guion:   python a_srt.py --palabras palabras.json SALIDA [--max-chars 42] [--max-seg 6] [--pausa 0.5]
                  arma los subtítulos solos: máximo 2 renglones de --max-chars letras, hasta --max-seg segundos,
                  y corta en pausas largas o en . ? ! (el texto sale tal cual lo oyó el reconocedor: REVISARLO).
SALIDA se escribe sin extensión: crea SALIDA.srt y SALIDA.vtt."""
import json, sys, textwrap
from _comun import tiempo_srt

a = sys.argv[1:]
def opt(n, d):
    if n in a: i = a.index(n); v = type(d)(a[i + 1]); del a[i:i + 2]; return v
    return d
mx = opt("--max-chars", 42); seg = opt("--max-seg", 6.0); pausa = opt("--pausa", 0.5)
if len(a) != 3 or a[0] not in ("--cues", "--palabras"): sys.exit(__doc__)
modo, fuente, salida = a
if modo == "--cues":
    cues = [{"a": c["a"], "b": c["b"], "lines": c["lines"]} for c in json.load(open(fuente, encoding="utf-8"))]
else:
    W = json.load(open(fuente, encoding="utf-8")); cues = []; grupo = []
    def cerrar():
        global grupo
        if not grupo: return
        texto = " ".join(w["w"] for w in grupo); lineas = textwrap.wrap(texto, mx)
        while len(lineas) > 2: lineas = textwrap.wrap(texto, int(mx * 1.5))[:2]; break
        cues.append({"a": grupo[0]["a"], "b": min(grupo[-1]["l"] + 0.35, grupo[-1]["l"] + 1.0), "lines": lineas}); grupo = []
    for i, w in enumerate(W):
        if grupo and (w["a"] - grupo[0]["a"] > seg or w["a"] - grupo[-1]["l"] > pausa or len(" ".join(x["w"] for x in grupo + [w])) > mx * 2):
            cerrar()
        grupo.append(w)
        if w["w"][-1:] in ".?!": cerrar()
    cerrar()
    for i in range(len(cues) - 1): cues[i]["b"] = min(cues[i]["b"], cues[i + 1]["a"] - 0.03)
for ext, punto in (("srt", ","), ("vtt", ".")):
    with open(f"{salida}.{ext}", "w", encoding="utf-8") as f:
        if ext == "vtt": f.write("WEBVTT\n\n")
        for n, c in enumerate(cues, 1):
            f.write(f"{n}\n{tiempo_srt(c['a'], punto)} --> {tiempo_srt(c['b'], punto)}\n" + "\n".join(c["lines"]) + "\n\n")
print(f"{len(cues)} subtítulos -> {salida}.srt y {salida}.vtt")
