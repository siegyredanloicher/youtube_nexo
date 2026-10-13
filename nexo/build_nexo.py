"""Nexo · personaje 3D para Blender (bpy). Cuerpo suave (skin modifier), capucha con pantalla facial,
ojos con shape keys (expresiones), mochila, esqueleto con IK y pesos automáticos.
Uso:  python3 build_nexo.py        -> crea nexo.blend
      (o dentro de Blender: Scripting > abrir y ejecutar)"""
import math
import sys

import bpy
import bmesh
from mathutils import Vector

ACC = {"eso": "#7DD3C0", "bach": "#7CC4F2", "uni": "#A78BFA", "avanzado": "#F8A5A5"}


def hexrgb(h, a=1.0):
    h = h.lstrip("#")
    lin = lambda v: ((v / 255 + 0.055) / 1.055) ** 2.4 if v / 255 > 0.04045 else v / 255 / 12.92
    return (lin(int(h[0:2], 16)), lin(int(h[2:4], 16)), lin(int(h[4:6], 16)), a)


# ---------------------------------------------------------------- materiales
def material(name, color, rough=0.8, **kw):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = hexrgb(color)
    b.inputs["Roughness"].default_value = rough
    for k, v in kw.items():
        if k in b.inputs:
            b.inputs[k].default_value = v
    return m


def fabric(name, color, bump=0.25, scale=260):
    m = material(name, color, 0.88, **{"Sheen Weight": 0.6, "Sheen Roughness": 0.4, "Subsurface Weight": 0.08})
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tex = nt.nodes.new("ShaderNodeTexNoise")
    tex.inputs["Scale"].default_value = scale
    tex.inputs["Detail"].default_value = 8
    bm = nt.nodes.new("ShaderNodeBump")
    bm.inputs["Strength"].default_value = bump
    bm.inputs["Distance"].default_value = 0.002
    nt.links.new(tex.outputs["Fac"], bm.inputs["Height"])
    nt.links.new(bm.outputs["Normal"], b.inputs["Normal"])
    return m


