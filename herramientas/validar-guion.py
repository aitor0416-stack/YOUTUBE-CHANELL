#!/usr/bin/env python3
"""Revisa un guion (03-guiones/*.json) ANTES de generar el vídeo. Si algo falla, no se genera.

Uso:
  python validar-guion.py 03-guiones/19-bigfoot.json [otro.json ...]
  python validar-guion.py 03-guiones/*.json

Comprueba:
  1. Título: máx. 60 caracteres, contiene "GTA 6" y acaba en un emoji.
  2. Descripción: pregunta con 👇, créditos de Rockstar + "Voz sintética", 4-6 hashtags con #gta6 y #shorts.
  3. Escenas: cada una con "texto" (lo que se dice), "subtitulo" (lo que se lee) y planos que existen
     en 02-referencias/planos-trailers.json.
  4. Palabras prohibidas (02-referencias/palabras-prohibidas.txt): leaks, spoilers, piratería y,
     en la primera escena, violencia.
  5. Fuentes: el guion lleva una lista "fuentes" con cada dato, de dónde sale y la confianza
     (Cierto / Probable). Cada número que aparece en los subtítulos debe estar en algún "dato".
  6. Subtítulos: "32%" sin espacio (si no, el % sale solo en pantalla).
  7. Duración estimada: avisa si va a quedar fuera de 20-35 s (es un aviso, no un fallo: la medida
     real la da el render).

Sale con 0 si todo está bien y con 1 si hay algún FALLO (los AVISOS no paran el render).
"""
import json
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PALABRAS_POR_SEGUNDO = 3.4   # medido en los Shorts 07-23 con Kokoro em_santa a velocidad 1.12
EMOJI = re.compile("[\U0001F300-\U0001FAFF☀-➿⭐✅❌]")


