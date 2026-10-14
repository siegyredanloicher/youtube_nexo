"""Chequeo de salud del repo: ejecútalo tras cambiar agentes, skills, esquemas, currículo o la librería de Nexo.

Uso:  python pipeline/comprobar.py
Comprueba:
  - currículo válido (ids, requisitos, ciclos)
  - el verificador pasa con pipeline/tests/claims_ejemplo.json
  - agentes y skills: frontmatter correcto y cada skill citada existe
  - comandos que citan agentes existentes
  - nexo/catalogo.json coincide con nexo/props.py y nexo/acciones.py (si bpy está disponible)
"""
import json
import re
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
fallos = []


def ok(cond, msg):
    print(("OK    " if cond else "FALLA ") + msg)
    if not cond:
        fallos.append(msg)


def frontmatter(p):
    m = re.match(r"^---\n(.*?)\n---\n", p.read_text(encoding="utf-8"), re.S)
    if not m:
        return None
    return dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)


def main():
    r = subprocess.run([sys.executable, str(RAIZ / "pipeline/curriculo.py"), "validar"], capture_output=True, text=True)
    ok(r.returncode == 0, "currículo válido" + ("" if r.returncode == 0 else f": {r.stdout.strip()}"))
    r = subprocess.run([sys.executable, str(RAIZ / "pipeline/verificar.py"), str(RAIZ / "pipeline/tests/claims_ejemplo.json")],
                       capture_output=True, text=True)
    ok(r.returncode == 0, "verificador con claims de ejemplo")

    skills = {p.parent.name for p in (RAIZ / ".claude/skills").glob("*/SKILL.md")}
    for p in sorted((RAIZ / ".claude/skills").glob("*/SKILL.md")):
        fm = frontmatter(p)
        ok(fm and fm.get("name", "").strip() == p.parent.name and fm.get("description"), f"skill {p.parent.name}")
    agentes = set()
    for p in sorted((RAIZ / ".claude/agents").glob("*.md")):
        fm = frontmatter(p) or {}
        agentes.add(fm.get("name", "").strip())
        citadas = [s.strip() for s in fm.get("skills", "").split(",") if s.strip()]
        faltan = [s for s in citadas if s not in skills]
        ok(fm.get("name", "").strip() == p.stem and fm.get("description") and not faltan,
           f"agente {p.stem}" + (f" (skills que no existen: {faltan})" if faltan else ""))
    for p in sorted((RAIZ / ".claude/commands").glob("*.md")):
        texto = p.read_text(encoding="utf-8")
        citados = set(re.findall(r"[Aa]gentes? `([a-z0-9-]+)`", texto)) | set(re.findall(r"`([a-z0-9-]+)`(?:,| y| \()", texto))
        faltan = [a for a in citados if a not in agentes and "-" in a and a not in skills and not a.startswith("e0")]
        ok(not faltan, f"comando /{p.stem}" + (f" (agentes que no existen: {faltan})" if faltan else ""))

    cat = json.loads((RAIZ / "nexo/catalogo.json").read_text(encoding="utf-8"))
    try:
        import bpy  # noqa: F401
        sys.path.insert(0, str(RAIZ / "nexo"))
        import acciones
        import props
        ok(set(cat["props"]) == set(props.PROPS), "catálogo de props al día (python3 nexo/props.py --catalogo)")
        ok(set(cat["acciones"]) == set(acciones.ACCIONES), "catálogo de acciones al día (python3 nexo/acciones.py --catalogo)")
    except ImportError:
        print("SALTO catálogo de Nexo (sin bpy)")
    print(f"\n{'Todo bien.' if not fallos else f'{len(fallos)} fallos.'}")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
