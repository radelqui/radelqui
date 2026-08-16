#!/usr/bin/env python3
"""
Genera la locución en español del vídeo y la monta sobre el MP4.

Sintetiza cada escena por separado con Piper y la coloca en su hueco exacto
del minuto. Si una frase no cabe en su escena, se vuelve a sintetizar más
rápida (`length_scale`) hasta que entra — así el audio nunca pisa la escena
siguiente.

Requisitos:
    pip install piper-tts
    modelo de voz .onnx + .onnx.json  (por defecto es_ES-davefx-medium)

Uso:
    python3 video/make_voice.py --model /ruta/es_ES-davefx-medium.onnx
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import wave

# (inicio en segundos, fin en segundos, texto) — los tiempos son los de SCENES
# en make_video.py. El texto lleva los números escritos en palabras para que
# el sintetizador no los lea en inglés ni los deletree.
NARRATION = [
    (0.0, 8.5,
     "Hola, soy Carlos De La Torre, arquitecto de inteligencia artificial. "
     "He leído vuestra oferta entera, y voy a responderla punto por punto."),

    (8.5, 23.5,
     "Empiezo por los resultados que esperáis. Voz en tiempo real, ya en producción. "
     "Fuera las hojas de cálculo: un proceso de cuarenta y cinco minutos, bajado a tres. "
     "Claude Code a diario, partner de Anthropic. "
     "Y treinta y cuatro mil tareas automatizadas al mes."),

    (23.5, 35.5,
     "Vuestras once competencias, del uno al cinco: cinco en todas. "
     "Claude Code, APIs de IA, chatbots, PostgreSQL, Firebase. "
     "No es una promesa: es lo que hago cada día."),

    (35.5, 46.5,
     "Vuestra lista de descartes también la leí, y ninguno me aplica. "
     "Nueve agentes que diseñé sin que me los pidieran. "
     "Treinta y un años en terminal, y dos servidores levantados desde cero."),

    (46.5, 60.0,
     "¿Por qué soy la persona ideal? Porque ya he construido lo que pedís, "
     "y está funcionando en producción, no en una demo. "
     "Y porque trabajo con una regla que aprendí en banca regulada: "
     "sin prueba, no está hecho. Hablemos."),
]

LEAD_IN = 0.35       # silencio al empezar cada escena, para que no atropelle
TAIL = 0.30          # margen antes de que entre la escena siguiente


def synth(text, model, out_path, length_scale):
    """Sintetiza `text` a WAV. Devuelve su duración en segundos."""
    cmd = [sys.executable, "-m", "piper", "-m", model, "-f", out_path,
           "--length-scale", f"{length_scale:.3f}"]
    subprocess.run(cmd, input=text.encode("utf-8"), check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with wave.open(out_path) as w:
        return w.getnframes() / w.getframerate()


def fit_scene(text, model, out_path, budget):
    """Sintetiza ajustando la velocidad hasta que la frase quepa en `budget`."""
    scale = 1.0
    for attempt in range(6):
        dur = synth(text, model, out_path, scale)
        if dur <= budget:
            return dur, scale
        # Piper escala casi lineal con length_scale: corrige y deja 3% de aire
        scale *= budget / dur * 0.97
        scale = max(scale, 0.55)          # por debajo suena atropellado
        print(f"    ajuste {attempt + 1}: {dur:.2f}s > {budget:.2f}s "
              f"-> length_scale {scale:.3f}")
    return dur, scale


def read_wav(path):
    with wave.open(path) as w:
        assert w.getsampwidth() == 2, "se esperaba PCM de 16 bits"
        return w.getframerate(), w.getnchannels(), w.readframes(w.getnframes())


def build_track(clips, total_seconds, out_path):
    """Coloca cada clip en su offset dentro de una pista silenciosa."""
    rate, channels, _ = read_wav(clips[0][1])
    frame_bytes = 2 * channels
    buf = bytearray(int(total_seconds * rate) * frame_bytes)

    for offset_s, path in clips:
        r, ch, data = read_wav(path)
        assert (r, ch) == (rate, channels), "los clips no comparten formato"
        start = int(offset_s * rate) * frame_bytes
        end = min(start + len(data), len(buf))
        buf[start:end] = data[:end - start]

    with wave.open(out_path, "wb") as w:
        w.setnchannels(channels)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(buf))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="ruta al .onnx de la voz Piper")
    ap.add_argument("--video", default="video/carlos-delatorre-omnidental-60s.mp4")
    ap.add_argument("--out", default="video/carlos-delatorre-omnidental-60s-con-voz.mp4")
    ap.add_argument("--wav", default="video/locucion.wav")
    args = ap.parse_args()

    for path in (args.model, args.video):
        if not os.path.exists(path):
            sys.exit(f"No encuentro: {path}")

    tmp = tempfile.mkdtemp(prefix="voz_")
    clips = []
    try:
        for i, (start, end, text) in enumerate(NARRATION):
            budget = (end - start) - LEAD_IN - TAIL
            print(f"Escena {i + 1}: hueco {end - start:.1f}s, presupuesto {budget:.1f}s")
            path = os.path.join(tmp, f"s{i}.wav")
            dur, scale = fit_scene(text, args.model, path, budget)
            print(f"  -> {dur:.2f}s (length_scale {scale:.3f})")
            clips.append((start + LEAD_IN, path))

        print("Montando la pista completa...")
        build_track(clips, 60.0, args.wav)

        print("Mezclando audio y vídeo...")
        subprocess.run([
            "ffmpeg", "-y", "-loglevel", "error",
            "-i", args.video, "-i", args.wav,
            # loudnorm deja la voz al nivel habitual de locución y con techo
            # a -1.5 dBTP, para que ningún reproductor la sature
            "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
            "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-ac", "1", "-shortest", "-movflags", "+faststart",
            args.out,
        ], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"Listo: {args.out}  ({os.path.getsize(args.out) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
