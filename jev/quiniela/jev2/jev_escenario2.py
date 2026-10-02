# -*- coding: utf-8 -*-
"""Jev ante el nuevo escenario: dossier con cuotas de mercado, público, Elo, forma, directos y valor; signo por partido,
veredicto por doble, nota de la múltiple y afirmaciones finales. Clave en TYPESAFE_API_KEY o ~/.env.jev."""
import json, os, re, sys, time, urllib.request, urllib.error
from pathlib import Path
AQUI=Path(__file__).resolve().parent; BASE=AQUI.parent
URL=os.environ.get("JEV_ENDPOINT","https://api.typesafe.ai/v1/systemone"); MODELO="jev-1.13.0"; S="1X2"
fm=json.load(open(BASE/'final-mercado.json')); P=fm['P']; mk=json.load(open(BASE/'mercado.json')); pub=json.load(open(BASE/'valor2.json'))['pub']
m=json.load(open(BASE/'modelo.json',encoding='utf-8'))['partidos']; cols=json.load(open(BASE/'columnas.json',encoding='utf-8'))['final']
cuotas={1:(2.67,3.32,2.46),2:(1.59,3.72,5.50),3:(2.77,3.13,2.50),4:(2.03,3.25,3.62),5:(2.50,3.23,2.67),6:(1.53,4.07,5.58),7:(1.24,6.00,9.17),8:(2.13,3.18,3.37),9:(2.15,3.35,3.13),10:(1.90,3.42,3.75)}
ligaf={11:"Liga F 2026-27, jornada 6. Barcelona F 1ª con 15 puntos, 21 goles a favor y 2 en contra; Real Madrid F 2ª con 13. Barcelona ha ganado todos los clásicos ligueros recientes. Sin cuotas disponibles.",
12:"Liga F. Deportivo F 11º con 5 puntos (4 goles a favor, 4 en contra); Atlético F 8º con 6 (8 a favor, 10 en contra). Sin cuotas disponibles.",
13:"Liga F. Madrid CFF 3º con 12 puntos (4 victorias, 1 derrota); Athletic F 4º con 10 (3 victorias, 1 empate, 1 derrota). Athletic ganó los dos duelos de la temporada pasada. Sin cuotas disponibles.",
14:"Liga F. Tenerife F 14º con 5 puntos (4 a favor, 10 en contra); Logroño F 7º con 6 (4 a favor, 5 en contra). Sin cuotas disponibles."}
sec=[]
for i in range(14):
    n=i+1; f=cols[i]; t=[f"PARTIDO {n}: {f['partido']}."]
    if n<=10:
        p=m[i]; o=cuotas[n]; pm=mk[str(n)]
        t.append(f"Segunda División. Cuotas medias de las casas (1/X/2): {o[0]}/{o[1]}/{o[2]}, que sin margen equivalen a {pm[0]:.0%}/{pm[1]:.0%}/{pm[2]:.0%}.")
        t.append(f"Elo: local {p['elo_local']}, visitante {p['elo_visit']} (ventaja de campo +60). Puntos en los últimos 6: local {p['forma_local_6']}/18, visitante {p['forma_visit_6']}/18. Directos desde 2018: "+("; ".join(p['h2h']) if p['h2h'] else "ninguno")+".")
    else: t.append(ligaf[n]+f" Probabilidad estimada por el analista: {P[i][0]:.0%}/{P[i][1]:.0%}/{P[i][2]:.0%}.")
    q=pub[i]; t.append(f"Porcentaje de apuestas del público (sitio quinielista): 1 {q[0]:.0%}, X {q[1]:.0%}, 2 {q[2]:.0%}. Valor (probabilidad/público): 1 {P[i][0]/q[0]:.2f}, X {P[i][1]/q[1]:.2f}, 2 {P[i][2]/q[2]:.2f}.")
    sec.append("\n".join(t))
