# Revisión de seguridad

Fase 2 revisada el 2026-11-04.

## Cómo se revisa cada cosa antes de agregarla
1. **Licencia** primero (ver `third-party/LEEME.md`): MIT, Apache-2.0, BSD, CC0 o Unlicense se pueden copiar; GPL o AGPL, solo ideas; sin licencia, solo enlazar.
2. **Leer el `SKILL.md` completo y sus scripts.** Buscar comandos de riesgo: descargar y ejecutar a la vez (`curl ... | sh`), `eval`, `rm -rf /`, `base64 -d`, `nc -e`, `sudo`.
3. **gitleaks** (busca claves y tokens escritos en archivos) sobre los archivos y el historial.
4. Instalar dependencias con `--ignore-scripts` y sin ejecutar binarios descargados.
5. **No se usa `snyk/agent-scan`:** pide cuenta y token de Snyk y sube el contenido de las skills a su servicio. Queda a decisión de Jeiler.

## Privacidad (el repo es público)
- No se suben nombres de estudiantes, voces, caras, audios ni capturas de videos reales. Los ejemplos usan personajes y textos inventados.
- `.gitignore` bloquea audios, videos y las carpetas `entregas/` y `privado/` como red de seguridad, pero no reemplaza la revisión a mano antes de cada commit.
- Archivos de comunidades indígenas: no se modifican ni se suben a servicios externos.

## Resultado
- **ffmpeg-skill** (tercero): se leyeron sus scripts y se buscaron patrones de riesgo. No hay descargas ni conexiones de red en su código (solo texto de ayuda con `pip install` y `sudo apt install`), ni `eval`, `exec`, `os.system` ni `shell=True`. Se dejó fuera su servidor MCP (`mcp/`), el instalador de Node (`bin/`), las demos y las páginas: no hacen falta.
- **Scripts propios** (`audio-limpio`, `subtitulos`): solo llaman a ffmpeg y a modelos locales. Lo único que baja cosas de internet es `instalar_modelos.sh`, y solo desde `github.com` (`k2-fsa/sherpa-onnx` y `microsoft/DNS-Challenge`) a una carpeta de usuario (`~/.cache/video-jeiler`), con un Python propio (venv) para no tocar el del sistema. No verifica una huella de los modelos: queda pendiente.
- **gitleaks:** 0 hallazgos.
