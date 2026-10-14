"""e01 · vida_real: la gráfica altura-tiempo se dibuja al ritmo del vuelo de la pelota que lanza Nexo."""
import json
from pathlib import Path

from omnia.fisica import G
from omnia.m2d import *  # noqa: F403

META = Path(__file__).resolve().parent.parent / "render" / "nexo" / "e01" / "plano_meta.json"
L = json.loads(META.read_text())["lanzamiento"] if META.exists() else {"v0": 4, "angulo": 50, "h0": 0.58, "t_vuelo": 1.2}
T_SUELTA = 0.98  # instante en que Nexo suelta la pelota en el plano (acción lanzar)


class E01(Escena):
    nivel = "eso"
    terminos = {"t": "mates.a", "h": "mates.b"}
    zona_nexo = "izquierda"

    def construct(self):
        self.titulo("La gráfica cuenta el vuelo", animar=False)
        import math
        vy = L["v0"] * math.sin(math.radians(L["angulo"]))
        h = lambda t: max(0.0, L["h0"] + vy * t - 0.5 * G * t * t)  # noqa: E731
        ax = ejes([0, 1.6, 0.5], [0, 1.2, 0.5], largo_x=6, largo_y=3.8, etiquetas=("t\\,(s)", "h\\,(m)"))
        self.colocar(ax, y=-0.4)
        self.play(Create(ax), run_time=0.8)
        self.wait(max(0.0, T_SUELTA - 0.8))
        curva = ax.plot(h, x_range=[0, L["t_vuelo"]], color=mc("mates.b"), stroke_width=7)
        self.play(Create(curva), run_time=L["t_vuelo"], rate_func=linear)
        punto = Dot(ax.c2p(L["t_vuelo"], 0), color=mc("mates.a"), radius=0.1)
        self.play(FadeIn(punto, scale=1.5), run_time=0.3)
        self.wait(4.5 - T_SUELTA - L["t_vuelo"] - 0.3)
