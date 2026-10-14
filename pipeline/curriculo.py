"""Consultas sobre el currículo (catálogo + curso.json de cada curso).

Uso:
    python pipeline/curriculo.py cursos                  # materias y cursos con su estado
    python pipeline/curriculo.py ficha MAT-1ESO-U6.3     # ficha completa de un vídeo (JSON)
    python pipeline/curriculo.py siguiente MAT-1ESO      # próximo vídeo pendiente con requisitos cumplidos
    python pipeline/curriculo.py estado MAT-1ESO-U6.3 publicado   # cambia el estado de un vídeo
    python pipeline/curriculo.py mapa MAT-1ESO           # regenera curriculo/<materia>/<curso>/MAPA.md
    python pipeline/curriculo.py validar                 # ids únicos, requisitos que existen, sin ciclos
Estados de un vídeo: pendiente → guion → aprobado → produccion → revision → publicado.
"""
import json
import sys
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
CUR = RAIZ / "curriculo"
ESTADOS = ["pendiente", "guion", "aprobado", "produccion", "revision", "publicado"]
HECHO = {"publicado", "revision", "produccion", "aprobado"}  # ya cuenta como visto para requisitos


def catalogo():
    return yaml.safe_load((CUR / "catalogo.yaml").read_text(encoding="utf-8"))


def ruta_curso(curso_id):
    mat, cur = curso_id.split("-", 1)
    carpeta = catalogo()["materias"][mat]["carpeta"]
    return CUR / carpeta / cur.lower() / "curso.json"


def cargar(curso_id):
    return json.loads(ruta_curso(curso_id).read_text(encoding="utf-8"))


def guardar(curso_id, data):
    ruta_curso(curso_id).write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def curso_de(video_id):
    partes = video_id.split("-")
    return f"{partes[0]}-{partes[1]}"


def ficha(video_id):
    data = cargar(curso_de(video_id))
    for v in data["videos"]:
        if v["id"] == video_id or v["codigo"] == video_id:
            return {**v, "curso": data["titulo"], "nivel_nexo": data["nivel_nexo"],
                    "duracion_min": data["duracion_min"], "materia": data["materia"]}
    raise SystemExit(f"No existe {video_id}")


def siguiente(curso_id):
    data = cargar(curso_id)
    hechos = {v["codigo"] for v in data["videos"] if v["estado"] in HECHO}
    for v in data["videos"]:
        if v["estado"] == "pendiente" and all(r in hechos for r in v["requisitos"]):
            return v
    return None


def mapa(curso_id):
    d = cargar(curso_id)
    L = [f"# {d['titulo']}", "", "> Generado desde `curso.json` con `pipeline/curriculo.py mapa`. No editar a mano.", "",
         f"Nivel de Nexo: **{d['nivel_nexo']}** · Duración: {d['duracion_min'][0]}-{d['duracion_min'][1]} min · "
         f"{len(d['videos'])} vídeos", ""]
    for u in d["unidades"]:
        L += [f"## {u['id']}. {u['titulo']}" if u["id"] != "T" else f"## {u['titulo']}", "", u["descripcion"], "",
              "| Vídeo | Estado | Idea clave | En la vida real | Nexo | Problema inverso | Requisitos |",
              "| --- | --- | --- | --- | --- | --- | --- |"]
        for v in d["videos"]:
            if v["unidad"] == u["id"] or (u["id"] == "T" and v["codigo"].startswith("T")):
                cells = [f"**{v['codigo']}** {v['titulo']}", v["estado"], v["idea_clave"], v["vida_real"], v["nexo"],
                         v["problema_inverso"], ", ".join(v["requisitos"]) or "—"]
                L.append("| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |")
        L.append("")
    out = ruta_curso(curso_id).with_name("MAPA.md")
    out.write_text("\n".join(L), encoding="utf-8")
    return out


def validar():
    errores = []
    for mat, m in catalogo()["materias"].items():
        for cur in m["cursos"]:
            cid = f"{mat}-{cur}"
            if not ruta_curso(cid).exists():
                continue
            d = cargar(cid)
            cods = [v["codigo"] for v in d["videos"]]
            if len(cods) != len(set(cods)):
                errores.append(f"{cid}: códigos repetidos")
            for v in d["videos"]:
                if v["estado"] not in ESTADOS:
                    errores.append(f"{v['id']}: estado desconocido {v['estado']}")
                for r in v["requisitos"]:
                    if r not in cods:
                        errores.append(f"{v['id']}: requisito {r} no existe")
            # ciclos
            dep = {v["codigo"]: v["requisitos"] for v in d["videos"]}
            visit, pila = set(), set()

            def dfs(n):
                if n in pila:
                    errores.append(f"{cid}: ciclo de requisitos en {n}")
                    return
                if n in visit:
                    return
                pila.add(n)
                for r in dep.get(n, []):
                    dfs(r)
                pila.discard(n)
                visit.add(n)
            for n in dep:
                dfs(n)
    return errores


def main(a):
    if not a:
        print(__doc__)
        return
    cmd = a[0]
    if cmd == "cursos":
        for mat, m in catalogo()["materias"].items():
            for cur, c in m["cursos"].items():
                print(f"{mat}-{cur:8s} {c['estado']:10s} {c['nivel']:9s} {c.get('nombre', m['nombre'])}")
    elif cmd == "ficha":
        print(json.dumps(ficha(a[1]), ensure_ascii=False, indent=1))
    elif cmd == "siguiente":
        v = siguiente(a[1])
        print(json.dumps(v, ensure_ascii=False, indent=1) if v else "No queda nada pendiente con requisitos cumplidos.")
    elif cmd == "estado":
        if a[2] not in ESTADOS:
            raise SystemExit(f"Estado no válido. Usa: {', '.join(ESTADOS)}")
        cid = curso_de(a[1])
        d = cargar(cid)
        for v in d["videos"]:
            if v["id"] == a[1]:
                v["estado"] = a[2]
        guardar(cid, d)
        mapa(cid)
        print(a[1], "→", a[2])
    elif cmd == "mapa":
        print("Escrito", mapa(a[1]))
    elif cmd == "validar":
        e = validar()
        print("\n".join(e) if e else "Currículo válido.")
        sys.exit(1 if e else 0)
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
