---
name: disenar-curso
description: Cómo diseñar el mapa de un curso nuevo (curso.json con sus fichas de vídeo) para cualquier materia y nivel, de ESO a universidad. Úsala con /nuevo-curso o cuando haya que ampliar, reordenar o revisar un mapa.
---

# Diseñar un curso

Un curso es `curriculo/<carpeta-materia>/<curso>/curso.json`. Ejemplo completo: `curriculo/matematicas/1eso/curso.json` (50 vídeos).
El catálogo (`curriculo/catalogo.yaml`) dice qué cursos existen, su nivel de Nexo y su estado.

## Pasos
1. **Fuentes.** ESO y Bachillerato: currículo LOMLOE (Real Decreto 217/2022 para ESO y 243/2022 para Bachillerato, más el decreto autonómico si aplica). Universidad: guías docentes de varias universidades españolas y un libro de referencia clásico. Anota las fuentes en el campo `fuentes`.
2. **Unidades.** Agrupa los saberes en unidades de 2-5 vídeos. Cada unidad tiene una aplicación «estrella» del mundo real.
3. **Fichas.** Un vídeo = una idea central que cabe en la duración del nivel. Campos obligatorios:
   `codigo` (U4.2), `id` (MAT-2ESO-U4.2), `unidad`, `titulo`, `idea_clave` (de dónde sale, en 1-2 frases),
   `vida_real` (ejemplo con números), `nexo` (qué hace Nexo: debe ser una acción del catálogo o una nueva justificada),
   `problema_inverso`, `requisitos` (códigos del mismo curso; de otros cursos con el ID completo), `estado: "pendiente"`.
4. **Requisitos sin ciclos** y en orden de emisión. `python pipeline/curriculo.py validar`.
5. **Series transversales** (códigos T1.1…) para lo que cruza unidades: finanzas, pensamiento computacional, historia de la ciencia.
6. **Mapa legible.** `python pipeline/curriculo.py mapa <CURSO>` genera MAPA.md. Cambia el estado del curso a `mapa` en el catálogo.

## Criterios de calidad de un mapa
- Cada ficha responde «¿para qué sirve esto?» con un ejemplo que un estudiante de esa edad reconoce.
- La ilustración con Nexo es una acción física (lanzar, medir, repartir, programar), no «Nexo explica».
- Los problemas inversos son de verdad inversos (de la respuesta a los datos); si no aportan, el campo se deja vacío.
- Ejemplos del mundo del espectador según su edad (1º-2º ESO: móviles, vídeos, videojuegos, deporte, clase, compras pequeñas).
- Progresión: lo que se usa en un vídeo se ha visto antes (requisitos).
- Lista de props y acciones de Nexo que el curso necesita y aún no existen → `nexo/pendientes.md` (los construye `constructor-props`).

## Universidad y avanzado
- Más rigor: cada ficha incluye además `resultado` (teorema o resultado central) y `demostracion` (sí / esquema / no).
- Duración 12-20 min; se permiten series de 2-3 vídeos para un mismo resultado largo.
- Referencias bibliográficas en `fuentes` del curso.
