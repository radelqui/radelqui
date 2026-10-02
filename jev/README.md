# Opinión de Jev sobre el README de perfil

Jev (TypeSafe AI, modelo sellado `jev-1.13.0`) es un evaluador probabilístico barato de otra familia de modelo. Aquí se le pasa el `README.md` del perfil con veinte preguntas sí/no y una nota global de 1 a 5.

## Ficheros

| Fichero | Qué es |
|---|---|
| `jev-banco-readme.json` | Las 20 preguntas (5 familias) y la nota global. Editable. |
| `preguntar_a_jev_readme.py` | Arma el dossier, pasa la guarda, llama a la API y agrega. |
| `jev-dossier-readme.md` | Lo único que sale de casa: contexto + README. Se genera. |
| `jev-crudo-readme.json` | Respuesta cruda de la API. Se genera. |
| `jev-readme.json` | Tabla agregada y eslabón más débil por familia. Se genera. |

## Cómo correrlo

```bash
cd jev
python preguntar_a_jev_readme.py --solo-dossier   # sin red: arma y revisa el dossier
python preguntar_a_jev_readme.py --prueba         # una pregunta, para ver formato y coste
python preguntar_a_jev_readme.py                  # pasada real
```

La clave se lee de `TYPESAFE_API_KEY` o de `~/.env.jev`. No se imprime ni se guarda. Variables opcionales: `JEV_ENDPOINT`, `JEV_MODELO`.

## Lectura

Por pregunta: si P(no_determinable) supera a P(sí) y a P(no), es ABSTENCIÓN; si no, gana la mayor. Por familia, el eslabón más débil es la menor P(sí) entre las no abstenidas. Las preguntas A4, C4, D1, E1, E2, E3, E4 y E5 están formuladas en negativo: ahí un «sí» con P alta es un aviso, no un elogio.
