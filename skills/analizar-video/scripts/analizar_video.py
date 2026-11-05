#!/usr/bin/env python3
"""Arma un «paquete de evidencia» de un video para entenderlo sin verlo entero: datos técnicos, cambios de escena,
picos de sonido, una hoja de cuadros y (si hay voz y modelos) la transcripción con tiempos.
Uso:  python analizar_video.py VIDEO CARPETA_SALIDA [--sin-voz] [--cuadros 4x3]
Deja en CARPETA_SALIDA:  resumen.md  |  hoja.png (cuadros con su minutaje)  |  palabras.json (si se transcribió)
Usa ffmpeg-skill (y subtitulos para la voz) instaladas como skills vecinas. Para la voz usar el Python de la instalación
(~/.cache/video-jeiler/venv/bin/python); sin él, el resto funciona con python3 y se omite la transcripción.
Nunca modifica el video. Claude no ve el movimiento ni oye el audio: esto da datos y cuadros, no una opinión."""
import json, pathlib, subprocess, sys

a = sys.argv[1:]; voz = "--sin-voz" not in a; a = [x for x in a if x != "--sin-voz"]; cuadros = "4x3"
if "--cuadros" in a: i = a.index("--cuadros"); cuadros = a[i + 1]; del a[i:i + 2]
if len(a) != 2: sys.exit(__doc__)
video, out = pathlib.Path(a[0]), pathlib.Path(a[1])
if not video.exists(): sys.exit(f"No existe {video}")
out.mkdir(parents=True, exist_ok=True)
FF = pathlib.Path(__file__).resolve().parents[2] / "ffmpeg-skill" / "scripts"
SUB = pathlib.Path(__file__).resolve().parents[2] / "subtitulos" / "scripts"
if not FF.exists(): sys.exit("Falta ffmpeg-skill. Instala el grupo analizar.")
def js(*cmd):
    r = subprocess.run([sys.executable, *map(str, cmd), "--json-brief"], capture_output=True, text=True)
    try: return json.loads(r.stdout[r.stdout.index("{"):])
    except Exception: return {"error": (r.stdout + r.stderr)[-300:]}
pr = js(FF / "probe.py", video); es = js(FF / "scenes.py", video, "--audio-peaks")
hoja = js(FF / "look.py", video, "--tiles", cuadros, "-o", out / "hoja.png", "--overwrite")
L = [f"# Análisis de {video.name}", "", "## Datos técnicos"]
v = pr.get("video") or {}; au = pr.get("audio") or {}
L += [f"- Duración: {pr.get('duration')} s | tamaño del archivo: {pr.get('size_bytes')} bytes",
      f"- Imagen: {v.get('width')}x{v.get('height')} a {v.get('fps')} fps, códec {v.get('codec')}",
      f"- Audio: {au.get('codec')} {au.get('channels')} canal(es) a {au.get('sample_rate')} Hz" if au else "- Audio: no tiene"]
L += ["", f"## Escenas ({es.get('scene_count', '?')})"]
for s in es.get("scenes", [])[:40]: L.append(f"- {s['start']:.1f} a {s['end']:.1f} s ({s['duration']:.1f} s)")
if es.get("audio_peaks"): L += ["", "## Momentos de más volumen (s): " + ", ".join(f"{p['time']:.1f}" for p in es["audio_peaks"][:12])]
L += ["", "## Cuadros", "Ver `hoja.png` (cada cuadro lleva su minutaje)."]
texto = None
if voz and au:
    try:
        import importlib.util
        sp = importlib.util.spec_from_file_location("sub", SUB / "_comun.py"); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
        W = m.palabras(m.audio_16k(str(video))); json.dump(W, open(out / "palabras.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        L += ["", "## Transcripción (el reconocedor se equivoca: revisarla)"]; fila = []; t0 = None
        for w in W:
            if t0 is None: t0 = w["a"]
            fila.append(w["w"])
            if w["w"][-1:] in ".?!" or len(fila) >= 25: L.append(f"- [{int(t0 // 60)}:{t0 % 60:04.1f}] " + " ".join(fila)); fila = []; t0 = None
        if fila: L.append(f"- [{int(t0 // 60)}:{t0 % 60:04.1f}] " + " ".join(fila))
    except BaseException as e:
        L += ["", f"## Transcripción omitida ({type(e).__name__}): faltan los modelos o el Python de la instalación. Usa `--sin-voz` o instala `subtitulos`."]
(out / "resumen.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L)[:1800]); print(f"\nPaquete en {out}/ (resumen.md, hoja.png" + (", palabras.json)" if (out / 'palabras.json').exists() else ")"))
