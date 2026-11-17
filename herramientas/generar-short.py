#!/usr/bin/env python3
"""Genera un Short vertical (1080x1920) dinámico a partir de un guion JSON.

Uso:
  python generar-short.py guion.json salida.mp4

Cada escena = una frase de voz + varios planos que se van cortando mientras habla.
Guion (ver 03-guiones/*.json):
{
  "gancho": "GTA 6 SALE EN 2 DÍAS",        # texto grande arriba durante la 1.ª escena
  "semilla_musica": 1,                       # cambia la base musical
  "escenas": [
    {"texto": "como suena (para la voz)", "subtitulo": "como se escribe",
     "etiqueta": "1. FECHA",                 # opcional: rótulo arriba durante la escena
     "planos": ["A17", "tag:vicecity", "imagen:lucia.jpg"],
     "corte": 1.6}                           # opcional: segundos por plano
  ]
}
Planos: id del catálogo 02-referencias/planos-trailers.json, "tag:<etiqueta>" (elige uno al azar
sin repetir) o "imagen:<archivo>" de 04-assets/clips-fuente/gta6-oficial.

Variables de entorno:
  COQUI_MODEL_DIR  carpeta del modelo de voz (instalar-voz.sh)
  TRAILERS_DIR     carpeta con launch.mp4, t1.mp4, t2.mp4 (tráileres oficiales en 4K)
  VOZ_REFERENCIA   opcional: wav de la voz de Aitor → la voz sintética se convierte a su timbre (FreeVC)
  FREEVC_DIR       carpeta del modelo FreeVC (necesaria con VOZ_REFERENCIA)
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
PAUSA = 0.12        # silencio tras cada frase (s)
TEMPO_VOZ = 1.10    # voz un 10 % más rápida: ritmo de Short
CORTE_GANCHO = 1.2  # segundos por plano en la primera escena
CORTE = 1.8         # segundos por plano en el resto
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sh(*args):
    r = subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if r.returncode:
        sys.exit(f"Error en: {' '.join(args)[:300]}\n{r.stderr[-1500:]}")


def duracion_wav(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


# ---------- voz ----------

def sintetizar(escenas, tmp):
    from TTS.api import TTS  # solo existe dentro del venv de Coqui

    d = os.environ["COQUI_MODEL_DIR"]
    tts = TTS(model_path=os.path.join(d, "model_file.pth"),
              config_path=os.path.join(d, "config.json"), progress_bar=False)
    ref = os.environ.get("VOZ_REFERENCIA")
    vc = None
    if ref:
        # FreeVC: cambia el timbre al de la grabación de referencia (necesita WavLM-Large.pt
        # en ~/.local/share/tts/, lo deja instalar-voz.sh)
        from TTS.utils.synthesizer import Synthesizer
        fv = os.environ["FREEVC_DIR"]
        vc = Synthesizer(vc_checkpoint=os.path.join(fv, "model.pth"), vc_config=os.path.join(fv, "config.json"))
    rutas = []
    for i, e in enumerate(escenas):
        crudo = os.path.join(tmp, f"voz{i}_raw.wav")
        tts.tts_to_file(text=e["texto"].replace("…", ","), file_path=crudo)
        if vc:
            convertido = os.path.join(tmp, f"voz{i}_vc.wav")
            vc.save_wav(vc.voice_conversion(source_wav=crudo, target_wav=ref), convertido)
            crudo = convertido
        limpio = os.path.join(tmp, f"voz{i}.wav")
        sh("ffmpeg", "-y", "-i", crudo, "-af",
           "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
           "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
           f"atempo={TEMPO_VOZ},highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,"
           f"apad=pad_dur={PAUSA}", "-ar", "48000", "-ac", "1", limpio)
        rutas.append(limpio)
    return rutas


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
    """Recorte vertical del tráiler 4K + zoom progresivo (punch-in)."""
    fw, fh, fx, fy = fuentes[p["src"]]["crop"]
    vw = int(fh * 9 / 16) // 2 * 2
    cx = int(fx + p["x"] * fw - vw / 2)
    cx = max(fx, min(cx, fx + fw - vw))
    largo = p["fin"] - p["ini"]
    ini = p["ini"] + min(offset, max(0, largo - dur))
    lento = max(1.0, min(2.0, dur / max(largo, 0.1)))  # plano corto → cámara lenta (máx. 2x)
    zoom = 0.06 if i % 2 == 0 else 0.10
    vf = (f"crop={vw}:{fh}:{cx}:{fy},setpts={lento:.3f}*PTS,"
          f"scale={W}:{H},"
          f"scale=w='{W}*(1+{zoom}*t/{dur:.3f})':h=-2:eval=frame,crop={W}:{H},"
          "eq=contrast=1.06:saturation=1.18,fps=30,format=yuv420p")
    trailer = os.path.join(os.environ["TRAILERS_DIR"], p["src"] + ".mp4")
    sh("ffmpeg", "-y", "-ss", f"{ini:.3f}", "-i", trailer, "-t", f"{dur:.3f}", "-an", "-vf", vf,
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", salida)


def segmento_imagen(img, dur, salida, i):
    frames = int(round(dur * FPS))
    vf = (f"split[a][b];[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
          f"gblur=sigma=40,eq=brightness=-0.15[fondo];"
          f"[b]scale={W - 80}:-2,scale=w='({W - 80})*(1+0.08*t/{dur:.3f})':h=-2:eval=frame[frente];"
          f"[fondo][frente]overlay=(W-w)/2:(H-h)/2-{int(H * 0.05)}:shortest=1,"
          "drawbox=x=0:y=0:w=iw:h=ih:color=black@0:t=0,format=yuv420p")
    sh("ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", img, "-filter_complex", vf,
       "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", salida)


# ---------- subtítulos, rótulos, barra ----------

def t_ass(t):
    h, r = divmod(max(t, 0), 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def construir_ass(escenas, duraciones, gancho, total, path):
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{FUENTE},92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,8,4,5,50,50,0,1
Style: Gancho,{FUENTE},96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,9,4,8,60,60,210,1
Style: Etiqueta,{FUENTE},82,&H00000000,&H00000000,&H0000E6FF,&H0000E6FF,-1,0,0,0,100,100,0,0,3,14,0,8,60,60,250,1
Style: Caja,{FUENTE},10,&H00FFFFFF,&H00FFFFFF,&H00FFFFFF,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    pop = r"\fscx70\fscy70\t(0,90,\fscx112\fscy112)\t(90,170,\fscx100\fscy100)"
    amarillo = r"\c&H00E6FF&"
    if gancho:
        lineas = gancho.split("\\N") if "\\N" in gancho else [gancho]
        txt = "\\N".join(lineas)
        # el gancho se pinta en blanco con la última palabra en amarillo
        palabras = txt.split(" ")
        txt = " ".join(palabras[:-1]) + (" " if len(palabras) > 1 else "") + "{" + amarillo + "}" + palabras[-1]
        ev.append(f"Dialogue: 2,{t_ass(0)},{t_ass(duraciones[0])},Gancho,,0,0,0,,{{{pop}}}{txt}")
    t0 = 0.0
    for idx, (e, dur) in enumerate(zip(escenas, duraciones)):
        if idx > 0:  # destello blanco al cambiar de punto
            ev.append(f"Dialogue: 5,{t_ass(t0)},{t_ass(t0 + 0.18)},Caja,,0,0,0,,"
                      f"{{\\an7\\pos(0,0)\\1a&H40&\\fad(0,170)\\p1}}m 0 0 l {W} 0 {W} {H} 0 {H}{{\\p0}}")
        if e.get("etiqueta"):
            ev.append(f"Dialogue: 3,{t_ass(t0 + 0.05)},{t_ass(t0 + dur)},Etiqueta,,0,0,0,,"
                      f"{{{pop}}}{e['etiqueta'].upper()}")
        palabras = (e.get("subtitulo") or e["texto"]).split()
        hablado = (dur - PAUSA)
        pesos = [len(p) + 2 + (4 if re.search(r"[.,:;?!]$", p) else 0) for p in palabras]
        total_p = sum(pesos)
        tiempos, t = [], t0
        for pz in pesos:
            d = hablado * pz / total_p
            tiempos.append((t, t + d))
            t += d
        # bloques de 2-3 palabras; cortar tras signos de puntuación
        bloques, act = [], []
        for k, p in enumerate(palabras):
            act.append(k)
            if len(act) == 3 or (len(act) >= 2 and len(p) > 7) or re.search(r"[.,:;?!]$", p):
                bloques.append(act)
                act = []
        if act:
            bloques.append(act)
        for b in bloques:
            for j, k in enumerate(b):
                ini, fin = tiempos[k]
                if k == b[-1]:
                    fin = tiempos[k][1]
                partes = []
                for kk in b:
                    w_ = palabras[kk].upper()
                    partes.append("{" + amarillo + "}" + w_ + "{\\c&HFFFFFF&}" if kk == k else w_)
                efecto = pop if j == 0 else ""
                ev.append(f"Dialogue: 1,{t_ass(ini)},{t_ass(fin)},Sub,,0,0,0,,"
                          f"{{\\pos({W // 2},{int(H * 0.70)}){efecto}}}{' '.join(partes)}")
        t0 += dur
    # barra de progreso inferior
    ms = int(total * 1000)
    ev.append(f"Dialogue: 4,{t_ass(0)},{t_ass(total)},Caja,,0,0,0,,"
              f"{{\\an7\\pos(0,{H - 14})\\c&H00E6FF&\\clip(0,{H - 14},0,{H})\\t(0,{ms},\\clip(0,{H - 14},{W},{H}))\\p1}}"
              f"m 0 0 l {W} 0 {W} 14 0 14{{\\p0}}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(cab + "\n".join(ev) + "\n")


# ---------- principal ----------

def main():
    guion_path, salida = sys.argv[1], sys.argv[2]
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

        musica = os.path.join(tmp, "musica.wav")
        sh(sys.executable, os.path.join(RAIZ, "herramientas", "musica.py"), musica, f"{total + 1:.1f}", str(semilla))

        ass = os.path.join(tmp, "subs.ass")
        construir_ass(escenas, duraciones, g.get("gancho", ""), total, ass)

        # audio: voz a -14 LUFS, música baja y que se aparta cuando hay voz, whoosh en cada cambio de punto
        cambios, t = [], 0.0
        for d in duraciones[:-1]:
            t += d
            cambios.append(t)
        fa = ("[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,asplit[voz][llave];"
              "[2:a]volume=0.22,aformat=channel_layouts=stereo[mus];"
              "[mus][llave]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=350[musd]")
        mezcla = ["[voz]", "[musd]"]
        if cambios:
            fa += (";[3:a]highpass=f=500,lowpass=f=6000,afade=t=in:d=0.15,afade=t=out:st=0.15:d=0.25,"
                   f"volume=0.25,asplit={len(cambios)}" + "".join(f"[w{i}]" for i in range(len(cambios))))
            for i, c in enumerate(cambios):
                ms_ = int(max(0, c - 0.18) * 1000)
                fa += f";[w{i}]adelay={ms_}|{ms_}[d{i}]"
                mezcla.append(f"[d{i}]")
        fa += ";" + "".join(mezcla) + f"amix=inputs={len(mezcla)}:duration=first:normalize=0,alimiter=limit=0.95[a]"
        entradas = ["-i", video, "-i", voz, "-i", musica]
        if cambios:
            entradas += ["-f", "lavfi", "-i", "anoisesrc=d=0.4:c=pink:a=0.6"]
        sh("ffmpeg", "-y", *entradas, "-filter_complex", f"[0:v]ass={ass}[v];{fa}",
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", "-t", f"{total:.3f}", salida)
    print(f"Listo: {salida} ({total:.1f} s, {len(segs)} planos)")


if __name__ == "__main__":
    main()
