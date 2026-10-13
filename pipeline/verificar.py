"""Verificación numérica con SymPy. Cada afirmación del guion se comprueba antes de producir.
Uso:  python verificar.py episodios/U6.3/claims.json
claims.json = lista de {"id": "...", "expr": "0.20*60", "esperado": "12", "nota": "20 % de 60"}"""
import json, sys
import sympy as sp


def comprobar(expr: str, esperado: str) -> bool:
    a = sp.nsimplify(sp.sympify(expr, rational=True))
    b = sp.nsimplify(sp.sympify(esperado, rational=True))
    return sp.simplify(a - b) == 0


def main(ruta):
    claims = json.load(open(ruta, encoding="utf-8"))
    malos = []
    for c in claims:
        try:
            ok = comprobar(c["expr"], c["esperado"])
        except Exception as e:  # expresión mal escrita = fallo
            ok = False
            c["error"] = str(e)
        print(("OK   " if ok else "FALLA"), c["id"], c["expr"], "=", c["esperado"], c.get("nota", ""))
        if not ok:
            malos.append(c["id"])
    if malos:
        print("\nFALLAN:", ", ".join(malos))
        sys.exit(1)
    print("\nTodo verificado.")


if __name__ == "__main__":
    main(sys.argv[1])
