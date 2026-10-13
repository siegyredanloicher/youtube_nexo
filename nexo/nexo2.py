"""Nexo v2 · más detalle: manos con dedos (metaballs), puños, botas, dobladillo, cremallera, correas pegadas al cuerpo
(ray-cast), capucha con forro, tela con variación de color y arrugas suaves, bloom en los ojos (post)."""
import math, sys
sys.path.insert(0, "/home/claude/nexo")
import bpy, bmesh
from mathutils import Vector, Matrix
import build_nexo as nx
from build_nexo import (hexrgb, material, fabric, glow, to_obj, activate, smooth, sphere, rbox, ACC, J, HEAD_Z,
                        build_head, build_eyes, build_rig, skin_to_rig, set_camera, expr, pose, idle, reset_pose)

CREAM, CREAM2, SOLE, NAVY = "#E8DBC9", "#CDB99F", "#BBA88E", "#1C2A47"


def fabric2(name, color, color2, bump=0.35, scale=300):
    m = material(name, color, 0.9, **{"Sheen Weight": 0.7, "Sheen Roughness": 0.35, "Subsurface Weight": 0.12,
                                     "Subsurface Radius": (0.9, 0.6, 0.4)})
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    n1 = nt.nodes.new("ShaderNodeTexNoise"); n1.inputs["Scale"].default_value = scale; n1.inputs["Detail"].default_value = 10
    n2 = nt.nodes.new("ShaderNodeTexNoise"); n2.inputs["Scale"].default_value = 6; n2.inputs["Detail"].default_value = 3
    bm = nt.nodes.new("ShaderNodeBump"); bm.inputs["Strength"].default_value = bump; bm.inputs["Distance"].default_value = 0.0025
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"
    mix.inputs["A"].default_value = hexrgb(color); mix.inputs["B"].default_value = hexrgb(color2)
    ra = nt.nodes.new("ShaderNodeMapRange"); ra.inputs["From Min"].default_value = 0.35; ra.inputs["From Max"].default_value = 0.65
    ra.inputs["To Min"].default_value = 0.0; ra.inputs["To Max"].default_value = 0.45
    nt.links.new(n2.outputs["Fac"], ra.inputs["Value"]); nt.links.new(ra.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    nt.links.new(n1.outputs["Fac"], bm.inputs["Height"]); nt.links.new(bm.outputs["Normal"], b.inputs["Normal"])
    return m


def hit(body, o, d):
    ok, loc, nor, _ = body.ray_cast(Vector(o), Vector(d))
    return (loc, nor) if ok else (None, None)


def tube(name, pts, mat, bevel=0.006, extrude=0.0, cyclic=False, bone=None):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"
    cu.bevel_depth, cu.extrude, cu.bevel_resolution = bevel, extrude, 4
    sp = cu.splines.new("BEZIER"); sp.bezier_points.add(len(pts) - 1); sp.use_cyclic_u = cyclic
    for p, q in zip(sp.bezier_points, pts):
        p.co = q; p.handle_left_type = p.handle_right_type = "AUTO"
    ob = bpy.data.objects.new(name, cu); bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat); activate(ob); bpy.ops.object.convert(target="MESH"); smooth(ob)
    return ob


def build_body2(mat):
    verts, rad, edges = [], [], []

    def add(p, rx, ry=None):
        verts.append(p); rad.append((rx, ry or rx)); return len(verts) - 1
    P = lambda k, s=1: (J[k][0] * s, J[k][1], J[k][2])
    pel = add(P("pelvis"), 0.138, 0.114); che = add(P("chest"), 0.142, 0.12); nec = add(P("neck"), 0.056)
    edges += [(pel, che), (che, nec)]
    for s in (1, -1):
        sh = add(P("shoulder", s), 0.068); el = add(P("elbow", s), 0.06); wr = add(P("wrist", s), 0.052)
        hp = add(P("hip", s), 0.076); kn = add(P("knee", s), 0.066); an = add(P("ankle", s), 0.06)
        edges += [(che, sh), (sh, el), (el, wr), (pel, hp), (hp, kn), (kn, an)]
    me = bpy.data.meshes.new("NexoBody"); me.from_pydata(verts, edges, [])
    ob = to_obj("NexoBody", me, mat); activate(ob)
    sk = ob.modifiers.new("Skin", "SKIN"); sk.branch_smoothing = 0.8; sk.use_smooth_shade = True
    for i, (rx, ry) in enumerate(rad):
        v = me.skin_vertices[0].data[i]; v.radius = (rx, ry); v.use_root = (i == pel)
    ob.modifiers.new("Subsurf", "SUBSURF").levels = 3
    bpy.ops.object.modifier_apply(modifier="Skin"); bpy.ops.object.modifier_apply(modifier="Subsurf")
    smooth(ob)
    return ob


