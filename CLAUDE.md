# Proyecto: canal faceless GTA 6 en español (Shorts + TikTok)

Objetivo: canal sin cara de Shorts/TikTok sobre GTA 6 para el público hispano, aprovechando el lanzamiento (19-nov-2026), para ganar visitas y suscriptores y monetizar después.

## Reglas del proyecto
- Fuente de imagen: gameplay propio > tráileres oficiales de Rockstar. **Nunca** clips de otros youtubers/streamers (copyright + Content ID + reused content).
- Sin spoilers de historia, finales, recopilaciones de cinemáticas ni leaks (Rockstar los retira).
- **Sin violencia gráfica en los primeros 7 s** ni en miniaturas (regla de anuncios de YouTube, sept-2026).
- Cada Short con voz y ángulo propio. Guion para leer en voz alta, 30–60 s.
- YPP vía Shorts: 1.000 subs + 10M vistas/90 días (20M para nuevos desde 1-feb-2027).

## Decisiones
- Mercado: todo el mundo hispano, español neutro.
- Voz: sintética (Coqui, voz masculina de España) desde 17-nov por petición de Aitor. Opción alternativa: su voz → `herramientas/limpiar-voz.sh`.
- Presupuesto 0 €. Tiempo: horas sueltas + finde.
- YouTube y rockstargames.com están bloqueados en el entorno cloud: descargas y render final en el PC de Aitor. Investigación de YouTube vía Firecrawl (gasta créditos).

## Estructura
- herramientas/limpiar-voz.sh — limpia la voz (ruido, pausas, -14 LUFS)
- herramientas/hacer-short.sh — clip 16:9 → vertical 1080x1920 con fondo difuminado, gancho, subtítulos .srt y voz con ducking
- herramientas/generar-short.py — guion JSON (03-guiones/*.json) → Short completo: voz sintética por escena, imágenes con zoom, subtítulos palabra a palabra, gancho, whoosh
- herramientas/instalar-voz.sh — instala Coqui TTS + modelo es/css10/vits (desde GitHub; HuggingFace está bloqueado). En el JSON, `texto` va escrito "como suena" (Ge te a seis, Vais Siti, Yeison) y `subtitulo` con la grafía correcta
- 04-assets/clips-fuente/gta6-oficial/ — imágenes oficiales sacadas de la galería de rockstargames.com/VI vía captura de Firecrawl (algunas tenían cortes de carga; revisar antes de usar)
- 01-investigacion/plan-gta6.md — hallazgos, formatos, pipeline
- 02-referencias/ — canales modelo y vídeos que funcionan
- 03-guiones/ — plantilla-short.md + guiones
- 04-assets/ — clips-fuente, audio, miniaturas (multimedia fuera de git)
- 05-videos-finales/

## Estado
- 2026-10-21: arranque como canal faceless genérico (en historial git).
- 2026-11-16: pivot a GTA 6 Shorts. Investigación hecha, hacer-short.sh probado con vídeo sintético.
- 2026-11-17: Aitor pide que Claude haga todo (voz sintética en vez de la suya). Vídeo 01 para subir hoy + guiones/vídeos 02–06 para el 18-nov. Pendiente: que Aitor escuche la voz (no se pudo verificar de oído), feedback de los primeros vídeos, saber si tiene consola + juego.
