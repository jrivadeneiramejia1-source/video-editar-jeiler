---
name: audio-limpio
description: Limpia el audio de una grabación hecha con teléfono o micrófono barato: quita el ruido de fondo con IA (sin internet), repara picos, deja un volumen parejo y une varias voces para que suenen igual de fuertes. Mide antes y después, porque Claude no puede oír. Usar cuando el usuario diga "quítale el ruido al audio", "se oye bajito", "tiene zumbido o ruido de fondo", "une estas voces", "iguala el volumen" o "limpia la voz" de un video o audio. No sirve para música ni para separar instrumentos.
---

# Audio limpio

Deja la **voz** de una grabación limpia y a buen volumen, y une varias voces para que suenen parejas. Todo corre en local (nada de la grabación sale de la sesión); internet solo hace falta una vez, para instalar los modelos.

## Reglas
- **Trabajar en copias.** El original nunca se modifica ni se borra. Los archivos de comunidades indígenas tampoco se suben a servicios externos.
- La voz de otra persona se procesa solo con su permiso.
- **Claude no puede oír.** Todo se mide (ruido, volumen, calidad estimada) y el informe lo dice; la última palabra es el oído de Jeiler.
- No pedir ni guardar claves (no se necesita ninguna).

## Instalar (una vez por sesión o computador)
Esta skill usa `ffmpeg-skill` (misma carpeta de skills): instalar el grupo `audio` o `editar-basico` con `./instalar.sh`.
```bash
bash scripts/instalar_modelos.sh      # ~520 MB desde github.com; crea ~/.cache/video-jeiler con su propio Python
PY=~/.cache/video-jeiler/venv/bin/python
```
Si ya está instalado por `subtitulos`, no se repite: comparten la carpeta.

## Proceso
1. **Medir el punto de partida:** `python3 ../ffmpeg-skill/scripts/probe.py VIDEO` y, si hace falta, `check.py VIDEO --platform youtube` (mide volumen y pico).
2. **Limpiar:**
   ```bash
   $PY scripts/limpiar_audio.py VIDEO_O_AUDIO voz_limpia.wav --lufs -14
   ```
   Sirve `-14` para YouTube, Shorts, Reels y TikTok; `-16` (por defecto) para voz sola o podcast. Deja `voz_limpia.wav` y `voz_limpia.informe.txt` (ruido en las pausas, distancia voz-ruido, calidad DNSMOS, volumen y pico).
3. **Volver a poner la voz en el video sin recodificar la imagen:**
   `python3 ../ffmpeg-skill/scripts/audio.py VIDEO --replace voz_limpia.wav -o video_limpio.mp4`
4. **Varias voces:**
   - Una después de otra (entrevista, respuestas grabadas por separado): `$PY scripts/mezclar_voces.py salida.wav voz1.wav voz2.wav --pausa 0.4`
   - A la vez (coro, doblaje): `... --modo juntas`
   Primero llevan cada voz al mismo volumen. Si una voz es muy baja, **su ruido sube con ella**: limpiarla antes.
5. **Música debajo de la voz:** `audio.py VIDEO --music pista.mp3 --duck` (de `ffmpeg-skill`); la música baja sola cuando se habla.
6. **Comprobar:** `python3 ../ffmpeg-skill/scripts/check.py VIDEO_FINAL --platform youtube --content` (volumen, pico, silencios, cortes de audio).

## Lo que se midió y hay que saber
- **La IA deja las pausas en silencio digital.** Suena «muerto» y `check.py` lo marca como cortes de audio (`dropouts`). Por eso `limpiar_audio.py` mezcla por defecto un murmullo de fondo muy suave (-62 dBFS); `--sin-ambiente` lo quita.
- **`--sin-ia` casi no mejora** con ruido fuerte (en la prueba, el ruido según DNSMOS empeoró). Es solo para cuando no hay modelos.
- **La IA puede bajar un poco el reconocimiento de voz** (en la prueba 96,5 % de palabras bien con el audio original contra 93 % con el limpio). Por eso los **subtítulos se transcriben del audio original**, no del limpio.
- **Quitar silencios funciona mejor después de limpiar:** con el ruido original (-41 dBFS) `silence.py` no encontró ninguna pausa; con la voz limpia encontró las 3 pausas largas (de 1 s o más).
- El volumen final queda cerca del pedido, no exacto (pidiendo -14 salió -15,3 LUFS): `loudnorm` sin deformar la voz no siempre llega.
- Sin compresor a propósito: sube el ruido de fondo.

## Señales de alerta
- Una voz que «suena a robot» o con burbujas: bajar la fuerza o dejar el original; avisar a Jeiler.
- Pausas con cortes bruscos: revisar el murmullo de fondo.
- Prometer calidad sin medir, o sin decir que no se pudo escuchar.
- Procesar la voz de alguien sin su permiso.

## Verificación
- [ ] El original sigue intacto y se trabajó en una copia.
- [ ] El informe muestra ruido, volumen y pico antes y después.
- [ ] `check.py --content` sin FAIL (los WARN se explican).
- [ ] Se dijo que no se pudo escuchar el resultado.

## Qué se probó (2026-11-04)
Con una grabación de prueba **inventada** (narración sintética de 47 s con ruido rosa, zumbido de 60 Hz y volumen bajo, como un teléfono): ruido medido -41 dBFS → -67 (con murmullo; -90 sin él), calidad DNSMOS de ruido 1,96 → 4,03, volumen -37 → -15 LUFS; la unión de dos voces de -46 y -13 LUFS las dejó en -16,1 y -16,0. **No se probó con una grabación real de teléfono, con voces de personas, con música ni en otros idiomas.** Licencias: DPDFNet (Apache-2.0), sherpa-onnx (Apache-2.0), DNSMOS de Microsoft (CC-BY-4.0).
