# Vídeo de candidatura — Omni Dental · Especialista y Líder en IA y Automatizaciones

Vídeo de 1 minuto para el campo del formulario que pide
*«un vídeo de 1 minuto presentándote y contándonos por qué crees que eres la
persona ideal para este puesto»*.

| Archivo | Qué es |
|---|---|
| `carlos-delatorre-omnidental-60s.mp4` | El vídeo. 1920x1080, 30 fps, 60 s exactos, sin audio |
| `guion-voz-en-off.md` | Guion cronometrado para grabar la voz encima |
| `make_video.py` | Generador — regenera el MP4 desde cero |

## La idea

El vídeo no es una presentación genérica: **cada escena responde a una sección
literal del anuncio**, en su mismo orden y con su mismo vocabulario.

| Escena | Tiempo | Responde a |
|---|---|---|
| Intro | 0:00 – 0:08,5 | Quién soy y a qué oferta me presento |
| Los resultados que esperáis | 0:08,5 – 0:23,5 | Su sección «Resultados esperados» |
| Mi autoevaluación, sin maquillar | 0:23,5 – 0:35,5 | Las 11 competencias que piden puntuar del 1 al 5 |
| Vuestra lista de descartes | 0:35,5 – 0:46,5 | Su lista «No apliques si…» |
| Por qué soy la persona ideal | 0:46,5 – 1:00 | La pregunta literal del campo del vídeo |

La escena 3 declara un **2 en Retell AI y HighLevel**, que son las dos casillas
que faltan. Es deliberado: la oferta exige «conocimiento profundo de Retell.ai»
y uno de sus tres valores declarados es *Courageous Honesty*. Un 5 inventado se
cae en la primera llamada técnica.

## Regenerar el vídeo

```bash
pip install pillow                 # única dependencia de Python
sudo apt-get install -y ffmpeg fonts-roboto

python3 make_video.py --photo /ruta/a/tu/foto.jpg
```

Tarda unos minutos: dibuja 1.800 frames con Pillow y los codifica con
`libx264`. Para tocar el contenido, edita las listas del bloque `# guion`
(`RESULTS`, `SELF_RATING`, `FILTERS`, `REASONS`) — el resto de la maquetación
se recoloca sola.

## Antes de enviarlo

1. **Grábate la voz encima.** El MP4 va sin audio a propósito; el guion
   cronometrado está en `guion-voz-en-off.md`, junto con el comando de
   `ffmpeg` para montarla.
2. **El formulario no acepta MP4.** Los formatos admitidos en ese campo son
   PDF, DOC/DOCX, XLS/CSV, JPG/JPEG, PNG y GIF. Sube el vídeo a YouTube como
   *no listado*, a Drive o a Loom, y pega el enlace donde el formulario lo
   permita.
3. **Revisa que las cifras siguen vigentes** (clientes, tareas/mes, contenedores)
   antes de enviarlo: van en pantalla y te las pueden preguntar.
