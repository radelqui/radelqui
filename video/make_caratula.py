#!/usr/bin/env python3
"""
Genera la carátula PDF que se sube al campo del vídeo del formulario.

El campo es obligatorio y sólo acepta PDF, DOC/DOCX, XLS/CSV, JPG/JPEG, PNG y
GIF. Que no admita MP4 no impide entregar el MP4: el vídeo viaja dentro de este
PDF y se reproduce con un clic sobre el póster de la página.

Este PDF se va a abrir en Gmail, en Drive, en el visor de Chrome o dentro del
propio ATS — casi nunca en Adobe Acrobat. Eso decide el diseño:

  - El póster entero es una anotación /Link a la URL del vídeo. Es lo único
    interactivo que respetan TODOS los visores, el de Drive incluido. Un clic
    y el vídeo se abre en el navegador, con sonido.
  - El MP4 va además embebido (/EmbeddedFiles) para quien se descargue el PDF
    y lo abra en Acrobat, Vista Previa o Firefox: ahí aparece en el panel de
    adjuntos. Donde no se soporta es invisible y no estorba.
  - El QR repite la misma URL, para saltar al móvil.

Se descartó la anotación /RichMedia, que reproduce el vídeo dentro de la
página: sólo la soporta Acrobat, y encima entra en conflicto con el /Link si
comparten rectángulo. Un enlace que funciona en todas partes vale más que una
reproducción incrustada que casi nadie va a ver.

Requisitos:
    pip install pillow qrcode pikepdf

Uso:
    python3 video/make_caratula.py --url https://youtu.be/XXXX --photo foto.jpg
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile

import pikepdf
import qrcode
from PIL import Image, ImageDraw, ImageFont

# A4 vertical a 150 ppp
W, H = 1240, 1754
DPI = 150.0
PT = 72.0 / DPI              # de píxel de esta maqueta a punto PDF

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

# Qué dice cada escena. Los tiempos NO se escriben aquí: salen de
# timeline.json, que genera make_voice_real.py a partir de la grabación.
SCENE_TEXT = [
    "Presentación y a qué oferta me presento",
    "Vuestra sección «Resultados esperados», respondida",
    "Las 11 competencias que pedís puntuar del 1 al 5",
    "Vuestra lista «No apliques si…», punto por punto",
    "Por qué soy la persona ideal · datos de contacto",
]

DEFAULT_TIMELINE = [0.0, 11.28, 30.35, 44.17, 55.91, 71.87]

# Zona del póster, en píxeles de esta maqueta (16:9)
POSTER = (72, 330, 1168, 946)
POSTER_AT = 0.62             # instante del vídeo del que se saca el póster,
                             # como fracción de la primera escena


def font(weight, size):
    key = (weight, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(_FONTS[weight], size)
    return _cache[key]


def text_w(d, s, f):
    return d.textbbox((0, 0), s, font=f)[2]


def rrect(d, box, radius, fill=None, outline=None, width=2):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def stamp(seconds):
    return f"{int(seconds) // 60}:{int(seconds) % 60:02d}"


def to_pdf_rect(box):
    """Rectángulo en píxeles (origen arriba-izquierda) -> puntos PDF."""
    x0, y0, x1, y1 = box
    return [x0 * PT, (H - y1) * PT, x1 * PT, (H - y0) * PT]


def load_timeline(path):
    """Fronteras de escena en segundos. Las escribe make_voice_real.py."""
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            bounds = json.load(fh)["bounds"]
        if len(bounds) == len(SCENE_TEXT) + 1:
            return bounds
        print(f"Aviso: {path} trae {len(bounds)} tiempos y se esperaban "
              f"{len(SCENE_TEXT) + 1}. Uso el reparto por defecto.")
    return DEFAULT_TIMELINE


def grab_frame(video, at, width):
    """Un fotograma del vídeo, escalado, como imagen de Pillow."""
    tmp = tempfile.mkdtemp(prefix="poster_")
    path = os.path.join(tmp, "f.png")
    subprocess.run(["ffmpeg", "-v", "error", "-ss", str(at), "-i", video,
                    "-frames:v", "1", "-vf", f"scale={width}:-1", path], check=True)
    return Image.open(path).convert("RGB")


def build_qr(url, size):
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
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


def build_poster(video, timeline):
    """Fotograma del vídeo, oscurecido, con el botón de play encima."""
    x0, y0, x1, y1 = POSTER
    pw, ph = x1 - x0, y1 - y0
    at = timeline[0] + (timeline[1] - timeline[0]) * POSTER_AT
    im = grab_frame(video, at, pw).resize((pw, ph), Image.LANCZOS)

    # El fotograma ya es claro y lleva texto propio, así que sin un velo
    # fuerte el botón de play se pelea con él. Con 0.42 el fotograma se lee
    # como fondo y el botón queda claramente encima.
    im = Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), 0.42)

    d = ImageDraw.Draw(im)
    cx, cy, r = pw // 2, ph // 2, 74
    d.ellipse((cx - r - 7, cy - r - 7, cx + r + 7, cy + r + 7), fill=(255, 255, 255))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BLUE)
    d.polygon([(cx - 24, cy - 38), (cx - 24, cy + 38), (cx + 40, cy)],
              fill=(255, 255, 255))

    label = "Un clic para ver el vídeo"
    f = font("bold", 30)
    tw = text_w(d, label, f)
    bx, by = cx - tw // 2 - 26, cy + r + 34
    rrect(d, (bx, by, bx + tw + 52, by + 62), 31, fill=(255, 255, 255))
    d.text((bx + 26, by + 13), label, font=f, fill=BLUE_DEEP)
    return im


def render(url, video, photo_path, out_pdf, timeline):
    page = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(page)

    # --- cabecera
    d.rectangle((0, 0, W, 286), fill=SOFT)
    d.line([(0, 286), (W, 286)], fill=BORDER, width=2)

    photo = round_photo(photo_path, 158)
    page.paste(photo, (72, 64), photo)

    d.text((276, 78), "CANDIDATURA · OMNI DENTAL", font=font("bold", 22), fill=BLUE)
    d.text((276, 114), "Carlos De La Torre", font=font("black", 58), fill=TEXT)
    d.text((276, 188), "Especialista y Líder en IA y Automatizaciones",
           font=font("medium", 29), fill=MUTED)
    d.text((276, 230), "radelqui@gmail.com · +34 745 03 71 90 · Madrid, 100% remoto",
           font=font("regular", 24), fill=DIM)

    # --- póster del vídeo (encima irá la anotación RichMedia)
    page.paste(build_poster(video, timeline), (POSTER[0], POSTER[1]))
    d.rectangle(POSTER, outline=BORDER, width=2)

    # --- pie del póster: qué hacer si el visor no lo reproduce
    y = 982
    d.text((72, y), f"Vídeo de presentación · {stamp(timeline[-1])} · con voz",
           font=font("bold", 32), fill=TEXT)
    d.text((72, y + 50), "Pulsa el vídeo de arriba, escanea el QR, o abre este enlace.",
           font=font("regular", 24), fill=MUTED)
    d.text((72, y + 84), "El MP4 va además adjunto dentro de este PDF, en el icono del clip.",
           font=font("regular", 24), fill=MUTED)

    f_url = font("bold", 27)
    while text_w(d, url, f_url) > 820 and f_url.size > 16:
        f_url = font("bold", f_url.size - 2)
    url_y = y + 130
    d.text((72, url_y), url, font=f_url, fill=BLUE_DEEP)
    d.line([(72, url_y + f_url.size + 7), (72 + text_w(d, url, f_url),
            url_y + f_url.size + 7)], fill=BLUE, width=2)
    url_box = (72, url_y - 6, 72 + text_w(d, url, f_url), url_y + f_url.size + 12)

    qr_size = 156
    qx, qy = W - 72 - qr_size, y - 4
    rrect(d, (qx - 14, qy - 14, qx + qr_size + 14, qy + qr_size + 14), 14,
          fill=(255, 255, 255), outline=BORDER, width=2)
    page.paste(build_qr(url, qr_size), (qx, qy))

    # --- escaleta
    y = 1206
    d.text((72, y), "Escaleta", font=font("black", 38), fill=TEXT)
    d.text((72, y + 54), "Cada escena responde a una sección literal de vuestra oferta.",
           font=font("regular", 26), fill=MUTED)
    y += 110
    for i, what in enumerate(SCENE_TEXT):
        top = y + i * 60
        rrect(d, (72, top, W - 72, top + 50), 12, fill=SOFT)
        d.text((100, top + 11), stamp(timeline[i]), font=font("bold", 26), fill=BLUE)
        d.text((196, top + 11), what, font=font("regular", 26), fill=TEXT)

    # --- pie
    d.line([(72, H - 118), (W - 72, H - 118)], fill=BORDER, width=2)
    d.text((72, H - 96), "Portfolio completo: sypnose.cloud/portfolio/carlos",
           font=font("medium", 25), fill=BLUE)
    d.text((72, H - 60), "linkedin.com/in/carlosdelatorre-ai · github.com/radelqui",
           font=font("regular", 23), fill=DIM)

    page.save(out_pdf, "PDF", resolution=DPI)
    # Zonas clicables: el póster, el enlace escrito y el QR
    return [POSTER, url_box,
            (qx - 14, qy - 14, qx + qr_size + 14, qy + qr_size + 14)]


def add_video(pdf_path, video_path, url, boxes):
    """Deja el MP4 dentro del PDF y hace clicable el póster.

    El póster es un /Link a la URL, no una anotación /RichMedia: el enlace lo
    respetan todos los visores y RichMedia sólo Acrobat. El fichero embebido
    va aparte, para quien descargue el PDF y lo abra en un visor de escritorio.
    """
    data = open(video_path, "rb").read()
    name = os.path.basename(video_path)

    with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
        pdf.attachments[name] = pikepdf.AttachedFileSpec(
            pdf, data, mime_type="video/mp4",
            description="Vídeo de presentación · 1 minuto")

        pdf.pages[0].Annots = pikepdf.Array([
            pdf.make_indirect(pikepdf.Dictionary(
                Type=pikepdf.Name.Annot,
                Subtype=pikepdf.Name.Link,
                Rect=pikepdf.Array(to_pdf_rect(box)),
                Border=pikepdf.Array([0, 0, 0]),      # sin marco azul
                A=pikepdf.Dictionary(S=pikepdf.Name.URI,
                                     URI=pikepdf.String(url)),
            ))
            for box in boxes
        ])
        pdf.save(pdf_path)

    # El PDF sólo vale si el vídeo se recupera intacto
    with pikepdf.open(pdf_path) as check:
        got = check.attachments[name].get_file().read_bytes()
    if hashlib.sha256(got).digest() != hashlib.sha256(data).digest():
        raise RuntimeError("el vídeo embebido no se recupera intacto")
    return len(data)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True,
                    help="enlace público al vídeo (YouTube no listado, Drive, Loom...)")
    ap.add_argument("--video", default="video/carlos-delatorre-omnidental-con-voz.mp4")
    ap.add_argument("--photo", required=True)
    ap.add_argument("--out", default="video/caratula-video-omnidental.pdf")
    ap.add_argument("--timeline", default="video/timeline.json")
    args = ap.parse_args()

    for path in (args.video, args.photo):
        if not os.path.exists(path):
            sys.exit(f"No encuentro: {path}")

    timeline = load_timeline(args.timeline)
    boxes = render(args.url, args.video, args.photo, args.out, timeline)
    size = add_video(args.out, args.video, args.url, boxes)

    print(f"Vídeo embebido y verificado: {size / 1e6:.2f} MB")
    print(f"Listo: {args.out}  ({os.path.getsize(args.out) / 1e6:.2f} MB)")


if __name__ == "__main__":
    main()
