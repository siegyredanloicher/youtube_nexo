# Canal educativo de matemáticas (ESO → Bachillerato → Universidad)

Misión: educación accesible para cualquiera con conexión a internet. Entender, no memorizar.
Primero 1º ESO completo (ver `curriculo/MAPA_1ESO.md`), luego 2º, 3º, 4º y Bachillerato.

## Reglas que no se rompen
1. **Pedagogía.** Todo vídeo explica de dónde sale la idea, la aplica a la vida real y la resuelve también al revés (problema inverso).
2. **Nexo** es el guía: sin género, serio y profesional, nada infantil. Interactúa en los ejemplos (lanza una pelota, conduce un coche). Su nivel de color sigue el curso.
3. **Identidad visual.** Colores y fuentes salen solo de `brand/tokens.json` (usa `brand/brand.py`). Nunca fondo negro.
4. **Cifras verificadas.** Todo número que aparece en un guion pasa por `pipeline/verificar.py` (SymPy) antes de producir. Si falla, se corrige el guion.
5. **Dos puntos de revisión humana:** (a) aprobar el guion, (b) aprobar el vídeo final antes de subir. Los agentes nunca publican.
6. **Idioma:** castellano, tuteo, tono cercano pero riguroso. Sin muletillas.
7. **Estructura de un episodio** en `episodios/<código>/` (ver `plantillas/`). El código viene del mapa (ejemplo: U6.3).

## Flujo (`/episodio U6.3`)
guionista → verificador-matematico → [aprobación humana] → director-visual → animador-2d + animador-nexo + locutor (en paralelo) → editor → revisor → [aprobación humana] → subida manual.

## Dónde corre cada cosa
- Texto, guiones, verificación, escenas 2D: en cualquier sitio.
- Clips de Nexo (Blender + Eevee) y montaje final (ffmpeg): en el PC con tarjeta gráfica.
