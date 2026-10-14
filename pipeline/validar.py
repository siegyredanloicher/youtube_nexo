"""Valida un episodio antes de producirlo: escenas.json contra su esquema y contra lo que existe de verdad.

Uso:  python pipeline/validar.py episodios/MAT-1ESO-U6.3
Comprueba:
  - escenas.json cumple pipeline/esquemas/escenas.schema.json
  - ids de escena únicos y en orden; cada claim citado existe en claims.json
  - cada acción y prop de Nexo existe en nexo/catalogo.json; las expresiones existen
  - duración total estimada por palabras (≈150 palabras/min) dentro de la duración del curso
  - hay problema inverso y ejemplo de vida real (reglas del canal)
Sale con código 1 si hay errores; los avisos no bloquean.
"""
import json
import re
import sys
from pathlib import Path

import jsonschema

RAIZ = Path(__file__).resolve().parent.parent
PALABRAS_MIN = 150


def cargar(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def validar(ep):
    ep = Path(ep)
    errores, avisos = [], []
    esc = cargar(ep / "escenas.json")
    v = jsonschema.Draft202012Validator(cargar(RAIZ / "pipeline/esquemas/escenas.schema.json"))
    errores += [f"esquema {'/'.join(map(str, e.path))}: {e.message}" for e in v.iter_errors(esc)]
    if errores:
        return errores, avisos

    ids = [e["id"] for e in esc["escenas"]]
    if len(ids) != len(set(ids)):
        errores.append("ids de escena repetidos")
    claims = {c["id"] for c in cargar(ep / "claims.json")} if (ep / "claims.json").exists() else set()
    cat = cargar(RAIZ / "nexo/catalogo.json")
    acciones, props = set(cat["acciones"]), set(cat["props"])
    secciones = {e["seccion"] for e in esc["escenas"]}
    for falta in ("inverso", "vida_real"):
        if falta not in secciones:
            errores.append(f"no hay ninguna escena de tipo '{falta}' (regla del canal)")

    palabras = 0
    for e in esc["escenas"]:
        palabras += len(re.findall(r"\w+", e["locucion"]))
        for c in e.get("claims", []):
            if c not in claims:
                errores.append(f"{e['id']}: cita {c}, que no está en claims.json")
        if re.search(r"\d", e["locucion"]) and not e.get("claims"):
            avisos.append(f"{e['id']}: la locución tiene cifras pero no cita ningún claim")
        for capa in e["capas"]:
            if capa["tipo"] != "nexo":
                continue
            pl = capa["plano"]
            if pl["accion"] not in acciones:
                errores.append(f"{e['id']}: acción de Nexo '{pl['accion']}' no existe (nexo/catalogo.json); "
                               "anótala en clips_pendientes.md")
            for p in pl.get("props", []):
                if p["prop"] not in props:
                    errores.append(f"{e['id']}: prop '{p['prop']}' no existe; pídelo con /nuevo-prop")
        if not any(c["tipo"] in ("2d", "nexo", "media") for c in e["capas"]):
            avisos.append(f"{e['id']}: solo hay fondo y texto; ¿seguro que no falta algo visual?")

    minutos = palabras / PALABRAS_MIN
    curso = esc["id"].rsplit("-", 1)[0]
    try:
        sys.path.insert(0, str(RAIZ / "pipeline"))
        import curriculo
        lo, hi = curriculo.cargar(curso)["duracion_min"]
        if not lo * 0.9 <= minutos <= hi * 1.1:
            avisos.append(f"duración estimada {minutos:.1f} min fuera de {lo}-{hi} min ({palabras} palabras)")
    except Exception:
        pass
    return errores, avisos


def main(ep):
    errores, avisos = validar(ep)
    for a in avisos:
        print("AVISO ", a)
    for e in errores:
        print("ERROR ", e)
    if errores:
        sys.exit(1)
    print("escenas.json válido.")


if __name__ == "__main__":
    main(sys.argv[1])
