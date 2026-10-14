# Nexo · guía técnica (Blender 5.x)

Nexo es el compañero del canal. Lleva capucha crema con un pico blando hacia atrás, una pantalla facial negra con forma de escudo redondeado y ojos luminosos, y una mochila marino. No tiene género y su estilo es 3D suave, de felpa.

Evoluciona por nivel con el color del emblema de la mochila: ESO verde agua · Bachillerato azul · Universidad violeta · Avanzado coral.

## Archivos
- `nexo3.py`: genera el modelo definitivo (v3) desde cero. Los colores salen de `brand/tokens.json`.
  - `python3 nexo/nexo3.py -- bach`: crea `nexo.blend` y `nexo.glb`.
  - `python3 nexo/nexo3.py -- eso --render`: además, guarda renders de revisión en `nexo/renders/`.
- `nexo.blend`: modelo listo con la animación `idle` (respira, mueve la cabeza y parpadea).
- `nexo.glb`: versión de intercambio con rig y shape keys (morph targets).
- `modelo_provisional/`, `build_nexo.py`, `nexo2.py`: versión anterior (v2), solo como referencia.

## Medidas
- Mide unos 1,04 m. La capucha ocupa casi la mitad de la altura. Mira hacia −Y y tiene Z hacia arriba.
- La cara es una superelipse (`FACE_A`, `FACE_B`, `FACE_N` en `nexo3.py`), más ancha que alta y algo más estrecha abajo. Sobresale un poco del reborde.

## Animar en Blender
- **Rig `NexoRig`:**
  - Controles IK: `IK_hand.L/R` e `IK_foot.L/R`.
  - Polos: `pole_elbow.*` y `pole_knee.*`. Su ángulo se calibra solo para que la pose de reposo no cambie.
  - FK: `hips`, `spine`, `chest`, `neck` y `head`.
- **Expresiones:** se controlan en el objeto `NexoEyeL`, en Data > Shape Keys (valores de 0 a 1).
  - Disponibles: Feliz, Tranquilo, Sorpresa, Pensativo, Concentrado, Curioso, Motivado, Entusiasmado y Parpadeo.
  - El ojo derecho comparte la malla, en espejo.
  - Las pupilas (`NexoPupil*`) se encienden solas con Sorpresa y Curioso, mediante un driver.
  - Las estrellas (`NexoStar*`) se encienden solas con Entusiasmado.
  - Para hacer un fundido entre expresiones, baja una y sube otra.
- **Desde código:** `expr(N, "Curioso")`, `pose(N, "señala" | "lanza" | "piensa" | "saluda")` e `idle(N)`.
- **Brillo de los ojos:** el halo lo pone el compositor (Glare tipo Bloom), así que funciona igual en Eevee y en Cycles. Para más o menos halo, cambia `Strength` en el grupo «Composicion».
- **Estudio:** `studio()` y `set_camera(cam, az, el, dist, tz)`. Un render en Cycles por CPU con 40 muestras tarda unos 45 s por imagen de 800x900.
