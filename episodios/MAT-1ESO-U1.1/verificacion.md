# Verificación · MAT-1ESO-U1.1 · Números grandes y aproximación · CUARTA VUELTA

## Veredicto: RECHAZADO

No hay errores numéricos. Quedan dos fallos de rigor (condición de validez en e15 y una afirmación vaga en e04), ambos de corrección rápida. La regla 2 («ciencia pura») se cumple en el resto del guion.

## Automática
- `pipeline/verificar.py`: 59 de 59 claims OK.
- Referencias del guion: todos los claims citados existen. El único claim sin escena es c66, que es la suma de duraciones de la cabecera.
- Cabecera: la suma de duraciones es 595 s (c66) y la locución tiene 1169 palabras sin pausas. Ambas coinciden. La media es de unas 118 palabras por minuto, que también coincide.
- Barrido de cifras: sin cifras sin claim. Las cifras decisivas (3, 4, 5, 9 y 8), los empujones (+1, +50 y +500), la diferencia 1934 y la franja 95 000–104 999 (10 000 números, 99 354 dentro por c76) están cubiertas. El único `×` que queda es el de la cabecera («nunca ×»).

## Revisión conceptual: correcto
- Valor posicional, tabla U–CM y descomposición de 99 354.
- Error al dictado (e07).
- Redondeo a los millares, con 354 y 646 y la mitad en 99 500 (e09).
- Redondeo a las decenas de millar, con 9354 y 646, y cierre «al redondear, siempre se dice a qué casilla» (e10).
- Mitad que sube, presentada como acuerdo y no como ley (e11, e16). Cumple la regla 2.
- Regla de la cifra siguiente (e12): 4 da 99 350, 5 da 99 400, 3 da 99 000 y 9 da 100 000.
- Estimación 150 000 frente a 148 066: se pasa en 1934 (e13). Es una cifra exacta, no «muy cerca».
- Redondeo en cadena (e14): 3449 → 3450 → 3500 → 4000, frente al 3000 correcto.
- Franja 95 000–104 999 y bordes 94 999 → 90 000 y 105 000 → 110 000 (e15).
- Concordancia de género correcta («trescientas… visualizaciones»).
- «Notación»: espacio fino declarado, 4 cifras sin separador y «· 10».
- Regla 2:
  - Las preguntas planteadas se cierran: e01 en e12; e03 en e05 y e06; e08 con sus dos razones; e09 y e10 con la distancia exacta; e11 con el acuerdo; e13 con la diferencia exacta; e15 con los límites.
  - No hay razonamientos sobre el significado de palabras («casi», «unos» han desaparecido).

## Fallos

**F1. e15, locución y «Se ve»: falta la condición de validez «enteros».**
- Línea del guion: «Un número, redondeado a las decenas de millar, da cien mil. ¿Cuál es el número más pequeño que pudo ser? ¿Y el más grande?», y «El más grande es ciento cuatro mil novecientos noventa y nueve… diez mil números posibles».
- Problema: sin decir que el número es entero, la respuesta es falsa. 104 999,9 también redondea a 100 000, así que no existe un «más grande» y hay infinitos números. Los 10 000 números solo se cuentan si son enteros. La pregunta queda sin cerrar con exactitud, contra la regla 2.
- Corrección propuesta: «Un número entero, redondeado a las decenas de millar, da cien mil». En e16, «un número redondo representa una franja exacta de números enteros». El contexto (visualizaciones) es entero, pero el enunciado general debe decirlo.

**F2. e04, locución: «Te pierdes, y tardarías horas» es una afirmación sin cifra.**
- Problema: «miles de cosas», a una por segundo, son desde unos 17 minutos (1000) hasta varias horas (10 000 o más). «Horas» no es cierto para cualquier cantidad de miles. La versión anterior era «con miles, te pierdes, y contar de una en una llevaría horas». La regla 2 pide no dejar afirmaciones vagas.
- Corrección propuesta: quitar la duración («Te pierdes y es muy fácil equivocarse») o dar una cifra verificable («Contar diez mil cosas, a una por segundo, llevaría casi tres horas», con su claim).

## Observaciones (no bloquean)
- e12: «Esa cifra te dice en qué mitad del camino estás» se enuncia sin mostrar el cálculo. Es válido para el nivel. Si se quiere mayor rigor, mostrar en la recta que el 5 es la mitad exacta.
- e09: «¿Y cuál es el número redondo correcto?» es una pregunta algo ambigua (depende de la casilla), pero se cierra en la propia e09 («A los millares, ese número es 99 000») y en e10. Se puede sustituir por «¿A qué millar redondeamos?».
- e17: el adelanto («Dos calculadoras dan resultados distintos… vas a ver por qué») deja una pregunta abierta, aunque es una promesa explícita para el próximo vídeo. Decisión del coordinador o de la persona que revise si encaja con la regla 2. Matemáticamente es correcto (14 con la jerarquía normal).
