# -*- coding: utf-8 -*-
"""Valor con la popularidad real de eduardolosilla (% en quinielista, jornada 11) y fórmula de premio consistente:
premio_k = fondo_k / (acertantes típicos_k + nosotros), con arrastre de categorías vacías hacia abajo."""
import json, itertools, statistics, random
S="1X2"; R=1_350_000; N=R/0.75
share={15:.075,14:.16,13:.075,12:.075,11:.075,10:.09}
c=json.load(open('columnas.json',encoding='utf-8'))['final']; P=[f['p'] for f in c]; nombres=[f['partido'] for f in c]
pub=[[x/100 for x in r] for r in [(20,21,59),(65,24,11),(28,33,39),(59,21,20),(35,29,36),(73,17,10),(90,6,4),(58,27,15),(51,26,23),(47,27,26),(86,9,5),(8,18,74),(43,29,28),(47,25,28)]]
def conv(ps):
    d=[1.0]+[0.0]*14
    for q in ps:
        nd=[0.0]*15
        for j,v in enumerate(d):
            if v: nd[j]+=v*(1-q)
            if v and j+1<15: nd[j+1]+=v*q
        d=nd
    return d
def premios(res, nuestras):
    typ=conv([pub[i][S.index(res[i])] for i in range(14)])
    gan={k:N*typ[k] for k in (10,11,12,13,14)}
    pr={}; arr=0.0
    pr[14]=share[14]*R/(gan[14]+nuestras.get(14,0)) if gan[14]+nuestras.get(14,0)>=1 else 0.0
    for k in (13,12,11,10):
        tot=gan[k]+nuestras.get(k,0)
        if tot<1: arr+=share[k]*R; pr[k]=0.0
        else: pr[k]=(share[k]*R+arr)/tot; arr=0.0
    return pr
def simular(cols, n=20000, seed=5):
    random.seed(seed); tot=[]; mejor=[]
    for _ in range(n):
        res="".join(random.choices(S,weights=P[i])[0] for i in range(14))
        hits=[sum(a==b for a,b in zip(col,res)) for col in cols]
        nuestras={}
        for h in hits:
            if h>=10: nuestras[h]=nuestras.get(h,0)+1
        pr=premios(res,nuestras)
        tot.append(sum(pr[h] for h in hits if h>=10)); mejor.append(max(hits))
    return tot, mejor, n
def fila(nombre, cols):
    tot,mejor,n=simular(cols); coste=len(cols)*0.75
    xs=statistics.mean(cc.count('X') for cc in cols)
    print(f"{nombre:<40} {coste:5.2f} €  X/col {xs:.1f}  EV {statistics.mean(tot):6.2f} € ({statistics.mean(tot)/coste:4.0%})  cobra {sum(1 for g in tot if g>0)/n:5.1%}  recupera {sum(1 for g in tot if g>=coste)/n:5.1%}  >=100 € {sum(1 for g in tot if g>=100)/n:5.2%}  >=1000 € {sum(1 for g in tot if g>=1000)/n:5.2%}  14 {sum(1 for m in mejor if m==14)/n:.3%}")
    return tot,mejor
print("valor por signo con la popularidad de eduardolosilla (p/popularidad):")
for i,nm in enumerate(nombres):
    r=[P[i][k]/pub[i][k] for k in range(3)]
    print(f"{i+1:>2} {nm:<26} p {P[i][0]:.2f}·{P[i][1]:.2f}·{P[i][2]:.2f}  público {pub[i][0]:.2f}·{pub[i][1]:.2f}·{pub[i][2]:.2f}  valor {r[0]:.2f}·{r[1]:.2f}·{r[2]:.2f}")
print(f"X esperadas {sum(p[1] for p in P):.2f} · X del público por columna {sum(q[1] for q in pub):.2f}")
A="21X1X111X11211"; B="21211111111221"
def mult(posiciones, pares):
    out=[]
    for combo in itertools.product(*pares):
        col=list("21211111111211")
        for pos,s in zip(posiciones,combo): col[pos]=s
        out.append("".join(col))
    return out
actual=mult((2,4,8,12),("X2","1X","1X","12"))
robusta=mult((2,4,8,13),("X2","1X","X1","1X"))
# búsqueda de la mejor múltiple de 4 dobles: elegir 4 partidos entre los 8 abiertos y el par de signos de mayor p en cada uno
abiertos=[2,4,8,9,12,13,1,3]
cands=[]
for pos in itertools.combinations(abiertos,4):
    pares=[]
    for p_ in pos:
        orden=sorted(range(3),key=lambda k:-P[p_][k]); pares.append(S[orden[0]]+S[orden[1]])
    cands.append((pos,pares))
print(f"\n{len(cands)} múltiples candidatas de 4 dobles; evalúo EV con 4.000 simulaciones cada una...")
res=[]
for pos,pares in cands:
    cols=mult(pos,pares); tot,_,n=simular(cols,4000,seed=1); res.append((statistics.mean(tot),pos,pares))
res.sort(reverse=True)
print("\n" + " "*41 + "coste   X/col   EV (retorno)   P(cobrar) P(recuperar) P(>=100) P(>=1000) P(14)")
fila("sencilla A x16 (referencia)", [A]*16)
fila("sencilla B x16 (referencia)", [B]*16)
fila("múltiple actual (3,5,9,13)", actual)
fila("múltiple X infravaloradas (3,5,9,14)", robusta)
for ev_,pos,pares in res[:3]:
    fila(f"múltiple mejor EV: partidos {','.join(str(p+1) for p in pos)} {'/'.join(pares)}", mult(pos,pares))
json.dump({"pub":pub,"mejores":[(e,[p+1 for p in pos],pares) for e,pos,pares in res[:10]]}, open('valor2.json','w'), indent=1)
