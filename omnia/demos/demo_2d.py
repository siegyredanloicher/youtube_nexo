"""Escenas de muestra de la librería (sirven de prueba y de catálogo visual).
Render: manim -ql omnia/demos/demo_2d.py Porcentaje   (desde la raíz del repo, con PYTHONPATH=.)"""
from omnia.m2d import *  # noqa: F403


class Porcentaje(Escena):
    nivel = "eso"
    terminos = {"20": "mates.a", "60": "mates.b", "12": "mates.c"}
    zona_nexo = "izquierda"

    def construct(self):
        self.titulo("El 20 % de 60", "Un porcentaje es una fracción de 100")
        barra = self.colocar(barra_porcentaje(20, self.nivel), y=-0.4).scale(0.9)
        self.play(FadeIn(barra, lag_ratio=0.01), run_time=1.5)
        self.play(barra.animate.scale(0.6).shift(UP * 0.2 + RIGHT * 2.2))
        f = self.cadena([r"20\,\%\ \text{de}\ 60", r"\frac{20}{100} \cdot 60", r"0{,}20 \cdot 60 = 12"], y=-2.2, pausa=0.4)
        self.play(Create(resaltar(f, self.nivel)))
        self.wait(0.5)


class Catalogo(Escena):
    nivel = "bach"
    terminos = {"x": "mates.a"}

    def construct(self):
        self.titulo("Componentes", "omnia.m2d", animar=False)
        ax = ejes([-3, 3, 1], [-1, 9, 2], largo_x=5, largo_y=3.6).to_edge(LEFT, buff=0.9).shift(DOWN * 0.9)
        curva = ax.plot(lambda x: x ** 2, color=mc("mates.a"), stroke_width=6)
        pie = sectores(8, 3, 1.2).shift(RIGHT * 0.8 + UP * 0.6)
        rn = recta_numerica(-5, 5, 1, largo=6, marcas={-2: "mates.b", 3: "mates.a"}).shift(RIGHT * 2.6 + DOWN * 2.4)
        cod = codigo("def mcd(a, b):\n    while b:\n        a, b = b, a % b\n    return a").scale(0.8).shift(RIGHT * 4.6 + UP * 0.6)
        n = nota("¡Ojo! 0,1 + 0,2 ≠ 0,3 en un ordenador", self.nivel).shift(DOWN * 1.3 + RIGHT * 3.6)
        f = formula(r"f(x) = x^2", self.terminos).move_to(ax.c2p(-1.6, 7.5))
        self.add(ax, curva, pie, rn, cod, n, f)
        self.wait(0.1)
