"""Small meshes for 1:many miniatures. Coordinates are Blender X east, -Y front, Z up."""

from collections import defaultdict
import math
from mathutils import Vector
from math import sin, cos, pi

PARTS = defaultdict(list)
part = "基座"


def group(name):
    global part
    part = name


def face(v, m, uv=None):
    p = [tuple(float(n) for n in pt) for pt in v]
    if len(set(p)) < 3:
        return
    clean = []
    for pt in p:
        if not clean or pt != clean[-1]:
            clean.append(pt)
    if clean[-1] == clean[0]:
        clean.pop()
    if len(clean) < 3:
        return
    PARTS[part].append((clean, m, uv))


def box(x, y, z, w, d, h, m):
    profile(x, y, z, [(0, w, d), (h, w, d)], m)


def profile(x, y, z, levels, m):
    loops = []
    for hh, w, d in levels:
        loops.append(
            [(x + a * w / 2, y + b * d / 2, z + hh) for a, b in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
        )
    face(loops[0][::-1], m)
    face(loops[-1], m)
    for l, u in zip(loops, loops[1:]):
        for j in range(4):
            k = (j + 1) % 4
            face([l[j], l[k], u[k], u[j]], m)


def cylinder(a, b, ra, rb, mat, sides=10):
    a, b = Vector(a), Vector(b)
    axis = b - a
    if axis.length < 1e-7:
        return
    axis.normalize()
    ref = Vector((0, 0, 1)) if abs(axis.z) < 0.88 else Vector((1, 0, 0))
    u = axis.cross(ref).normalized()
    v = axis.cross(u).normalized()
    low = []
    hi = []
    for j in range(sides):
        t = j * 2 * pi / sides
        rr = u * cos(t) + v * sin(t)
        low.append(a + rr * ra)
        hi.append(b + rr * rb)
    face(low[::-1], mat)
    face(hi, mat)
    for j in range(sides):
        k = (j + 1) % sides
        face([low[j], low[k], hi[k], hi[j]], mat)


def shaft(x, y, z, r, h, m, n=10, r2=None):
    cylinder((x, y, z), (x, y, z + h), r, r if r2 is None else r2, m, n)


def sphere(x, y, z, sx, sy, sz, m, s=8, n=5):
    prev = None
    for i in range(n + 1):
        theta = -pi / 2 + pi * i / n
        loop = [
            (
                x + sx * cos(theta) * cos(k * 2 * pi / s),
                y + sy * cos(theta) * sin(k * 2 * pi / s),
                z + sz * sin(theta),
            )
            for k in range(s)
        ]
        if i == 0 or i == n:
            loop = [(x, y, z + sz * (-1 if i == 0 else 1))] * s
        if prev is not None:
            for j in range(s):
                k = (j + 1) % s
                face([prev[j], prev[k], loop[k], loop[j]], m)
        prev = loop


def ring(x, y, z, r, sub, m, n=30, k=5, plane="xz"):
    def pos(j, i):
        t = 2 * pi * j / n
        a = 2 * pi * i / k
        rad = r + sub * cos(a)
        if plane == "xy":
            return (x + rad * cos(t), y + rad * sin(t), z + sub * sin(a))
        return (x + rad * cos(t), y + sub * sin(a), z + rad * sin(t))

    for j in range(n):
        for i in range(k):
            face([pos(j, i), pos(j + 1, i), pos(j + 1, i + 1), pos(j, i + 1)], m)


def floorplan(x, y, z, outline, h, m):
    lo = [(x + a, y + b, z) for a, b in outline]
    hi = [(a, b, c + h) for a, b, c in lo]
    face(lo[::-1], m)
    face(hi, m)
    for j in range(len(lo)):
        k = (j + 1) % len(lo)
        face([lo[j], lo[k], hi[k], hi[j]], m)


def hip(x, y, z, w, d, h, m, trim="timber", lift=0.12):
    # A swept hip roof with raised corners, a shallow hollow lower slope and a straight main ridge.
    ridge = max(w * 0.12, w - d * 0.72)
    n = 8
    levels = 3
    for side in range(4):

        def point(u, t):
            rw = w + (ridge - w) * t
            rd = d * (1 - t)
            if side == 0:
                xx, yy = rw * u / 2, -rd / 2
            elif side == 1:
                xx, yy = rw / 2, rd * u / 2
            elif side == 2:
                xx, yy = -rw * u / 2, rd / 2
            else:
                xx, yy = -rw / 2, -rd * u / 2
            return (x + xx, y + yy, z + h * (0.58 * t + 0.42 * t * t + lift * (abs(u) ** 3) * (1 - t)))

        for j in range(n):
            u0 = -1 + 2 * j / n
            u1 = -1 + 2 * (j + 1) / n
            p = point(u0, 0)
            q = point(u1, 0)
            face([(p[0], p[1], p[2] - 0.08), (q[0], q[1], q[2] - 0.08), q, p], trim)
            for k in range(levels):
                t0 = k / levels
                t1 = (k + 1) / levels
                face([point(u0, t0), point(u1, t0), point(u1, t1), point(u0, t1)], m)
        cylinder(point(1, 0), point(1, 1), 0.045, 0.035, m, 5)
    cylinder((x - ridge / 2, y, z + h), (x + ridge / 2, y, z + h), 0.06, 0.06, m, 6)


def annular_arch(x, y, z, r, thick, depth, m, n=12):
    # Semicircular voussoirs around an actual aperture, extruded along Y.
    for j in range(n):
        a, b = pi * j / n, pi * (j + 1) / n
        cross = [
            (x + r * cos(a), z + r * sin(a)),
            (x + (r + thick) * cos(a), z + (r + thick) * sin(a)),
            (x + (r + thick) * cos(b), z + (r + thick) * sin(b)),
            (x + r * cos(b), z + r * sin(b)),
        ]
        fr = [(xx, y - depth / 2, zz) for xx, zz in cross]
        ba = [(xx, y + depth / 2, zz) for xx, zz in cross]
        face(fr, m)
        face(ba[::-1], m)
        for i in range(4):
            k = (i + 1) % 4
            face([fr[i], ba[i], ba[k], fr[k]], m)


def roofcone(x, y, z, r, h, mat, tip=0.02, n=14):
    for i, (tt, rr) in enumerate(
        [(0, r), (0.08, r * 1.02), (0.35, r * 0.62), (0.70, r * 0.32), (1, tip)]
    ):
        if i:
            cylinder((x, y, z + h * t0), (x, y, z + h * tt), r0, rr, mat, n)
        t0, r0 = tt, rr


def steps(x, y, z, w, run, rise, n, m):
    for i in range(n):
        box(x, y + run * (i + 0.5) / n, z, w, run / n + 0.001, rise * (i + 1) / n, m)


def window(x, y, z, w, h, frame="timber", glass="dark"):
    box(x, y, z, w, 0.065, h, frame)
    box(x, y - 0.041, z + 0.055, w * 0.73, 0.025, max(0.06, h - 0.11), glass)
