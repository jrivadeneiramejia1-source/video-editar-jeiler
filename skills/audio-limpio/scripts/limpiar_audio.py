#!/usr/bin/env python3
"""Limpia la voz de una grabación: repara picos recortados, quita el ruido de fondo con IA (DPDFNet), filtra graves y deja el volumen estándar.

Uso:  python limpiar_audio.py ENTRADA SALIDA.wav [--recorte SEGUNDOS] [--lufs -16] [--ambiente -62 | --sin-ambiente] [--sin-ia]
  ENTRADA   audio o video (se usa su primer audio). Nunca se modifica.
  SALIDA    .wav mono de 48 kHz. Junto a él queda SALIDA.informe.txt con las medidas.
  --recorte quita esos segundos del inicio (por defecto 0).
  --lufs    volumen final (por defecto -16; para YouTube, Shorts, Reels o TikTok conviene -14).
  --ambiente DB  la IA deja las pausas en silencio digital (suena «muerto» y algunos revisores lo marcan como corte de audio):
            se mezcla un murmullo de fondo muy suave a ese nivel (por defecto -62 dBFS). --sin-ambiente lo desactiva.
  --sin-ia  usa el filtro de ffmpeg (afftdn) en vez de la IA: no necesita modelos, pero con ruido fuerte casi no mejora
            (en la prueba el ruido medido por DNSMOS incluso empeoró). Úsalo solo si no hay modelos.
NO usa compresor (sube el ruido de fondo). Orden: reparar picos -> quitar ruido -> graves -> volumen estándar (dos pasadas).
Con modelos: usar el Python de la instalación (~/.cache/video-jeiler/venv/bin/python)."""
import pathlib, sys, tempfile
import numpy as np
from _comun import MODELOS, dnsmos, escribir_wav, ffmpeg, leer_wav, loudnorm_dos_pasadas, nivel_pausas, volumen

def main():
    a = sys.argv[1:]; rec = 0.0; lufs = -16.0; sin_ia = False; amb = -62.0
    if "--recorte" in a: i = a.index("--recorte"); rec = float(a[i + 1]); del a[i:i + 2]
    if "--lufs" in a: i = a.index("--lufs"); lufs = float(a[i + 1]); del a[i:i + 2]
    if "--ambiente" in a: i = a.index("--ambiente"); amb = float(a[i + 1]); del a[i:i + 2]
    if "--sin-ambiente" in a: a.remove("--sin-ambiente"); amb = None
    if "--sin-ia" in a: a.remove("--sin-ia"); sin_ia = True
    if len(a) != 2: sys.exit(__doc__)
    src, dst = pathlib.Path(a[0]), pathlib.Path(a[1])
    if not src.exists(): sys.exit(f"No existe {src}")
    if src.resolve() == dst.resolve(): sys.exit("La salida no puede ser el mismo archivo que la entrada.")
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="audio-limpio-"))
    o48, o16, den = tmp / "o48.wav", tmp / "o16.wav", tmp / "den.wav"
    ffmpeg("-i", src, "-vn", "-ar", 48000, "-ac", 1, "-af", "adeclip", "-c:a", "pcm_s16le", o48)   # adeclip repara picos recortados
    if sin_ia:
        metodo = "filtro de ffmpeg (afftdn), sin IA"
        ffmpeg("-i", o48, "-ar", 16000, "-ac", 1, "-af", "afftdn=nf=-30:tn=1", "-c:a", "pcm_s16le", den)
    else:
        modelo = MODELOS / "dpdfnet_baseline.onnx"
        if not modelo.exists(): sys.exit("Faltan los modelos. Corre primero: bash instalar_modelos.sh  (o usa --sin-ia)")
        import sherpa_onnx
        metodo = "IA DPDFNet (sherpa-onnx)"
        ffmpeg("-i", o48, "-ar", 16000, "-ac", 1, "-c:a", "pcm_s16le", o16)
        x16, _ = leer_wav(o16)
        cfg = sherpa_onnx.OfflineSpeechDenoiserConfig(model=sherpa_onnx.OfflineSpeechDenoiserModelConfig(
            dpdfnet=sherpa_onnx.OfflineSpeechDenoiserDpdfNetModelConfig(model=str(modelo)), num_threads=4))
        r = sherpa_onnx.OfflineSpeechDenoiser(cfg)(x16, 16000)
        escribir_wav(den, np.array(r.samples, dtype=np.float32), r.sample_rate)
    pre = "highpass=f=70" + (f",atrim=start={rec},asetpts=PTS-STARTPTS" if rec else "") + ",afade=t=in:st=0:d=0.03"
    loudnorm_dos_pasadas(den, dst, lufs=lufs, tp=-1.5, pre=pre)
    if amb is not None and not sin_ia:   # murmullo de fondo para que las pausas no queden en silencio digital
        mezcla = tmp / "mezcla.wav"
        ffmpeg("-i", dst, "-f", "lavfi", "-i", f"anoisesrc=color=pink:amplitude={10 ** (amb / 20) * 3:.6f}:sample_rate=48000", "-filter_complex",
               "[0:a][1:a]amix=inputs=2:duration=first:normalize=0", "-ar", 48000, "-ac", 1, "-c:a", "pcm_s16le", mezcla)
        mezcla.replace(dst)
    xo, so = leer_wav(o48); xf, sf = leer_wav(dst)
    (ro, vo), (rf, vf) = nivel_pausas(xo, so), nivel_pausas(xf, sf)
    L = [f"Método: {metodo}" + (f" + murmullo de fondo a {amb:.0f} dBFS" if amb is not None and not sin_ia else ""),
         f"Duración: original {len(xo) / so:.2f} s | limpia {len(xf) / sf:.2f} s (recorte {rec:.2f} s)",
         f"Ruido en las pausas (más negativo = más limpio; -90 = silencio total): original {ro:.1f} dBFS -> limpia {rf:.1f} dBFS",
         f"Distancia voz-ruido (voz fuerte menos ruido): original {vo - ro:.1f} dB -> limpia {vf - rf:.1f} dB"]
    for nom, p in (("original", o48), ("limpia", dst)):
        s = dnsmos(p)
        if s: L.append(f"Calidad DNSMOS {nom}: voz {s[0]:.2f} | ruido {s[1]:.2f} | global {s[2]:.2f} (1 a 5, más alto = mejor)")
    li, pk = volumen(dst); L.append(f"Volumen final: {li} LUFS | pico real {pk} dBFS")
    dst.with_suffix(".informe.txt").write_text("\n".join(L), encoding="utf-8"); print("\n".join(L))
    for f in tmp.iterdir(): f.unlink()
    tmp.rmdir()

if __name__ == "__main__":
    main()
