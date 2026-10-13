"""Genera avatar, banner y favicon de Omnia en PNG a partir de los SVG y tokens.json.
Uso: python brand/logo/render_assets.py <carpeta con node_modules (fontsource + katex)> [salida]
Requiere playwright."""
import json, pathlib, sys
from playwright.sync_api import sync_playwright

AQUI = pathlib.Path(__file__).parent
T = json.loads((AQUI.parent / "tokens.json").read_text(encoding="utf-8"))
C = T["color"]; N = T["canal"]
NIV = [C["nivel"][k]["relleno"] for k in ("eso", "bachillerato", "universidad", "avanzado")]
nm = pathlib.Path(sys.argv[1]).resolve() / "node_modules"
out = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else AQUI
out.mkdir(parents=True, exist_ok=True)
marca = (AQUI / "omnia_marca_sin_fondo.svg").read_text(encoding="utf-8")
logo = (AQUI / "omnia_logo_horizontal.svg").read_text(encoding="utf-8")

FONTS = f"""
@font-face{{font-family:Manrope;font-weight:500;src:url(file://{nm}/@fontsource/manrope/files/manrope-latin-500-normal.woff2)}}
@font-face{{font-family:Sora;font-weight:600;src:url(file://{nm}/@fontsource/sora/files/sora-latin-600-normal.woff2)}}"""

avatar = f"""<style>body{{margin:0}}.a{{width:800px;height:800px;background:{C['tinta']['principal']};display:grid;place-items:center}}.a svg{{width:560px;height:560px}}</style>
<div class="a">{marca}</div>"""

anillos = "".join(
    f'<circle cx="0" cy="0" r="430" fill="none" stroke="{c}" stroke-width="120" stroke-linecap="round" opacity=".16" '
    f'stroke-dasharray="{3.1416*430/2-120-60:.0f} 9999" transform="rotate({90*i-90+8})"/>' for i, c in enumerate(NIV))
banner = f"""<style>{FONTS}
body{{margin:0}}.b{{width:2560px;height:1440px;background:{C['fondo']['base']};position:relative;overflow:hidden;font-family:Manrope}}
.ring{{position:absolute;opacity:1}}
.l{{position:absolute;left:50%;top:50%;transform:translate(-50%,-56%);text-align:center}}
.l svg{{height:250px;width:auto;display:block;margin:0 auto}}
.d{{margin-top:26px;font-size:44px;color:{C['tinta']['suave']};letter-spacing:.01em}}
.d b{{font-family:Sora;font-weight:600;color:{C['tinta']['principal']}}}
.f{{position:absolute;color:rgba(28,42,71,.11);font-size:76px;white-space:nowrap}}
</style><div class="b">
<svg class="ring" style="left:-560px;top:360px" width="1200" height="1200" viewBox="-600 -600 1200 1200">{anillos}</svg>
<svg class="ring" style="right:-560px;top:-540px" width="1200" height="1200" viewBox="-600 -600 1200 1200" transform="rotate(180)">{anillos}</svg>

<div class="l">{logo}<div class="d"><b>{N['descriptor']['es']}</b> &nbsp;·&nbsp; {N['descriptor']['en']}</div></div>
</div>
"""

with sync_playwright() as pw:
    b = pw.chromium.launch()
    for nombre, html, w, h in [("omnia_avatar.png", avatar, 800, 800), ("omnia_banner_youtube.png", banner, 2560, 1440)]:
        tmp = out / f"_{nombre}.html"; tmp.write_text("<meta charset=utf-8>" + html, encoding="utf-8")
        pg = b.new_page(viewport={"width": w, "height": h}); pg.goto("file://" + str(tmp.resolve())); pg.wait_for_timeout(1500)
        pg.screenshot(path=str(out / nombre)); pg.close(); tmp.unlink()
    b.close()
print("PNG generados en", out)
