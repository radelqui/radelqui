# -*- coding: utf-8 -*-
"""preguntar_a_jev_quiniela.py — pide a Jev (jev-1.13.0) el signo más probable de los 14 partidos de la jornada 11
y lo cruza con las columnas A y B. La clave se lee de TYPESAFE_API_KEY o ~/.env.jev; no se imprime ni se guarda.

Uso: python preguntar_a_jev_quiniela.py --solo-dossier   (arma el dossier y para)
     python preguntar_a_jev_quiniela.py --prueba         (un solo partido)
     python preguntar_a_jev_quiniela.py                  (los 14)
"""
import json, os, re, sys, time, urllib.error, urllib.request
from pathlib import Path
for _f in (sys.stdout, sys.stderr): _f.reconfigure(encoding="utf-8")
AQUI = Path(__file__).resolve().parent
URL = os.environ.get("JEV_ENDPOINT", "https://api.typesafe.ai/v1/systemone")
MODELO = os.environ.get("JEV_MODELO", "jev-1.13.0")
B = json.loads((AQUI / "jev-banco-quiniela.json").read_text(encoding="utf-8"))
PROHIBIDO = re.compile(r"(?i)bearer\s+\S|api[_-]?key\s*[=:]|apikey_[0-9a-f]{8}|TYPESAFE_API_KEY")

def dossier(): return "\n\n".join([B["contexto"], ""] + B["secciones"])
def clave():
    k = os.environ.get("TYPESAFE_API_KEY"); f = Path.home() / ".env.jev"
    if not k and f.exists():
        for l in f.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(r"\s*TYPESAFE_API_KEY\s*=\s*(.+)", l)
            if m: k = m.group(1).strip().strip("\"'")
    if not k: print("PARADO: no hay TYPESAFE_API_KEY en el entorno ni en ~/.env.jev"); sys.exit(4)
    return k
def preguntas(prueba=False):
    ps = B["preguntas"][:1] if prueba else B["preguntas"]
    return {p["id"]: {"type": "choice", "instructions": p["instructions"], "criteria": p["criteria"]} for p in ps}
def llamar(estado, qs, k):
    cuerpo = json.dumps({"model": MODELO, "state": estado, "questions": qs}, ensure_ascii=False).encode("utf-8")
    for intento in range(1, 4):
        pet = urllib.request.Request(URL, data=cuerpo, method="POST", headers={"Authorization": "Bearer " + k, "Content-Type": "application/json", "User-Agent": "quiniela-jev/1"})
        try:
            with urllib.request.urlopen(pet, timeout=180) as r: return json.loads(r.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            t = e.read().decode("utf-8", errors="replace")[:400]
            if e.code in (400, 401, 403, 422): print(f"PARADO: la API responde {e.code}: {t}"); sys.exit(5)
            print(f"intento {intento}: {e.code}; espero")
        except Exception as e: print(f"intento {intento}: {type(e).__name__}; espero")
        time.sleep(10 * intento)
    print("PARADO: tres intentos sin respuesta"); sys.exit(6)

if __name__ == "__main__":
    texto = dossier()
    if PROHIBIDO.search(texto): print("PARADO: el dossier contiene algo que no puede salir"); sys.exit(3)
    (AQUI / "jev-dossier-quiniela.md").write_text(texto, encoding="utf-8")
    print(f"dossier: {len(texto)} caracteres · {len(B['preguntas'])} preguntas")
    if "--solo-dossier" in sys.argv: sys.exit(0)
    prueba = "--prueba" in sys.argv
    r = llamar(texto, preguntas(prueba), clave())
    (AQUI / "jev-crudo-quiniela.json").write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"modelo {r.get('model')} · uso {r.get('usage')}")
    if prueba: print(json.dumps(r, ensure_ascii=False, indent=2)); sys.exit(0)
    A, Bc = B["columnaA"], B["columnaB"]; filas = []; colJ = ""
    print(f"\n{'#':>2} {'partido':<28} {'P(1)':>5} {'P(X)':>5} {'P(2)':>5} Jev A B")
    for i, p in enumerate(B["preguntas"]):
        a = r["answers"][p["id"]]; pr = {k: float(v) for k, v in a["probabilities"].items()}
        s = max("1X2", key=lambda k: pr.get(k, 0)); colJ += s
        filas.append({"n": p["n"], "jev": s, "p": pr, "confianza": a.get("confidence"), "A": A[i], "B": Bc[i]})
        print(f"{p['n']:>2} {p['instructions'].split('(')[1].split(')')[0]:<28} {pr.get('1',0):>5.2f} {pr.get('X',0):>5.2f} {pr.get('2',0):>5.2f}  {s}  {A[i]} {Bc[i]}{'  <- discrepa' if s not in (A[i], Bc[i]) else ''}")
    print(f"\ncolumna Jev {colJ} · coincide con A en {sum(1 for f in filas if f['jev']==f['A'])}/14 · con B en {sum(1 for f in filas if f['jev']==f['B'])}/14")
    (AQUI / "jev-quiniela.json").write_text(json.dumps({"modelo": MODELO, "cuando": time.strftime("%Y-%m-%dT%H:%M:%S"), "uso": r.get("usage"), "columna_jev": colJ, "filas": filas}, ensure_ascii=False, indent=2), encoding="utf-8")
