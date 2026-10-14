"""Acciones de Nexo: gestos reutilizables que animan el rig (y los props) a partir de unos pocos parámetros.

Un plano = una acción + props + expresiones + cámara (lo describe escenas.json y lo renderiza
pipeline/render_nexo.py). Cada acción es  fn(P, **params) -> duración en segundos  y se registra con @accion.

Convenciones del rig (nexo/nexo3.py): Nexo mira hacia -Y, Z arriba, mide ~1,04 m, rig en el origen.
  Controles IK: IK_hand.L/R, IK_foot.L/R (posiciones en metros, espacio del mundo).
  FK: hips, spine, chest, neck, head (rotaciones en grados).
  .L es la mano izquierda de Nexo (lado +X del mundo); .R, la derecha (-X).
Expresiones: Feliz, Tranquilo, Sorpresa, Pensativo, Concentrado, Curioso, Motivado, Entusiasmado, Parpadeo, Neutro.
Añadir una acción: escribe la función, regístrala con @accion y ejecuta  python nexo/acciones.py --catalogo
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: F401  (carga mathutils)
from mathutils import Euler, Vector

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent))
from omnia import fisica  # noqa: E402

ACCIONES = {}
EXPRESIONES = ["Feliz", "Tranquilo", "Sorpresa", "Pensativo", "Concentrado", "Curioso", "Motivado",
               "Entusiasmado", "Parpadeo"]


def accion(descripcion, params=None, props=(), usos=()):
    def deco(fn):
        ACCIONES[fn.__name__] = dict(fn=fn, descripcion=descripcion, params=params or {}, props=list(props),
                                     usos=list(usos))
        return fn
    return deco


# ---------------------------------------------------------------- plano: utilidades de animación
class Plano:
    """Escribe keyframes sobre el rig de Nexo y los props. Tiempos en segundos."""

    def __init__(self, rig, ojos, fps=24):
        self.rig, self.ojos, self.fps = rig, ojos, fps
        self.kb = ojos.data.shape_keys.key_blocks
        self.props = {}            # id -> objeto
        self._pistas = {}          # id -> lista de (t0, t1, fn(t) -> Matrix mundo)
        self.dur = 0.0
        self._expr_activa = None
        b = rig.data.bones
        self.reposo = {n: Vector(b[n].head_local) for n in ("IK_hand.L", "IK_hand.R", "IK_foot.L", "IK_foot.R")}
        self.hombro = {s: Vector(b[f"upper_arm.{s}"].head_local) for s in "LR"}

    def f(self, t):
        return 1 + round(t * self.fps)

    def _pb(self, n):
        return self.rig.pose.bones[n]

    def ik(self, nombre, pos, t, rot=None):
        """Coloca un control IK en una posición del mundo (m) y, opcionalmente, con rotación (grados)."""
        pb = self._pb(nombre)
        rest = self.rig.data.bones[nombre].head_local
        pb.location = pb.bone.matrix_local.to_3x3().inverted() @ (Vector(pos) - rest)
        pb.keyframe_insert("location", frame=self.f(t))
        if rot is not None:
            pb.rotation_mode = "XYZ"
            pb.rotation_euler = Euler([math.radians(a) for a in rot])
            pb.keyframe_insert("rotation_euler", frame=self.f(t))
        self.dur = max(self.dur, t)

    def rot(self, hueso, grados, t):
        pb = self._pb(hueso)
        pb.rotation_mode = "XYZ"
        pb.rotation_euler = Euler([math.radians(a) for a in grados])
        pb.keyframe_insert("rotation_euler", frame=self.f(t))
        self.dur = max(self.dur, t)

    def mirar(self, t, giro=0.0, cabeceo=0.0, ladeo=0.0):
        """Cabeza: giro (izq/der, + hacia su izquierda), cabeceo (+ abajo), ladeo (+ hacia su izquierda)."""
        self.rot("head", (cabeceo, giro, ladeo), t)

    def cuerpo(self, t, giro=0.0, inclinacion=0.0, subir=0.0):
        self.rot("spine", (inclinacion * 0.5, giro * 0.5, 0), t)
        self.rot("chest", (inclinacion * 0.5, giro * 0.5, 0), t)
        pb = self._pb("hips")
        pb.location = (0, subir, 0)  # Y local de la cadera = arriba
        pb.keyframe_insert("location", frame=self.f(t))

    def expr(self, nombre, t, valor=1.0, fundido=0.2):
        """Cambia de expresión con un fundido corto. 'Neutro' apaga todas."""
        f0, f1 = self.f(max(0.0, t - fundido)), self.f(t)
        for k in EXPRESIONES:
            kb = self.kb[k]
            kb.keyframe_insert("value", frame=f0)
            kb.value = valor if k == nombre else 0.0
            kb.keyframe_insert("value", frame=f1)
        self.dur = max(self.dur, t)

    def parpadeo(self, t):
        kb = self.kb["Parpadeo"]
        for dt, v in ((0, 0.0), (0.06, 1.0), (0.16, 0.0)):
            kb.value = v
            kb.keyframe_insert("value", frame=self.f(t + dt))

    def relajado(self, t, fase=0.0):
        """Pose base: brazos sueltos, algo doblados; peso en una pierna."""
        r = self.reposo
        self.ik("IK_hand.L", r["IK_hand.L"] + Vector((-0.035, -0.02, -0.012 + 0.004 * math.sin(fase))), t, (-4, 0, 6))
        self.ik("IK_hand.R", r["IK_hand.R"] + Vector((0.04, 0.0, -0.008 + 0.004 * math.sin(fase + 1))), t, (-3, 0, -8))
        self.ik("IK_foot.L", r["IK_foot.L"], t)
        self.ik("IK_foot.R", r["IK_foot.R"], t)
        self.cuerpo(t, giro=2, inclinacion=2, subir=0.003 * math.sin(fase))
        self.mirar(t, giro=-4, cabeceo=-2, ladeo=-5)

    def respirar(self, t0, t1, periodo=3.2):
        t = t0
        while t <= t1 + 1e-6:
            self.relajado(t, 2 * math.pi * (t - t0) / periodo)
            t += periodo / 4

    # props -----------------------------------------------------------------
    def palma(self, mano):
        """Matriz del mundo del centro de la palma (evalúa el rig en el fotograma actual)."""
        pb = self._pb(f"hand.{mano}")
        m = self.rig.matrix_world @ pb.matrix
        eje = (m.to_3x3() @ Vector((0, 1, 0))).normalized()
        frente = (m.to_3x3() @ Vector((0, 0, 1))).normalized()
        centro = m.translation + eje * 0.045 + frente * 0.0
        out = m.copy()
        out.translation = centro
        return out

    def en_mano(self, pid, mano, t0, t1, separacion=None):
        ob = self.props[pid]
        sep = separacion if separacion is not None else ob.get("radio", 0.04) + 0.012

        def fn(t, mano=mano, sep=sep):
            m = self.palma(mano)
            hacia = Vector((-1 if mano == "L" else 1, -0.6, 0.35)).normalized()  # hacia el interior y delante
            pos = m.translation + hacia * sep
            return pos, None
        self._pistas.setdefault(pid, []).append((t0, t1, fn))

    def trayecto(self, pid, t0, t1, fn):
        """fn(t_relativo) -> posición del mundo."""
        self._pistas.setdefault(pid, []).append((t0, t1, lambda t, fn=fn, t0=t0: (Vector(fn(t - t0)), None)))
        self.dur = max(self.dur, t1)

    def fijo(self, pid, pos, rot_z=0.0):
        ob = self.props[pid]
        ob.location = Vector(pos)
        ob.rotation_euler = (0, 0, math.radians(rot_z))

    def hornear(self, escena):
        """Evalúa fotograma a fotograma y fija la posición de los props que van en la mano o en trayecto."""
        if not self._pistas:
            return
        for f in range(1, self.f(self.dur) + 1):
            t = (f - 1) / self.fps
            escena.frame_set(f)
            for pid, pistas in self._pistas.items():
                for t0, t1, fn in pistas:
                    if t0 - 1e-6 <= t <= t1 + 1e-6:
                        pos, _ = fn(t)
                        ob = self.props[pid]
                        ob.location = pos
                        ob.keyframe_insert("location", frame=f)
                        break


# ---------------------------------------------------------------- acciones
@accion("Reposo natural: respira, mira alrededor y parpadea", {"duracion": 4.0}, usos=["escuchar", "transición"])
def idle(P, duracion=4.0, expresion="Tranquilo"):
    P.expr(expresion, 0.0)
    P.respirar(0, duracion)
    P.mirar(duracion * 0.5, giro=6, cabeceo=-3, ladeo=-3)
    P.parpadeo(duracion * 0.6)
    return duracion


@accion("Saluda con la mano", {"mano": "L", "veces": 3}, usos=["intro", "despedida"])
def saludar(P, mano="L", veces=3, expresion="Feliz"):
    s = 1 if mano == "L" else -1
    P.relajado(0)
    P.expr(expresion, 0.3)
    alto = P.hombro[mano] + Vector((0.1 * s, -0.04, 0.17))
    P.ik(f"IK_hand.{mano}", alto, 0.45, (0, 0, -20 * s))
    t = 0.45
    for _ in range(veces):
        P.ik(f"IK_hand.{mano}", alto + Vector((0.03 * s, 0, 0)), t + 0.18, (0, 0, -35 * s))
        P.ik(f"IK_hand.{mano}", alto + Vector((-0.02 * s, 0, 0)), t + 0.36, (0, 0, -5 * s))
        t += 0.36
    P.mirar(0.4, giro=-3, ladeo=6 * s)
    P.relajado(t + 0.5)
    P.parpadeo(t + 0.7)
    return t + 0.9


@accion("Señala un punto (a su izquierda/derecha o [x,y,z] en metros)", {"objetivo": "derecha", "mano": "auto"},
        usos=["explicar", "presentar un resultado", "dirigir la mirada"])
def senalar(P, objetivo="derecha", mano="auto", expresion="Curioso", duracion=2.5):
    if isinstance(objetivo, str):
        objetivo = {"derecha": (1.6, -0.6, 0.8), "izquierda": (-1.6, -0.6, 0.8), "arriba": (0.4, -0.8, 2.0),
                    "camara": (0.0, -3.0, 0.75)}[objetivo]
    obj = Vector(objetivo)
    if mano == "auto":
        mano = "L" if obj.x > 0 else "R"
    s = 1 if mano == "L" else -1
    d = (obj - P.hombro[mano]).normalized()
    P.relajado(0)
    P.expr(expresion, 0.35)
    P.ik(f"IK_hand.{mano}", P.hombro[mano] + d * 0.2, 0.55, (0, 0, 0))
    giro = math.degrees(math.atan2(obj.x, -obj.y)) * 0.6
    P.mirar(0.5, giro=giro, cabeceo=-math.degrees(math.atan2(obj.z - 0.75, 2.0)) * 0.4)
    P.cuerpo(0.55, giro=giro * 0.3)
    P.ik(f"IK_hand.{mano}", P.hombro[mano] + d * 0.205, duracion - 0.5, (0, 0, 0))
    P.expr("Feliz", duracion - 0.6)
    P.relajado(duracion)
    P.mirar(duracion, giro=0)
    P.cuerpo(duracion)
    return duracion


@accion("Piensa con la mano en la barbilla", {"duracion": 3.0}, usos=["plantear una pregunta", "dudar", "problema inverso"])
def pensar(P, duracion=3.0, mano="R"):
    s = 1 if mano == "L" else -1
    P.relajado(0)
    P.expr("Pensativo", 0.4)
    P.ik(f"IK_hand.{mano}", Vector((0.06 * s, -0.24, 0.53)), 0.6, (60, 0, 30 * s))
    P.mirar(0.6, giro=-8 * s, cabeceo=-6, ladeo=10 * s)
    P.mirar(duracion - 0.5, giro=-14 * s, cabeceo=-8, ladeo=6 * s)
    P.parpadeo(duracion * 0.6)
    P.ik(f"IK_hand.{mano}", Vector((0.065 * s, -0.24, 0.535)), duracion - 0.2, (60, 0, 30 * s))
    return duracion


@accion("Sostiene un prop delante del pecho", {"prop": "pelota", "mano": "L"}, props=["cualquiera de mano"],
        usos=["presentar un objeto", "hablar de él"])
def sostener(P, prop="p1", mano="L", duracion=3.0, expresion="Feliz"):
    s = 1 if mano == "L" else -1
    P.relajado(0)
    P.expr(expresion, 0.3)
    delante = Vector((0.1 * s, -0.2, 0.42))
    P.ik(f"IK_hand.{mano}", delante, 0.5, (70, 0, -20 * s))
    P.ik(f"IK_hand.{mano}", delante + Vector((0, 0, 0.01)), duracion, (70, 0, -20 * s))
    P.mirar(0.6, giro=8 * s, cabeceo=12)
    P.mirar(duracion - 0.6, giro=0, cabeceo=0)
    P.en_mano(prop, mano, 0, duracion)
    return duracion


@accion("Muestra un prop a cámara levantándolo", {"prop": "dado", "mano": "L"}, usos=["enseñar", "sorpresa"])
def mostrar(P, prop="p1", mano="L", duracion=2.6):
    s = 1 if mano == "L" else -1
    P.relajado(0)
    P.ik(f"IK_hand.{mano}", Vector((0.1 * s, -0.2, 0.42)), 0.4, (70, 0, -20 * s))
    P.ik(f"IK_hand.{mano}", Vector((0.17 * s, -0.27, 0.6)), 0.9, (90, 0, -10 * s))
    P.expr("Entusiasmado" if duracion > 2 else "Feliz", 0.9)
    P.mirar(0.9, giro=0, cabeceo=-4)
    P.ik(f"IK_hand.{mano}", Vector((0.17 * s, -0.28, 0.61)), duracion, (90, 0, -10 * s))
    P.en_mano(prop, mano, 0, duracion)
    return duracion


@accion("Lanza un prop con física real (tiro parabólico). Usa omnia.fisica: la 2D puede dibujar la misma curva",
        {"prop": "pelota", "v0": 4.0, "angulo": 45, "hacia": "derecha", "rebotes": 1},
        props=["pelota", "dado", "bloque"], usos=["parábolas", "gravedad", "funciones cuadráticas", "probabilidad (dado)"])
def lanzar(P, prop="p1", v0=4.0, angulo=45.0, hacia="derecha", rebotes=1, mano="auto"):
    d = 1 if hacia == "derecha" else -1        # derecha de la imagen = +X del mundo = lado izquierdo de Nexo
    mano = mano if mano != "auto" else ("L" if d > 0 else "R")
    s = 1 if mano == "L" else -1
    P.relajado(0)
    P.expr("Concentrado", 0.2)
    atras = P.hombro[mano] + Vector((0.08 * s - 0.06 * d, 0.1, 0.05))
    suelta = P.hombro[mano] + Vector((0.16 * d, -0.08, 0.14))
    P.ik(f"IK_hand.{mano}", Vector((0.12 * s, -0.17, 0.4)), 0.35, (60, 0, 0))
    P.ik(f"IK_hand.{mano}", atras, 0.75, (-20, 0, 0))
    P.cuerpo(0.75, giro=-14 * d, inclinacion=-4)
    t_rel = 0.98
    P.ik(f"IK_hand.{mano}", suelta, t_rel, (40, 0, 0))
    P.cuerpo(t_rel, giro=12 * d, inclinacion=6)
    P.ik(f"IK_hand.{mano}", suelta + Vector((0.05 * d, -0.05, -0.08)), t_rel + 0.25, (60, 0, 0))
    P.en_mano(prop, mano, 0, t_rel)
    # vuelo: parte de la mano en el instante de soltar
    escena = P.rig.users_scene[0]
    escena.frame_set(P.f(t_rel))
    pos0 = P.palma(mano).translation.copy()
    r = P.props[prop].get("radio", 0.05)
    # el centro del prop toca el suelo a altura r: se calcula la parábola con el suelo desplazado r
    pts = fisica.trayectoria(v0, angulo, h0=pos0.z - r, n=80, rebotes=rebotes)
    t_vuelo = pts[-1][0]

    def vuelo(t):
        for (ta, xa, ya), (tb, xb, yb) in zip(pts, pts[1:]):
            if ta <= t <= tb:
                k = (t - ta) / (tb - ta) if tb > ta else 0
                x, y = xa + (xb - xa) * k, ya + (yb - ya) * k
                break
        else:
            x, y = pts[-1][1], pts[-1][2]
        return (pos0.x + d * x, pos0.y, y + r)
    P.trayecto(prop, t_rel, t_rel + t_vuelo, vuelo)
    P.mirar(t_rel + 0.2, giro=-25 * d, cabeceo=-10)
    P.mirar(t_rel + t_vuelo * 0.5, giro=-35 * d, cabeceo=-4)
    P.mirar(t_rel + t_vuelo, giro=-30 * d, cabeceo=8)
    P.expr("Sorpresa", t_rel + 0.3)
    P.expr("Feliz", t_rel + t_vuelo)
    P.relajado(t_rel + t_vuelo + 0.3)
    P._lanzamiento = dict(v0=v0, angulo=angulo, h0=pos0.z, t_vuelo=t_vuelo, alcance=pts[-1][1])
    return t_rel + t_vuelo + 0.8


@accion("Celebra: brazos arriba y saltito", {"duracion": 2.0}, usos=["resultado correcto", "final"])
def celebrar(P, duracion=2.0):
    P.relajado(0)
    P.expr("Entusiasmado", 0.25)
    for s, m in ((1, "L"), (-1, "R")):
        P.ik(f"IK_hand.{m}", P.hombro[m] + Vector((0.08 * s, -0.04, 0.19)), 0.4, (0, 0, -15 * s))
    P.cuerpo(0.3, subir=-0.02)
    P.cuerpo(0.55, subir=0.05)
    P.cuerpo(0.8, subir=0.0)
    for s, m in ((1, "L"), (-1, "R")):
        P.ik(f"IK_hand.{m}", P.hombro[m] + Vector((0.09 * s, -0.04, 0.2)), duracion - 0.4, (0, 0, -15 * s))
    P.relajado(duracion)
    return duracion


@accion("Asiente con la cabeza", {"veces": 2}, usos=["confirmar", "sí"])
def asentir(P, veces=2):
    P.relajado(0)
    P.expr("Feliz", 0.2)
    t = 0.2
    for _ in range(veces):
        P.mirar(t + 0.15, cabeceo=12)
        P.mirar(t + 0.35, cabeceo=-3)
        t += 0.35
    P.mirar(t + 0.2)
    return t + 0.4


@accion("Encoge los hombros: «no está tan claro»", {"duracion": 1.8}, usos=["error común", "duda"])
def encoger(P, duracion=1.8):
    P.relajado(0)
    P.expr("Curioso", 0.3)
    for s, m in ((1, "L"), (-1, "R")):
        P.ik(f"IK_hand.{m}", Vector((0.2 * s, -0.12, 0.36)), 0.45, (80, 0, -40 * s))
    P.mirar(0.45, ladeo=12)
    P.mirar(duracion - 0.4, ladeo=8)
    P.relajado(duracion)
    return duracion


@accion("Escribe en la pizarra (la pizarra queda a la derecha de la imagen)", {"duracion": 3.0},
        props=["pizarra"], usos=["desarrollar una fórmula", "dibujar"])
def escribir(P, duracion=3.0, pizarra="p1"):
    if pizarra in P.props:
        P.fijo(pizarra, (0.72, 0.02, 0), rot_z=-28)
    P.relajado(0)
    P.cuerpo(0.4, giro=30)
    P.mirar(0.4, giro=38, cabeceo=-4)
    P.expr("Concentrado", 0.4)
    base = Vector((0.36, -0.12, 0.66))
    t, k = 0.6, 0
    while t < duracion - 0.4:
        P.ik("IK_hand.L", base + Vector((0.012 * k, 0.008 * k, 0.02 * math.sin(k * 2.1))), t, (70, 0, -40))
        t += 0.18
        k += 1
    P.expr("Feliz", duracion - 0.3)
    P.cuerpo(duracion, giro=10)
    P.mirar(duracion, giro=10)
    return duracion


@accion("Teclea en el portátil sobre la mesa", {"duracion": 3.0}, props=["mesa", "portatil"],
        usos=["programación", "calcular", "buscar datos"])
def teclear(P, duracion=3.0, mesa="p1", portatil="p2"):
    if mesa in P.props:
        P.fijo(mesa, (0, -0.38, 0))
    if portatil in P.props:
        P.fijo(portatil, (0, -0.4, P.props[mesa].get("altura_superficie", 0.42) if mesa in P.props else 0.42), 180)
    P.relajado(0)
    P.expr("Concentrado", 0.3)
    P.mirar(0.3, cabeceo=18)
    P.cuerpo(0.3, inclinacion=8)
    t, k = 0.4, 0
    while t < duracion:
        for s, m in ((1, "L"), (-1, "R")):
            P.ik(f"IK_hand.{m}", Vector((0.07 * s, -0.27, 0.45 + 0.012 * ((k + (s > 0)) % 2))), t, (80, 0, 0))
        t += 0.14
        k += 1
    return duracion


@accion("Camina una distancia en una dirección del suelo", {"distancia": 1.0, "direccion": "derecha"},
        usos=["entrar en plano", "recorrer una recta numérica", "transición"])
def caminar(P, distancia=1.0, direccion="derecha", velocidad=0.5):
    d = {"derecha": Vector((-1, 0, 0)), "izquierda": Vector((1, 0, 0)), "delante": Vector((0, -1, 0)),
         "atras": Vector((0, 1, 0))}[direccion] if isinstance(direccion, str) else Vector(direccion).normalized()
    dur = distancia / velocidad
    paso = 0.45                 # s por paso
    zancada = velocidad * paso  # lo que avanza el cuerpo mientras un pie está apoyado
    raiz = P._pb("root")        # los controles IK cuelgan de root: se mueven con él
    P.expr("Motivado", 0.2)
    t = 0.0
    while t <= dur + 1e-6:
        raiz.location = raiz.bone.matrix_local.to_3x3().inverted() @ (d * velocidad * t)
        raiz.keyframe_insert("location", frame=P.f(t))
        fase = (t / (2 * paso)) % 1.0
        for s, m, ph in ((1, "L", 0.0), (-1, "R", 0.5)):
            p = (fase + ph) % 1.0
            if p < 0.5:   # apoyo: el pie retrocede respecto al cuerpo = quieto en el suelo
                off, lift = zancada / 2 - zancada * (p / 0.5), 0.0
            else:         # vuelo: adelanta el pie levantándolo
                q = (p - 0.5) / 0.5
                off, lift = -zancada / 2 + zancada * q, 0.035 * math.sin(math.pi * q)
            P.ik(f"IK_foot.{m}", P.reposo[f"IK_foot.{m}"] + d * off + Vector((0, 0, lift)), t)
            P.ik(f"IK_hand.{m}", P.reposo[f"IK_hand.{m}"] - d * off * 0.5 + Vector((-0.03 * s, -0.01, -0.012)), t)
        P.cuerpo(t, subir=0.006 * math.cos(4 * math.pi * fase), giro=3 * math.sin(2 * math.pi * fase))
        t += paso / 4
    return dur


def catalogo():
    return {n: {"descripcion": a["descripcion"], "params": a["params"], "props": a["props"], "usos": a["usos"]}
            for n, a in sorted(ACCIONES.items())}


if __name__ == "__main__":
    if "--catalogo" in sys.argv:
        import json
        ruta = AQUI / "catalogo.json"
        data = json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}
        data["acciones"] = catalogo()
        ruta.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        print("Catálogo de acciones actualizado:", ", ".join(data["acciones"]))
