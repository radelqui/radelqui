# -*- coding: utf-8 -*-
"""Respuesta a la auditoría de Jev: (1) sensibilidad a los pesos de la mezcla, (2) K y ventaja de campo óptimos, (3) prueba retrospectiva."""
import json, csv, glob, math, collections, itertools, statistics
from datetime import datetime, timedelta
S="1X2"
# ---------- (1) sensibilidad a los pesos
c=json.load(open('columnas-afilado.json',encoding='utf-8'))['final']
def mezcla(wm,wc,we):
    out=[]
    for f in c:
        b=[wm*f['modelo_afilado'][k]+wc*f['comunidad'][k]+we*f['expertos'][k] for k in range(3)]; s=sum(b); out.append([x/s for x in b])
    return out
pub=json.load(open('valor2.json'))['pub']
print("(1) SENSIBILIDAD A LOS PESOS modelo/comunidad/pronosticadores → signos con valor >1,2 y top-2 por partido en los 7 abiertos")
abiertos=[2,4,8,9,12,13,1]
for w in [(0.5,0.3,0.2),(0.7,0.2,0.1),(0.9,0.1,0.0),(1.0,0.0,0.0),(0.4,0.4,0.2),(0.3,0.3,0.4)]:
    P=mezcla(*w)
    val=[(i+1,S[k],round(P[i][k]/pub[i][k],2)) for i in range(14) for k in range(3) if P[i][k]/pub[i][k]>=1.2 and P[i][k]>=0.25]
    top2="".join(f" {i+1}:"+"".join(S[k] for k in sorted(range(3),key=lambda k:-P[i][k])[:2]) for i in abiertos)
    print(f"  pesos {w}: X esperadas {sum(p[1] for p in P):.2f} · valor>=1,2 (p>=25%): {[(a,b,v) for a,b,v in val]} · dobles:{top2}")
# ---------- (2) K y HFA óptimos
rows=[]
for f in sorted(glob.glob('fd/*.csv')):
    for r in csv.DictReader(open(f,encoding='utf-8-sig')):
        if r.get('FTR') in 'HDA': rows.append((datetime.strptime(r['Date'],'%d/%m/%Y'),r['HomeTeam'],r['AwayTeam'],int(r['FTHG']),int(r['FTAG']),r['FTR'],r['Div']))
rows.sort()
def correr(K,HFA,decay=0.0):
    elo=collections.defaultdict(lambda:1500.0); hist=[]; last=collections.defaultdict(lambda:None)
    for d,h,a,hg,ag,ftr,div in rows:
        for t in (h,a):
            if decay and last[t] is not None:
                dias=(d-last[t]).days
                if dias>60: elo[t]=1500+(elo[t]-1500)*math.exp(-decay*dias/365)
            last[t]=d
        diff=elo[h]+HFA-elo[a]; res={'H':0,'D':1,'A':2}[ftr]; hist.append((diff,res,d))
        exp=1/(1+10**(-diff/400)); sc={0:1,1:0.5,2:0}[res]; m=math.log(abs(hg-ag)+1)+1 if hg!=ag else 1
        delta=K*m*(sc-exp); elo[h]+=delta; elo[a]-=delta
    return hist, elo
def ajustar(hist):
    train=[x for x in hist if x[2]<datetime(2024,8,1)]; test=[x for x in hist if x[2]>=datetime(2024,8,1)]
    def probs(d,b,c1,c2):
        z=b*d; p2=1/(1+math.exp(z-c1)); px2=1/(1+math.exp(z-c2)); return (1-px2,px2-p2,p2)
    def nll(b,c1,c2,data): return -sum(math.log(max(probs(d,b,c1,c2)[r],1e-9)) for d,r,_ in data)/len(data)
    # búsqueda en rejilla gruesa + fina
    best=None
    for b in [0.003,0.004,0.005,0.006]:
        for c1 in [-1.1,-0.9,-0.7]:
            for c2 in [0.3,0.5,0.7]:
                v=nll(b,c1,c2,train)
                if best is None or v<best[0]: best=(v,b,c1,c2)
    _,b,c1,c2=best
    for _ in range(2):
        for db in [-0.0005,0,0.0005]:
            for dc1 in [-0.1,0,0.1]:
                for dc2 in [-0.1,0,0.1]:
                    v=nll(b+db,c1+dc1,c2+dc2,train)
                    if v<best[0]: best=(v,b+db,c1+dc1,c2+dc2)
        _,b,c1,c2=best
    return (b,c1,c2), nll(b,c1,c2,test), probs
