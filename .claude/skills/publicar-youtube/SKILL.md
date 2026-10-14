---
name: publicar-youtube
description: Cómo preparar los metadatos de YouTube de un episodio (títulos, descripción con capítulos, etiquetas, miniatura, versión inglesa) sin publicar nada. Úsala cuando un vídeo esté aprobado y haya que dejar listo el paquete de subida.
---

# Paquete de publicación

Los agentes **nunca publican**: dejan `episodios/<ID>/publicacion/` listo para que una persona suba el vídeo.

## Archivos
- `es.md` y `en.md`: título, descripción, capítulos, etiquetas.
- `miniatura.png` (1280×720, < 2 MB).
- `subtitulos.es.srt`, `subtitulos.en.srt`.

## Título
- Máx. 60 caracteres, la pregunta o el resultado que engancha + el tema: «¿Por qué −·− da +? | Números enteros».
- Sin mayúsculas gritonas ni clickbait que el vídeo no cumpla.

## Descripción
1. Dos líneas que resumen lo que se aprende (aparecen antes de «más»).
2. Capítulos con marcas de tiempo desde 0:00 (uno por sección del guion; mínimo 3, de al menos 10 s), sacados de `audio/tiempos.json`.
3. Requisitos (vídeos anteriores, con enlace cuando existan) y siguiente vídeo.
4. Curso y nivel: «Matemáticas · 1º ESO · Unidad 6».
5. Fuentes de los datos del mundo real (las de `claims.json`).
6. Lema del canal y nada más: sin listas de hashtags.

## Etiquetas
10-15: tema, curso, «matemáticas 1 ESO», conceptos clave y sinónimos de búsqueda en el idioma del vídeo.

## Versión inglesa
La prepara `adaptador-en` (guion adaptado y audio propio). Comparte miniatura salvo el texto.
