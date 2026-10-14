# Verificación · MAT-1ESO-U1.1 · Números grandes y aproximación

## Veredicto: RECHAZADO

No hay errores matemáticos. Se rechaza por fallos de notación y de redacción (corrección rápida) y por dudas menores de lógica. Tras corregirlos, el guion puede aprobarse.

## Automática
- `pipeline/verificar.py`: 61 claims originales OK.
- Barrido: se añaden c62 a c66 (cifra decisiva de 99 354, 3449 y 48 712; distancia de la estimación al total exacto, 1934; suma de duraciones de escena, 620 s). Resultado final: 66 de 66 claims OK.
- Sin cobertura posible en claims (no es un número verificable): el recuento de palabras de la cabecera (ver fallo 5).

## Revisión conceptual: correcto
- Valor posicional y tabla U–D–C–UM–DM–CM, con los valores 1 a 100 000.
- Descomposición de 99 354 (90 000 + 9000 + 300 + 50 + 4).
- Regla del 5: el caso del medio sube y la cifra decisiva es la siguiente (99 354 → 3 → 99 000; 48 712 → 8 → 50 000; 3449 → 4 → 3000).
- Rangos del problema inverso:
  - Al millar: 99 500–100 499, 1000 números.
  - A la decena de millar: 95 000–104 999, 10 000 números.
  - «Casi» como menor que 100 000: 95 000–99 999, y 99 354 está dentro.
  - A las centenas: 2950–3049, 100 números.
  - Los bordes «fuera» (99 499, 100 500, 94 999, 105 000, 2949, 3050) son correctos.
- Escena del redondeo en cadena (e13): 3449 → 3450 → 3500 → 4000 es correcto como cadena errónea. El correcto es 3000.
- Cifras dichas con letra frente a cifras en pantalla: coinciden en todos los casos revisados.
  - Revisados: 99 354, 48 712, 148 066, 30 405, 3405, 3449, 2950, 3049, 95 000, 104 999, 99 500, 100 499.
  - La concordancia de género («trescientos» frente a «trescientas») es un asunto aparte, en el fallo 4.
- Suma de duraciones: 620 s, coincide con la cabecera.

## Fallos

1. **Notación de la multiplicación (e05 «Se ve» y e17 «Se ve»).**
   - Problema: las flechas «× 10» usan `×`. `materias/referencias/matematicas.md` pide `·` en ESO y evita `×` salvo en tablas de multiplicar.
   - Corrección propuesta: rotular «· 10» (o «por 10») en ambas escenas.

2. **Espacio fino (todo el guion y la cabecera).**
   - Problema: la cabecera declara espacio fino como separador de miles. El archivo usa un espacio ASCII normal en las cifras de 5 o más dígitos (99 354, 100 000…). Un espacio normal permite saltos de línea dentro de la cifra y no es el espacio fino declarado.
   - Corrección propuesta: usar U+202F (espacio fino sin separación) en guion y escenas, o aclarar en la cabecera que el guion usa espacio normal y que el render aplica el fino. Las cifras de 4 dígitos sin separador sí cumplen la norma.

3. **Separador en la cabecera.**
   - Problema: la línea 3 escribe «1.339 palabras». Un número de 4 cifras va sin separador en castellano (la norma del propio guion).
   - Corrección propuesta: «1339 palabras».

4. **Concordancia (e12, locución).**
   - Problema: «noventa y nueve mil trescientos cincuenta y cuatro personas» y «cuarenta y ocho mil setecientas doce» son inconsistentes entre sí. Delante de «personas» (femenino) lo normativo es «trescientas cincuenta y cuatro» y «setecientas doce».
   - Corrección propuesta: «noventa y nueve mil trescientas cincuenta y cuatro personas». Opcional: reformular («entraron 99 354 personas») para evitar el problema. Las cifras en pantalla no cambian.

5. **Recuento de palabras (cabecera, línea 3).**
   - Problema: la cabecera dice 1.339 palabras. El recuento real de la locución (sin las pausas) es 1342. Es una discrepancia pequeña, pero un dato de cabecera debe ser exacto.
   - Corrección propuesta: «1342 palabras» o «≈ 1340».

6. **Lógica de «por eso» (e06, locución).**
   - Problema: «Y por eso escribimos un pequeño espacio cada tres cifras». Agrupar de tres en tres no se deduce de la tabla de posiciones: es una convención ligada a los nombres de millar y millón. Además, la locución dice «cada tres cifras» sin avisar de que los números de 4 cifras (9000, 3449…) van sin espacio. Eso es lo que verá el alumno en pantalla, y puede parecerle una incoherencia.
   - Corrección propuesta: presentarlo como convención («por convención…»). Añadir una frase del estilo: «Con cuatro cifras no hace falta».

7. **Redondeo en cadena (e13, locución).**
   - Problema: «cada paso ha empujado un poquito hacia arriba». Los empujones son +1, +50 y +500, es decir, crecientes. «Un poquito» y «se acumulan» es una simplificación aceptable, pero el último paso no es pequeño.
   - Corrección propuesta: decir «cada paso ha empujado hacia arriba» y quitar «un poquito». Opcional: mostrar +1, +50 y +500 en pantalla.

8. **Tabla en la tarjeta de resumen (e17, «Se ve»).**
   - Problema: la tabla se describe como «U-D-C-UM-DM» y omite CM, que sí aparece en e05 y en el 100 000 de la tarjeta 2.
   - Corrección propuesta: «U-D-C-UM-DM-CM».

## Observaciones (no bloquean)
- e14 y e16 solo consideran un nivel de redondeo cada vez. El texto lo dice («depende otra vez de a qué se redondeó»), así que es correcto.
- El adelanto de e18 (14 frente a 18) es correcto como teaser. Queda para U1.2 explicar que 18 = 3·(4 + 2) no corresponde al ticket. Conviene verificarlo entonces.
- Los claims c04 a c06 y c54 son poco informativos, pero verdaderos.
