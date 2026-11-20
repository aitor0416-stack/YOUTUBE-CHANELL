# Investigar y contrastar (Firecrawl)

Firecrawl gasta créditos de Aitor. Antes de una tanda, haz pocas búsquedas bien elegidas y
lánzalas en paralelo. Al entregar, di cuántos créditos se gastaron aproximadamente.

## Recetas

| Qué | Llamada | Coste aprox. |
|---|---|---|
| Noticias del día | `firecrawl_search` con `sources:["news","web"]`, `tbs:"qdr:d"` (día) o `"qdr:w"` (semana), `limit` 8–10 | 2–4 |
| Sacar datos concretos de un artículo | `firecrawl_scrape` con `formats:["query"]` y `queryOptions.prompt` pidiendo cifras exactas y quién las dice | 5 |
| TikTok más visto | `alexandria_library_read` → `scrapecreators` / `tiktok/search-videos`, `options:{query, date_posted:"yesterday", sort_by:"most-liked", trim:true}` | 2 |
| YouTube | `scrapecreators` / `youtube/search` (`sortBy` solo `relevance` o `popular`) | 2 |
| Leer un vídeo (descripción + transcripción) | `youtube` / `read` con `options:{url, language:"es"}` | 1–5 |
| Descargar un tráiler oficial | `youtube` / `read` con `formats:["video"]` (ver entorno.md) | ~9 |

**Respuestas grandes:** TikTok devuelve más de 1 MB. Si la respuesta queda guardada en un archivo,
no la leas entera: saca lo útil con jq/python (reproducciones, región, primeros 200 caracteres de la
descripción) y ordena por reproducciones. Si queda en un "workspace" de Firecrawl, usa
`provider:"firecrawl", capability:"bash"` con el `workspaceId` (caduca a los 5 minutos).

```bash
jq -r '.data.alexandria[0].data.search_item_list[] | [.statistics.play_count, .region,
  (.desc|gsub("\n";" ")|.[0:200])] | @tsv' response.json | sort -rn | head -20
```

## Contrastar: cuándo un dato entra en un guion

| Caso | Qué hacer | Confianza |
|---|---|---|
| Lo dice Rockstar (web oficial, Newswire, bios) | Entra | Cierto |
| 2+ medios serios independientes (Forbes, PBS, Mirror, IGN, Infobae…) | Entra | Cierto |
| Estimación de una consultora (Sensor Tower), un estudio con nombre (Remote, BambooHR) | Entra diciendo quién lo estima | Probable |
| Descubrimiento de jugadores visto en 2+ fuentes independientes (YouTube, Instagram, wikis) | Entra con "los jugadores han encontrado…", sin ubicaciones exactas | Probable |
| Una sola fuente, una cuenta de parodia, "dicen que…" sin origen | Fuera | — |
| Leak, datamine, insider | Fuera siempre (además, palabra prohibida) | — |
| Historia/argumento del juego | Fuera (spoiler) | — |

Ejemplos reales ya descartados: el perro en moto de agua (una fuente), "Rubius tiró el huevo
desde la torre" (cuenta de parodia de Threads), la consola PixelShot (una fuente), el fantasma
con mensaje (solo Instagram), "1,5 millones de bajas" (bulo desmentido por PBS: se convirtió en
el Short 18 llevando la contraria).

## Usar vídeos de otros creadores como investigación
Leer su transcripción (`youtube/read`) para ver qué mecánicas o secretos enseñan, contrastarlos
con un análisis serio (GamingTrend, IGN…) y contarlos con nuestra voz e imagen oficial. Nunca
recortar su vídeo. Ejemplo: el gameplay de TheGrefg (IKmDcF0QhBA) dio los Shorts 12–15.

## Señales de qué formato rinde (medidas en nov-2026)
- YouTube Shorts top: 0,3–3M visitas; gancho en el segundo 0; subtítulos 1–2 palabras con color;
  cortes cada 1,75–3,2 s; -14 LUFS.
- TikTok España/LatAm el día de salida: "5 detalles" (450K), detalles de coches (500K),
  "GTA 4 supera a GTA 6 en…" (220K).
- En español casi todo está por debajo de 2.000 visitas: hay hueco, y el ángulo hispano destaca.
Detalle completo en `02-referencias/analisis-virales.md`.