def build_hand(side, mat):
    mb = bpy.data.metaballs.new(f"HandMB{side}"); mb.resolution = 0.0035; mb.render_resolution = 0.0035; mb.threshold = 0.5
    ob = bpy.data.objects.new(f"NexoHand{'L' if side > 0 else 'R'}", mb); bpy.context.collection.objects.link(ob)

    def ball(x, y, z, r):
        e = mb.elements.new(type="BALL"); e.co = (x, y, z); e.radius = r * 1.9; e.stiffness = 2.0
    for dx in (-0.016, 0, 0.016):
        ball(dx, 0, -0.03, 0.027)
    for i, x in enumerate((-0.024, -0.008, 0.008, 0.024)):
        ball(x, -0.002, -0.056, 0.0155)
        ball(x, -0.006, -0.074 - (0.006 if i in (1, 2) else 0), 0.0135)
    # pulgar hacia el interior y adelante
    for (x, y, z, r) in ((-0.032, -0.008, -0.03, 0.017), (-0.045, -0.02, -0.046, 0.0145), (-0.051, -0.03, -0.06, 0.0125)):
        ball(x * -side, y, z, r)
    activate(ob); bpy.ops.object.convert(target="MESH"); ob = bpy.context.active_object
    ob.data.materials.append(mat); smooth(ob)
    # orientar: -Z local -> dirección muñeca->mano
    w = Vector((J["wrist"][0] * side, J["wrist"][1], J["wrist"][2]))
    h = Vector((J["hand"][0] * side, J["hand"][1] - 0.01, J["hand"][2] - 0.04))
    d = (h - w).normalized()
    q = Vector((0, 0, -1)).rotation_difference(d)
    ob.matrix_world = Matrix.Translation(w + d * 0.005) @ q.to_matrix().to_4x4()
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return ob


def build_boot(side, mat, mat_sole):
    c = Vector((J["ankle"][0] * side, -0.032, 0.052))
    boot = sphere(f"NexoBoot{side}", c, (0.068, 0.108, 0.056), mat, 48, 32)
    sole = sphere(f"NexoSole{side}", Vector((c.x, c.y - 0.004, 0.02)), (0.072, 0.114, 0.021), mat_sole, 48, 24)
    cap = sphere(f"NexoCap{side}", Vector((c.x, c.y - 0.055, 0.05)), (0.058, 0.06, 0.044), mat, 40, 24)
    return [boot, sole, cap]


def band(name, center, axis, radius, mat, minor=0.012, scale_xy=(1, 1)):
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=minor, major_segments=56, minor_segments=18)
    t = bpy.context.active_object; t.name = name; t.data.materials.append(mat)
    q = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized())
    t.matrix_world = Matrix.Translation(center) @ q.to_matrix().to_4x4()
    smooth(t); return t


