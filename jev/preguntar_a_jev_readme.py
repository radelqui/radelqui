# -*- coding: utf-8 -*-
"""preguntar_a_jev_readme.py — manda a Jev (jev-1.13.0, modelo sellado) las veinte preguntas de jev-banco-readme.json
y una nota global, sobre el README de perfil de GitHub (../README.md).

Uso: python preguntar_a_jev_readme.py --solo-dossier   (arma y revisa el dossier y para: no llama a nadie)
     python preguntar_a_jev_readme.py --prueba         (una sola pregunta, para ver el formato y el coste)
     python preguntar_a_jev_readme.py                  (pasada real)

Qué sale de casa: solo el texto de jev-dossier-readme.md, que es el README público más un contexto. Antes de
llamar, una guarda busca claves, tokens y cabeceras de autorización: si encuentra algo, para.
La clave se lee de la variable TYPESAFE_API_KEY o de ~/.env.jev; no se imprime ni se guarda en ningún fichero.
Agregación (la de la skill jev): por pregunta, si «no_determinable» supera a «si» y a «no» es ABSTENCIÓN; si no, gana
la mayor y P = P(si). Por familia, eslabón más débil = la menor P(si) entre las no abstenidas. Nunca entre familias.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

for _f in (sys.stdout, sys.stderr):
    _f.reconfigure(encoding="utf-8")

AQUI = Path(__file__).resolve().parent
URL = os.environ.get("JEV_ENDPOINT", "https://api.typesafe.ai/v1/systemone")
MODELO = os.environ.get("JEV_MODELO", "jev-1.13.0")
BANCO = json.loads((AQUI / "jev-banco-readme.json").read_text(encoding="utf-8"))
README = AQUI.parent / "README.md"
PROHIBIDO = re.compile(r"(?i)bearer\s+\S|api[_-]?key\s*[=:]|apikey_[0-9a-f]{8}|sk-[A-Za-z0-9]{20}|ghp_[A-Za-z0-9]{20}|TYPESAFE_API_KEY")


def dossier():
    o = ["DOCUMENTO: README de perfil de GitHub.", "", BANCO["contexto"], "", "--- EMPIEZA EL DOCUMENTO ---", "",
         README.read_text(encoding="utf-8").strip(), "", "--- TERMINA EL DOCUMENTO ---"]
    return "\n".join(o)


def guarda(texto, nombre):
    m = PROHIBIDO.findall(texto)
    if m:
        print(f"PARADO: {nombre} contiene {len(m)} cosas que no pueden salir")
        sys.exit(3)


def clave():
    k = os.environ.get("TYPESAFE_API_KEY")
    f = Path.home() / ".env.jev"
    if not k and f.exists():
        for linea in f.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"\s*TYPESAFE_API_KEY\s*=\s*(.+)", linea)
            if m:
                k = m.group(1).strip().strip("\"'")
    if not k:
        print("PARADO: no hay TYPESAFE_API_KEY en el entorno ni en ~/.env.jev")
        sys.exit(4)
    return k


def preguntas_api(solo_una=False):
    ps = BANCO["preguntas"][:1] if solo_una else BANCO["preguntas"]
    q = {p["id"]: {"type": "choice", "instructions": f"Sobre el DOCUMENTO: {p['instructions']}", "criteria": p["criteria"]} for p in ps}
    if not solo_una:
        g = BANCO["nota_global"]
        q[g["id"]] = {"type": g["type"], "instructions": g["instructions"], "criteria": g["criteria"]}
    return q


def llamar(estado, preguntas, k):
    cuerpo = json.dumps({"model": MODELO, "state": estado, "questions": preguntas}, ensure_ascii=False).encode("utf-8")
    for intento in range(1, 4):
        pet = urllib.request.Request(URL, data=cuerpo, method="POST",
                                     headers={"Authorization": "Bearer " + k, "Content-Type": "application/json", "User-Agent": "radelqui-readme/1"})
        try:
            with urllib.request.urlopen(pet, timeout=180) as r:
                return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            texto = e.read().decode("utf-8", errors="replace")[:400]
            if e.code in (400, 401, 403, 422):
                print(f"PARADO: la API responde {e.code} y no se reintenta: {texto}")
                sys.exit(5)
            print(f"intento {intento}: la API responde {e.code}; espero")
        except Exception as e:  # red, tiempo agotado
            print(f"intento {intento}: {type(e).__name__}; espero")
        time.sleep(10 * intento)
    print("PARADO: tres intentos sin respuesta")
    sys.exit(6)


def leer(respuesta):
    """id → (respuesta, P(si), P(no), P(no_determinable)) para las choice; la score se devuelve aparte."""
    o, nota = {}, None
    for ident, a in respuesta["answers"].items():
        if a.get("type") == "score" or "score" in a:
            nota = a
            continue
        pr = {k: float(v) for k, v in a["probabilities"].items()}
        si, no, nd = pr.get("si", 0.0), pr.get("no", 0.0), pr.get("no_determinable", 0.0)
        o[ident] = ("ABSTENCIÓN" if nd > max(si, no) else ("sí" if si >= no else "no"), si, no, nd)
    return o, nota


def debil(lectura, tipo):
    vivos = [(lectura[p["id"]][1], p["n"]) for p in BANCO["preguntas"] if p["tipo"] == tipo and p["id"] in lectura and lectura[p["id"]][0] != "ABSTENCIÓN"]
    return min(vivos) if vivos else (None, None)


if __name__ == "__main__":
    texto = dossier()
    guarda(texto, "jev-dossier-readme.md")
    guarda(json.dumps(preguntas_api(), ensure_ascii=False), "preguntas")
    (AQUI / "jev-dossier-readme.md").write_text(texto, encoding="utf-8")
    print(f"dossier: {len(texto)} caracteres · guarda: 0 hallazgos · {len(BANCO['preguntas'])} preguntas + 1 nota global")
    if "--solo-dossier" in sys.argv:
        sys.exit(0)
    k = clave()
    prueba = "--prueba" in sys.argv
    r = llamar(texto, preguntas_api(solo_una=prueba), k)
    (AQUI / "jev-crudo-readme.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    lect, nota = leer(r)
    uso = r.get("usage", {})
    print(f"{len(lect)} respuestas · modelo {r.get('model')} · uso {uso}")
    if prueba:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        sys.exit(0)
    filas = []
    for p in BANCO["preguntas"]:
        a = lect[p["id"]]
        filas.append({"n": p["n"], "id": p["id"], "tipo": p["tipo"], "pregunta": p["instructions"],
                      "respuesta": a[0], "p_si": round(a[1], 2), "p_no": round(a[2], 2), "p_nd": round(a[3], 2)})
    familias = []
    for t, nombre in BANCO["familias"].items():
        pa, na = debil(lect, t)
        familias.append({"tipo": t, "nombre": nombre, "debil": None if pa is None else round(pa, 2), "pregunta": na})
    salida = {"modelo": MODELO, "cuando": time.strftime("%Y-%m-%dT%H:%M:%S"), "uso": uso, "nota_global": nota, "filas": filas, "familias": familias}
    (AQUI / "jev-readme.json").write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{'#':>2} {'tipo':>4} {'resp.':>10} {'P(sí)':>6} {'P(nd)':>6} pregunta")
    for f in filas:
        print(f"{f['n']:>2} {f['tipo']:>4} {f['respuesta']:>10} {f['p_si']:>6.2f} {f['p_nd']:>6.2f} {f['pregunta'][:90]}")
    print("\neslabón más débil por familia (menor P(sí) entre las no abstenidas):")
    for f in familias:
        print(f"  {f['tipo']} {f['nombre']:<42} {f['debil']} (pregunta {f['pregunta']})")
    if nota:
        print(f"\nnota global: {nota.get('score')} · confianza {nota.get('confidence')} · {nota.get('legend', '')}")
    print("\nescrito: jev-dossier-readme.md, jev-crudo-readme.json, jev-readme.json")
