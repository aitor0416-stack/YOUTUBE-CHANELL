#!/usr/bin/env python3
"""Genera un Short vertical (1080x1920) a partir de un guion JSON:
voz sintética por escena + imagen con movimiento + subtítulos palabra a palabra + gancho.

Uso:
  python generar-short.py guion.json salida.mp4

Formato del guion (ver 03-guiones/*.json):
{
  "gancho": "GTA 6 SALE EN 2 DÍAS",          # texto grande arriba los 3 primeros segundos
  "imagenes_dir": "ruta/a/las/imagenes",      # relativo al JSON
  "escenas": [
    {"texto": "frase que dice la voz", "imagen": "26.jpg", "subtitulo": "opcional, si difiere"}
  ]
}
Voz: Coqui TTS (modelo tts_models/es/css10/vits) — variable COQUI_MODEL_DIR con model_file.pth y config.json.
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import wave

W, H, FPS = 1080, 1920, 30
FUENTE = "DejaVu Sans"
PAUSA = 0.25  # silencio entre escenas (s)


def sh(*args):
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def duracion_wav(path):
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def sintetizar(escenas, tmp):
    from TTS.api import TTS  # import aquí: solo existe dentro del venv de Coqui

    d = os.environ["COQUI_MODEL_DIR"]
    tts = TTS(model_path=os.path.join(d, "model_file.pth"),
              config_path=os.path.join(d, "config.json"), progress_bar=False)
    rutas = []
    for i, e in enumerate(escenas):
        crudo = os.path.join(tmp, f"voz{i}_raw.wav")
        tts.tts_to_file(text=e["texto"], file_path=crudo)
        limpio = os.path.join(tmp, f"voz{i}.wav")
        # recorta silencios al inicio/fin y deja mono 48 kHz
        sh("ffmpeg", "-y", "-i", crudo, "-af",
           "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
           "silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
           f"apad=pad_dur={PAUSA}", "-ar", "48000", "-ac", "1", limpio)
        rutas.append(limpio)
    return rutas


def ass_tiempo(t):
    h, r = divmod(t, 3600)
    m, s = divmod(r, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def subtitulos_ass(escenas, duraciones, gancho, path):
    """Subtítulos en bloques de 2-3 palabras, repartidos según la longitud de cada palabra."""
    cab = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{FUENTE},84,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,7,3,5,60,60,0,1
Style: Gancho,{FUENTE},92,&H0000E6FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,8,3,8,60,60,230,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lineas = []
    if gancho:
        lineas.append(f"Dialogue: 1,{ass_tiempo(0)},{ass_tiempo(3)},Gancho,,0,0,0,,{gancho}")
    t0 = 0.0
    for e, dur in zip(escenas, duraciones):
        palabras = (e.get("subtitulo") or e["texto"]).split()
        hablado = dur - PAUSA
        total = sum(len(p) + 2 for p in palabras)
        bloques, actual = [], []
        for p in palabras:
            actual.append(p)
            if len(actual) == 3 or re.search(r"[.,:;?!]$", p):
                bloques.append(actual)
                actual = []
        if actual:
            bloques.append(actual)
        t = t0
        for b in bloques:
            d = hablado * sum(len(p) + 2 for p in b) / total
            texto = " ".join(b).upper()
            # posición: en el centro, algo por debajo (fuera de la zona de botones de Shorts)
            lineas.append(f"Dialogue: 0,{ass_tiempo(t)},{ass_tiempo(t + d)},Sub,,0,0,0,,{{\\pos({W // 2},{int(H * 0.66)})}}{texto}")
            t += d
        t0 += dur
    with open(path, "w", encoding="utf-8") as f:
        f.write(cab + "\n".join(lineas) + "\n")


def tamano_imagen(img):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                          "stream=width,height", "-of", "csv=p=0", img],
                         check=True, capture_output=True, text=True).stdout
    w, h = out.strip().split(",")[:2]
    return int(w), int(h)


def clip_imagen(img, dur, salida, i):
    """Imagen con zoom lento. Si al llenar la pantalla vertical habría que ampliarla más de 2x
    (se vería pixelada), se muestra entera a lo ancho sobre un fondo difuminado."""
    frames = int(round(dur * FPS))
    sentido = 1 if i % 2 == 0 else -1
    iw, ih = tamano_imagen(img)
    escala_cubrir = max(W / iw, H / ih)
    if escala_cubrir <= 2.0:
        # pantalla completa: zoom 1.00→1.08 + paneo horizontal suave
        vf = (f"scale={int(W * 1.12)}:{int(H * 1.12)}:force_original_aspect_ratio=increase,"
              f"crop={int(W * 1.12)}:{int(H * 1.12)},"
              f"zoompan=z='1+0.08*on/{frames}':"
              f"x='(iw-iw/zoom)/2+{sentido}*(iw-iw/zoom)/2*(on/{frames}-0.5)':"
              f"y='(ih-ih/zoom)/2':d={frames}:s={W}x{H}:fps={FPS},"
              "eq=contrast=1.05:saturation=1.1,format=yuv420p")
    else:
        # imagen entera a lo ancho + fondo de la misma imagen difuminado y oscurecido
        vf = (f"split[a][b];"
              f"[a]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
              f"gblur=sigma=40,eq=brightness=-0.15[fondo];"
              f"[b]scale={W * 2}:-2,zoompan=z='1+0.06*on/{frames}':x='(iw-iw/zoom)/2':"
              f"y='(ih-ih/zoom)/2':d={frames}:s={W}x{int(W * ih / iw) // 2 * 2}:fps={FPS}[frente];"
              f"[fondo][frente]overlay=(W-w)/2:(H-h)/2-{int(H * 0.06)},"
              "eq=contrast=1.05:saturation=1.1,format=yuv420p")
    sh("ffmpeg", "-y", "-loop", "1", "-framerate", str(FPS), "-i", img,
       "-filter_complex" if "[" in vf else "-vf", vf, "-frames:v", str(frames),
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", salida)


def main():
    guion_path, salida = sys.argv[1], sys.argv[2]
    with open(guion_path, encoding="utf-8") as f:
        g = json.load(f)
    base = os.path.dirname(os.path.abspath(guion_path))
    img_dir = os.path.join(base, g.get("imagenes_dir", "."))
    escenas = g["escenas"]

    with tempfile.TemporaryDirectory() as tmp:
        voces = sintetizar(escenas, tmp)
        duraciones = [duracion_wav(v) for v in voces]

        clips = []
        for i, (e, d) in enumerate(zip(escenas, duraciones)):
            c = os.path.join(tmp, f"clip{i}.mp4")
            clip_imagen(os.path.join(img_dir, e["imagen"]), d, c, i)
            clips.append(c)

        with open(os.path.join(tmp, "clips.txt"), "w") as f:
            f.writelines(f"file '{c}'\n" for c in clips)
        with open(os.path.join(tmp, "voces.txt"), "w") as f:
            f.writelines(f"file '{v}'\n" for v in voces)
        sh("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "clips.txt"),
           "-c", "copy", os.path.join(tmp, "video.mp4"))
        sh("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", os.path.join(tmp, "voces.txt"),
           os.path.join(tmp, "voz.wav"))

        ass = os.path.join(tmp, "subs.ass")
        subtitulos_ass(escenas, duraciones, g.get("gancho", ""), ass)

        # "whoosh" suave en cada cambio de imagen (ruido filtrado, sin copyright)
        cortes, t = [], 0.0
        for d in duraciones[:-1]:
            t += d
            cortes.append(t)
        filtro_a = "[1:a]loudnorm=I=-14:TP=-1.5:LRA=11[voz]"
        entradas = ["-i", os.path.join(tmp, "video.mp4"), "-i", os.path.join(tmp, "voz.wav")]
        if cortes:
            entradas += ["-f", "lavfi", "-i", "anoisesrc=d=0.45:c=pink:a=0.5"]
            filtro_a += (";[2:a]highpass=f=600,lowpass=f=5000,afade=t=in:d=0.2,"
                         "afade=t=out:st=0.2:d=0.25,volume=0.12,asplit=" + str(len(cortes)) +
                         "".join(f"[w{i}]" for i in range(len(cortes))))
            for i, c in enumerate(cortes):
                ms = int(max(0, c - 0.22) * 1000)
                filtro_a += f";[w{i}]adelay={ms}|{ms}[d{i}]"
            filtro_a += ";[voz]" + "".join(f"[d{i}]" for i in range(len(cortes))) + \
                        f"amix=inputs={len(cortes) + 1}:duration=first:normalize=0[a]"
        else:
            filtro_a = filtro_a.replace("[voz]", "[a]")

        sh("ffmpeg", "-y", *entradas,
           "-filter_complex", f"[0:v]ass={ass}[v];{filtro_a}",
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
           "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", "-shortest", salida)
    print(f"Listo: {salida} ({sum(duraciones):.1f} s)")


if __name__ == "__main__":
    main()
