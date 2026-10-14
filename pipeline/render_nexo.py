"""Renderiza un plano de Nexo descrito en JSON (el objeto "plano" de escenas.json).

Uso:
    python3 pipeline/render_nexo.py plano.json --salida episodios/X/render/nexo/e05 [opciones]
    blender -b nexo/nexo.blend --python pipeline/render_nexo.py -- plano.json --salida ...   (igual)
Opciones:
    --motor eevee|cycles   eevee por defecto (PC con gráfica); cycles funciona sin GPU
    --res 1920x1080        resolución (por defecto la de tokens.json)
    --muestras N           muestras de render (por defecto 64 en eevee, 48 en cycles)
    --nivel eso|bach|uni|avanzado   color del emblema (por defecto el del plano o eso)
    --mov                  además, une la secuencia en un .mov ProRes 4444 con alfa
    --prueba               rápido: 1/3 de resolución, pocas muestras, para revisar el movimiento
    --fotograma N          solo ese fotograma (para miniaturas o revisión)
Salida: <salida>/####.png (RGBA, fondo transparente salvo entorno "estudio") y <salida>/plano_meta.json.

Ejemplo de plano:
{"accion": "lanzar", "params": {"prop": "p1", "v0": 4, "angulo": 50},
 "props": [{"id": "p1", "prop": "pelota"}], "camara": "completo", "encuadre": "izquierda", "duracion_s": 3}
"""
import json
import math
import subprocess
import sys
from pathlib import Path

import bpy
from mathutils import Vector

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "nexo"))
import acciones as A  # noqa: E402
import props as PR  # noqa: E402
from omnia.marca import VIDEO, nivel_color  # noqa: E402

CAMARAS = {  # azimut, elevación, qué hay que encuadrar
    "completo": (0, 6, "todo"), "tres_cuartos": (-30, 8, "todo"), "lateral": (90, 4, "todo"),
    "picado": (-15, 32, "todo"), "medio": (-8, 4, "busto"), "primer_plano": (-10, 2, "cabeza"),
}


def args_cli():
    a = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    op = {"plano": a[0], "salida": None, "motor": "eevee", "res": None, "muestras": None, "nivel": None,
          "mov": False, "prueba": False, "fotograma": None}
    i = 1
    while i < len(a):
        k = a[i].lstrip("-")
        if k in ("mov", "prueba"):
            op[k] = True
        else:
            op[k] = a[i + 1]
            i += 1
        i += 1
    if not op["salida"]:
        op["salida"] = str(Path(op["plano"]).with_suffix(""))
    return op


def abrir_modelo():
    if "NexoRig" not in bpy.data.objects:
        bpy.ops.wm.open_mainfile(filepath=str(RAIZ / "nexo" / "nexo.blend"))
    rig, ojos = bpy.data.objects["NexoRig"], bpy.data.objects["NexoEyeL"]
    rig.animation_data_clear()
    if ojos.data.shape_keys.animation_data:
        ojos.data.shape_keys.animation_data_clear()
    for kb in ojos.data.shape_keys.key_blocks:
        kb.value = 0.0
    for pb in rig.pose.bones:
        pb.location, pb.rotation_mode = (0, 0, 0), "XYZ"
        pb.rotation_euler, pb.scale = (0, 0, 0), (1, 1, 1)
    return rig, ojos


def aplicar_nivel(nivel):
    m = bpy.data.materials.get("Acento")
    if not m:
        return
    for n in m.node_tree.nodes:
        if n.type == "EMISSION":
            h = nivel_color(nivel).lstrip("#")
            f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4  # noqa: E731
            n.inputs["Color"].default_value = tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (1,)


def puntos_interes(P, modo, escena, n_frames):
    if modo == "cabeza":
        return [Vector((x, y, z)) for x in (-0.3, 0.3) for y in (-0.3, 0.3) for z in (0.48, 1.05)]
    if modo == "busto":
        return [Vector((x, y, z)) for x in (-0.33, 0.33) for y in (-0.3, 0.3) for z in (0.3, 1.06)]
    pts = [Vector((x, y, z)) for x in (-0.36, 0.36) for y in (-0.3, 0.3) for z in (0.0, 1.08)]
    raiz = escena.objects["NexoRig"]
    paso = max(1, n_frames // 24)
    for f in range(1, n_frames + 1, paso):
        escena.frame_set(f)
        desp = raiz.pose.bones["root"].matrix.translation
        pts += [p + desp for p in pts[:2]]
        for ob in P.props.values():
            r = ob.get("radio", 0.1)
            c = ob.matrix_world.translation
            pts += [c + Vector((dx, 0, dz)) for dx in (-r, r) for dz in (-r, r * 2)]
    escena.frame_set(1)
    return pts


def encuadrar(cam, escena, pts, az, el, encuadre, margen=0.08):
    centro = sum(pts, Vector()) / len(pts)
    a, e = math.radians(az), math.radians(el)
    adelante = Vector((-math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), -math.sin(e)))  # de cámara a sujeto
    cam.data.shift_x = {"izquierda": 0.18, "derecha": -0.18}.get(encuadre, 0.0)
    asp = escena.render.resolution_x / escena.render.resolution_y
    fov = cam.data.angle  # horizontal (sensor_fit AUTO con imagen apaisada)
    th, tv = math.tan(fov / 2), math.tan(fov / 2) / asp
    lim_h = th * (1 - margen) - abs(cam.data.shift_x) * 2 * th
    lim_v = tv * (1 - margen)
    dist = 1.0
    for _ in range(200):
        cam.location = centro - adelante * dist
        cam.rotation_euler = adelante.to_track_quat("-Z", "Y").to_euler()
        bpy.context.view_layer.update()
        inv = cam.matrix_world.inverted()
        ok = True
        for p in pts:
            q = inv @ p
            if -q.z <= 0.05 or abs(q.x / -q.z) > lim_h or abs(q.y / -q.z) > lim_v:
                ok = False
                break
        if ok:
            return dist
        dist *= 1.04
    return dist