def build_pack2(body, mat_navy, mat_acc, mat_strap, mat_trim):
    objs = []
    objs.append(rbox("NexoPack", (0, 0.118, 0.405), (0.205, 0.095, 0.215), mat_navy, 0.032))
    objs.append(rbox("NexoPackFlap", (0, 0.166, 0.466), (0.185, 0.022, 0.085), mat_navy, 0.013))
    objs.append(rbox("NexoPackPocket", (0, 0.172, 0.352), (0.125, 0.032, 0.075), mat_navy, 0.013))
    for x in (-0.095, 0.095):
        objs.append(rbox(f"NexoSidePocket{x}", (x, 0.118, 0.37), (0.03, 0.07, 0.11), mat_navy, 0.012))
    objs.append(rbox("NexoBuckle", (0, 0.182, 0.452), (0.03, 0.01, 0.028), mat_trim, 0.005))
    bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, segments=3, radius1=0.03, radius2=0.03, depth=0.006)
    me = bpy.data.meshes.new("NexoEmblem"); bm.to_mesh(me); bm.free()
    em = to_obj("NexoEmblem", me, mat_acc); em.rotation_euler = (math.pi / 2, 0, 0); em.location = (0, 0.1925, 0.352); objs.append(em)
    # correas pegadas al cuerpo
    for s in (1, -1):
        pts = []
        for z in (0.34, 0.43):
            loc, nor = hit(body, (0.076 * s, 1, z), (0, -1, 0)); pts.append(loc + nor * 0.007)
        for y in (0.045, -0.035):
            loc, nor = hit(body, (0.09 * s, y, 1), (0, 0, -1)); pts.append(loc + nor * 0.007)
        for z in (0.45, 0.385, 0.325):
            loc, nor = hit(body, (0.084 * s, -1, z), (0, 1, 0)); pts.append(loc + nor * 0.007)
        st = tube(f"NexoStrap{s}", pts, mat_strap, 0.013, 0.004)
        objs.append(st)
        loc, nor = hit(body, (0.084 * s, -1, 0.40), (0, 1, 0))
        objs.append(rbox(f"NexoStrapBuckle{s}", loc + nor * 0.012, (0.026, 0.012, 0.03), mat_trim, 0.004))
    return objs


def details(body, mat_trim, mat_zip):
    objs = []
    # dobladillo de la chaqueta (anillo que sigue la silueta)
    pts = []
    for k in range(48):
        a = 2 * math.pi * k / 48
        loc, nor = hit(body, (0, 0, 0.245), (math.cos(a), math.sin(a), 0))
        if loc is not None:
            pts.append(loc + nor * 0.004)
    hem = tube("NexoHem", pts, mat_trim, 0.012, 0.0, True); objs.append(("hips", hem))
    # cremallera
    pts = []
    for z in (0.49, 0.45, 0.40, 0.35, 0.30, 0.255):
        loc, nor = hit(body, (0, -1, z), (0, 1, 0)); pts.append(loc + nor * 0.003)
    objs.append(("spine", tube("NexoZip", pts, mat_zip, 0.0042)))
    loc, nor = hit(body, (0, -1, 0.462), (0, 1, 0))
    objs.append(("spine", rbox("NexoZipPull", loc + nor * 0.008, (0.014, 0.006, 0.026), mat_trim, 0.003)))
    return objs


def build2(nivel="bach"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cream = fabric2("Cream", CREAM, "#D9C7AE"); trim = fabric2("Trim", CREAM2, "#B9A586", 0.5, 380)
    soleM = material("Sole", SOLE, 0.6); navy = fabric2("Navy", NAVY, "#2B3D63", 0.3, 240)
    zipM = material("Zip", "#A8957C", 0.5); strapM = fabric2("Strap", "#2A3B60", "#3A4E7A", 0.3, 300)
    screen = material("Screen", "#020308", 0.22, **{"Coat Weight": 0.5, "Coat Roughness": 0.15, "Specular IOR Level": 0.4})
    eye = glow("Eye", "#BFE0FF", 14.0); acc = glow("Accent", ACC[nivel], 4.0)
    body = build_body2(cream)
    head, scr, rim, collar = build_head(cream, screen)
    # forro de la capucha y arrugas suaves
    bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.14, major_segments=80, minor_segments=20)
    lin = bpy.context.active_object; lin.name = "NexoHoodLining"; lin.data.materials.append(trim)
    lin.rotation_euler = (math.pi / 2, 0, 0); lin.location = (0, -0.215, HEAD_Z); lin.scale = (0.176, 0.176, 0.156); smooth(lin)
    tex = bpy.data.textures.new("Wr", "CLOUDS"); tex.noise_scale = 0.10
    dm = head.modifiers.new("Wrinkle", "DISPLACE"); dm.texture = tex; dm.strength = 0.006; dm.mid_level = 0.5
    e1, e2 = build_eyes(eye)
    hands = [build_hand(1, cream), build_hand(-1, cream)]
    boots = build_boot(1, cream, soleM) + build_boot(-1, cream, soleM)
    cuffs = []
    for s, sf in ((1, "L"), (-1, "R")):
        w = Vector((J["wrist"][0] * s, J["wrist"][1], J["wrist"][2])); e = Vector((J["elbow"][0] * s, J["elbow"][1], J["elbow"][2]))
        cuffs.append((f"forearm.{sf}", band(f"CuffW{sf}", w + (e - w).normalized() * 0.016, (w - e), 0.047, trim, 0.016)))
        a = Vector((J["ankle"][0] * s, J["ankle"][1], J["ankle"][2])); k = Vector((J["knee"][0] * s, J["knee"][1], J["knee"][2]))
        cuffs.append((f"shin.{sf}", band(f"CuffA{sf}", a + (k - a).normalized() * 0.018, (a - k), 0.056, trim, 0.017)))
    det = details(body, trim, zipM)
    pack = build_pack2(body, navy, acc, strapM, trim)
    rig = build_rig()
    others = [(head, "head"), (scr, "head"), (rim, "head"), (lin, "head"), (collar, "neck"), (e1, "head"), (e2, "head"),
              (hands[0], "hand.L"), (hands[1], "hand.R")]
    others += [(b, "foot.L" if "1" in b.name and "-" not in b.name else "foot.R") for b in boots]
    others += [(o, bn) for bn, o in cuffs] + [(o, bn) for bn, o in det] + [(p, "chest") for p in pack]
    skin_to_rig(body, rig, others)
    mz = min(v.co.z for v in body.data.vertices)
    for b in boots:
        mz = min(mz, min((b.matrix_world @ v.co).z for v in b.data.vertices))
    return dict(rig=rig, body=body, eyes=(e1, e2), floor_z=mz)


