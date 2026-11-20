# Errores ya vistos: síntoma → causa → arreglo

| Síntoma | Causa | Arreglo |
|---|---|---|
| Subtítulo cortado por los lados ("ESTARÁS DESCARGAN", "MODO RENDIMIENTO") | Bloque de más de 14 caracteres a tamaño 112 | Ya está en el generador (máx. 14). Si sale un bloque largo, `producir.sh` lo marca: reescribe la frase |
| "% EN" suelto en pantalla | "32 %" con espacio: el % pasa al bloque siguiente | Escribir "32%" (el validador lo exige) |
| Subtítulo que parpadea | Huecos de 50–120 ms entre bloques | Ya arreglado (cada bloque dura hasta el siguiente); `verificar-sync.py` cuenta parpadeos |
| Reproductores muestran 1080x1922 o imagen estirada | Píxel no cuadrado (SAR raro del recorte) | `setsar=1` en todos los filtros (ya está). `producir.sh` comprueba `1080,1920,1:1` |
| `verificar-sync.py` da DESFASADO en una palabra larga al final de escena ("helicóptero") | Micropausa dentro de la palabra (consonante oclusiva) que el detector toma por pausa | Casi siempre falsa alarma, pero se entrega en SINCRONIZADO: reformula para que la escena no acabe en esa palabra |
| Rótulos del tráiler ("Follow", "DIRT-BIKE…") pisan el subtítulo | Planos de etiqueta `redes`/`noticias` | Cambiar el plano (ver planos.md) |
| Vídeo de menos de 20 s | Guion corto (menos de ~68 palabras) | Añadir 1–2 frases sin datos nuevos sin fuente |
| Voz que dice mal una palabra | Kokoro lee en inglés o deletrea | En `texto` escríbela como suena ("Ge te a seis", "Rimout", "efe pe ese"); `subtitulo` queda bien escrita |
| En Playwright el vídeo da `error: 3` (decode) y no salta | Copia webm corrupta (VP9 `-deadline realtime` en paralelo) | Rehacer con `-deadline good -cpu-used 4` (ya lo hace `producir.sh`); ffmpeg `-f null` dice si el mp4 está bien |
| `browser_evaluate` se corta a los 60 s | Revisar varios vídeos en una sola llamada | `revisar(n)` de uno en uno |
| `currentTime` no se mueve | Servidor sin soporte de Range | Usar `scripts/servidor_rangos.py` (no `python -m http.server`) |
| Playwright enseña una versión vieja del vídeo | Caché del navegador | La página añade `?Date.now()` a cada archivo; recarga la URL |
| Vídeo negro al final en la captura de Playwright | El navegador no repinta tras el muestreo | No es el archivo: comprobar el brillo del último fotograma con ffmpeg `signalstats` |
| Playwright no arranca | Busca `/opt/google/chrome/chrome`; somos root | `abrir-revision.sh` crea el lanzador con `--no-sandbox` |
| Chromium no reproduce el mp4 | Esta build no trae H.264 | Revisar copias VP9 (webm); el mp4 final no cambia |
| `curl` a rockstargames.com: 403 | Host bloqueado por el proxy | Firecrawl puede leer páginas, no imágenes sueltas; pedir a Aitor que descargue la galería si hace falta |
| Firecrawl `firecrawl_scrape` "not supported" (CNET…) | Sitio no soportado | Usar otra fuente; no reintentar |
| Firecrawl screenshot de una imagen: "engine does not support screenshot" | Firecrawl no captura archivos de imagen | No insistir (gasta créditos) |
| Un plano del catálogo enseña otra persona/toma al final | El tramo cruzaba un corte | Revisar fotogramas inicio/mitad/fin; ajustar `ini`/`fin` |
