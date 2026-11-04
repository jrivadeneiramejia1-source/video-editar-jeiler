"""Funciones comunes de graficos-por-palabra: texto normalizado y lectura de palabras.json."""
import difflib, json, re, unicodedata

_NUM = dict(zip(map(str, range(21)), "cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciseis diecisiete dieciocho diecinueve veinte".split()))

def norm(t):
    """Texto en minúscula, sin tildes (la ñ se conserva) y sin signos: lista de palabras. Los números del 0 al 20 se escriben con letras."""
    t = unicodedata.normalize("NFD", t.lower().replace("ñ", "\u0001"))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn").replace("\u0001", "ñ")
    return [_NUM.get(p, p) for p in re.findall(r"[a-zñ0-9]+", t)]

def cargar_palabras(ruta):
    """palabras.json (de subtitulos/transcribir.py) -> lista de {w, a, l, n: palabra normalizada, fin: fin estimado}."""
    W = json.load(open(ruta, encoding="utf-8")); P = []
    for o in W:
        for n in norm(o["w"]) or [""]:
            P.append({"w": o["w"], "a": o["a"], "l": o["l"], "n": n})
    for i, p in enumerate(P):   # el reconocedor da el inicio de cada palabra; el fin se estima (último trozo + 0,3 s, sin pasar de la palabra siguiente)
        sig = P[i + 1]["a"] if i + 1 < len(P) else p["l"] + 0.5
        p["fin"] = min(p["l"] + 0.3, sig)
    return P
