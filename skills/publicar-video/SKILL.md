---
name: publicar-video
description: >-
  Deja un video listo para publicar sin publicarlo: versión para cada plataforma (YouTube, Shorts, TikTok, Reels, WhatsApp), título y texto de miniatura, descripción con créditos y fuentes, capítulos, subtítulos, etiqueta de IA y marca «para niños», más una lista de pasos para que Jeiler lo suba. Usar cuando el usuario diga "prepáralo para subir", "ponle título y descripción", "hazle capítulos", "qué pongo al subirlo" o "versión vertical para TikTok". Esta skill nunca publica ni pide claves de las plataformas.
---

# Publicar un video (preparar, no subir)

Entrega un archivo `publicacion.md` con bloques listos para copiar y los videos exportados. **Jeiler sube.**

## Reglas
- **Nada se publica solo**; nunca pedir ni guardar claves o sesiones de YouTube, TikTok o Instagram.
- Verificar antes con `verificar-video`. No preparar la publicación de algo que falló.
- Los créditos dicen la verdad: música, imágenes, logos, voz y herramientas de IA usadas. Voces o caras de personas reales, solo con su permiso.
- Reglas de las plataformas sobre IA, contenido para niños y derechos cambian: **verificarlas en sus páginas oficiales** el día de subir. La skill no promete que el video «funcione» ni que sea monetizable.

## Proceso
1. **Preguntar destino:** plataforma(s), horizontal o vertical, y si va dirigido a niños (cambia reglas y marcas).
2. **Verificar:** `verificar-video` para la plataforma elegida.
3. **Exportar una versión por plataforma** con `ffmpeg-skill`, por ejemplo `python3 ../ffmpeg-skill/scripts/export.py VIDEO --preset shorts --fit pad --pad-fill blur --normalize -o vertical.mp4` (presets: `youtube`, `shorts`, `tiktok`, `reels`, `facebook`...) y repasarla con `check.py --platform shorts`. Los gráficos y subtítulos se ponen **después** de dar el formato (ver `graficos-por-palabra` y `subtitulos`).
4. **Subtítulos:** subir el `.srt` revisado como pista aparte (YouTube) además de quemarlos si el video es vertical.
5. **Redactar `publicacion.md`** con estos bloques (con las herramientas `yt-*` que ayuden):
   - **Título** (3 opciones) y **texto de miniatura** que no repita el título: `python3 ../yt-package/title.py --title "..." --thumb "..."`.
   - **Descripción:** qué se aprende, **capítulos** (`python3 ../yt-chapters/chapters.py subtitulos.srt --target 6`, y volver a titular cada línea), créditos, fuentes y la frase de IA («Hecho con apoyo de inteligencia artificial: ...»).
   - **Etiquetas y palabras clave** (`yt-seo`).
   - **Declaraciones al subir:** ¿contenido alterado o sintético? ¿para niños? Dejar la respuesta recomendada y el motivo, para que Jeiler la marque.
   - **Lista de pasos** para subirlo y qué mirar después de publicar.
6. **Entregar** `publicacion.md` y los archivos; decir qué no se pudo comprobar (cómo se ve dentro de la plataforma, derechos de música).

## Sobre las skills `yt-*` (de terceros, en inglés)
Vienen de `Jakeschincariol/youtube-agent-skill` (MIT) y están pensadas para inglés. Se parchearon `yt-chapters` y `yt-package` para que lean tildes y palabras en español. **No usar el puntaje de ganchos de `yt-script` ni `yt-viral` en español**: sus fórmulas y listas son inglesas. Para ajustar el tono a Jeiler, copiar `plantilla/voice.md` a `~/.claude/youtube/voice.md` y llenarla. `yt-retention` necesita el CSV de retención que exporta YouTube Studio (después de publicar).

## Señales de alerta
- Prometer vistas, ingresos o «que se haga viral».
- Créditos incompletos o música sin licencia anotada.
- Copiar un título de otro canal.
- Marcar «no es para niños» cuando sí va dirigido a ellos.

## Verificación
- [ ] `verificar-video` pasó para cada versión.
- [ ] `publicacion.md` tiene título, descripción, capítulos, créditos, frase de IA y declaraciones.
- [ ] Reglas de la plataforma revisadas el día de subir.
- [ ] No se publicó nada ni se pidieron claves.

## Qué se probó (2026-11-04)
Con el video de prueba **inventado**: `export.py --preset shorts --fit pad --pad-fill blur --normalize` dio un 1080x1920 que pasó 12 comprobaciones de Shorts sin FAIL (-14,9 LUFS); `title.py` marcó en español una palabra vaga («increíble») y que la miniatura repetía «limonada»; `chapters.py` dio tres capítulos con palabras completas tras el parche (antes cortaba «limón» en «limo»). **No se probó** subir a ninguna plataforma, ni la redacción completa de `publicacion.md` con un caso real, ni `yt-seo`, `yt-plan`, `yt-audit`, `yt-comment`, `yt-retention` ni `yt-viral`.
