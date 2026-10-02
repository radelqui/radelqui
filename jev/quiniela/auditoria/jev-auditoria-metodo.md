# Auditoría del método por Jev · jornada 11

Modelo `jev-1.13.0` · 37,126 tokens de entrada, 3,595 de salida (unos 4 céntimos) · 83 preguntas en 8 familias, una llamada por familia, más una afirmación final.

**Afirmación final** «el método tiene al menos una debilidad que, por sí sola, invalida la recomendación»: **P = 0.83**.

## Gravedad por familia (0 irrelevante · 4 crítica)

| Familia | Gravedad | Lectura |
|---|---|---|
| A Datos | 3.07 | Alta |
| B Modelo | 3.11 | Alta |
| C Mezcla de fuentes | 3.14 | Alta |
| D Popularidad y premios | 3.23 | Alta |
| E Análisis de valor | 2.81 | Alta |
| F Construcción de la múltiple | 3.26 | Alta |
| G Uso de Jev | 1.81 | Media |
| H Proceso y decisión | 3.33 | Alta |

Jev señala el **proceso** (3,33), la **múltiple** (3,26) y los **premios** (3,23) como lo más grave, y el **uso de Jev** (1,81) como lo menos. Nota: Jev dice «sí» con P ≥ 0,9 a 39 de 83 preguntas; tiene sesgo a confirmar la debilidad que se le sugiere, así que vale más lo que **descarta** y la **ordenación** que los 1,00.

## Lo que Jev descarta (P(sí) ≤ 0,10)

- **B06** (P 0.00): ¿La calibración 1,1 medida sobre 2024-26 garantiza que las probabilidades de esta jornada están bien calibradas en los partidos igualados?
- **A06** (P 0.03): ¿Faltan las cuotas de las casas para los partidos de esta jornada, y su ausencia debilita el modelo más que cualquier otro dato?
- **H10** (P 0.03): ¿La documentación del método permite reproducir los números exactos por una tercera persona?
- **B05** (P 0.05): ¿Que el modelo pierda frente a las casas (1,017 contra 0,994 de log-loss) significa que apostar contra el público usando el modelo no tiene base?
- **F01** (P 0.07): ¿Elegir los 4 dobles por mayor esperanza en una búsqueda sobre 70 combinaciones con 4.000 simulaciones cada una es suficientemente estable?
- **F02** (P 0.07): ¿Descartar el 2 en Madrid CFF-Athletic (31 %) para dejar fijo el 1 es coherente con el criterio de valor aplicado en otros partidos?
- **C03** (P 0.09): ¿Los pesos 50/30/20 sin ajuste son un riesgo mayor que cualquier otro supuesto del método?

Es decir: la elección de los 4 dobles es estable, descartar el 2 de Madrid CFF es coherente, que el modelo pierda frente a las casas no invalida apostar contra el público, la calibración 1,1 no garantiza nada en partidos igualados (ahí el «no» es malo para nosotros), y los pesos 50/30/20 no son el mayor riesgo.

## Las 25 debilidades más probables según Jev

