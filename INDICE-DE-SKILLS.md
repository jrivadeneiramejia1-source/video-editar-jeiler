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

## Pendientes (fases siguientes)
| Grupo | Skills | Fase | Estado |
|---|---|---|---|
| editar-por-texto | ★ editar-por-texto | 3 | pendiente |
| graficos-por-palabra | ★ graficos-por-palabra (logos de Simple Icons, CC0) | 3 | pendiente |
| publicar | youtube-agent-skill (MIT), ★ publicar-video | 3 | pendiente |
| analizar | plugin watch-video (del directorio) | 3 | pendiente |
