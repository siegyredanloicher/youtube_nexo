"""Verifica claims.json: toda cifra, identidad, solución, unidad, fragmento de código o dato del guion.

Uso:  python pipeline/verificar.py episodios/MAT-1ESO-U6.3/claims.json
Sale con código 1 si algo falla. Esquema: pipeline/esquemas/claims.schema.json

Tipos de claim (campo "tipo"):
  numero     expr == esperado (exacto). Con "decimales": el guion redondea a esas cifras.
             {"expr": "0.20*60", "esperado": "12"}  ·  {"expr": "pi*20**2", "esperado": "1256.64", "decimales": 2}
  simbolico  identidad simbólica: derivadas, integrales, simplificaciones, límites.
             {"expr": "diff(x**3, x)", "esperado": "3*x**2"}
  ecuacion   las soluciones dadas son TODAS las soluciones en el dominio.
             {"ecuacion": "3*x - 4 = 11", "incognita": "x", "soluciones": ["5"], "dominio": "reales"}
  unidades   conversión o cálculo con unidades (pint).
             {"expr": "5 m * 3 m * 1.5 m", "esperado": "22500 L"}
  codigo     el fragmento se ejecuta y su salida coincide.
             {"lenguaje": "python", "codigo": "print(sum(range(4)))", "salida": "6"}
  dato       hecho del mundo real: solo pasa con "estado": "verificado" y una "fuente".
"""
import json
import subprocess
import sys
from pathlib import Path

import sympy as sp

ESQUEMA = Path(__file__).resolve().parent / "esquemas" / "claims.schema.json"
_UREG = None


def _sym(s):
    return sp.sympify(s.replace("^", "**"), rational=True)


def numero(c):
    a, b = sp.nsimplify(_sym(c["expr"])), sp.nsimplify(_sym(c["esperado"]))
    if "decimales" in c:
        d = c["decimales"]
        return round(float(a), d) == round(float(b), d), f"{sp.N(a, 12)} ≈ {b} ({d} decimales)"
    return sp.simplify(a - b) == 0, f"{a} = {b}"


def simbolico(c):
    a, b = _sym(c["expr"]), _sym(c["esperado"])
    a = a.doit() if hasattr(a, "doit") else a
    return sp.simplify(a - b) == 0, f"{sp.simplify(a)} = {b}"


def ecuacion(c):
    izq, der = c["ecuacion"].split("=")
    x = sp.Symbol(c["incognita"])
    dom = {"reales": sp.S.Reals, "enteros": sp.S.Integers, "naturales": sp.S.Naturals0,
           "complejos": sp.S.Complexes}[c.get("dominio", "reales")]
    sol = sp.solveset(sp.Eq(_sym(izq), _sym(der)), x, domain=dom)
    dadas = sp.FiniteSet(*[_sym(s) for s in c["soluciones"]])
    return sol == dadas, f"solveset = {sol}, guion = {dadas}"


def unidades(c):
    global _UREG
    import pint
    _UREG = _UREG or pint.UnitRegistry()
    a, b = _UREG(c["expr"]), _UREG(c["esperado"])
    try:
        a_b = a.to(b.units)
    except pint.DimensionalityError as e:
        return False, f"dimensiones distintas: {e}"
    ok = abs(a_b.magnitude - b.magnitude) <= 1e-9 * max(1.0, abs(b.magnitude))
    return ok, f"{a_b:~P} = {b:~P}"


def codigo(c):
    if c["lenguaje"] != "python":
        return False, "lenguaje no soportado todavía"
    r = subprocess.run([sys.executable, "-I", "-c", c["codigo"]], capture_output=True, text=True, timeout=20)
    salida = r.stdout.rstrip()
    ok = r.returncode == 0 and salida == c["salida"].rstrip()
    return ok, f"salida {salida!r}" + (f" error {r.stderr.strip()[-200:]}" if r.returncode else "")


def dato(c):
    ok = c.get("estado") == "verificado" and bool(c.get("fuente"))
    return ok, f"fuente: {c.get('fuente', '—')} ({c.get('estado')})"


TIPOS = dict(numero=numero, simbolico=simbolico, ecuacion=ecuacion, unidades=unidades, codigo=codigo, dato=dato)


def validar_esquema(claims):
    try:
        import jsonschema
    except ImportError:
        return []
    v = jsonschema.Draft202012Validator(json.loads(ESQUEMA.read_text(encoding="utf-8")))
    return [f"{'/'.join(map(str, e.path))}: {e.message}" for e in v.iter_errors(claims)]


def verificar(claims):
    """Devuelve lista de (claim, ok, detalle)."""
    res = []
    for c in claims:
        try:
            ok, det = TIPOS[c.get("tipo", "numero")](c)
        except Exception as e:  # una expresión mal escrita es un fallo, no un cuelgue
            ok, det = False, f"error: {e}"
        res.append((c, ok, det))
    return res


def main(ruta):
    claims = json.loads(Path(ruta).read_text(encoding="utf-8"))
    for c in claims:  # compatibilidad con el formato antiguo (sin tipo)
        c.setdefault("tipo", "numero")
        c.setdefault("nota", "")
    errores = validar_esquema(claims)
    if errores:
        print("ESQUEMA NO VÁLIDO:\n  " + "\n  ".join(errores))
        sys.exit(1)
    malos = []
    for c, ok, det in verificar(claims):
        print(("OK    " if ok else "FALLA ") + f"{c['id']:5s} {c['tipo']:9s} {det}   · {c.get('nota', '')}")
        if not ok:
            malos.append(c["id"])
    if malos:
        print("\nFALLAN:", ", ".join(malos))
        sys.exit(1)
    print(f"\nTodo verificado ({len(claims)} claims).")


if __name__ == "__main__":
    main(sys.argv[1])