contexto=("DOSSIER: jornada 11 de La Quiniela (3-5 de octubre de 2026), 14 partidos 1X2 más pleno al 15 (España-República Checa). Para cada partido: cuotas de las casas (la mejor estimación de probabilidad disponible; en 8 temporadas baten a cualquier modelo de historial), Elo, forma, directos, porcentaje de apuestas del público y valor (probabilidad/público). Un valor mayor que 1,2 significa que el público apuesta ese signo menos de lo que merece, y si acierta se reparte el premio entre menos gente. El fondo de premios es el 55 % de lo recaudado; el 14 reparte el 16 % entre sus acertantes.\n\n"
"APUESTA PROPUESTA (12 €, 16 columnas): base = signo más probable del mercado en cada partido (2 1 2 1 1 1 1 1 1 1 1 2 1 1), con cuatro dobles: partido 1 Albacete-Eibar 2 y 1; partido 4 Sabadell-Andorra 1 y X; partido 10 Córdoba-Tenerife 1 y X; partido 13 Madrid CFF-Athletic 1 y 2. Pleno al 15: 2-0. Alternativas descartadas: (a) la múltiple anterior con dobles X2, X1, X1, 1X en los partidos 3, 5, 9 y 14, construida sobre la creencia, luego desmentida por las cuotas, de que la X valía 42 % en los partidos 3, 5 y 9; (b) una múltiple de máximo acierto con dobles 12, 21, 21, 12 en los partidos 5, 3, 1 y 13, sin ninguna X. En el histórico de 233 jornadas de Segunda salen 4,1 empates por jornada; el público juega 2,3 en estos 10 partidos y el mercado espera 2,6.\n\n")
DOSSIER=contexto+"\n\n".join(sec)
def clave():
    k=os.environ.get("TYPESAFE_API_KEY"); f=Path.home()/".env.jev"
    if not k and f.exists():
        for l in f.read_text(encoding="utf-8",errors="replace").splitlines():
            mm=re.match(r"\s*TYPESAFE_API_KEY\s*=\s*(.+)",l)
            if mm: k=mm.group(1).strip().strip("\"'")
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
        except Exception as e: print("intento",i,type(e).__name__)
        time.sleep(10*i)
    sys.exit(6)
