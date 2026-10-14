# Verificación · MAT-1ESO-U1.1 · Números grandes y aproximación · SEGUNDA VUELTA

## Veredicto: RECHAZADO

Queda un fallo de lógica en e16 (corrección de una frase). Los 8 fallos de la primera vuelta están resueltos y no hay errores numéricos.

## Automática
- `pipeline/verificar.py`: 75 de 75 claims OK (c01 a c75).
- Barrido de cifras: no hay cifras sin claim.
  - Las cifras decisivas (3, 4, 5, 9, 8), los empujones (+1, +50, +500) y el razonamiento de «casi» a los millares están cubiertos (c62 a c65, c67 a c75).
  - Las duraciones suman 665 s (c66) y la cabecera lo indica.
  - El recuento de palabras de la locución, sin pausas, es 1397 y coincide con la cabecera.

## Fallos de la primera vuelta
1. «× 10»: resuelto. e05 y e18 usan «· 10». El único `×` que queda es la mención en la cabecera («nunca ×»).
2. Espacio fino: resuelto. La cabecera explica que el guion usa espacio normal y que el render pone el espacio fino sin separación.
3. «1.339 palabras»: resuelto. Ahora es «1397 palabras».
4. Concordancia: resuelta en e13 («trescientas cincuenta y cuatro personas», «setecientas doce»). En e01, e03 y e09 la cifra no lleva sustantivo, así que no hay problema.
5. Recuento de palabras: resuelto (1397 exactas).
6. Convención de la separación en grupos de tres: resuelto en e06 («Por convención…», «Con cuatro cifras no hace falta», 9000 sin hueco).
7. «Un poquito»: resuelto en e14. Ahora dice «ha empujado hacia arriba» y muestra +1, +50 y +500.
8. CM en la tarjeta de resumen: resuelto. e18 usa U-D-C-UM-DM-CM.

## Revisión conceptual de las escenas nuevas o cambiadas
- e09: la definición de «redondear a los millares» es correcta. 354 y 646 son correctos. La mitad, 99 500, es correcta.
- e10: el contraste millares frente a decenas de millar es correcto (9354 frente a 646). La escena deja la pregunta abierta, y e16 la cierra.
- e11: el caso del medio (99 500 a 500 de cada lado, se sube) está bien presentado como acuerdo.
- e12: la cifra que decide es correcta en las cuatro filas:
  - decenas: 4, queda 99 350;
  - centenas: 5, queda 99 400;
  - millares: 3, queda 99 000;
  - decenas de millar: 9, queda 100 000.
  La regla y su porqué son correctos.
- e13: 99 354 pasa a 100 000, 48 712 pasa a 50 000, la suma estimada es 150 000 y la exacta 148 066. La concordancia es correcta.
- e14 y e15: los rangos 99 500–100 499 (1000 números) y 95 000–104 999 (10 000 números) son correctos. Las dos mitades marcadas (99 500 y 100 500) son correctas. Los bordes «fuera» son correctos.
- e17: correcto. El rango 2950–3049 son 100 números, y la nota «redondeado a las centenas» queda fuera del cartel.
- e18: correcto.

## Fallo pendiente

**F1. e16, locución, línea 101: «Así que redondeó a las decenas de millar».** Es una conclusión que no se sigue.
- Problema: lo que se ha demostrado es que a los millares (y a las centenas o decenas) 99 354 no da 100 000. Eso deja abiertas todas las casillas mayores.
- A las centenas de millar, 99 354 también redondea a 100 000. La franja de «casi cien mil» sería entonces 50 000–99 999, y 99 354 estaría dentro. El propio guion muestra la columna CM en e05 y e18.
- Afirmar que redondeó a las decenas de millar es una afirmación falsa: es lo que más probablemente hizo, pero no es lo único posible. En un vídeo cuyo lema es «entender, no memorizar» se contradice con la lógica del problema inverso de e15 («depende de a qué se redondeó»).
- Corrección propuesta: «Así que no redondeó a los millares. Redondeó al menos a las decenas de millar», o «Así que tuvo que redondear a una casilla mayor, por ejemplo a las decenas de millar: quedan…». Después se mantiene el cálculo de la franja 95 000–99 999. Si se quiere más rigor, añadir que a las centenas de millar la franja sería aún más amplia.
- También en «Se ve» de e16: la expresión «el periódico redondeó a las decenas de millar» no aparece como tal, así que solo hay que revisar la locución. Opcional: cambiar «El periódico no mintió» por «El titular es compatible con el número», que es lo que se demuestra.

## Observaciones (no bloquean)
- e16: «las matemáticas te dan el margen máximo» es vago. Se podría decir «las matemáticas acotan el margen».
- e19: el adelanto 14 frente a 18 es correcto como teaser. Verificar en U1.2 que 18 = 3·(4 + 2) corresponde a otra cuenta, no a este ticket.
