---
name: subtitulos
description: >-
  Crea subtítulos sincronizados para un video o audio en español: transcribe con el tiempo de cada palabra (sin internet), alinea un guion ya escrito o arma los subtítulos solos, genera .srt y .vtt, los quema en el video (con estilos, animados o palabra por palabra) y comprueba después que no estén corridos ni mal escritos. Usar cuando el usuario diga "ponle subtítulos", "subtitula este video", "transcribe el audio", "sácame el .srt" o "revisa que los subtítulos estén bien". No cubre wayuunaiki ni idiomas fuera de los europeos.
---

# Subtítulos

Transcribe la voz con el segundo de cada palabra y deja subtítulos que aparecen cuando se dice cada frase. Corre en local; internet solo para instalar los modelos.

## Reglas
- **Subtítulos = lo que se dice** (con el guion como referencia). Si alguien leyó distinto al guion, el subtítulo dice lo que dijo y se avisa a Jeiler.
- **Revisar el texto antes de quemar.** El reconocedor se equivoca (en la prueba: «limón» como «limo», «tres» como «3»). Mostrar a Jeiler los errores que se vean.
- Trabajar en copias; originales intactos. Audios de comunidades indígenas: no se suben a ningún servicio.
- **Transcribir del audio original**, no del limpiado con IA (reconoce mejor; ver `audio-limpio`).
- Idiomas: el modelo cubre español y otros 24 idiomas europeos. **Wayuunaiki y otras lenguas indígenas no**: ahí los subtítulos los escribe y revisa un hablante.
- Claude no oye ni ve el video en movimiento: mide y mira cuadros.

Usa `ffmpeg-skill` para quemar los subtítulos: instalar el grupo `subtitulos` o `editar-basico`.

## Instalar (una vez)
```bash
bash scripts/instalar_modelos.sh
PY=~/.cache/video-jeiler/venv/bin/python
```

## Proceso
1. **Transcribir (del original):** `$PY scripts/transcribir.py VIDEO palabras.json` (imprime el texto para leerlo).
2. **Partir en subtítulos**
   - **Con guion:** escribir `cues.txt` (un subtítulo por línea, texto exacto, `|` para partir en dos renglones) y `$PY scripts/alinear_guion.py cues.txt palabras.json cues.json`. Mirar la tabla: si dice REVISAR, ajustar a mano.
   - **Sin guion:** va directo al paso 3 con `--palabras` (corta en pausas y signos; máximo 2 renglones de 42 letras).
3. **Escribir .srt y .vtt:** `$PY scripts/a_srt.py --cues cues.json salida` o `$PY scripts/a_srt.py --palabras palabras.json salida`. El `.srt` se puede subir tal cual a YouTube como pista aparte.
4. **Quemarlos en el video** con `ffmpeg-skill`: `python3 ../ffmpeg-skill/scripts/caption.py VIDEO --srt salida.srt --platform youtube -o final.mp4` (estilo, posición y zona segura para vertical con `--platform tiktok|reels|shorts`; `--animate pop` o `--karaoke` para palabra por palabra).
5. **Verificar el resultado** (otra vez, desde el video final):
   `$PY scripts/verificar_subtitulos.py final.mp4 salida.srt`
   Mide: cada subtítulo sale hasta 0,45 s antes o 0,3 s después de su primera palabra, y el texto coincide con la voz re-transcrita más del 93 %. Sale con código 1 si falla.
6. **Mirar cuadros** del video con subtítulos: `python3 ../ffmpeg-skill/scripts/look.py final.mp4 --tiles 3x2` y revisar que se lean y no tapen nada.

## Señales de alerta
- Subtítulos con texto «arreglado» que ya no coincide con lo dicho.
- Quemar sin haber leído el texto.
- Tiempos corridos más de medio segundo: casi siempre hay un recorte de audio no contado.
- Subtítulos que tapan la cara, un logo o la zona de botones de TikTok o Shorts.

## Verificación
- [ ] `verificar_subtitulos.py` pasó (o se explicó cada falla).
- [ ] Se leyó el texto completo contra el guion o el audio.
- [ ] Se miraron cuadros con subtítulos a tamaño completo.
- [ ] Se dijo que no se pudo oír el audio ni ver el video en movimiento.

## Qué se probó (2026-11-04)
Con la grabación de prueba **inventada** (10 frases, 115 palabras): el reconocedor acertó 111 palabras con ruido (96,5 %) y 113 con la voz limpia de origen (98,3 %); con el audio limpiado con IA bajó a 93 %. La alineación con guion puso el inicio de las 10 frases a menos de 0,3 s de la verdad (media 0,17 s; el reconocedor marca las palabras ~0,2 s antes). La verificación dejó pasar el archivo correcto, aceptó un corrimiento de +0,25 s y rechazó uno de +1,5 s y otro de -0,6 s. Quemado con `caption.py` y revisado en cuadros. **No se probó con una voz real, con acentos, con varias personas hablando, con música de fondo ni en idiomas distintos del español.** Modelos: Parakeet TDT v3 de NVIDIA (su ficha en Hugging Face indica CC-BY-4.0; verificar), sherpa-onnx (Apache-2.0), Silero VAD (MIT).
