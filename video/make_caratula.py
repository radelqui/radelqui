#!/usr/bin/env python3
"""
Genera la carátula en PDF que se sube al campo del vídeo del formulario.

El formulario de Omni Dental pide un vídeo de 1 minuto pero su campo de subida
sólo acepta PDF, DOC/DOCX, XLS/CSV, JPG/JPEG, PNG y GIF — el mismo componente
por defecto que usan para el currículum, sin ajustar.

El vídeo en sí se entrega como GIF (ver make_gif.py), que es un formato que el
campo sí acepta. Esta carátula lo acompaña: da acceso a la versión en HD con
locución mediante enlace y QR, y resume la escaleta para que se entienda la
pieza aunque nadie pulse nada.

Uso:
    python3 video/make_caratula.py --url https://youtu.be/XXXXXXXX
"""

import argparse
import os
import subprocess
import sys
import tempfile

import qrcode
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# A4 vertical a 150 ppp
W, H = 1240, 1754

BG = (255, 255, 255)
SOFT = (245, 248, 252)
BORDER = (219, 228, 241)
BLUE = (10, 102, 194)
BLUE_DEEP = (7, 74, 143)
BLUE_SOFT = (232, 240, 253)
GREEN = (5, 150, 105)
TEXT = (15, 23, 42)
MUTED = (91, 107, 133)
DIM = (152, 166, 187)

FDIR = "/usr/share/fonts/truetype/roboto/unhinted/RobotoTTF"
_FONTS = {
    "black": f"{FDIR}/Roboto-Black.ttf",
    "bold": f"{FDIR}/Roboto-Bold.ttf",
    "medium": f"{FDIR}/Roboto-Medium.ttf",
    "regular": f"{FDIR}/Roboto-Regular.ttf",
    "light": f"{FDIR}/Roboto-Light.ttf",
}
_cache = {}

# Momentos del vídeo que mejor resumen cada escena
FRAME_TIMES = [7.0, 21.0, 33.0, 58.0]
FRAME_CAPTIONS = [
    "Presentación",
    "Vuestros resultados esperados",
    "Las 11 competencias",
    "Por qué soy la persona ideal",
]

SCENES = [
    ("0:00", "Presentación y a qué oferta me presento"),
    ("0:08", "Vuestra sección «Resultados esperados», respondida"),
    ("0:23", "Las 11 competencias que pedís puntuar del 1 al 5"),
    ("0:35", "Vuestra lista «No apliques si…», punto por punto"),
    ("0:46", "Por qué soy la persona ideal · datos de contacto"),
]


def font(weight, size):
    key = (weight, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(_FONTS[weight], size)
    return _cache[key]


def text_w(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]


def rrect(d, box, radius, fill=None, outline=None, width=2):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def grab_frames(video, times, height=210):
    """Extrae un fotograma del vídeo por cada instante pedido."""
    tmp = tempfile.mkdtemp(prefix="frames_")
    out = []
    for i, t in enumerate(times):
        path = os.path.join(tmp, f"f{i}.png")
        subprocess.run([
            "ffmpeg", "-v", "error", "-ss", str(t), "-i", video,
            "-frames:v", "1", "-vf", f"scale=-1:{height}", path,
        ], check=True)
        out.append(Image.open(path).convert("RGB"))
    return out


def build_qr(url, size):
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=10, border=1)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color=(15, 23, 42), back_color=(255, 255, 255))
    return img.convert("RGB").resize((size, size), Image.NEAREST)


