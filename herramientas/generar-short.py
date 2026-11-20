#!/usr/bin/env python3
"""Genera un Short vertical (1080x1920) dinámico a partir de un guion JSON.

Uso:
  python generar-short.py guion.json salida.mp4

Cada escena = una frase de voz + varios planos que se van cortando mientras habla.
En pantalla solo hay subtítulos abajo (1-2 palabras, la que suena hace "pop";
números y nombres propios en amarillo). El gancho se DICE en el segundo 0.
Guion (ver 03-guiones/*.json):
{
  "titulo": "...", "descripcion": "...",     # para publicar (ver 03-guiones/plantilla-short.md)
  "semilla_musica": 1,                       # cambia la base musical
  "escenas": [
    {"texto": "como suena (para la voz)", "subtitulo": "como se escribe",
     "planos": ["A17", "tag:vicecity", "imagen:lucia.jpg"],
     "corte": 1.6}                           # opcional: segundos por plano
  ]
}
Planos: id del catálogo 02-referencias/planos-trailers.json, "tag:<etiqueta>" (elige uno al azar
sin repetir) o "imagen:<archivo>" de 04-assets/clips-fuente/gta6-oficial.

Variables de entorno:
  VOZ_MOTOR        kokoro (por defecto) | coqui
  KOKORO_DIR       carpeta con kokoro-v1.0.onnx y voices-v1.0.bin; KOKORO_VOZ (em_santa por defecto)
  COQUI_MODEL_DIR  carpeta del modelo Coqui (si VOZ_MOTOR=coqui)
  TRAILERS_DIR     carpeta con launch.mp4, t1.mp4, t2.mp4 (tráileres oficiales en 4K)
  VOZ_REFERENCIA   opcional: wav de la voz de Aitor → la voz se convierte a su timbre (FreeVC)
  FREEVC_DIR       carpeta del modelo FreeVC (necesaria con VOZ_REFERENCIA)
  SIN_VALIDAR=1    salta la revisión previa del guion (herramientas/validar-guion.py); solo para pruebas
"""
import json
import os
import random
import re
import subprocess
import sys
import tempfile
import wave

W, H, FPS = 1080, 1920, 30
FUENTE = "DejaVu Sans"
PAUSA = 0.10        # silencio tras cada frase (s)
TEMPO_VOZ = 1.0     # Kokoro ya va a velocidad 1.12; Coqui necesita 1.10
CORTE_GANCHO = 1.1  # segundos por plano en la primera escena
CORTE = 1.7         # segundos por plano en el resto
SUB_Y = int(H * 0.73)  # altura de los subtítulos: abajo, pero por encima del título/botones de Shorts
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# palabras que se pintan en amarillo además de las que llevan números
DESTACAR = {"GTA", "LUCÍA", "JASON", "VICE", "CITY", "LEONIDA", "ROCKSTAR", "PS5", "XBOX", "PC", "GB",
            "MIAMI", "FLORIDA", "ESPAÑA", "MÉXICO", "ARGENTINA", "CHILE", "URUGUAY", "ZELANDA", "CÁRCEL",
            "RÉCORD", "KEYS", "GRASSRIVERS", "GELLHORN", "AMBROSIA", "KALAGA", "YOUTUBE", "NUNCA", "NADIE"}


def sh(*args):
    r = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if r.returncode:
        sys.exit(f"Error en: {' '.join(args)[:300]}\n{r.stderr[-1500:]}")


