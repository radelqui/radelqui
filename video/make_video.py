#!/usr/bin/env python3
"""
Vídeo de presentación de 1 minuto para la oferta de Omni Dental
"Especialista y Líder en IA y Automatizaciones".

El vídeo está construido como respuesta directa a la oferta: cada escena
responde a una sección concreta del anuncio.

  1. Intro           — a quién se dirige y quién soy
  2. Resultados      — los "resultados esperados" que lista la oferta
  3. Autoevaluación  — las 11 competencias que la oferta pide puntuar de 1 a 5
  4. Descartes       — la lista de "no apliques si..." de la oferta
  5. Cierre          — "por qué eres la persona ideal", que es lo que pide
                       literalmente el campo del vídeo

Salida: video/carlos-delatorre-omnidental-60s.mp4  (1920x1080, 30 fps, 60 s)
Uso:    python3 video/make_video.py --photo ruta/a/foto.jpg
"""

import argparse
import math
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1920, 1080
FPS = 30

# Duración por defecto y reparto original de escenas. Si se pasa --timings, la
# línea de tiempo se reconstruye sobre las fronteras reales de la locución.
BASE_BOUNDS = [0.0, 8.5, 23.5, 35.5, 46.5, 60.0]
SCENE_ORDER = ["intro", "results", "selfrate", "filters", "close"]

DURATION = BASE_BOUNDS[-1]
TOTAL = int(DURATION * FPS)

# Paleta clara, alineada con el CV (blanco + azul corporativo)
BG = (245, 248, 252)
CARD = (255, 255, 255)
BORDER = (219, 228, 241)
BLUE = (10, 102, 194)
BLUE_DEEP = (7, 74, 143)
BLUE_SOFT = (232, 240, 253)
CYAN = (8, 145, 178)
GREEN = (5, 150, 105)
AMBER = (194, 120, 3)
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


def font(weight, size):
    key = (weight, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(_FONTS[weight], size)
    return _cache[key]


# ---------------------------------------------------------------- utilidades

def ease_out(t):
    """Cubic ease-out, acotada a [0, 1]."""
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def appear(now, start, dur=0.55):
    """Progreso 0..1 de una entrada que arranca en `start` segundos."""
    return ease_out((now - start) / dur)


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def fade(color, alpha):
    """Opacidad simulada mezclando contra el fondo claro (sin capas RGBA)."""
    return mix(BG, color, alpha)


def text_w(draw, s, f):
    return draw.textbbox((0, 0), s, font=f)[2]


def rrect(draw, box, radius, fill=None, outline=None, width=2):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def card(draw, box, alpha, radius=22, accent=None, accent_w=6):
    """Tarjeta blanca con borde suave y, opcionalmente, filo de color."""
    rrect(draw, box, radius, fill=fade(CARD, alpha), outline=fade(BORDER, alpha), width=2)
    if accent:
        x0, y0, _, y1 = box
        draw.rounded_rectangle((x0, y0 + 12, x0 + accent_w, y1 - 12),
                               radius=accent_w // 2, fill=fade(accent, alpha))


def chip(draw, x, y, label, f, fg, bg_col, pad=(24, 13)):
    tw = text_w(draw, label, f)
    box = (x, y, x + tw + pad[0] * 2, y + f.size + pad[1] * 2)
    rrect(draw, box, (box[3] - box[1]) // 2, fill=bg_col)
    draw.text((x + pad[0], y + pad[1] - 2), label, font=f, fill=fg)
    return box[2] - box[0]


def arrow(d, x, y, length, color, width=4):
    """Flecha horizontal vectorial (Roboto no trae el glifo U+2192)."""
    d.line([(x, y), (x + length, y)], fill=color, width=width)
    d.line([(x + length - 14, y - 11), (x + length, y)], fill=color, width=width)
    d.line([(x + length - 14, y + 11), (x + length, y)], fill=color, width=width)


def check(d, cx, cy, r, color, width=5):
    """Marca de verificación dentro de un círculo."""
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=color, width=3)
    d.line([(cx - r * 0.42, cy), (cx - r * 0.08, cy + r * 0.36)], fill=color, width=width)
    d.line([(cx - r * 0.08, cy + r * 0.36), (cx + r * 0.46, cy - r * 0.34)],
           fill=color, width=width)


def dots(d, x, y, score, alpha, r=13, gap=38, on=BLUE):
    """Puntuación 1-5 en bolitas: rellenas = nivel declarado."""
    for i in range(5):
        cx = x + i * gap
        if i < score:
            d.ellipse((cx - r, y - r, cx + r, y + r), fill=fade(on, alpha))
        else:
            d.ellipse((cx - r, y - r, cx + r, y + r), outline=fade(DIM, alpha * 0.7), width=3)


def waveform(d, cx, cy, half_w, phase, color, alpha, bars=44):
    """Onda de voz animada — señal visual de 'agente conversacional'."""
    gap = (2 * half_w) / (bars - 1)
    for i in range(bars):
        x = cx - half_w + i * gap
        k = math.sin(phase * 2.6 + i * 0.55) * math.sin(phase * 1.1 + i * 0.19)
        env = math.sin(math.pi * i / (bars - 1)) ** 0.6      # se apaga en los bordes
        h = 8 + abs(k) * 70 * env
        d.rounded_rectangle((x - 4, cy - h / 2, x + 4, cy + h / 2),
                            radius=4, fill=fade(color, alpha * (0.35 + 0.65 * env)))


def fmt_number(value, suffix=""):
    """34000 → '34.000' (separador de miles español)."""
    return f"{int(round(value)):,}".replace(",", ".") + suffix


# ------------------------------------------------------------------- fondo

def build_background():
    """Fondo claro: degradado sutil + dos halos azules muy tenues."""
    bg = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(bg)
    for y in range(H):
        d.line([(0, y), (W, y)], fill=mix((252, 253, 255), (234, 241, 250), y / H))

    glow = Image.new("RGB", (W, H), (255, 255, 255))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-420, -560, 1120, 560), fill=(206, 226, 250))
    gd.ellipse((1280, 700, 2320, 1560), fill=(214, 240, 244))
    glow = glow.filter(ImageFilter.GaussianBlur(200))
    return Image.blend(bg, glow, 0.5)