def round_photo(path, size):
    """Foto recortada en círculo con aro azul, igual que en el vídeo."""
    src = Image.open(path).convert("RGB")
    w, h = src.size
    side = min(w, h)
    src = src.crop(((w - side) // 2, int((h - side) * 0.06),
                    (w - side) // 2 + side, int((h - side) * 0.06) + side))
    ss = size * 3
    src = src.resize((ss, ss), Image.LANCZOS)
    mask = Image.new("L", (ss, ss), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, ss - 1, ss - 1), fill=255)

    pad = 24
    canvas = Image.new("RGBA", (ss + pad * 2, ss + pad * 2), (0, 0, 0, 0))
    canvas.paste(src, (pad, pad), mask)
    ImageDraw.Draw(canvas).ellipse(
        (pad - 9, pad - 9, pad + ss + 9, pad + ss + 9), outline=BLUE + (255,), width=18
    )
    return canvas.resize((size + (pad * 2) // 3,) * 2, Image.LANCZOS)


def render(url, video, photo_path, out_pdf):
    page = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(page)

    # Banda superior
    d.rectangle((0, 0, W, 300), fill=SOFT)
    d.line([(0, 300), (W, 300)], fill=BORDER, width=2)

    photo = round_photo(photo_path, 168)
    page.paste(photo, (72, 66), photo)

    d.text((286, 84), "CANDIDATURA · OMNI DENTAL", font=font("bold", 22), fill=BLUE)
    d.text((286, 122), "Carlos De La Torre", font=font("black", 62), fill=TEXT)
    d.text((286, 200), "Especialista y Líder en IA y Automatizaciones",
           font=font("medium", 30), fill=MUTED)
    d.text((286, 244), "radelqui@gmail.com · +34 745 03 71 90 · Madrid, 100% remoto",
           font=font("regular", 25), fill=DIM)

    # Bloque del enlace + QR
    y = 352
    rrect(d, (72, y, W - 72, y + 396), 22, fill=BLUE_SOFT, outline=BORDER, width=2)
    d.text((116, y + 40), "VÍDEO DE PRESENTACIÓN · 1 MINUTO",
           font=font("bold", 24), fill=BLUE_DEEP)
    d.text((116, y + 88), "Ver el vídeo aquí:", font=font("regular", 28), fill=MUTED)

    f_url = font("bold", 34)
    while text_w(d, url, f_url) > 620 and f_url.size > 18:
        f_url = font("bold", f_url.size - 2)
    d.text((116, y + 134), url, font=f_url, fill=BLUE_DEEP)
    d.line([(116, y + 134 + f_url.size + 8),
            (116 + text_w(d, url, f_url), y + 134 + f_url.size + 8)],
           fill=BLUE, width=2)

    d.text((116, y + 214), "El GIF que adjunto es este mismo vídeo: se reproduce",
           font=font("regular", 25), fill=MUTED)
    d.text((116, y + 250), "sin salir del formulario. El enlace lleva al HD con voz.",
           font=font("regular", 25), fill=MUTED)
    d.text((116, y + 306), "1920x1080 · 60 s exactos · con locución",
           font=font("medium", 25), fill=GREEN)

    qr = build_qr(url, 268)
    qx, qy = W - 72 - 44 - 268, y + 64
    rrect(d, (qx - 18, qy - 18, qx + 286, qy + 286), 16, fill=(255, 255, 255),
          outline=BORDER, width=2)
    page.paste(qr, (qx, qy))
    cap = "Escanea para verlo"
    d.text((qx + 134 - text_w(d, cap, font("regular", 22)) / 2, qy + 296), cap,
           font=font("regular", 22), fill=DIM)

    # Tira de fotogramas
    y = 800
    d.text((72, y), "Qué vas a ver", font=font("black", 38), fill=TEXT)
    y += 68
    frames = grab_frames(video, FRAME_TIMES, height=196)
    fw = (W - 144 - 3 * 20) // 4
    for i, im in enumerate(frames):
        im = im.resize((fw, int(im.height * fw / im.width)), Image.LANCZOS)
        x = 72 + i * (fw + 20)
        page.paste(im, (x, y))
        d.rectangle((x, y, x + fw, y + im.height), outline=BORDER, width=2)
        d.text((x, y + im.height + 12), FRAME_CAPTIONS[i],
               font=font("regular", 19), fill=MUTED)

    # Escaleta
    y += 196 + 78
    d.text((72, y), "Escaleta", font=font("black", 38), fill=TEXT)
    d.text((72, y + 54), "Cada escena responde a una sección literal de vuestra oferta.",
           font=font("regular", 26), fill=MUTED)
    y += 110
    for i, (stamp, what) in enumerate(SCENES):
        top = y + i * 62
        rrect(d, (72, top, W - 72, top + 52), 12, fill=SOFT)
        d.text((100, top + 12), stamp, font=font("bold", 27), fill=BLUE)
        d.text((196, top + 12), what, font=font("regular", 27), fill=TEXT)

    # Pie
    d.line([(72, H - 128), (W - 72, H - 128)], fill=BORDER, width=2)
    d.text((72, H - 104), "Portfolio completo: sypnose.cloud/portfolio/carlos",
           font=font("medium", 25), fill=BLUE)
    d.text((72, H - 68), "linkedin.com/in/carlosdelatorre-ai · github.com/radelqui",
           font=font("regular", 23), fill=DIM)

    page.save(out_pdf, "PDF", resolution=150.0)
    return out_pdf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True,
                    help="enlace público al vídeo (YouTube no listado, Drive, Loom...)")
    ap.add_argument("--video", default="video/carlos-delatorre-omnidental-60s-con-voz.mp4")
    ap.add_argument("--photo", required=True)
    ap.add_argument("--out", default="video/caratula-video-omnidental.pdf")
    args = ap.parse_args()

    for path in (args.video, args.photo):
        if not os.path.exists(path):
            sys.exit(f"No encuentro: {path}")

    render(args.url, args.video, args.photo, args.out)
    print(f"Listo: {args.out}  ({os.path.getsize(args.out) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
