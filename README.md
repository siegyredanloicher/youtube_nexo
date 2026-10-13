# Omnia: sistema de producción del canal

Qué es: un repositorio donde Claude Code produce los vídeos con agentes especializados. Tú apruebas el guion y el vídeo final.

## Puesta en marcha (una vez)
1. Instala Claude Code (app de escritorio o terminal) y Blender.
2. Sube esta carpeta a un repositorio privado de GitHub y ábrelo con Claude Code en tu PC.
3. Instala: `pip install sympy pillow numpy` y ffmpeg.
4. Añade fuentes en `brand/fonts/`, el modelo de Nexo en `nexo/` y elige voz en `pipeline/voz.md`.
5. Prueba con `python brand/brand.py` y `/episodio U1.1`.

## Estructura
- `CLAUDE.md` reglas del canal (las lee cada agente)
- `.claude/agents/` los 8 agentes; `.claude/commands/episodio.md` el director de orquesta
- `brand/` identidad visual (tokens, fuentes, logo)
- `nexo/` modelo, rig y biblioteca de clips
- `curriculo/` mapas por curso
- `plantillas/` y `episodios/` un directorio por vídeo
- `pipeline/` scripts compartidos (`verificar.py`)

## Pendiente de construir
`pipeline/render_nexo.py` (cuando llegue el modelo), `pipeline/componer.py` (ffmpeg), motor de voz, intro/cierre.

## Próximos pasos (en orden)
1. ~~Nombre, logo y carta~~ hechos (Omnia). Falta comprobar nombre en YouTube, dominio y marca, y revisar la carta con el modelo definitivo de Nexo.
2. Agente de revisión periódica del contenido (comprobar si algo debe actualizarse: currículo, datos, enlaces).
3. Modelo definitivo de Nexo y biblioteca de clips.
4. Voz de la locución y scripts de render y montaje.
5. Primer episodio de 1º ESO con `/episodio`.

Idea guía: conocimiento universal y accesible para todo el mundo.
