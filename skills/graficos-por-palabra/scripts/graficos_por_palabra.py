#!/usr/bin/env python3
"""Poner un logo, una imagen o un texto en el video justo cuando la voz dice una palabra (ej.: dices «Gemini» y sale su logo).

  python graficos_por_palabra.py plan VIDEO palabras.json reglas.json [--plataforma youtube|shorts|tiktok|reels] [--retraso 0] [-o plan_graficos.json]
        busca cada palabra en lo que se dijo y arma la lista de gráficos (qué sale, cuándo, dónde). No cambia el video.
  python graficos_por_palabra.py aplicar VIDEO plan_graficos.json SALIDA.mp4
        pone los gráficos en una pasada (audio sin tocar) en una copia nueva; el original no se modifica.
  python graficos_por_palabra.py verificar VIDEO_ORIGINAL SALIDA.mp4 plan_graficos.json
        compara cuadros: el gráfico debe estar donde y cuando dice el plan, y el resto del cuadro no debe cambiar.

reglas.json:  {"reglas": [
   {"palabra": "Gemini",  "tipo": "logo",   "slug": "googlegemini", "posicion": "top-left",  "tamano": 0.12, "duracion": 3},
   {"palabra": "ChatGPT", "tipo": "texto",  "texto": "ChatGPT", "color": "#10A37F",          "posicion": "top-right"},
   {"palabra": "limones", "tipo": "imagen", "archivo": "limon.png", "posicion": "bottom-right", "solo_primera": true}]}
  tipo logo: "slug" (de simple-icons: logos de marca en SVG, dominio público CC0; la marca sigue siendo de su dueño) o "archivo" (svg/png propio).
         "color" opcional (por defecto el color oficial de la marca). Si el logo no existe (p. ej. OpenAI no está en Simple Icons),
         pedir el archivo a Jeiler o usar tipo texto: nunca redibujar un logo de marca.
  posicion: top-left, top-right, bottom-left, bottom-right, center. tamano: fracción del ancho (0,12 por defecto). duracion: segundos (3).
  solo_primera: true = solo la primera vez que se dice; false (por defecto) = cada vez.
Requisitos: ffmpeg con drawtext; para logos SVG, ffmpeg con librsvg o ImageMagick (convert). palabras.json sale de subtitulos/scripts/transcribir.py."""
import json, os, pathlib, re, shutil, subprocess, sys, tempfile, urllib.request
import numpy as np
from _comun import cargar_palabras, norm

CACHE = pathlib.Path(os.environ.get("VIDEO_JEILER_MODELOS", pathlib.Path.home() / ".cache" / "video-jeiler")) / "logos"
URL_ICONOS = "https://raw.githubusercontent.com/simple-icons/simple-icons/develop"

def ffprobe(video, campo):
    return subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", f"stream={campo}", "-of", "csv=p=0", str(video)], capture_output=True, text=True).stdout.strip()

def tamano_video(video):
    w, h = ffprobe(video, "width,height").split(",")[:2]; return int(w), int(h)

def svg_a_png(svg_texto, color, destino):
    """SVG -> PNG de 512 px con el color pedido (ffmpeg con librsvg; si no, ImageMagick)."""
    t = re.sub(r"<svg ", f'<svg width="512" height="512" fill="{color}" ', svg_texto, count=1)
    tmp = pathlib.Path(tempfile.mkdtemp()) / "logo.svg"; tmp.write_text(t, encoding="utf-8")
    r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", "-i", str(tmp), "-frames:v", "1", str(destino)], capture_output=True)
    if r.returncode != 0 or not pathlib.Path(destino).exists():
        if shutil.which("convert"): subprocess.run(["convert", "-background", "none", "-density", "384", str(tmp), "-resize", "512x512", str(destino)], check=True)
        else: raise ValueError("No puedo convertir el SVG a PNG: hace falta ffmpeg con librsvg o ImageMagick (convert).")

