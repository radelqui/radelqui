# -*- coding: utf-8 -*-
"""Elo + logit ordenado sobre 8 temporadas de Primera y Segunda (football-data.co.uk), para la jornada 11 de la Quiniela."""
import csv, glob, math, json, collections
from datetime import datetime

rows = []
for f in sorted(glob.glob('fd/*.csv')):
    with open(f, encoding='utf-8-sig') as fh:
        for r in csv.DictReader(fh):
            if r.get('FTR') in ('H', 'D', 'A'):
                r['_d'] = datetime.strptime(r['Date'], '%d/%m/%Y'); r['_div'] = r['Div']; rows.append(r)
rows.sort(key=lambda r: r['_d'])

# ---- Elo
K, HFA = 20, 60
elo = collections.defaultdict(lambda: 1500.0)
hist = []  # (diff_con_hfa, resultado 0/1/2 = 1/X/2, fecha, div, odds)
form = collections.defaultdict(list)
h2h = collections.defaultdict(list)
for r in rows:
    h, a = r['HomeTeam'], r['AwayTeam']
    hg, ag = int(r['FTHG']), int(r['FTAG'])
    d = elo[h] + HFA - elo[a]
    res = {'H': 0, 'D': 1, 'A': 2}[r['FTR']]
    odds = None
    try:
        oh, od, oa = float(r['AvgH']), float(r['AvgD']), float(r['AvgA'])
        s = 1/oh + 1/od + 1/oa; odds = (1/oh/s, 1/od/s, 1/oa/s)
    except Exception: pass
    hist.append((d, res, r['_d'], r['_div'], odds))
    exp = 1/(1+10**(-d/400)); sc = {0: 1, 1: 0.5, 2: 0}[res]
    mult = math.log(abs(hg-ag)+1) + 1 if hg != ag else 1
    delta = K*mult*(sc-exp); elo[h] += delta; elo[a] -= delta
    form[h].append(('L', hg, ag, 3 if res == 0 else 1 if res == 1 else 0, r['_d'], a))
    form[a].append(('V', ag, hg, 3 if res == 2 else 1 if res == 1 else 0, r['_d'], h))
    h2h[frozenset((h, a))].append((r['_d'].strftime('%d/%m/%y'), h, hg, ag, a))

# ---- logit ordenado P(1),P(X),P(2) ~ diff  (ajuste por descenso de gradiente, sin numpy)
def probs(d, b, c1, c2):
    z = b*d
    p2 = 1/(1+math.exp(z - c1))          # P(y>=... ) orden: 2 < X < 1
    px2 = 1/(1+math.exp(z - c2))
    return (1-px2, px2-p2, p2)            # (P1, PX, P2)
def nll(params, data):
    b, c1, c2 = params; s = 0
    for d, res, *_ in data:
        p = probs(d, b, c1, c2)[res]; s -= math.log(max(p, 1e-9))
    return s/len(data)
train = [x for x in hist if x[2] < datetime(2024, 8, 1)]
test = [x for x in hist if x[2] >= datetime(2024, 8, 1)]
b, c1, c2 = 0.005, -0.8, 0.4
lr = 0.02
for it in range(400):
    gb = gc1 = gc2 = 0
    for d, res, *_ in train:
        eps = 1e-4
        base = -math.log(max(probs(d, b, c1, c2)[res], 1e-9))
        gb += (-math.log(max(probs(d, b+eps, c1, c2)[res], 1e-9)) - base)/eps
        gc1 += (-math.log(max(probs(d, b, c1+eps, c2)[res], 1e-9)) - base)/eps
        gc2 += (-math.log(max(probs(d, b, c1, c2+eps)[res], 1e-9)) - base)/eps
    n = len(train); b -= lr*gb/n*0.001; c1 -= lr*gc1/n; c2 -= lr*gc2/n
params = (b, c1, c2)
ll_model = nll(params, test)
ll_book = -sum(math.log(x[4][x[1]]) for x in test if x[4])/sum(1 for x in test if x[4])
seg = [x for x in hist if x[3] == 'SP2']
base = collections.Counter(x[1] for x in seg); n = len(seg)
print(f"ajuste: b={b:.5f} c1={c1:.3f} c2={c2:.3f} · log-loss test modelo {ll_model:.4f} vs casas {ll_book:.4f} (n={len(test)})")
print(f"base Segunda 2018-26 (n={n}): 1 {base[0]/n:.1%} · X {base[1]/n:.1%} · 2 {base[2]/n:.1%}")

jornada = [("Albacete", "Eibar"), ("Almeria", "Burgos"), ("Cadiz", "Leganes"), ("Sabadell", "Andorra"), ("Sociedad B", "Granada"),
           ("Sp Gijon", "Celta B"), ("Castellon", "Ceuta"), ("Las Palmas", "Valladolid"), ("Girona", "Mallorca"), ("Cordoba", "Tenerife")]
out = []
for h, a in jornada:
    d = elo[h] + HFA - elo[a]; p = probs(d, *params)
    fh = form[h][-6:]; fa = form[a][-6:]
    pts_h = sum(x[3] for x in fh); pts_a = sum(x[3] for x in fa)
    hh = h2h[frozenset((h, a))][-8:]
    cnt = collections.Counter('1' if (x[1] == h and x[2] > x[3]) or (x[4] == h and x[3] > x[2]) else 'X' if x[2] == x[3] else '2' for x in hh)
    out.append({"local": h, "visitante": a, "elo_local": round(elo[h]), "elo_visit": round(elo[a]), "p1": round(p[0], 3), "px": round(p[1], 3), "p2": round(p[2], 3),
                "forma_local_6": pts_h, "forma_visit_6": pts_a, "h2h": [f"{x[0]} {x[1]} {x[2]}-{x[3]} {x[4]}" for x in hh], "h2h_signos": dict(cnt)})
    print(f"{h:>11} - {a:<11} Elo {elo[h]:.0f}/{elo[a]:.0f}  P1 {p[0]:.2f} PX {p[1]:.2f} P2 {p[2]:.2f}  forma6 {pts_h}/{pts_a}  h2h {dict(cnt)}")
json.dump({"params": params, "logloss_test": ll_model, "logloss_casas": ll_book, "base_segunda": {k: v/n for k, v in base.items()}, "partidos": out}, open('modelo.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
