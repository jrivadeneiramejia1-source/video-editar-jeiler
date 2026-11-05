---
name: analizar-video
description: >-
  Entiende un video sin verlo entero: arma un paquete de evidencia con datos técnicos, cambios de escena, momentos de más volumen, una hoja de cuadros con minutaje y la transcripción con tiempos. Usar cuando el usuario diga "mira este video y dime de qué trata", "analiza este video", "qué pasa en este video", "revisa cómo está hecho este video" o antes de estudiar un video de referencia. No opina de calidad artística: da datos y cuadros.
---

# Analizar un video

Un solo comando deja una carpeta con `resumen.md`, `hoja.png` y, si hay voz, `palabras.json`. Sirve para entender un video propio o uno de referencia (por ejemplo, para copiar su **estilo**, nunca su contenido).

## Reglas
- Nunca se modifica el video. Videos de otras personas: solo estudiar su estilo; respetar derechos y términos de la plataforma. Archivos de comunidades indígenas: no se suben a servicios externos (todo corre en local).
- Claude **no ve el movimiento ni oye el audio**: la hoja de cuadros y los datos son la evidencia; decirlo.
- La transcripción se equivoca: revisarla antes de citarla.

## Proceso
1. `$PY scripts/analizar_video.py VIDEO carpeta_analisis` (con `--sin-voz` para omitir la transcripción; `--cuadros 5x4` para más cuadros). `PY=~/.cache/video-jeiler/venv/bin/python` si se quiere la voz; sin ese Python se omite la transcripción y lo demás funciona.
2. Abrir `hoja.png` (cuadros con minutaje) y leer `resumen.md`.
3. Responder con lo que se ve y se mide: duración, formato, ritmo (escenas por minuto), de qué habla, qué muestra en cada parte, y **qué no se pudo saber** (música, movimiento, tono de voz, sensaciones).
4. Si es una referencia de estilo, anotar: paleta de colores de los cuadros, tipografía, ritmo, tipo de plano y duración de cada parte (la skill `estudiar-video-referencia` de `video-crear-jeiler` usa este paquete).

## Señales de alerta
- Afirmar cosas del audio o del movimiento que no se midieron.
- Copiar el guion o los planos de un video ajeno.

## Verificación
- [ ] El video original no se tocó.
- [ ] Se miró la hoja de cuadros.
- [ ] Se dijo qué no se pudo saber.

## Qué se probó (2026-11-04)
Con el video de prueba **inventado** «Gemini contra ChatGPT» (23 s): salió el resumen con duración, formato, una escena, cuatro picos de volumen, la hoja de cuadros y la transcripción de las 6 frases con su minutaje. **No se probó con un video real con muchos cortes, con música ni con un video de otra persona.** Alternativa de terceros: el plugin `watch-video` del directorio de plugins (no instalado desde aquí).
