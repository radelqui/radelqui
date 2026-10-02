# -*- coding: utf-8 -*-
"""Dónde está el valor: probabilidad real frente a lo que apuesta el público, y columna que maximiza el premio esperado."""
import json, csv, glob, collections, itertools, math, statistics, random
from datetime import datetime, timedelta
S="1X2"; R=1_350_000; N=R/0.75
share={15:.075,14:.16,13:.075,12:.075,11:.075,10:.09}
c=json.load(open('columnas.json',encoding='utf-8'))['final']
P=[f['p'] for f in c]; nombres=[f['partido'] for f in c]
comm=[[x/100 for x in r] for r in [(18,20,63),(72,17,11),(21,31,48),(65,20,15),(23,42,35),(73,14,13),(81,9,9),(68,20,12),(43,35,22),(38,37,25),(81,10,10),(10,14,76),(51,29,20),(67,17,16)]]

# 1) Histórico: cuántas X salen en 14 partidos de Segunda, y cuántos favoritos caen
rows=[]
for f in sorted(glob.glob('fd/*SP2.csv')):
    for r in csv.DictReader(open(f,encoding='utf-8-sig')):
        if r.get('FTR') in 'HDA' and r.get('AvgH'):
            rows.append((datetime.strptime(r['Date'],'%d/%m/%Y'), r['FTR'], float(r['AvgH']),float(r['AvgD']),float(r['AvgA'])))
rows.sort()
# jornadas reales: agrupar por semana (jueves a miércoles)
jor=collections.defaultdict(list)
for d,ftr,oh,od,oa in rows: jor[(d - timedelta(days=(d.weekday()-3)%7)).date()].append((ftr,oh,od,oa))
jor={k:v for k,v in jor.items() if 9<=len(v)<=12}
nx=[sum(1 for m in v if m[0]=='D')*14/len(v) for v in jor.values()]           # X escaladas a 14 partidos
fav=[sum(1 for m in v if (m[0]=='H' and m[1]<min(m[2],m[3])) or (m[0]=='A' and m[3]<min(m[1],m[2])))/len(v) for v in jor.values()]
print(f"{len(jor)} jornadas de Segunda 2018-26 (11 partidos cada una, escaladas a 14):")
print(f"  empates por jornada: media {statistics.mean(nx):.1f} · mediana {statistics.median(nx):.1f} · P(0 X) {sum(1 for x in nx if x<0.5)/len(nx):.1%} · P(<=1 X) {sum(1 for x in nx if x<1.5)/len(nx):.1%} · P(>=3 X) {sum(1 for x in nx if x>=2.5)/len(nx):.1%}")
print(f"  el favorito de las casas gana el {statistics.mean(fav):.0%} de los partidos; una columna 'todo favoritos' acierta de media {14*statistics.mean(fav):.1f}/14")
# cuántas veces una columna todo-favoritos hubiera hecho >=12 de 14 (escalado: >=9.4 de 11)
tf=[sum(1 for m in v if (m[0]=='H' and m[1]<min(m[2],m[3])) or (m[0]=='A' and m[3]<min(m[1],m[2])) or (m[0]=='D' and m[2]<min(m[1],m[3])))/len(v) for v in jor.values()]
print(f"  jornadas en que 'todo favoritos' habría pasado del 85 % de aciertos (12+ de 14): {sum(1 for x in tf if x>=12/14)/len(tf):.1%}")

# 2) Valor por signo: p real / popularidad
print("\nvalor por signo (p / popularidad; >1,15 = el público lo infravalora):")
for i,n in enumerate(nombres):
    r=[P[i][k]/comm[i][k] for k in range(3)]
    best=max(range(3),key=lambda k:r[k])
    print(f"{i+1:>2} {n:<26} p 1·X·2 {P[i][0]:.2f}·{P[i][1]:.2f}·{P[i][2]:.2f}  público {comm[i][0]:.2f}·{comm[i][1]:.2f}·{comm[i][2]:.2f}  valor {r[0]:.2f}·{r[1]:.2f}·{r[2]:.2f}  → {S[best]}")
print(f"\nX esperadas en el resultado real: {sum(p[1] for p in P):.2f} · X que juega el público de media por columna: {sum(cm[1] for cm in comm):.2f}")

# 3) EV de una columna: suma_k P(k) * premio_k, premio_k = fondo_k/(acertantes_típicos_k + 1)
def conv(ps):
    d=[1.0]+[0.0]*14
    for q in ps:
        nd=[0.0]*15
        for j,v in enumerate(d):
            if v: nd[j]+=v*(1-q)
            if v and j+1<15: nd[j+1]+=v*q
        d=nd
    return d
def ev(col, detalle=False):
    mine=conv([P[i][S.index(col[i])] for i in range(14)])
    # acertantes típicos condicionados a que salga nuestra columna en k: aproximación con popularidad de nuestros signos
    typ=conv([comm[i][S.index(col[i])] for i in range(14)])
    total=0; out={}
    for k in (14,13,12,11,10):
        win=N*typ[k]; premio=share[k]*R/(win+1); total+=mine[k]*premio; out[k]=(mine[k],win,premio)
    # categoría 15: 14 + pleno; suponemos pleno 2-0 con P 0,30 y popularidad 0,45
    premio15=share[15]*R/(N*typ[14]*0.45+1); total+=mine[14]*0.30*premio15; out[15]=(mine[14]*0.30,N*typ[14]*0.45,premio15)
    return (total,out,mine) if detalle else total
A="21X1X111X11211"; B="21211111111221"
# búsqueda: enumeración sobre los 7 partidos abiertos, fijando los 7 claros en su mejor signo por valor o probabilidad
claros={1:"2",3:"1",5:"1",6:"1",7:"1",10:"1",11:"2"}  # índices 0-based
abiertos=[i for i in range(14) if i not in claros]
mejor=[]
for combo in itertools.product(S, repeat=len(abiertos)):
    col=[None]*14
    for i,s in claros.items(): col[i]=s
    for i,s in zip(abiertos,combo): col[i]=s
    col="".join(col); mejor.append((ev(col),col))
mejor.sort(reverse=True)
print("\nEV por columna (0,75 €):")
for nombre,col in (("A",A),("B",B)):
    t,out,mine=ev(col,True); print(f"  {nombre} {col}: EV {t:.2f} € · P(14) {mine[14]:.4%} · si hace 14 cobra ~{out[14][2]:,.0f} € con ~{out[14][1]:.1f} acertantes más")
print("  top 8 columnas por EV (7 partidos claros fijos, 7 abiertos libres):")
for t,col in mejor[:8]:
    _,out,mine=ev(col,True); print(f"    {col}: EV {t:.2f} € · P(14) {mine[14]:.4%} · premio 14 ~{out[14][2]:,.0f} € · X en la columna {col.count('X')}")
json.dump({"top":mejor[:60]}, open('valor-top.json','w'))
