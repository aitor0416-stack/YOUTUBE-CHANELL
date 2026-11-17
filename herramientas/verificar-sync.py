#!/usr/bin/env python3
"""Comprueba que los subtítulos (.srt) van a la vez que la voz (.voz.wav, generado con GUARDAR_VOZ=1).
Uso: python verificar-sync.py video.srt video.voz.wav
Mide: (1) que ningún subtítulo aparezca durante un silencio largo, (2) que cada pausa real de la voz
coincida con un cambio de subtítulo (±150 ms), (3) que el último subtítulo acabe cuando acaba la voz."""
import re
import subprocess
import sys


def srt(path):
    bloques = []
    for m in re.finditer(r"(\d+):(\d+):(\d+),(\d+) --> (\d+):(\d+):(\d+),(\d+)\n(.+)", open(path, encoding="utf-8").read()):
        g = [int(x) for x in m.groups()[:8]]
        a = g[0] * 3600 + g[1] * 60 + g[2] + g[3] / 1000
        b = g[4] * 3600 + g[5] * 60 + g[6] + g[7] / 1000
        bloques.append((a, b, m.group(9)))
    return bloques


def silencios(wav):
    r = subprocess.run(["ffmpeg", "-i", wav, "-af", "silencedetect=noise=-35dB:d=0.045", "-f", "null", "-"],
                       capture_output=True, text=True)
    ini = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r.stderr)]
    fin = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r.stderr)]
    dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", r.stderr).group(3)) + \
        60 * int(re.search(r"Duration: (\d+):(\d+)", r.stderr).group(2))
    return list(zip(ini, fin)), dur


def main():
    subs = srt(sys.argv[1])
    sil, dur = silencios(sys.argv[2])
    cambios = sorted({round(a, 3) for a, _, _ in subs} | {round(b, 3) for _, b, _ in subs})
    fallos = 0
    print(f"{len(subs)} subtítulos, {len(sil)} pausas en la voz, voz {dur:.2f} s")
    # (a) ningún subtítulo debe empezar dentro de un silencio (margen 60 ms)
    malos = [(ini, txt) for ini, _, txt in subs
             if any(a + 0.06 < ini < b - 0.06 for a, b in sil)]
    for ini, txt in malos:
        print(f"  subtítulo '{txt}' empieza a {ini:.2f}s, en pleno silencio  DESFASADO")
    fallos += len(malos)
    print(f"  subtítulos que empiezan en silencio: {len(malos)}/{len(subs)}")
    # (b) en cada pausa larga (fin de frase) debe cambiar el subtítulo
    for a, b in sil:
        if b - a < 0.10 or a < 0.05 or b > dur - 0.05:
            continue
        # el subtítulo debe cambiar durante la pausa o muy cerca
        cerca = min(cambios, key=lambda c: min(abs(c - a), abs(c - b)) if not (a <= c <= b) else 0)
        dist = 0 if a <= cerca <= b else min(abs(cerca - a), abs(cerca - b))
        ok = dist <= 0.15
        fallos += not ok
        print(f"  pausa {a:6.2f}-{b:6.2f}s → cambio de subtítulo a {dist * 1000:4.0f} ms {'OK' if ok else 'DESFASADO'}")
    # (d) sin parpadeos: entre dos subtítulos no debe quedar un hueco corto (30 ms - 0,5 s)
    huecos = [(subs[k][1], subs[k + 1][0] - subs[k][1]) for k in range(len(subs) - 1)
              if 0.03 < subs[k + 1][0] - subs[k][1] < 0.5]
    fallos += len(huecos)
    print(f"  parpadeos (huecos cortos entre subtítulos): {len(huecos)}")
    fin_subs = max(b for _, b, _ in subs)
    habla_fin = sil[-1][0] if sil and sil[-1][1] >= dur - 0.05 else dur
    d_fin = abs(fin_subs - habla_fin)
    fallos += d_fin > 0.25
    print(f"  último subtítulo acaba a {fin_subs:.2f}s, la voz a {habla_fin:.2f}s → {d_fin * 1000:.0f} ms "
          f"{'OK' if d_fin <= 0.25 else 'DESFASADO'}")
    print("RESULTADO:", "SINCRONIZADO" if not fallos else f"{fallos} PROBLEMAS")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
