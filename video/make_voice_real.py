#!/usr/bin/env python3
"""
Monta la locución grabada por Carlos sobre el vídeo.

La grabación llega como una sola toma continua, más larga que el minuto del
montaje original. En vez de acelerar la voz para que quepa —que suena a prisa—,
aquí se hace al revés: se localizan las fronteras entre los cinco bloques del
guion y el vídeo se regenera con esas duraciones. Manda la voz.

Las fronteras salen de transcribir la grabación con marcas de tiempo por
palabra. Una primera versión las buscaba sólo por energía —la pausa más larga
cerca de donde el reparto de palabras decía que debía caer el corte— y falló
por cuatro segundos en el tercero: cogió una pausa interna del bloque en vez
de la que lo cierra. Con la transcripción el hueco entre bloques es
observable, no inferido.

Requisitos:
    pip install faster-whisper

Uso:
    python3 video/make_voice_real.py --audio grabacion.m4a --photo foto.jpg
"""

import argparse
import os
import subprocess
import sys

# Palabras de cada bloque del guion (ver texto-para-grabar.txt)
WORDS = [23, 44, 28, 32, 38]

SEARCH = 4.0         # cuánto se busca el hueco alrededor del punto esperado
HEAD = 0.45          # aire que se deja antes de la primera palabra
TAIL = 1.60          # aire tras la última palabra, para que respire el cierre
MODEL = "small"      # suficiente: sólo interesan las marcas de tiempo


def transcribe(audio):
    """Devuelve las palabras con marca de tiempo. Los errores de la
    transcripción dan igual: sólo se usan los tiempos, no el texto."""
    from faster_whisper import WhisperModel

    model = WhisperModel(MODEL, device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio, language="es",
                                   word_timestamps=True, vad_filter=False)
    words = []
    for seg in segments:
        words.extend(seg.words or [])
    if len(words) < sum(WORDS) * 0.6:
        sys.exit(f"La transcripción sólo reconoció {len(words)} palabras de "
                 f"~{sum(WORDS)}. Revisa la grabación.")
    return words


def find_gap(words, center):
    """El hueco más largo entre palabras consecutivas cerca de `center`."""
    best = None
    for a, b in zip(words, words[1:]):
        mid = (a.end + b.start) / 2
        if abs(mid - center) > SEARCH:
            continue
        gap = b.start - a.end
        if best is None or gap > best[1]:
            best = (mid, gap)
    return best


def locate_blocks(audio):
    """Fronteras entre los cinco bloques del guion, en segundos."""
    words = transcribe(audio)
    start, end = words[0].start, words[-1].end
    print(f"Transcritas {len(words)} palabras · voz de {start:.2f}s a {end:.2f}s\n")

    bounds, acc = [], 0
    for n in WORDS[:-1]:
        acc += n
        # El índice de palabra es mejor guía que el tiempo: absorbe los
        # cambios de ritmo entre bloques.
        idx = min(len(words) - 1, round(len(words) * acc / sum(WORDS)))
        center = words[idx].end
        found = find_gap(words, center)
        if found is None:
            sys.exit(f"No encuentro el corte cerca de {center:.2f}s.")
        cut, gap = found
        bounds.append(cut)
        print(f"  corte {len(bounds)}: esperado ~{center:6.2f}s -> "
              f"{cut:6.2f}s (hueco de {gap:.2f}s)")

    if any(b >= c for b, c in zip(bounds, bounds[1:])):
        sys.exit(f"Los cortes no salen en orden: {bounds}")
    return start, end, bounds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audio", required=True, help="la grabación tal cual salga del móvil")
    ap.add_argument("--photo", required=True)
    ap.add_argument("--video", default="video/carlos-delatorre-omnidental.mp4")
    ap.add_argument("--wav", default="video/locucion-carlos.wav")
    args = ap.parse_args()

    for path in (args.audio, args.photo):
        if not os.path.exists(path):
            sys.exit(f"No encuentro: {path}")

    start, end, bounds = locate_blocks(args.audio)

    # La línea de tiempo del vídeo, ya con los silencios extremos recortados
    offset = max(0.0, start - HEAD)
    timeline = [0.0] + [b - offset for b in bounds] + [end - offset + TAIL]
    print("\nLínea de tiempo del vídeo:")
    for i, name in enumerate(["intro", "resultados", "competencias",
                              "descartes", "cierre"]):
        print(f"  {name:13s} {timeline[i]:6.2f} -> {timeline[i + 1]:6.2f}s "
              f"({timeline[i + 1] - timeline[i]:5.2f}s)")
    print(f"  TOTAL {timeline[-1]:.2f}s")

    # Voz limpia: fuera el retumbe por debajo de 80 Hz, reducción suave de
    # ruido y nivel de locución con techo a -1.5 dBTP.
    print("\nLimpiando la voz...")
    subprocess.run([
        "ffmpeg", "-v", "error", "-y",
        "-ss", f"{offset:.3f}", "-t", f"{timeline[-1]:.3f}", "-i", args.audio,
        "-af", "highpass=f=80,afftdn=nr=12:nf=-32,"
               "loudnorm=I=-16:TP=-1.5:LRA=11,"
               f"apad=whole_dur={timeline[-1]:.3f}",
        "-ac", "1", "-ar", "44100", args.wav,
    ], check=True)

    print("Regenerando el vídeo con esta duración...")
    subprocess.run([
        sys.executable, "video/make_video.py",
        "--photo", args.photo,
        "--out", args.video,
        "--timings", ",".join(f"{t:.3f}" for t in timeline),
    ], check=True)

    out = args.video.replace(".mp4", "-con-voz.mp4")
    print("Mezclando...")
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-i", args.video, "-i", args.wav,
        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
        "-shortest", "-movflags", "+faststart", out,
    ], check=True)

    print(f"\nListo: {out}  ({os.path.getsize(out) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
