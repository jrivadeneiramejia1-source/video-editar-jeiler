#!/usr/bin/env python3
"""Une varias voces (de distintas personas, micrófonos o volúmenes) para que suenen parejas.
Uso:  python mezclar_voces.py SALIDA.wav ENTRADA1 ENTRADA2 [ENTRADA3 ...] [--modo seguidas|juntas] [--pausa 0.4] [--lufs -16]
  seguidas (por defecto)  una después de otra, con --pausa segundos entre ellas (entrevista, respuestas grabadas por separado).
  juntas                  todas a la vez, superpuestas (coro, doblaje, dos personas hablando a la vez).
Cada entrada se lleva primero al mismo volumen (dos pasadas, sin compresor). En «juntas» se vuelve a ajustar el volumen del resultado.
Las entradas nunca se modifican. Para limpiar el ruido de cada voz, usar antes limpiar_audio.py."""
import pathlib, sys, tempfile
from _comun import ffmpeg, loudnorm_dos_pasadas, volumen

a = sys.argv[1:]; modo = "seguidas"; pausa = 0.4; lufs = -16.0
if "--modo" in a: i = a.index("--modo"); modo = a[i + 1]; del a[i:i + 2]
if "--pausa" in a: i = a.index("--pausa"); pausa = float(a[i + 1]); del a[i:i + 2]
if "--lufs" in a: i = a.index("--lufs"); lufs = float(a[i + 1]); del a[i:i + 2]
if len(a) < 3 or modo not in ("seguidas", "juntas"): sys.exit(__doc__)
dst, entradas = pathlib.Path(a[0]), [pathlib.Path(x) for x in a[1:]]
for e in entradas:
    if not e.exists(): sys.exit(f"No existe {e}")
    if e.resolve() == dst.resolve(): sys.exit("La salida no puede ser una de las entradas.")
tmp = pathlib.Path(tempfile.mkdtemp(prefix="mezclar-voces-"))
norm = []
for n, e in enumerate(entradas):
    o = tmp / f"n{n}.wav"; loudnorm_dos_pasadas(e, o, lufs=lufs, tp=-1.5, pre="adeclip"); norm.append(o)
    print(f"entrada {n + 1}: {volumen(e)[0]} LUFS -> {volumen(o)[0]} LUFS ({e.name})")
if modo == "seguidas":
    ins = []; fil = []
    for n, o in enumerate(norm): ins += ["-i", o]
    partes = []
    for n in range(len(norm)):
        fil.append(f"[{n}:a]aresample=48000,apad=pad_dur={pausa if n < len(norm) - 1 else 0}[s{n}]"); partes.append(f"[s{n}]")
    fil.append("".join(partes) + f"concat=n={len(norm)}:v=0:a=1[o]")
    ffmpeg(*ins, "-filter_complex", ";".join(fil), "-map", "[o]", "-ar", 48000, "-ac", 1, "-c:a", "pcm_s16le", dst)
else:
    ins = []
    for o in norm: ins += ["-i", o]
    mezcla = tmp / "mezcla.wav"
    ffmpeg(*ins, "-filter_complex", f"amix=inputs={len(norm)}:duration=longest:normalize=0", "-ar", 48000, "-ac", 1, "-c:a", "pcm_s16le", mezcla)
    loudnorm_dos_pasadas(mezcla, dst, lufs=lufs, tp=-1.5)
li, pk = volumen(dst); print(f"Resultado ({modo}): {dst} | {li} LUFS | pico real {pk} dBFS")
for f in tmp.iterdir(): f.unlink()
tmp.rmdir()
