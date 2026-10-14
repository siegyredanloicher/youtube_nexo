# Arquitectura de Omnia

Un sistema para producir vídeos educativos de calidad con agentes, desde 1º ESO hasta nivel universitario y en varias materias.
La idea central: **los agentes escriben datos; el código los convierte en vídeo.** Así cada pieza se puede validar, repetir y mejorar sin rehacer el resto.

## Capas

```
curriculo/            QUÉ enseñar      catálogo de materias y cursos → curso.json con fichas de vídeo
.claude/skills/       CÓMO enseñar     pedagogía, guion, verificación, 2D, Nexo, materias, montaje, publicación
.claude/agents/       QUIÉN lo hace    13 agentes especializados
episodios/<ID>/       EL VÍDEO         guion.md, claims.json, escenas.json, render/, audio/, publicacion/
pipeline/             LAS MÁQUINAS     verificar, validar, render_nexo, componer, curriculo (+ esquemas JSON)
omnia/ · nexo/        LAS LIBRERÍAS    2D con la marca, física compartida, Nexo con props y acciones
brand/                LA IDENTIDAD     tokens.json (colores, fuentes, escala), fuentes OFL, logotipo
```

## Contratos de datos (lo que se pasan los agentes)
| Archivo | Lo escribe | Lo valida | Lo usan |
| --- | --- | --- | --- |
| `curso.json` | curriculista | `curriculo.py validar` | guionista, /episodio |
| `guion.md` | guionista | verificador, pedagogo, persona | director-visual |
| `claims.json` | guionista | `verificar.py` + esquema | verificador, animador-2d, revisor, publicador |
| `escenas.json` | director-visual | `validar.py` + esquema | animadores, locutor, editor |
| plano de Nexo (dentro de escenas.json) | director-visual | esquema + catálogo | `render_nexo.py` |
| `audio/tiempos.json` | locutor | — | editor, publicador |

Los esquemas viven en `pipeline/esquemas/`. Cambiar un formato = cambiar el esquema + la skill que lo explica + el código que lo lee, en el mismo commit.

## Episodio: estructura de carpeta
```
episodios/MAT-1ESO-U6.3/
  guion.md  claims.json  verificacion.md  revision_pedagogica.md  escenas.json  clips_pendientes.md
  escenas/e03.py ...            código Manim de cada escena 2D
  render/2d/e03.mp4 ...         escenas 2D
  ####.png      planos de Nexo (alfa) y e05.json (el plano)
  audio/e01.wav ... tiempos.json  subtitulos.srt
  render/final.mp4  revision.md
  en/                           versión inglesa (guion, claims, escenas, audio)
  publicacion/                  es.md, en.md, miniatura.png, subtítulos
```
Las carpetas `render/` y `audio/` no se suben a git (ver `.gitignore`); se regeneran.

## Nexo como actor
- **Modelo**: `nexo/nexo3.py` genera `nexo.blend` (rig con IK, 9 expresiones por shape keys).
- **Props** (`nexo/props.py`): objetos procedurales en su estilo, con punto de agarre y parámetros (nivel, tamaño, estado).
- **Acciones** (`nexo/acciones.py`): gestos parametrizados sobre el rig (señalar, lanzar con física real, escribir, teclear, caminar…).
- **Catálogo** (`nexo/catalogo.json`): lo que existe. El director visual solo usa lo que está aquí; lo que falta va a `clips_pendientes.md` y lo construye `constructor-props`.
- **Render** (`pipeline/render_nexo.py`): plano JSON → PNG con alfa / .mov ProRes 4444, con cámara que se encuadra sola.
- **Física compartida** (`omnia/fisica.py`): la pelota que lanza Nexo y la parábola que dibuja Manim salen de las mismas ecuaciones.

## Escalar a nuevas materias y niveles
1. Añade la materia y sus cursos a `curriculo/catalogo.yaml`.
2. Escribe su referencia en `.claude/skills/materias/referencias/<materia>.md` (notación, metáforas, errores, verificación).
3. `/nuevo-curso <MATERIA-CURSO>`: el curriculista diseña el mapa y lista los props/acciones que faltan.
4. `/nuevo-prop` para cada objeto o gesto nuevo (telescopio, osciloscopio, brazo robótico…).
5. Si la materia necesita un tipo de verificación nuevo (p. ej., ajustar reacciones químicas), añádelo a `pipeline/verificar.py` y al esquema de claims.
6. Componentes 2D nuevos (circuitos, moléculas, grafos) → `omnia/m2d.py` con su demo.

## Pendiente
- Motor de voz (`pipeline/voz.md`): elegir uno con buena voz en castellano e inglés y licencia comercial.
- Intro y cierre del canal (5 s cada uno) en `brand/`.
- Escenarios 3D reutilizables para Nexo (aula, laboratorio, calle) además del fondo transparente.
