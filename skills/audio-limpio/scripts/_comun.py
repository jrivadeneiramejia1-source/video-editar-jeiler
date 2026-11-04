"""Funciones comunes de audio-limpio: ffmpeg, lectura de wav, medidas y carpeta de modelos."""
import json, os, pathlib, re, subprocess, wave
import numpy as np

BASE = pathlib.Path(os.environ.get("VIDEO_JEILER_MODELOS", pathlib.Path.home() / ".cache" / "video-jeiler"))
MODELOS = BASE / "modelos"

def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *map(str, args)], check=True)

def leer_wav(ruta):
    w = wave.open(str(ruta))
    x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return x, w.getframerate()

def escribir_wav(ruta, x, sr):
    w = wave.open(str(ruta), "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()

def nivel_pausas(x, sr):
    """Nivel (dBFS) del 10 % de ventanas de 50 ms más silenciosas = ruido de fondo. Más negativo = más limpio."""
    n = int(0.05 * sr); v = x[:len(x) // n * n].reshape(-1, n)
    e = 20 * np.log10(np.sqrt((v ** 2).mean(1)) + 1e-9)
    # Se corta en -90 dBFS: por debajo es silencio total (la IA deja las pausas en silencio digital).
    return max(float(np.percentile(e, 10)), -90.0), float(np.percentile(e, 90))

def volumen(ruta):
    """(LUFS integrado, pico real dBFS) con ebur128."""
    e = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-nostdin", "-i", str(ruta), "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", e); p = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", e)
    return (float(i[-1]) if i else None), (float(p[-1]) if p else None)

def loudnorm_dos_pasadas(entrada, salida, lufs=-16.0, tp=-1.5, pre=""):
    """Volumen estándar en dos pasadas (linear=true: no deforma la voz). `pre` = filtros previos."""
    ant = (pre + ",") if pre else ""
    p1 = subprocess.run(["ffmpeg", "-v", "info", "-nostdin", "-i", str(entrada), "-ar", "48000", "-af",
                         f"{ant}loudnorm=I={lufs}:TP={tp}:LRA=7:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(re.search(r'\{[^{}]*"input_i"[^{}]*\}', p1, re.S).group(0))
    ln = (f"loudnorm=I={lufs}:TP={tp}:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
          f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    ffmpeg("-i", entrada, "-ar", 48000, "-ac", 1, "-af", ant + ln, "-c:a", "pcm_s16le", salida)

def dnsmos(ruta):
    """Calidad de la voz sin escucharla (modelo DNSMOS de Microsoft): (voz, ruido, global), de 1 a 5. None si falta el modelo."""
    modelo = MODELOS / "sig_bak_ovr.onnx"
    if not modelo.exists():
        return None
    import onnxruntime as ort, tempfile
    sess = ort.InferenceSession(str(modelo), providers=["CPUExecutionProvider"])
    p_ovr = np.poly1d([-0.06766283, 1.11546468, 0.04602535]); p_sig = np.poly1d([-0.08397278, 1.22083953, 0.0052439]); p_bak = np.poly1d([-0.13166888, 1.60915514, -0.39604546])
    tmp = pathlib.Path(tempfile.mkdtemp()) / "d16.wav"
    ffmpeg("-i", ruta, "-vn", "-ar", 16000, "-ac", 1, "-c:a", "pcm_s16le", tmp)
    x, _ = leer_wav(tmp); L = int(9.01 * 16000)
    while len(x) < L:
        x = np.concatenate([x, x])
    S = []; B = []; O = []
    for i in range(max(int(np.floor(len(x) / 16000 - 9.01)) + 1, 1)):
        seg = x[i * 16000:i * 16000 + L]
        if len(seg) < L:
            break
        o = sess.run(None, {"input_1": seg[None, :].astype(np.float32)})[0][0]
        S.append(p_sig(o[0])); B.append(p_bak(o[1])); O.append(p_ovr(o[2]))
    return float(np.mean(S)), float(np.mean(B)), float(np.mean(O))
