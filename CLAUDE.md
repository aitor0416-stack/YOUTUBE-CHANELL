# Proyecto: canal YouTube faceless en español

Objetivo: adaptar al mercado hispano el formato de canales faceless de EE.UU. que ya funcionan, para generar visitas e ingresos.

## Reglas del proyecto
- No traducir guiones ajenos: copiar formato/estructura/temas, guion propio con varias fuentes (copyright + política "inauthentic content" de YouTube).
- Cada vídeo debe tener ángulo propio y edición variada (YouTube evalúa el canal entero).
- Planificar YPP con umbral 2027: 1.000 subs + 8.000 h (o 20M vistas Shorts).

## Decisiones
- Mercado: todo el mundo hispano, español neutro.
- Voz: la de Aitor (grabada) → limpiar con `herramientas/limpiar-voz.sh`. Guiones escritos para leer en voz alta.
- Presupuesto 0 € al inicio. Tiempo: horas sueltas + finde → 1 vídeo largo/semana + Shorts derivados.

## Estructura
- herramientas/ — scripts (limpiar-voz.sh: ffmpeg, quita ruido, acorta pausas, normaliza a -14 LUFS)
- 01-investigacion/ — hallazgos, análisis de nicho y canales (ver plan-y-hallazgos.md)
- 02-referencias-usa/ — datos y transcripciones de canales modelo (solo análisis)
- 03-guiones/ — guiones en español
- 04-assets/ — imágenes, audio, miniaturas
- 05-videos-finales/

## Estado
- 2026-10-21: directorio creado, investigación inicial hecha, decisiones de fase 0 tomadas, script de voz probado con audio sintético. Pendiente: repo GitHub (lo crea Aitor, Claude no puede crear repos desde esta sesión), prueba con voz real, fase 1 validar nicho.
