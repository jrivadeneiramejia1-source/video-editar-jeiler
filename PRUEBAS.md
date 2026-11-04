# Qué se probó de verdad

Todas las pruebas de la fase 2 (2026-11-04) usaron un video **inventado**: una narración sintética de 47 s, con ruido y volumen bajo para imitar un teléfono. **Falta probar con una grabación real tuya** (1 minuto, con tu voz y tu permiso).

| Skill | Estado | Qué se probó |
|---|---|---|
| **ffmpeg-skill** | Probada en la tarea de prueba | Se revisó su código (sin red ni comandos de riesgo) y corrieron `probe`, `audio --replace`, `silence`, `caption`, `check --content` y `look` desde la carpeta instalada. No se probaron sus otras 35 herramientas. |
| **audio-limpio** | Probada en la tarea de prueba | Ruido -41 → -67 dBFS y DNSMOS de ruido 1,96 → 4,03 con la IA; sin IA casi no mejora. Unión de dos voces de -46 y -13 LUFS: quedaron en -16,1 y -16,0. Hallazgos: la IA deja silencio digital (se agrega murmullo) y baja un poco el reconocimiento. Sin probar: grabación real, música, otros idiomas. |
| **subtitulos** | Probada en la tarea de prueba | Reconocimiento 96,5 % con ruido; alineación con guion a menos de 0,3 s en 10 de 10 frases; la verificación aceptó +0,25 s y rechazó +1,5 s y -0,6 s; subtítulos quemados y mirados en cuadros. Sin probar: voz real, acentos, varias voces, música, otros idiomas. |
| **verificar-video** | Probada en parte | Las medidas corrieron (18 comprobaciones sin FAIL en el video final). La revisión manual (derechos, etiqueta de IA, 3D) no se ha usado con casos reales. |

## Activación sola
Todavía no se midió (se hará en la fase 7).
