# Matemáticas

## Notación
- Multiplicación: `·` (punto centrado) en ESO; se evita `×` salvo en tablas de multiplicar. Nunca `*` en pantalla.
- División: fracción o `:`; en ESO, `÷` solo si el libro de texto lo usa.
- Decimales con coma: en LaTeX `0{,}25`. Intervalos con corchetes: `[a, b)`. Conjuntos ℕ, ℤ, ℚ, ℝ.
- Funciones: `f(x)`, dominio/recorrido; en Bachillerato y universidad `f: A → B`.
- Ángulos en grados en ESO; radianes desde 1º Bachillerato (se dice siempre la unidad).

## Metáforas visuales que funcionan
- Fracciones: pizza, barra de chocolate, vasos medidores (props `vaso`, 2D `sectores`).
- Enteros: ascensor, termómetro, recta numérica por la que camina Nexo (`caminar`).
- Ecuaciones: balanza (prop `balanza` con `inclinacion`).
- Proporcionalidad: recetas que escalan, tablas de doble entrada.
- Funciones: un taxi (prop `coche`) cuyo precio crece con los km; punto que recorre la gráfica.
- Áreas: cortar y recolocar; baldosas (`bloque`).
- Probabilidad: dado lanzado muchas veces (`lanzar` con `dado`) y frecuencias que se estabilizan.
- Cálculo: pendiente como velocidad del coche; integral como área que se llena; límite como zoom.
- Álgebra lineal: matrices como transformaciones del plano (rejilla que se deforma).

## Errores frecuentes que conviene desactivar
- (a + b)² = a² + b² · −3² = 9 · dividir entre 0 · 0,1 + 0,2 en ordenador.
- Confundir porcentaje de subida y bajada (subir 10 % y bajar 10 % no deja igual).
- «Una ecuación de 2º grado siempre tiene dos soluciones».
- Media como «valor típico» con valores extremos.
- Derivada = pendiente de la secante; confundir límite con valor de la función.

## Verificación
Todo pasa por `pipeline/verificar.py`: `numero`, `simbolico` (derivadas, integrales, límites, simplificaciones), `ecuacion` (todas las soluciones, con dominio).

## Progresión
ESO: intuición y cálculo con sentido · Bachillerato: análisis (límites, derivadas, integrales), geometría analítica, probabilidad · Universidad: cálculo riguroso, álgebra lineal, EDO, probabilidad y estadística · Avanzado: análisis real, topología, optimización.
