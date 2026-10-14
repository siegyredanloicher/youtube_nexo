---
name: dirigir-nexo
description: Cómo poner a Nexo a actuar en un episodio (acciones, props, expresiones, cámara, planos JSON y render) y cómo ampliar su biblioteca de gestos y objetos. Úsala al escribir capas "nexo" de escenas.json, renderizar clips o crear props/acciones nuevos.
---

# Dirigir a Nexo

Nexo es el guía del canal: sin género, serio y cercano, nada infantil. **Participa** en los ejemplos (lanza la
pelota cuya parábola estudiamos, reparte la pizza, programa el robot). Nunca es decoración.

## Piezas
| Archivo | Qué es |
| --- | --- |
| `nexo/nexo3.py` → `nexo/nexo.blend` | el modelo con rig IK y expresiones (shape keys) |
| `nexo/props.py` | objetos reutilizables en su estilo (pelota, dado, pizarra, portátil, balanza, bloque, regla, puntero, coche, mesa, matraz, robot, vaso, libro) |
| `nexo/acciones.py` | gestos con parámetros (idle, saludar, senalar, pensar, sostener, mostrar, lanzar, celebrar, asentir, encoger, escribir, teclear, caminar) |
| `nexo/catalogo.json` | lista de props y acciones con sus parámetros y usos: **consúltala siempre** |
| `pipeline/render_nexo.py` | renderiza un plano JSON a PNG con alfa (y .mov ProRes 4444) |

## Un plano
Es la capa `{"tipo": "nexo", "plano": {...}}` de escenas.json (esquema en `pipeline/esquemas/escenas.schema.json`):
```json
{"accion": "lanzar",
 "params": {"prop": "p1", "v0": 4, "angulo": 50, "hacia": "derecha", "rebotes": 1},
 "props": [{"id": "p1", "prop": "pelota"}],
 "expresiones": [{"t": 2.4, "nombre": "Feliz"}],
 "camara": "completo", "encuadre": "izquierda", "duracion_s": 4}
```
- `params` de la acción: ver catálogo. Los props se citan por su `id` del plano.
- `props[].en`: `[x, y, z]` en metros para fijarlo en un sitio (Nexo está en el origen mirando a cámara, −Y; la derecha de la imagen es +X).
- `camara`: completo, tres_cuartos, lateral, picado, medio, primer_plano. La cámara se encuadra sola para que quepan Nexo y la trayectoria de los props.
- `encuadre`: izquierda/derecha deja a Nexo en ese tercio y libera el otro lado para la 2D (la escena 2D usa `zona_nexo` igual).
- `expresiones`: cambios extra sobre los de la acción. Nombres: Feliz, Tranquilo, Sorpresa, Pensativo, Concentrado, Curioso, Motivado, Entusiasmado, Parpadeo, Neutro.
- Si el plano dura más que la acción, Nexo respira en reposo el resto del tiempo.

## Render
```
python3 pipeline/render_nexo.py plano.json --salida episodios/<ID>/render/nexo/e05 --mov          # Eevee (PC con GPU)
python3 pipeline/render_nexo.py plano.json --salida /tmp/prueba --motor cycles --prueba            # sin GPU, rápido
python3 pipeline/render_nexo.py plano.json --salida /tmp/prueba --motor cycles --prueba --fotograma 20
```
El nivel (`--nivel eso|bach|uni|avanzado`) cambia el color del emblema y de props como la pelota.
12 fps por defecto (`video.fps_nexo` de tokens.json: estilo «animación a doses»); `"fps": 24` en el plano si hace falta más fluidez.
`plano_meta.json` guarda duración real y, al lanzar, `lanzamiento` (v0, ángulo, altura, tiempo de vuelo, alcance) para que la 2D dibuje la misma curva y el guion cite cifras verificables.

## Cuándo usar cada acción
- Gancho: `mostrar` un objeto curioso, `pensar`, `lanzar`.
- Explicación: `senalar` hacia la zona 2D, `escribir` en la pizarra (la pizarra es una pantalla: el editor incrusta la 2D en su superficie).
- Error común: `encoger` y luego `asentir` al corregirlo.
- Vida real: la acción que el ejemplo pide (lanzar, teclear, caminar por la recta numérica, sostener la balanza).
- Final: `celebrar` o `saludar`.

## Ampliar la biblioteca (agente constructor-props, comando /nuevo-prop)
- **Prop nuevo**: función en `nexo/props.py` con `@prop(agarre, descripcion, usos)`; origen = punto de agarre (o centro de la base). Estilo: formas suaves con bisel, materiales con `mat(nombre, token)`, colores solo de tokens. Escala real (Nexo mide 1,04 m). Luego `python3 nexo/props.py --catalogo`.
- **Acción nueva**: función en `nexo/acciones.py` con `@accion(descripcion, params, props, usos)`. Usa las utilidades de `Plano` (`ik`, `mirar`, `cuerpo`, `expr`, `en_mano`, `trayecto`, `relajado`). Si hay física, usa `omnia.fisica`. Luego `python3 nexo/acciones.py --catalogo`.
- Prueba siempre con `--prueba --fotograma N` en dos o tres momentos y mira las imágenes antes de dar el trabajo por bueno.
- Reutilizable antes que específico: «sostener» con cualquier prop es mejor que «sostener_pizza».
