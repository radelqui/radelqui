# -*- coding: utf-8 -*-
"""Simulación de jornadas pasadas para mejorar las probabilidades.
Modelo nuevo: logit ordenado con anchura de empate variable. z = b1*difElo + b2*nivel; anchura = exp(a0 + a1*golesEsperados + a2*tasaEmpates + a3*segunda).
Validación rodante por temporadas (entrenar con lo anterior, probar la temporada), frente al modelo base (solo difElo).
Métricas: log-loss, aciertos de la columna de máxima probabilidad, y precisión de las X cuando el modelo las señala."""
import csv, glob, math, collections, statistics, json
from datetime import datetime
rows=[]
for f in sorted(glob.glob('fd/*.csv')):
    for r in csv.DictReader(open(f,encoding='utf-8-sig')):
        if r.get('FTR') in 'HDA':
            o=None
            try: oh,od,oa=float(r['AvgH']),float(r['AvgD']),float(r['AvgA']); s=1/oh+1/od+1/oa; o=(1/oh/s,1/od/s,1/oa/s)
            except: pass
            rows.append(dict(d=datetime.strptime(r['Date'],'%d/%m/%Y'),h=r['HomeTeam'],a=r['AwayTeam'],hg=int(r['FTHG']),ag=int(r['FTAG']),res={'H':0,'D':1,'A':2}[r['FTR']],div=r['Div'],odds=o))
rows.sort(key=lambda r:r['d'])
# --- rasgos calculados solo con el pasado de cada partido
K,HFA=15,60
elo=collections.defaultdict(lambda:1500.0); ult=collections.defaultdict(list)  # (gf,gc,empate)
feats=[]
for r in rows:
    h,a=r['h'],r['a']
    def stats(t,n=10):
        u=ult[t][-n:]
        if len(u)<3: return (1.3,1.3,0.30)
        return (statistics.mean(x[0] for x in u),statistics.mean(x[1] for x in u),statistics.mean(x[2] for x in u))
    gfh,gch,xh=stats(h); gfa,gca,xa=stats(a)
    x=dict(dif=(elo[h]+HFA-elo[a])/100, nivel=((elo[h]+elo[a])/2-1500)/100, goles=(gfh+gca+gfa+gch)/2, emp=(xh+xa)/2, seg=1.0 if r['div']=='SP2' else 0.0)
    feats.append(x)
    exp=1/(1+10**(-(elo[h]+HFA-elo[a])/400)); sc={0:1,1:0.5,2:0}[r['res']]; m=math.log(abs(r['hg']-r['ag'])+1)+1 if r['hg']!=r['ag'] else 1
    dl=K*m*(sc-exp); elo[h]+=dl; elo[a]-=dl
    ult[h].append((r['hg'],r['ag'],1 if r['res']==1 else 0)); ult[a].append((r['ag'],r['hg'],1 if r['res']==1 else 0))
def F(t): return 1/(1+math.exp(-t))
def p_nuevo(x,th):
    b1,b2,m,a0,a1,a2,a3=th
    z=b1*x['dif']+b2*x['nivel']-m; w=math.exp(a0+a1*(x['goles']-2.5)+a2*(x['emp']-0.3)+a3*x['seg'])
    p1=1-F(-(z-w)); p2=F(-(z+w)); px=max(1e-6,1-p1-p2); s=p1+px+p2; return (p1/s,px/s,p2/s)
def p_base(x,th):
    b,c1,c2=th; z=b*x['dif']; p2=F(c1-z); px2=F(c2-z); return (1-px2,px2-p2,p2)
def nll(fn,th,idx): return -sum(math.log(max(fn(feats[i],th)[rows[i]['res']],1e-9)) for i in idx)/len(idx)
def ajustar(fn,th,idx,pasos=60,lr=0.5):
    th=list(th); best=nll(fn,th,idx)
    for it in range(pasos):
        g=[]
        for j in range(len(th)):
            t2=list(th); t2[j]+=1e-4; g.append((nll(fn,t2,idx)-best)/1e-4)
        paso=lr
        while paso>1e-3:
            t2=[th[j]-paso*g[j] for j in range(len(th))]; v=nll(fn,t2,idx)
            if v<best: th,best=t2,v; break
            paso/=2
        else: break
    return th,best
