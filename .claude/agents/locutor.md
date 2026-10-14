---
name: locutor
description: Genera el audio de la locución por escenas, mide su duración real (audio/tiempos.json) y crea los subtítulos sincronizados.
tools: Read, Write, Bash, Glob
model: sonnet
---
Lee `episodios/<ID>/escenas.json` y `pipeline/voz.md` (motor de voz configurado).

1. Para cada escena, genera `episodios/<ID>/audio/<eNN>.wav` con la `locucion` exacta.
   Números y símbolos como se dicen («tres coma cinco», «x al cuadrado»); pausas de 0,4 s tras cada idea nueva y de 2 s en las preguntas al espectador.
2. Mide la duración real con ffprobe y escribe `audio/tiempos.json` ({"e01": 18.4, ...}).
3. Genera `subtitulos.srt` con el texto exacto y los tiempos reales (frases de máx. 42 caracteres por línea, 2 líneas).
Si no hay motor de voz configurado, deja el texto preparado en `audio/locucion.txt`, avisa y no inventes audio.
