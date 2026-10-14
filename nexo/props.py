"""Biblioteca de props de Nexo: objetos reutilizables en el mismo estilo (formas suaves, colores de tokens.json).

Cada prop es una función  nombre(m, **params) -> objeto raíz, registrada con @prop.
Convenciones (las usa nexo/acciones.py):
  - Unidades en metros, Z arriba. Nexo mide ~1,04 m: un prop de mano mide 5-15 cm.
  - El origen del objeto raíz es su punto de agarre (o el centro de la base si va en el suelo/mesa).
  - ob["agarre"] = "mano" | "suelo" | "mesa";  ob["radio"] = radio aproximado (para colocarlo en la palma).
  - ob["altura_superficie"] (mesa, pizarra...) = altura de la superficie de trabajo.
  - Opcionales: ob["sep_mano"] = distancia palma-origen al llevarlo (si no, radio + 1,2 cm) y ob["desp_mano"] = [x hacia
    el interior, y, z] ajuste extra en la mano;
    ob["semialto"] = distancia del origen a la base (para dejarlo apoyado: acción colocar);
    ob["pantalla"] = [ancho, alto, z del centro, (x del centro)] de una superficie donde el editor incrusta 2D
    (mira a -Y) y ob["pantalla_objeto"] = nombre del objeto de esa superficie.
Añadir uno nuevo: escribe la función, regístrala con @prop y ejecuta  python nexo/props.py --catalogo
(o usa /nuevo-prop). Ver .claude/skills/nexo-actor/SKILL.md.
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: I001
import bmesh
from mathutils import Matrix, Vector

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
from omnia.marca import C, color, nivel_color  # noqa: E402

PROPS = {}


def prop(agarre="mano", descripcion="", usos=()):
    def deco(fn):
        PROPS[fn.__name__] = dict(fn=fn, agarre=agarre, descripcion=descripcion, usos=list(usos))
        return fn
    return deco


# ---------------------------------------------------------------- materiales del estilo
def _lin(hexa):
    h = hexa.lstrip("#")
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4  # noqa: E731
    return tuple(f(int(h[i:i + 2], 16) / 255) for i in (0, 2, 4)) + (1.0,)


def mat(nombre, ruta_o_hex, rough=0.55, metal=0.0, emision=0.0, transm=0.0):
    """Material del estilo de props: plástico mate suave. Se reutiliza si ya existe."""
    key = f"P_{nombre}"
    if key in bpy.data.materials:
        return bpy.data.materials[key]
    hexa = ruta_o_hex if ruta_o_hex.startswith("#") else color(ruta_o_hex)
    m = bpy.data.materials.new(key)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = _lin(hexa)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    b.inputs["Coat Weight"].default_value = 0.15
    if transm:
        b.inputs["Transmission Weight"].default_value = transm
    if emision:
        b.inputs["Emission Color"].default_value = _lin(hexa)
        b.inputs["Emission Strength"].default_value = emision
    return m


# ---------------------------------------------------------------- utilidades de modelado
def _obj(nombre, bm, material=None, suave=True):
    me = bpy.data.meshes.new(nombre)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(ob)
    if material:
        me.materials.append(material)
    if suave:
        for p in me.polygons:
            p.use_smooth = True
    return ob


def _caja(nombre, tam, centro=(0, 0, 0), material=None, bisel=0.01, seg=3):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=tam, verts=bm.verts)
    bmesh.ops.translate(bm, vec=centro, verts=bm.verts)
    ob = _obj(nombre, bm, material)
    if bisel:
        b = ob.modifiers.new("Bisel", "BEVEL")
        b.width, b.segments, b.limit_method = bisel, seg, "NONE"
    return ob


def _esfera(nombre, r, centro=(0, 0, 0), material=None, escala=(1, 1, 1), seg=32):
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r)
    bmesh.ops.scale(bm, vec=escala, verts=bm.verts)
    bmesh.ops.translate(bm, vec=centro, verts=bm.verts)
    return _obj(nombre, bm, material)


def _cilindro(nombre, r, h, centro=(0, 0, 0), material=None, seg=40, r2=None, eje="Z", bisel=0.004, tapas=True):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=tapas, segments=seg, radius1=r, radius2=r if r2 is None else r2, depth=h)
    if eje != "Z":
        ang = {"X": (math.pi / 2, "Y"), "Y": (math.pi / 2, "X")}[eje]
        bmesh.ops.rotate(bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(ang[0], 3, ang[1]))
    bmesh.ops.translate(bm, vec=centro, verts=bm.verts)
    ob = _obj(nombre, bm, material)
    if bisel:
        b = ob.modifiers.new("Bisel", "BEVEL")
        b.width, b.segments, b.limit_method, b.angle_limit = bisel, 3, "ANGLE", math.radians(40)
    return ob


def _grupo(nombre, hijos, **meta):
    """Raíz vacía con los hijos colgando (el origen de la raíz es el punto de agarre)."""
    raiz = bpy.data.objects.new(nombre, None)
    raiz.empty_display_type = "PLAIN_AXES"
    raiz.empty_display_size = 0.05
    bpy.context.scene.collection.objects.link(raiz)
    for h in hijos:
        h.parent = raiz
    for k, v in meta.items():
        raiz[k] = v
    return raiz


# ---------------------------------------------------------------- props
@prop("mano", "Pelota blanda con franjas del nivel", ["lanzar", "parábolas", "gravedad", "física"])
def pelota(m=None, nivel="eso", r=0.055):
    base = _esfera("Pelota", r, material=mat("blanco", "fondo.superficie", 0.6))
    franja = _cilindro("PelotaFranja", r * 1.012, r * 0.3, material=mat(f"nivel_{nivel}", nivel_color(nivel)), r2=r * 1.012,
                       tapas=False, bisel=0)
    sol = franja.modifiers.new("Grosor", "SOLIDIFY")
    sol.thickness = 0.002
    franja.rotation_euler = (math.pi / 2, 0, 0.6)
    return _grupo("pelota", [base, franja], agarre="mano", radio=r)


@prop("mano", "Dado de seis caras con puntos marino", ["probabilidad", "estadística", "azar"])
def dado(m=None, lado=0.08):
    cubo = _caja("Dado", (lado,) * 3, material=mat("blanco", "fondo.superficie", 0.4), bisel=lado * 0.18, seg=4)
    puntos = []
    pip = mat("marino", "nexo.marino", 0.4)
    caras = {  # normal, puntos en coordenadas de la cara (u, v) en [-1, 1]
        (0, 0, 1): [(0, 0)], (0, 0, -1): [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)],
        (1, 0, 0): [(-1, -1), (1, 1)], (-1, 0, 0): [(-1, -1), (0, 0), (1, 1)],
        (0, 1, 0): [(-1, -1), (-1, 1), (1, -1), (1, 1)], (0, -1, 0): [(-1, -1), (-1, 1), (0, 0), (1, -1), (1, 1)]}
    for n, pts in caras.items():
        n = Vector(n)
        u = Vector((0, 1, 0)) if abs(n.y) < 0.5 else Vector((1, 0, 0))
        v = n.cross(u)
        for a, b in pts:
            c = n * lado / 2 + (u * a + v * b) * lado * 0.27
            puntos.append(_esfera("DadoPunto", lado * 0.085, centro=c, material=pip, escala=(1, 1, 1), seg=12))
    return _grupo("dado", [cubo] + puntos, agarre="mano", radio=lado * 0.6)


@prop("suelo", "Pizarra con caballete; la superficie es una pantalla donde el editor incrusta 2D", ["explicar", "escribir", "fórmulas"])
def pizarra(m=None, ancho=1.2, alto=0.8):
    marco = mat("madera", "#C9A27A", 0.6)
    tabla = _caja("PizarraTabla", (ancho, 0.03, alto), centro=(0, 0, 0.32 + alto / 2), material=mat("marino", "nexo.marino", 0.7), bisel=0.01)
    borde = _caja("PizarraBorde", (ancho + 0.06, 0.04, alto + 0.06), centro=(0, 0.006, 0.32 + alto / 2), material=marco, bisel=0.012)
    patas = [_cilindro(f"PizarraPata{i}", 0.018, 0.36, centro=(x, 0.02, 0.18), material=marco) for i, x in enumerate((-ancho / 2 + 0.08, ancho / 2 - 0.08))]
    bandeja = _caja("PizarraBandeja", (ancho * 0.8, 0.07, 0.02), centro=(0, -0.04, 0.32), material=marco, bisel=0.006)
    g = _grupo("pizarra", [borde, tabla, bandeja] + patas, agarre="suelo", radio=ancho / 2,
               altura_superficie=0.32 + alto / 2)
    g["pantalla"] = [ancho, alto, 0.32 + alto / 2]  # ancho, alto y altura del centro de la zona de escritura
    return g


@prop("mesa", "Portátil abierto con el triángulo de Nexo en la tapa", ["programación", "datos", "investigar"])
def portatil(m=None, ancho=0.32):
    gris = mat("aluminio", "#B9BCC4", 0.35, 0.6)
    base = _caja("PortatilBase", (ancho, ancho * 0.68, 0.016), centro=(0, 0, 0.008), material=gris, bisel=0.004)
    teclado = _caja("PortatilTeclado", (ancho * 0.85, ancho * 0.3, 0.003), centro=(0, ancho * 0.08, 0.0165), material=mat("marino", "nexo.marino", 0.7), bisel=0.001)
    tapa = _caja("PortatilTapa", (ancho, 0.01, ancho * 0.64), centro=(0, ancho * 0.34 + 0.02, ancho * 0.32 + 0.01), material=gris, bisel=0.004)
    tapa.rotation_euler = (math.radians(-12), 0, 0)
    pantalla = _caja("PortatilPantalla", (ancho * 0.9, 0.002, ancho * 0.54), centro=(0, ancho * 0.34 + 0.014, ancho * 0.32 + 0.01), material=mat("pantalla", "nexo.pantalla", 0.2, emision=0.6), bisel=0)
    pantalla.rotation_euler = tapa.rotation_euler
    return _grupo("portatil", [base, teclado, tapa, pantalla], agarre="mesa", radio=ancho / 2)


@prop("mano", "Libro de tapa marino", ["estudiar", "leer", "historia de la ciencia"])
def libro(m=None):
    tapa = _caja("LibroTapa", (0.17, 0.035, 0.23), material=mat("marino", "nexo.marino", 0.7), bisel=0.004)
    hojas = _caja("LibroHojas", (0.16, 0.031, 0.222), centro=(0.006, 0, 0), material=mat("papel", "fondo.superficie", 0.9), bisel=0.002)
    return _grupo("libro", [tapa, hojas], agarre="mano", radio=0.1)


@prop("suelo", "Balanza de dos platos; params: inclinacion (-1 a 1)", ["ecuaciones", "igualdad", "equilibrio", "masa"])
def balanza(m=None, inclinacion=0.0):
    met = mat("laton", "#C9A85C", 0.35, 0.8)
    base = _cilindro("BalanzaBase", 0.12, 0.03, centro=(0, 0, 0.015), material=met)
    poste = _cilindro("BalanzaPoste", 0.015, 0.45, centro=(0, 0, 0.255), material=met)
    brazo = _caja("BalanzaBrazo", (0.6, 0.02, 0.02), centro=(0, 0, 0.48), material=met, bisel=0.005)
    ang = math.radians(12) * inclinacion
    brazo.rotation_euler = (0, ang, 0)
    hijos = [base, poste, brazo]
    for s in (-1, 1):
        x = s * 0.29 * math.cos(ang)
        z = 0.48 - s * 0.29 * math.sin(ang)
        plato = _cilindro(f"BalanzaPlato{s}", 0.11, 0.012, centro=(x, 0, z - 0.16), material=met, r2=0.09)
        for k in range(3):
            a = 2 * math.pi * k / 3
            p0 = Vector((x, 0, z))
            p1 = Vector((x + 0.09 * math.cos(a), 0.09 * math.sin(a), z - 0.155))
            hilo = _cilindro(f"BalanzaHilo{s}{k}", 0.002, (p1 - p0).length, centro=(p0 + p1) / 2, material=met, bisel=0)
            hilo.rotation_mode = "QUATERNION"
            hilo.rotation_quaternion = Vector((0, 0, 1)).rotation_difference(p1 - p0)
            hijos.append(hilo)
        hijos.append(plato)
    return _grupo("balanza", hijos, agarre="suelo", radio=0.35)


def _cubitos(nombre, n, lado, material, holgura=0.06):
    """Malla con n = (nx, ny, nz) cubitos biselados de `lado` (separados por una ranura fina), centrada en el origen.
    Solo se generan los cubitos de la superficie y un núcleo tapa las ranuras por dentro."""
    nx, ny, nz = n
    plantilla = bmesh.new()
    bmesh.ops.create_cube(plantilla, size=lado * (1 - holgura))
    bmesh.ops.bevel(plantilla, geom=list(plantilla.edges) + list(plantilla.verts), offset=lado * 0.12, segments=2,
                    affect="EDGES", profile=0.5)
    v0 = [v.co.copy() for v in plantilla.verts]
    f0 = [[v.index for v in f.verts] for f in plantilla.faces]
    plantilla.free()
    verts, caras = [], []
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                if 0 < i < nx - 1 and 0 < j < ny - 1 and 0 < k < nz - 1:
                    continue  # interior: no se ve
                c = Vector(((i - (nx - 1) / 2) * lado, (j - (ny - 1) / 2) * lado, (k - (nz - 1) / 2) * lado))
                base = len(verts)
                verts += [v + c for v in v0]
                caras += [[base + x for x in f] for f in f0]
    me = bpy.data.meshes.new(nombre)
    me.from_pydata([tuple(v) for v in verts], [], caras)
    me.materials.append(material)
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(nombre, me)
    bpy.context.scene.collection.objects.link(ob)
    nucleo = _caja(nombre + "Nucleo", tuple(max(d - 0.3, 0.7) * lado for d in n), material=material, bisel=0)
    return [ob, nucleo]


def _emblema(nombre, r, centro, material):
    """Emblema de Nexo (triángulo hueco con trazo central, como el de la mochila) mirando a +Y."""
    cx, cy, cz = centro
    bm = bmesh.new()

    def tri(rr):
        return [bm.verts.new((cx + rr * math.sin(a), cy, cz + rr * math.cos(a))) for a in (0, 2 * math.pi / 3, 4 * math.pi / 3)]
    o, i_ = tri(r), tri(r * 0.7)
    for k in range(3):
        bm.faces.new((o[k], o[(k + 1) % 3], i_[(k + 1) % 3], i_[k]))
    q = [bm.verts.new((cx + dx * r, cy, cz + dz * r)) for dx, dz in ((-0.1, -0.35), (0.1, -0.35), (0.1, 0.53), (-0.1, 0.53))]
    bm.faces.new(q)
    ob = _obj(nombre, bm, material, suave=False)
    so = ob.modifiers.new("Grosor", "SOLIDIFY")
    so.thickness = 0.0008
    return ob


FORMAS_BLOQUE = {"unidad": (1, 1, 1), "barra": (10, 1, 1), "placa": (10, 10, 1), "cubo_mil": (10, 10, 10)}


@prop("mano", "Bloque de base 10 en color de mates, con cada cubito marcado. params: forma (unidad | barra 10×1×1 | "
      "placa 10×10×1 | cubo_mil 10×10×10), lado (arista del cubito, 2 cm), col (mates.a-d), de_pie (barra vertical o "
      "placa de cara a cámara en vez de tumbada)",
      ["contar", "valor posicional", "base 10", "decimales", "área", "volumen", "álgebra", "apilar"])
def bloque(m=None, lado=0.02, col="mates.a", forma="unidad", de_pie=False):
    if forma not in FORMAS_BLOQUE:
        raise ValueError(f"bloque: forma '{forma}' no existe ({', '.join(FORMAS_BLOQUE)})")
    n = FORMAS_BLOQUE[forma]
    if de_pie:  # la barra se pone vertical y la placa queda en el plano XZ, de cara a cámara (-Y)
        n = {"barra": (1, 1, 10), "placa": (10, 1, 10)}.get(forma, n)
    material = mat(f"bloque_{col}", col, 0.5)
    hijos = _cubitos("Bloque", n, lado, material)
    tam = [d * lado for d in n]
    return _grupo("bloque", hijos, agarre="mano", radio=max(tam) * 0.6, forma=forma, tam=tam,
                  semialto=tam[2] / 2, sep_mano=min(tam) / 2 + 0.012)


@prop("mano", "Teléfono móvil genérico (7×15 cm), marco marino y crema, sin marcas; la pantalla (objeto MovilPantalla) "
      "es una superficie donde el editor incrusta 2D. params: pantalla_encendida, orientacion (vertical | horizontal)",
      ["datos", "porcentajes", "gráficas", "temporizador", "código", "mensajes", "redes"])
def movil(m=None, pantalla_encendida=True, orientacion="vertical", ancho=0.07, alto=0.15, grosor=0.008, nivel="eso"):
    marino = mat("marino", "nexo.marino", 0.45)
    crema = mat("crema", "nexo.crema", 0.5)
    zc = alto * 0.4          # el agarre (origen) queda abajo: la pantalla asoma por encima de los dedos
    cuerpo = _caja("MovilCuerpo", (ancho, grosor, alto), centro=(0, 0, zc), material=marino, bisel=grosor * 0.45, seg=4)
    marco = _caja("MovilMarco", (ancho + 0.0016, grosor * 0.55, alto + 0.0016), centro=(0, 0, zc), material=crema,
                  bisel=grosor * 0.27, seg=3)
    pw, ph = ancho - 0.007, alto - 0.012
    if pantalla_encendida:
        mp = mat("movil_encendida", "fondo.oscuro", 0.25, emision=0.8)
    else:
        mp = mat("movil_apagada", "nexo.pantalla", 0.12)
    pantalla = _caja("MovilPantalla", (pw, 0.0006, ph), centro=(0, -grosor / 2 - 0.0002, zc), material=mp, bisel=0)
    altavoz = _caja("MovilAltavoz", (0.012, 0.0008, 0.0012), centro=(0, -grosor / 2 - 0.0001, zc + alto / 2 - 0.0035),
                    material=crema, bisel=0)
    botones = [_caja("MovilBoton", (0.0016, 0.004, l), centro=(ancho / 2 + 0.0006, 0, zc + z), material=crema, bisel=0.0006)
               for z, l in ((0.035, 0.018), (0.01, 0.01))]
    camara = _caja("MovilCamara", (0.018, 0.0016, 0.018), centro=(-ancho / 2 + 0.014, grosor / 2 + 0.0006, zc + alto / 2 - 0.014),
                   material=crema, bisel=0.004)
    lente = _cilindro("MovilLente", 0.0042, 0.002, centro=(-ancho / 2 + 0.014, grosor / 2 + 0.0016, zc + alto / 2 - 0.014),
                      material=mat("pantalla_vidrio", "nexo.pantalla", 0.1), eje="Y", seg=24, bisel=0)
    tri = _emblema("MovilEmblema", 0.012, (0, grosor / 2 + 0.0003, zc + 0.01), mat(f"nivel_{nivel}", nivel_color(nivel), 0.4, emision=0.3))
    hijos = [cuerpo, marco, pantalla, altavoz, camara, lente, tri] + botones
    ancho_p, alto_p = pw, ph
    if orientacion == "horizontal":  # gira el móvil 90° en el plano de la pantalla (eje Y); el agarre sigue en el origen
        rot = Matrix.Rotation(math.radians(90), 4, "Y")
        for h in hijos:
            h.data.transform(rot)
        ancho_p, alto_p = ph, pw
        centro_p = rot @ Vector((0, 0, zc))
    else:
        centro_p = Vector((0, 0, zc))
    g = _grupo("movil", hijos, agarre="mano", radio=alto * 0.35, sep_mano=0.02, desp_mano=[0.0, -0.025, 0.0], semialto=grosor / 2,
               pantalla_objeto=pantalla.name, orientacion=orientacion, encendida=bool(pantalla_encendida))
    # ancho, alto, altura del centro y desplazamiento lateral (x) del centro, en coordenadas del prop; la cara mira a -Y
    g["pantalla"] = [ancho_p, alto_p, centro_p.z, centro_p.x]
    return g


def _papel_dentado(nombre, ancho, alto, dientes, material, grosor=0.0005):
    """Hoja en el plano XZ (centrada en el origen) con los bordes superior e inferior dentados, como un tique cortado."""
    pts = []
    for k in range(dientes + 1):
        pts.append((-ancho / 2 + ancho * k / dientes, -alto / 2 + (0.0025 if k % 2 else 0)))
    for k in range(dientes, -1, -1):
        pts.append((-ancho / 2 + ancho * k / dientes, alto / 2 - (0.0025 if k % 2 else 0)))
    bm = bmesh.new()
    vs = [bm.verts.new((x, 0, z)) for x, z in pts]
    bm.faces.new(vs)
    bmesh.ops.triangulate(bm, faces=bm.faces[:])
    ob = _obj(nombre, bm, material, suave=False)
    s = ob.modifiers.new("Grosor", "SOLIDIFY")
    s.thickness, s.offset = grosor, 0
    return ob


@prop("mano", "Tique de caja de papel (8×18 cm); la zona de texto (objeto TicketTexto) es una superficie donde el editor "
      "incrusta 2D", ["cuentas", "compras", "precios", "operaciones", "porcentajes", "IVA"])
def ticket(m=None, ancho=0.08, alto=0.18):
    zc = alto * 0.4
    papel = _papel_dentado("TicketPapel", ancho, alto, 16, mat("papel", "fondo.superficie", 0.9))
    papel.location = (0, 0, zc)
    tw, th = ancho - 0.012, alto - 0.024
    texto = _caja("TicketTexto", (tw, 0.0003, th), centro=(0, -0.0005, zc), material=mat("papel_texto", "fondo.superficie", 0.85),
                  bisel=0)
    g = _grupo("ticket", [papel, texto], agarre="mano", radio=alto * 0.35, sep_mano=0.02, desp_mano=[0.0, -0.025, 0.0], semialto=0.0005,
               pantalla_objeto=texto.name)
    g["pantalla"] = [tw, th, zc, 0.0]
    return g


@prop("mano", "Regla de 30 cm con marcas", ["medir", "longitud", "geometría"])
def regla(m=None):
    cuerpo = _caja("Regla", (0.3, 0.004, 0.035), material=mat("regla", "#E9D9A8", 0.5), bisel=0.0015)
    marcas = []
    tinta = mat("marino", "nexo.marino", 0.7)
    for i in range(31):
        h = 0.012 if i % 5 == 0 else 0.006
        marcas.append(_caja("ReglaMarca", (0.0012, 0.0045, h), centro=(-0.15 + i * 0.01, -0.0003, 0.0175 - h / 2), material=tinta, bisel=0))
    return _grupo("regla", [cuerpo] + marcas, agarre="mano", radio=0.02)


@prop("mano", "Puntero con punta del color del nivel", ["señalar", "explicar"])
def puntero(m=None, nivel="eso", largo=0.45):
    vara = _cilindro("PunteroVara", 0.006, largo, centro=(0, 0, -largo / 2), material=mat("marino", "nexo.marino", 0.5), r2=0.004)
    punta = _esfera("PunteroPunta", 0.012, centro=(0, 0, -largo), material=mat(f"nivel_{nivel}", nivel_color(nivel), 0.4, emision=0.4))
    return _grupo("puntero", [vara, punta], agarre="mano", radio=0.01, punta=[0, 0, -largo])


@prop("suelo", "Coche de juguete; se desplaza para hablar de velocidad y funciones", ["movimiento", "velocidad", "funciones", "taxi"])
def coche(m=None, nivel="eso"):
    carroceria = _caja("CocheCuerpo", (0.36, 0.18, 0.09), centro=(0, 0, 0.085), material=mat(f"nivel_{nivel}", nivel_color(nivel), 0.4), bisel=0.03, seg=4)
    cabina = _caja("CocheCabina", (0.18, 0.15, 0.08), centro=(-0.02, 0, 0.16), material=mat("cristal", "nexo.pantalla", 0.15), bisel=0.03, seg=4)
    ruedas = [_cilindro("CocheRueda", 0.042, 0.03, centro=(x, y, 0.042), material=mat("marino", "nexo.marino", 0.7), eje="Y", bisel=0.008)
              for x in (-0.11, 0.11) for y in (-0.09, 0.09)]
    return _grupo("coche", [carroceria, cabina] + ruedas, agarre="suelo", radio=0.2)


@prop("suelo", "Mesa baja a la altura de Nexo sentado o de pie", ["trabajar", "teclear", "experimentos"])
def mesa(m=None, ancho=0.9, fondo=0.5, alto=0.42):
    madera = mat("madera", "#C9A27A", 0.6)
    tablero = _caja("MesaTablero", (ancho, fondo, 0.04), centro=(0, 0, alto - 0.02), material=madera, bisel=0.012)
    patas = [_cilindro("MesaPata", 0.022, alto - 0.04, centro=(x, y, (alto - 0.04) / 2), material=madera)
             for x in (-ancho / 2 + 0.06, ancho / 2 - 0.06) for y in (-fondo / 2 + 0.06, fondo / 2 - 0.06)]
    return _grupo("mesa", [tablero] + patas, agarre="suelo", radio=ancho / 2, altura_superficie=alto)


@prop("mano", "Matraz Erlenmeyer con líquido del color del nivel", ["química", "reacciones", "disoluciones"])
def matraz(m=None, nivel="eso"):
    vidrio = mat("vidrio", "#EAF4FA", 0.05, transm=0.95)
    cuerpo = _cilindro("MatrazCuerpo", 0.06, 0.1, centro=(0, 0, 0.05), material=vidrio, r2=0.018, seg=48, bisel=0.006)
    cuello = _cilindro("MatrazCuello", 0.018, 0.06, centro=(0, 0, 0.13), material=vidrio, seg=32, bisel=0.002)
    liquido = _cilindro("MatrazLiquido", 0.055, 0.045, centro=(0, 0, 0.024), material=mat(f"liquido_{nivel}", nivel_color(nivel), 0.1, emision=0.15), r2=0.04, seg=48)
    return _grupo("matraz", [cuerpo, cuello, liquido], agarre="mano", radio=0.06)


@prop("suelo", "Robot móvil pequeño con dos ruedas, sensor y antena", ["robótica", "sensores", "algoritmos", "programación"])
def robot(m=None, nivel="eso"):
    cuerpo = _caja("RobotCuerpo", (0.22, 0.2, 0.12), centro=(0, 0, 0.11), material=mat("blanco", "fondo.superficie", 0.4), bisel=0.035, seg=4)
    tapa = _caja("RobotTapa", (0.18, 0.16, 0.02), centro=(0, 0, 0.175), material=mat(f"nivel_{nivel}", nivel_color(nivel), 0.4), bisel=0.008)
    ojos = [_esfera("RobotSensor", 0.016, centro=(x, -0.1, 0.12), material=mat("ojo", "nexo.ojo", 0.2, emision=2.0)) for x in (-0.045, 0.045)]
    ruedas = [_cilindro("RobotRueda", 0.05, 0.03, centro=(x, 0, 0.05), material=mat("marino", "nexo.marino", 0.7), eje="X", bisel=0.01) for x in (-0.125, 0.125)]
    antena = _cilindro("RobotAntena", 0.004, 0.08, centro=(0.05, 0.04, 0.225), material=mat("marino", "nexo.marino", 0.7), bisel=0)
    bola = _esfera("RobotAntenaBola", 0.012, centro=(0.05, 0.04, 0.27), material=mat(f"nivel_{nivel}", nivel_color(nivel), 0.4, emision=0.5))
    return _grupo("robot", [cuerpo, tapa, antena, bola] + ojos + ruedas, agarre="suelo", radio=0.15)


@prop("mano", "Vaso medidor graduado con líquido; params: lleno (0-1)", ["fracciones", "capacidad", "medir"])
def vaso(m=None, lleno=0.5, nivel="eso"):
    vidrio = mat("vidrio", "#EAF4FA", 0.05, transm=0.95)
    h = 0.14
    cuerpo = _cilindro("VasoCuerpo", 0.045, h, centro=(0, 0, h / 2), material=vidrio, r2=0.05, seg=48, bisel=0.003)
    hijos = [cuerpo]
    if lleno > 0:
        hijos.append(_cilindro("VasoLiquido", 0.042, h * lleno * 0.95, centro=(0, 0, h * lleno * 0.95 / 2 + 0.003),
                               material=mat(f"liquido_{nivel}", nivel_color(nivel), 0.1, emision=0.15), r2=0.042 + 0.005 * lleno, seg=48))
    tinta = mat("marino", "nexo.marino", 0.7)
    for k in range(1, 5):
        hijos.append(_caja("VasoMarca", (0.02, 0.002, 0.002), centro=(0, -0.049, h * k / 5), material=tinta, bisel=0))
    return _grupo("vaso", hijos, agarre="mano", radio=0.05)


def construir(nombre, **params):
    if nombre not in PROPS:
        raise KeyError(f"Prop '{nombre}' no existe. Disponibles: {', '.join(sorted(PROPS))}")
    return PROPS[nombre]["fn"](**params)


def catalogo():
    return {n: {"agarre": p["agarre"], "descripcion": p["descripcion"], "usos": p["usos"]} for n, p in sorted(PROPS.items())}


if __name__ == "__main__":
    if "--catalogo" in sys.argv:
        import json
        ruta = AQUI / "catalogo.json"
        data = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
        data["props"] = catalogo()
        ruta.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("Catálogo de props actualizado:", ", ".join(data["props"]))