def preparar_imagen(regla, carpeta):
    """Devuelve la ruta de un PNG listo para poner (o None para texto)."""
    if regla["tipo"] == "texto": return None
    if regla["tipo"] == "imagen" or regla.get("archivo"):
        ruta = pathlib.Path(regla["archivo"])
        if not ruta.exists(): raise ValueError(f"No existe el archivo del gráfico: {ruta}")
        if ruta.suffix.lower() == ".svg":
            destino = carpeta / (ruta.stem + ".png"); svg_a_png(ruta.read_text(encoding="utf-8"), regla.get("color", "#FFFFFF"), destino); return destino
        return ruta
    slug = regla["slug"]; CACHE.mkdir(parents=True, exist_ok=True); svg = CACHE / f"{slug}.svg"
    if not svg.exists():
        try: urllib.request.urlretrieve(f"{URL_ICONOS}/icons/{slug}.svg", svg)
        except Exception: raise ValueError(f"El logo «{slug}» no está en Simple Icons (o no hay internet). Pide el archivo a Jeiler o usa tipo texto.")
    color = regla.get("color")
    if not color:   # color oficial de la marca
        try:
            datos = json.load(urllib.request.urlopen(f"{URL_ICONOS}/data/simple-icons.json", timeout=30)); datos = datos["icons"] if isinstance(datos, dict) else datos
            titulo = svg.read_text(encoding="utf-8"); titulo = re.search(r"<title>(.*?)</title>", titulo).group(1)
            color = "#" + next(i["hex"] for i in datos if i["title"] == titulo)
        except Exception: color = "#FFFFFF"
    destino = carpeta / f"{slug}.png"; svg_a_png(svg.read_text(encoding="utf-8"), color, destino); return destino