def studio2(floor_z=0.0, hero=False):
    cam = nx.studio(floor_z=floor_z)
    sc = bpy.context.scene
    for o in bpy.data.objects:
        if o.type == "LIGHT":
            o.data.energy *= {"Key": 1.0, "Fill": 1.1, "Rim": 1.0}.get(o.name, 1)
            if o.name == "Key":
                o.data.size = 3.0
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.5
    sc.cycles.samples = 48
    sc.view_settings.exposure = -0.15
    return cam


def bloom(path, out=None, strength=1.0):
    import numpy as np
    from PIL import Image, ImageFilter
    im = Image.open(path).convert("RGB"); a = np.asarray(im).astype(np.float32) / 255
    m = np.clip((a.min(axis=2) - 0.86) / 0.14, 0, 1)
    m = np.clip(m * (a[..., 2] > 0.9), 0, 1)
    lum = Image.fromarray((a.mean(axis=2) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(14))
    dark = np.clip((0.42 - np.asarray(lum).astype(np.float32) / 255) / 0.2, 0, 1)
    m = m * dark
    mm = Image.fromarray((m * 255).astype(np.uint8))
    g1 = np.asarray(mm.filter(ImageFilter.GaussianBlur(9))).astype(np.float32) / 255
    g2 = np.asarray(mm.filter(ImageFilter.GaussianBlur(26))).astype(np.float32) / 255
    tint = np.array([0.55, 0.78, 1.0], dtype=np.float32)
    add = (g1 * 1.1 + g2 * 0.9)[..., None] * tint * strength
    r = 1 - (1 - a) * (1 - np.clip(add, 0, 1))
    Image.fromarray((np.clip(r, 0, 1) * 255).astype(np.uint8)).save(out or path)


if __name__ == "__main__":
    N = build2("bach"); cam = studio2(N["floor_z"])
    sc = bpy.context.scene; sc.render.resolution_x, sc.render.resolution_y = 700, 800; sc.cycles.samples = 36
    for n, az in (("n2_front", 0), ("n2_three", 38)):
        reset_pose(N); expr(N, "Feliz"); set_camera(cam, az, 5, 2.9, 0.5); sc.render.filepath = f"/home/claude/nexo/{n}.png"
        bpy.ops.render.render(write_still=True); bloom(sc.render.filepath)
    pose(N, "señala"); expr(N, "Curioso"); set_camera(cam, 22, 5, 2.9, 0.5); sc.render.filepath = "/home/claude/nexo/n2_pose.png"
    bpy.ops.render.render(write_still=True); bloom(sc.render.filepath)
    print("ok")
