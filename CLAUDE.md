# Omnia: canal educativo de ciencia y tecnología (ESO → Bachillerato → Universidad → Avanzado)
Canal bilingüe (castellano e inglés). Conocimiento universal y accesible para todo el mundo.
Misión: educación accesible para cualquiera con conexión a internet. **Entender, no memorizar.**
Empezamos por Matemáticas de 1º ESO y crecemos a física, química, programación, robótica e IA, hasta nivel universitario.

## Reglas que no se rompen
1. **Pedagogía.** Todo vídeo explica de dónde sale la idea, la aplica a la vida real y la resuelve también al revés (problema inverso). Método completo: skill `pedagogia-omnia`.
2. **Nexo** es el guía: sin género, serio y profesional, nada infantil. **Participa** en los ejemplos (lanza, mide, reparte, programa). Su color de nivel sigue el curso.
3. **Identidad visual.** Colores y fuentes salen solo de `brand/tokens.json` (en código: `omnia.marca`). Nunca fondo negro.
4. **Todo verificado.** Toda cifra, fórmula, unidad, fragmento de código o dato de un guion está en `claims.json` y pasa `pipeline/verificar.py`. Si falla, se corrige el guion. Nada se inventa.
5. **Dos puntos de revisión humana:** (a) aprobar el guion, (b) aprobar el vídeo final. Los agentes nunca publican.
6. **Idioma:** castellano, tuteo, tono cercano pero riguroso. Sin muletillas. La versión inglesa se adapta, no se traduce literal.
7. **Reutilizar antes que repetir.** Lo que sirva para más de un vídeo va a la librería (`omnia/`, `nexo/props.py`, `nexo/acciones.py`), no al episodio.

## Mapa del repo
| Ruta | Qué hay |
| --- | --- |
| `curriculo/catalogo.yaml` | materias, cursos, nivel de Nexo y estado |
| `curriculo/<materia>/<curso>/curso.json` | fichas de vídeo (fuente de verdad); MAPA.md se genera |
| `episodios/<ID>/` | un vídeo: guion, claims, escenas, render, audio, publicación (plantilla en `_plantilla/`) |
| `omnia/` | librería Python: `marca` (tokens), `m2d` (Manim con la marca), `fisica` (compartida 2D/3D) |
| `nexo/` | modelo (`nexo3.py` → `nexo.blend`), `props.py`, `acciones.py`, `catalogo.json` |
| `pipeline/` | `curriculo.py`, `verificar.py`, `validar.py`, `render_nexo.py`, `componer.py`, esquemas JSON |
| `brand/` | tokens, fuentes, logotipo |
| `.claude/agents/` | 13 agentes · `.claude/skills/` conocimiento · `.claude/commands/` flujos |
| `docs/ARQUITECTURA.md` | cómo encaja todo y cómo ampliarlo |

ID de vídeo: `<MATERIA>-<CURSO>-<código>`, por ejemplo `MAT-1ESO-U6.3`. Ficha: `python pipeline/curriculo.py ficha MAT-1ESO-U6.3`.

## Flujo de un episodio (`/episodio MAT-1ESO-U6.3`)
guionista → verificador + pedagogo → **[aprobación humana del guion]** → director-visual → (constructor-props si falta algo)
→ animador-2d + animador-nexo + locutor → editor → revisor → adaptador-en + publicador → **[aprobación humana del vídeo]** → subida manual.

Otros comandos: `/nuevo-curso FIS-1BACH`, `/nuevo-prop <qué>`, `/plano <descripción>`, `/estado`.

## Dónde corre cada cosa
- Texto, guiones, verificación, currículo, escenas 2D (Manim) y montaje (ffmpeg): en cualquier sitio con las dependencias de `requirements.txt`.
- Planos de Nexo: Blender 5.x. Eevee en el PC con tarjeta gráfica (por defecto); `--motor cycles` funciona sin GPU (más lento).
