# Omnia: sistema de producción del canal

Repositorio donde Claude Code produce vídeos educativos con agentes especializados, de 1º ESO a universidad.
Tú apruebas el guion y el vídeo final; todo lo demás está automatizado y verificado.

## Puesta en marcha (una vez, en el PC con gráfica)
1. Instala Claude Code, Blender 5.x, ffmpeg y LaTeX (`texlive-latex-extra`, `dvisvgm`; en Windows, MiKTeX).
2. `pip install -r requirements.txt` (si Manim da guerra, mira la documentación de Manim Community para tu sistema).
3. Comprueba que todo responde:
   ```
   python pipeline/curriculo.py validar
   python pipeline/verificar.py pipeline/tests/claims_ejemplo.json
   PYTHONPATH=. manim -ql -s omnia/demos/demo_2d.py Catalogo
   python pipeline/render_nexo.py pipeline/tests/plano_lanzar.json --salida render_pruebas/lanzar --prueba --fotograma 20
   ```
4. Elige motor de voz en `pipeline/voz.md`.

## Uso diario
- `/estado` — cursos, vídeos por estado y siguiente vídeo recomendado.
- `/episodio MAT-1ESO-U6.3` — produce un episodio de principio a fin (para dos veces a pedir tu aprobación).
- `/nuevo-curso FIS-1BACH` — diseña el mapa de un curso nuevo.
- `/nuevo-prop un telescopio` — amplía lo que Nexo tiene o sabe hacer.
- `/plano Nexo lanza el dado y celebra` — renderiza un plano suelto de Nexo.

## Cómo está hecho
Lee `CLAUDE.md` (reglas y mapa) y `docs/ARQUITECTURA.md` (capas, contratos de datos y cómo escalar).
