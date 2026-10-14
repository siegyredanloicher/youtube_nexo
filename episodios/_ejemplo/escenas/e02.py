"""e02 · inverso: de la velocidad y el ángulo a la parte que hace subir la pelota."""
from omnia.m2d import *  # noqa: F403


class E02(Escena):
    nivel = "eso"
    terminos = {"v_y": "mates.b"}

    def construct(self):
        self.titulo("Al revés", "¿Qué parte de la velocidad la hace subir?")
        f = self.cadena([r"v_y = 4 \cdot \operatorname{sen} 50^\circ", r"v_y \approx 3{,}06\ \text{m/s}"], y=-0.6, pausa=0.6)
        self.play(Create(resaltar(f, self.nivel)), run_time=0.5)
        self.wait(0.6)
