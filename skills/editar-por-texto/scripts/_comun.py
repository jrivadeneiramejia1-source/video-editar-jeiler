"""Funciones comunes de editar-por-texto: texto normalizado y búsqueda de frases en palabras.json."""
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

def buscar_frase(P, frase, n=3):
    """Las n mejores coincidencias de la frase en la transcripción: [(puntaje 0-1, índice_inicio, índice_fin)]."""
    f = norm(frase)
    if not f: return []
    H = [p["n"] for p in P]; res = []
    for L in range(max(1, len(f) - 2), len(f) + 3):
        for i in range(0, len(H) - L + 1):
            r = difflib.SequenceMatcher(None, f, H[i:i + L], autojunk=False).ratio()
            if r >= 0.6: res.append((r, i, i + L - 1))
    res.sort(key=lambda x: -x[0]); out = []
    for r, i, j in res:   # sin repetir ventanas que se pisan
        if all(j < a or i > b for _, a, b in out): out.append((r, i, j))
        if len(out) >= n: break
    return out

def ampliar_a_oracion(P, i, j, pausa=0.5):
    """Extiende [i, j] hasta el principio y el fin de la oración: signo . ? ! o una pausa larga."""
    while i > 0 and not P[i - 1]["w"].rstrip().endswith((".", "?", "!")) and P[i]["a"] - P[i - 1]["fin"] < pausa: i -= 1
    while j + 1 < len(P) and not P[j]["w"].rstrip().endswith((".", "?", "!")) and P[j + 1]["a"] - P[j]["fin"] < pausa: j += 1
    return i, j
