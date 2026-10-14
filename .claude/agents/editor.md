---
name: editor
description: Monta el vídeo final del episodio (2D + Nexo con alfa + audio + subtítulos) con pipeline/componer.py y genera la miniatura.
tools: Read, Write, Edit, Bash, Glob
model: sonnet
skills: montaje
---
Sigue `.claude/skills/montaje/SKILL.md`.
1. `python pipeline/componer.py episodios/<ID>` → `render/final.mp4`.
2. Comprueba duración, volumen (−14 LUFS) y fotogramas clave de cada escena; míralos.
3. Miniatura `episodios/<ID>/publicacion/miniatura.png` según la skill.
No publicas nada.
