"""Manim con la identidad de Omnia: fondo, fuentes, colores y componentes listos para usar.

    from omnia.m2d import *

    class E05Porcentaje(Escena):
        nivel = "eso"
        terminos = {"x": "mates.a", "60": "mates.b"}   # el mismo color en todo el vídeo

        def construct(self):
            t = self.titulo("El 20 % de 60")
            f = formula(r"0{,}20 \\cdot 60 = 12", self.terminos)
            self.play(Write(f))

Render (1080p, 30 fps):  manim -qh omnia_demo.py E05Porcentaje   (ver .claude/skills/manim-omnia)
Zonas: si Nexo ocupa un lado del plano, usa self.zona("izquierda") para colocar el contenido en el otro.
"""
from manim import *  # noqa: F401,F403  (las escenas importan todo desde aquí)
from manim import (DOWN, LEFT, ORIGIN, RIGHT, UP, Arrow, Code, Create, FadeIn, Line, ManimColor, MathTex,
                   NumberLine, Rectangle, RoundedRectangle, Scene, Square, SurroundingRectangle, TexTemplate, Text,
                   TransformMatchingTex, VGroup, Write, config, Axes, AnnularSector, Sector, Underline)
import manimpango

from .marca import C, ESCALA_PX, FUENTES, VIDEO, color, nivel_color  # noqa: F401

for _f in sorted(FUENTES.glob("*.ttf")):
    manimpango.register_font(str(_f))

config.background_color = color("fondo.base")
config.frame_rate = VIDEO["fps"]

TITULO, CUERPO, MONO = "Sora", "Manrope", "JetBrains Mono"
TINTA = ManimColor(color("tinta.principal"))
SUAVE = ManimColor(color("tinta.suave"))
SUPERFICIE = ManimColor(color("fondo.superficie"))
ALT = ManimColor(color("fondo.alt"))
MARGEN = 96 / 1080 * 8.0  # margen seguro de tokens.json, en unidades de Manim (≈0.71)
PX = 8.0 / 1080           # una unidad de pantalla a 1080p

PLANTILLA = TexTemplate()
PLANTILLA.add_to_preamble(r"\usepackage[T1]{fontenc}\usepackage{lmodern}\usepackage{amsmath}\usepackage{amssymb}")


def tam(estilo: str) -> float:
    """Tamaño de letra de Manim para un estilo de la escala tipográfica (titulo, subtitulo, cuerpo, formula, pie)."""
    return ESCALA_PX[estilo] * 0.62


def mc(ruta_o_hex: str) -> ManimColor:
    return ManimColor(ruta_o_hex if ruta_o_hex.startswith("#") else color(ruta_o_hex))


# ---------------------------------------------------------------- texto y fórmulas
def texto(s: str, estilo: str = "cuerpo", col=None, **kw) -> Text:
    fuente = TITULO if estilo in ("titulo", "subtitulo") else CUERPO
    peso = "SEMIBOLD" if estilo in ("titulo", "subtitulo") else "MEDIUM"
    return Text(s, font=fuente, weight=peso, font_size=tam(estilo), color=col or TINTA, **kw)


def formula(tex: str, terminos: dict | None = None, estilo: str = "formula", **kw) -> MathTex:
    """Fórmula LaTeX con cada término coloreado según el mapa del episodio ({'x': 'mates.a'})."""
    terminos = terminos or {}
    m = MathTex(tex, tex_template=PLANTILLA, color=TINTA, font_size=tam(estilo),
                substrings_to_isolate=list(terminos), **kw)
    for t, c in terminos.items():
        m.set_color_by_tex(t, mc(c))
    return m


def pasos(texs: list[str], terminos: dict | None = None) -> list[MathTex]:
    """Cadena de igualdades para animar con self.cadena(...): cada paso transforma el anterior."""
    return [formula(t, terminos) for t in texs]


# ---------------------------------------------------------------- piezas visuales
def panel(ancho: float, alto: float, col="fondo.superficie") -> RoundedRectangle:
    return RoundedRectangle(width=ancho, height=alto, corner_radius=0.18, fill_color=mc(col), fill_opacity=1,
                            stroke_color=ALT, stroke_width=2)


def resaltar(m, nivel: str = "eso", grosor: float = 5):
    return SurroundingRectangle(m, color=mc(nivel_color(nivel)), buff=0.14, corner_radius=0.12, stroke_width=grosor)


def subrayar(m, nivel: str = "eso"):
    return Underline(m, color=mc(nivel_color(nivel)), stroke_width=6, buff=0.08)


def nota(s: str, nivel: str = "eso") -> VGroup:
    """Etiqueta en un globo del color del nivel (para «¡ojo!», pistas, definiciones cortas)."""
    t = texto(s, "pie", col=mc(nivel_color(nivel, "texto")))
    fondo = RoundedRectangle(width=t.width + 0.5, height=t.height + 0.36, corner_radius=0.16,
                             fill_color=mc(nivel_color(nivel)), fill_opacity=0.28, stroke_width=0)
    return VGroup(fondo, t.move_to(fondo))


def recta_numerica(a: int, b: int, paso: int = 1, largo: float = 10, marcas: dict | None = None) -> VGroup:
    """Recta numérica; marcas = {valor: 'mates.a'} pinta puntos destacados."""
    r = NumberLine(x_range=[a, b, paso], length=largo, color=TINTA, include_numbers=True,
                   decimal_number_config={"color": TINTA, "num_decimal_places": 0}, font_size=tam("cuerpo") * 0.8,
                   stroke_width=3)
    g = VGroup(r)
    for v, c in (marcas or {}).items():
        from manim import Dot
        g.add(Dot(r.n2p(v), radius=0.11, color=mc(c)))
    return g


