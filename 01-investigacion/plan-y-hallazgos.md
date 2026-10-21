# Canal YouTube faceless ES — hallazgos y plan

Fecha: 2026-10-21 · Leyenda de confianza: **Cierto** / **Probable** / **Suposición**

## 1. Lo que cambia el plan (leer primero)

| # | Hallazgo | Confianza | Consecuencia |
|---|----------|-----------|--------------|
| 1 | Traducir el guion de otro youtuber = obra derivada. Necesita permiso del autor | Cierto (Copyright Office EE.UU.) | NO traducimos transcripciones. Copiamos **formato, estructura y temas** (las ideas no tienen copyright) y escribimos guion propio con varias fuentes |
| 2 | Política "inauthentic content" (jul-2025): YouTube desmonetiza canales con contenido en serie, plantillas genéricas, sin aporte propio. Se evalúa **el canal entero**, no un vídeo | Cierto | Cada vídeo necesita investigación, opinión/ángulo propio y edición variada. Nada de "pipeline sin humano" |
| 3 | Desde el **1-feb-2027** los canales nuevos necesitan **8.000 h** de visualización (antes 4.000) o 20M vistas de Shorts + 1.000 subs | Probable (varias fuentes de prensa, no he leído el post oficial) | Con canal desde cero no llegamos a 4.000 h antes de febrero. Planificar para 8.000 h |
| 4 | RPM España ≈ 2 $ media, finanzas ≈ 3,3 $. EE.UU. finanzas ≈ 5–30 $ | Probable (webs de herramientas, sin metodología pública) | La misma vista vale 3–8x menos en español. AdSense solo no basta: hay que sumar afiliados/patrocinios desde el inicio |
| 5 | El público en español es España + LATAM. LATAM paga aún menos por vista pero da mucho volumen | Probable | Decidir si escribimos para España o para todo el mundo hispano (cambia ejemplos, moneda, acento de voz) |

### Cálculo rápido de las 8.000 h
8.000 h = 480.000 min. Con vídeos de ~12 min y ~4 min vistos de media → **~120.000 vistas en 12 meses** solo para entrar. Es alcanzable con 1–2 vídeos/semana si 2–3 vídeos funcionan, pero no es rápido. (Suposición sobre retención)

## 2. Nichos candidatos (para validar con datos, no decidido)

Criterio: alto RPM + formato faceless probado en EE.UU. + poca oferta de calidad en español.

| Nicho | Referencias EE.UU. (faceless) | RPM ES | Competencia ES | Riesgo |
|---|---|---|---|---|
| Documentales de negocio / historias de empresas | Business Casual, Company Man, Modern MBA | medio-alto (anunciantes de finanzas) | Suposición: baja en calidad visual | Bajo. Evergreen |
| Finanzas personales explicadas | Alux.com, The Swedish Investor | el más alto de ES (~3,3 $) | Alta en España (muchos con cara) | Medio: consejo financiero → más exigencia de YouTube con temas "Your Money Your Life" |
| Historias de traición/venganza narradas | Revenge With Jake, Stories of Retaliation | bajo-medio | Suposición: media | **Alto**: es justo el formato que YouTube está desmonetizando como "AI slop" |
| Explicadores de IA/tecnología | varios | medio | media | Medio: se queda antiguo rápido |

**Mi recomendación provisional:** documentales de negocio (historias de empresas, quiebras, fortunas). Junta RPM de finanzas, formato que admite mucha IA visual sin parecer plantilla, y encaja con tu perfil LEINN. A validar en la tarea 1.

## 3. Stack a 0 € (decidido 2026-10-21)

