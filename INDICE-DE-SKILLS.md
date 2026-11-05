# Índice de skills (plan: `docs/PLAN-video.md`, 2026-11-04)

★ = skill original (MIT). Los grupos se instalan con `./instalar.sh GRUPO`; `editar-basico` trae las cuatro y es el que se instala solo en la nube.

## Fase 2: edición básica (hecha)
| Skill | Cuándo usarla | Origen |
|---|---|---|
| **ffmpeg-skill** | Cortar, unir, acelerar, reencuadrar, quitar silencios, mezclar música, quemar subtítulos, exportar para cada plataforma y comprobar el resultado (42 herramientas de ffmpeg). | `kajisho5/ffmpeg-skill` (MIT), commit 1ce2c18; sin servidor MCP, demos ni páginas |
| ★ **audio-limpio** | Quitar el ruido de fondo de una voz con IA, dejar el volumen parejo y unir varias voces. | Original (usa DPDFNet, Apache-2.0) |
| ★ **subtitulos** | Transcribir con tiempo por palabra, alinear un guion, crear `.srt`/`.vtt`, quemarlos y verificarlos. | Original (usa Parakeet y Silero VAD) |
| ★ **verificar-video** | Puerta de calidad antes de entregar: medidas, cuadros, subtítulos y revisión manual (derechos, etiqueta de IA, caras en 3D). | Original |

| Grupo | Skills |
|---|---|
| cortar | ffmpeg-skill |
| audio | ffmpeg-skill, audio-limpio |
| subtitulos | ffmpeg-skill, subtitulos |
| verificar | ffmpeg-skill, verificar-video |
| editar-basico | las cuatro |

## Cambios respecto al plan (criterio tras revisar `ffmpeg-skill`)
- **`exportar-para` ya no se escribe:** `ffmpeg-skill` trae `export.py`, plantillas por plataforma y `check.py` con su tabla de especificaciones. Repetirlo sería duplicar.
- **`auto-editor` se descartó:** `silence.py` de `ffmpeg-skill` ya quita silencios (probado).
- **`verificar-video` quedó delgada:** usa `check.py --content` y `look.py` y agrega solo lo que no hacen (derechos, etiqueta de IA, caras y pelo, audiencia).

## Fase 3: edición avanzada y publicación (hecha)
| Skill | Cuándo usarla | Origen |
|---|---|---|
| ★ **editar-por-texto** | «Quita la parte donde digo X», «empieza en tal frase», «termina cuando diga Y». | Original |
| ★ **graficos-por-palabra** | Que salga un logo, imagen o texto cuando la voz dice una palabra (Gemini → logo de Gemini). | Original (logos de Simple Icons, CC0) |
| ★ **analizar-video** | Entender un video (propio o de referencia): datos, escenas, cuadros y transcripción. | Original |
| ★ **publicar-video** | Dejar listo para subir: versiones por plataforma, título, descripción, créditos, capítulos, etiqueta de IA. No sube nada. | Original |
| yt-audit, yt-chapters, yt-comment, yt-edit, yt-package, yt-plan, yt-retention, yt-script, yt-seo, yt-shorts, yt-viral | Crecer y preparar el texto en YouTube (ganchos, título y miniatura, capítulos, SEO, retención, comentarios). | `Jakeschincariol/youtube-agent-skill` (MIT), a2feb21; en inglés, con 2 parches para español |

| Grupo | Skills |
|---|---|
| editar-por-texto | ffmpeg-skill, subtitulos, editar-por-texto |
| graficos-por-palabra | ffmpeg-skill, subtitulos, graficos-por-palabra |
| analizar | ffmpeg-skill, subtitulos, analizar-video |
| publicar | ffmpeg-skill, verificar-video, publicar-video y las 11 `yt-*` |

Cambio respecto al plan: **`analizar-video` se escribió como skill propia** (usa lo ya instalado: `look.py`, `scenes.py` y la transcripción) en vez de depender del plugin `watch-video`, que no se puede instalar desde una sesión. El plugin sigue siendo una alternativa.
