# Proyecto: canal faceless GTA 6 en español (Shorts + TikTok)

Objetivo: canal sin cara de Shorts/TikTok sobre GTA 6 para el público hispano, aprovechando el lanzamiento (19-nov-2026), para ganar visitas y suscriptores y monetizar después.

## Reglas del proyecto
- Fuente de imagen: gameplay propio > tráileres oficiales de Rockstar. **Nunca** clips de otros youtubers/streamers (copyright + Content ID + reused content).
- Sin spoilers de historia, finales, recopilaciones de cinemáticas ni leaks (Rockstar los retira).
- **Sin violencia gráfica en los primeros 7 s** ni en miniaturas (regla de anuncios de YouTube, sept-2026).
- Cada Short con voz y ángulo propio. Guion para leer en voz alta, 20–35 s.
- **Gancho hablado en el segundo 0** = el título dicho en voz alta. Fórmulas probadas en `03-guiones/plantilla-short.md` (contraria, comparación con GTA 5, ventaja, lista con urgencia, aviso, ángulo hispano). Análisis en `02-referencias/analisis-virales.md`.
- **En pantalla solo subtítulos abajo** (1–2 palabras, clave en amarillo, pop). Nada de rótulos arriba ni barras (petición de Aitor 17-nov).
- Cada guion JSON lleva `titulo` (≤60 car., gancho + "GTA 6" + 1 emoji), `descripcion` (gancho, pregunta 👇, créditos, 4–5 hashtags).
- Verificar sincronía con `herramientas/verificar-sync.py` y revisar en navegador (Playwright) antes de entregar.
- YPP vía Shorts: 1.000 subs + 10M vistas/90 días (20M para nuevos desde 1-feb-2027).

## Decisiones
- Mercado: todo el mundo hispano, español neutro.
- Voz: sintética Kokoro (`em_santa`, modelo Apache-2.0 desde GitHub thewh1teagle/kokoro-onnx releases model-files-v1.0) por defecto; Coqui css10 como alternativa (VOZ_MOTOR=coqui). Opción: su voz → `herramientas/limpiar-voz.sh`, o su timbre vía FreeVC.
- Playwright MCP: necesita `ln -sf /opt/pw-browsers/chromium-1194/chrome-linux/chrome /opt/google/chrome/chrome` (no persiste entre sesiones).
- Presupuesto 0 €. Tiempo: horas sueltas + finde.
- YouTube y rockstargames.com están bloqueados en el entorno cloud: descargas y render final en el PC de Aitor. Investigación de YouTube vía Firecrawl (gasta créditos).

## Estructura
- herramientas/limpiar-voz.sh — limpia la voz (ruido, pausas, -14 LUFS)
- herramientas/hacer-short.sh — clip 16:9 → vertical 1080x1920 con fondo difuminado, gancho, subtítulos .srt y voz con ducking
- herramientas/generar-short.py — guion JSON (03-guiones/*.json) → Short dinámico: voz por escena (+10 % velocidad), planos del tráiler 4K recortados en vertical con zoom (corte cada 1,2 s en el gancho y ~1,8 s después), subtítulos karaoke (palabra activa en amarillo, pop), etiqueta por punto, destello entre puntos, barra de progreso, música propia con ducking, whoosh. Env: COQUI_MODEL_DIR, TRAILERS_DIR, opcional VOZ_REFERENCIA + FREEVC_DIR
- herramientas/musica.py — base synthwave generada (sin copyright); `semilla_musica` del guion la varía
- herramientas/instalar-voz.sh — instala Coqui TTS + modelo es/css10/vits (desde GitHub; HuggingFace está bloqueado). Con CON_FREEVC=1 instala también FreeVC+WavLM para convertir la voz al timbre de Aitor (probado: funciona). En el JSON, `texto` va escrito "como suena" (Ge te a seis, Vais Siti, Yeison) y `subtitulo` con la grafía correcta
- 02-referencias/planos-trailers.json — catálogo de 68 planos útiles de los 3 tráileres oficiales (id, segundos, etiquetas, centro del recorte). Sin armas/explosiones/logos. Solo imagen: el audio tiene música con copyright
- Tráileres 4K: se descargan con Firecrawl `alexandria_library_read` provider `youtube` capability `read` formats ["video"] (devuelve URL en storage.googleapis.com, caduca en 1 h). IDs: launch rz1B4B2yBZY, t1 QdBZY2fkU-0, t2 VQRLujxTm3c → guardar como launch.mp4/t1.mp4/t2.mp4 en TRAILERS_DIR
- Referencia que funciona en español: "Leo te lo Cuenta" (@Leo-te-lo-Cuenta), Short "Los chistes de GTA 6 que solo pillas si hablas español" 21K vistas en 1 día: 31 s, 3 puntos, cortes de 1,2 s en el gancho, gancho fijo arriba, subtítulos de 2 palabras, tarjetas con zoom, barra de progreso, mascota de dibujo. El ángulo "hispano" rinde más que curiosidades genéricas
- Playwright MCP no arranca (busca Chrome en /opt/google/chrome) y YouTube está bloqueado igualmente: usar Firecrawl
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
- 2026-11-17 (2): v2 dinámica con metraje real de tráileres, karaoke, música y conversión de voz lista. Pendiente: grabación de 30–60 s de Aitor para VOZ_REFERENCIA; ideas de ángulo hispano (chistes/carteles que solo pilla un hispanohablante).
- 2026-11-18: día de lanzamiento (NZ ya juega desde las 11:00 UTC). 5 Shorts de noticia del día: 07 récord Metacritic 99 (empata Ocarina of Time; GTA IV 98, GTA V 97), 08 ya se juega en Nueva Zelanda + aviso truco región Xbox (va contra sus normas), 09 reservas ~1.100 M$ (estimación Sensor Tower, 11,27 M uds; GTA V tardó 3 días en 1.000 M), 10 sin versión PC (sin fecha; medios hablan de 2027), 11 guía antes de medianoche (precarga, 212 GB, parches). Fix: bloques de subtítulo de máx. 14 caracteres (16 todavía cortaba "MODO RENDIMIENTO") (se cortaba "ESTARÁS DESCARGANDO"); evitar planos `redes` cuando compiten con subtítulos. Noticias caducan rápido: publicar hoy.
- 2026-11-18 (2): Aitor pidió clips de un gameplay de TheGrefg (IKmDcF0QhBA): rechazado (sin permiso en la descripción, spoilers de historia y violencia). Se usa como investigación: Shorts 12–15 de mecánicas contrastadas con el análisis de GamingTrend (cuerpo/fitness, policía recuerda ropa/coche, perfil criminal + relación de 4 niveles, 30 FPS sin modos gráficos). TikTok Creator Rewards (TikTok Creator Academy, sept-2026): solo EE. UU., UK, Alemania, Japón, Corea, Francia, México y Brasil; 10K seguidores, 100K vistas/30 días, vídeos ≥1 min y 100 % originales → los clips ajenos no cobran. España no está.