def glow(name, color, power=9.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = hexrgb(color)
    e.inputs["Strength"].default_value = power
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(e.outputs["Emission"], o.inputs["Surface"])
    return m


# ---------------------------------------------------------------- utilidades
def to_obj(name, mesh, mat=None):
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(ob)
    if mat:
        ob.data.materials.append(mat)
    return ob


def activate(ob):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def smooth(ob, sub=0):
    for p in ob.data.polygons:
        p.use_smooth = True
    if sub:
        m = ob.modifiers.new("Subsurf", "SUBSURF")
        m.levels = sub
        m.render_levels = sub + 1


def sphere(name, loc, scale, mat, seg=48, rings=32):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = to_obj(name, me, mat)
    ob.location = loc
    ob.scale = scale
    smooth(ob)
    return ob


def rbox(name, loc, size, mat, bevel=0.02, rot=(0, 0, 0)):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = to_obj(name, me, mat)
    ob.location = loc
    ob.scale = size
    ob.rotation_euler = rot
    activate(ob)
    bpy.ops.object.transform_apply(scale=True)
    b = ob.modifiers.new("Bevel", "BEVEL")
    b.width = bevel
    b.segments = 5
    s = ob.modifiers.new("Subsurf", "SUBSURF")
    s.levels = 1
    s.render_levels = 2
    smooth(ob)
    return ob


# ---------------------------------------------------------------- cuerpo
J = {  # articulaciones (m) · Z arriba, mira hacia -Y
    "pelvis": (0, 0, 0.27), "chest": (0, 0, 0.42), "neck": (0, 0, 0.50),
    "shoulder": (0.115, 0, 0.455), "elbow": (0.185, -0.012, 0.355), "wrist": (0.20, -0.04, 0.265), "hand": (0.205, -0.052, 0.225),
    "hip": (0.058, 0, 0.245), "knee": (0.064, -0.012, 0.135), "ankle": (0.064, 0, 0.058), "toe": (0.064, -0.055, 0.04),
}
HEAD_Z = 0.77


def build_body(mat):
    verts, rad, edges = [], [], []

    def add(p, rx, ry=None):
        verts.append(p)
        rad.append((rx, ry or rx))
        return len(verts) - 1

    P = lambda k, s=1: (J[k][0] * s, J[k][1], J[k][2])
    pel = add(P("pelvis"), 0.128, 0.108)
    che = add(P("chest"), 0.13, 0.112)
    nec = add(P("neck"), 0.052)
    edges += [(pel, che), (che, nec)]
    for s in (1, -1):
        sh = add(P("shoulder", s), 0.064)
        el = add(P("elbow", s), 0.056)
        wr = add(P("wrist", s), 0.05)
        ha = add(P("hand", s), 0.068, 0.06)
        hp = add(P("hip", s), 0.07)
        kn = add(P("knee", s), 0.062)
        an = add(P("ankle", s), 0.058)
        to = add(P("toe", s), 0.066, 0.085)
        edges += [(che, sh), (sh, el), (el, wr), (wr, ha), (pel, hp), (hp, kn), (kn, an), (an, to)]
    me = bpy.data.meshes.new("NexoBody")
    me.from_pydata(verts, edges, [])
    ob = to_obj("NexoBody", me, mat)
    activate(ob)
    sk = ob.modifiers.new("Skin", "SKIN")
    sk.branch_smoothing = 0.7
    sk.use_smooth_shade = True
    for i, (rx, ry) in enumerate(rad):
        v = me.skin_vertices[0].data[i]
        v.radius = (rx, ry)
        v.use_root = (i == pel)
    ob.modifiers.new("Subsurf", "SUBSURF").levels = 2
    ob.modifiers["Subsurf"].render_levels = 3
    bpy.ops.object.modifier_apply(modifier="Skin")
    bpy.ops.object.modifier_apply(modifier="Subsurf")
    smooth(ob)
    return ob


def build_head(mat_cream, mat_screen):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=72, v_segments=54, radius=1.0)
    for v in bm.verts:
        x, y, z = v.co
        X, Y, Z = x * 0.265, y * 0.255, z * 0.245
        # pico suave de la capucha (arriba y algo atrás)
        if z > 0:
            Z += 0.075 * z * math.exp(-((x * 2.6) ** 2 + ((y - 0.15) * 2.4) ** 2))
        # nuca algo más prominente
        if y > 0.2:
            Y += 0.02 * (y - 0.2)
        v.co = (X, Y, Z)
    me = bpy.data.meshes.new("NexoHead")
    bm.to_mesh(me)
    bm.free()
    head = to_obj("NexoHead", me, mat_cream)
    head.location = (0, 0, HEAD_Z)
    smooth(head)
    # pantalla facial
    scr = sphere("NexoScreen", (0, -0.2255, HEAD_Z), (0.172, 0.036, 0.152), mat_screen, 64, 40)
    # reborde de la capucha
    bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.2, major_segments=80, minor_segments=24)
    rim = bpy.context.active_object
    rim.name = "NexoRim"
    rim.data.materials.append(mat_cream)
    rim.rotation_euler = (math.pi / 2, 0, 0)
    rim.location = (0, -0.2, HEAD_Z)
    rim.scale = (0.19, 0.19, 0.168)
    smooth(rim)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.3, major_segments=48, minor_segments=20)
    col = bpy.context.active_object
    col.name = 'NexoCollar'
    col.data.materials.append(mat_cream)
    col.location = (0, -0.005, 0.515)
    col.scale = (0.078, 0.07, 0.05)
    smooth(col)
    return head, scr, rim, col


