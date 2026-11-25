# Hallazgos de la investigación con REA — editar (2026-11-06)

**Resultado corto:** REA no hizo falta. El vacío 3 ya está cubierto y para el 5 existe una herramienta libre. Todo se probó en la nube de Claude con un video inventado; nada se instaló en computadores de Jeiler.

| # | Vacío | Herramienta | Licencia | Resultado |
| --- | --- | --- | --- | --- |
| 3 | Textos animados y transiciones | `join.py` y `graphics.py` de `ffmpeg-skill` | MIT | Cubierto; ver mejora abajo |
| 5 | Reencuadre a vertical siguiendo la cara | `pyautoflip@0.2.1` | MIT | **Se instala y corre; sin probar con una cara real** |

## 3. Textos animados y transiciones
- `graphics.py` ya trae tercio inferior, título, gancho de apertura, sticker, cuenta regresiva y más; `caption.py` trae subtítulos con `--animate pop` y `--karaoke`.
- `join.py` ofrece **15 transiciones** (su texto de ayuda dice 12 y está desactualizado), pero el `ffmpeg` de la nube (6.1.1) trae **58**; faltan, por ejemplo, `zoomin`, `pixelize`, `coverleft`, `revealup` y `squeezeh`. **Mejora propuesta:** ampliar la lista `TRANSITIONS` de `join.py` con esas, sin herramienta nueva. No está hecha ni probada con el resto del script.
- Descartado `ffmpeg-concat` (transiciones OpenGL): archivado desde julio de 2026.

## 5. Reencuadre vertical
- Hoy `fit.py --fit crop` recorta al centro (o donde se le diga con `--crop-x/--crop-y`) y `crop.py` acepta un rectángulo si alguien ya detectó la cara. No hay detección automática.
- `pyautoflip` (versión 0.2.1 del 27 de marzo de 2026; usa MediaPipe, InsightFace y PySceneDetect; corre en CPU) se instaló en un entorno aparte en 79 s. Con un video sintético de 4 s sin personas procesó 100 cuadros en 1,6 s, mantuvo el audio y entregó 404×720 (formato 9:16 con la altura del original, así que conviene partir de un video en 1080p). Detectó 0 caras, como era de esperar.
- **Sin probar:** que siga bien una cara real (no se usaron videos con personas); cuántos segundos tarda con videos largos; calidad del relleno borroso.
- Alternativa vista: `KazKozDev/auto-vertical-reframe` (MIT, YOLO + seguimiento): más pesada (PyTorch), probada solo en Mac según su página, 4 commits. Queda de segunda opción.

## Fuentes (páginas abiertas el 2026-11-06)
- [pyautoflip en PyPI](https://pypi.org/project/pyautoflip/)
- [KazKozDev/auto-vertical-reframe](https://github.com/KazKozDev/auto-vertical-reframe)
- [mifi/ffmpeg-concat](https://github.com/mifi/ffmpeg-concat)
