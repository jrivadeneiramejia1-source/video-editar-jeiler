# video-editar-jeiler

Skills para **editar y terminar videos**: cortar, quitar silencios, limpiar y unir voces, subtitular, poner logos cuando se nombran, comprimir para cada plataforma, verificar y preparar la publicación.
Sirven para videos hechos con `video-crear-jeiler` y también para los que grabes con el teléfono. Hermano de `agent-skills-jeiler`, `app-skills-jeiler` y `apk-skills-jeiler`.

Cada carpeta de `skills/` es una skill: un archivo `SKILL.md` con instrucciones para que Claude sepa cuándo y cómo usarla.

## Estado: fase 2 hecha (edición básica)
Hay 4 skills: `ffmpeg-skill` (de terceros), `audio-limpio`, `subtitulos` y `verificar-video`. Las demás llegan por fases; el orden está en `INDICE-DE-SKILLS.md`. Lo probado y lo no probado: `PRUEBAS.md`.

## Cómo usarlas
Una skill solo funciona si está en la carpeta de skills de Claude (`~/.claude/skills/`). El instalador copia por grupos:

```bash
./instalar.sh --lista            # ver los grupos
./instalar.sh editar-basico      # instalar las 4 skills de la fase 2
```
**En sesiones en la nube** se instalan solos los grupos de `grupos-activos.txt`, con un hook de inicio en `.claude/`; solo funciona si este repo está cargado como repo de la sesión. El instalador no pisa una skill que ya exista con el mismo nombre y que no haya instalado él. Mejor pocos grupos a la vez: cada skill agrega su descripción al contexto y eso gasta tokens.

## Reglas
- Repo **público**: nunca datos de personas (ver `SEGURIDAD.md` y `CLAUDE.md`).
- Siempre se trabaja en una **copia** del video; los originales no se tocan.
- Licencia MIT para lo original (`LICENSE`); lo de terceros, con su licencia en `third-party/` y su origen en `FUENTES.md`.
- Qué está probado de verdad y qué no: `PRUEBAS.md`.