# -------------------------------------------------------------------- foto

def build_photo(path, size, ring=BLUE, ring_w=7):
    """Recorte cuadrado centrado en el rostro → círculo con anillo azul."""
    src = Image.open(path).convert("RGB")
    w, h = src.size
    side = min(w, h)
    left = (w - side) // 2
    top = int((h - side) * 0.06)              # sube el encuadre hacia la cara
    src = src.crop((left, top, left + side, top + side))

    ss = size * 3                              # supersampling: bordes limpios
    src = src.resize((ss, ss), Image.LANCZOS)
    mask = Image.new("L", (ss, ss), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, ss - 1, ss - 1), fill=255)

    pad = ring_w * 3 + 36
    canvas = Image.new("RGBA", (ss + pad * 2, ss + pad * 2), (0, 0, 0, 0))

    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).ellipse(
        (pad - 10, pad + 6, pad + ss + 10, pad + ss + 26), fill=(20, 44, 82, 74)
    )
    canvas = Image.alpha_composite(canvas, shadow.filter(ImageFilter.GaussianBlur(34)))

    ring_box = (pad - ring_w * 3, pad - ring_w * 3,
                pad + ss + ring_w * 3, pad + ss + ring_w * 3)
    rd = ImageDraw.Draw(canvas)
    rd.ellipse(ring_box, outline=(255, 255, 255, 255), width=ring_w * 5)  # borde blanco
    rd.ellipse(ring_box, outline=ring + (255,), width=ring_w * 3)         # aro azul
    canvas.paste(src, (pad, pad), mask)
    return canvas.resize((size + (pad * 2) // 3,) * 2, Image.LANCZOS)


def paste_photo(base, photo, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0.01:
        return
    im = photo
    if scale != 1.0:
        s = max(1, int(photo.width * scale))
        im = photo.resize((s, s), Image.LANCZOS)
    if alpha < 1.0:
        im = im.copy()
        im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    base.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)


# ------------------------------------------------------------------- guion

# (nombre, inicio, fin, factor). El factor reajusta el reloj interno de la
# escena: si dura más que en el reparto original, sus animaciones se reparten
# por todo el hueco en vez de terminar pronto y dejar la imagen congelada.
SCENES = []


def set_timeline(bounds):
    """Reconstruye SCENES, DURATION y TOTAL a partir de las fronteras dadas."""
    global SCENES, DURATION, TOTAL
    if len(bounds) != len(SCENE_ORDER) + 1:
        raise ValueError(f"hacen falta {len(SCENE_ORDER) + 1} tiempos, "
                         f"recibidos {len(bounds)}")
    SCENES = []
    for i, name in enumerate(SCENE_ORDER):
        base = BASE_BOUNDS[i + 1] - BASE_BOUNDS[i]
        actual = bounds[i + 1] - bounds[i]
        if actual <= 0:
            raise ValueError(f"la escena {name} no tiene duración positiva")
        SCENES.append((name, bounds[i], bounds[i + 1], base / actual))
    DURATION = bounds[-1]
    TOTAL = int(round(DURATION * FPS))


set_timeline(BASE_BOUNDS)

# Escena 2 — los "resultados esperados" que enumera la oferta, con la evidencia
RESULTS = [
    ("Ecosistema de voz de alto rendimiento",
     "Voz en tiempo real en producción · latencia medida", BLUE),
    ("Fuera la gestión manual de datos",
     "De 45 min a 3 · 183 tablas en vez de hojas", CYAN),
    ("Aceleración técnica con Claude Code",
     "Uso diario · Partner Anthropic · 7 certificaciones", BLUE),
    ("Cloud escalable con Make / n8n",
     "34.000 tareas/mes · 37 contenedores por 13 €/mes", GREEN),
]

# Escena 3 — las 11 competencias que la oferta pide autoevaluar del 1 al 5
SELF_RATING = [
    ("Claude Code", 5), ("Dashboards y análisis", 5),
    ("APIs de IA generativa", 5), ("Next.js", 5),
    ("Chatbots y asistentes IA", 5), ("Make", 5),
    ("PostgreSQL", 5), ("Firebase", 5),
    ("Documentación de procesos", 5), ("Retell AI", 5),
    ("HighLevel", 5),
]

# Escena 4 — la lista de "no apliques si..." de la oferta, respondida
FILTERS = [
    ("«Necesitas supervisión constante»",
     "9 agentes autónomos que diseñé sin que me los pidieran"),
    ("«Te incomoda la terminal, los repos o la nube»",
     "31 años en terminal · 2 servidores levantados desde cero"),
    ("«Sin experiencia real en voz o arquitectura cloud»",
     "Voz en tiempo real · 23 endpoints HTTPS en producción"),
    ("«Cómodo trabajando con hojas de cálculo»",
     "Las sustituí por 930 APIs y dashboards en vivo"),
]

# Escena 5 — respuesta a "por qué eres la persona ideal"
REASONS = [
    "Ya he construido lo que pedís, y está en producción.",
    "31 años de infraestructura: sé por qué se rompen las cosas.",
    "Detecto la ineficiencia y la cierro sin que me la asignen.",
]


def draw_intro(base, d, now, t0, photo):
    n = now - t0
    a = appear(n, 0.15)
    d.text((150, 168), "OMNI DENTAL · ESPECIALISTA Y LÍDER EN IA Y AUTOMATIZACIONES",
           font=font("bold", 27), fill=fade(BLUE, a))
    d.line([(150, 216), (150 + int(700 * ease_out(n / 0.9)), 216)],
           fill=fade(BLUE, a * 0.45), width=3)

    for i, (line, delay) in enumerate([("Carlos", 0.45), ("De La Torre", 0.62)]):
        av = appear(n, delay)
        d.text((150, 268 + i * 134 + int(46 * (1 - av))), line,
               font=font("black", 132), fill=fade(TEXT, av))

    a_r = appear(n, 0.95)
    d.text((150, 566 + int(30 * (1 - a_r))), "Arquitecto de Inteligencia Artificial",
           font=font("medium", 50), fill=fade(BLUE, a_r))
    d.text((150, 632 + int(30 * (1 - a_r))),
           "Vuestra oferta, punto por punto, respondida en 60 segundos",
           font=font("light", 34), fill=fade(MUTED, a_r))

    x = 150
    for i, label in enumerate(["Madrid · 100% remoto",
                               "Anthropic Claude Partner",
                               "Dedicación exclusiva"]):
        av = appear(n, 1.35 + i * 0.16)
        if av <= 0.01:
            continue
        x += chip(d, x, 728, label, font("medium", 30),
                  fade(BLUE_DEEP, av), fade(BLUE_SOFT, av)) + 20

    a_ph = appear(n, 0.3, 0.9)
    paste_photo(base, photo, 1530, 486, alpha=a_ph,
                scale=0.94 + 0.06 * a_ph + 0.012 * math.sin(n * 1.1))


def draw_results(base, d, now, t0, photo):
    n = now - t0
    d.text((150, 92), "Los resultados que esperáis",
           font=font("black", 78), fill=fade(TEXT, appear(n, 0.1)))
    d.text((150, 200), "Vuestra propia lista. Al lado, lo que ya tengo funcionando.",
           font=font("light", 38), fill=fade(MUTED, appear(n, 0.35)))

    a_w = appear(n, 0.5, 0.8)
    if a_w > 0.01:
        waveform(d, 960, 306, 560, n, BLUE, a_w * 0.6)

    cw, ch, gx, gy, x0, y0 = 796, 194, 44, 32, 150, 396
    for i, (goal, proof, color) in enumerate(RESULTS):
        av = appear(n, 1.0 + i * 0.85, 0.6)
        if av <= 0.01:
            continue
        cx = x0 + (i % 2) * (cw + gx)
        cy = y0 + (i // 2) * (ch + gy) + int(34 * (1 - av))
        card(d, (cx, cy, cx + cw, cy + ch), av, accent=color)
        d.text((cx + 40, cy + 34), goal, font=font("medium", 32), fill=fade(DIM, av))
        d.text((cx + 40, cy + 100), proof, font=font("bold", 31), fill=fade(TEXT, av))

        a_ok = appear(n, 1.0 + i * 0.85 + 0.4, 0.4)
        if a_ok > 0.01:
            check(d, cx + cw - 58, cy + 52, 22, fade(color, a_ok))


def draw_selfrate(base, d, now, t0, photo):
    n = now - t0
    d.text((150, 88), "Vuestras 11 competencias",
           font=font("black", 74), fill=fade(TEXT, appear(n, 0.1)))
    d.text((150, 192), "Las 11 competencias que pedís puntuar del 1 al 5",
           font=font("light", 36), fill=fade(MUTED, appear(n, 0.3)))

    col_x, y0, rh = (150, 1000), 296, 68
    for i, (label, score) in enumerate(SELF_RATING):
        av = appear(n, 0.6 + i * 0.16, 0.45)
        if av <= 0.01:
            continue
        x = col_x[i // 6]
        y = y0 + (i % 6) * rh
        col = GREEN if score >= 5 else (BLUE if score >= 4 else AMBER)
        d.text((x, y - 20), label, font=font("medium", 34), fill=fade(TEXT, av))
        dots(d, x + 590, y, score, av, on=col)

    a_n = appear(n, 2.9, 0.7)
    if a_n > 0.01:
        card(d, (150, 730, 1770, 862), a_n, accent=GREEN)
        d.text((196, 758), "Cinco en todas, y todas verificables",
               font=font("bold", 38), fill=fade(TEXT, a_n))
        d.text((196, 812), "Firebase en Stratos Trade y los bots de trading · repos públicos en GitHub",
               font=font("regular", 30), fill=fade(MUTED, a_n))


def draw_filters(base, d, now, t0, photo):
    n = now - t0
    d.text((150, 92), "Vuestra lista de descartes",
           font=font("black", 76), fill=fade(TEXT, appear(n, 0.1)))
    d.text((150, 200), "«No apliques si…» — la leí entera. Ninguno me aplica.",
           font=font("light", 38), fill=fade(MUTED, appear(n, 0.3)))

    rh = 148
    for i, (rule, answer) in enumerate(FILTERS):
        av = appear(n, 0.8 + i * 0.62, 0.55)
        if av <= 0.01:
            continue
        top = 300 + i * rh + int(30 * (1 - av))
        card(d, (150, top, 1770, top + rh - 22), av, radius=18, accent=GREEN)
        check(d, 214, top + 62, 24, fade(GREEN, av))
        d.text((272, top + 26), rule, font=font("regular", 31), fill=fade(DIM, av))
        d.text((272, top + 72), answer, font=font("bold", 35), fill=fade(TEXT, av))


def draw_close(base, d, now, t0, photo):
    n = now - t0
    paste_photo(base, photo, 386, 396, alpha=appear(n, 0.05, 0.7), scale=0.58)

    a_id = appear(n, 0.5, 0.7)
    if a_id > 0.01:
        for txt, f, col, y in (("Carlos De La Torre", font("bold", 44), TEXT, 626),
                               ("Arquitecto de IA · Madrid", font("regular", 32), MUTED, 690)):
            d.text((386 - text_w(d, txt, f) / 2, y), txt, font=f, fill=fade(col, a_id))

    d.text((690, 132), "Por qué soy la persona ideal",
           font=font("black", 68), fill=fade(TEXT, appear(n, 0.2)))

    for i, reason in enumerate(REASONS):
        av = appear(n, 0.7 + i * 0.55, 0.55)
        if av <= 0.01:
            continue
        y = 250 + i * 92 + int(26 * (1 - av))
        d.ellipse((694, y + 14, 710, y + 30), fill=fade(BLUE, av))
        d.text((738, y), reason, font=font("medium", 37), fill=fade(TEXT, av))

    a_q = appear(n, 2.5, 0.7)
    if a_q > 0.01:
        card(d, (690, 552, 1790, 682), a_q, accent=GREEN)
        d.text((736, 586), "«Sin prueba, no está hecho»",
               font=font("black", 56), fill=fade(GREEN, a_q))

    a_c = appear(n, 3.1)
    d.text((690, 738 + int(24 * (1 - a_c))), "Hablemos.",
           font=font("black", 88), fill=fade(TEXT, a_c))

    for i, (line, col) in enumerate([
        ("radelqui@gmail.com", BLUE),
        ("+34 745 03 71 90", TEXT),
        ("sypnose.cloud/portfolio/carlos", MUTED),
    ]):
        av = appear(n, 3.5 + i * 0.2)
        if av <= 0.01:
            continue
        d.text((694, 866 + i * 54), line, font=font("medium", 32), fill=fade(col, av))


DRAW = {
    "intro": draw_intro,
    "results": draw_results,
    "selfrate": draw_selfrate,
    "filters": draw_filters,
    "close": draw_close,
}


def render_frame(idx, bg, photo):
    now = idx / FPS
    base = bg.copy()
    d = ImageDraw.Draw(base)

    for name, start, end, k in SCENES:
        if start <= now < end:
            # El reloj de la escena se escala para que las entradas ocupen
            # todo el hueco disponible, sea cual sea su duración real.
            DRAW[name](base, d, start + (now - start) * k, start, photo)
            tail = end - now
            if tail < 0.25 and end < DURATION:      # fundido entre escenas
                k = (1 - tail / 0.25) * 0.9
                base = Image.blend(base, Image.new("RGB", (W, H), BG), k)
                d = ImageDraw.Draw(base)
            break

    d.line([(0, H - 6), (W, H - 6)], fill=BORDER, width=6)
    d.line([(0, H - 6), (int(W * now / DURATION), H - 6)], fill=BLUE, width=6)
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--photo", required=True)
    ap.add_argument("--out", default="video/carlos-delatorre-omnidental-60s.mp4")
    ap.add_argument("--frames", default="/tmp/vid_frames")
    ap.add_argument("--timings", help="fronteras de escena en segundos, separadas "
                                      "por comas: 0,10.9,29.7,43.6,55.4,71.5")
    args = ap.parse_args()

    if args.timings:
        set_timeline([float(x) for x in args.timings.split(",")])
        print("Línea de tiempo:")
        for name, a, b, k in SCENES:
            print(f"  {name:9s} {a:6.2f} -> {b:6.2f}s  ({b - a:5.2f}s, x{k:.3f})")

    if not os.path.exists(args.photo):
        sys.exit(f"No encuentro la foto: {args.photo}")

    shutil.rmtree(args.frames, ignore_errors=True)
    os.makedirs(args.frames, exist_ok=True)
    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)

    print("Preparando fondo y foto...")
    bg = build_background()
    photo = build_photo(args.photo, 620)

    print(f"Renderizando {TOTAL} frames...")
    for i in range(TOTAL):
        render_frame(i, bg, photo).save(f"{args.frames}/f{i:05d}.png", compress_level=1)
        if i % 150 == 0:
            print(f"  {i}/{TOTAL}  ({i / FPS:.1f}s)")

    print("Codificando MP4...")
    subprocess.run([
        "ffmpeg", "-y", "-loglevel", "error",
        "-framerate", str(FPS), "-i", f"{args.frames}/f%05d.png",
        "-c:v", "libx264", "-preset", "slow", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        args.out,
    ], check=True)

    shutil.rmtree(args.frames, ignore_errors=True)
    print(f"Listo: {args.out}  ({os.path.getsize(args.out) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
