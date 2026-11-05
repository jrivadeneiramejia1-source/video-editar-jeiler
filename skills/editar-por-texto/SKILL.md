---
name: editar-por-texto
description: >-
  Edita un video diciendo qué frases quitar o conservar, como si se editara la transcripción: «quita la parte donde digo X», «empieza en tal frase», «termina cuando diga Y». Transcribe, encuentra la frase, propone la lista de cortes para aprobarla, corta en una copia sin dejar palabras a medias y comprueba el resultado volviendo a transcribirlo. Usar cuando el usuario diga "quita la parte donde digo...", "córtame lo de...", "deja solo hasta que diga...", "elimina esa frase del video" o "recorta el principio". No sirve para cortes por imagen (sin voz) ni para videos sin habla.
---

# Editar por texto

En vez de buscar el segundo exacto en una línea de tiempo, Jeiler dice la frase y esta skill encuentra dónde está, arma los cortes y los aplica **en una copia**.

## Reglas
- **Mostrar siempre la lista de cortes y esperar el «sí» de Jeiler** antes de cortar. Los cortes no se rehacen gratis.
- Trabajar en copias: el video original no se toca. Archivos de comunidades indígenas: nunca se modifican ni se suben.
- Quitar una frase quita **la oración entera** (hasta el punto o una pausa larga); `--exacto` solo las palabras halladas. Lo mismo para empezar y terminar.
- Si la frase se parece menos del 75 % a lo que se oye, el aviso sale en la lista: confirmar antes de aplicar.
- Claude no oye: los empalmes (el punto donde se unen dos partes) los tiene que escuchar Jeiler.
- Una voz de otra persona solo con su permiso.

## Instalar
Instalar el grupo `editar-por-texto` (trae `ffmpeg-skill` y `subtitulos`) y los modelos de `subtitulos` (`bash ../subtitulos/scripts/instalar_modelos.sh`). `PY=~/.cache/video-jeiler/venv/bin/python`.

## Proceso
1. **Transcribir el audio original:** `$PY ../subtitulos/scripts/transcribir.py VIDEO palabras.json`.
2. **Buscar** (si hay duda de qué se oye o dónde): `python3 scripts/editar_por_texto.py buscar palabras.json "frase"`.
3. **Armar el plan** (no corta nada):
   ```bash
   python3 scripts/editar_por_texto.py plan palabras.json --video VIDEO \
       --quitar "si la limonada queda muy ácida" --empezar-en "primero lava bien" --terminar-en "quinto añade hielo" -o plan.json
   ```
   Se puede repetir `--quitar`. `--margen` (0,25 s por defecto) es el respiro que queda a cada lado de un corte; las pausas largas junto a lo quitado también se van, y los empalmes quedan con una pausa de ~0,5 s.
4. **Enseñar la lista** (cada corte con minutaje y el texto que se oye) y esperar el «sí».
5. **Aplicar** (usa `cut.py --remove --accurate` de `ffmpeg-skill`): `python3 scripts/editar_por_texto.py aplicar VIDEO plan.json SALIDA.mp4`. No sobrescribe: elegir un nombre nuevo.
6. **Verificar:** `$PY scripts/editar_por_texto.py verificar SALIDA.mp4 palabras.json plan.json` (duración esperada, texto conservado vs voz re-transcrita > 93 %, y que lo quitado ya no se oye). Sale con código 1 si algo falla.
7. Si hay subtítulos, rehacerlos sobre el video nuevo (`subtitulos`): los tiempos cambiaron.

## Señales de alerta
- Cortar sin haber enseñado la lista.
- Un corte que deja una frase a medias (revisar con `buscar` y repetir con otra frase o con `--exacto`).
- Frases que se repiten en el video (la skill toma la mejor coincidencia): confirmar el minutaje.
- Prometer que «suena natural» sin que Jeiler lo haya escuchado.

## Verificación
- [ ] Jeiler aprobó la lista de cortes.
- [ ] `verificar` pasó (o se explicó cada falla).
- [ ] El original sigue intacto.
- [ ] Se dijo que los empalmes no se pudieron escuchar.

## Qué se probó (2026-11-04)
Con una grabación **inventada** de 47 s (10 frases): quitar una frase cortó de 27,30 a 35,61 s; la verdad era que la frase anterior terminaba en 26,82 y la siguiente empezaba en 36,14, o sea, sin palabras cortadas. La duración quedó en 39,07 s (esperada 39,09) y el texto conservado coincidió 98 %. Con tres cortes a la vez (empezar en, quitar, terminar en) la duración fue la esperada (17,67 s) y el texto coincidió 93,5 %. La verificación **falló** como debía al aplicarla al video sin cortar. Un error real que apareció y se corrigió: `--terminar-en` cortaba a mitad de la oración. **No se probó con una voz real** (muletillas, tartamudeos, frases repetidas), con varias personas hablando, ni con cortes que necesiten continuidad de imagen.
