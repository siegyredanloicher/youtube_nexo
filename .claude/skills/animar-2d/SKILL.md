---
name: animar-2d
description: Cómo crear las escenas 2D de Omnia con Manim y la librería omnia.m2d (fórmulas coloreadas, gráficas, geometría, código, diagramas), dejando sitio a Nexo. Úsala al implementar o revisar capas "2d" de escenas.json.
---

# Escenas 2D con Manim + omnia.m2d

## Entorno
- Manim Community (≥ 0.19), LaTeX (texlive con lmodern) y ffmpeg. Instalación: `pip install -r requirements.txt` (más los paquetes de sistema del README).
- Siempre desde la raíz del repo con `PYTHONPATH=.`:
  `PYTHONPATH=. manim -qh episodios/<ID>/escenas/e03.py E03 --media_dir episodios/<ID>/render/2d`
  Prueba rápida: `-ql`; fotograma final: `-s`.
- Catálogo visual de componentes: `omnia/demos/demo_2d.py` (Catalogo, Porcentaje).

## Reglas
- Importa todo de `omnia.m2d` (`from omnia.m2d import *`). Nunca colores hex ni fuentes sueltas: `mc("mates.a")`, `texto(..., "titulo")`.
- Hereda de `Escena` y fija: `nivel`, `terminos` (el mapa del episodio de escenas.json, idéntico en todas las escenas) y `zona_nexo` si la capa de Nexo ocupa un lado.
- Coloca el contenido con `self.colocar(m, y=...)` y `self.titulo(...)`: respetan márgenes seguros y la zona libre.
- Una clase por escena, con nombre `E03` (id de escena en mayúscula). Un archivo por escena en `episodios/<ID>/escenas/`.
- La duración la marca el audio: termina con `self.wait(...)` hasta la duración de `audio/tiempos.json` si existe (o la estimada).
- Números: los de `claims.json`, nunca recalculados a mano. Coma decimal en castellano: escribe `0{,}25` en LaTeX y "0,25" en texto.
- Física compartida con Nexo: `from omnia.fisica import trayectoria` para dibujar la misma parábola que la pelota del plano 3D (lee `render/nexo/<escena>/plano_meta.json` → `lanzamiento`).

## Componentes de omnia.m2d
| Componente | Para |
| --- | --- |
| `titulo(s, sub)` (método de Escena) | rótulo de escena arriba |
| `texto(s, estilo)` | cuerpo, pie, subtitulo |
| `formula(tex, terminos)` | ecuaciones con términos coloreados |
| `self.cadena([tex1, tex2, ...])` | transformar una igualdad paso a paso (TransformMatchingTex) |
| `ejes(xr, yr)` + `ax.plot(f)` | funciones y datos |
| `recta_numerica(a, b, marcas={v: color})` | enteros, decimales, intervalos |
| `barra_porcentaje(pct)` | porcentajes (10×10) |
| `sectores(n, k)` | fracciones, probabilidad |
| `tabla(filas, encabezado)` | proporcionalidad, frecuencias |
| `codigo(src, lenguaje)` | programación (JetBrains Mono) |
| `nota(s)` | «¡Ojo!», pistas, definiciones |
| `resaltar(m)`, `subrayar(m)`, `flecha(a, b)` | dirigir la mirada |
| `panel(w, h)` | tarjeta de fondo para agrupar |

Si necesitas algo que se repetirá en otros vídeos, **añádelo a `omnia/m2d.py`** (con su ejemplo en `demos/`), no lo copies en el episodio.

## Patrones visuales por idea
- **Fórmula que se descubre**: primero el caso numérico, luego los números se transforman en letras con `TransformMatchingTex` conservando colores.
- **Igualdad / ecuación**: balanza (Nexo en 3D) + cadena de igualdades en 2D con la operación aplicada a ambos lados resaltada.
- **Función**: tabla → puntos que aparecen en los ejes → curva que los une. Un punto móvil (`ValueTracker`) conecta x e y.
- **Geometría**: cortar y recolocar piezas (`Transform` de polígonos) en lugar de enunciar la fórmula.
- **Probabilidad**: experimento repetido con un contador y una barra de frecuencias que se estabiliza.
- **Código**: el código aparece línea a línea; una flecha recorre la ejecución y una tabla muestra las variables.
- **Física**: vector velocidad sobre la trayectoria; descomposición en componentes con colores mates.a / mates.b.

## Ritmo
- Algo cambia en pantalla cada 3-6 s.
- Aparición: `Write` para fórmulas, `FadeIn(shift=UP*0.2)` para texto, `Create` para trazos. 0,6-1,2 s por animación.
- Máximo 3 elementos nuevos a la vez; lo que ya no hace falta, se va (`FadeOut`).
