"""Nexo v3 · modelo definitivo a partir de las hojas de referencia (Blender 5.x, bpy).

Cambios frente a v2:
- Cara con forma de escudo redondeado (superelipse más ancha que alta y algo más estrecha abajo),
  que sobresale un poco de la capucha. Ya no es un círculo.
- Pantalla negra satinada (brillo suave, no espejo) y ojos gruesos con halo contenido (glare del compositor).
- Capucha grande y mullida con pico blando hacia atrás y reborde acolchado que sigue el contorno de la cara.
- Cuerpo de felpa (metaballs): tronco en pera, piernas cortas, botas con suela, manos con dedos cortos.
- Mochila acolchada con bolsillo, asa, emblema del nivel y correas pegadas al cuerpo.
- Expresiones como shape keys (mismo sistema que la guía): Feliz, Tranquilo, Sorpresa, Pensativo, Concentrado,
  Curioso, Motivado, Entusiasmado (estrellas), Parpadeo.

Uso:
    python3 nexo/nexo3.py                 # nivel bach -> nexo/nexo.blend y nexo/nexo.glb
    python3 nexo/nexo3.py -- eso          # otro nivel: eso | bach | uni | avanzado
    python3 nexo/nexo3.py -- bach --render   # además, renders de revisión en nexo/renders/
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: I001  (bpy antes que bmesh)
import bmesh
from mathutils import Matrix, Vector
from mathutils import noise as mnoise
from mathutils.bvhtree import BVHTree

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "brand"))
from brand import C, linear  # noqa: E402

NX = C["nexo"]
NIVELES = {"eso": "eso", "bach": "bachillerato", "uni": "universidad", "avanzado": "avanzado"}
EXPRESIONES = ["Feliz", "Tranquilo", "Sorpresa", "Pensativo", "Concentrado", "Curioso",
               "Motivado", "Entusiasmado", "Parpadeo"]

# ---------------------------------------------------------------- medidas (m) · Z arriba, mira hacia -Y
# Mide ~1.04 m: la capucha ocupa casi la mitad de la altura, como en la referencia.
J = {
    "pelvis": (0, 0, 0.29), "spine": (0, 0, 0.37), "chest": (0, 0, 0.44), "neck": (0, 0, 0.50),
    "shoulder": (0.14, 0, 0.455), "elbow": (0.225, -0.01, 0.37), "wrist": (0.255, -0.03, 0.29),
    "hand": (0.265, -0.045, 0.215),
    "hip": (0.07, 0, 0.255), "knee": (0.07, -0.012, 0.185), "ankle": (0.072, 0, 0.11), "toe": (0.074, -0.1, 0.035),
}
HEAD_C = Vector((0, 0.012, 0.745))     # centro de la capucha
HEAD_R = Vector((0.272, 0.255, 0.258))  # semiejes de la capucha
PEAK = Vector((0, 0.74, 0.67)).normalized()  # dirección del pico (arriba y atrás)
FACE_Z, FACE_A, FACE_B, FACE_N = 0.738, 0.19, 0.157, 3.0  # contorno de la cara (superelipse)
EYE_X, EYE_Z = 0.08, FACE_Z + 0.014   # posición de los ojos
EYE_W, EYE_H = 0.031, 0.041            # semiejes del ojo neutro (antes de EYE_S)
EYE_S = 1.22                           # escala de todos los dibujos de ojos


def P(k, s=1):
    x, y, z = J[k]
    return Vector((x * s, y, z))


# ---------------------------------------------------------------- utilidades
def to_obj(name, data, mat=None):
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    if mat is not None and hasattr(data, "materials"):
        data.materials.append(mat)
    return ob


def bm_obj(name, bm, mat=None):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    return to_obj(name, me, mat)


def activate(ob):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob


def smooth(ob):
    for p in ob.data.polygons:
        p.use_smooth = True


def subsurf(ob, levels=1, render=2):
    m = ob.modifiers.new("Subsurf", "SUBSURF")
    m.levels, m.render_levels = levels, render
    return m


def apply_all(ob):
    activate(ob)
    for m in list(ob.modifiers):
        bpy.ops.object.modifier_apply(modifier=m.name)


def ellipsoid(name, c, r, mat, seg=48, rings=32):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings, radius=1.0)
    bmesh.ops.scale(bm, vec=r, verts=bm.verts)
    bmesh.ops.translate(bm, vec=c, verts=bm.verts)
    ob = bm_obj(name, bm, mat)
    smooth(ob)
    return ob


def bvh_of(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    bm = bmesh.new()
    bm.from_object(ob, dg)
    bm.transform(ob.matrix_world)
    t = BVHTree.FromBMesh(bm)
    bm.free()
    return t


def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def seg_param(p, a, b):
    """(t, distancia, punto más cercano) de p al segmento a-b."""
    ab = b - a
    t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
    q = a + ab * t
    return t, (p - q).length, q


def angle_around(p, q, axis, ref=Vector((0, -1, 0))):
    """Ángulo de p alrededor del eje (q, axis); 0 = lado de ref (delante)."""
    r = ref - axis * axis.dot(ref)
    r.normalize()
    v = p - q
    return math.atan2(axis.cross(r).dot(v), r.dot(v))


def catmull(pts, n):
    """Curva suave que pasa por pts, con n muestras."""
    pts = [Vector(p) for p in pts]
    ext = [pts[0] * 2 - pts[1]] + pts + [pts[-1] * 2 - pts[-2]]
    out = []
    segs = len(pts) - 1
    for k in range(n):
        u = k / (n - 1) * segs
        i = min(int(u), segs - 1)
        t = u - i
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    return out


# ---------------------------------------------------------------- materiales
def principled(name, hexa, rough=0.8, **kw):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = linear(hexa)
    b.inputs["Roughness"].default_value = rough
    for k, v in kw.items():
        b.inputs[k].default_value = v
    return m


def felpa(name, hexa, hexa2, bump=0.3, grano=320, arrugas=0.12):
    """Tela de felpa: color con manchas suaves, grano fino, arrugas grandes muy suaves y sheen."""
    m = principled(name, hexa, 0.92, **{"Sheen Weight": 0.75, "Sheen Roughness": 0.4,
                                         "Subsurface Weight": 0.1, "Subsurface Radius": (0.9, 0.6, 0.4),
                                         "Subsurface Scale": 0.01})
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexCoord")
    fino = nt.nodes.new("ShaderNodeTexNoise")
    fino.inputs["Scale"].default_value = grano
    fino.inputs["Detail"].default_value = 10
    manchas = nt.nodes.new("ShaderNodeTexNoise")
    manchas.inputs["Scale"].default_value = 7
    manchas.inputs["Detail"].default_value = 3
    plieg = nt.nodes.new("ShaderNodeTexNoise")
    plieg.inputs["Scale"].default_value = 9
    plieg.inputs["Detail"].default_value = 2
    for n in (fino, manchas, plieg):
        nt.links.new(tc.outputs["Object"], n.inputs["Vector"])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = linear(hexa)
    mix.inputs["B"].default_value = linear(hexa2)
    ra = nt.nodes.new("ShaderNodeMapRange")
    ra.inputs["From Min"].default_value = 0.35
    ra.inputs["From Max"].default_value = 0.68
    ra.inputs["To Max"].default_value = 0.4
    nt.links.new(manchas.outputs["Fac"], ra.inputs["Value"])
    nt.links.new(ra.outputs["Result"], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    b1 = nt.nodes.new("ShaderNodeBump")
    b1.inputs["Strength"].default_value = bump
    b1.inputs["Distance"].default_value = 0.002
    b2 = nt.nodes.new("ShaderNodeBump")
    b2.inputs["Strength"].default_value = arrugas
    b2.inputs["Distance"].default_value = 0.02
    nt.links.new(fino.outputs["Fac"], b1.inputs["Height"])
    nt.links.new(plieg.outputs["Fac"], b2.inputs["Height"])
    nt.links.new(b2.outputs["Normal"], b1.inputs["Normal"])
    nt.links.new(b1.outputs["Normal"], b.inputs["Normal"])
    return m


def brillo(name, hexa, fuerza):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs["Color"].default_value = linear(hexa)
    e.inputs["Strength"].default_value = fuerza
    o = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(e.outputs["Emission"], o.inputs["Surface"])
    return m


def materiales(nivel):
    return dict(
        crema=felpa("Crema", NX["crema"], NX["crema_sombra"]),
        ribete=felpa("Ribete", NX["crema"], NX["crema_sombra"], 0.35, 380, 0.05),
        suela=principled("Suela", NX["suela"], 0.7, **{"Sheen Weight": 0.3}),
        marino=felpa("Marino", NX["marino"], NX["marino"], 0.3, 260, 0.06),
        pantalla=principled("Pantalla", NX["pantalla"], 0.5, **{
            "Coat Weight": 0.55, "Coat Roughness": 0.12, "Specular IOR Level": 0.2}),
        ojo=brillo("Ojo", NX["ojo"], 5.0),
        acento=brillo("Acento", C["nivel"][NIVELES[nivel]]["relleno"], 2.2),
    )


# ---------------------------------------------------------------- capucha, cara y ojos
def contorno(t):
    """Punto (x, z) del borde de la cara para el ángulo t."""
    c, s = math.cos(t), math.sin(t)
    x = FACE_A * math.copysign(abs(c) ** (2 / FACE_N), c)
    z = FACE_B * math.copysign(abs(s) ** (2 / FACE_N), s)
    if z < 0:
        x *= 1 - 0.1 * (-z / FACE_B) ** 2  # algo más estrecha abajo: forma de escudo
    return x, FACE_Z + z


def forma_capucha(p):
    x, y, z = p
    q = Vector((x * (1 + 0.08 * max(0.0, -z)), y, z))  # se abre sobre los hombros
    caida = max(0.0, -z - 0.4)  # la tela de abajo se posa sobre los hombros
    q.x *= 1 + 0.55 * caida
    q.y *= 1 + 0.2 * caida
    q.z -= 0.18 * caida
    if y > 0 and z < 0:
        q.z -= 0.22 * y * (-z)  # la nuca cae hacia la espalda
    g = math.exp(-(Vector(p).angle(PEAK) / 0.4) ** 2)
    q += PEAK * 0.3 * g          # pico blando...
    q.y += 0.14 * g ** 3         # ...cuya punta se dobla hacia atrás
    q.z -= 0.05 * g ** 3
    q.x *= 1 - 0.15 * g
    q.y -= 0.05 * max(0.0, -y) * max(0.0, z)  # frente algo más llena
    return HEAD_C + Vector((q.x * HEAD_R.x, q.y * HEAD_R.y, q.z * HEAD_R.z))


def build_hood(m):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=96, v_segments=64, radius=1.0)
    for v in bm.verts:
        v.co = forma_capucha(v.co.normalized())
    pliegues_capucha(bm)
    hood = bm_obj("NexoHead", bm, m["crema"])
    smooth(hood)
    subsurf(hood, 1, 1)
    return hood


def pliegues_capucha(bm):
    """Tela, no carcasa: bultos suaves, pliegues que salen del borde de la cara y frunces en la nuca."""
    bm.normal_update()
    for v in bm.verts:
        p, n = v.co.copy(), v.normal.copy()
        d = 0.007 * mnoise.noise(p * 6.0) + 0.002 * mnoise.noise(p * 24.0)
        xn, zn = p.x / FACE_A, (p.z - FACE_Z) / FACE_B
        if p.y < HEAD_C.y:
            rho = (abs(xn) ** FACE_N + abs(zn) ** FACE_N) ** (1 / FACE_N)
            t = math.atan2(zn, xn)
            w = math.exp(-((rho - 1.32) / 0.28) ** 2) * min(1.0, (HEAD_C.y - p.y) / 0.1)
            d += 0.0075 * w * math.sin(9 * t + 2.8 * mnoise.noise(p * 5.0))
        rz = (p.z - HEAD_C.z) / HEAD_R.z
        if p.y > HEAD_C.y - 0.05:
            w = smoothstep(-0.15, -0.65, rz) * smoothstep(HEAD_C.y - 0.05, HEAD_C.y + 0.1, p.y)
            d += 0.006 * w * math.sin(p.z * 150 + 3.5 * mnoise.noise(p * 7.0))
        v.co = p + n * d


def build_face(m, hood):
    """Pantalla (cúpula con contorno de escudo) y reborde acolchado de la capucha."""
    tree = bvh_of(hood)

    def hood_hit(x, z):
        hit = tree.ray_cast(Vector((x, -2.0, z)), Vector((0, 1, 0)))
        if hit[0] is None:
            return Vector((x, HEAD_C.y - HEAD_R.y, z)), Vector((0, -1, 0))
        return hit[0], hit[1]

    def hood_y(x, z):
        return hood_hit(x, z)[0].y

    K, S = 128, 30
    edge = []
    for i in range(K):
        t = 2 * math.pi * i / K
        x, z = contorno(t)
        edge.append((x, z, hood_y(x, z)))
    y_front = hood_y(0, FACE_Z) - 0.028  # la cara sobresale un poco de la capucha

    # pantalla
    bm = bmesh.new()
    center = bm.verts.new((0, y_front, FACE_Z))
    rings = []
    for j in range(1, S + 1):
        s = (j / S) ** 0.8
        row = []
        for i in range(K):
            x, z, ye = edge[i]
            px, pz = x * s, FACE_Z + (z - FACE_Z) * s
            ye_in = ye + 0.012
            y = ye_in + (y_front - ye_in) * (1 - s * s) ** 0.5
            y = min(y, hood_y(px, pz) - 0.004)  # siempre por delante de la capucha
            row.append(bm.verts.new((px, y, pz)))
        rings.append(row)
    for i in range(K):
        bm.faces.new((center, rings[0][i], rings[0][(i + 1) % K]))
    for j in range(S - 1):
        a, b = rings[j], rings[j + 1]
        for i in range(K):
            bm.faces.new((a[i], b[i], b[(i + 1) % K], a[(i + 1) % K]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    screen = bm_obj("NexoScreen", bm, m["pantalla"])
    smooth(screen)
    if screen.data.polygons[0].normal.y > 0:  # que mire hacia delante
        activate(screen)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.flip_normals()
        bpy.ops.object.mode_set(mode="OBJECT")

    # reborde: tubo acolchado que sigue el contorno sobre la superficie de la capucha, más grueso arriba
    bm = bmesh.new()
    T = 16
    hits = [hood_hit(e[0], e[1]) for e in edge]
    grid = []
    for i in range(K):
        t = 2 * math.pi * i / K
        p, nh = hits[i]
        tan = (hits[(i + 1) % K][0] - hits[i - 1][0]).normalized()
        o = tan.cross(nh).normalized()  # hacia fuera de la cara, tangente a la capucha
        if o.dot(Vector((p.x, 0, p.z - FACE_Z))) < 0:
            o = -o
        r = 0.03 + 0.008 * max(0.0, math.sin(t))
        c = p - nh * 0.004 + o * (r * 0.25)
        row = []
        for j in range(T):
            b = 2 * math.pi * j / T
            row.append(bm.verts.new(c + o * (r * math.cos(b)) + nh * (r * 1.0 * math.sin(b))))
        grid.append(row)
    for i in range(K):
        for j in range(T):
            bm.faces.new((grid[i][j], grid[(i + 1) % K][j], grid[(i + 1) % K][(j + 1) % T], grid[i][(j + 1) % T]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    rim = bm_obj("NexoRim", bm, m["crema"])
    smooth(rim)
    subsurf(rim, 1, 2)
    return screen, rim


def _oval(x, w, h, dz=0.0):
    k = math.sqrt(max(0.0, 1 - x * x))
    return (w * x, dz + h * k), (w * x, dz - h * k)


def _arco(u, R, T, a0, a1, dz, k=1.0, interior_arriba=False):
    a = a0 + (a1 - a0) * u
    t = T * (0.45 + 0.55 * math.sin(math.pi * u) ** 0.5)
    ro, ri = R + t / 2, R - t / 2
    po = (ro * math.cos(a), dz + ro * math.sin(a) * k)
    pi_ = (ri * math.cos(a), dz + ri * math.sin(a) * k)
    return (pi_, po) if interior_arriba else (po, pi_)


EYE_M = 40


def _eye_shapes():
    """Para cada expresión, listas (arriba, abajo) de EYE_M puntos (x, z) del ojo izquierdo."""
    xs = [-math.cos(math.pi * i / (EYE_M - 1)) for i in range(EYE_M)]
    us = [i / (EYE_M - 1) for i in range(EYE_M)]
    w, h = EYE_W, EYE_H
    sh = {}
    sh["Basis"] = [_oval(x, w, h) for x in xs]
    sh["Feliz"] = [_arco(u, 0.033, 0.014, math.pi - 0.22, 0.22, -0.013) for u in us]
    sh["Tranquilo"] = [_arco(u, 0.035, 0.0095, math.pi + 0.3, 2 * math.pi - 0.3, 0.012, 0.6, True) for u in us]
    sh["Motivado"] = [((w * 1.12 * x, 0.004 - 0.003 * x * x), (w * 1.12 * x, 0.004 - h * 0.78 * math.sqrt(1 - x * x)))
                      for x in xs]
    sh["Sorpresa"] = [_oval(x, w * 1.22, h * 1.24) for x in xs]
    sh["Curioso"] = [_oval(x, w * 1.06, h * 1.12, 0.004) for x in xs]

    def lid(x, z0, slope, hh=0.9):
        top, bot = _oval(x, w, h * hh)
        return ((top[0], max(min(top[1], z0 + slope * x * w), bot[1] + 0.0015)), bot)
    sh["Concentrado"] = [lid(x, 0.006, 0.45) for x in xs]          # párpado bajando hacia dentro
    sh["Pensativo"] = [lid(x, 0.012, -0.5, 0.95) for x in xs]       # párpado inclinado al revés
    sh["Parpadeo"] = [_oval(x, w * 1.05, 0.0028) for x in xs]
    sh["Entusiasmado"] = [((0.0002 * x, 0.0), (0.0002 * x, 0.0)) for x in xs]  # el ojo da paso a la estrella
    return sh


def _project(screen_tree, wx, wz, lift=0.0022):
    hit = screen_tree.ray_cast(Vector((wx, -2.0, wz)), Vector((0, 1, 0)))
    return (hit[0].y if hit[0] else -0.3) - lift


def _shape_mesh(name, n_verts_fn, faces):
    me = bpy.data.meshes.new(name)
    me.from_pydata(n_verts_fn, [], faces)
    me.update()
    return me


def build_eyes(m, screen):
    """Ojos: cinta de 2 x EYE_M vértices con shape keys. El derecho comparte malla (escala X = -1).
    Pupilas y estrellas: mallas aparte cuyas shape keys siguen a las del ojo mediante drivers."""
    tree = bvh_of(screen)
    base = Vector((EYE_X, 0, EYE_Z))
    oy = _project(tree, EYE_X, EYE_Z)

    def to3(pts, lift=0.0018):
        pts = [(x * EYE_S, z * EYE_S) for x, z in pts]
        return [(x, _project(tree, EYE_X + x, EYE_Z + z, lift) - oy, z) for x, z in pts]

    shapes = _eye_shapes()

    rows = 6  # filas entre el borde de arriba y el de abajo, para que el ojo se ciña a la pantalla curva

    def flat(pairs):
        out = []
        for k in range(rows + 1):
            f = k / rows
            out += [(a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f) for a, b in pairs]
        return out
    faces = [(k * EYE_M + i, k * EYE_M + i + 1, (k + 1) * EYE_M + i + 1, (k + 1) * EYE_M + i)
             for k in range(rows) for i in range(EYE_M - 1)]
    me = _shape_mesh("NexoEyeMesh", to3(flat(shapes["Basis"])), faces)
    eyeL = to_obj("NexoEyeL", me, m["ojo"])
    eyeL.shape_key_add(name="Basis")
    for name in EXPRESIONES:
        k = eyeL.shape_key_add(name=name)
        for i, co in enumerate(to3(flat(shapes[name]))):
            k.data[i].co = co
        k.slider_min, k.slider_max = 0.0, 1.0
    eyeR = to_obj("NexoEyeR", me)
    eyeL.location = base + Vector((0, oy, 0))
    eyeR.location = Vector((-EYE_X, oy, EYE_Z))
    eyeR.scale.x = -1

    # pupila: disco oscuro, recogido en Basis; visible con Sorpresa o Curioso
    N = 32
    pc = (0.004, 0.004)
    full = [pc] + [(pc[0] + 0.0155 * math.cos(2 * math.pi * i / N), pc[1] + 0.017 * math.sin(2 * math.pi * i / N))
                   for i in range(N)]
    fan = [(0, 1 + i, 1 + (i + 1) % N) for i in range(N)]
    pme = _shape_mesh("NexoPupilMesh", to3([pc] * (N + 1), 0.004), fan)
    pupL = to_obj("NexoPupilL", pme, m["pantalla"])
    pupL.shape_key_add(name="Basis")
    kp = pupL.shape_key_add(name="Pupila")
    for i, co in enumerate(to3(full, 0.004)):
        kp.data[i].co = co
    pupR = to_obj("NexoPupilR", pme)
    pupL.location, pupR.location, pupR.scale.x = eyeL.location, eyeR.location, -1

    # estrella (Entusiasmado)
    N = 10
    star = [(0.0, -0.002)] + [((0.037 if i % 2 == 0 else 0.016) * math.cos(math.pi / 2 + i * math.pi / 5),
                               -0.002 + (0.037 if i % 2 == 0 else 0.016) * math.sin(math.pi / 2 + i * math.pi / 5))
                              for i in range(N)]
    fan = [(0, 1 + i, 1 + (i + 1) % N) for i in range(N)]
    sme = _shape_mesh("NexoStarMesh", to3([star[0]] * (N + 1)), fan)
    starL = to_obj("NexoStarL", sme, m["ojo"])
    starL.shape_key_add(name="Basis")
    ks = starL.shape_key_add(name="Entusiasmado")
    for i, co in enumerate(to3(star)):
        ks.data[i].co = co
    starR = to_obj("NexoStarR", sme)
    starL.location, starR.location, starR.scale.x = eyeL.location, eyeR.location, -1

    keys = me.shape_keys

    def driver(target_key, expr, *names):
        d = target_key.driver_add("value").driver
        d.type = "SCRIPTED"
        for i, n in enumerate(names):
            v = d.variables.new()
            v.name = "abcdef"[i]
            v.targets[0].id_type = "KEY"
            v.targets[0].id = keys
            v.targets[0].data_path = f'key_blocks["{n}"].value'
        d.expression = expr
    driver(kp, "max(a, b)", "Sorpresa", "Curioso")
    driver(ks, "a", "Entusiasmado")
    for o in (eyeL, eyeR, pupL, pupR, starL, starR):
        o.visible_shadow = False
    return [eyeL, eyeR, pupL, pupR, starL, starR]


# ---------------------------------------------------------------- cuerpo
MB_K = 0.575  # radio de superficie / radio del elemento (rigidez 2, umbral 0.6)


def metaball(name, elems, res=0.006):
    mb = bpy.data.metaballs.new(name)
    mb.resolution = mb.render_resolution = res
    mb.threshold = 0.6
    for e in elems:
        kind = e[0]
        el = mb.elements.new(type=kind)
        el.stiffness = 2.0
        if kind == "CAPSULE":
            a, b, r = Vector(e[1]), Vector(e[2]), e[3]
            el.co = (a + b) / 2
            el.size_x = (b - a).length / 2
            el.rotation = Vector((1, 0, 0)).rotation_difference(b - a)
            el.radius = r / MB_K
        elif kind == "ELLIPSOID":
            el.co, el.radius = e[1], e[2] / MB_K
            el.size_x, el.size_y, el.size_z = e[3]
        else:
            el.co, el.radius = e[1], e[2] / MB_K
    ob = to_obj(name, mb)
    activate(ob)
    bpy.ops.object.convert(target="MESH")
    return bpy.context.view_layer.objects.active


def build_body(m):
    parts = [metaball("NexoTorsoMB", [
        ("ELLIPSOID", (0, -0.004, 0.325), 0.148, (1.0, 0.84, 0.82)),
        ("ELLIPSOID", (0, 0.004, 0.425), 0.128, (1.02, 0.88, 0.8)),
        ("BALL", (0, 0.01, 0.5), 0.06),
    ])]
    for s, sf in ((1, "L"), (-1, "R")):
        parts.append(metaball(f"NexoLegMB{sf}", [("CAPSULE", P("hip", s), P("ankle", s) + Vector((0, 0, 0.01)), 0.064)]))
        parts.append(metaball(f"NexoArmMB{sf}", [
            ("CAPSULE", P("shoulder", s), P("elbow", s), 0.055),
            ("CAPSULE", P("elbow", s), P("wrist", s), 0.05),
        ]))
    body = parts[0]
    activate(body)
    for p in parts[1:]:
        p.select_set(True)
    bpy.ops.object.join()
    body.name = body.data.name = "NexoBody"
    r = body.modifiers.new("Remesh", "REMESH")
    r.mode, r.voxel_size = "VOXEL", 0.0045
    c = body.modifiers.new("Suave", "CORRECTIVE_SMOOTH")
    c.iterations, c.use_only_smooth = 12, True
    apply_all(body)
    arrugas_ropa(body)
    d = body.modifiers.new("Decimate", "DECIMATE")
    d.ratio = 0.45
    apply_all(body)
    body.data.materials.clear()
    body.data.materials.append(m["crema"])
    smooth(body)
    return body


def arrugas_ropa(body):
    """Pliegues de sudadera y pantalón: codos, rodillas, tela amontonada en muñecas y tobillos, cintura."""
    me = body.data
    tau = 2 * math.pi
    for v in me.vertices:
        p, n = v.co.copy(), v.normal.copy()
        d = 0.0025 * mnoise.noise(p * 9.0) + 0.001 * mnoise.noise(p * 30.0)
        for s in (1, -1):
            sh, el, wr = P("shoulder", s), P("elbow", s), P("wrist", s)
            t1, d1, q1 = seg_param(p, sh, el)
            t2, d2, q2 = seg_param(p, el, wr)
            if min(d1, d2) < 0.08 and abs(p.x) > 0.13:
                u = t1 * 0.5 if d1 < d2 else 0.5 + t2 * 0.5   # 0 hombro, 0.5 codo, 1 muñeca
                axis = (el - sh).normalized() if d1 < d2 else (wr - el).normalized()
                ang = angle_around(p, q1 if d1 < d2 else q2, axis)
                wob = 1.0 * mnoise.noise(p * 14.0)
                w = math.exp(-((u - 0.52) / 0.12) ** 2)
                d += 0.005 * w * (0.35 + 0.65 * max(0.0, math.cos(ang))) * math.sin(tau * u * 8 + 1.2 * math.sin(2 * ang + s) + wob)
                w = smoothstep(0.7, 0.93, u)
                d += 0.0055 * w * math.sin(tau * u * 15 + 1.4 * math.sin(3 * ang + 1.7 * s) + wob)
                w = math.exp(-((u - 0.12) / 0.08) ** 2) * max(0.0, -math.cos(ang - s * 1.2))
                d += 0.003 * w * math.sin(tau * u * 10 + wob)  # axila
            hp, an = P("hip", s), P("ankle", s)
            t, dd, q = seg_param(p, hp, an)
            if dd < 0.09 and p.z < 0.25:
                ang = angle_around(p, q, (an - hp).normalized())
                wob = 1.0 * mnoise.noise(p * 12.0 + Vector((3, 0, 0)))
                w = smoothstep(0.62, 0.92, t)
                d += 0.006 * w * math.sin(tau * t * 11 + 1.5 * math.sin(3 * ang + s) + wob)
                w = math.exp(-((t - 0.47) / 0.12) ** 2) * (0.3 + 0.7 * max(0.0, -math.cos(ang)))
                d += 0.004 * w * math.sin(tau * t * 8 + 0.8 * math.sin(2 * ang) + wob)
        if 0.25 < p.z < 0.48 and abs(p.x) < 0.17:  # tronco
            w = math.exp(-((p.z - 0.3) / 0.035) ** 2)
            d += 0.003 * w * math.sin(p.z * 240 + 5 * mnoise.noise(p * 6.0))
            w = math.exp(-((p.z - 0.43) / 0.04) ** 2) * smoothstep(0.06, 0.13, abs(p.x))
            d += 0.0035 * w * math.sin((p.z - 0.6 * abs(p.x)) * 200 + 3 * mnoise.noise(p * 5.0))
        v.co = p + n * d


def build_hand(s, m):
    """Mano sencilla: palma redonda, cuatro dedos cortos casi unidos y pulgar hacia delante."""
    elems = [("ELLIPSOID", (0, 0, -0.034), 0.036, (0.62, 1.0, 1.05))]
    for i, y in enumerate((-0.021, -0.007, 0.007, 0.021)):
        extra = 0.006 if i in (1, 2) else 0.0
        elems.append(("CAPSULE", (0, y, -0.06), (0.002, y, -0.078 - extra), 0.0125))
    elems.append(("CAPSULE", (-0.008 * s, -0.03, -0.032), (-0.016 * s, -0.047, -0.052), 0.0125))
    ob = metaball(f"NexoHandMB{'L' if s > 0 else 'R'}", elems, 0.0035)
    ob.name = ob.data.name = f"NexoHand{'L' if s > 0 else 'R'}"
    w = P("wrist", s)
    d = (P("hand", s) - w).normalized()
    q = Vector((0, 0, -1)).rotation_difference(d)
    ob.matrix_world = Matrix.Translation(w + d * 0.004) @ q.to_matrix().to_4x4()
    activate(ob)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    ob.data.materials.clear()
    ob.data.materials.append(m["crema"])
    smooth(ob)
    return ob


def band(name, center, axis, radius, minor, mat, ph=0.0):
    """Puño o dobladillo de tela: grosor y altura irregulares, no un anillo perfecto."""
    bm = bmesh.new()
    seg, tube = 56, 14
    grid = []
    for i in range(seg):
        a = 2 * math.pi * i / seg
        k = 1 + 0.28 * math.sin(3 * a + ph) + 0.12 * math.sin(7 * a + 2 * ph)
        dz = minor * 0.35 * math.sin(2 * a + 1.3 * ph)
        row = []
        for j in range(tube):
            b = 2 * math.pi * j / tube
            rr = radius + minor * k * math.cos(b)
            row.append(bm.verts.new((rr * math.cos(a), rr * math.sin(a), dz + minor * k * 1.3 * math.sin(b))))
        grid.append(row)
    for i in range(seg):
        for j in range(tube):
            bm.faces.new((grid[i][j], grid[(i + 1) % seg][j], grid[(i + 1) % seg][(j + 1) % tube], grid[i][(j + 1) % tube]))
    q = Vector((0, 0, 1)).rotation_difference(Vector(axis).normalized())
    bm.transform(Matrix.Translation(center) @ q.to_matrix().to_4x4())
    ob = bm_obj(name, bm, mat)
    smooth(ob)
    return ob


def build_feet(m):
    out = []
    for s, sf in ((1, "L"), (-1, "R")):
        c = Vector((0.072 * s, -0.03, 0.06))
        boot = ellipsoid(f"NexoBoot{sf}", c, (0.068, 0.102, 0.058), m["crema"])
        sole = ellipsoid(f"NexoSole{sf}", Vector((c.x, c.y - 0.003, 0.022)), (0.071, 0.106, 0.022), m["suela"])
        for v in sole.data.vertices:
            v.co.z = max(v.co.z, 0.0)
        for v in boot.data.vertices:
            v.co.z = max(v.co.z, 0.018)
        cuff = band(f"NexoCuffA{sf}", Vector((0.072 * s, -0.004, 0.118)), (0, 0, 1), 0.058, 0.014, m["ribete"], 1 + s)
        out.append((f"foot.{sf}", boot))
        out.append((f"foot.{sf}", sole))
        out.append((f"shin.{sf}", cuff))
    return out


# ---------------------------------------------------------------- prendas de la sudadera
def tube(name, pts, radius, mat):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth, cu.bevel_resolution, cu.resolution_u = radius, 4, 12
    sp = cu.splines.new("NURBS")
    sp.points.add(len(pts) - 1)
    for pt, co in zip(sp.points, pts):
        pt.co = (*co, 1)
    sp.use_endpoint_u, sp.order_u = True, 3
    cu.use_fill_caps = True
    ob = to_obj(name, cu, mat)
    activate(ob)
    bpy.ops.object.convert(target="MESH")
    ob = bpy.context.view_layer.objects.active
    smooth(ob)
    return ob


def build_ropa(m, body, hood):
    """Detalles que dicen «ropa»: dobladillo de la sudadera, bolsillo canguro y cordones de la capucha."""
    tree = bvh_of(body)
    out = []
    # dobladillo: sigue el contorno del cuerpo a la altura de la cadera
    zc = 0.268
    bm = bmesh.new()
    K, T = 72, 12
    grid = []
    for i in range(K):
        a = 2 * math.pi * i / K
        o = Vector((0, 0, zc + 0.004 * math.sin(3 * a)))  # desde dentro: el primer choque es el tronco, no los brazos
        loc, nor, _, _ = tree.ray_cast(o, Vector((math.cos(a), math.sin(a), 0)))
        if nor is not None and nor.dot(Vector((math.cos(a), math.sin(a), 0))) < 0:
            nor = -nor
        if loc is None:
            loc, nor = Vector((0.15 * math.cos(a), 0.12 * math.sin(a), zc)), Vector((math.cos(a), math.sin(a), 0))
        r = 0.011 * (1 + 0.25 * mnoise.noise(loc * 20))
        c = loc + nor * (r * 0.5)
        row = []
        for j in range(T):
            b = 2 * math.pi * j / T
            row.append(bm.verts.new(c + nor * (r * math.cos(b)) + Vector((0, 0, 1.4 * r * math.sin(b)))))
        grid.append(row)
    for i in range(K):
        for j in range(T):
            bm.faces.new((grid[i][j], grid[(i + 1) % K][j], grid[(i + 1) % K][(j + 1) % T], grid[i][(j + 1) % T]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    hem = bm_obj("NexoHem", bm, m["ribete"])
    smooth(hem)
    subsurf(hem, 1, 2)
    out.append(("hips", hem))

    # bolsillo canguro: parche de tela sobre la tripa, más ancho abajo
    bm = bmesh.new()
    U, W = 18, 9
    rows = []
    for j in range(W + 1):
        w = j / W
        row = []
        for i in range(U + 1):
            u = -1 + 2 * i / U
            half = 0.062 + 0.026 * w
            x = u * half
            z = 0.372 - w * 0.07 + 0.004 * (1 - u * u) * w
            loc, nor, _, _ = tree.ray_cast(Vector((x, -1.0, z)), Vector((0, 1, 0)))
            puff = 0.005 + 0.004 * (1 - u * u) * math.sin(math.pi * w)
            row.append(bm.verts.new(loc + nor * puff))
        rows.append(row)
    for j in range(W):
        for i in range(U):
            bm.faces.new((rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    pocket = bm_obj("NexoPocket", bm, m["crema"])
    if pocket.data.polygons[0].normal.y > 0:
        for poly in pocket.data.polygons:
            poly.flip()
    so = pocket.modifiers.new("Grosor", "SOLIDIFY")
    so.thickness, so.offset = 0.004, -1
    subsurf(pocket, 1, 2)
    smooth(pocket)
    out.append(("spine", pocket))

    # cordones: salen de la capucha bajo la cara y caen sobre el pecho
    htree = bvh_of(hood)
    for s, sf in ((1, "L"), (-1, "R")):
        x0 = 0.055 * s
        z0 = FACE_Z - FACE_B - 0.045
        hit = htree.ray_cast(Vector((x0, -1.0, z0)), Vector((0, 1, 0)))
        start = (hit[0] if hit[0] else Vector((x0, -0.2, z0))) + Vector((0, -0.004, 0))
        pts = [start]
        for k, z in enumerate((0.47, 0.43, 0.395)):
            xx = x0 * (1.0 + 0.08 * k) + 0.004 * s * k
            loc, nor, _, _ = tree.find_nearest(Vector((xx, -0.2, z)))
            pts.append(loc + nor * 0.008)
        cord = tube(f"NexoCord{sf}", [tuple(p) for p in pts], 0.0052, m["ribete"])
        tip = ellipsoid(f"NexoCordTip{sf}", pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.008,
                        (0.0075, 0.0075, 0.013), m["marino"], 16, 10)
        out += [("chest", cord), ("chest", tip)]
    return out


# ---------------------------------------------------------------- mochila
def soft_box(name, c, half, mat, bevel, puff=0.0, cuts=6):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    for v in bm.verts:
        x, y, z = v.co
        if y > 0.99 and puff:
            v.co.y += puff * (1 - x * x) * (1 - z * z) / max(half[1], 1e-6)
        v.co = Vector((v.co.x * half[0], v.co.y * half[1], v.co.z * half[2])) + Vector(c)
    ob = bm_obj(name, bm, mat)
    b = ob.modifiers.new("Bevel", "BEVEL")
    b.width, b.segments, b.limit_method, b.angle_limit = bevel, 4, "ANGLE", math.radians(35)
    subsurf(ob, 1, 2)
    smooth(ob)
    return ob


def ribbon(name, pts, normals, width, thick, mat):
    bm = bmesh.new()
    rows = []
    for i, (p, n) in enumerate(zip(pts, normals)):
        tan = (pts[min(i + 1, len(pts) - 1)] - pts[max(i - 1, 0)]).normalized()
        side = tan.cross(n).normalized() * (width / 2)
        rows.append((bm.verts.new(p - side), bm.verts.new(p + side)))
    for i in range(len(rows) - 1):
        a, b = rows[i], rows[i + 1]
        bm.faces.new((a[0], a[1], b[1], b[0]))
    ob = bm_obj(name, bm, mat)
    so = ob.modifiers.new("Grosor", "SOLIDIFY")
    so.thickness, so.offset = thick, 1.0
    subsurf(ob, 1, 2)
    smooth(ob)
    return ob


def build_pack(m, body):
    tree = bvh_of(body)
    hit = tree.ray_cast(Vector((0, 1.0, 0.375)), Vector((0, -1, 0)))
    back_y = hit[0].y
    py = back_y + 0.05
    objs = [soft_box("NexoPack", (0, py, 0.37), (0.13, 0.052, 0.15), m["marino"], 0.035, 0.014)]
    objs.append(soft_box("NexoPackPocket", (0, py + 0.064, 0.3), (0.1, 0.018, 0.068), m["marino"], 0.014, 0.007, 4))
    objs.append(soft_box("NexoPackFlap", (0, py + 0.08, 0.36), (0.104, 0.007, 0.016), m["marino"], 0.005, 0.0, 2))
    # asa superior
    angs = [math.pi * k / 20 for k in range(21)]
    pts = [Vector((0.04 * math.cos(a), py, 0.51 + 0.032 * math.sin(a))) for a in angs]
    nors = [Vector((math.cos(a), 0, math.sin(a))) for a in angs]
    objs.append(ribbon("NexoPackHandle", pts, nors, 0.016, 0.008, m["marino"]))
    # emblema: triángulo hueco con trazo central, en el color del nivel
    pack_tree = bvh_of(objs[0])
    ez = 0.445
    eh = pack_tree.ray_cast(Vector((0, 1.0, ez)), Vector((0, -1, 0)))
    ey = eh[0].y + 0.002
    bm = bmesh.new()

    def tri(r):
        return [bm.verts.new((r * math.sin(a), ey, ez + r * math.cos(a)))
                for a in (0, 2 * math.pi / 3, 4 * math.pi / 3)]
    o, i_ = tri(0.034), tri(0.024)
    for k in range(3):
        bm.faces.new((o[k], o[(k + 1) % 3], i_[(k + 1) % 3], i_[k]))
    q = [bm.verts.new((dx, ey, ez + dz)) for dx, dz in ((-0.0035, -0.012), (0.0035, -0.012), (0.0035, 0.018), (-0.0035, 0.018))]
    bm.faces.new(q)
    emb = bm_obj("NexoEmblem", bm, m["acento"])
    so = emb.modifiers.new("Grosor", "SOLIDIFY")
    so.thickness = 0.003
    objs.append(emb)

    # correas: siguen la superficie del cuerpo (de la mochila, por el hombro, al pecho y de vuelta por el costado)
    for s, sf in ((1, "L"), (-1, "R")):
        guide = [(0.07 * s, back_y + 0.01, 0.47), (0.085 * s, 0.06, 0.53), (0.09 * s, -0.05, 0.52),
                 (0.088 * s, -0.11, 0.45), (0.094 * s, -0.12, 0.37), (0.112 * s, -0.095, 0.3),
                 (0.14 * s, 0.0, 0.285), (0.1 * s, back_y + 0.005, 0.3)]
        pts, nors = [], []
        for p in catmull(guide, 90):
            loc, nor, _, _ = tree.find_nearest(p)
            pts.append(loc + nor * 0.006)
            nors.append(nor)
        objs.append(ribbon(f"NexoStrap{sf}", pts, nors, 0.034, 0.008, m["marino"]))
    return objs


# ---------------------------------------------------------------- esqueleto
def build_rig():
    arm = bpy.data.armatures.new("NexoRig")
    rig = to_obj("NexoRig", arm)
    rig.show_in_front = True
    activate(rig)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones

    def bone(name, head, tail, parent=None, deform=True):
        b = eb.new(name)
        b.head, b.tail = Vector(head), Vector(tail)
        b.use_deform = deform
        if parent:
            b.parent = eb[parent]
        return b

    bone("root", (0, 0, 0), (0, 0, 0.08), deform=False)
    bone("hips", P("pelvis"), P("spine"), "root")
    bone("spine", P("spine"), P("chest"), "hips")
    bone("chest", P("chest"), P("neck"), "spine")
    bone("neck", P("neck"), (0, 0, 0.56), "chest")
    bone("head", (0, 0, 0.56), (0, 0, 1.06), "neck")
    for s, sf in ((1, "L"), (-1, "R")):
        bone(f"clavicle.{sf}", (0.03 * s, 0, 0.47), P("shoulder", s), "chest")
        bone(f"upper_arm.{sf}", P("shoulder", s), P("elbow", s), f"clavicle.{sf}")
        bone(f"forearm.{sf}", P("elbow", s), P("wrist", s), f"upper_arm.{sf}")
        bone(f"hand.{sf}", P("wrist", s), P("hand", s), f"forearm.{sf}")
        bone(f"thigh.{sf}", P("hip", s), P("knee", s), "hips")
        bone(f"shin.{sf}", P("knee", s), P("ankle", s), f"thigh.{sf}")
        bone(f"foot.{sf}", P("ankle", s), P("toe", s), f"shin.{sf}")
        w, a = P("wrist", s), P("ankle", s)
        bone(f"IK_hand.{sf}", w, w - Vector((0, 0, 0.05)), "root", deform=False)
        bone(f"IK_foot.{sf}", a, P("toe", s), "root", deform=False)  # misma orientación que el pie
        bone(f"pole_elbow.{sf}", (0.28 * s, 0.17, 0.37), (0.28 * s, 0.17, 0.41), "root", deform=False)
        bone(f"pole_knee.{sf}", (0.07 * s, -0.32, 0.19), (0.07 * s, -0.32, 0.23), "root", deform=False)
    bpy.ops.object.mode_set(mode="POSE")
    for sf in ("L", "R"):
        c = rig.pose.bones[f"forearm.{sf}"].constraints.new("IK")
        c.target, c.subtarget = rig, f"IK_hand.{sf}"
        c.pole_target, c.pole_subtarget = rig, f"pole_elbow.{sf}"
        c.pole_angle, c.chain_count = math.radians(-90), 2
        c = rig.pose.bones[f"shin.{sf}"].constraints.new("IK")
        c.target, c.subtarget = rig, f"IK_foot.{sf}"
        c.pole_target, c.pole_subtarget = rig, f"pole_knee.{sf}"
        c.pole_angle, c.chain_count = math.radians(-90), 2
        c = rig.pose.bones[f"foot.{sf}"].constraints.new("COPY_ROTATION")
        c.target, c.subtarget = rig, f"IK_foot.{sf}"
        c = rig.pose.bones[f"hand.{sf}"].constraints.new("COPY_ROTATION")
        c.target, c.subtarget = rig, f"IK_hand.{sf}"
        c.mix_mode, c.target_space, c.owner_space = "BEFORE", "LOCAL", "LOCAL"
    bpy.ops.object.mode_set(mode="OBJECT")
    calibrate_poles(rig)
    for b in arm.bones:
        if b.name.startswith("IK_"):
            b.color.palette = "THEME04"
        elif b.name.startswith("pole_"):
            b.color.palette = "THEME03"
    return rig


def calibrate_poles(rig):
    """Elige el pole_angle de cada IK que deja la pose de reposo intacta."""
    for owner in ("forearm.L", "forearm.R", "shin.L", "shin.R"):
        c = rig.pose.bones[owner].constraints["IK"]
        chain = [owner, rig.pose.bones[owner].parent.name]
        best = None
        for deg in range(-180, 181, 5):
            c.pole_angle = math.radians(deg)
            bpy.context.view_layer.update()
            err = 0.0
            for n in chain:
                pbn, rest = rig.pose.bones[n], rig.data.bones[n]
                err += (pbn.tail - rest.tail_local).length + (pbn.head - rest.head_local).length
                err += sum(abs(a - b) for ra, rb in zip(pbn.matrix.to_3x3(), rest.matrix_local.to_3x3())
                           for a, b in zip(ra, rb)) * 0.01
            if best is None or err < best[0]:
                best = (err, deg)
        c.pole_angle = math.radians(best[1])
    bpy.context.view_layer.update()


def skin(body, rig, rigid):
    activate(body)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    for bone, ob in rigid:
        vg = ob.vertex_groups.new(name=bone)
        vg.add(list(range(len(ob.data.vertices))), 1.0, "REPLACE")
        mod = ob.modifiers.new("Armature", "ARMATURE")
        mod.object = rig
        mw = ob.matrix_world.copy()
        ob.parent = rig
        ob.matrix_world = mw


# ---------------------------------------------------------------- escena
def studio():
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    w = bpy.data.worlds.new("Mundo")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = linear(C["fondo"]["base"])
    bg.inputs["Strength"].default_value = 0.55
    bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=10)
    floor = bm_obj("Floor", bm, principled("Suelo", C["fondo"]["alt"], 0.95))

    def area(name, loc, energy, size, hexa, target=(0, 0, 0.55)):
        d = bpy.data.lights.new(name, "AREA")
        d.energy, d.size, d.color = energy, size, linear(hexa)[:3]
        o = to_obj(name, d)
        o.location = loc
        o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        return o
    area("Key", (-1.5, -2.0, 2.3), 150, 2.2, C["fondo"]["superficie"])
    area("Fill", (2.2, -1.4, 1.1), 45, 2.6, C["fondo"]["base"])
    area("Rim", (0.6, 2.2, 1.9), 110, 1.4, C["fondo"]["superficie"])
    # brillo suave de los ojos (funciona igual en Cycles y en Eevee)
    ng = bpy.data.node_groups.new("Composicion", "CompositorNodeTree")
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    rl = ng.nodes.new("CompositorNodeRLayers")
    gl = ng.nodes.new("CompositorNodeGlare")
    gl.inputs["Type"].default_value = "Bloom"
    gl.inputs["Quality"].default_value = "High"
    gl.inputs["Threshold"].default_value = 1.2
    gl.inputs["Strength"].default_value = 0.55
    gl.inputs["Size"].default_value = 0.45
    out = ng.nodes.new("NodeGroupOutput")
    ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
    ng.links.new(gl.outputs["Image"], out.inputs[0])
    sc.compositing_node_group = ng
    sc.render.use_compositing = True
    if hasattr(sc.render, "compositor_device"):
        sc.render.compositor_device = "CPU"
    cam = to_obj("Cam", bpy.data.cameras.new("Cam"))
    cam.data.lens = 85
    sc.camera = cam
    return cam, floor


def set_camera(co, az=0, el=6, dist=3.6, tz=0.55, tx=0, ty=0):
    a, e = math.radians(az), math.radians(el)
    co.location = (tx + dist * math.cos(e) * math.sin(a), ty - dist * math.cos(e) * math.cos(a), tz + dist * math.sin(e))
    co.rotation_euler = (Vector((tx, ty, tz)) - co.location).to_track_quat("-Z", "Y").to_euler()


# ---------------------------------------------------------------- construcción
def build(nivel="bach"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    m = materiales(nivel)
    body = build_body(m)
    hood = build_hood(m)
    screen, rim = build_face(m, hood)
    eyes = build_eyes(m, screen)
    hands = [build_hand(1, m), build_hand(-1, m)]
    feet = build_feet(m)
    cuffs = []
    for s, sf in ((1, "L"), (-1, "R")):
        w, e = P("wrist", s), P("elbow", s)
        d = (w - e).normalized()
        cuffs.append((f"forearm.{sf}", band(f"NexoCuffW{sf}", w - d * 0.012, d, 0.043, 0.012, m["ribete"], 2 - s)))
    ropa = build_ropa(m, body, hood)
    pack = build_pack(m, body)
    rig = build_rig()
    rigid = [("head", o) for o in [hood, screen, rim] + eyes]
    rigid += [("hand.L", hands[0]), ("hand.R", hands[1])] + feet + cuffs + ropa + [("chest", o) for o in pack]
    skin(body, rig, rigid)
    col = bpy.data.collections.new("Nexo")
    sc.collection.children.link(col)
    for o in [rig, body, hood, screen, rim, *eyes, *hands, *[o for _, o in feet], *[o for _, o in cuffs], *[o for _, o in ropa], *pack]:
        sc.collection.objects.unlink(o)
        col.objects.link(o)
    return dict(rig=rig, body=body, eyes=eyes, col=col, nivel=nivel)


# ---------------------------------------------------------------- expresiones, poses y animación
def expr(N, name=None, v=1.0):
    kb = N["eyes"][0].data.shape_keys.key_blocks
    for k in kb:
        if k.name != "Basis":
            k.value = 0.0
    if name:
        kb[name].value = v
    bpy.context.view_layer.update()


def pb(N, name):
    return N["rig"].pose.bones[name]


def reset_pose(N):
    for b in N["rig"].pose.bones:
        b.location = (0, 0, 0)
        b.rotation_mode = "XYZ"
        b.rotation_euler = (0, 0, 0)
        b.scale = (1, 1, 1)
    bpy.context.view_layer.update()


def place(N, name, p):
    b = pb(N, name)
    mtx = b.matrix.copy()
    mtx.translation = Vector(p)
    b.matrix = mtx
    bpy.context.view_layer.update()


def pose(N, nombre):
    """Poses de ejemplo: relajado (la de por defecto), señala, lanza, piensa, saluda."""
    reset_pose(N)
    activate(N["rig"])
    bpy.ops.object.mode_set(mode="POSE")
    r = math.radians
    if nombre == "relajado":
        relajar(N)
    elif nombre == "señala":
        place(N, "IK_hand.L", (0.42, -0.2, 0.62)); place(N, "pole_elbow.L", (0.42, 0.2, 0.38))
        pb(N, "head").rotation_euler = (0, 0, r(-12)); pb(N, "spine").rotation_euler = (0, 0, r(6))
    elif nombre == "lanza":
        place(N, "IK_hand.R", (-0.27, 0.15, 0.62)); place(N, "pole_elbow.R", (-0.42, 0.25, 0.3))
        place(N, "IK_hand.L", (0.28, -0.25, 0.47)); place(N, "pole_elbow.L", (0.4, 0.0, 0.3))
        pb(N, "spine").rotation_euler = (0, 0, r(-16)); pb(N, "head").rotation_euler = (r(8), 0, r(12))
    elif nombre == "piensa":
        place(N, "IK_hand.R", (-0.12, -0.2, 0.52)); place(N, "pole_elbow.R", (-0.3, 0.05, 0.3))
        pb(N, "head").rotation_euler = (r(6), r(-8), r(10))
    elif nombre == "saluda":
        place(N, "IK_hand.L", (0.33, -0.08, 0.66)); place(N, "pole_elbow.L", (0.45, 0.15, 0.32))
        pb(N, "head").rotation_euler = (0, r(6), r(-6))
    bpy.ops.object.mode_set(mode="OBJECT")
    bpy.context.view_layer.update()


def relajar(N, fase=0.0):
    """Brazos sueltos y algo doblados, peso en una pierna, cabeza ladeada: nada de pose de maniquí."""
    r = math.radians
    place(N, "IK_hand.L", (0.218, -0.05, 0.278 + 0.004 * math.sin(fase)))
    place(N, "pole_elbow.L", (0.26, 0.3, 0.38))
    place(N, "IK_hand.R", (-0.214, -0.03, 0.282 + 0.004 * math.sin(fase + 1)))
    place(N, "pole_elbow.R", (-0.26, 0.3, 0.38))
    pb(N, "IK_hand.L").rotation_euler = (r(-4), 0, r(6))
    pb(N, "IK_hand.R").rotation_euler = (r(-3), 0, r(-8))
    pb(N, "hips").rotation_euler = (0, r(2.5), r(-3))
    pb(N, "spine").rotation_euler = (r(2), r(-2), r(2))
    pb(N, "chest").rotation_euler = (r(3), r(-1.5), r(2))
    pb(N, "head").rotation_euler = (r(-3), r(5), r(-6))
    bpy.context.view_layer.update()


def idle(N, frames=96):
    """Respira, mueve un poco la cabeza y parpadea una vez."""
    sc = bpy.context.scene
    sc.frame_start, sc.frame_end, sc.render.fps = 1, frames, 24
    rig = N["rig"]
    activate(rig)
    bpy.ops.object.mode_set(mode="POSE")
    reset_pose(N)
    for f in range(1, frames + 1, frames // 4):
        ph = (f - 1) / frames * 2 * math.pi
        relajar(N, ph)
        for n in ("IK_hand.L", "IK_hand.R"):
            pb(N, n).keyframe_insert("location", frame=f)
            pb(N, n).keyframe_insert("rotation_euler", frame=f)
        pb(N, "hips").location = (0, 0, 0.005 * math.sin(ph))
        pb(N, "hips").keyframe_insert("location", frame=f)
        pb(N, "chest").rotation_euler = (math.radians(3) + 0.025 * math.sin(ph), 0, math.radians(2))
        pb(N, "chest").keyframe_insert("rotation_euler", frame=f)
        pb(N, "head").rotation_euler = (math.radians(-3) + 0.02 * math.sin(ph + 1), math.radians(5), math.radians(-6) + 0.06 * math.sin(ph))
        pb(N, "head").keyframe_insert("rotation_euler", frame=f)
    bpy.ops.object.mode_set(mode="OBJECT")
    kb = N["eyes"][0].data.shape_keys.key_blocks["Parpadeo"]
    for f, v in ((1, 0), (60, 0), (63, 1), (66, 0), (frames, 0)):
        kb.value = v
        kb.keyframe_insert("value", frame=f)
    sc.frame_set(1)


# ---------------------------------------------------------------- salida
def export_glb(N, path):
    activate(N["rig"])
    for o in N["col"].objects:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True, export_apply=True,
                              export_skins=True, export_morph=True, export_animations=False, export_yup=True)


def render_review(N, cam, out):
    out.mkdir(exist_ok=True)
    sc = bpy.context.scene
    sc.render.resolution_x, sc.render.resolution_y = 800, 900
    sc.cycles.samples = 40
    vistas = {"frente": 0, "tres_cuartos": -32, "lateral": 90, "espalda": 180}
    pose(N, "relajado")
    expr(N, "Feliz")
    for n, az in vistas.items():
        set_camera(cam, az, 6, 3.7, 0.53)
        sc.render.filepath = str(out / f"v3_{n}.png")
        bpy.ops.render.render(write_still=True)
    sc.render.resolution_x = sc.render.resolution_y = 420
    sc.cycles.samples = 28
    for name in EXPRESIONES:
        expr(N, name)
        set_camera(cam, -14, 4, 1.75, 0.74)
        sc.render.filepath = str(out / "expresiones" / f"{name}.png")
        bpy.ops.render.render(write_still=True)
    expr(N, "Curioso")
    pose(N, "señala")
    sc.render.resolution_x, sc.render.resolution_y = 800, 900
    sc.cycles.samples = 40
    set_camera(cam, -24, 6, 3.7, 0.55)
    sc.render.filepath = str(out / "v3_pose_senala.png")
    bpy.ops.render.render(write_still=True)
    reset_pose(N)
    expr(N)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    nivel = next((a for a in args if a in NIVELES), "bach")
    N = build(nivel)
    cam, _ = studio()
    set_camera(cam)
    export_glb(N, AQUI / "nexo.glb")
    if "--render" in args or "--quick" in args:
        if "--quick" in args:
            sc = bpy.context.scene
            sc.render.resolution_x, sc.render.resolution_y = 500, 560
            sc.cycles.samples = 16
            pose(N, "relajado")
            expr(N, "Feliz")
            for n, az in {"frente": 0, "tres_cuartos": -32, "lateral": 90, "espalda": 180}.items():
                set_camera(cam, az, 6, 3.7, 0.53)
                sc.render.filepath = str(AQUI / "renders" / f"q_{n}.png")
                bpy.ops.render.render(write_still=True)
        else:
            render_review(N, cam, AQUI / "renders")
    idle(N)
    bpy.ops.wm.save_as_mainfile(filepath=str(AQUI / "nexo.blend"))
    print("OK", nivel)