k=clave(); (AQUI/"jev-dossier-escenario2.md").write_text(DOSSIER,encoding="utf-8"); print(f"dossier {len(DOSSIER)} caracteres")
# 1) signo por partido
q1={f"P{i+1:02d}":{"type":"choice","instructions":f"PARTIDO {i+1} ({cols[i]['partido']}): con los datos de su sección, ¿qué signo es el más probable?","criteria":{"1":"Gana el local.","X":"Empate.","2":"Gana el visitante."}} for i in range(14)}
r1=llamar(q1,k)
# 2) por partido: ¿qué merece jugarse en una múltiple de 16 columnas que busca premio con pocos acertantes?
q2={f"J{i+1:02d}":{"type":"choice","instructions":f"PARTIDO {i+1} ({cols[i]['partido']}): en una múltiple de 16 columnas que busca cobrar con pocos acertantes, ¿qué conviene jugar en este partido?","criteria":{"fijo_1":"Fijo al 1.","fijo_X":"Fijo a la X.","fijo_2":"Fijo al 2.","doble_1X":"Doble 1 y X.","doble_12":"Doble 1 y 2.","doble_X2":"Doble X y 2."}} for i in range(14)}
r2=llamar(q2,k)
# 3) veredicto sobre la apuesta
q3={"D01":{"type":"choice","instructions":"¿Es correcto construir la base de la múltiple con el signo más probable del mercado en lugar de con el modelo propio o con el foro?","criteria":{"si":"Sí, el mercado es la mejor probabilidad disponible.","no":"No, hay una fuente mejor en el dossier.","no_determinable":"No se puede decidir con el dossier."}},
"D02":{"type":"choice","instructions":"¿Fue correcto abandonar la múltiple anterior (X en 3, 5, 9 y 14) al ver las cuotas?","criteria":{"si":"Sí.","no":"No, las X seguían siendo buenas.","no_determinable":"No se puede decidir."}},
"D03":{"type":"choice","instructions":"¿Conviene que la múltiple tenga más empates que la propuesta (una X por columna de media), dado que el histórico da 4,1 por jornada?","criteria":{"si":"Sí, faltan X.","no":"No, con estas cuotas no hay dónde ponerlas.","no_determinable":"No se puede decidir."}},
"D04":{"type":"choice","instructions":"¿Es un error dejar fijo el 2 en Cádiz-Leganés (37 %) en lugar de doblarlo?","criteria":{"si":"Sí, debería ser doble.","no":"No, el fijo es razonable.","no_determinable":"No se puede decidir."}},
"D05":{"type":"choice","instructions":"¿Es un error dejar fijo el 1 en Las Palmas-Valladolid (43 %) cuando el 2 tiene valor 1,83?","criteria":{"si":"Sí, debería doblarse 1 y 2.","no":"No, el fijo es razonable.","no_determinable":"No se puede decidir."}},
"D06":{"type":"choice","instructions":"¿Es un error dejar fijo el 1 en R. Sociedad B-Granada (37 % frente a 35 % del 2)?","criteria":{"si":"Sí, debería ser doble 1 y 2.","no":"No, el fijo es razonable.","no_determinable":"No se puede decidir."}},
"D07":{"type":"choice","instructions":"¿El doble en Madrid CFF-Athletic (sin cuotas) debería sustituirse por un doble en un partido de Segunda con cuotas?","criteria":{"si":"Sí.","no":"No.","no_determinable":"No se puede decidir."}},
"D08":{"type":"choice","instructions":"¿El pleno al 15 fijo en 2-0 es la mejor elección para España-República Checa, con España a cuota 1,14?","criteria":{"si":"Sí.","no":"No, otro marcador es más probable.","no_determinable":"No se puede decidir."}},
"D09":{"type":"choice","instructions":"¿Tiene esta múltiple más esperanza de premio que la múltiple de máximo acierto sin X (dobles 12, 21, 21, 12 en los partidos 5, 3, 1 y 13)?","criteria":{"si":"Sí.","no":"No.","no_determinable":"No se puede decidir."}},
"D10":{"type":"choice","instructions":"Si hubiera que cambiar un solo doble de la propuesta, ¿cuál?","criteria":{"ninguno":"Dejarla como está.","quitar_1":"Quitar el doble de Albacete-Eibar.","quitar_4":"Quitar el doble de Sabadell-Andorra.","quitar_10":"Quitar el doble de Córdoba-Tenerife.","quitar_13":"Quitar el doble de Madrid CFF-Athletic."}},
"D11":{"type":"choice","instructions":"Si hubiera que añadir un doble (pasando a 32 columnas, 24 €), ¿dónde?","criteria":{"p3":"Cádiz-Leganés.","p5":"R. Sociedad B-Granada.","p8":"Las Palmas-Valladolid.","p9":"Girona-Mallorca.","p14":"Tenerife F-Logroño.","ninguno":"No añadir."}},
"NOTA":{"type":"score","instructions":"Califica la apuesta propuesta como forma de jugar 12 € a esta jornada buscando premio con pocos acertantes.","criteria":["Mala: va contra los datos.","Floja: desaprovecha el valor evidente.","Aceptable: razonable con mejoras claras.","Buena: bien construida, mejoras menores.","Muy buena: no la cambiaría."]},
"F1":{"type":"noul","instructions":"Afirmación: la apuesta propuesta es mejor que la múltiple anterior con X en los partidos 3, 5, 9 y 14."},
"F2":{"type":"noul","instructions":"Afirmación: con estas cuotas, ninguna apuesta de 12 € tiene esperanza positiva; lo máximo que se puede hacer es no pagar la prima del público por los favoritos."}}
r3=llamar(q3,k)
uso={k_:r1['usage'][k_]+r2['usage'][k_]+r3['usage'][k_] for k_ in r1['usage']}
json.dump({"r1":r1,"r2":r2,"r3":r3},open(AQUI/"jev-escenario2-crudo.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
base="21211111111211"; propuesta={1:"21",4:"1X",10:"1X",13:"12"}
print(f"\nuso {uso}\n\n # partido                      Jev signo  P(1) P(X) P(2)   Jev jugaría    propuesta")
colJ=""; filas=[]
for i in range(14):
    a=r1['answers'][f"P{i+1:02d}"]; pr={x:float(y) for x,y in a['probabilities'].items()}; s=max("1X2",key=lambda x:pr.get(x,0)); colJ+=s
    b=r2['answers'][f"J{i+1:02d}"]; jug=b['choice']; prop=propuesta.get(i+1,"fijo_"+base[i])
    filas.append({"n":i+1,"partido":cols[i]['partido'],"jev":s,"p":pr,"jugaria":jug,"p_jugaria":{x:round(float(y),2) for x,y in b['probabilities'].items()},"propuesta":prop})
    print(f"{i+1:>2} {cols[i]['partido']:<28} {s:^9}  {pr.get('1',0):.2f} {pr.get('X',0):.2f} {pr.get('2',0):.2f}   {jug:<12}   {prop}{'  <- distinto' if jug!=prop else ''}")
print(f"\ncolumna Jev {colJ} · coincide con la base en {sum(1 for a,b in zip(colJ,base) if a==b)}/14")
print("\nVEREDICTO:")
for q in ("D01","D02","D03","D04","D05","D06","D07","D08","D09","D10","D11"):
    a=r3['answers'][q]; pr={x:round(float(y),2) for x,y in a['probabilities'].items()}; print(f"  {q} {a['choice']:<10} {pr}   {q3[q]['instructions'][:95]}")
n=r3['answers']['NOTA']; print(f"  NOTA {n.get('score')} (0-4) confianza {n.get('confidence')} · {n.get('legend')}")
print(f"  F1 'mejor que la anterior': {r3['answers']['F1'].get('noul')} · F2 'nadie tiene esperanza positiva': {r3['answers']['F2'].get('noul')}")
json.dump({"modelo":MODELO,"cuando":time.strftime("%Y-%m-%dT%H:%M:%S"),"uso":uso,"columna_jev":colJ,"filas":filas,"veredicto":{q:r3['answers'][q] for q in r3['answers']}},open(AQUI/"jev-escenario2.json","w",encoding="utf-8"),ensure_ascii=False,indent=1)
