# -*- coding: utf-8 -*-
import json, itertools
m = json.load(open('modelo.json', encoding='utf-8'))
modelo = {(p['local'], p['visitante']): (p['p1'], p['px'], p['p2']) for p in m['partidos']}
# quiniela15.com (294 quinielistas), 1-10 Segunda, 11-14 Liga F
comunidad = [(18,20,63),(72,17,11),(21,31,48),(65,20,15),(23,42,35),(73,14,13),(81,9,9),(68,20,12),(43,35,22),(38,37,25),(81,10,10),(10,14,76),(51,29,20),(67,17,16)]
# expertos: betbrothers, apuestas-deportivas, loterias1fuengirola (dobles repartidos)
expertos = [["2","2","12"],["1","1","1"],["X","X","X2"],["1","1","1X"],["X","X","1X2"],["1","1","1"],["1","1","1"],["1","1","1X"],["X","X","1X"],["1","1","1"],["1","1","1"],["2","2","2"],["2","1","12"],["1","X","1X"],]
nombres = ["Albacete - Eibar","Almería - Burgos","Cádiz - Leganés","Sabadell - Andorra","R. Sociedad B - Granada","Sporting - Celta B","Castellón - Ceuta","Las Palmas - Valladolid","Girona - Mallorca","Córdoba - Tenerife","Barcelona F - Real Madrid F","Deportivo F - Atlético F","Madrid CFF - Athletic F","Tenerife F - Logroño F"]
claves = list(modelo.keys())
# Liga F: juicio por clasificación 2026-27 (Barça 15 pts/21-2, RM 13, Madrid CFF 12, Athletic 10, Atlético 6, Logroño 6, Tenerife 5, Deportivo 5)
ligaf = {10: (0.70,0.18,0.12), 11: (0.15,0.22,0.63), 12: (0.42,0.27,0.31), 13: (0.45,0.30,0.25)}
def dist_exp(picks):
    d=[0,0,0]
    for s in picks:
        for ch in s: d["1X2".index(ch)] += 1/len(s)
    t=sum(d); return [x/t for x in d]
final=[]
for i,n in enumerate(nombres):
    c=[x/100 for x in comunidad[i]]; e=dist_exp(expertos[i])
    if i<10:
        mo=modelo[claves[i]]; w=(0.5,0.3,0.2); base=[w[0]*mo[k]+w[1]*c[k]+w[2]*e[k] for k in range(3)]
    else:
        mo=ligaf[i]; w=(0.5,0.3,0.2); base=[w[0]*mo[k]+w[1]*c[k]+w[2]*e[k] for k in range(3)]
    s=sum(base); p=[x/s for x in base]
    final.append({"n":i+1,"partido":n,"modelo":[round(x,2) for x in mo],"comunidad":[round(x,2) for x in c],"expertos":[round(x,2) for x in e],"p":[round(x,3) for x in p]})
signos="1X2"
colA=[signos[max(range(3),key=lambda k:f["p"][k])] for f in final]
# columna B: en los 4 partidos con menor margen entre 1ª y 2ª opción, jugar la 2ª opción
margen=[]
for f in final:
    ps=sorted(range(3),key=lambda k:-f["p"][k]); margen.append((f["p"][ps[0]]-f["p"][ps[1]], f["n"], signos[ps[1]]))
cambiar={n:s for _,n,s in sorted(margen)[:4]}
colB=[cambiar.get(f["n"],colA[i]) for i,f in enumerate(final)]
def esperado(col): return sum(f["p"][signos.index(col[i])] for i,f in enumerate(final))
def p_al_menos(col,k):
    ps=[f["p"][signos.index(col[i])] for i,f in enumerate(final)]
    dist=[1.0]+[0.0]*14
    for q in ps:
        nd=[0.0]*15
        for j,v in enumerate(dist):
            if v: nd[j]+=v*(1-q); 
            if v and j+1<15: nd[j+1]+=v*q
        dist=nd
    return sum(dist[k:])
print(f"{'#':>2} {'partido':<28} {'modelo':<16} {'comunidad':<16} {'expertos':<16} {'final':<18} A B")
for i,f in enumerate(final):
    fmt=lambda v:" ".join(f"{x:.2f}" for x in v)
    print(f"{f['n']:>2} {f['partido']:<28} {fmt(f['modelo']):<16} {fmt(f['comunidad']):<16} {fmt(f['expertos']):<16} {fmt(f['p']):<18} {colA[i]} {colB[i]}")
print("\nColumna A (máxima probabilidad):", "".join(colA), "· pleno 2-0")
print("Columna B (4 cambios en los más igualados):", "".join(colB), "· pleno 1-0")
for nom,col in (("A",colA),("B",colB)):
    print(f"  {nom}: aciertos esperados {esperado(col):.2f}/14 · P(>=10) {p_al_menos(col,10):.1%} · P(>=12) {p_al_menos(col,12):.1%} · P(14) {p_al_menos(col,14):.2%}")
json.dump({"final":final,"colA":colA,"colB":colB,"cambios_B":cambiar}, open('columnas.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