def build_eyes(mat_eye):
    """ojo = anillo de 2 coronas de vértices; shape keys cambian la expresión"""
    N = 40
    rx, rz = 0.032, 0.044
    outer = [(math.cos(2 * math.pi * i / N) * rx, 0, math.sin(2 * math.pi * i / N) * rz) for i in range(N)]
    kin = 0.02
    inner = [(p[0] * kin, 0, p[2] * kin) for p in outer]
    verts = outer + inner
    faces = [(i, (i + 1) % N, N + (i + 1) % N, N + i) for i in range(N)]
    me = bpy.data.meshes.new("NexoEyeMesh")
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new("NexoEyeL", me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat_eye)
    ob.shape_key_add(name="Basis")

    def key(name, fn):
        k = ob.shape_key_add(name=name)
        for i in range(2 * N):
            ring_in = i >= N
            a = 2 * math.pi * (i % N) / N
            k.data[i].co = fn(a, ring_in)
        return k

    base = lambda a, ri: (math.cos(a) * rx * (kin if ri else 1), 0, math.sin(a) * rz * (kin if ri else 1))

    def feliz(a, ri):
        x, _, z = base(a, ri)
        kx = 0.64 if ri else 1.0
        x2, z2 = math.cos(a) * rx * 1.12 * kx, math.sin(a) * rz * 0.9 * kx
        return (x2, 0, max(z2, 0.0) - 0.004)

    key("Feliz", feliz)
    key("Tranquilo", lambda a, ri: (math.cos(a) * rx * 1.15 * (0.55 if ri else 1), 0, (math.sin(a) * rz * 0.16 * (0.55 if ri else 1)) - 0.012 * (1 - (math.cos(a)) ** 2) * 0 + (0.012 * math.cos(a) ** 2 - 0.006)))
    key("Sorpresa", lambda a, ri: (base(a, ri)[0] * 1.28, 0, base(a, ri)[2] * 1.3))
    key("Pensativo", lambda a, ri: (base(a, ri)[0], 0, min(base(a, ri)[2], 0.012) if not ri else 0.0))
    key("Concentrado", lambda a, ri: (base(a, ri)[0] * 1.08, 0, base(a, ri)[2] * 0.55))
    key("Curioso", lambda a, ri: (base(a, ri)[0] * 0.92, 0, base(a, ri)[2] * 1.08))
    for k in ob.data.shape_keys.key_blocks:
        k.slider_min, k.slider_max = 0.0, 1.0
    smooth(ob)
    ob2 = bpy.data.objects.new("NexoEyeR", me)  # comparte malla y shape keys
    bpy.context.collection.objects.link(ob2)
    ob.location = (0.074, -0.2655, HEAD_Z + 0.008)
    ob2.location = (-0.074, -0.2655, HEAD_Z + 0.008)
    ob.rotation_euler = ob2.rotation_euler = (0, 0, 0)
    ob["halos"] = []
    return ob, ob2


def build_pack(mat_navy, mat_cream, mat_acc, nivel):
    bag = rbox("NexoPack", (0, 0.115, 0.405), (0.2, 0.09, 0.2), mat_navy, 0.03)
    flap = rbox("NexoPackFlap", (0, 0.158, 0.455), (0.18, 0.02, 0.08), mat_navy, 0.012)
    pocket = rbox("NexoPackPocket", (0, 0.163, 0.355), (0.12, 0.03, 0.07), mat_navy, 0.012)
    straps = []
    for s_ in (1, -1):
        cu = bpy.data.curves.new(f"StrapC{s_}", "CURVE")
        cu.dimensions = "3D"
        cu.bevel_depth = 0.011
        cu.extrude = 0.006
        cu.bevel_resolution = 3
        sp = cu.splines.new("BEZIER")
        pts = [(0.07, 0.09, 0.505), (0.088, 0.0, 0.505), (0.095, -0.075, 0.468), (0.085, -0.108, 0.395), (0.115, -0.07, 0.32), (0.11, 0.02, 0.325), (0.09, 0.075, 0.33)]
        sp.bezier_points.add(len(pts) - 1)
        for p, q in zip(sp.bezier_points, pts):
            p.co = (q[0] * s_, q[1], q[2])
            p.handle_left_type = p.handle_right_type = "AUTO"
        co = bpy.data.objects.new(f"NexoStrap{s_}", cu)
        bpy.context.collection.objects.link(co)
        co.data.materials.append(mat_navy)
        activate(co)
        bpy.ops.object.convert(target="MESH")
        smooth(co)
        straps.append(co)
    # emblema triangular
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=3, radius1=0.032, radius2=0.032, depth=0.006)
    me = bpy.data.meshes.new("NexoEmblem")
    bm.to_mesh(me)
    bm.free()
    em = to_obj("NexoEmblem", me, mat_acc)
    em.rotation_euler = (math.pi / 2, 0, 0)
    em.location = (0, 0.1705, 0.37)
    return [bag, flap, pocket] + straps + [em]


