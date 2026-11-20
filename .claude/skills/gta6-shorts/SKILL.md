---
name: gta6-shorts
description: >-
  Fabrica y revisa Shorts/TikToks verticales de GTA 6 en español para el canal faceless de Aitor:
  investiga qué se está haciendo viral, contrasta cada dato con 2 fuentes, escribe el guion JSON con
  gancho, título, descripción y fuentes, genera el vídeo (voz Kokoro, planos de tráileres oficiales,
  subtítulos abajo, música propia) y lo verifica (sincronía, fotogramas, Playwright) antes de entregar.
  Úsala SIEMPRE que se pida en este repo "hazme shorts", "más vídeos", "clips", "curiosidades",
  "noticias de GTA 6", "sube a TikTok", "mejora el vídeo", un guion, un título o una descripción,
  aunque no se nombre la skill. También para decidir si un material ajeno (gameplay de un streamer,
  vídeo de otro canal) se puede usar, y para preguntas de monetización de YouTube/TikTok del canal.
---

# Shorts de GTA 6 en español

Esta skill es el método completo del canal, con lo aprendido produciendo los Shorts 01–23
(nov-2026). Las herramientas ya existen en el repo; la skill dice en qué orden usarlas, qué
comprobar y por qué. El estado del canal y las decisiones de Aitor están en `CLAUDE.md`: léelo
antes de empezar, porque manda sobre esta skill si se contradicen.

## Las reglas que no se negocian (y por qué)

| Regla | Por qué |
|---|---|
| Imagen: gameplay propio de Aitor > tráileres oficiales de Rockstar. **Nunca** clips de otros youtubers/streamers, aunque "se los vea muchos hacerlo" | Content ID reclama o bloquea el vídeo, 3 avisos de copyright cierran el canal y YouTube niega la monetización por "contenido reutilizado". Lo de otros sirve como **investigación** (qué temas funcionan), nunca como material |
| Cada dato, contrastado en **2 fuentes** (o 1 oficial de Rockstar) y apuntado en `fuentes` del guion | Un dato falso en un canal pequeño se come los comentarios y la credibilidad. Las cuentas de parodia (ej. Threads "fullstackparody") y lo que solo dice una persona se descartan |
| Sin spoilers de historia, sin leaks | Rockstar retira ese contenido y la gente lo castiga |
| Sin violencia en los primeros 7 s (texto e imagen) | Regla de anuncios de YouTube (sept-2026): si no, el vídeo pierde anuncios |
| En pantalla **solo subtítulos abajo** (1–2 palabras, máx. 14 caracteres) | Lo pidió Aitor; los Shorts que funcionan lo hacen así; con más de 14 caracteres se cortan por los lados |
| Gancho **dicho en el segundo 0** y = título | Es lo único común a todos los Shorts virales medidos (0,3–3M visitas) |
| 20–35 s | Rango de los virales medidos; por debajo de 20 s el algoritmo apenas lo empuja |
| Presupuesto 0 € | Decisión de Aitor: nada de herramientas de pago (ni plantillas tipo "Pro Pack") |

Si Aitor pide saltarse una regla (p. ej. "coge clips de TheGrefg"), no lo hagas: explica en una
frase el riesgo concreto y ofrece la alternativa que sí funciona (usar el vídeo como investigación
y montar el Short con material oficial). Es un asesor que quiere que le digan la verdad incómoda.

## Flujo de trabajo

### 0. Sesión nueva: dejar el entorno listo
El contenedor cloud se borra entre sesiones. Comprueba y, si falta algo, sigue
`references/entorno.md` (voz, tráileres 4K, Chromium para Playwright). Tarda unos minutos y
sin eso nada se genera.

### 1. Investigar qué funciona hoy
Con Firecrawl (gasta créditos: avisa a Aitor de cuántos aproximadamente). Recetas exactas en
`references/investigacion.md`: noticias del día, TikTok/YouTube más vistos, leer un vídeo
(transcripción) sin descargarlo. Busca temas, no material: el valor está en el ángulo.
Lo que más rinde para este canal, por orden: ángulo hispano (Bad Bunny en la radio, España en el
top de algo), comparación con GTA 5, llevar la contraria / desmentir un bulo, listas ("4 secretos"),
avisos ("cuidado al…"), noticia del día.

### 2. Contrastar
Cada dato: ¿lo dicen 2 fuentes independientes o Rockstar? Si no, fuera, o se dice con cautela
("según cuentan") y confianza `Probable`. Nunca se publica una suposición.

