#!/usr/bin/env python3
"""Editar un video diciendo qué frases quitar o conservar (se edita la transcripción, no la línea de tiempo).

  python editar_por_texto.py buscar  palabras.json "frase"
        muestra dónde se dice esa frase (segundo, contexto, parecido).
  python editar_por_texto.py plan    palabras.json [--quitar "frase"]... [--empezar-en "frase"] [--terminar-en "frase"]
                                     [--exacto] [--margen 0.25] [--video VIDEO] [-o plan.json]
        arma la lista de cortes y la muestra para aprobarla. Por defecto, quitar una frase quita su ORACIÓN completa
        (--exacto: solo las palabras encontradas). Lo mismo con --empezar-en y --terminar-en: se conserva la oración entera de esa frase. --margen: segundos de respiro que quedan a cada lado de un corte.
        --video: lee la duración exacta del video (si no, se estima con la última palabra).
  python editar_por_texto.py aplicar VIDEO plan.json SALIDA.mp4
        corta con ffmpeg-skill (cut.py --remove --accurate) en una copia nueva; el video original no se toca.
  python editar_por_texto.py verificar SALIDA.mp4 palabras.json plan.json
        vuelve a transcribir la salida y comprueba que lo quitado no está, que lo conservado sí, y la duración.
palabras.json sale de subtitulos/scripts/transcribir.py (transcribir SIEMPRE del audio original)."""
import difflib, json, pathlib, subprocess, sys
from _comun import ampliar_a_oracion, buscar_frase, cargar_palabras, norm

AQUI = pathlib.Path(__file__).resolve().parent
CUT = AQUI.parent.parent / "ffmpeg-skill" / "scripts" / "cut.py"

def mmss(s): return f"{int(s // 60)}:{s % 60:05.2f}"

def cmd_buscar(a):
    if len(a) != 2: sys.exit(__doc__)
    P = cargar_palabras(a[0]); res = buscar_frase(P, a[1])
    if not res: print("No encontré esa frase. Prueba con otras palabras de la misma parte."); return
    for r, i, j in res:
        ctx = " ".join(p["w"] for p in P[max(0, i - 4):j + 5])
        print(f"parecido {r:.0%} | {mmss(P[i]['a'])} a {mmss(P[j]['fin'])} | «{' '.join(p['w'] for p in P[i:j + 1])}» | contexto: …{ctx}…")

def _opt(a, nombre, defecto=None, varios=False):
    out = []
    while nombre in a:
        i = a.index(nombre); out.append(a[i + 1]); del a[i:i + 2]
    return out if varios else (out[-1] if out else defecto)

