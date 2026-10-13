---
description: Produce un episodio completo a partir de su código del mapa (ejemplo /episodio U6.3)
argument-hint: <código del mapa, ejemplo U6.3>
---
Produce el episodio $ARGUMENTS siguiendo `CLAUDE.md`.

1. Crea `episodios/$ARGUMENTS/` copiando `episodios/_plantilla/`.
2. Agente `guionista`: escribe `guion.md` y `claims.json`.
3. Agente `verificador-matematico`: debe dar APROBADO. Si da RECHAZADO, devuelve al guionista (máximo 3 vueltas).
4. **PARA aquí y pide aprobación humana del guion.** No sigas sin un sí explícito.
5. Agente `director-visual`: genera `escenas.json`.
6. En paralelo: `animador-2d`, `animador-nexo` y `locutor`.
7. Agente `editor`: monta el vídeo.
8. Agente `revisor`: debe dar APROBADO.
9. **PARA y pide aprobación humana del vídeo final.** La subida a YouTube la hace una persona.

Al terminar, resume en 5 líneas: qué se hizo, qué cifras se verificaron y qué queda pendiente.
