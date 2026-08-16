# Vídeo de candidatura — Omni Dental · Especialista y Líder en IA y Automatizaciones

Vídeo de **1:11 con la voz de Carlos** para el campo del formulario que pide
*«un vídeo de 1 minuto presentándote y contándonos por qué crees que eres la
persona ideal para este puesto»*.

### Lo que se sube al formulario

| Archivo | Qué es |
|---|---|
| **`carlos-delatorre-omnidental.gif`** | **El vídeo, en un formato que el campo sí acepta.** 960x540, 12 fps, 6,7 MB |
| **`caratula-video-omnidental.pdf`** | **El vídeo se reproduce con un clic dentro del PDF** (4,70 MB) |

### Los originales

| Archivo | Qué es |
|---|---|
| `carlos-delatorre-omnidental-con-voz.mp4` | El máster: 1920x1080, 30 fps, 71,9 s |
| `carlos-delatorre-omnidental.mp4` | La misma pieza sin audio (es la fuente del GIF) |
| `locucion-carlos.wav` | Solo la voz, ya limpia y recortada |
| `texto-para-grabar.txt` | El texto en cinco bloques, para leer al grabar |
| `guion-voz-en-off.md` | El guion con sus tiempos y por qué dice lo que dice |
| `timeline.json` | Las fronteras de escena — fuente única de los tiempos |
| `make_video.py` · `make_voice_real.py` · `make_gif.py` · `make_caratula.py` | Los generadores |
| `make_voice.py` | Locución sintética con Piper — alternativa descartada |

## La idea

El vídeo no es una presentación genérica: **cada escena responde a una sección
literal del anuncio**, en su mismo orden y con su mismo vocabulario.

| Escena | Tiempo | Responde a |
|---|---|---|
| Intro | 0:00 – 0:11,3 | Quién soy y a qué oferta me presento |
| Los resultados que esperáis | 0:11,3 – 0:30,4 | Su sección «Resultados esperados» |
| Vuestras 11 competencias | 0:30,4 – 0:44,2 | Las 11 competencias que piden puntuar del 1 al 5 |
| Vuestra lista de descartes | 0:44,2 – 0:55,9 | Su lista «No apliques si…» |
| Por qué soy la persona ideal | 0:55,9 – 1:11,9 | La pregunta literal del campo del vídeo |

Los tiempos no son de diseño: **salen de la grabación**. El vídeo se regenera
con la duración real de cada bloque para que las escenas cambien justo en las
pausas de la voz. Manda la voz, no el montaje.

## Regenerar el vídeo

```bash
pip install pillow qrcode faster-whisper
sudo apt-get install -y ffmpeg fonts-roboto

# 1. Monta una grabación nueva: localiza los bloques, limpia la voz,
#    regenera el vídeo a esa duración y mezcla. Llama solo a make_video.py.
python3 make_voice_real.py --audio grabacion.m4a --photo /ruta/foto.jpg

# 2. El GIF que se sube al formulario
python3 make_gif.py --video carlos-delatorre-omnidental.mp4 \
                    --out carlos-delatorre-omnidental.gif

# 3. La carátula PDF, con el vídeo dentro y a un clic
python3 make_caratula.py --url https://youtu.be/XXXX \
                         --video carlos-delatorre-omnidental-con-voz.mp4 \
                         --photo /ruta/foto.jpg
```

Los tiempos de la escaleta del PDF salen de `timeline.json`, que escribe
`make_voice_real.py`. No se escriben a mano: cuando lo estaban, se quedaron
con el reparto de 60 s después de remontar el vídeo a 71,9 s.

`make_voice_real.py` transcribe la grabación con `faster-whisper` para sacar
las marcas de tiempo, localiza los cuatro huecos entre bloques y pasa esas
fronteras a `make_video.py` con `--timings`. Cada escena reescala su reloj
interno, de modo que las animaciones ocupan todo el hueco por largo que sea.
La voz se limpia con `highpass` a 80 Hz, `afftdn` suave y `loudnorm`
(I=-16, TP=-1.5 dB).

Para cambiar el contenido visual, edita las listas del bloque `# guion` en
`make_video.py` (`RESULTS`, `SELF_RATING`, `FILTERS`, `REASONS`); la maquetación
se recoloca sola. Si cambia el texto hablado, actualiza también `WORDS` en
`make_voice_real.py` con el número de palabras de cada bloque.

### Por qué la detección de bloques usa transcripción

La primera versión buscaba las fronteras solo por energía: la pausa más larga
cerca de donde el reparto de palabras decía que debía caer el corte. Falló por
cuatro segundos en el tercer bloque — cogió una pausa interna en vez de la que
lo cierra — y eso habría dejado la diapositiva equivocada en pantalla durante
esos cuatro segundos. Con la transcripción el hueco entre bloques es
observable, no inferido.

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
   regenera la carátula con esa URL. Ahora mismo apunta al portfolio, que
   funciona, pero no es el vídeo.
2. **Escúchalo entero una vez**, con auriculares, para confirmar que los
   cambios de escena caen donde toca.
3. **Revisa que las cifras siguen vigentes** (clientes, tareas/mes, contenedores)
   antes de enviarlo: van en pantalla y te las pueden preguntar en la entrevista.