### 3. Escribir el guion
Formato, fórmulas de gancho, fonética y reglas de título/descripción en
`03-guiones/plantilla-short.md`. Lo esencial:
- `texto` como suena ("Ge te a seis", "Vais Siti", "Pléisteishon"), `subtitulo` como se escribe.
- Porcentajes pegados: "32%".
- `fuentes`: lista de `{dato, fuente, url?, confianza}`. Todo número de los subtítulos tiene que
  aparecer en algún `dato` (el validador lo exige).
- Planos: ids de `02-referencias/planos-trailers.json`. Primer plano distinto al de los últimos
  vídeos; sin planos con etiqueta `redes`/`noticias` donde vaya texto (sus rótulos tapan los
  subtítulos). Catálogo y recortes en `references/planos.md`.
- Unas 68–100 palabras de `texto` (3,4 palabras/s ≈ 20–30 s).

### 4. Generar y comprobar en un paso
```bash
herramientas/producir.sh 03-guiones/24-algo.json 03-guiones/25-otro.json
```
Revisa el guion (`validar-guion.py`: título, descripción, fuentes, palabras prohibidas, planos),
genera, comprueba la sincronía (`verificar-sync.py`), busca bloques largos, hace hojas de
fotogramas y copias para el navegador. Si dice REVISAR o NO GENERADO, se arregla antes de seguir.
Si un vídeo queda por debajo de 20 s, añade una frase que no meta datos nuevos sin fuente.

### 5. Mirar las hojas de fotogramas (Read sobre la imagen)
`producir.sh` las deja en `<REVISION_DIR>/hojas/`. Busca: rótulos del tráiler compitiendo con el
subtítulo, palabras cortadas, violencia o armas en los primeros 7 s, aperturas repetidas,
"%" o números sueltos en un bloque. Si algo falla: cambia planos o texto y vuelve al paso 4.

### 6. Revisar en el navegador con Playwright
```bash
.claude/skills/gta6-shorts/scripts/abrir-revision.sh 24-algo 25-otro   # imprime la URL
```
Abre la URL con `browser_navigate` y llama `revisar("<nombre>")` con `browser_evaluate`
**una vez por vídeo** (cada evaluate se corta a los 60 s). Bien = `error: null`, 1080x1920,
`vacias: 0`, `saltos_fallidos: 0`. Para comparar texto quemado vs pista, `irA(n, seg)` +
captura (guárdala en `.playwright-mcp/` y bórrala después). Fallos ya vistos y su arreglo:
`references/errores-conocidos.md`.

### 7. Entregar
- `SendUserFile` con los `.mp4` y sus `.srt` (display `attach`).
- Mensaje a Aitor: primero lo incómodo (qué no se pudo hacer, qué dato es más flojo), luego tabla
  título / fórmula / confianza, comprobaciones con sus números reales, orden de publicación si
  hay noticias que caducan, créditos de Firecrawl gastados. Marca la confianza (Cierto / Probable /
  Suposición). En español, sin rodeos.
- Añade una línea al apartado "Estado" de `CLAUDE.md` (qué se hizo, fuentes clave, lecciones) y
  haz commit + push a `main` (Aitor trabaja así; el hook de parada lo pide).

## Preguntas que se repiten
- **"¿Me renta TikTok?"** Para crecer sí; para cobrar desde España no: Creator Rewards solo existe
  en EE. UU., UK, Alemania, Japón, Corea, Francia, México y Brasil, pide 10K seguidores, 100K
  vistas/30 días y vídeos ≥1 min 100 % originales (TikTok Creator Academy, sept-2026). Recomendar
  subir el mismo archivo a TikTok, Shorts y Reels (sin marca de agua de otra red) y monetizar vía
  YouTube (1.000 subs + 10M vistas/90 días; 20M desde 1-feb-2027).
- **"Coge clips de X / haz clipping"** → regla 1. Clipping legal = con permiso o programa de pago
  del creador.
- **"¿Es segura esta skill/herramienta?"** → clonar en el scratchpad sin ejecutar, leer los
  scripts enteros, grep de patrones (red, borrados, ofuscación, instrucciones ocultas, ventas) y
  valorar coste/encaje con 0 € y español.

## Referencias (léelas cuando toque)
- `references/entorno.md` — montar la sesión desde cero.
- `references/investigacion.md` — recetas de Firecrawl y cómo contrastar.
- `references/planos.md` — catálogo de planos, recortes de los tráileres y cómo añadir planos.
- `references/errores-conocidos.md` — síntoma → causa → arreglo de todo lo que ya falló.
- `03-guiones/plantilla-short.md` — formato del guion y fórmulas de gancho.
- `02-referencias/analisis-virales.md` — qué se midió en los virales.
- `02-referencias/palabras-prohibidas.txt` — lista que usa el validador (añade palabras ahí).