| # | P(sí) | Debilidad |
|---|---|---|
| A01 | 1.00 | ¿Faltan datos relevantes para 4 de los 14 partidos (Liga F) hasta el punto de que esas probabilidades sean poco más que una opinión? |
| C01 | 1.00 | ¿Usar el porcentaje de una comunidad de 294 quinielistas como el 30 % de la probabilidad confunde popularidad con probabilidad? |
| C09 | 1.00 | ¿El analista debería haber medido la sensibilidad del resultado a los pesos antes de recomendar? |
| D01 | 1.00 | ¿Usar los porcentajes de un sitio web en lugar de los oficiales de Loterías puede cambiar qué signos aparecen como infravalorados? |
| G02 | 1.00 | ¿Las probabilidades extremas (1,00/0,00 en nueve partidos) indican que Jev no debe usarse como estimador de probabilidad en este dominio? |
| H01 | 1.00 | ¿Que la recomendación cambiara tres veces en pocas horas indica que el método no estaba estabilizado antes de recomendar? |
| H03 | 1.00 | ¿La corrección tardía de las cifras de acertantes sugiere que otras cifras del estudio podrían tener errores no detectados? |
| H04 | 1.00 | ¿Falta un plan de actualización con alineaciones antes del cierre del sábado a las 14:00? |
| H05 | 1.00 | ¿La dependencia de una sola fuente de popularidad y de tres pronosticadores hace frágil la conclusión? |
| H06 | 1.00 | ¿El estudio debería incluir una prueba retrospectiva: aplicar el método completo a 20 jornadas pasadas y ver qué habría cobrado? |
| H11 | 1.00 | ¿Hay algún punto del dossier donde el analista afirme más de lo que sus datos demuestran? |
| B04 | 0.98 | ¿Un logit ordenado con solo la diferencia de Elo como variable es demasiado pobre frente a lo que las casas incorporan? |
| D03 | 0.98 | ¿La discrepancia con la realidad (modelo: ~4 acertantes de 14 y 124 de 13; realidad reciente: 0 de 14 y 2-22 de 13) invalida las estimaciones absolutas de premio? |
| D09 | 0.98 | ¿El reparto por categorías citado (7,5/16/7,5/7,5/7,5/9) debería verificarse en la normativa antes de confiar en él? |
| A02 | 0.97 | ¿Es un problema que Ceuta, Sabadell y Andorra tengan un Elo casi inicial (1500 más 7 partidos), de modo que sus partidos estén mal medidos? |
| A07 | 0.97 | ¿Agrupar jornadas históricas por semana natural (9-12 partidos) puede producir jornadas artificiales que distorsionen la estadística de empates? |
| B01 | 0.97 | ¿Un K fijo de 20 sin periodo de arranque rápido para equipos nuevos es una debilidad que afecta a esta jornada en concreto? |
| B02 | 0.97 | ¿Una ventaja de campo fija de +60 para todos los equipos y divisiones es una simplificación que sesga partidos concretos? |
| G08 | 0.97 | ¿Jev sería más útil evaluando el método (como ahora) que prediciendo partidos? |
| B08 | 0.96 | ¿La ausencia de decaimiento temporal hace que resultados de 2018-2020 pesen tanto como los recientes y contaminen el Elo actual? |
| B09 | 0.96 | ¿Es una debilidad no usar los goles esperados (xG) que la base ya trae? |
| C06 | 0.96 | ¿Las probabilidades a ojo de la Liga F (por ejemplo 70/18/12 para Barcelona-Real Madrid) deberían considerarse el eslabón más débil de la mezcla? |
| G07 | 0.96 | ¿Fue correcto tratar a Jev como un voto más (sin peso en las probabilidades) en lugar de descartarlo o de integrarlo? |
| H02 | 0.95 | ¿Hay riesgo de que el analista haya ajustado el análisis para confirmar la intuición del jugador sobre los empates? |
| A04 | 0.94 | ¿Ignorar alineaciones, lesiones y sanciones es una debilidad grave para partidos que se juegan 1 a 3 días después del análisis? |

Abstenciones: C07, C08, D08 (independencia de los pronosticadores, sesgo del foro, pleno al 15).

## Respuesta del analista a lo accionable hoy

**C09 · Sensibilidad a los pesos (hecho).** Con pesos modelo/comunidad/pronosticadores de 50/30/20, 70/20/10, 40/40/20 y 30/30/40 los cuatro dobles no cambian (3: X2, 5: X1, 9: X1, 14: 1X) y las X infravaloradas siguen siendo las de los partidos 3, 5 y 9. Solo con el modelo a solas (90/10/0 o 100/0/0) cambia el reparto: el valor se va a signos raros (2 en Almería-Burgos, X en Sporting-Celta B) porque el modelo reparte la X casi plana. **La estructura de la apuesta es robusta a los pesos; el valor concreto de cada X, no tanto.**

