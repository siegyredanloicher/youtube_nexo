---
name: escribir-guion
description: Formato y técnica para escribir el guion de un episodio de Omnia (guion.md + claims.json). Úsala al escribir o corregir un guion, en cualquier materia o nivel, en castellano o inglés.
---

# Escribir un guion de Omnia

Entrada: la ficha del vídeo (`python pipeline/curriculo.py ficha <ID>`) y la skill `pedagogia-omnia`.
Salida, en `episodios/<ID>/`:
- `guion.md` con la estructura de `episodios/_plantilla/guion.md`.
- `claims.json`: toda cifra, identidad, solución, unidad, fragmento de código o dato del mundo real.

## Escribir para el oído
- Frases de 8 a 15 palabras. Una idea por frase. Voz activa.
- Tú, presente, sin muletillas («básicamente», «vale», «pues»).
- Los números se escriben como se leen en la locución cuando haya ambigüedad: «tres coma cinco», «diez elevado a seis». En pantalla, con notación normal (coma decimal en castellano, punto en inglés).
- Las fórmulas no se leen símbolo a símbolo: se dice lo que significan («el área es la base por la altura»).
- 150 palabras por minuto de locución. Un vídeo de 10 min tiene unas 1.500 palabras.

## Cada escena del guion
```
## e03 · origen · 45 s
- Locución: (texto exacto que se dirá)
- Se ve: (qué aparece, en qué orden, qué se resalta)
- Nexo: acción (de nexo/catalogo.json) + expresión, o «no aparece»
- Claims: c04, c05
```
- El `id` (e01, e02…) y la `seccion` son los de `pipeline/esquemas/escenas.schema.json`: gancho, problema, origen, regla, ejemplo, vida_real, inverso, error_comun, demostracion, codigo, practica, resumen, siguiente.
- «Se ve» describe lo visual con verbos: «aparece la barra de 100 casillas; se pintan 20 en el color del nivel».
- Nexo actúa solo cuando aporta (lanza la pelota cuyo vuelo se estudia, reparte la pizza…). Consulta el catálogo: `nexo/catalogo.json`. Si falta un gesto o un prop, escríbelo en «Nexo» igualmente y añádelo a `clips_pendientes.md`.

## claims.json
Formato y tipos en `pipeline/verificar.py` (numero, simbolico, ecuacion, unidades, codigo, dato). Reglas:
- Una entrada por cada cifra que se dice o se ve, también las intermedias.
- `nota` cuenta qué afirma el guion con palabras; `escena` dice dónde aparece.
- Redondeos: `"decimales": 2` si el guion dice 1.256,64.
- Datos del mundo real (récords, precios, fechas): `tipo: dato` con `fuente` comprobable. Si no la tienes, `estado: a_verificar` y el verificador lo marcará: no se inventa nada.
- Código que aparece en pantalla: `tipo: codigo` con la salida exacta.

## Bilingüe
Se escribe primero en castellano. La versión inglesa la hace `adaptador-en`: adapta (no traduce literalmente) ejemplos, unidades y notación.

## Antes de entregar
- [ ] Están las cinco piezas obligatorias (gancho, de dónde sale, vida real, inverso, resumen).
- [ ] Hay al menos un error común tratado.
- [ ] Duración estimada dentro del rango del curso (palabras / 150).
- [ ] Cada número de la locución y de «Se ve» está en claims.json.
- [ ] Ninguna escena introduce dos conceptos nuevos.
