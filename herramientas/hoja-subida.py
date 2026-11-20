#!/usr/bin/env python3
"""Hoja de subida: todo lo que hay que copiar y pegar al publicar, vídeo por vídeo.

Uso:
  python3 hoja-subida.py 03-guiones/24-*.json 03-guiones/25-*.json   → 05-videos-finales/SUBIR.md
  python3 hoja-subida.py --todos                                     (todos los que tienen .mp4)

Por qué: subir a mano en YouTube Studio / TikTok cuesta ~2 min por vídeo si el título, la
descripción y el archivo de subtítulos están ya juntos y en orden. No hay conector oficial de
YouTube para subir desde aquí y YouTube está bloqueado en el entorno cloud.
"""
import glob
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FINALES = os.path.join(RAIZ, "05-videos-finales")


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    if sys.argv[1] == "--todos":
        guiones = [g for g in sorted(glob.glob(os.path.join(RAIZ, "03-guiones", "[0-9]*.json")))
                   if os.path.exists(os.path.join(FINALES, os.path.basename(g)[:-5] + ".mp4"))]
    else:
        guiones = sys.argv[1:]
    partes = ["# Hoja de subida\n",
              "Para cada vídeo: sube el .mp4, pega el título y la descripción, y en YouTube añade el .srt "
              "como subtítulos (Subtítulos → Subir archivo → Con sincronización). En TikTok sube el mismo "
              "archivo (sin marca de agua de otra red) y usa el título como texto del post.\n",
              "Ajustes de YouTube: Shorts, «No es contenido para niños», «contenido alterado»: No (la voz "
              "sintética no imita a ninguna persona real ni muestra hechos reales falsos), categoría Videojuegos. Programa 1–2 al día en vez de todos a la vez.\n"]
    for g in guiones:
        d = json.load(open(g, encoding="utf-8"))
        n = os.path.basename(g)[:-5]
        mp4 = os.path.join(FINALES, n + ".mp4")
        aviso = "" if os.path.exists(mp4) else "  ⚠️ NO EXISTE TODAVÍA EL MP4"
        partes.append(f"\n---\n\n## {n}{aviso}\n")
        partes.append(f"- Archivo: `05-videos-finales/{n}.mp4` · subtítulos: `05-videos-finales/{n}.srt`\n")
        partes.append(f"\n**Título**\n```\n{d['titulo']}\n```\n")
        partes.append(f"\n**Descripción**\n```\n{d['descripcion']}\n```\n")
        flojos = [f["dato"] for f in d.get("fuentes", []) if f.get("confianza") != "Cierto"]
        if flojos:
            partes.append("\n_Datos con confianza Probable (vigila los comentarios):_ "
                          + "; ".join(x[:90] for x in flojos) + "\n")
    salida = os.path.join(FINALES, "SUBIR.md")
    open(salida, "w", encoding="utf-8").write("".join(partes))
    print(f"Hoja de subida: {salida} ({len(guiones)} vídeos)")


if __name__ == "__main__":
    main()
