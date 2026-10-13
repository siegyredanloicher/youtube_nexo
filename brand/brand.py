"""Acceso único a la identidad visual. Uso: from brand import C, F, rgb, linear, nivel"""
import json, pathlib

_T = json.loads((pathlib.Path(__file__).parent / "tokens.json").read_text(encoding="utf-8"))
C = _T["color"]
F = _T["tipografia"]
VIDEO = _T["video"]
ESCALA = _T["escala_tipografica_1080p"]


def rgb(hexa: str):
    """'#1C2A47' -> (28, 42, 71)"""
    h = hexa.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def linear(hexa: str):
    """Hex sRGB -> RGBA lineal 0-1 (para materiales de Blender)."""
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (f(v / 255) for v in rgb(hexa))
    return (r, g, b, 1.0)


def nivel(nombre: str):
    """nivel('eso') -> {'relleno': ..., 'texto': ..., 'nombre': ...}"""
    return C["nivel"][nombre]


def contraste(a: str, b: str) -> float:
    def lum(h):
        f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        r, g, bl = (f(v / 255) for v in rgb(h))
        return 0.2126 * r + 0.7152 * g + 0.0722 * bl
    x, y = sorted((lum(a), lum(b)), reverse=True)
    return (x + 0.05) / (y + 0.05)


if __name__ == "__main__":
    base = C["fondo"]["base"]
    for n, v in C["nivel"].items():
        print(f"{n:13s} texto {contraste(v['texto'], base):.2f}  relleno {contraste(v['relleno'], base):.2f}")
    for k, v in C["mates"].items():
        if k != "_uso":
            print(f"mates.{k} {contraste(v, base):.2f}")
    print("tinta", round(contraste(C["tinta"]["principal"], base), 2))