def metricas(fn,th,idx):
    ll=nll(fn,th,idx); hits=0; xs_sel=0; xs_ok=0; x_real=0
    for i in idx:
        p=fn(feats[i],th); pred=max(range(3),key=lambda k:p[k]); hits+=(pred==rows[i]['res']); x_real+=(rows[i]['res']==1)
        if p[1]>=0.33: xs_sel+=1; xs_ok+=(rows[i]['res']==1)
    return ll, hits/len(idx), xs_sel, (xs_ok/xs_sel if xs_sel else float('nan')), x_real/len(idx)
temporadas=[(datetime(2023,8,1),datetime(2024,8,1),"2023-24"),(datetime(2024,8,1),datetime(2025,8,1),"2024-25"),(datetime(2025,8,1),datetime(2027,8,1),"2025-27")]
th_b=(0.4,-0.85,0.48); th_n=(0.4,0.0,0.15,-0.9,0.0,0.0,0.0)
print("VALIDACIÓN RODANTE (entrenar con todo lo anterior, probar la temporada)")
print(f"{'temporada':<9} {'modelo':<6} {'log-loss':>8} {'acierto col.':>12} {'X señaladas':>11} {'precisión X':>11} {'X reales':>8}")
for ini,fin,nombre in temporadas:
    tr=[i for i,r in enumerate(rows) if r['d']<ini and r['d']>=datetime(2019,1,1)]; te=[i for i,r in enumerate(rows) if ini<=r['d']<fin]
    th_b,_=ajustar(p_base,th_b,tr,40); th_n,_=ajustar(p_nuevo,th_n,tr,80)
    for nom,fn,th in (("base",p_base,th_b),("nuevo",p_nuevo,th_n)):
        ll,ac,xs,px,xr=metricas(fn,th,te); print(f"{nombre:<9} {nom:<6} {ll:8.4f} {ac:12.1%} {xs:11d} {px:11.1%} {xr:8.1%}")
    cas=[i for i in te if rows[i]['odds']]; llc=-sum(math.log(rows[i]['odds'][rows[i]['res']]) for i in cas)/len(cas); print(f"{nombre:<9} {'casas':<6} {llc:8.4f}")
print("\nparámetros finales nuevo:", [round(t,3) for t in th_n])
# --- aplicar a la jornada 11 (Segunda) con el estado actual
jor=[("Albacete","Eibar"),("Almeria","Burgos"),("Cadiz","Leganes"),("Sabadell","Andorra"),("Sociedad B","Granada"),("Sp Gijon","Celta B"),("Castellon","Ceuta"),("Las Palmas","Valladolid"),("Girona","Mallorca"),("Cordoba","Tenerife")]
def stats_now(t,n=10):
    u=ult[t][-n:]
    if len(u)<3: return (1.3,1.3,0.30)
    return (statistics.mean(x[0] for x in u),statistics.mean(x[1] for x in u),statistics.mean(x[2] for x in u))
col=json.load(open('columnas-afilado.json',encoding='utf-8'))['final']
print("\nJORNADA 11 · modelo nuevo frente al actual (1·X·2) y rasgos de empate")
nuevo=[]
for i,(h,a) in enumerate(jor):
    gfh,gch,xh=stats_now(h); gfa,gca,xa=stats_now(a)
    x=dict(dif=(elo[h]+HFA-elo[a])/100,nivel=((elo[h]+elo[a])/2-1500)/100,goles=(gfh+gca+gfa+gch)/2,emp=(xh+xa)/2,seg=1.0)
    p=p_nuevo(x,th_n); q=col[i]['modelo_afilado']; nuevo.append(p)
    print(f"{i+1:>2} {h:>11}-{a:<11} nuevo {p[0]:.2f}·{p[1]:.2f}·{p[2]:.2f}  actual {q[0]:.2f}·{q[1]:.2f}·{q[2]:.2f}  goles esperados {x['goles']:.2f}  tasa empates últimos 10: {xh:.0%}/{xa:.0%}")
json.dump({"th":th_n,"jornada":[{"partido":f"{h}-{a}","p":[round(v,3) for v in p]} for (h,a),p in zip(jor,nuevo)]},open('modelo-nuevo.json','w'),indent=1)
