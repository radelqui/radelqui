# Guion de voz en off — vídeo 1 minuto · Omni Dental

Vídeo: `carlos-delatorre-omnidental-60s.mp4` (60 s exactos, 1920x1080, 30 fps).

Este es el texto que ya va locutado en
`carlos-delatorre-omnidental-60s-con-voz.mp4` (voz Piper `es_ES-davefx-medium`).

Si prefieres grabarte tú, usa `carlos-delatorre-omnidental-60s.mp4` —el mismo
vídeo sin audio— y lee este guion siguiendo los tiempos. Ritmo: ~2,6
palabras/segundo.

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

## Escena 3 — Vuestras 11 competencias · 0:23,5 → 0:35,5

> Vuestras once competencias, del uno al cinco: cinco en todas.
> Claude Code, APIs de IA, chatbots, PostgreSQL, Firebase.
> No es una promesa: es lo que hago cada día.

*26 palabras · el «cinco en todas» tiene que sonar tranquilo, no defensivo.*

---

## Escena 4 — Vuestra lista de descartes · 0:35,5 → 0:46,5

> Vuestra lista de descartes también la leí. Ninguno me aplica:
> nueve agentes que diseñé sin que me los pidieran,
> treinta y un años en terminal y dos servidores levantados desde cero.

*31 palabras.*

---

## Escena 5 — Por qué soy la persona ideal · 0:46,5 → 1:00

> ¿Por qué soy la persona ideal?
> Porque ya he construido lo que pedís, y está funcionando en producción, no en una demo.
> Y porque trabajo con una regla que aprendí en banca regulada: sin prueba, no está hecho.
> Hablemos.

*38 palabras · deja que «Hablemos» caiga sobre el cierre, y no hables sobre los datos de contacto.*

---

## Si quieres poner tu propia voz

1. Abre `carlos-delatorre-omnidental-60s.mp4` (el que va sin audio) y ponlo a
   reproducir mientras lees — te marca el ritmo escena a escena.
2. Graba solo el audio (el móvil vale; mejor con auriculares con micro).
3. Móntalo con:

```bash
ffmpeg -i carlos-delatorre-omnidental-60s.mp4 -i voz.m4a \
       -af "loudnorm=I=-16:TP=-1.5:LRA=11" \
       -c:v copy -c:a aac -b:a 192k -shortest \
       carlos-delatorre-omnidental-60s-con-voz.mp4
```

---

## Por qué el guion dice lo que dice

Cada escena responde a una sección literal del anuncio:

| Escena | Sección de la oferta a la que responde |
|---|---|
| 2 | «Resultados esperados» (los 8 puntos que enumeran) |
| 3 | Las 11 competencias que piden autoevaluar del 1 al 5 |
| 4 | La lista «No apliques si…» |
| 5 | El campo del vídeo: «por qué crees que eres la persona ideal» |
