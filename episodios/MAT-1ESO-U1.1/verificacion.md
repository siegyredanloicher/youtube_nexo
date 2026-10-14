# Verificación · MAT-1ESO-U1.1 · Números grandes y aproximación · TERCERA VUELTA

## Veredicto: APROBADO

## Comprobaciones
- `pipeline/verificar.py`: 75 de 75 claims OK, con c66 = 670 s.
- Cabecera: la suma de duraciones de escena es 670 s y la locución tiene 1395 palabras sin pausas. Ambas cifras coinciden con la cabecera.
- Fallo F1 de la segunda vuelta (e16): resuelto. Ahora dice «tuvo que redondear a una casilla más grande. Si fue a las decenas de millar, quedan desde 95 000 hasta 99 999». Ya no afirma una casilla única. Es compatible con las centenas de millar. El cálculo de la franja es correcto y 99 354 está dentro.
- «Las matemáticas acotan el margen»: correcto.
- «El periódico no mintió»: se acepta. Es verdad para cualquier casilla mayor que los millares, porque 99 354 cabe en «casi 100 000» tanto a las decenas como a las centenas de millar. La justificación está en `cambios.md`.
- e14 a 55 s y la frase quitada de e04: no afectan al contenido matemático.

Sin fallos pendientes. Los 8 de la primera vuelta y el F1 de la segunda están resueltos.
