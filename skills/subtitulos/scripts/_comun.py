"""Funciones comunes de subtitulos: ffmpeg, texto normalizado, SRT y reconocimiento de voz con tiempo por palabra."""
import os, pathlib, re, subprocess, tempfile, unicodedata, wave
import numpy as np

BASE = pathlib.Path(os.environ.get("VIDEO_JEILER_MODELOS", pathlib.Path.home() / ".cache" / "video-jeiler"))
MODELOS = BASE / "modelos"

def ffmpeg(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-nostdin", *map(str, args)], check=True)

def audio_16k(ruta):
    """Extrae el primer audio como mono 16 kHz (float32) para el reconocedor."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="subtitulos-")) / "a16.wav"
    ffmpeg("-i", ruta, "-vn", "-ar", 16000, "-ac", 1, "-c:a", "pcm_s16le", tmp)
    w = wave.open(str(tmp)); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    tmp.unlink(); tmp.parent.rmdir()
    return x

_NUM = dict(zip(map(str, range(21)), "cero uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince dieciseis diecisiete dieciocho diecinueve veinte".split()))

def norm(t):
    """Texto en minúscula, sin tildes (la ñ se conserva) y sin signos: lista de palabras. Los números del 0 al 20 se escriben con letras (3 = tres)."""
    t = unicodedata.normalize("NFD", t.lower().replace("ñ", "\u0001"))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn").replace("\u0001", "ñ")
    return [_NUM.get(p, p) for p in re.findall(r"[a-zñ0-9]+", t)]

def tiempo_srt(s, punto=","):
    s = max(s, 0.0); h = int(s // 3600); m = int(s % 3600 // 60); sec = s % 60
    return f"{h:02d}:{m:02d}:{int(sec):02d}{punto}{int(round((sec - int(sec)) * 1000)):03d}".replace("1000", "999")

def leer_srt(ruta):
    """SRT -> lista de {a, b, lines}."""
    cues = []
    for bloque in re.split(r"\n\s*\n", pathlib.Path(ruta).read_text(encoding="utf-8").strip().replace("\r", "")):
        l = bloque.split("\n")
        m = re.search(r"(\d+):(\d+):(\d+)[,.](\d+)\s*-->\s*(\d+):(\d+):(\d+)[,.](\d+)", bloque)
        if not m: continue
        g = [int(x) for x in m.groups()]
        a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000; b = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        txt = [x for x in l[l.index(next(z for z in l if "-->" in z)) + 1:] if x.strip()]
        cues.append({"a": a, "b": b, "lines": txt})
    return cues

def _vad_trozos(x16, sr, maximo=25.0):
    """Corta el audio en trozos de hasta ~25 s SIEMPRE en una pausa. Así el reconocedor no se pierde ni se salta frases."""
    import sherpa_onnx
    cfg = sherpa_onnx.VadModelConfig(); cfg.silero_vad.model = str(MODELOS / "silero_vad.onnx"); cfg.silero_vad.min_silence_duration = 0.3
    cfg.silero_vad.min_speech_duration = 0.15; cfg.silero_vad.threshold = 0.4; cfg.sample_rate = sr
    vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=60); ws = cfg.silero_vad.window_size; segs = []
    def sacar():
        while not vad.empty():
            s = vad.front; segs.append((s.start / sr, (s.start + len(s.samples)) / sr)); vad.pop()
    for i in range(0, len(x16) - ws + 1, ws):
        vad.accept_waveform(x16[i:i + ws]); sacar()
    vad.flush(); sacar()
    trozos = []; ini = fin = None
    for a, b in segs:
        if ini is None: ini, fin = a, b
        elif b - ini <= maximo: fin = b
        else: trozos.append((ini, fin)); ini, fin = a, b
    if ini is not None: trozos.append((ini, fin))
    return [(max(0.0, a - 0.2), min(len(x16) / sr, b + 0.2)) for a, b in trozos]

_REC = None
def palabras(x16, sr=16000):
    """Voz -> [{w: palabra, a: segundo en que EMPIEZA, l: segundo de su último trozo}] (Parakeet TDT v3 int8; español y otros 24 idiomas europeos)."""
    global _REC
    import sherpa_onnx
    d = MODELOS / "sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8"
    if not d.exists(): raise SystemExit("Faltan los modelos. Corre primero: bash instalar_modelos.sh")
    if _REC is None:
        _REC = sherpa_onnx.OfflineRecognizer.from_transducer(encoder=str(d / "encoder.int8.onnx"), decoder=str(d / "decoder.int8.onnx"), joiner=str(d / "joiner.int8.onnx"),
                                                              tokens=str(d / "tokens.txt"), num_threads=4, model_type="nemo_transducer")
    toks = []
    for a, b in _vad_trozos(x16, sr):
        s = _REC.create_stream(); s.accept_waveform(sr, x16[int(a * sr):int(b * sr)]); _REC.decode_stream(s)
        toks += [(t, ts + a) for t, ts in zip(s.result.tokens, s.result.timestamps)]
    W = []; cur = None
    for tok, t in toks:   # una palabra nueva empieza con espacio
        if tok.startswith(" ") or cur is None:
            if cur: W.append(cur)
            cur = {"w": tok.strip(), "a": round(t, 2), "l": round(t, 2)}
        else:
            cur["w"] += tok; cur["l"] = round(t, 2)
    if cur: W.append(cur)
    return W