def zona(posicion, W, H, w, h, margen):
    m = int(margen * W)
    return {"top-left": (m, m), "top-right": (W - w - m, m), "bottom-left": (m, H - h - m), "bottom-right": (W - w - m, H - h - m),
            "center": ((W - w) // 2, (H - h) // 2)}[posicion]

def cmd_plan(a):
    plat = None; retraso = 0.0; salida = "plan_graficos.json"
    for nombre in ("--plataforma", "--retraso", "-o"):
        if nombre in a:
            i = a.index(nombre); v = a[i + 1]; del a[i:i + 2]
            if nombre == "--plataforma": plat = v
            elif nombre == "--retraso": retraso = float(v)
            else: salida = v
    if len(a) != 3: sys.exit(__doc__)
    video, pj, rj = a; P = cargar_palabras(pj); reglas = json.load(open(rj, encoding="utf-8"))["reglas"]; W, H = tamano_video(video)
    dur_video = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video], capture_output=True, text=True).stdout)
    carpeta = pathlib.Path(salida).resolve().parent / (pathlib.Path(salida).stem + "_img"); carpeta.mkdir(exist_ok=True)
    items = []; avisos = []
    for r in reglas:
        clave = norm(r["palabra"]); n = len(clave); hallazgos = []
        for i in range(len(P) - n + 1):
            if [p["n"] for p in P[i:i + n]] == clave: hallazgos.append(P[i]["a"])
        if not hallazgos: avisos.append(f"«{r['palabra']}» no se oye en el audio: no habrá gráfico."); continue
        if r.get("solo_primera"): hallazgos = hallazgos[:1]
        try: png = preparar_imagen(r, carpeta)
        except ValueError as e: avisos.append(f"«{r['palabra']}»: {e} (sin gráfico para esa palabra)."); continue
        dur = float(r.get("duracion", 3.0))
        for t in hallazgos:
            ini = max(0.0, t + retraso); fin = min(dur_video, ini + dur)
            items.append({"palabra": r["palabra"], "tipo": r["tipo"], "oido_en": round(t, 2), "inicio": round(ini, 2), "fin": round(fin, 2), "posicion": r.get("posicion", "top-right"),
                          "tamano": float(r.get("tamano", 0.12)), "png": str(png) if png else None, "texto": r.get("texto", r["palabra"]), "color": r.get("color", "#FFFFFF")})
    items.sort(key=lambda x: x["inicio"]); fus = []
    for x in items:   # la misma palabra dicha otra vez mientras su gráfico sigue en pantalla (o casi): un solo gráfico más largo
        previo = next((y for y in reversed(fus) if y["palabra"] == x["palabra"] and y["posicion"] == x["posicion"] and x["inicio"] <= y["fin"] + 1.0), None)   # menos de 1 s de hueco: se une para que no parpadee
        if previo: previo["fin"] = max(previo["fin"], x["fin"])
        else: fus.append(x)
    items = fus
    for i, x in enumerate(items):
        for y in items[i + 1:]:
            if y["inicio"] < x["fin"] and y["posicion"] == x["posicion"]: avisos.append(f"«{x['palabra']}» y «{y['palabra']}» coinciden en {x['posicion']} entre {y['inicio']:.1f} y {min(x['fin'], y['fin']):.1f} s: cambia una de posición.")
        if plat in ("shorts", "tiktok", "reels", "youtube-shorts") and x["posicion"].startswith("bottom"): avisos.append(f"«{x['palabra']}» en {x['posicion']}: en {plat} esa zona la tapan los botones y el título de la app; usa top-* o center.")
    plan = {"video": video, "ancho": W, "alto": H, "graficos": items}; json.dump(plan, open(salida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("PLAN DE GRÁFICOS (el video no se ha tocado; Jeiler lo aprueba):")
    for x in items: print(f"  «{x['palabra']}» dicho en {x['oido_en']:.2f} s -> {x['tipo']} en {x['posicion']} de {x['inicio']:.2f} a {x['fin']:.2f} s")
    for av in avisos: print("  AVISO:", av)
    print(f"{len(items)} gráficos. Plan en {salida}")

def cmd_aplicar(a):
    if len(a) != 3: sys.exit(__doc__)
    video, plan_j, salida = a; plan = json.load(open(plan_j, encoding="utf-8")); W, H = plan["ancho"], plan["alto"]
    if pathlib.Path(salida).resolve() == pathlib.Path(video).resolve(): sys.exit("La salida no puede ser el video original.")
    if pathlib.Path(salida).exists(): sys.exit(f"{salida} ya existe: elige otro nombre (no se sobrescribe).")
    entradas = ["-i", video]; filtros = []; ult = "0:v"; k = 0; n_in = 0   # k numera los gráficos; n_in, las entradas de imagen (la 0 es el video)
    for g in plan["graficos"]:
        ini, fin = g["inicio"], g["fin"]; fade = min(0.25, (fin - ini) / 3)
        if g["png"]:
            w = int(g["tamano"] * W); entradas += ["-loop", "1", "-framerate", "30", "-t", f"{fin + 0.5:.3f}", "-i", g["png"]]; k += 1; n_in += 1
            filtros.append(f"[{n_in}:v]format=rgba,scale={w}:-1,fade=t=in:st={ini}:d={fade}:alpha=1,fade=t=out:st={fin - fade}:d={fade}:alpha=1[g{k}]")
            from_h = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", g["png"]], capture_output=True, text=True).stdout.strip().split("\n")[0].split(",")
            h = int(w * int(from_h[1]) / int(from_h[0])); x, y = zona(g["posicion"], W, H, w, h, 0.03)
            filtros.append(f"[{ult}][g{k}]overlay={x}:{y}:enable='between(t,{ini},{fin})'[v{k}]"); ult = f"v{k}"
        else:
            k += 1; tam = int(H * 0.07 * (g["tamano"] / 0.12) ** 0.5); texto = g["texto"].replace("\\", "\\\\").replace(":", "\\:").replace("'", "’")
            alfa = f"if(lt(t,{ini}),0,if(lt(t,{ini + fade}),(t-{ini})/{fade},if(lt(t,{fin - fade}),1,max(0,({fin}-t)/{fade}))))"
            m = int(0.03 * W); px = {"top-left": f"{m}", "bottom-left": f"{m}", "top-right": f"w-tw-{m}", "bottom-right": f"w-tw-{m}", "center": "(w-tw)/2"}[g["posicion"]]
            py = {"top-left": f"{m}", "top-right": f"{m}", "bottom-left": f"h-th-{m}", "bottom-right": f"h-th-{m}", "center": "(h-th)/2"}[g["posicion"]]
            filtros.append(f"[{ult}]drawtext=text='{texto}':fontsize={tam}:fontcolor={g['color'].replace('#', '0x')}:box=1:boxcolor=0x000000@0.55:boxborderw={tam // 4}:x={px}:y={py}:alpha='{alfa}':enable='between(t,{ini},{fin})'[v{k}]"); ult = f"v{k}"
    if not filtros: sys.exit("El plan no tiene gráficos.")
    cmd = ["ffmpeg", "-v", "error", "-nostdin", *entradas, "-filter_complex", ";".join(filtros), "-map", f"[{ult}]", "-map", "0:a?", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", salida]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: sys.exit("ffmpeg falló:\n" + r.stderr[-1200:])
    print(f"Listo: {salida} ({len(plan['graficos'])} gráficos; audio sin tocar)")

def cuadro(video, t, W, H):
    r = subprocess.run(["ffmpeg", "-v", "error", "-nostdin", "-ss", f"{t:.3f}", "-i", str(video), "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    return np.frombuffer(r.stdout, dtype=np.uint8).reshape(H, W, 3).astype(np.int16) if len(r.stdout) == W * H * 3 else None

def cmd_verificar(a):
    if len(a) != 3: sys.exit(__doc__)
    orig, final, plan_j = a; plan = json.load(open(plan_j, encoding="utf-8")); W, H = plan["ancho"], plan["alto"]; ok = True
    for g in plan["graficos"]:
        if g["png"]:
            w = int(g["tamano"] * W); fh = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=width,height", "-of", "csv=p=0", g["png"]], capture_output=True, text=True).stdout.strip().split("\n")[0].split(",")
            h = int(w * int(fh[1]) / int(fh[0])); x, y = zona(g["posicion"], W, H, w, h, 0.03)
        else:   # texto: se mide en una zona generosa de la esquina elegida
            w, h = int(0.4 * W), int(0.16 * H); x, y = zona(g["posicion"], W, H, w, h, 0.0)
        reg = (slice(y, y + h), slice(x, x + w)); medio = (g["inicio"] + g["fin"]) / 2
        def dif(t):   # % de píxeles de la zona que cambiaron (más de 25 niveles) respecto al video original
            f, o = cuadro(final, t, W, H), cuadro(orig, t, W, H)
            return None if f is None or o is None else float((np.abs(f[reg] - o[reg]).max(axis=2) > 25).mean() * 100)
        def libre(t):   # no medir en un momento donde otro gráfico del plan ocupa la misma esquina
            return not any(o is not g and o["posicion"] == g["posicion"] and o["inicio"] <= t <= o["fin"] for o in plan["graficos"])
        dentro = dif(medio)
        antes = dif(g["inicio"] - 0.6) if g["inicio"] > 0.7 and libre(g["inicio"] - 0.6) else None
        despues = dif(g["fin"] + 0.6) if libre(g["fin"] + 0.6) else None
        bien = dentro is not None and dentro > 0.3 and (antes is None or antes < 0.05) and (despues is None or despues < 0.05)
        ok &= bien
        f = lambda v: "—" if v is None else f"{v:.2f}%"
        print(f"  «{g['palabra']}» {g['inicio']:.1f}-{g['fin']:.1f} s: píxeles cambiados dentro {f(dentro)} | antes {f(antes)} | después {f(despues)}  {'OK' if bien else '<-- REVISAR'}")
    print("Se compara cada cuadro con el del video original en la zona del gráfico: dentro deben cambiar píxeles; antes y después, ninguno. Claude no ve el video en movimiento: mira también una hoja de cuadros.")
    sys.exit(0 if ok else 1)

if len(sys.argv) < 2 or sys.argv[1] not in ("plan", "aplicar", "verificar"): sys.exit(__doc__)
{"plan": cmd_plan, "aplicar": cmd_aplicar, "verificar": cmd_verificar}[sys.argv[1]](sys.argv[2:])
