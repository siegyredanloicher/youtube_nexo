# Robótica

## Convenciones
- Sistemas de referencia dibujados (ejes del robot y del mundo) y unidades SI (rad/s, m/s, N·m).
- Sensores con su rango y su ruido; actuadores con sus límites.

## Metáforas visuales
- Prop `robot`: robot móvil con dos ruedas, sensor y antena. Nexo lo programa con `teclear` y luego el robot se mueve.
- Bucle sentir → pensar → actuar como un ciclo que se repite.
- Control: termostato y ducha (abrir el grifo demasiado y pasarse = sobreoscilación).
- Cinemática: brazo articulado como una cadena de ángulos (el propio rig de Nexo con IK es un ejemplo).

## Errores frecuentes
- Creer que un sensor mide sin error.
- Olvidar el retardo entre medir y actuar.
- Confundir velocidad de rueda y velocidad del robot (radio de la rueda).

## Verificación
`unidades` (velocidad de rueda = ω·r), `codigo` para la lógica de control, `simbolico` para la cinemática.