# ---------------------------------------------------------------- esqueleto
def build_rig():
    arm = bpy.data.armatures.new("NexoRig")
    rig = bpy.data.objects.new("NexoRig", arm)
    bpy.context.collection.objects.link(rig)
    activate(rig)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones

    def bone(name, head, tail, parent=None, roll=0.0, deform=True):
        b = eb.new(name)
        b.head, b.tail = Vector(head), Vector(tail)
        b.roll = roll
        b.use_deform = deform
        if parent:
            b.parent = eb[parent]
        return b

    bone("root", (0, 0, 0), (0, 0, 0.08), deform=False)
    bone("hips", (0, 0, 0.27), (0, 0, 0.34), "root")
    bone("spine", (0, 0, 0.34), (0, 0, 0.43), "hips")
    bone("chest", (0, 0, 0.43), (0, 0, 0.5), "spine")
    bone("neck", (0, 0, 0.50), (0, 0, 0.56), "chest")
    bone("head", (0, 0, 0.56), (0, 0, 1.06), "neck")
    for s, sf in ((1, "L"), (-1, "R")):
        P = lambda k: (J[k][0] * s, J[k][1], J[k][2])
        bone(f"clavicle.{sf}", (0.03 * s, 0, 0.47), P("shoulder"), "chest")
        bone(f"upper_arm.{sf}", P("shoulder"), P("elbow"), f"clavicle.{sf}")
        bone(f"forearm.{sf}", P("elbow"), P("wrist"), f"upper_arm.{sf}")
        bone(f"hand.{sf}", P("wrist"), (J["hand"][0] * s, J["hand"][1] - 0.01, J["hand"][2] - 0.04), f"forearm.{sf}")
        bone(f"thigh.{sf}", P("hip"), P("knee"), "hips")
        bone(f"shin.{sf}", P("knee"), P("ankle"), f"thigh.{sf}")
        bone(f"foot.{sf}", P("ankle"), P("toe"), f"shin.{sf}")
        # controles IK
        bone(f"IK_hand.{sf}", P("wrist"), (P("wrist")[0], P("wrist")[1], P("wrist")[2] - 0.05), "root", deform=False)
        bone(f"IK_foot.{sf}", P("ankle"), (P("ankle")[0], P("ankle")[1] - 0.06, P("ankle")[2]), "root", deform=False)
        bone(f"pole_elbow.{sf}", (0.26 * s, 0.17, 0.36), (0.26 * s, 0.17, 0.40), "root", deform=False)
        bone(f"pole_knee.{sf}", (0.09 * s, -0.32, 0.15), (0.09 * s, -0.32, 0.19), "root", deform=False)
    bpy.ops.object.mode_set(mode="POSE")
    for sf in ("L", "R"):
        c = rig.pose.bones[f"forearm.{sf}"].constraints.new("IK")
        c.target, c.subtarget = rig, f"IK_hand.{sf}"
        c.pole_target, c.pole_subtarget = rig, f"pole_elbow.{sf}"
        c.pole_angle = math.radians(-90 if sf == "L" else -90)
        c.chain_count = 2
        c2 = rig.pose.bones[f"shin.{sf}"].constraints.new("IK")
        c2.target, c2.subtarget = rig, f"IK_foot.{sf}"
        c2.pole_target, c2.pole_subtarget = rig, f"pole_knee.{sf}"
        c2.pole_angle = math.radians(-90)
        c2.chain_count = 2
        # el pie copia la rotación del control
        c3 = rig.pose.bones[f"foot.{sf}"].constraints.new("COPY_ROTATION")
        c3.target, c3.subtarget = rig, f"IK_foot.{sf}"
    # formas de los controles
    for n, pb in rig.pose.bones.items():
        if n.startswith(("IK_", "pole_")):
            pb.custom_shape_scale_xyz = (1, 1, 1)
    bpy.ops.object.mode_set(mode="OBJECT")
    for b in arm.bones:
        if b.name.startswith(("IK_", "pole_")):
            b.color.palette = "THEME04" if b.name.startswith("IK_") else "THEME03"
    return rig


def skin_to_rig(body, rig, others):
    activate(body)
    body.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    for ob, bone in others:
        vg = ob.vertex_groups.new(name=bone)
        vg.add(list(range(len(ob.data.vertices))), 1.0, "REPLACE")
        m = ob.modifiers.new("Armature", "ARMATURE")
        m.object = rig
        ob.parent = rig


