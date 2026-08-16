# Vídeo de candidatura — Omni Dental · Especialista y Líder en IA y Automatizaciones

Vídeo de 1 minuto **con locución en español** para el campo del formulario que
pide *«un vídeo de 1 minuto presentándote y contándonos por qué crees que eres
la persona ideal para este puesto»*.

| Archivo | Qué es |
|---|---|
| **`carlos-delatorre-omnidental-60s-con-voz.mp4`** | **El vídeo final, con voz.** 1920x1080, 30 fps, 60 s exactos |
| `carlos-delatorre-omnidental-60s.mp4` | La misma pieza sin audio, por si prefieres grabar tu propia voz |
| `locucion.wav` | Solo la pista de voz, alineada al minuto |
| `guion-voz-en-off.md` | El guion, escena a escena, con sus tiempos |
| `make_video.py` | Generador del vídeo |
| `make_voice.py` | Generador de la locución + mezcla con el vídeo |

## La idea

El vídeo no es una presentación genérica: **cada escena responde a una sección
literal del anuncio**, en su mismo orden y con su mismo vocabulario.

| Escena | Tiempo | Responde a |
|---|---|---|
| Intro | 0:00 – 0:08,5 | Quién soy y a qué oferta me presento |
| Los resultados que esperáis | 0:08,5 – 0:23,5 | Su sección «Resultados esperados» |
| Vuestras 11 competencias | 0:23,5 – 0:35,5 | Las 11 competencias que piden puntuar del 1 al 5 |
| Vuestra lista de descartes | 0:35,5 – 0:46,5 | Su lista «No apliques si…» |
| Por qué soy la persona ideal | 0:46,5 – 1:00 | La pregunta literal del campo del vídeo |

## Regenerar el vídeo

```bash
pip install pillow piper-tts
sudo apt-get install -y ffmpeg fonts-roboto

# 1. La pieza visual (1.800 frames con Pillow + libx264)
python3 make_video.py --photo /ruta/a/tu/foto.jpg

# 2. La locución, ajustada escena a escena, y la mezcla final
python3 make_voice.py --model /ruta/es_ES-davefx-medium.onnx
```

La voz es el modelo Piper `es_ES-davefx-medium`, que se descarga de
[rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices/tree/main/es/es_ES/davefx/medium)
(hacen falta el `.onnx` y su `.onnx.json`).

`make_voice.py` mide cada frase y, si no cabe en su escena, la vuelve a
sintetizar algo más rápida hasta que entra — así el audio nunca pisa la escena
siguiente. La mezcla final pasa por `loudnorm` (I=-16, TP=-1.5 dB), que es el
estándar de locución.

Para cambiar el contenido, edita las listas del bloque `# guion` en
`make_video.py` (`RESULTS`, `SELF_RATING`, `FILTERS`, `REASONS`) y los textos de
`NARRATION` en `make_voice.py`. El resto de la maquetación se recoloca sola.

## Antes de enviarlo

1. **El formulario no acepta MP4.** Los formatos admitidos en ese campo son PDF,
   DOC/DOCX, XLS/CSV, JPG/JPEG, PNG y GIF. Sube el vídeo a YouTube como *no
   listado*, a Drive o a Loom, y pega el enlace donde el formulario lo permita.
2. **Escúchalo entero una vez.** La voz es sintética (Piper). Suena natural,
   pero si prefieres que sea la tuya, usa `carlos-delatorre-omnidental-60s.mp4`
   —el mismo vídeo sin audio— y el guion cronometrado de `guion-voz-en-off.md`.
3. **Revisa que las cifras siguen vigentes** (clientes, tareas/mes, contenedores)
   antes de enviarlo: van en pantalla y te las pueden preguntar en la entrevista.
