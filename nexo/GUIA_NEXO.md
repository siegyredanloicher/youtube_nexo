# Nexo · guía técnica (Blender 5.x)

Compañero del canal: capucha crema con pico, pantalla facial negra con ojos luminosos, mochila navy.
Genérico en género, estilo 3D suave. Evoluciona por nivel (color de acento de la mochila/emblema):
ESO verde agua · Bachillerato azul · Universidad violeta · Avanzado coral.

## Archivos
- `build_nexo.py`  genera todo (cuerpo skin, capucha, ojos con shape keys, mochila, rig con IK, pesos). `python3 build_nexo.py -- bach`
- `nexo.blend`     modelo listo + animación `idle` (respira, mueve la cabeza, parpadea)
- `nexo.glb`       intercambio (rig + shape keys)

## Animar en Blender
- Rig `NexoRig`: controles IK `IK_hand.L/R`, `IK_foot.L/R`; poles `pole_elbow.*`, `pole_knee.*`; FK en `hips, spine, chest, neck, head`.
- Expresión: objeto `NexoEyeL` > Data > Shape Keys: Feliz, Tranquilo, Sorpresa, Pensativo, Concentrado, Curioso (0-1). El ojo derecho comparte la malla.
- Poses de ejemplo en `build_nexo.pose(N, "señala"|"lanza"|"piensa")`.
- Cámara/estudio: `studio()`; render Cycles CPU 40-48 muestras (~45 s por imagen 700x800).
