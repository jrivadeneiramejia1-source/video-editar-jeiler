---
name: graficos-por-palabra
description: >-
  Pone un logo, una imagen o un texto en el video justo cuando la voz dice una palabra: dices «Gemini» y aparece su logo, dices «ChatGPT» y sale su nombre. Encuentra cada vez que se dice la palabra, arma la lista de gráficos para aprobarla, los pone en una sola pasada sin tocar el audio y comprueba cuadro por cuadro que salen cuando y donde debían. Usar cuando el usuario diga "que salga el logo cuando diga X", "pon una imagen cuando mencione...", "gráficos que acompañen lo que digo" o "comparar A con B en el video". No crea los logos: usa Simple Icons (CC0) o el archivo que dé Jeiler.
---

# Gráficos por palabra

Cuando la voz dice una palabra clave, aparece un gráfico con entrada y salida suaves. Es el modo «edición» de explicativos y comparaciones (Gemini contra ChatGPT, herramientas, marcas, objetos).

## Reglas
- **Logos de marcas: solo para nombrar o comparar**, nunca para dar a entender que la marca apoya el video. Si se publica, decirlo en la descripción cuando haya duda.
- **Nunca redibujar ni inventar un logo.** Fuentes permitidas: Simple Icons (iconos de marcas en SVG, de dominio público CC0; la marca sigue siendo de su dueño) o un archivo que Jeiler entregue (de la página de prensa oficial de la marca). **Hay marcas que no están en Simple Icons** (en la prueba, OpenAI): ahí se pide el archivo o se usa un texto.
- Mostrar la lista y esperar el «sí» de Jeiler antes de generar.
- Trabajar en copias; originales intactos.
- Claude no ve el movimiento: mide cuadros y mira una hoja de cuadros.

## Proceso
1. **Transcribir del audio original** (`subtitulos/scripts/transcribir.py`) → `palabras.json`.
2. **Dar el formato final primero** (por ejemplo vertical con `export.py --preset shorts`, de `ffmpeg-skill`) y poner los gráficos **después**, para que queden en la zona segura. Los subtítulos van al final (`subtitulos`).
3. **Escribir `reglas.json`** (ver ejemplo en `python3 scripts/graficos_por_palabra.py` sin argumentos). Tipos: `logo` (`slug` de Simple Icons o `archivo` svg/png, `color` opcional), `imagen` (`archivo` png/jpg) y `texto`. `posicion`: top-left, top-right, bottom-left, bottom-right, center. `tamano` (fracción del ancho), `duracion` (s), `solo_primera`.
4. **Plan:** `python3 scripts/graficos_por_palabra.py plan VIDEO palabras.json reglas.json --plataforma youtube -o plan_graficos.json`. Dice cuándo se oyó cada palabra y avisa si falta un logo, si dos gráficos chocan en la misma esquina o si cae en una zona que tapan los botones de la app (`--plataforma shorts|tiktok|reels`). La misma palabra dicha seguido se une en un solo gráfico para que no parpadee.
5. **Enseñar la lista** y esperar el «sí».
6. **Aplicar:** `python3 scripts/graficos_por_palabra.py aplicar VIDEO plan_graficos.json SALIDA.mp4` (una pasada; audio sin tocar; no sobrescribe).
7. **Verificar:** `python3 scripts/graficos_por_palabra.py verificar VIDEO SALIDA.mp4 plan_graficos.json` compara con el original: dentro del intervalo deben cambiar píxeles en la zona del gráfico; antes y después, ninguno. Después, mirar cuadros: `python3 ../ffmpeg-skill/scripts/look.py SALIDA.mp4 --tiles 3x2`.

## Señales de alerta
- Un logo «parecido» dibujado a mano.
- Gráficos que tapan la cara, los subtítulos o la zona de botones de TikTok o Shorts.
- Logos demasiado grandes o muchos a la vez: el video se vuelve un catálogo.
- Palabras que el reconocedor oye mal (aparece el aviso «no se oye»): revisar la transcripción.

## Verificación
- [ ] Jeiler aprobó la lista de gráficos.
- [ ] `verificar` pasó y se miró una hoja de cuadros.
- [ ] Cada logo viene de Simple Icons o de un archivo dado por Jeiler.
- [ ] Se dijo que no se pudo ver el video en movimiento.

## Qué se probó (2026-11-04)
Con una narración **inventada** de 23 s («Gemini contra ChatGPT»): el logo de Gemini (Simple Icons, con su color de marca) salió en la esquina superior izquierda cuando se dijo la palabra, «ChatGPT» salió como texto verde arriba a la derecha, y el de Gmail abajo; las menciones seguidas se unieron en un solo gráfico. La verificación midió 21 a 50 % de píxeles cambiados dentro del intervalo y 0 % antes y después, y falló como debía al aplicarla al video sin gráficos. Se miró una hoja de tres cuadros. También se probó una imagen propia y un SVG local con color. La búsqueda de «openai» en Simple Icons dio un aviso claro (no existe) y el resto del plan siguió. Bugs reales que aparecieron y se corrigieron: numeración de entradas de ffmpeg con textos y parpadeo en menciones seguidas. **No se probó** en formato vertical con zonas seguras, con PNG oficiales de marcas, con muchos gráficos juntos ni en un video con movimiento.
