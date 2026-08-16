# Vídeo de candidatura — Omni Dental · Especialista y Líder en IA y Automatizaciones

Vídeo de 1 minuto **con locución en español** para el campo del formulario que
pide *«un vídeo de 1 minuto presentándote y contándonos por qué crees que eres
la persona ideal para este puesto»*.

### Lo que se sube al formulario

| Archivo | Qué es |
|---|---|
| **`carlos-delatorre-omnidental-60s.gif`** | **El vídeo, en un formato que el campo sí acepta.** 960x540, 12 fps, 5,9 MB |
| **`caratula-video-omnidental.pdf`** | Una página con enlace + QR al HD con voz, fotogramas y escaleta |

### Los originales

| Archivo | Qué es |
|---|---|
| `carlos-delatorre-omnidental-60s-con-voz.mp4` | El máster: 1920x1080, 30 fps, 60 s, con locución |
| `carlos-delatorre-omnidental-60s.mp4` | La misma pieza sin audio (es la fuente del GIF) |
| `locucion.wav` | Solo la pista de voz, alineada al minuto |
| `guion-voz-en-off.md` | El guion, escena a escena, con sus tiempos |
| `make_video.py` · `make_voice.py` · `make_gif.py` · `make_caratula.py` | Los cuatro generadores |

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

# 3. El GIF que se sube al formulario
python3 make_gif.py

# 4. La carátula PDF (pip install qrcode)
python3 make_caratula.py --url https://youtu.be/XXXX --photo /ruta/foto.jpg
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

## El problema del campo de subida, y cómo se resuelve

El campo del vídeo es **obligatorio** y sólo acepta PDF, DOC/DOCX, XLS/CSV,
JPG/JPEG, PNG y GIF. En el HTML de la página, ese campo y el de «Subir
Currículum» llevan **exactamente la misma cadena de formatos**: es el
componente de subida por defecto de su generador de formularios, pegado dos
veces sin ajustarle los tipos al del vídeo.

La salida no es pedir una excepción, es que **el campo acepta GIF y un GIF es
vídeo**. Y admite hasta 10 archivos, así que van los dos:

1. `carlos-delatorre-omnidental-60s.gif` — la pieza entera, que se reproduce
   sin salir del formulario y sin depender de ningún enlace externo.
2. `caratula-video-omnidental.pdf` — enlace y QR a la versión en HD con
   locución, más los fotogramas y la escaleta.

Lo único que pierde el GIF es el audio, no el mensaje: la pieza se diseñó para
leerse en silencio, con todo el contenido en pantalla.

## Antes de enviarlo

1. **Sube el MP4 con voz a algún sitio** (YouTube no listado, Drive, Loom) y
   regenera la carátula con esa URL:
   `python3 make_caratula.py --url https://... --photo /ruta/foto.jpg`.
   Ahora mismo apunta al portfolio, que funciona, pero no es el vídeo.
2. **Escúchalo entero una vez.** La voz es sintética (Piper). Suena natural,
   pero si prefieres que sea la tuya, usa la versión sin audio y el guion
   cronometrado de `guion-voz-en-off.md`.
3. **Revisa que las cifras siguen vigentes** (clientes, tareas/mes, contenedores)
   antes de enviarlo: van en pantalla y te las pueden preguntar en la entrevista.
