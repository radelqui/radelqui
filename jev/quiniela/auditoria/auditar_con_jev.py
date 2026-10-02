# -*- coding: utf-8 -*-
"""Auditoría del método con Jev: una llamada por familia (preguntas sí/no + gravedad), más una afirmación final. Clave en TYPESAFE_API_KEY o ~/.env.jev."""
import json, os, re, sys, time, urllib.request, urllib.error
from pathlib import Path
AQUI=Path(__file__).resolve().parent
URL=os.environ.get("JEV_ENDPOINT","https://api.typesafe.ai/v1/systemone"); MODELO=os.environ.get("JEV_MODELO","jev-1.13.0")
B=json.loads((AQUI/"jev-banco-auditoria.json").read_text(encoding="utf-8")); DOSSIER=(AQUI/"dossier-metodo.md").read_text(encoding="utf-8")
def clave():
    k=os.environ.get("TYPESAFE_API_KEY"); f=Path.home()/".env.jev"
    if not k and f.exists():
        for l in f.read_text(encoding="utf-8",errors="replace").splitlines():
            m=re.match(r"\s*TYPESAFE_API_KEY\s*=\s*(.+)",l)
            if m: k=m.group(1).strip().strip("\"'")
    if not k: print("PARADO: sin clave"); sys.exit(4)
    return k
def llamar(qs,k):
    cuerpo=json.dumps({"model":MODELO,"state":DOSSIER,"questions":qs},ensure_ascii=False).encode()
    for i in range(1,4):
        try:
            with urllib.request.urlopen(urllib.request.Request(URL,data=cuerpo,method="POST",headers={"Authorization":"Bearer "+k,"Content-Type":"application/json"}),timeout=240) as r: return json.loads(r.read())
        except urllib.error.HTTPError as e:
            t=e.read().decode(errors="replace")[:400]
            if e.code in (400,401,403,422): print("PARADO",e.code,t); sys.exit(5)
            print("intento",i,e.code)
        except Exception as e: print("intento",i,type(e).__name__)
        time.sleep(10*i)
    sys.exit(6)
k=clave(); crudo={}; filas=[]; grav={}; uso={"input_tokens":0,"output_tokens":0}
for fam,nombre in B["familias"].items():
    qs={p["id"]:{"type":"choice","instructions":p["instructions"],"criteria":p["criteria"]} for p in B["preguntas"] if p["familia"]==fam}
    qs["GRAVEDAD_"+fam]={"type":"score","instructions":f"Familia «{nombre}». "+B["gravedad"]["instructions"],"criteria":B["gravedad"]["criteria"]}
    r=llamar(qs,k); crudo[fam]=r
    for kk,v in r.get("usage",{}).items(): uso[kk]=uso.get(kk,0)+v
    for p in B["preguntas"]:
        if p["familia"]!=fam: continue
        a=r["answers"][p["id"]]; pr={x:float(y) for x,y in a["probabilities"].items()}
        si,no,nd=pr.get("si",0),pr.get("no",0),pr.get("no_determinable",0)
        filas.append({"id":p["id"],"familia":fam,"pregunta":p["instructions"],"resp":"ABSTENCIÓN" if nd>max(si,no) else ("sí" if si>=no else "no"),"p_si":round(si,2),"p_no":round(no,2),"p_nd":round(nd,2)})
    g=r["answers"]["GRAVEDAD_"+fam]; grav[fam]={"score":g.get("score"),"confianza":g.get("confidence"),"legend":g.get("legend"),"probabilities":g.get("probabilities")}
    print(f"familia {fam} {nombre}: {len(qs)-1} preguntas · gravedad {g.get('score')} ({g.get('legend')})")
rf=llamar({"FINAL":{"type":"noul","instructions":B["final"]["instructions"]}},k); crudo["FINAL"]=rf
final=rf["answers"]["FINAL"].get("noul"); 
for kk,v in rf.get("usage",{}).items(): uso[kk]=uso.get(kk,0)+v
(AQUI/"jev-auditoria-crudo.json").write_text(json.dumps(crudo,ensure_ascii=False,indent=1),encoding="utf-8")
(AQUI/"jev-auditoria.json").write_text(json.dumps({"modelo":MODELO,"cuando":time.strftime("%Y-%m-%dT%H:%M:%S"),"uso":uso,"gravedad":grav,"final_noul":final,"filas":filas},ensure_ascii=False,indent=1),encoding="utf-8")
print(f"\nuso total {uso} · afirmación final 'hay una debilidad que invalida': P = {final}")
print("\nTOP debilidades (P(sí) más alta):")
for f in sorted(filas,key=lambda x:-x["p_si"])[:25]: print(f"  {f['id']} P(sí) {f['p_si']:.2f}  {f['pregunta'][:120]}")
print("\nLo que Jev descarta (P(sí) más baja):")
for f in sorted(filas,key=lambda x:x["p_si"])[:10]: print(f"  {f['id']} P(sí) {f['p_si']:.2f}  {f['pregunta'][:120]}")
print("\nabstenciones:", [f["id"] for f in filas if f["resp"]=="ABSTENCIÓN"])