def cargar_prohibidas():
    generales, gancho = [], []
    seccion = generales
    with open(os.path.join(RAIZ, "02-referencias", "palabras-prohibidas.txt"), encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#"):
                continue
            if linea == "[gancho]":
                seccion = gancho
                continue
            seccion.append(linea)
    return generales, gancho


def busca(palabra, texto):
    if palabra.startswith("="):
        return re.search(r"\b" + re.escape(palabra[1:]) + r"\b", texto, re.I)
    if " " in palabra:
        return re.search(re.escape(palabra), texto, re.I)
    return re.search(r"\b" + re.escape(palabra) + r"\w*", texto, re.I)


def numeros_a_justificar(subtitulo):
    """Números que dicen un dato. No cuentan: el 6/5/4 de "GTA 6", los pegados a letras porque son
    parte de un nombre ("PS5", "Game8", "3D") ni el número de un punto de lista ("1. ...")."""
    s = re.sub(r"\bGTA\s+(VI|V|IV|\d)\b", " ", subtitulo)
    s = re.sub(r"^(Y\s+)?\d+\.\s", " ", s.strip())          # "1. ..." / "Y 4. ..."
    return re.findall(r"(?<![A-Za-zÁÉÍÓÚáéíóúñÑ])\d+(?:[.,]\d+)*(?![A-Za-zÁÉÍÓÚáéíóúñÑ])", s)


def validar(ruta, planos_catalogo, prohibidas, prohibidas_gancho):
    fallos, avisos = [], []
    try:
        g = json.load(open(ruta, encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return [f"no se puede leer el JSON: {e}"], []

    # 1. título
    t = g.get("titulo", "")
    if not t:
        fallos.append("falta 'titulo'")
    else:
        if len(t) > 60:
            fallos.append(f"título de {len(t)} caracteres (máx. 60)")
        if "GTA 6" not in t and "GTA VI" not in t:
            fallos.append("el título no dice 'GTA 6'")
        if not EMOJI.search(t[-3:]):
            avisos.append("el título no acaba en emoji")

    # 2. descripción
    d = g.get("descripcion", "")
    if "👇" not in d:
        fallos.append("la descripción no tiene la pregunta con 👇")
    if "Rockstar Games" not in d or "Voz sintética" not in d:
        fallos.append("faltan los créditos ('Imágenes: tráileres oficiales de Rockstar Games. Voz sintética.')")
    tags = re.findall(r"#\w+", d)
    if not 4 <= len(tags) <= 6:
        fallos.append(f"{len(tags)} hashtags (entre 4 y 6)")
    for obligatorio in ("#gta6", "#shorts"):
        if obligatorio not in tags:
            fallos.append(f"falta {obligatorio}")

    # 3. escenas
    escenas = g.get("escenas") or []
    if not escenas:
        fallos.append("no hay escenas")
    for i, e in enumerate(escenas, 1):
        if not e.get("texto") or not e.get("subtitulo"):
            fallos.append(f"escena {i}: falta 'texto' o 'subtitulo'")
        for p in e.get("planos") or []:
            if p.startswith("tag:"):
                continue
            if p.startswith("imagen:"):
                if not os.path.exists(os.path.join(RAIZ, "04-assets", "clips-fuente", "gta6-oficial", p[7:])):
                    fallos.append(f"escena {i}: no existe la imagen {p[7:]}")
            elif p not in planos_catalogo:
                fallos.append(f"escena {i}: el plano {p} no está en el catálogo")
        if not e.get("planos"):
            fallos.append(f"escena {i}: sin planos")
        # 6. porcentajes
        if re.search(r"\d\s+%", e.get("subtitulo", "")):
            fallos.append(f"escena {i}: escribe el % pegado al número (\"32%\")")

    # 4. palabras prohibidas
    todo = " ".join([t, d] + [e.get("texto", "") + " " + e.get("subtitulo", "") for e in escenas])
    for p in prohibidas:
        m = busca(p, todo)
        if m:
            fallos.append(f"palabra prohibida '{p.lstrip('=')}' (\"{m.group(0)}\")")
    if escenas:
        primera = escenas[0].get("texto", "") + " " + escenas[0].get("subtitulo", "")
        for p in prohibidas_gancho:
            m = busca(p, primera)
            if m:
                fallos.append(f"violencia en el gancho (primeros 7 s): '{m.group(0)}'")

    # 5. fuentes
    fuentes = g.get("fuentes")
    if not fuentes:
        fallos.append("falta 'fuentes' (lista de datos con su fuente y confianza)")
        fuentes = []
    for k, f in enumerate(fuentes, 1):
        if not f.get("dato") or not f.get("fuente"):
            fallos.append(f"fuente {k}: falta 'dato' o 'fuente'")
        if f.get("confianza") not in ("Cierto", "Probable"):
            fallos.append(f"fuente {k}: 'confianza' debe ser Cierto o Probable (una suposición no se publica)")
    datos = " ".join(f.get("dato", "") for f in fuentes)
    datos_norm = datos.replace(".", "").replace(",", "")
    for i, e in enumerate(escenas, 1):
        for n in numeros_a_justificar(e.get("subtitulo", "")):
            if n.replace(".", "").replace(",", "") not in datos_norm:
                fallos.append(f"escena {i}: el número {n} no está en ningún 'dato' de 'fuentes'")

    # 7. duración
    palabras = sum(len(e.get("texto", "").split()) for e in escenas)
    seg = palabras / PALABRAS_POR_SEGUNDO
    if not 20 <= seg <= 35:
        avisos.append(f"duración estimada {seg:.0f} s ({palabras} palabras); la regla es 20-35 s")
    return fallos, avisos


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    with open(os.path.join(RAIZ, "02-referencias", "planos-trailers.json"), encoding="utf-8") as f:
        planos = {p["id"] for p in json.load(f)["planos"]}
    prohibidas, prohibidas_gancho = cargar_prohibidas()
    total = 0
    for ruta in sys.argv[1:]:
        fallos, avisos = validar(ruta, planos, prohibidas, prohibidas_gancho)
        estado = "OK" if not fallos else f"{len(fallos)} FALLOS"
        print(f"{os.path.basename(ruta)}: {estado}")
        for x in fallos:
            print(f"   FALLO  {x}")
        for x in avisos:
            print(f"   aviso  {x}")
        total += len(fallos)
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
