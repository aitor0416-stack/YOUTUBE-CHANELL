#!/usr/bin/env python3
"""Genera una base synthwave original (sin copyright) para los Shorts.
Uso: python musica.py salida.wav [segundos=60] [semilla=1]
Acordes Am-F-C-G a 105 BPM: bombo, palmada, charles, bajo en corcheas, pad y arpegio.
La semilla cambia el arpegio y el timbre para que no todos los vídeos suenen igual."""
import sys
import wave

import numpy as np

SR = 48000
BPM = 105
BEAT = 60 / BPM

# notas MIDI (raíz de cada acorde) y triadas
ACORDES = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [48, 52, 55]), (55, [55, 59, 62])]


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def env(n, ataque, caida):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(ataque, 1e-4)) * np.exp(-t / caida)
    return e


def paso_bajo(x, corte):
    a = np.exp(-2 * np.pi * corte / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):  # filtro de un polo; suficiente para suavizar sierras
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def sierra(f, n, detune=0.0):
    t = np.arange(n) / SR
    return 2 * ((t * f * (1 + detune)) % 1) - 1


def main():
    salida = sys.argv[1]
    dur = float(sys.argv[2]) if len(sys.argv) > 2 else 60
    rng = np.random.default_rng(int(sys.argv[3]) if len(sys.argv) > 3 else 1)
    n = int(dur * SR)
    mix = np.zeros(n)
    pad = np.zeros(n)
    beat_n = int(BEAT * SR)
    compas = 4 * beat_n

    # patrón de arpegio aleatorio pero fijo para todo el tema
    patron = rng.integers(0, 3, 16)
    octava_arp = rng.choice([12, 24])

    k = int(0.35 * SR)
    t = np.arange(k) / SR
    bombo = np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-t * 30)) / SR) * np.exp(-t * 9)
    pal = rng.standard_normal(int(0.18 * SR)) * env(int(0.18 * SR), 0.001, 0.05)
    pal = pal - paso_bajo(pal, 900)  # quita graves: suena a palmada
    hh = rng.standard_normal(int(0.05 * SR)) * env(int(0.05 * SR), 0.0005, 0.012)
    hh = hh - paso_bajo(hh, 6000)

    def pega(dst, src, pos, vol):
        if pos >= len(dst):
            return
        m = min(len(src), len(dst) - pos)
        dst[pos:pos + m] += vol * src[:m]

    c = 0
    while c * compas < n:
        raiz, triada = ACORDES[c % 4]
        ini = c * compas
        # pad: 3 sierras desafinadas por nota, ataque lento
        largo = min(compas, n - ini)
        p = sum(sierra(hz(m), largo, d) for m in triada for d in (-0.004, 0.0, 0.005))
        pad[ini:ini + largo] += paso_bajo(p, 1400) * env(largo, 0.4, 6) * 0.05
        for b in range(4):
            pos = ini + b * beat_n
            pega(mix, bombo, pos, 0.9)
            if b in (1, 3):
                pega(mix, pal, pos, 0.2)
            for corch in range(2):
                pos8 = pos + corch * beat_n // 2
                pega(mix, hh, pos8 + beat_n // 4, 0.1)
                nb = beat_n // 2
                bajo = paso_bajo(sierra(hz(raiz - 12), nb), 500) * env(nb, 0.003, 0.18)
                pega(mix, bajo, pos8, 0.35)
            for s in range(4):  # arpegio en semicorcheas
                pos16 = pos + s * beat_n // 4
                nota = triada[patron[(b * 4 + s) % 16]] + octava_arp
                ns = beat_n // 4
                tt = np.arange(ns) / SR
                cuadrada = np.sign(np.sin(2 * np.pi * hz(nota) * tt))
                pega(mix, paso_bajo(cuadrada, 2500) * env(ns, 0.002, 0.07), pos16, 0.06)
        c += 1

    # "bombeo": el pad baja de volumen en cada bombo (típico del género)
    tt = (np.arange(n) % beat_n) / beat_n
    pad *= 0.35 + 0.65 * np.minimum(1, tt * 3)
    mix += pad
    # entrada y salida suaves
    f = int(0.8 * SR)
    mix[:f] *= np.linspace(0, 1, f)
    mix[-f:] *= np.linspace(1, 0, f)
    mix /= np.max(np.abs(mix)) + 1e-9
    est = np.stack([mix, np.roll(mix, int(0.012 * SR))], 1)  # ligera apertura estéreo
    pcm = (est * 0.9 * 32767).astype(np.int16)
    with wave.open(salida, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"Listo: {salida} ({dur:.0f} s)")


if __name__ == "__main__":
    main()