| Pieza | Herramienta | Coste | Nota |
|---|---|---|---|
| Investigación de canales | vidIQ free / ViewStats / YouTube Data API (gratis con API key) | 0 € | |
| Transcripciones de referencia | yt-dlp (subtítulos auto) | 0 € | Solo para analizar estructura, no para traducir |
| Guion | Claude (aquí) | 0 € | |
| Voz | **Voz de Aitor** grabada con el móvil + `herramientas/limpiar-voz.sh` | 0 € | Protege contra "inauthentic content" |
| Imágenes | ChatGPT free / Gemini free (límite diario) + Pexels/Pixabay (fotos y vídeo de stock gratis, uso comercial) | 0 € | Revisar términos de uso comercial de cada generador antes de publicar |
| Edición | DaVinci Resolve free (exporta hasta 4K) o CapCut free (más fácil, revisar marca de agua) | 0 € | |
| Miniaturas | Canva free + imagen IA | 0 € | |
| **Total** | | **0 €** | Primer gasto cuando haya tracción: ElevenLabs no hace falta; mejor ChatGPT Plus (~20 $) para imágenes |

Límite real del stack gratis: los límites diarios de imágenes. Con 1 vídeo/semana y ~30–40 imágenes por vídeo hay que repartir la generación entre varios días y herramientas (Suposición: límites exactos cambian y las fuentes no coinciden).

## 3b. Decisiones tomadas
- Mercado: **todo el mundo hispano** (España + LATAM). Español neutro, ejemplos de varios países, cifras en dólares cuando aplique.
- Voz: la de Aitor. Claude prepara el guion para leer en voz alta y limpia el audio con ffmpeg.
- Presupuesto: 0 € al inicio, ir subiendo.
- Tiempo: horas sueltas + fines de semana → ritmo realista **1 vídeo largo/semana + 2–3 Shorts sacados del mismo vídeo**.

## 4. Tareas por fases

**Fase 0 — Decisiones (tú)**
- [x] Mercado: todo hispano
- [x] Voz: propia
- [x] Presupuesto 0 € · horas sueltas + finde
- [ ] Crear repo GitHub privado `canal-youtube-es` (Aitor) y subir el proyecto (Claude)
- [ ] Grabar 1 min de prueba con el móvil para ajustar `limpiar-voz.sh` a tu voz y tu cuarto

**Fase 1 — Validar nicho (1 semana)**
- [ ] Sacar 10–15 canales faceless EE.UU. por nicho candidato: subs, vistas medias, vídeos "outlier" (vídeo con 3x+ las vistas medias del canal)
- [ ] Buscar equivalentes en español: cuántos hay, calidad, vistas
- [ ] Elegir 1 nicho + 2–3 canales "modelo"

**Fase 2 — Diseño del canal**
- [ ] Nombre, identidad visual, estilo de imágenes fijo, tono de voz
- [ ] Plantilla de guion (gancho 0–30 s, estructura, cierre) sacada del análisis de los canales modelo
- [ ] Lista de 20 temas: los outliers de EE.UU. adaptados + temas propios del mundo hispano

**Fase 3 — Producción piloto (3 vídeos)**
- [ ] Guion → voz → imágenes → edición → miniatura → SEO (título, descripción)
- [ ] Medir tiempo y coste real por vídeo

**Fase 4 — Publicar y medir**
- [ ] 1–2 vídeos/semana. Revisar CTR de miniatura y retención a los 30 s
- [ ] Afiliados/patrocinios desde ~1.000 subs, sin esperar a YPP

## Fuentes
- https://air.io/en/news-air/how-youtube-treats-ai-in-2026-new-update
- https://www.subsub.io/blog/inauthentic-content-why-so-many-creators-are-getting-demonetized
- https://metricool.com/youtube-partner-program-2027-changes/
- https://www.shacknews.com/article/150324/youtube-partner-program-minimum-qualified-public-watch-hours-shorts-views
- https://tubeanalytics.net/benchmarks/spain
- https://www.collabpals.com/tools/youtube-revenue-per-view-calculator
- https://www.flipflow.io/en/?p=21895
- https://blogs.loc.gov/copyright/2022/10/copyright-in-translation-gregory-rabassa/
- https://www.clipspeed.ai/blog/faceless-youtube-niches-2026.html
- https://smallest.ai/blog/elevenlabs-pricing-plans-cost-what-you-get-in-2026
