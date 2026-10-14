---
description: Renderiza un plano de Nexo a partir de una descripción (ejemplo /plano Nexo lanza el dado y celebra)
argument-hint: <descripción del plano>
---
1. Traduce "$ARGUMENTS" a un plano JSON (esquema en `pipeline/esquemas/escenas.schema.json`, `$defs.plano`) usando solo acciones y props de `nexo/catalogo.json`. Si algo no existe, dilo y propone /nuevo-prop.
2. Render de prueba: `python3 pipeline/render_nexo.py plano.json --salida render_pruebas/<nombre> --prueba` (sin GPU: `--motor cycles`).
3. Enseña 2-3 fotogramas y el JSON; si la persona lo aprueba, render final con `--mov`.