def cmd_plan(a):
    quitar = _opt(a, "--quitar", varios=True); ini = _opt(a, "--empezar-en"); fin = _opt(a, "--terminar-en")
    margen = float(_opt(a, "--margen", 0.25)); salida = _opt(a, "-o", "plan.json"); video = _opt(a, "--video"); exacto = "--exacto" in a
    a = [x for x in a if x != "--exacto"]
    if len(a) != 1 or not (quitar or ini or fin): sys.exit(__doc__)
    P = cargar_palabras(a[0]); dur = P[-1]["fin"] + 0.3; rangos = []
    if video: dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True).stdout)   # rangos de palabras a quitar: (i, j, motivo)
    def mejor(frase):
        r = buscar_frase(P, frase, 1)
        if not r: sys.exit(f"No encontré «{frase}». Usa el comando buscar para ver qué se oye.")
        sc, i, j = r[0]
        if sc < 0.75: print(f"AVISO: «{frase}» solo se parece un {sc:.0%}; revisa el corte antes de aplicar.")
        return i, j
    for fr in quitar:
        i, j = mejor(fr)
        if not exacto: i, j = ampliar_a_oracion(P, i, j)
        rangos.append((i, j, f"quitar «{fr}»"))
    if ini:
        i, j = mejor(ini)
        if not exacto: i, _ = ampliar_a_oracion(P, i, j)   # empezar en el principio de esa oración
        if i > 0: rangos.append((0, i - 1, f"empezar en «{ini}»"))
    if fin:
        i, j = mejor(fin)
        if not exacto: _, j = ampliar_a_oracion(P, i, j)   # terminar al final de esa oración
        if j + 1 < len(P): rangos.append((j + 1, len(P) - 1, f"terminar en «{fin}»"))
    rangos.sort(); fus = []
    for i, j, m in rangos:   # juntar rangos que se pisan o se tocan
        if fus and i <= fus[-1][1] + 1: fus[-1] = (fus[-1][0], max(fus[-1][1], j), fus[-1][2] + " + " + m)
        else: fus.append((i, j, m))
    cortes = []
    for i, j, m in fus:
        # el corte empieza un respiro después de la palabra anterior y termina un respiro antes de la siguiente (a la mitad si la pausa es corta)
        ant = P[i - 1]["fin"] if i > 0 else 0.0; sig = P[j + 1]["a"] if j + 1 < len(P) else dur
        a_ = ant + margen if i > 0 else 0.0
        b_ = sig - margen if j + 1 < len(P) else dur
        if a_ >= b_: a_ = b_ = (ant + sig) / 2
        if i > 0 and P[i]["a"] - ant < 2 * margen: a_ = min(a_, (ant + P[i]["a"]) / 2)
        if j + 1 < len(P) and sig - P[j]["fin"] < 2 * margen: b_ = max(b_, (P[j]["fin"] + sig) / 2)
        cortes.append({"a": round(a_, 3), "b": round(b_, 3), "motivo": m, "texto_quitado": " ".join(p["w"] for p in P[i:j + 1])})
    quitado = sum(c["b"] - c["a"] for c in cortes)
    plan = {"duracion_antes": round(dur, 2), "duracion_despues": round(dur - quitado, 2), "cortes": cortes}
    json.dump(plan, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("PLAN DE CORTES (nada se ha cortado todavía; Jeiler lo aprueba):")
    for n, c in enumerate(cortes, 1): print(f"  {n}. quitar {mmss(c['a'])} a {mmss(c['b'])} ({c['b'] - c['a']:.1f} s) — {c['motivo']}\n     se oye: «{c['texto_quitado'][:110]}»")
    print(f"Duración: {dur:.1f} s -> {dur - quitado:.1f} s. Plan guardado en {salida}")

def cmd_aplicar(a):
    if len(a) != 3: sys.exit(__doc__)
    video, plan, salida = a; pl = json.load(open(plan, encoding="utf-8"))
    if pathlib.Path(salida).resolve() == pathlib.Path(video).resolve(): sys.exit("La salida no puede ser el video original.")
    if not CUT.exists(): sys.exit(f"Falta ffmpeg-skill ({CUT}). Instala el grupo editar-por-texto.")
    rem = ",".join(f"{c['a']}-{c['b']}" for c in pl["cortes"])
    r = subprocess.run([sys.executable, str(CUT), video, "--remove", rem, "--accurate", "-o", salida, "--json-brief"], capture_output=True, text=True)
    print(r.stdout[-600:] if r.returncode == 0 else r.stdout[-800:] + r.stderr[-400:]); sys.exit(r.returncode)

def cmd_verificar(a):
    if len(a) != 3: sys.exit(__doc__)
    video, pj, plan = a
    ruta = AQUI.parent.parent / "subtitulos" / "scripts" / "_comun.py"
    try:   # se carga con otro nombre porque esta skill también tiene su propio _comun.py
        import importlib.util
        sp = importlib.util.spec_from_file_location("subtitulos_comun", ruta); sub = importlib.util.module_from_spec(sp); sp.loader.exec_module(sub)
        audio_16k, palabras = sub.audio_16k, sub.palabras
    except Exception: sys.exit("Falta la skill subtitulos (y sus modelos) para verificar. Instala el grupo editar-por-texto.")
    P = cargar_palabras(pj); pl = json.load(open(plan, encoding="utf-8"))
    def quitada(p): return any(c["a"] <= (p["a"] + p["fin"]) / 2 <= c["b"] for c in pl["cortes"])
    esperado = [p["n"] for p in P if not quitada(p) and p["n"]]
    oido = [n for o in palabras(audio_16k(video)) for n in norm(o["w"])]
    sm = difflib.SequenceMatcher(None, esperado, oido, autojunk=False); ratio = sm.ratio() * 100
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True).stdout)
    ok_d = abs(dur - pl["duracion_despues"]) <= 0.6; ok_t = ratio > 93
    print(f"1) duración: {dur:.2f} s (esperada {pl['duracion_despues']:.2f} s)  {'OK' if ok_d else '<-- REVISAR'}")
    print(f"2) texto conservado vs voz re-transcrita: {ratio:.1f}% de coincidencia  {'OK' if ok_t else '<-- REVISAR'}")
    ok_q = True
    for c in pl["cortes"]:
        q = [n for o in c["texto_quitado"].split() for n in norm(o)]
        if len(q) >= 3:
            r = difflib.SequenceMatcher(None, q, oido, autojunk=False); m = sum(b.size for b in r.get_matching_blocks())
            seguidas = max((b.size for b in r.get_matching_blocks()), default=0)
            if seguidas >= max(3, len(q) // 2): ok_q = False; print(f"   <-- lo quitado «{c['texto_quitado'][:50]}…» TODAVÍA se oye ({seguidas} palabras seguidas)")
    print(f"3) lo quitado ya no se oye  {'OK' if ok_q else '<-- REVISAR'}")
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag != "equal": print("     ", tag, "ESPERADO:", " ".join(esperado[i1:i2]), "| VOZ:", " ".join(oido[j1:j2]))
    print("Claude no oye el audio: esto mide; los empalmes hay que escucharlos.")
    sys.exit(0 if ok_d and ok_t and ok_q else 1)

if len(sys.argv) < 2 or sys.argv[1] not in ("buscar", "plan", "aplicar", "verificar"): sys.exit(__doc__)
{"buscar": cmd_buscar, "plan": cmd_plan, "aplicar": cmd_aplicar, "verificar": cmd_verificar}[sys.argv[1]](sys.argv[2:])
