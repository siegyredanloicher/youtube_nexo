---
name: verificar-contenido
description: Cómo comprobar que un guion es correcto (cifras, símbolos, unidades, código, datos y rigor conceptual) en matemáticas, física, química, programación y robótica. Úsala al verificar o revisar cualquier contenido antes de producir.
---

# Verificar contenido

Un error publicado destruye la confianza en el canal. Se verifica **todo** antes de producir.

## 1. Verificación automática
```
python pipeline/verificar.py episodios/<ID>/claims.json
```
| tipo | Qué comprueba | Ejemplo |
| --- | --- | --- |
| numero | igualdad exacta (o con `decimales`) | 20 % de 60 = 12 |
| simbolico | identidades, derivadas, integrales, límites (SymPy) | d/dx x³ = 3x² |
| ecuacion | que las soluciones dadas son TODAS en el dominio | x² = 4 → {−2, 2} |
| unidades | conversiones y magnitudes (pint) | 5·3·1,5 m³ = 22 500 L |
| codigo | ejecuta Python y compara la salida | mcd(48, 18) → 6 |
| dato | exige fuente y estado verificado | récord 100 m: 9,58 s |

Si un claim no encaja en ningún tipo, se reformula hasta que encaje o se convierte en `dato` con fuente.

## 2. Barrido del guion
Busca en `guion.md` toda cifra, fórmula y afirmación técnica que **no** esté en claims.json (también en «Se ve» y en los ejemplos de código). Añádela y vuelve a ejecutar.

## 3. Revisión conceptual (a mano)
- Definiciones correctas **para el nivel**: simplificar está bien; afirmar algo falso, no. Una simplificación se señala en el guion.
- Sin saltos de lógica: cada paso se sigue del anterior.
- Signos, unidades y cifras significativas coherentes.
- El problema inverso tiene solución única, o el guion dice cuántas hay.
- Condiciones de validez explícitas: «sin rozamiento», «si la población es grande», «para n ≥ 1».
- Notación según `.claude/skills/materias/` (coma decimal en castellano, etc.).

### Por materia
- **Matemáticas**: dominios, divisiones por cero, raíces (±), redondeos frente a valores exactos.
- **Física**: unidades SI y análisis dimensional; g = 9,81 m/s² salvo que se diga otra cosa; modelo frente a realidad.
- **Química**: ajuste de reacciones (conservación de masa y carga), estados, seguridad en los experimentos.
- **Programación**: el código se ejecuta tal como aparece en pantalla; versión del lenguaje; casos límite.
- **Robótica**: unidades de sensores, sistemas de referencia (y la convención de signos), límites físicos de motores.

## 4. Informe
`episodios/<ID>/verificacion.md` con **APROBADO** o **RECHAZADO**, y para cada fallo: escena, línea del guion, qué está mal y la corrección propuesta. El verificador **no reescribe** el guion.
