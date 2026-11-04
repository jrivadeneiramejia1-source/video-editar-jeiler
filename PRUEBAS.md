# Qué se probó de verdad

Todas las pruebas de las fases 2 y 3 (2026-11-04) usaron un video **inventado**: narraciones sintéticas (una de 47 s con ruido y volumen bajo para imitar un teléfono, y otra de 23 s sobre «Gemini contra ChatGPT»). **Falta probar con una grabación real tuya** (1 minuto, con tu voz y tu permiso).

| Skill | Estado | Qué se probó |
|---|---|---|
| **ffmpeg-skill** | Probada en la tarea de prueba | Se revisó su código (sin red ni comandos de riesgo) y corrieron `probe`, `audio --replace`, `silence`, `caption`, `check --content` y `look` desde la carpeta instalada. No se probaron sus otras 35 herramientas. |
| **audio-limpio** | Probada en la tarea de prueba | Ruido -41 → -67 dBFS y DNSMOS de ruido 1,96 → 4,03 con la IA; sin IA casi no mejora. Unión de dos voces de -46 y -13 LUFS: quedaron en -16,1 y -16,0. Hallazgos: la IA deja silencio digital (se agrega murmullo) y baja un poco el reconocimiento. Sin probar: grabación real, música, otros idiomas. |
| **subtitulos** | Probada en la tarea de prueba | Reconocimiento 96,5 % con ruido; alineación con guion a menos de 0,3 s en 10 de 10 frases; la verificación aceptó +0,25 s y rechazó +1,5 s y -0,6 s; subtítulos quemados y mirados en cuadros. Sin probar: voz real, acentos, varias voces, música, otros idiomas. |
| **verificar-video** | Probada en parte | Las medidas corrieron (18 comprobaciones sin FAIL en el video final). La revisión manual (derechos, etiqueta de IA, 3D) no se ha usado con casos reales. |
| **editar-por-texto** | Probada en la tarea de prueba | Quitar una frase: corte sin palabras cortadas (margen de ~0,5 s a cada lado frente a la verdad), duración 39,07 s (esperada 39,09), texto conservado 98 %. Tres cortes a la vez: 93,5 %. La verificación falla como debe con el video sin cortar. Se corrigió un error real (`--terminar-en` cortaba a mitad de oración). Sin probar: voz real con muletillas, varias personas, empalmes escuchados. |
| **graficos-por-palabra** | Probada en la tarea de prueba | Logos de Gemini y Gmail (Simple Icons), «ChatGPT» como texto, imagen propia y SVG local; plan, aplicación en una pasada, verificación por píxeles (21-50 % dentro, 0 % fuera) y hoja de cuadros mirada. OpenAI no está en Simple Icons: aviso claro. Dos errores reales corregidos. Sin probar: vertical con zonas seguras, PNG oficiales, video con movimiento. |
| **analizar-video** | Probada en la tarea de prueba | Resumen, escenas, picos, hoja de cuadros y transcripción con minutaje del video de 23 s. Sin probar: video real con cortes y música. |
| **publicar-video** | Probada en parte | Exportar a Shorts (12 comprobaciones sin FAIL), `title.py` y `chapters.py` en español tras el parche. Sin probar: subir, `publicacion.md` con un caso real, `yt-seo` y el resto de `yt-*`. |
| **yt-\*** (11, de terceros) | Probadas solo 2 herramientas | `chapters.py` y `title.py` (parcheadas para español). El puntaje de ganchos (`yt-script`, `yt-viral`) es solo para inglés. |

## Activación sola
Todavía no se midió (se hará en la fase 7).