# ---------------------------------------------------------------- escena
def studio(bg="#E9E1D6", floor_z=0.0):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.cycles.denoiser = "OPENIMAGEDENOISE"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = 0.0
    w = bpy.data.worlds.new("W")
    sc.world = w
    w.use_nodes = True
    n = w.node_tree.nodes["Background"]
    n.inputs["Color"].default_value = hexrgb("#E9E1D6")
    n.inputs["Strength"].default_value = 0.45
    # suelo
    bpy.ops.mesh.primitive_plane_add(size=20)
    fl = bpy.context.active_object
    fl.name = "Floor"
    fl.location.z = floor_z
    fl.data.materials.append(material("Floor", bg, 0.95))

    def area(name, loc, energy, size, col="#FFFFFF", target=(0, 0, 0.5)):
        d = bpy.data.lights.new(name, "AREA")
        d.energy, d.size = energy, size
        d.color = hexrgb(col)[:3]
        o = bpy.data.objects.new(name, d)
        bpy.context.collection.objects.link(o)
        o.location = loc
        v = Vector(target) - Vector(loc)
        o.rotation_euler = v.to_track_quat("-Z", "Y").to_euler()
        return o

    area("Key", (1.6, -2.0, 2.4), 70, 1.6, "#FFF1DE")
    area("Fill", (-2.2, -1.6, 1.0), 22, 2.2, "#DCE8FF")
    area("Rim", (0.4, 2.2, 1.8), 55, 1.2, "#FFFFFF")
    sm = bpy.data.materials.new("Contact")
    sm.use_nodes = True
    nt = sm.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Location"].default_value = (-1.0, -1.0, 0)
    mp.inputs["Scale"].default_value = (2.0, 2.0, 2.0)
    gr = nt.nodes.new("ShaderNodeTexGradient")
    gr.gradient_type = "SPHERICAL"
    ra = nt.nodes.new("ShaderNodeValToRGB")
    ra.color_ramp.elements[0].color = (0, 0, 0, 1)
    ra.color_ramp.elements[1].color = (0.55, 0.55, 0.55, 1)
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    bk = nt.nodes.new("ShaderNodeBsdfDiffuse")
    bk.inputs["Color"].default_value = (0.02, 0.015, 0.01, 1)
    mx = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(tc.outputs["Generated"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], gr.inputs["Vector"])
    nt.links.new(gr.outputs["Fac"], ra.inputs["Fac"])
    nt.links.new(ra.outputs["Color"], mx.inputs["Fac"])
    nt.links.new(tr.outputs["BSDF"], mx.inputs[1])
    nt.links.new(bk.outputs["BSDF"], mx.inputs[2])
    nt.links.new(mx.outputs["Shader"], out.inputs["Surface"])
    bpy.ops.mesh.primitive_plane_add(size=0.62)
    cs = bpy.context.active_object
    cs.name = "ContactShadow"
    cs.location = (0, -0.01, floor_z + 0.0015)
    cs.data.materials.append(sm)
    cam = bpy.data.cameras.new("Cam")
    cam.lens = 85
    co = bpy.data.objects.new("Cam", cam)
    bpy.context.collection.objects.link(co)
    sc.camera = co
    return co


def set_camera(co, az=0, el=6, dist=3.6, tz=0.52, tx=0, ty=0):
    a, e = math.radians(az), math.radians(el)
    co.location = (tx + dist * math.cos(e) * math.sin(a), ty - dist * math.cos(e) * math.cos(a), tz + dist * math.sin(e))
    v = Vector((tx, ty, tz)) - co.location
    co.rotation_euler = v.to_track_quat("-Z", "Y").to_euler()


def build(nivel="bach"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cream = fabric("Cream", "#E7DACA")
    navy = fabric("Navy", "#1C2A47", 0.2, 200)
    screen = material("Screen", "#030409", 0.3, **{"Coat Weight": 0.35, "Coat Roughness": 0.25, "Specular IOR Level": 0.3})
    eye = glow("Eye", "#C9E4FF", 7.0)
    acc = glow("Accent", ACC[nivel], 3.0)
    body = build_body(cream)
    head, scr, rim, collar = build_head(cream, screen)
    e1, e2 = build_eyes(eye)
    halos = [bpy.data.objects[n] for n in e1["halos"]]
    pack = build_pack(navy, cream, acc, nivel)
    rig = build_rig()
    skin_to_rig(body, rig, [(head, "head"), (scr, "head"), (rim, "head"), (collar, "neck"), (e1, "head"), (e2, "head")] + [(h, "head") for h in halos] + [(p, "chest") for p in pack])
    mz = min(v.co.z for v in body.data.vertices)
    N = dict(rig=rig, body=body, eyes=(e1, e2), floor_z=mz)
    return N


# ---------------------------------------------------------------- poses y expresiones
def expr(N, name=None, v=1.0):
    kb = N["eyes"][0].data.shape_keys.key_blocks
    for k in kb:
        if k.name != "Basis":
            k.value = 0.0
    if name:
        kb[name].value = v


def reset_pose(N):
    rig = N["rig"]
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)