print("\n(2) K, VENTAJA DE CAMPO Y DECAIMIENTO: log-loss en 2024-26 (casas 0,9936; actual K20/HFA60: 1,0166)")
res2=[]
for K,HFA,dec in [(20,60,0),(20,40,0),(20,80,0),(30,60,0),(15,60,0),(40,60,0),(20,60,0.3),(30,60,0.3),(30,80,0.3)]:
    hist,elo=correr(K,HFA,dec); params,ll,probs=ajustar(hist); res2.append((ll,K,HFA,dec,params,elo,probs))
    print(f"  K={K} HFA={HFA} decay={dec}: log-loss {ll:.4f}")
res2.sort(key=lambda x:x[0]); ll,K,HFA,dec,params,elo,probs=res2[0]
print(f"  mejor: K={K} HFA={HFA} decay={dec} → {ll:.4f}")
jor=[("Albacete","Eibar"),("Almeria","Burgos"),("Cadiz","Leganes"),("Sabadell","Andorra"),("Sociedad B","Granada"),("Sp Gijon","Celta B"),("Castellon","Ceuta"),("Las Palmas","Valladolid"),("Girona","Mallorca"),("Cordoba","Tenerife")]
print("  probabilidades del mejor modelo frente al actual (1·X·2):")
for i,(h,a) in enumerate(jor):
    p=probs(elo[h]+HFA-elo[a],*params); q=c[i]['modelo']
    print(f"   {i+1:>2} {h:>11}-{a:<11} nuevo {p[0]:.2f}·{p[1]:.2f}·{p[2]:.2f}  actual {q[0]:.2f}·{q[1]:.2f}·{q[2]:.2f}")
# ---------- (3) prueba retrospectiva: en cada semana de Segunda 2024-26, columna 'máxima probabilidad' vs 'X donde P(X)>=0,33'
print("\n(3) PRUEBA RETROSPECTIVA 2024-26 (semanas de Segunda con 9-12 partidos, con el modelo entrenado solo hasta 2024)")
hist,elo0=correr(20,60,0); params0,_,probs0=ajustar(hist)
# re-simular Elo cronológicamente para tener el Elo vigente antes de cada partido
elo=collections.defaultdict(lambda:1500.0); semanas=collections.defaultdict(list)
for d,h,a,hg,ag,ftr,div in rows:
    diff=elo[h]+60-elo[a]
    if d>=datetime(2024,8,1) and div=='SP2':
        p=probs0(diff,*params0); semanas[(d-timedelta(days=(d.weekday()-3)%7)).date()].append((p,{'H':'1','D':'X','A':'2'}[ftr]))
    exp=1/(1+10**(-diff/400)); sc={'H':1,'D':0.5,'A':0}[ftr]; m=math.log(abs(hg-ag)+1)+1 if hg!=ag else 1
    delta=20*m*(sc-exp); elo[h]+=delta; elo[a]-=delta
semanas={k:v for k,v in semanas.items() if 9<=len(v)<=12}
def aciertos(sem, estrategia):
    n=0
    for p,real in sem:
        if estrategia=='maxp': s=S[max(range(3),key=lambda k:p[k])]
        elif estrategia=='x33': s='X' if p[1]>=0.33 else S[max(range(3),key=lambda k:p[k])]
        elif estrategia=='x30': s='X' if p[1]>=0.30 else S[max(range(3),key=lambda k:p[k])]
        elif estrategia=='todo1': s='1'
        n+= (s==real)
    return n/len(sem)*14
for est,nombre in (('todo1','todo 1'),('maxp','máxima probabilidad (como B)'),('x30','X si P(X)>=30 % (muchas X)'),('x33','X si P(X)>=33 % (como A)')):
    ac=[aciertos(v,est) for v in semanas.values()]
    xs=statistics.mean(sum(1 for p,_ in v if (est=='x33' and p[1]>=0.33) or (est=='x30' and p[1]>=0.30))/len(v)*14 for v in semanas.values()) if est.startswith('x') else 0
    print(f"  {nombre:<32} {len(ac)} semanas · aciertos medios {statistics.mean(ac):.2f}/14 · >=10: {sum(1 for x in ac if x>=10)/len(ac):.0%} · >=11: {sum(1 for x in ac if x>=11)/len(ac):.0%} · >=12: {sum(1 for x in ac if x>=12)/len(ac):.0%} · X jugadas/col {xs:.1f}")
# ¿cuántas X salieron realmente en esas semanas?
print(f"  X reales por semana (escala 14): {statistics.mean(sum(1 for _,r in v if r=='X')/len(v)*14 for v in semanas.values()):.2f}")
