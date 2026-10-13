"""Genera el logotipo de Omnia (SVG y PNG) desde tokens.json.
Uso: python brand/logo/make_logo.py <ruta a sora-latin-700-normal.woff> [carpeta_salida]
El texto del logotipo se convierte a trazados, así el SVG no depende de ninguna fuente."""
import json, math, pathlib, sys
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

AQUI = pathlib.Path(__file__).parent
T = json.loads((AQUI.parent / "tokens.json").read_text(encoding="utf-8"))
C = T["color"]
NIVELES = [C["nivel"][k]["relleno"] for k in ("eso", "bachillerato", "universidad", "avanzado")]
INK, BASE, EMBLEMA = C["tinta"]["principal"], C["fondo"]["base"], C["nexo"]["emblema"]


def marca(size=512, fondo=INK, radio_tile=0.26):
    """Marca: anillo de 4 arcos (los 4 niveles) con el triángulo de Nexo en el centro."""
    s = size / 512
    r, w, gap = 150, 46, 26
    circ = 2 * math.pi * r
    dash = circ / 4 - w - gap
    arcos = "".join(
        f'<circle cx="256" cy="256" r="{r}" fill="none" stroke="{c}" stroke-width="{w}" stroke-linecap="round" '
        f'stroke-dasharray="{dash:.1f} {circ:.1f}" transform="rotate({90 * i - 90 + (gap + w) / 2 / r * 180 / math.pi:.2f} 256 256)"/>'
        for i, c in enumerate(NIVELES))
    tile = f'<rect width="512" height="512" rx="{512 * radio_tile:.0f}" fill="{fondo}"/>' if fondo else ""
    tri = (f'<path d="M256 196 L318 306 H194 Z" fill="{EMBLEMA}" stroke="{EMBLEMA}" stroke-width="14" stroke-linejoin="round"/>')
    return f'<g transform="scale({s})">{tile}{arcos}{tri}</g>'


def texto_a_trazado(font_path, texto, tam, x=0, y=0, tracking=0.0):
    f = TTFont(font_path)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    esc = tam / f["head"].unitsPerEm
    d, cur = [], 0.0
    for ch in texto:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (esc, 0, 0, -esc, x + cur, y)))
        d.append(pen.getCommands())
        cur += hmtx[g][0] * esc + tracking * tam
    return " ".join(d), cur


def svg(ancho, alto, cuerpo, fondo=None):
    bg = f'<rect width="{ancho}" height="{alto}" fill="{fondo}"/>' if fondo else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}">{bg}{cuerpo}</svg>')


def main(font, out):
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    # marca sola (con y sin tile)
    (out / "omnia_marca.svg").write_text(svg(512, 512, marca(512)), encoding="utf-8")
    (out / "omnia_marca_sin_fondo.svg").write_text(svg(512, 512, marca(512, fondo=None)), encoding="utf-8")
    # horizontal: marca + palabra
    d, ancho_txt = texto_a_trazado(font, "omnia", 150, x=0, y=0, tracking=-0.02)
    pad = 40
    H = 160
    cuerpo = (f'<g transform="translate({pad},{pad / 2 + 4})">{marca(H)}</g>'
              f'<g transform="translate({pad + H + 36},{pad / 2 + 4 + 118})"><path d="{d}" fill="{INK}"/></g>')
    W = int(pad + H + 36 + ancho_txt + pad)
    (out / "omnia_logo_horizontal.svg").write_text(svg(W, H + pad + 8, cuerpo), encoding="utf-8")
    (out / "omnia_logo_horizontal_fondo.svg").write_text(svg(W, H + pad + 8, cuerpo, fondo=BASE), encoding="utf-8")
    print("SVG generados en", out, "ancho horizontal", W)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else str(AQUI))
