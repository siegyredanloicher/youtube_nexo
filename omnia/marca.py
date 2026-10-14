"""Identidad visual en código. Única puerta a brand/tokens.json para scripts y escenas.

    from omnia.marca import color
    color("mates.a")        -> "#1F6B9E"
    color("nivel.eso")      -> relleno del nivel ESO
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
_T = json.loads((RAIZ / "brand" / "tokens.json").read_text(encoding="utf-8"))
C = _T["color"]
F = _T["tipografia"]
VIDEO = _T["video"]
ESCALA_PX = _T["escala_tipografica_1080p"]
FUENTES = RAIZ / "brand" / "fonts"

NIVEL_TOKEN = {"eso": "eso", "bach": "bachillerato", "uni": "universidad", "avanzado": "avanzado"}


def color(ruta: str) -> str:
    """'mates.a', 'fondo.base', 'tinta.principal', 'nivel.eso', 'nivel.eso.texto', 'nexo.marino'..."""
    partes = ruta.split(".")
    if partes[0] == "nivel":
        n = C["nivel"][NIVEL_TOKEN.get(partes[1], partes[1])]
        return n[partes[2] if len(partes) > 2 else "relleno"]
    v = C
    for p in partes:
        v = v[p]
    if not isinstance(v, str):
        raise KeyError(f"{ruta} no es un color")
    return v


def nivel_color(nivel: str, uso: str = "relleno") -> str:
    return C["nivel"][NIVEL_TOKEN.get(nivel, nivel)][uso]
