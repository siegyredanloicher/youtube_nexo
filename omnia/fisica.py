"""Física compartida entre la animación 2D (Manim) y la 3D (Nexo en Blender).

Si Nexo lanza una pelota a 6 m/s y 45°, la gráfica 2D dibuja la MISMA parábola con estas funciones.
Las cifras que se digan en el guion se verifican además con pipeline/verificar.py.
"""
import math

G = 9.81  # m/s², gravedad en la superficie terrestre (valor estándar redondeado)


def tiro_parabolico(v0: float, angulo_deg: float, h0: float = 0.0, g: float = G):
    """Devuelve (vx, vy, t_vuelo, alcance, altura_max) de un lanzamiento desde altura h0 hasta y = 0."""
    a = math.radians(angulo_deg)
    vx, vy = v0 * math.cos(a), v0 * math.sin(a)
    t = (vy + math.sqrt(vy * vy + 2 * g * h0)) / g
    return vx, vy, t, vx * t, h0 + vy * vy / (2 * g)


def posicion(v0: float, angulo_deg: float, t: float, h0: float = 0.0, g: float = G):
    """(x, y) en el instante t (sin rozamiento)."""
    a = math.radians(angulo_deg)
    return v0 * math.cos(a) * t, h0 + v0 * math.sin(a) * t - 0.5 * g * t * t


def trayectoria(v0: float, angulo_deg: float, h0: float = 0.0, n: int = 60, rebotes: int = 0,
                restitucion: float = 0.5, g: float = G):
    """Lista de (t, x, y) hasta tocar el suelo; con rebotes, sigue botando con pérdida de energía."""
    pts, t0, x0, vx, vy, y0 = [], 0.0, 0.0, None, None, h0
    a = math.radians(angulo_deg)
    vx, vy = v0 * math.cos(a), v0 * math.sin(a)
    for k in range(rebotes + 1):
        tv = (vy + math.sqrt(vy * vy + 2 * g * y0)) / g
        for i in range(n + 1):
            t = tv * i / n
            pts.append((t0 + t, x0 + vx * t, max(0.0, y0 + vy * t - 0.5 * g * t * t)))
        t0, x0, y0 = t0 + tv, x0 + vx * tv, 0.0
        vy = (vy - g * tv) * -restitucion
        vx *= 0.85
    return pts


def caida_libre(h: float, g: float = G):
    """Tiempo y velocidad final al soltar algo desde h metros."""
    t = math.sqrt(2 * h / g)
    return t, g * t
