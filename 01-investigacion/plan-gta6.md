# Canal faceless GTA 6 (Shorts + TikTok) — hallazgos y plan

Fecha: 2026-11-16 · Confianza: **Cierto** / **Probable** / **Suposición**
(El plan anterior de canal faceless genérico está en el historial de git.)

## 1. Lo que cambia el plan

| # | Hallazgo | Confianza | Consecuencia |
|---|----------|-----------|--------------|
| 1 | GTA 6 sale el **19-nov-2026** (PS5 / Xbox Series). PC sin fecha. GTA Online previsto 2027 | Cierto (varias fuentes coinciden, sin retraso anunciado a 12-nov) | La ventana de máxima demanda son las 2–4 semanas tras el lanzamiento. Hay que publicar ya |
| 2 | Política de Rockstar: tolera vídeos de gameplay de fans, pero la define como **uso no comercial**. Retira leaks, finales, recopilaciones de cinemáticas y "grandes revelaciones" de la historia | Cierto (página oficial de soporte Rockstar, resumida por terceros: no pude abrirla desde aquí) | Nada de spoilers de historia ni recopilar cinemáticas. Monetizar es zona gris: Rockstar puede retirar cuando quiera |
| 3 | YouTube (sept-2026): violencia gráfica de videojuego en los **primeros 7 s = sin anuncios**; 8–15 s = anuncios limitados; >15 s = elegible. Miniaturas violentas también penalizan. Matanzas de NPCs = sin anuncios | Probable (prensa de gaming, no leí el texto oficial de YouTube) | Regla de edición: **gancho sin violencia en los 7 primeros segundos** |
| 4 | Recortar vídeos de otros youtubers = su copyright + Content ID + "reused content" | Cierto | Fuente de imagen: tu propio gameplay > tráileres oficiales de Rockstar > nunca vídeos de otros creadores |
| 5 | Shorts gaming pagan ~0,02–0,08 $ por 1.000 vistas → **1M vistas ≈ 20–80 $**, y en español hacia la parte baja | Probable (blogs, sin dato oficial) | Los Shorts dan **visitas y suscriptores**, no dinero directo. El dinero llega después (vídeos largos, afiliados, patrocinios) |
| 6 | YPP vía Shorts: 1.000 subs + 10M vistas en 90 días. Desde el 1-feb-2027 para nuevos: **20M** | Probable | Si el lanzamiento nos da tracción, intentar llegar a 10M antes de febrero. Si no, objetivo 20M |
| 7 | TikTok Creator Rewards: México sí; **España dudoso** (fuentes contradictorias). Exige vídeos de +1 min | Probable | TikTok = alcance. No contar con dinero de TikTok desde una cuenta española sin comprobarlo en TikTok Studio |
| 8 | YouTube y la web de Rockstar están **bloqueados** en este entorno cloud | Cierto (probado) | Las descargas y el renderizado final se hacen en tu PC. Aquí: guiones, investigación (vía Firecrawl), scripts |

## 2. Formatos (de más seguro a más arriesgado)

1. **Guías y trucos** ("cómo ganar dinero rápido", "3 secretos de Vice City", "dónde está X"). Necesita gameplay propio. Búsquedas altas tras el lanzamiento, poco riesgo de copyright. ← el mejor
2. **Comparativas** (Vice City vs Miami real, GTA 6 vs GTA 5, detalles de físicas). Tráiler o gameplay + fotos libres de Miami (Pexels).
3. **Noticias y curiosidades** (precio, peso de la descarga, horarios, GTA Online). Tráileres oficiales + tu voz. Muy competido y caduca rápido.
4. ❌ Clipping de streamers/youtubers, spoilers de historia, leaks, matanzas para hacer gracia.

## 3. Pipeline por Short (~45–60 min)

1. **Guion** (Claude): gancho 0–3 s, sin violencia en 0–7 s, 30–60 s en total, cierre con pregunta para comentarios. Plantilla en `03-guiones/plantilla-short.md`
2. **Voz** (tú, móvil) → `herramientas/limpiar-voz.sh`
3. **Clip** (tu gameplay o tráiler oficial) → `04-assets/clips-fuente/`
4. **Subtítulos .srt**: CapCut los genera solo, o los hago yo a partir del guion
5. **Montaje** → `herramientas/hacer-short.sh` (vertical, fondo difuminado, gancho, subtítulos, el juego baja de volumen cuando hablas)
6. Publicar el mismo vídeo en YouTube Shorts + TikTok (+ Instagram Reels)

## 4. Herramientas (0 €)

| Pieza | Herramienta | Nota |
|---|---|---|
| Guion / investigación | Claude + Firecrawl (búsqueda en YouTube, transcripciones) | Firecrawl gasta créditos de tu cuenta |
| Captura de gameplay | Botón Share de PS5 / Xbox Game Bar | Requiere consola + juego |
| Descargar tráileres oficiales | yt-dlp en tu PC | Los Términos de YouTube no permiten descargar; riesgo bajo en la práctica, pero existe (Probable) |
| Voz | móvil + `limpiar-voz.sh` | |
| Montaje | `hacer-short.sh` (ffmpeg) o CapCut free | |

## 5. Decisión pendiente clave
- **¿Tienes PS5/Xbox y vas a tener GTA 6 el día 19?** Sin gameplay propio solo quedan los formatos 2–3, más competidos y con menos margen.

## Fuentes
- https://www.forbes.com/sites/erikkain/2026/11/16/gta-6-release-date-time-ps5-xbox-series-x-download-size-day-one-update/
- https://endgametools.com/en/gta-6/news/gta-6-release-date-latest-news
- https://support.rockstargames.com/articles/7bNaeoMFTV0iUDGhStTXvz/policy-on-posting-copyrighted-material
- https://respawn.outlookindia.com/gaming/gaming-news/youtube-updates-gaming-violence-ad-rules-ahead-of-gta-6
- https://air.io/en/air-data-findings/what-is-youtube-shorts-rpm-in-your-niche-in-2026
- https://vidiq.com/blog/post/youtube-shorts-monetization/
- https://metricool.com/youtube-partner-program-2027-changes/
- https://ttcalculator.net/data/reference/creator-fund-countries/
- https://quasa.io/media/tiktok-creator-rewards-program-eligible-countries-in-2026
