#!/usr/bin/env python3
"""Propone el tiempo de cada subtítulo comparando el guion con lo que se dijo de verdad.
Uso:  python alinear_guion.py cues.txt palabras.json [salida.json]
  cues.txt      un subtítulo por línea, EXACTO como en el guion; usa  |  para partir en dos renglones. Ejemplo:
                    Hola, hoy preparamos una limonada.
                    Primero, lava bien los limones | y exprímelos en una jarra.
  palabras.json el que genera transcribir.py.
Resultado: salida.json = [{a: inicio, b: fin, lines: [...]}] (para a_srt.py) y una tabla para revisar.
Los tiempos son una PROPUESTA: si la tabla dice REVISAR, o la persona leyó distinto, ajústalo a mano."""
import difflib, json, sys
from _comun import norm

if len(sys.argv) < 3: sys.exit(__doc__)
cues = [l.strip() for l in open(sys.argv[1], encoding="utf-8") if l.strip()]
W = json.load(open(sys.argv[2], encoding="utf-8"))
S = [(w, i) for i, c in enumerate(cues) for w in norm(c.replace("|", " "))]   # palabras del guion: (palabra, n_cue)
H = [(w, o["a"]) for o in W for w in norm(o["w"])]                             # palabras oídas: (palabra, segundo)
sm = difflib.SequenceMatcher(None, [w for w, _ in S], [w for w, _ in H], autojunk=False)
tiempo = {}
for tag, i1, i2, j1, j2 in sm.get_opcodes():
    if tag == "equal":
        for k in range(i2 - i1): tiempo[i1 + k] = H[j1 + k][1]
res = []; prev = 0.0; filas = []
for ci, c in enumerate(cues):
    idx = [i for i, (_, n) in enumerate(S) if n == ci]
    ok = [(k, i) for k, i in enumerate(idx) if i in tiempo]
    if ok:
        k, i = ok[0]; a = tiempo[i] - 0.38 * k; flag = "" if k == 0 else "REVISAR (la 1a palabra no se oyó igual)"
    else:
        a = prev + 1.0; flag = "REVISAR (ninguna palabra coincide)"
    a = max(a, prev + 0.1); res.append({"a": round(a, 2), "lines": [x.strip() for x in c.split("|")]}); prev = a
    filas.append((len(ok), len(idx), flag))
fin = W[-1]["l"] + 0.8
for i, r in enumerate(res): r["b"] = round((res[i + 1]["a"] - 0.03) if i + 1 < len(res) else fin, 2)
out = sys.argv[3] if len(sys.argv) > 3 else "cues_propuestos.json"
json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("%-3s %7s %7s  %-9s %s" % ("#", "inicio", "fin", "palabras", "texto"))
for i, (r, (n, m, fl)) in enumerate(zip(res, filas)):
    print("%-3d %7.2f %7.2f  %3d/%-3d    %s %s" % (i, r["a"], r["b"], n, m, " / ".join(r["lines"])[:60], fl))
print("palabras del guion encontradas en la voz: %d de %d (%.0f%%)" % (len(tiempo), len(S), 100 * len(tiempo) / max(len(S), 1)))
