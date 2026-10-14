---
name: constructor-props
description: Amplía la biblioteca de Nexo con props 3D y acciones nuevas reutilizables (Blender/bpy), en su estilo y probados con render. Úsalo con /nuevo-prop o cuando haya clips_pendientes.md o nexo/pendientes.md.
tools: Read, Write, Edit, Bash, Glob
model: opus
skills: dirigir-nexo
---
Sigue la sección «Ampliar la biblioteca» de `.claude/skills/dirigir-nexo/SKILL.md`.
1. Antes de crear, busca en `nexo/catalogo.json` si algo existente (con parámetros) resuelve la necesidad.
2. Props en `nexo/props.py`, acciones en `nexo/acciones.py`; regenera el catálogo (`--catalogo`).
3. Prueba con un plano mínimo: `python3 pipeline/render_nexo.py plano.json --salida /tmp/x --motor cycles --prueba --fotograma N` en varios momentos y **mira las imágenes**.
4. Diseña para reutilizar: parámetros (tamaño, color de nivel, estado) mejor que variantes copiadas.
5. Marca como hecho lo que resuelvas en `clips_pendientes.md` / `nexo/pendientes.md`.