def preparar_render(escena, op, entorno):
    motor = op["motor"]
    escena.render.engine = "BLENDER_EEVEE" if motor == "eevee" else "CYCLES"
    if motor == "cycles":
        escena.cycles.device = "CPU"
        escena.cycles.samples = int(op["muestras"] or (12 if op["prueba"] else 48))
        escena.cycles.use_denoising = True
    else:
        escena.eevee.taa_render_samples = int(op["muestras"] or (16 if op["prueba"] else 64))
    w, h = (map(int, op["res"].split("x")) if op["res"] else VIDEO["resolucion"])
    if op["prueba"]:
        w, h = w // 3, h // 3
    escena.render.resolution_x, escena.render.resolution_y = w, h
    escena.render.image_settings.file_format = "PNG"
    escena.render.image_settings.color_mode = "RGBA"
    suelo = escena.objects.get("Floor")
    if entorno == "estudio":
        escena.render.film_transparent = False
    else:
        escena.render.film_transparent = True
        if suelo:
            if motor == "cycles":
                suelo.is_shadow_catcher = True
            else:
                suelo.hide_render = True
    if hasattr(escena.render, "compositor_device"):
        escena.render.compositor_device = "CPU"


def main():
    op = args_cli()
    plano = json.loads(Path(op["plano"]).read_text(encoding="utf-8"))
    if "plano" in plano:          # admite también la capa entera de escenas.json
        plano = plano["plano"]
    rig, ojos = abrir_modelo()
    escena = bpy.context.scene  # después de abrir el .blend
    nivel = op["nivel"] or plano.get("nivel", "eso")
    aplicar_nivel(nivel)
    fps = int(plano.get("fps", VIDEO.get("fps_nexo", VIDEO["fps"])))
    escena.render.fps = fps
    P = A.Plano(rig, ojos, fps)

    for p in plano.get("props", []):
        params = {k: v for k, v in p.get("params", {}).items()}
        if p["prop"] in ("pelota", "puntero", "coche", "matraz", "robot", "vaso") and "nivel" not in params:
            params["nivel"] = nivel
        ob = PR.construir(p["prop"], **params)
        ob.name = p["id"]
        if p.get("escala"):
            ob.scale = (p["escala"],) * 3
        en = p.get("en")
        if isinstance(en, list):
            ob.location = Vector(en)
        P.props[p["id"]] = ob

    if plano["accion"] not in A.ACCIONES:
        raise SystemExit(f"Acción '{plano['accion']}' no existe. Disponibles: {', '.join(sorted(A.ACCIONES))}")
    dur = A.ACCIONES[plano["accion"]]["fn"](P, **plano.get("params", {}))
    total = max(dur, plano.get("duracion_s", 0))
    if total > dur + 0.3:      # el resto del plano, en reposo
        P.respirar(dur + 0.3, total)
    for e in plano.get("expresiones", []):
        if e["nombre"] == "Neutro":
            P.expr("Feliz", e["t"], 0.0)
        else:
            P.expr(e["nombre"], e["t"], e.get("valor", 1.0))
    n_frames = P.f(total)
    escena.frame_start, escena.frame_end = 1, n_frames
    P.hornear(escena)

    preparar_render(escena, op, plano.get("entorno", "transparente"))
    az, el, modo = CAMARAS[plano.get("camara", "completo")]
    cam = escena.camera
    cam.data.lens = 50
    encuadrar(cam, escena, puntos_interes(P, modo, escena, n_frames), az, el, plano.get("encuadre", "centro"))

    salida = Path(op["salida"])
    salida.mkdir(parents=True, exist_ok=True)
    escena.render.filepath = str(salida) + "/"
    if op["fotograma"]:
        escena.frame_set(int(op["fotograma"]))
        escena.render.filepath = str(salida / f"{int(op['fotograma']):04d}.png")
        bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)
    meta = dict(accion=plano["accion"], fps=fps, fotogramas=n_frames, duracion_s=n_frames / fps,
                resolucion=[escena.render.resolution_x, escena.render.resolution_y], motor=op["motor"],
                camara=plano.get("camara", "completo"), encuadre=plano.get("encuadre", "centro"))
    if hasattr(P, "_lanzamiento"):
        meta["lanzamiento"] = P._lanzamiento
    (salida / "plano_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    if op["mov"] and not op["fotograma"]:
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(fps), "-i", str(salida / "%04d.png"),
                        "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le",
                        str(salida.with_suffix(".mov"))], check=True)
    print("PLANO OK", json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