def duracion_wav(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


# ---------- voz ----------

def sintetizar(escenas, tmp):
    motor = os.environ.get("VOZ_MOTOR", "kokoro")
    if motor == "kokoro":
        import soundfile as sf
        from kokoro_onnx import Kokoro
        d = os.environ["KOKORO_DIR"]
        k = Kokoro(os.path.join(d, "kokoro-v1.0.onnx"), os.path.join(d, "voices-v1.0.bin"))
        voz = os.environ.get("KOKORO_VOZ", "em_santa")

        def decir(texto, ruta):
            s, sr = k.create(texto, voice=voz, speed=1.12, lang="es")
            sf.write(ruta, s, sr)
        tempo = TEMPO_VOZ
    else:
        from TTS.api import TTS
        d = os.environ["COQUI_MODEL_DIR"]
        tts = TTS(model_path=os.path.join(d, "model_file.pth"),
                  config_path=os.path.join(d, "config.json"), progress_bar=False)

        def decir(texto, ruta):
            tts.tts_to_file(text=texto, file_path=ruta)
        tempo = 1.10

    ref = os.environ.get("VOZ_REFERENCIA")
    vc = None
    if ref:
        # FreeVC: cambia el timbre al de la grabación de referencia (WavLM-Large.pt en ~/.local/share/tts/)
        from TTS.utils.synthesizer import Synthesizer
        fv = os.environ["FREEVC_DIR"]
        vc = Synthesizer(vc_checkpoint=os.path.join(fv, "model.pth"), vc_config=os.path.join(fv, "config.json"))
    rutas = []
    for i, e in enumerate(escenas):
        crudo = os.path.join(tmp, f"voz{i}_raw.wav")
        decir(e["texto"].replace("…", ","), crudo)
        if vc:
            convertido = os.path.join(tmp, f"voz{i}_vc.wav")
            vc.save_wav(vc.voice_conversion(source_wav=crudo, target_wav=ref), convertido)
            crudo = convertido
        limpio = os.path.join(tmp, f"voz{i}.wav")
        sh("ffmpeg", "-y", "-i", crudo, "-af",
           "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
           "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
           f"atempo={tempo},highpass=f=70,"
           # un poco de "presencia" (2-4 kHz) y compresión: voz más cercana y con pegada
           "equalizer=f=3000:t=q:w=1.2:g=3,equalizer=f=180:t=q:w=1:g=2,"
           "acompressor=threshold=-20dB:ratio=3.5:attack=4:release=100:makeup=2,"
           f"apad=pad_dur={PAUSA}", "-ar", "48000", "-ac", "1", limpio)
        rutas.append(limpio)
    return rutas


def pausas_internas(wav, dur):
    """Micropausas de la voz (≥45 ms): casi siempre caen entre dos palabras. Son las anclas de sincronía."""
    r = subprocess.run(["ffmpeg", "-i", wav, "-af", "silencedetect=noise=-35dB:d=0.045", "-f", "null", "-"],
                       capture_output=True, text=True)
    ini = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r.stderr)]
    fin = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r.stderr)]
    return [(a, b) for a, b in zip(ini, fin) if 0.08 < a < dur - PAUSA - 0.08]


def silabas(palabra):
    """Aproximación de sílabas en español: grupos de vocales (los números cuentan como palabras largas)."""
    if re.search(r"\d", palabra):
        return 2 + len(re.sub(r"\D", "", palabra))
    return max(1, len(re.findall(r"[aeiouáéíóúü]+", palabra.lower())))


def tiempos_palabras(palabras, dur, wav):
    """Alineación sin reconocimiento de voz:
    1) estima dónde acaba cada palabra repartiendo la frase por sílabas (las pausas de puntuación pesan más);
    2) cada micropausa real del audio se 'engancha' al límite entre palabras estimado más cercano (±0,35 s),
       en orden y sin cruzarse;
    3) entre anclas, vuelve a repartir por sílabas. Devuelve [(ini, fin)] por palabra."""
    hablado = dur - PAUSA
    n = len(palabras)
    peso = [silabas(p) + (1.5 if re.search(r"[.,:;?!]$", p) else 0) for p in palabras]
    tot = sum(peso)
    estim, acc = [], 0.0
    for w_ in peso[:-1]:
        acc += w_
        estim.append(hablado * acc / tot)          # límite estimado tras la palabra k
    pausas = pausas_internas(wav, dur)
    anclas = {}
    # 1.º los finales de frase/coma: se enganchan a la pausa MÁS LARGA cercana (±0,45 s)
    for k in range(n - 1):
        if not re.search(r"[.,:;?!]$", palabras[k]):
            continue
        cand = [(b - a, (a, b)) for a, b in pausas if abs(estim[k] - (a + b) / 2) < 0.45
                and (a, b) not in anclas.values()]
        if cand:
            anclas[k] = max(cand)[1]
    # 2.º el resto de micropausas, a los límites entre palabras más cercanos sin cruzar anclas (±0,35 s)
    for a, b in pausas:
        if (a, b) in anclas.values():
            continue
        m = (a + b) / 2
        antes = max([k for k, (pa, _) in anclas.items() if pa < a], default=-1)
        despues = min([k for k, (pa, _) in anclas.items() if pa > a], default=n - 1)
        cand = [(abs(estim[k] - m), k) for k in range(antes + 1, despues) if k not in anclas and abs(estim[k] - m) < 0.35]
        if cand:
            anclas[min(cand)[1]] = (a, b)
    # seguridad: las anclas deben avanzar en el tiempo al avanzar las palabras
    limpias, ultimo = {}, -1.0
    for k, (a, b) in sorted(anclas.items()):
        if a > ultimo:
            limpias[k] = (a, b)
            ultimo = b
    anclas = limpias
    # tramos entre anclas
    res = [None] * n
    ini_palabra, t_ini = 0, 0.0
    for k in sorted(anclas) + [n - 1]:
        fin_tramo = anclas[k][0] if k in anclas else hablado
        sil = peso[ini_palabra:k + 1]
        s_tot = sum(sil) or 1
        t = t_ini
        for j, s in enumerate(sil):
            d = (fin_tramo - t_ini) * s / s_tot
            res[ini_palabra + j] = (t, t + d)
            t += d
        if k in anclas:
            ini_palabra, t_ini = k + 1, anclas[k][1]
    return res


