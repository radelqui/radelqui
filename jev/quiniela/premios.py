# -*- coding: utf-8 -*-
"""Estimación de premios de la múltiple (4 dobles) en la jornada 11 con recaudación estimada de 1,35 M€.
Reparto oficial: 55 % a premios → 15: 7,5 % · 14: 16 % · 13: 7,5 % · 12: 7,5 % · 11: 7,5 % · 10: 9 %.
Acertantes esperados por categoría: columnas jugadas (R/0,75) × P(k aciertos) de una columna 'típica' (la que
reparte sus signos como los 294 quinielistas), condicionada al resultado real. Monte Carlo sobre nuestras probabilidades."""
import json, random, statistics
random.seed(11)
c = json.load(open('columnas.json', encoding='utf-8'))['final']
S = "1X2"; R = 1_350_000; N = R/0.75
share = {15: .075, 14: .16, 13: .075, 12: .075, 11: .075, 10: .09}
comunidad = [(18,20,63),(72,17,11),(21,31,48),(65,20,15),(23,42,35),(73,14,13),(81,9,9),(68,20,12),(43,35,22),(38,37,25),(81,10,10),(10,14,76),(51,29,20),(67,17,16)]
P = [f['p'] for f in c]
fijos = {1:"2",2:"1",4:"1",6:"1",7:"1",8:"1",10:"1",11:"1",12:"2",14:"1"}
dobles = {3:"X2",5:"1X",9:"1X",13:"12"}
import itertools
columnas = []
for combo in itertools.product(*[dobles[n] for n in sorted(dobles)]):
    col = []
    it = iter(combo)
    for n in range(1, 15): col.append(fijos[n] if n in fijos else next(it))
    columnas.append("".join(col))
B = "21211111111221"; A = "21X1X111X11211"
def conv(ps):
    d = [1.0] + [0.0]*14
    for q in ps:
        nd = [0.0]*15
        for j, v in enumerate(d):
            if v: nd[j] += v*(1-q); 
            if v and j+1 < 15: nd[j+1] += v*q
        d = nd
    return d
def premios(resultado):
    # acertantes esperados por categoría según la columna típica
    typ = conv([comunidad[i][S.index(resultado[i])]/100 for i in range(14)])
    ganadores = {k: N*typ[k] for k in (10, 11, 12, 13, 14)}
    ganadores[15] = ganadores[14]*0.25  # un cuarto de los 14 acierta el pleno (2-0 al 45 % es lo más jugado)
    fondo = {k: share[k]*R for k in share}
    premio = {}
    arrastre = 0.0
    for k in (15, 14):
        if ganadores[k] < 0.5: premio[k] = 0.0  # va a bote, no se reparte
        else: premio[k] = fondo[k]/ganadores[k]
    for k in (13, 12, 11, 10):
        if ganadores[k] < 0.5: arrastre += fondo[k]; premio[k] = 0.0
        else: premio[k] = (fondo[k]+arrastre)/ganadores[k]; arrastre = 0.0
    return premio
def simular(cols, n=20000):
    tot = []; mejor = []; porcat = {k: 0 for k in range(10, 15)}
    for _ in range(n):
        res = "".join(random.choices(S, weights=P[i])[0] for i in range(14))
        pr = premios(res); g = 0.0; m = 0
        for col in cols:
            h = sum(a == b for a, b in zip(col, res)); m = max(m, h)
            if h >= 10: g += pr[h]; porcat[h] += 1
        tot.append(g); mejor.append(m)
    return tot, mejor, porcat, n
tot, mejor, porcat, n = simular(columnas)
coste = len(columnas)*0.75
print(f"Múltiple {len(columnas)} columnas · coste {coste:.2f} €")
print(f"ganancia media {statistics.mean(tot):.2f} € · mediana {statistics.median(tot):.2f} € · P(cobrar algo) {sum(1 for g in tot if g>0)/n:.1%} · P(recuperar los 12 €) {sum(1 for g in tot if g>=coste)/n:.1%} · P(>=100 €) {sum(1 for g in tot if g>=100)/n:.1%} · P(>=1000 €) {sum(1 for g in tot if g>=1000)/n:.2%}")
for k in (14, 13, 12, 11, 10):
    casos = [g for g, m in zip(tot, mejor) if m == k]
    if casos: print(f"  si la mejor columna hace {k}: ocurre {len(casos)/n:.1%} de las veces · cobro medio total {statistics.mean(casos):.0f} € (mín {min(casos):.0f}, máx {max(casos):.0f})")
# premios por categoría típicos de la jornada (promedio sobre resultados simulados)
acum = {k: [] for k in (15,14,13,12,11,10)}
for _ in range(3000):
    res = "".join(random.choices(S, weights=P[i])[0] for i in range(14)); pr = premios(res)
    for k in acum: 
        if pr[k] > 0: acum[k].append(pr[k])
print("\npremio por apuesta esperado en esta jornada (mediana de resultados simulados):")
for k in (15,14,13,12,11,10): print(f"  {k} aciertos: {statistics.median(acum[k]) if acum[k] else 0:>10.2f} €")
for nombre, cols in (("sencilla B", [B]), ("sencilla A", [A])):
    t, m, pc, nn = simular(cols, 20000)
    print(f"\n{nombre}: coste 0,75 € · ganancia media {statistics.mean(t):.2f} € · P(cobrar) {sum(1 for g in t if g>0)/nn:.1%}")