**B01/B02/B08 · Parámetros del Elo (hecho).** Probados K = 15, 20, 30, 40; ventaja de campo 40, 60, 80; con y sin decaimiento temporal. El mejor es K = 15 sin decaimiento (log-loss 1,0141 frente a 1,0157 del actual; las casas 0,9936). Las probabilidades de los 10 partidos de Segunda cambian como mucho 2 puntos. **No cambia ningún signo.**

**H06 · Prueba retrospectiva 2024-26 (hecho, y es la mala noticia).** 80 semanas de Segunda con el modelo entrenado solo hasta 2024:

| Estrategia | Aciertos medios /14 | ≥10 | ≥11 | ≥12 |
|---|---|---|---|---|
| Todo 1 | 6,30 | 6 % | 1 % | 0 % |
| Signo de máxima probabilidad del modelo (como B) | 6,52 | 8 % | 4 % | 1 % |
| X donde el modelo da P(X) ≥ 30 % (7,8 X por columna) | 5,39 | 2 % | 1 % | 0 % |

El modelo **nunca** da P(X) ≥ 33 %, así que por sí solo nunca juega una X, y cuando se le obliga a jugarlas pierde. Sabe que salen 3,5 empates por jornada pero **no sabe en cuáles**. Las X de la columna A y de la múltiple vienen de la comunidad y los pronosticadores, no del modelo, y eso no se puede probar hacia atrás porque no hay porcentajes históricos. Esto confirma la debilidad B03 (sin propensión al empate por equipo) y rebaja la fuerza del argumento de valor: **sabemos que el público juega pocas X; no sabemos demostrar que sabemos dónde caen.**

**D01 · Popularidad (parcial).** Los porcentajes oficiales de Loterías no se pudieron obtener. Tres fuentes de usuarios discrepan hasta 13 puntos en la X del mismo partido (R. Sociedad B-Granada: 42 %, 29 %, 29 %; Girona-Mallorca: 35 %, 26 %, 27 %). El valor de la X en esos partidos depende de qué fuente se mire. **Fragilidad confirmada.**

**A01/C06 · Liga F (no resuelto).** Sin datos históricos; las probabilidades de 4 partidos son a ojo. Es el eslabón más débil y lo sigue siendo. Las fijas en esos 4 partidos (Barcelona 1, Atlético 2, Madrid CFF 1) coinciden con todas las fuentes; la duda real está en Tenerife F-Logroño, que ya va doblado.

**H04 · Alineaciones (no resuelto).** No hay plan de actualización antes del cierre del sábado a las 14:00. Si quieres, el sábado por la mañana reviso alineaciones y bajas de los 10 partidos de Segunda y digo si algún doble cambia.

## Conclusión revisada

1. **La múltiple de 12 € se mantiene** (2 1 X2 1 X1 1 1 1 X1 1 1 2 1 1X, pleno 2-0): su estructura resiste pesos, parámetros del Elo y fuentes de popularidad.
2. **Rebajo las expectativas:** el «retorno ~98 %» y el «165 % de la columna A» descansan en que las X estén donde dicen la comunidad y los pronosticadores, y eso no está demostrado. Lo honesto es: **retorno probablemente algo mejor que el 55 % del jugador medio, sin poder decir cuánto.**
3. **Lo que sí está demostrado** con 233 jornadas: una columna sin empates (B, Jev) está en el 8 % de jornadas más raras, y «todo favoritos» no llega a 12 de 14. Eso justifica meter X; no justifica prometer premio.
4. **Siguiente mejora real** si se quiere seguir jugando: un modelo con propensión al empate por equipo (goles esperados, ritmo de goles) y porcentajes oficiales de Loterías guardados cada jornada para poder probar el valor hacia atrás.
