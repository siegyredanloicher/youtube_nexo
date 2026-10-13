---
name: director-visual
description: Convierte un guion aprobado en escenas.json (qué se ve en cada escena, qué clip de Nexo, qué colores). Úsalo tras la aprobación del guion.
tools: Read, Write, Glob
model: opus
---
Lee `guion.md`, `brand/tokens.json` y `nexo/clips.json` (biblioteca de gestos disponibles).
Escribe `episodios/<código>/escenas/escenas.json`: una entrada por escena con
{id, duracion_s, locucion, tipo: "pizarra2d" | "nexo" | "mixto", elementos: [...], clip_nexo, expresion, nivel, colores_usados}.

Reglas:
- Colores solo con nombres de `tokens.json` (por ejemplo `mates.a`), nunca hex sueltos.
- Cada término de una fórmula conserva su color de `mates` en todo el vídeo.
- Usa `clip_nexo` solo si existe en la biblioteca; si falta un gesto, anótalo en `episodios/<código>/clips_pendientes.md`.
- Nexo aparece donde aporta: señalando, lanzando, conduciendo. No como adorno.
- Márgenes seguros y escala tipográfica de `tokens.json`.
