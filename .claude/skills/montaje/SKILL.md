---
name: montaje
description: Cómo montar el vídeo final de un episodio (2D + planos de Nexo con alfa + audio + subtítulos) con pipeline/componer.py y ffmpeg, y cómo comprobar el resultado. Úsala en el editor y en el revisor.
---

# Montaje

## Entrada (en `episodios/<ID>/`)
- `escenas.json` (validado con `pipeline/validar.py`).
- `render/2d/<eNN>.mp4`: una escena 2D por id (Manim).
- `render/nexo/<eNN>/####.png` o `<eNN>.mov`: planos de Nexo con alfa.
- `audio/<eNN>.wav` y `audio/tiempos.json` (duración real de cada escena); `subtitulos.srt`.

## Componer
```
python pipeline/componer.py episodios/<ID>            # vídeo final: render/final.mp4
python pipeline/componer.py episodios/<ID> --escena e05   # solo una escena (para revisar)
python pipeline/componer.py episodios/<ID> --borrador     # sin audio: duración estimada, 720p
```
Por cada escena: fondo de tokens → capa 2D → capa de Nexo en su `zona` (izquierda/derecha/centro/esquina) → texto. La duración es la del audio (o `duracion_s` si aún no hay audio). Las escenas se unen con un fundido corto.

## Reglas
- 1920×1080, 30 fps, H.264 (CRF 18), audio AAC 192 kbps normalizado a −14 LUFS (`loudnorm`).
- Nunca fondo negro: si falta una capa, se usa `fondo.base`.
- Los planos de Nexo se renderizan a 30 fps, como el vídeo; si un plano usa otros fps, `componer.py` lo convierte.
- Subtítulos: archivo .srt aparte (YouTube) y quemados solo si se pide.
- Miniatura `miniatura.png` (1280×720): fondo crema, título en Sora (máx. 4 palabras), Nexo expresivo con un prop del episodio (fotograma de un plano con `--fotograma`).

## Comprobar
- `ffprobe` de duración y pistas; `ffmpeg -i final.mp4 -af ebur128 -f null -` para el volumen.
- Fotogramas de inicio, mitad y final de cada escena (`ffmpeg -ss T -frames:v 1`) y **mirarlos**.
