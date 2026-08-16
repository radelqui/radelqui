# Guion de voz en off — vídeo 1 minuto · Omni Dental

Vídeo: `carlos-delatorre-omnidental-60s.mp4` (60 s exactos, 1920x1080, 30 fps).

El vídeo va **sin audio a propósito**: la voz la pones tú. Un recruiter distingue
una voz sintética al instante y el campo del formulario pide literalmente
*«un vídeo de 1 minuto presentándote»* — tiene que sonar a ti.

Ritmo objetivo: **~2,6 palabras/segundo**. Total: 152 palabras.
Si te sale largo, lo que se recorta primero está marcado con `[opcional]`.

---

## Escena 1 — Intro · 0:00 → 0:08,5

> Hola, soy Carlos De La Torre, arquitecto de IA.
> He leído vuestra oferta entera y voy a responderla punto por punto.

*22 palabras · deja medio segundo de silencio antes de empezar.*

---

## Escena 2 — Los resultados que esperáis · 0:08,5 → 0:23,5

> Empiezo por los resultados que esperáis.
> Voz en tiempo real, ya en producción.
> Fuera las hojas de cálculo: un proceso de cuarenta y cinco minutos bajado a tres.
> Claude Code a diario, partner de Anthropic.
> Y treinta y cuatro mil tareas automatizadas al mes.

*41 palabras · marca una pausa corta entre cada resultado, van apareciendo en pantalla.*

---

## Escena 3 — Autoevaluación · 0:23,5 → 0:35,5

> Mi autoevaluación, sin maquillar: cinco en Claude Code, APIs de IA y chatbots.
> Retell y HighLevel, un dos.
> Prefiero decíroslo yo ahora que lo descubráis vosotros la primera semana.

*30 palabras · esta es la frase que más va a pesar. Dila despacio y mirando a cámara.*

---

## Escena 4 — Vuestra lista de descartes · 0:35,5 → 0:46,5

> Vuestra lista de descartes también la leí. Ninguno me aplica:
> nueve agentes que diseñé sin que me los pidieran,
> treinta y un años en terminal y dos servidores levantados desde cero.

*31 palabras.*

---

## Escena 5 — Por qué soy la persona ideal · 0:46,5 → 1:00

> ¿Por qué soy la persona ideal?
> Porque ya he construido lo que pedís, y está funcionando.
> Y porque trabajo con una regla: sin prueba, no está hecho.
> Hablemos.

*28 palabras · deja que «Hablemos» caiga sobre el cierre, y no hables sobre los datos de contacto.*

---

## Cómo grabar la voz

1. Abre el MP4 en pantalla y ponlo a reproducir mientras lees — te marca el ritmo.
2. Graba solo el audio (el móvil vale; mejor con auriculares con micro).
3. Manda el audio y lo monto sobre el vídeo con `ffmpeg`:

```bash
ffmpeg -i carlos-delatorre-omnidental-60s.mp4 -i voz.m4a \
       -c:v copy -c:a aac -b:a 192k -shortest \
       carlos-delatorre-omnidental-60s-con-voz.mp4
```

## Alternativa: grabarte a ti mismo

Si prefieres salir tú en cámara (suele puntuar más en un proceso de selección),
usa este mismo guion como teleprompter y el MP4 como material de apoyo para
intercalar. La escena 3 —la autoevaluación honesta— funciona mejor dicha a
cámara que leída.

---

## Por qué el guion dice lo que dice

Cada escena responde a una sección literal del anuncio:

| Escena | Sección de la oferta a la que responde |
|---|---|
| 2 | «Resultados esperados» (los 8 puntos que enumeran) |
| 3 | Las 11 competencias que piden autoevaluar del 1 al 5 |
| 4 | La lista «No apliques si…» |
| 5 | El campo del vídeo: «por qué crees que eres la persona ideal» |

La escena 3 declara un **2 honesto** en Retell AI y HighLevel. Es deliberado:
la oferta pide «conocimiento profundo de Retell.ai» y uno de sus tres valores
declarados es *Courageous Honesty*. Inflarlo a un 5 se cae en la primera
llamada técnica; declararlo a 2 y aun así presentarse es coherente con lo que
ellos mismos dicen valorar.
