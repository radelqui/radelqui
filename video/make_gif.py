#!/usr/bin/env python3
"""
Convierte el vídeo a GIF animado para poder subirlo al formulario.

El campo del vídeo de Omni Dental es obligatorio y sólo acepta PDF, DOC/DOCX,
XLS/CSV, JPG/JPEG, PNG y GIF. Un GIF *es* vídeo, así que la pieza entra tal
cual en el formulario, sin pedir excepciones ni depender de un enlace externo.

Lo que se pierde es el audio, no el mensaje: el vídeo se diseñó para leerse
sin sonido, con todo el contenido en pantalla. La versión con locución va
enlazada desde la carátula PDF.

Se usa paleta en dos pasadas (palettegen + paletteuse). Con `stats_mode=diff`
la paleta se calcula sobre lo que cambia entre frames, que es lo que mantiene
legibles los textos sobre el fondo claro.

Uso:
    python3 video/make_gif.py
    python3 video/make_gif.py --width 800 --fps 10   # más ligero
"""

import argparse
import os
import subprocess
import sys
import tempfile


def build(video, out, width, fps, colors):
    tmp = tempfile.mkdtemp(prefix="gif_")
    palette = os.path.join(tmp, "palette.png")
    scale = f"fps={fps},scale={width}:-1:flags=lanczos"

    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", video,
        "-vf", f"{scale},palettegen=max_colors={colors}:stats_mode=diff",
        palette,
    ], check=True)

    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", video, "-i", palette,
        "-lavfi", f"{scale}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=3",
        "-loop", "0", out,
    ], check=True)

    os.remove(palette)
    os.rmdir(tmp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", default="video/carlos-delatorre-omnidental-60s.mp4",
                    help="fuente; por defecto la versión sin audio, que es la que "
                         "importa aquí porque el GIF no lleva sonido")
    ap.add_argument("--out", default="video/carlos-delatorre-omnidental-60s.gif")
    ap.add_argument("--width", type=int, default=960)
    ap.add_argument("--fps", type=int, default=12)
    ap.add_argument("--colors", type=int, default=128)
    args = ap.parse_args()

    if not os.path.exists(args.video):
        sys.exit(f"No encuentro: {args.video}")

    build(args.video, args.out, args.width, args.fps, args.colors)
    mb = os.path.getsize(args.out) / 1e6
    print(f"Listo: {args.out}  ({mb:.1f} MB, {args.width}px @ {args.fps} fps)")
    if mb > 25:
        print("Aviso: pesa bastante. Prueba --width 800 --fps 10.")


if __name__ == "__main__":
    main()
