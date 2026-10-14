---
description: Diseña el mapa de un curso nuevo (ejemplo /nuevo-curso FIS-1BACH o /nuevo-curso MAT-CALC1)
argument-hint: <MATERIA-CURSO del catálogo>
---
1. Comprueba que $ARGUMENTS existe en `curriculo/catalogo.yaml` (si no, propón cómo añadirlo y pide confirmación).
2. Agente `curriculista`: escribe `curso.json`, MAPA.md y `nexo/pendientes.md`.
3. Agente `pedagogo`: revisa el mapa entero (progresión, ejemplos, problemas inversos, papel de Nexo) en `curriculo/<materia>/<curso>/revision.md`.
4. Corrige con el curriculista lo imprescindible y **para a pedir aprobación humana del mapa** con un resumen: unidades, nº de vídeos, aplicaciones estrella, props/acciones nuevas que harán falta.
