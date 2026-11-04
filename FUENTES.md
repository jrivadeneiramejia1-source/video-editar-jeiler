# Fuentes de las skills copiadas

Cada fila dice de dónde viene una skill, qué versión se copió y con qué licencia. Sirve para saber si hay una versión nueva en el origen (se compara el commit).

| Skills | Origen | Commit copiado | Fecha | Licencia |
|---|---|---|---|---|
| `ffmpeg-skill` (solo `SKILL.md`, `references/` y `scripts/`) | kajisho5/ffmpeg-skill | 1ce2c18 | 2026-11-01 | MIT |

## Revisar si hay versiones nuevas (cada mes)
```bash
python3 -I comparar-fuentes.py
```
Es de solo lectura: compara cada commit de esta tabla con el más nuevo del repo de origen y dice «igual» o «HAY CAMBIOS» (o no pudo consultar). Salida 0 = todo igual, 1 = hay cambios, 2 = no se pudo consultar alguno. Que haya cambios no obliga a actualizar: primero mirar qué cambió, volver a revisar su seguridad (`SEGURIDAD.md`) y actualizar la fila de esta tabla.

Los modelos que descargan `audio-limpio` y `subtitulos` (no están en el repo): DPDFNet (Apache-2.0), Silero VAD (MIT), Parakeet TDT 0.6B v3 de NVIDIA (su ficha indica CC-BY-4.0; verificar) y DNSMOS de Microsoft (CC-BY-4.0). Salen de `github.com/k2-fsa/sherpa-onnx` y `microsoft/DNS-Challenge`.
