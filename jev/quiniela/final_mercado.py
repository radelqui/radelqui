# -*- coding: utf-8 -*-
"""Probabilidades definitivas: mercado (cuotas sin margen) para los 10 de Segunda; mezcla anterior para los 4 de Liga F.
Búsqueda de la mejor múltiple de 4 dobles por esperanza (premios corregidos por el control 0,69) y por aciertos."""
import json, itertools, statistics, random
S="1X2"; R=1_350_000; N=R/0.75; share={15:.075,14:.16,13:.075,12:.075,11:.075,10:.09}; CORR=0.69
c=json.load(open('columnas-afilado.json',encoding='utf-8'))['final']; mk=json.load(open('mercado.json'))
pub=json.load(open('valor2.json'))['pub']
P=[mk[str(i+1)] if i<10 else c[i]['p'] for i in range(14)]
nombres=[f['partido'] for f in c]
def conv(ps):
    d=[1.0]+[0.0]*14
    for q in ps:
        nd=[0.0]*15
        for j,v in enumerate(d):
            if v: nd[j]+=v*(1-q)
            if v and j+1<15: nd[j+1]+=v*q
        d=nd
    return d
def premios(res,nuestras):
    typ=conv([pub[i][S.index(res[i])] for i in range(14)]); gan={k:N*typ[k] for k in (10,11,12,13,14)}; pr={}; arr=0.0
    pr[14]=share[14]*R/(gan[14]+nuestras.get(14,0)) if gan[14]+nuestras.get(14,0)>=1 else 0.0
    for k in (13,12,11,10):
        tot=gan[k]+nuestras.get(k,0)
        if tot<1: arr+=share[k]*R; pr[k]=0.0
        else: pr[k]=(share[k]*R+arr)/tot; arr=0.0
    return pr
def simular(cols,n=20000,seed=5):
    random.seed(seed); tot=[]; mejor=[]
    for _ in range(n):
        res="".join(random.choices(S,weights=P[i])[0] for i in range(14))
        hits=[sum(a==b for a,b in zip(col,res)) for col in cols]; nu={}
        for h in hits:
            if h>=10: nu[h]=nu.get(h,0)+1
        pr=premios(res,nu); tot.append(CORR*sum(pr[h] for h in hits if h>=10)); mejor.append(max(hits))
    return tot,mejor,n
def fila(nombre,cols,n=20000):
    tot,mejor,nn=simular(cols,n); coste=len(cols)*0.75; xs=statistics.mean(cc.count('X') for cc in cols)
    print(f"{nombre:<46} X/col {xs:.1f}  retorno {statistics.mean(tot)/coste:4.0%}  cobra {sum(1 for g in tot if g>0)/nn:5.1%}  recupera {sum(1 for g in tot if g>=coste)/nn:5.1%}  >=100 € {sum(1 for g in tot if g>=100)/nn:5.2%}  >=1000 € {sum(1 for g in tot if g>=1000)/nn:5.2%}  P(14) {sum(1 for m in mejor if m==14)/nn:.3%}  acierto medio {statistics.mean(mejor):.2f}")
    return statistics.mean(tot)/coste
maxp="".join(S[max(range(3),key=lambda k:P[i][k])] for i in range(14))
print("probabilidades definitivas (1·X·2) y columna de máxima probabilidad:")
for i in range(14): print(f"{i+1:>2} {nombres[i]:<26} {P[i][0]:.2f}·{P[i][1]:.2f}·{P[i][2]:.2f}  → {maxp[i]}")
print("columna máxima probabilidad:",maxp,"· X esperadas en la jornada:",round(sum(p[1] for p in P),2))
def mult(base,posiciones,pares):
    out=[]
    for combo in itertools.product(*pares):
        col=list(base)
        for pos,s in zip(posiciones,combo): col[pos]=s
        out.append("".join(col))
    return out
# candidatos: 4 dobles entre los 9 partidos más abiertos (menor p máxima), pares = dos signos más probables
abiertos=sorted(range(14),key=lambda i:max(P[i]))[:9]
print("partidos más abiertos:",[i+1 for i in abiertos])
cands=[]
for pos in itertools.combinations(abiertos,4):
    pares=[]
    for p_ in pos:
        o=sorted(range(3),key=lambda k:-P[p_][k]); pares.append(S[o[0]]+S[o[1]])
    cands.append((pos,pares))
res=[]
for pos,pares in cands:
    cols=mult(maxp,pos,pares); tot,mejor,n=simular(cols,3000,seed=1); res.append((statistics.mean(tot)/12,statistics.mean(mejor),pos,pares))
print("\nmejores múltiples por retorno (3.000 sim. cada una, 126 candidatas):")
for r_,ac,pos,pares in sorted(res,reverse=True)[:5]: print(f"  dobles en {[p+1 for p in pos]} {pares}: retorno {r_:.0%} · acierto medio mejor columna {ac:.2f}")
print("mejores por aciertos de la mejor columna:")
for r_,ac,pos,pares in sorted(res,key=lambda x:-x[1])[:3]: print(f"  dobles en {[p+1 for p in pos]} {pares}: retorno {r_:.0%} · acierto medio {ac:.2f}")
print("\n"+" "*47+"X/col   retorno   cobra   recupera  >=100   >=1000   P(14)   acierto")
anterior=mult("21211111111211",(2,4,8,13),("X2","X1","X1","1X"))
fila("múltiple anterior (X en 3,5,9,14) con P de mercado",anterior)
best=sorted(res,reverse=True)[0]; nueva=mult(maxp,best[2],best[3])
fila(f"múltiple nueva: dobles {[p+1 for p in best[2]]} {best[3]}",nueva)
bestac=sorted(res,key=lambda x:-x[1])[0]; nueva2=mult(maxp,bestac[2],bestac[3])
fila(f"múltiple máx. aciertos: dobles {[p+1 for p in bestac[2]]} {bestac[3]}",nueva2)
fila("sencilla A x16",["21X1X111X11211"]*16); fila("sencilla máx. prob. x16",[maxp]*16)
json.dump({"P":P,"maxp":maxp,"nueva":{"dobles":[p+1 for p in best[2]],"pares":best[3],"columnas":nueva},"maxac":{"dobles":[p+1 for p in bestac[2]],"pares":bestac[3]}},open('final-mercado.json','w'),indent=1)
