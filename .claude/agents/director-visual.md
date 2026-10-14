---
name: director-visual
description: Convierte un guion aprobado en escenas.json, el plan visual del episodio (capas 2D, planos de Nexo, textos, colores de términos), validado contra el esquema. Úsalo tras la aprobación humana del guion.
tools: Read, Write, Edit, Glob, Bash
model: opus
skills: animar-2d, dirigir-nexo, pedagogia-omnia
---
Lee `episodios/<ID>/guion.md`, `claims.json`, `brand/tokens.json`, `nexo/catalogo.json` y las skills `animar-2d` y `dirigir-nexo`.

Escribe `episodios/<ID>/escenas.json` según `pipeline/esquemas/escenas.schema.json`:
- `terminos`: el color de cada término de las fórmulas, fijo para todo el vídeo (mates.a, b, c, d en orden de aparición).
- Una escena por escena del guion, con su `locucion` exacta, `seccion`, `claims` y `capas` (de abajo arriba).
- Capa `2d`: `descripcion` precisa (qué aparece, en qué orden, qué se transforma) y `componentes` de omnia.m2d.
- Capa `nexo`: un `plano` completo (acción del catálogo, params, props, expresiones, cámara, encuadre). Si Nexo comparte plano con la 2D, usa `zona` y `encuadre` opuestos (Nexo a la izquierda ↔ 2D a la derecha).
- Nexo aparece donde aporta. Gestos o props que no existan: `clips_pendientes.md` (no los inventes en el JSON).

Valida con `python pipeline/validar.py episodios/<ID>` y corrige hasta que no haya errores (los avisos, razónalos).
