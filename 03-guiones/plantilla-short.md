# Plantilla de guion — Short GTA 6 (20–35 s)

Basada en el análisis del 17-nov-2026 de los Shorts y TikToks de GTA 6 con más visitas
(ver `02-referencias/analisis-virales.md`).

## Reglas
- **Segundo 0 = gancho hablado.** Nada de "hola", ni presentación ni música sola. La primera frase ES el título dicho en voz alta
- 0–7 s: **sin violencia gráfica** (si no, el vídeo pierde anuncios)
- 20–35 s en total (~2,7 palabras/s → 55–90 palabras). Frases de 4–10 palabras
- Un tema por Short. En las listas, cada punto empieza por su número ("Uno.", "Dos."…)
- Cierre en una frase corta con pregunta ("¿Equipo Jason o equipo Lucía?"). Sin "suscríbete" al final: hace que la gente se vaya antes
- En pantalla **solo subtítulos abajo**: 1–2 palabras, números y nombres propios en amarillo
- Sin spoilers de la historia. Todo dato, verificado (fuente oficial o 2 medios) antes de escribirlo, y apuntado en `fuentes`
- Porcentajes pegados al número ("32%"); bloques de subtítulo de máx. 14 caracteres (el generador ya los parte)
- `texto` como suena (Ge te a seis, Vais Siti, Yeison, Pléisteishon, Iutub); `subtitulo` como se escribe

## Fórmulas de gancho (de vídeos con 0,3–3M visitas)
| Fórmula | Ejemplo viral (visitas) | Nuestra versión |
|---|---|---|
| Llevar la contraria | "Stop saying GTA 6's map is going to be empty" (3M) | "Deja de pensar que GTA 6 es solo Vice City" |
| Comparar con GTA 5 | "Robbing Stores in GTA 6 Works Differently To GTA 5" (2,2M) | "En GTA 6 esto ya no funciona como en GTA 5" |
| Ventaja / quién juega antes | "Xbox gamers can play GTA 6 early" (2,1M) | "Nueva Zelanda jugará GTA 6 19 horas antes que México" |
| Historia con giro | "I Bought GTA 6's Physical Edition… But There's NO Disc?" (1M) | — (necesita cámara/objeto propio) |
| Lista con urgencia | "5 Things You NEED To Know Before Playing GTA 6 🤯" (520K) | "5 cosas que DEBES saber antes de jugar GTA 6 🤯" |
| Aviso | "Don't Ruin Your First GTA 6 Playthrough" (301K) | "No arruines tu primera partida de GTA 6" |
| Guía práctica (TikTok ES) | "El día que ejecutes GTA 6 por primera vez, haz esto en este orden 👇" (414K) | — |
| Cuenta atrás + noticia (TikTok ES) | "🚨 FALTAN 2 DÍAS PARA GTA 6 🚨 …" (300K) | "FALTA 1 DÍA: …" |
| Ángulo hispano | "Los chistes de GTA 6 que solo pillas si hablas español 😂" (21K en 1 día, canal pequeño) | Buscar detalles que solo entiende un hispanohablante |

## Título, descripción y hashtags
- **Título** (máx. ~60 caracteres, lo importante en los primeros 40): fórmula de gancho + "GTA 6" + 1 emoji al final (🤯 😳 💀 🗺️). Una palabra en MAYÚSCULAS como mucho
- **Descripción**: línea 1 = el gancho ampliado; línea 2 = la pregunta del cierre + 👇; después créditos ("Imágenes: tráileres oficiales de Rockstar Games. Voz sintética.") y 4–5 hashtags
- **Hashtags**: #gta6 #gtavi #vicecity #rockstargames #shorts (+1 del tema)

## Formato JSON (lo lee `herramientas/generar-short.py`)
```json
{
  "titulo": "5 cosas que DEBES saber antes de jugar GTA 6 🤯",
  "gancho": "5 COSAS ANTES DE JUGAR",
  "descripcion": "Línea gancho\n¿Pregunta? 👇\n\nImágenes: …\n\n#gta6 #gtavi #vicecity #rockstargames #shorts",
  "semilla_musica": 1,
  "escenas": [
    {"texto": "Cinco cosas que tienes que saber antes de jugar Ge te a seis.",
     "subtitulo": "Cinco cosas que tienes que saber antes de jugar GTA 6.",
     "planos": ["A17", "A13", "A15"]}
  ],
  "fuentes": [
    {"dato": "Sale el 19 de noviembre a medianoche en PS5 y Xbox Series",
     "fuente": "Rockstar Newswire", "url": "https://www.rockstargames.com/newswire/...", "confianza": "Cierto"}
  ]
}
```
`fuentes` es obligatorio (lo revisa `herramientas/validar-guion.py` antes de generar): cada dato
del guion con su fuente y `confianza` Cierto o Probable. Todo número de los subtítulos debe
aparecer en algún `dato`. Una suposición no se publica.
`gancho` no sale en el vídeo: sirve como texto de portada (miniatura) si se hace una.
