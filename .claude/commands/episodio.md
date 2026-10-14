---
description: Produce un episodio completo a partir de su ID del currículo (ejemplo /episodio MAT-1ESO-U6.3)
argument-hint: <ID del vídeo, ejemplo MAT-1ESO-U6.3>
---
Produce el episodio $ARGUMENTS siguiendo `CLAUDE.md`. Carpeta: `episodios/$ARGUMENTS/` (crea copiando `episodios/_plantilla/`).
Si el argumento es solo un curso (MAT-1ESO), elige el siguiente con `python pipeline/curriculo.py siguiente MAT-1ESO` y confírmalo con la persona.

**Fase 1 · Guion**
1. Agente `guionista`: `guion.md` + `claims.json`.
2. En paralelo, agentes `verificador` y `pedagogo`. Si alguno no aprueba, vuelve al guionista con ambos informes (máximo 3 vueltas; si no converge, para y explica por qué).
3. **PARA y pide aprobación humana del guion.** Muestra: resumen en 5 líneas, duración estimada, qué hace Nexo y los puntos discutibles. No sigas sin un sí explícito. Luego `python pipeline/curriculo.py estado $ARGUMENTS aprobado`.

**Fase 2 · Producción**
4. Agente `director-visual`: `escenas.json` validado con `pipeline/validar.py`.
5. Si hay `clips_pendientes.md`: agente `constructor-props` primero.
6. En paralelo: `animador-2d`, `animador-nexo` y `locutor`. (`animador-nexo` y el render final necesitan el PC con gráfica; si esta sesión no la tiene, renderiza con `--motor cycles` o deja preparado y avisa.)
7. Agente `editor`: `render/final.mp4` y miniatura.
8. Agente `revisor`: debe dar APROBADO; si no, devuelve cada fallo a quien corresponda.
9. Agentes `adaptador-en` (versión inglesa) y `publicador` (paquete de subida).
10. **PARA y pide aprobación humana del vídeo final.** La subida la hace una persona.

Al terminar, resume en 5 líneas: qué se hizo, cifras verificadas, qué queda pendiente.