def place(N, name, p):
    from mathutils import Matrix
    b = N["rig"].pose.bones[name]
    m = b.matrix.copy()
    m.translation = Vector(p)
    b.matrix = m
    bpy.context.view_layer.update()


def pose(N, nombre):
    reset_pose(N)
    bpy.context.view_layer.update()
    rig = N["rig"]
    activate(rig)
    bpy.ops.object.mode_set(mode="POSE")
    if nombre == "señala":
        place(N, "IK_hand.L", (0.40, -0.23, 0.66)); place(N, "pole_elbow.L", (0.40, 0.18, 0.40))
        place(N, "IK_hand.R", (-0.13, -0.13, 0.33)); place(N, "pole_elbow.R", (-0.30, 0.15, 0.36))
        pb(N, "head").rotation_euler = (0, 0, math.radians(-14)); pb(N, "spine").rotation_euler = (0, 0, math.radians(8))
    elif nombre == "lanza":
        place(N, "IK_hand.R", (-0.26, 0.17, 0.60)); place(N, "pole_elbow.R", (-0.40, 0.25, 0.30))
        place(N, "IK_hand.L", (0.27, -0.26, 0.48)); place(N, "pole_elbow.L", (0.38, 0.0, 0.30))
        pb(N, "spine").rotation_euler = (0, 0, math.radians(-18)); pb(N, "hips").rotation_euler = (math.radians(-6), 0, 0)
        pb(N, "head").rotation_euler = (math.radians(10), 0, math.radians(14))
    elif nombre == "piensa":
        place(N, "IK_hand.R", (-0.07, -0.21, 0.575)); place(N, "pole_elbow.R", (-0.30, 0.0, 0.30))
        place(N, "IK_hand.L", (0.16, -0.14, 0.34)); place(N, "pole_elbow.L", (0.28, 0.15, 0.36))
        pb(N, "head").rotation_euler = (math.radians(8), 0, math.radians(10))
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()


def idle(N, frames=96):
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end = 1, frames
    sc.render.fps = 24
    rig = N["rig"]
    activate(rig)
    bpy.ops.object.mode_set(mode="POSE")
    reset_pose(N)
    for f in range(1, frames + 1, frames // 4):
        ph = (f - 1) / frames * 2 * math.pi
        sc.frame_set(f)
        h = rig.pose.bones["hips"]
        h.location = (0, 0, 0.006 * math.sin(ph))
        h.keyframe_insert("location")
        c = rig.pose.bones["chest"]
        c.rotation_euler = (0.03 * math.sin(ph), 0, 0)
        c.keyframe_insert("rotation_euler")
        hd = rig.pose.bones["head"]
        hd.rotation_euler = (0.02 * math.sin(ph + 1), 0, 0.07 * math.sin(ph))
        hd.keyframe_insert("rotation_euler")
    sc.frame_set(1)
    bpy.ops.object.mode_set(mode="OBJECT")
    kb = N["eyes"][0].data.shape_keys.key_blocks["Tranquilo"]
    for f, v in ((1, 0), (48, 0), (51, 1), (54, 0), (frames, 0)):
        kb.value = v
        kb.keyframe_insert("value", frame=f)
    for fc in rig.animation_data.action.fcurves if hasattr(rig.animation_data.action, "fcurves") else []:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
    sc.frame_set(1)


def pb(N, name):
    return N["rig"].pose.bones[name]


if __name__ == "__main__":
    nivel = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else "bach"
    N = build(nivel)
    cam = studio(floor_z=N['floor_z'])
    set_camera(cam)
    bpy.ops.wm.save_as_mainfile(filepath="/home/claude/nexo/nexo.blend")
    print("OK")
