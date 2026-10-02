# -*- coding: utf-8 -*-
"""Calibra la nitidez del modelo (p^a normalizado) sobre 2024-26 y recalcula valor y EV con probabilidades afiladas."""
import csv, glob, math, json, collections, itertools, statistics, random
from datetime import datetime
exec(open('modelo.py').read().split("jornada = [")[0].replace('print(','(lambda *a,**k:None)('))  # reusa Elo+logit sin imprimir
def sharpen(p,a):
    q=[x**a for x in p]; s=sum(q); return [x/s for x in q]
best=None
for a in [1.0,1.1,1.2,1.3,1.4,1.5,1.6,1.8,2.0]:
    ll=-sum(math.log(max(sharpen(probs(d,*params),a)[res],1e-9)) for d,res,*_ in test)/len(test)
    print(f"a={a:.1f} log-loss {ll:.4f}"); 
    if best is None or ll<best[0]: best=(ll,a)
print(f"mejor nitidez a={best[1]} (casas 0.9936)")
A_=best[1]
# recomputa la mezcla final con el modelo afilado
S="1X2"
col=json.load(open('columnas.json',encoding='utf-8'))
nuevo=[]
for f in col['final']:
    mo=sharpen(f['modelo'],A_); c_=f['comunidad']; e=f['expertos']
    base=[0.5*mo[k]+0.3*c_[k]+0.2*e[k] for k in range(3)]; s=sum(base); f2=dict(f); f2['modelo_afilado']=[round(x,3) for x in mo]; f2['p']=[round(x/s,3) for x in base]; nuevo.append(f2)
json.dump({"final":nuevo,"a":A_}, open('columnas-afilado.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
P=[f['p'] for f in nuevo]
pub=json.load(open('valor2.json'))['pub']
print(f"\nX esperadas (afilado) {sum(p[1] for p in P):.2f} · público {sum(q[1] for q in pub):.2f}")
print("valor por signo (afilado):")
for i,f in enumerate(nuevo):
    r=[P[i][k]/pub[i][k] for k in range(3)]
    print(f"{i+1:>2} {f['partido']:<26} p {P[i][0]:.2f}·{P[i][1]:.2f}·{P[i][2]:.2f}  valor {r[0]:.2f}·{r[1]:.2f}·{r[2]:.2f}")
src=open('valor2.py').read()
src=src.split("print(\"valor por signo")[0]  # funciones
exec(src.replace("P=[f['p'] for f in c]","P=P"))
R=1_350_000; N=R/0.75
def fila(nombre, cols):
    tot,mejor,n=simular(cols); coste=len(cols)*0.75
    xs=statistics.mean(cc.count('X') for cc in cols)
    print(f"{nombre:<40} {coste:5.2f} €  X/col {xs:.1f}  EV {statistics.mean(tot):6.2f} € ({statistics.mean(tot)/coste:4.0%})  cobra {sum(1 for g in tot if g>0)/n:5.1%}  recupera {sum(1 for g in tot if g>=coste)/n:5.1%}  >=100 € {sum(1 for g in tot if g>=100)/n:5.2%}  >=1000 € {sum(1 for g in tot if g>=1000)/n:5.2%}  14 {sum(1 for m in mejor if m==14)/n:.3%}")
A="21X1X111X11211"; B="21211111111221"
actual=mult((2,4,8,12),("X2","1X","1X","12")); robusta=mult((2,4,8,13),("X2","1X","X1","1X"))
print("\n" + " "*41 + "coste   X/col   EV (retorno)   P(cobrar) P(recuperar) P(>=100) P(>=1000) P(14)")
fila("sencilla A x16", [A]*16); fila("sencilla B x16", [B]*16); fila("Jev x16", ["21211111111211"]*16)
fila("múltiple actual (3,5,9,13)", actual); fila("múltiple X infravaloradas (3,5,9,14)", robusta)
# referencia: si el público tuviera razón (P = público), el retorno debe rondar el 55 %
P_save=P; P=[list(q) for q in pub]; fila("control: múltiple actual si P=público", actual); P=P_save