# ---------- planos ----------

def cargar_catalogo():
    with open(os.path.join(RAIZ, "02-referencias", "planos-trailers.json"), encoding="utf-8") as f:
        cat = json.load(f)
    return cat["fuentes"], {p["id"]: p for p in cat["planos"]}


def resolver_planos(escenas, planos, semilla):
    rnd = random.Random(semilla)
    usados = set()
    for e in escenas:
        lista = []
        for p in e["planos"]:
            if p.startswith("tag:"):
                cand = [k for k, v in planos.items() if p[4:] in v["tags"] and k not in usados]
                cand = cand or [k for k, v in planos.items() if p[4:] in v["tags"]]
                if not cand:
                    sys.exit(f"No hay planos con la etiqueta {p[4:]}")
                p = rnd.choice(sorted(cand))
            usados.add(p)
            lista.append(p)
        e["_planos"] = lista


def segmento_trailer(p, fuentes, dur, salida, i, offset):
    """Recorte vertical del tráiler 4K + zoom. El primer plano entra con zoom hacia fuera (golpe visual)."""
    fw, fh, fx, fy = fuentes[p["src"]]["crop"]
    vw = int(fh * 9 / 16) // 2 * 2
    cx = int(fx + p["x"] * fw - vw / 2)
    cx = max(fx, min(cx, fx + fw - vw))
    largo = p["fin"] - p["ini"]
    ini = p["ini"] + min(offset, max(0, largo - dur))
    lento = max(1.0, min(2.0, dur / max(largo, 0.1)))  # plano corto → cámara lenta (máx. 2x)
    if i == 0:
        zoom = f"{W}*(1.22-0.22*min(t/0.45\\,1))"  # entra a 122 % y se asienta en 0,45 s
    else:
        z = 0.06 if i % 2 == 0 else 0.10
        zoom = f"{W}*(1+{z}*t/{dur:.3f})"
    vf = (f"crop={vw}:{fh}:{cx}:{fy},setpts={lento:.3f}*PTS,"
          f"scale={W}:{H},"
          f"scale=w='{zoom}':h=-2:eval=frame,crop={W}:{H},"
          "eq=contrast=1.07:saturation=1.2,fps=30,setsar=1,format=yuv420p")
    trailer = os.path.join(os.environ["TRAILERS_DIR"], p["src"] + ".mp4")
    sh("ffmpeg", "-y", "-ss", f"{ini:.3f}", "-i", trailer, "-t", f"{dur:.3f}", "-an", "-vf", vf,
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", salida)


def segmento_imagen(img, dur, salida, i):
    frames = int(round(dur * FPS))
    vf = (f"split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"gblur=sigma=40,eq=brightness=-0.15[fondo];"
          f"[b]scale={W - 80}:-2,scale=w='({W - 80})*(1+0.08*t/{dur:.3f})':h=-2:eval=frame[frente];"
          f"[fondo][frente]overlay=(W-w)/2:(H-h)/2-{int(H * 0.05)}:shortest=1,setsar=1,format=yuv420p")
    sh("ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", img, "-filter_complex", vf,
       "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", salida)


# ---------- subtítulos ----------

def t_ass(t):
    h, r = divmod(max(t, 0), 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def destacada(w):
    limpia = re.sub(r"[^\wÁÉÍÓÚÑÜáéíóúñü$]", "", w).upper()
    return bool(re.search(r"\d", w)) or limpia in DESTACAR


def construir_ass(escenas, duraciones, voces, path, srt_path):
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{FUENTE},112,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,9,5,5,40,40,0,1
Style: Caja,{FUENTE},10,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev, srt, todos = [], [], []
    pop =r"\fscx78\fscy78\t(0,80,\fscx108\fscy108)\t(80,150,\fscx100\fscy100)"
    amarillo, blanco = r"\c&H00E6FF&", r"\c&HFFFFFF&"
    t0 = 0.0
    for idx, (e, dur, wav) in enumerate(zip(escenas, duraciones, voces)):
        if idx > 0:  # destello suave al cambiar de punto (no es texto)
            ev.append(f"Dialogue: 5,{t_ass(t0)},{t_ass(t0 + 0.14)},Caja,,0,0,0,,"
                      f"{{\\an7\\pos(0,0)\\1a&H70&\\fad(0,130)\\p1}}m 0 0 l {W} 0 {W} {H} 0 {H}{{\\p0}}")
        palabras = (e.get("subtitulo") or e["texto"]).split()
        tiempos = [(t0 + a, t0 + b) for a, b in tiempos_palabras(palabras, dur, wav)]
        # bloques de 1-2 palabras: palabras largas o con puntuación van solas
        bloques, act = [], []
        es_num = lambda w: bool(re.match(r"^\d", w))  # noqa: E731
        for k, p in enumerate(palabras):
            sig = palabras[k + 1] if k + 1 < len(palabras) else ""
            # "GTA" + su número van juntos; nunca dos números seguidos en el mismo subtítulo
            if act and es_num(p) and es_num(palabras[act[-1]]):
                bloques.append(act)
                act = []
            # a tamaño 112 caben ~14 caracteres en 1080 px: si no caben juntas, cada una en su bloque
            if act and len(" ".join(palabras[j] for j in act + [k])) > 14:
                bloques.append(act)
                act = []
            act.append(k)
            if p.upper() == "GTA" and es_num(sig):
                continue
            if len(act) >= 2 or len(p) >= 8 or re.search(r"[.,:;?!]$", p) or (es_num(p) and es_num(sig)):
                bloques.append(act)
                act = []
        if act:
            bloques.append(act)
        for b in bloques:
            todos.append(([palabras[k] for k in b], [tiempos[k] for k in b]))
        t0 += dur
    # sin parpadeos: cada palabra/bloque se queda en pantalla hasta que entra el siguiente
    # (si el hueco es una micropausa; en un silencio largo, >0,5 s, sí se apaga)
    for i, (pals, ts) in enumerate(todos):
        sig = todos[i + 1][1][0][0] if i + 1 < len(todos) else None
        fin_bloque = sig if sig is not None and sig - ts[-1][1] < 0.5 else ts[-1][1]
        srt.append((ts[0][0], fin_bloque, " ".join(pals)))
        for j in range(len(pals)):
            ini = ts[j][0]
            fin = ts[j + 1][0] if j + 1 < len(pals) else fin_bloque
            partes = []
            for jj, w_ in enumerate(pals):
                w_ = w_.upper()
                color = amarillo if destacada(w_) else blanco
                if jj == j:
                    partes.append("{" + color + r"\fscx106\fscy106}" + w_ + "{" + blanco + r"\fscx100\fscy100}")
                else:
                    partes.append("{" + color + "}" + w_ + "{" + blanco + "}")
            efecto = pop if j == 0 else ""
            ev.append(f"Dialogue: 1,{t_ass(ini)},{t_ass(fin)},Sub,,0,0,0,,"
                      f"{{\\pos({W // 2},{SUB_Y}){efecto}}}{' '.join(partes)}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(cab + "\n".join(ev) + "\n")
    # SRT aparte: sirve para subir subtítulos a YouTube/TikTok y para comprobar la sincronía
    with open(srt_path, "w", encoding="utf-8") as f:
        for n, (a, b, txt) in enumerate(srt, 1):
            fa = f"{int(a // 3600):02d}:{int(a % 3600 // 60):02d}:{a % 60:06.3f}".replace(".", ",")
            fb = f"{int(b // 3600):02d}:{int(b % 3600 // 60):02d}:{b % 60:06.3f}".replace(".", ",")
            f.write(f"{n}\n{fa} --> {fb}\n{txt}\n\n")


# ---------- principal ----------

def validar_antes(guion_path):
    """Pasa herramientas/validar-guion.py: si el guion tiene fallos (sin fuentes, palabra prohibida,
    plano inexistente...) no se gasta tiempo en generar. SIN_VALIDAR=1 lo salta (solo para pruebas)."""
    if os.environ.get("SIN_VALIDAR"):
        return
    r = subprocess.run([sys.executable, os.path.join(RAIZ, "herramientas", "validar-guion.py"), guion_path],
                       capture_output=True, text=True)
    print(r.stdout.strip())
    if r.returncode:
        sys.exit("El guion no pasa la revisión: corrige los FALLOS de arriba antes de generar.")


def main():
    guion_path, salida = sys.argv[1], sys.argv[2]
    validar_antes(guion_path)
    with open(guion_path, encoding="utf-8") as f:
        g = json.load(f)
    escenas = g["escenas"]
    semilla = g.get("semilla_musica", 1)
    fuentes, planos = cargar_catalogo()
    resolver_planos(escenas, planos, semilla)
    img_dir = os.path.join(RAIZ, "04-assets", "clips-fuente", "gta6-oficial")

    with tempfile.TemporaryDirectory() as tmp:
        voces = sintetizar(escenas, tmp)
        duraciones = [duracion_wav(v) for v in voces]
        total = sum(duraciones)

        segs, n = [], 0
        for idx, (e, dur) in enumerate(zip(escenas, duraciones)):
            corte = e.get("corte", CORTE_GANCHO if idx == 0 else CORTE)
            partes = max(1, round(dur / corte))
            lista = e["_planos"]
            for k in range(partes):
                d = dur / partes
                p = lista[k % len(lista)]
                vuelta = k // len(lista)  # si se repite el plano, otro momento del mismo
                out = os.path.join(tmp, f"seg{n:03d}.mp4")
                if p.startswith("imagen:"):
                    segmento_imagen(os.path.join(img_dir, p[7:]), d, out, n)
                else:
                    segmento_trailer(planos[p], fuentes, d, out, n, offset=vuelta * d)
                segs.append(out)
                n += 1

        lista_txt = os.path.join(tmp, "segs.txt")
        with open(lista_txt, "w") as f:
            f.writelines(f"file '{s}'\n" for s in segs)
        video = os.path.join(tmp, "video.mp4")
        sh("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", lista_txt, "-c", "copy", video)
        voces_txt = os.path.join(tmp, "voces.txt")
        with open(voces_txt, "w") as f:
            f.writelines(f"file '{v}'\n" for v in voces)
        voz = os.path.join(tmp, "voz.wav")
        sh("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", voces_txt, voz)
        if os.environ.get("GUARDAR_VOZ"):  # para comprobar la sincronía (herramientas/verificar-sync.py)
            sh("ffmpeg", "-y", "-i", voz, os.path.splitext(salida)[0] + ".voz.wav")

        musica = os.path.join(tmp, "musica.wav")
        sh(sys.executable, os.path.join(RAIZ, "herramientas", "musica.py"), musica, f"{total + 1:.1f}", str(semilla))

        ass = os.path.join(tmp, "subs.ass")
        construir_ass(escenas, duraciones, voces, ass, os.path.splitext(salida)[0] + ".srt")

        # audio: voz a -14 LUFS, música que se aparta cuando hay voz, golpe de bajo en el segundo 0
        # y whoosh en cada cambio de punto
        cambios, t = [], 0.0
        for d in duraciones[:-1]:
            t += d
            cambios.append(t)
        fa = ("[1:a]loudnorm=I=-14:TP=-1.5:LRA=9,asplit[voz][llave];"
              "[2:a]volume=0.22,aformat=channel_layouts=stereo[mus];"
              "[mus][llave]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=350[musd];"
              "[3:a]volume=0.9[golpe]")
        mezcla = ["[voz]", "[musd]", "[golpe]"]
        if cambios:
            fa += (";[4:a]highpass=f=500,lowpass=f=6000,afade=t=in:d=0.15,afade=t=out:st=0.15:d=0.25,"
                   f"volume=0.22,asplit={len(cambios)}" + "".join(f"[w{i}]" for i in range(len(cambios))))
            for i, c in enumerate(cambios):
                ms_ = int(max(0, c - 0.18) * 1000)
                fa += f";[w{i}]adelay={ms_}|{ms_}[d{i}]"
                mezcla.append(f"[d{i}]")
        fa += ";" + "".join(mezcla) + f"amix=inputs={len(mezcla)}:duration=first:normalize=0,alimiter=limit=0.95[a]"
        entradas = ["-i", video, "-i", voz, "-i", musica,
                    "-f", "lavfi", "-i", "sine=f=55:d=0.6,afade=t=out:st=0.05:d=0.55,aformat=channel_layouts=stereo"]
        if cambios:
            entradas += ["-f", "lavfi", "-i", "anoisesrc=d=0.4:c=pink:a=0.6"]
        sh("ffmpeg", "-y", *entradas, "-filter_complex", f"[0:v]setsar=1,ass={ass}[v];{fa}",
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", "-t", f"{total:.3f}", salida)
    print(f"Listo: {salida} ({total:.1f} s, {len(segs)} planos)")


if __name__ == "__main__":
    main()