def ejes(x_range, y_range, largo_x: float = 9, largo_y: float = 5.5, etiquetas=("x", "y")) -> Axes:
    ax = Axes(x_range=x_range, y_range=y_range, x_length=largo_x, y_length=largo_y,
              axis_config={"color": TINTA, "stroke_width": 3, "include_tip": True,
                           "decimal_number_config": {"color": TINTA, "num_decimal_places": 0},
                           "font_size": tam("cuerpo") * 0.8},
              tips=True)
    ax.add_coordinates()
    ex = MathTex(etiquetas[0], tex_template=PLANTILLA, color=TINTA, font_size=tam("cuerpo")).next_to(ax.x_axis, RIGHT)
    ey = MathTex(etiquetas[1], tex_template=PLANTILLA, color=TINTA, font_size=tam("cuerpo")).next_to(ax.y_axis, UP)
    ax.add(ex, ey)
    return ax


def barra_porcentaje(pct: int, nivel: str = "eso", lado: float = 0.42) -> VGroup:
    """Cuadrícula 10x10: pct casillas pintadas del color del nivel. Ideal para porcentajes."""
    g = VGroup()
    for i in range(100):
        sq = Square(side_length=lado * 0.92, stroke_width=1.5, stroke_color=ALT,
                    fill_color=mc(nivel_color(nivel)) if i < pct else SUPERFICIE, fill_opacity=1)
        sq.move_to(((i % 10) * lado) * RIGHT + (-(i // 10) * lado) * UP)
        g.add(sq)
    return g.move_to(ORIGIN)


def sectores(n: int, k: int, radio: float = 2.0, col="mates.a") -> VGroup:
    """Círculo en n partes iguales con k pintadas (pizzas, fracciones, probabilidad)."""
    from manim import TAU
    g = VGroup()
    for i in range(n):
        s = Sector(radius=radio, angle=TAU / n, start_angle=TAU / 4 - (i + 1) * TAU / n,
                   fill_color=mc(col) if i < k else SUPERFICIE, fill_opacity=1, stroke_color=TINTA, stroke_width=3)
        g.add(s)
    return g


def tabla(filas: list[list[str]], encabezado: list[str] | None = None, ancho_col: float = 2.2) -> VGroup:
    """Tabla sencilla con la tipografía del canal; filas de texto o números."""
    todas = ([encabezado] if encabezado else []) + filas
    g = VGroup()
    alto = 0.7
    for r, fila in enumerate(todas):
        for c, val in enumerate(fila):
            celda = Rectangle(width=ancho_col, height=alto, stroke_color=ALT, stroke_width=2,
                              fill_color=ALT if (encabezado and r == 0) else SUPERFICIE, fill_opacity=1)
            celda.move_to(c * ancho_col * RIGHT + r * alto * DOWN)
            t = texto(str(val), "pie")
            g.add(VGroup(celda, t.move_to(celda)))
    return g.move_to(ORIGIN)


def codigo(fuente: str, lenguaje: str = "python") -> Code:
    """Bloque de código con la fuente del canal (JetBrains Mono), fondo superficie y números de línea."""
    return Code(code_string=fuente, language=lenguaje, formatter_style="friendly", background="window",
                background_config={"fill_color": SUPERFICIE, "stroke_color": ALT},
                paragraph_config={"font": MONO, "font_size": tam("pie")})


def flecha(a, b, col="tinta.principal") -> Arrow:
    return Arrow(a, b, color=mc(col), stroke_width=6, buff=0.15, max_tip_length_to_length_ratio=0.15)


# ---------------------------------------------------------------- escena base
class Escena(Scene):
    """Escena del canal. Atributos de clase: nivel ('eso'...), terminos ({'x': 'mates.a'}),
    zona_nexo (None | 'izquierda' | 'derecha'): deja libre esa franja para el plano de Nexo."""
    nivel = "eso"
    terminos: dict = {}
    zona_nexo: str | None = None

    def zona(self, nombre: str | None = None):
        """Centro y ancho útil de una zona del plano (respeta márgenes seguros)."""
        nombre = nombre or {"izquierda": "derecha", "derecha": "izquierda"}.get(self.zona_nexo, "completa")
        w = config.frame_width - 2 * MARGEN
        if nombre == "completa":
            return ORIGIN, w
        mitad = w * 0.58
        x = config.frame_width / 2 - MARGEN - mitad / 2
        return (x * (1 if nombre == "derecha" else -1)) * RIGHT, mitad

    def colocar(self, m, zona: str | None = None, y: float = 0.0):
        c, w = self.zona(zona)
        if m.width > w:
            m.scale_to_fit_width(w)
        return m.move_to(c + y * UP)

    def titulo(self, s: str, sub: str | None = None, animar: bool = True):
        t = texto(s, "titulo")
        g = VGroup(t)
        if sub:
            g.add(texto(sub, "subtitulo", col=SUAVE).next_to(t, DOWN, aligned_edge=LEFT, buff=0.15))
        c, w = self.zona()
        g.to_edge(UP, buff=MARGEN)
        g.set_x(c[0] - w / 2 + g.width / 2)
        if animar:
            self.play(Write(t), *[FadeIn(x, shift=0.2 * UP) for x in g[1:]], run_time=1.2)
        else:
            self.add(g)
        return g

    def cadena(self, texs: list[str], y: float = 0.0, pausa: float = 1.0):
        """Transforma una igualdad en la siguiente conservando los términos (y sus colores)."""
        ms = pasos(texs, self.terminos)
        for m in ms:
            self.colocar(m, y=y)
        self.play(Write(ms[0]))
        self.wait(pausa)
        for a, b in zip(ms, ms[1:]):
            self.play(TransformMatchingTex(a, b), run_time=1.2)
            self.wait(pausa)
        return ms[-1]
