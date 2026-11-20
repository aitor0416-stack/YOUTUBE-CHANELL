# Planos: catálogo, recortes y cómo ampliar

## Catálogo
`02-referencias/planos-trailers.json`: 67 planos de los 3 tráileres oficiales de GTA VI, ya
revisados a mano (sin armas, explosiones, logos ni tomas mezcladas). Cada plano:
`{"id":"A01","src":"t1","ini":2.75,"fin":4.92,"tags":[...],"x":0.5}`. `x` es el centro horizontal
del recorte vertical (0 = izquierda, 1 = derecha). Prefijos: A = Trailer 1, B = Trailer 2,
L = Launch Trailer.

Etiquetas con más planos: humor 14, lucia 11, keys 11, jason 10, coche 9, ciudad 7, carcel 7,
vicecity 7, mar 7, fiesta 6, redes 6, pareja 6, atardecer 5, playa 4, bar 4, pantano 3.

En un guion: id concreto (`"A13"`), `"tag:pantano"` (uno al azar sin repetir) o
`"imagen:archivo.jpg"` de `04-assets/clips-fuente/gta6-oficial/`.

## Cómo elegir
- **Primer plano:** impactante, sin violencia, distinto del de los últimos vídeos (que el canal no
  parezca repetitivo). Ya usados como apertura (guiones 01–23): A13, B37, A06, L04, A04, A17, A15, B19,
  A09, A28, B31, L13, A10, B38, A16, B02, L15, B08, B35, A07. Para saber los actuales:
  `python3 -c "import json,glob;print([json.load(open(f))['escenas'][0]['planos'][0] for f in sorted(glob.glob('03-guiones/[0-9]*.json'))])"`
- **Evitar donde haya texto:** los de etiqueta `redes` (A18, A19, A20, A22, A26, A29) y
  `noticias` (A36) llevan rótulos del propio tráiler ("Follow", "DIRT-BIKE…") que se pisan con el
  subtítulo. Úsalos solo si el tema es justo ese y comprueba la hoja de fotogramas.
- **Que la imagen acompañe a la frase:** pantano → A06, A28, B35; ciudad de noche → A12, A13;
  coches → B02, L15, A39, A31; fiesta → A09, A11, A14, B25, L14, L18; pareja → L08, L16, L25, B23.
- **Repetir un plano:** el generador coge otro momento del mismo plano si una escena es más larga.

## Recortes (franjas negras de los tráileres)
`fuentes` del catálogo: launch `[3840,1920,0,120]`, t1 `[3840,2160,0,0]`, t2 `[3840,1728,0,216]`
(ancho, alto, x, y de la zona con imagen). Si se recorta fuera de esa zona sale una franja negra.

## Añadir planos nuevos (p. ej. del tráiler de GTA V para comparativas)
1. Cortes de escena: `ffmpeg -i video.mp4 -vf "select='gt(scene,0.25)',showinfo" -f null - 2>&1 | grep -o "pts_time:[0-9.]*"`.
2. Hoja de contactos con el tiempo pintado:
   `ffmpeg -i video.mp4 -vf "fps=1,scale=192:108,drawtext=text='%{pts\:hms}':x=2:y=2:fontsize=14:fontcolor=yellow:box=1:boxcolor=black,tile=8x8" -frames:v 1 hoja.png`
   y mírala con Read.
3. Para cada plano candidato, mira fotogramas del inicio, mitad y final (un plano puede mezclar dos
   tomas: pasó con A04, A12 y L28).
4. Añádelo con su `src` (y la fuente en `fuentes` con su recorte si es un vídeo nuevo).
   gtav.mp4 (720p) se ve peor en vertical: úsalo poco y en planos abiertos.
