---
name: verificar-video
description: Puerta de calidad antes de entregar o publicar un video: mide formato, volumen, picos, cuadros negros o congelados, silencios y cortes de audio, mira cuadros a tamaño completo, comprueba subtítulos y repasa lo que una máquina no mide (caras, manos y pelo raros en 3D o IA, derechos de música e imágenes, logos, etiqueta de IA y contenido para niños). Usar cuando el usuario diga "revisa el video", "está listo para subir", "verifica que se vea y se oiga bien" o antes de publicar en YouTube, TikTok, Reels o WhatsApp.
---

# Verificar un video

Nada se da por entregado sin evidencia: un comando corrido, un cuadro mirado, una medida. Y se dice siempre qué **no** se pudo comprobar (Claude no oye el audio ni ve el movimiento).

Usa `ffmpeg-skill` (instalar el grupo `verificar` o `editar-basico`).

## Reglas
- No cambiar el video mientras se verifica: primero el informe; los arreglos, uno por vez y con permiso de Jeiler.
- Datos de personas reales (voz, cara, nombre): solo con su permiso. Los archivos de comunidades indígenas no se tocan.
- Nada se publica solo: Jeiler sube.

## Proceso
1. **Medir** (con `ffmpeg-skill`):
   `python3 ../ffmpeg-skill/scripts/check.py VIDEO --platform youtube --content` (cambiar la plataforma: `shorts`, `reels`, `tiktok`, `podcast`...). Revisa duración, formato, fotogramas por segundo, tamaño, volumen, pico, cuadros negros, imagen congelada, destellos, silencios y cortes de audio. Cada FAIL trae el comando que lo arregla.
2. **Mirar cuadros a tamaño completo:** `python3 ../ffmpeg-skill/scripts/look.py VIDEO --tiles 3x2` y abrir la imagen. Revisar texto legible, nada cortado, nada tapando caras ni logos.
3. **Subtítulos** (si hay): `verificar_subtitulos.py` de la skill `subtitulos`.
4. **Audio con ruido:** si el informe muestra ruido o volumen bajo, usar `audio-limpio` y repetir el paso 1.
5. **Lo que una máquina no mide** (revisar a mano y anotar):
   - **3D o clips de IA:** caras simétricas, ojos y dientes bien, **pelo completo**, manos con cinco dedos, nada flotando ni cambiando de forma entre tomas. Mirar fijas de varias tomas.
   - **Música, imágenes, voces y logos:** de dónde viene cada una y su licencia; los logos solo para nombrar o comparar, nunca para aparentar apoyo de la marca; guardar los créditos.
   - **Etiqueta de IA:** si hay IA fotorrealista, cara o voz sintética, declararlo en la plataforma; aun en animación, poner en los créditos o la descripción que se hizo con apoyo de IA. Verificar la regla vigente de cada plataforma.
   - **Para niños:** nada que asuste, ritmo calmado, un adulto lo revisó; si va dirigido a niños, marcarlo «para niños» al subirlo.
   - **Personas reales:** permiso de quien sale o habla; nombres escritos como los confirmó.
6. **Informe corto**, con tres columnas: **Probado y bien**, **Falló** (qué pasó, cómo repetirlo, gravedad, arreglo) y **No se pudo probar** (por ejemplo: oído humano, teléfono real, cómo se ve dentro de la plataforma).

## Señales de alerta
- «Se ve bien» sin haber mirado cuadros.
- Un WARN ignorado sin explicar.
- Falta de licencia de una música o imagen.
- Una voz o cara de una persona real sin permiso.

## Verificación
- [ ] `check.py --content` corrido para la plataforma de destino.
- [ ] Cuadros mirados a tamaño completo.
- [ ] Lista de derechos, etiqueta de IA y audiencia repasada.
- [ ] El informe dice qué no se pudo comprobar.
- [ ] Ningún arreglo se hizo sin permiso.

## Qué se probó (2026-11-04)
La cadena de medidas (`check.py --content`, `look.py` y la verificación de subtítulos) se corrió sobre un video de prueba **inventado**: antes de limpiar el audio marcó un FAIL de volumen (-37 LUFS); con el audio limpio sin murmullo marcó 12 cortes de audio; con la cadena completa dio 18 comprobaciones sin FAIL. **No se probó con un video real de teléfono ni con 3D o clips de IA** (esas skills llegan en fases posteriores); la lista de revisión manual es una guía que se afina con los primeros casos reales.
