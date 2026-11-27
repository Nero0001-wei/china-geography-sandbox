"""Small-scale architectural geometry in Blender's Z-up frame, front facing -Y."""

import bpy
from math import sin, cos, pi, tau
from pathlib import Path
from collections import defaultdict
from contextlib import contextmanager
from mathutils import Vector

ROOT = Path(__file__).parent
PALETTE = {
    "stone": ("#b3aa95", "limestone"),
    "marble": ("#d6cdb8", "granite"),
    "redbrick": ("#974e39", "terracotta"),
    "goldroof": ("#b7863b", "goldtile"),
    "slate": ("#4b5354", "slate"),
    "copper": ("#628f79", "copper"),
    "blue": ("#527da2", "bluetile"),
    "water": ("#63939a", "river"),
    "sandstone": ("#b6a989", "sandstone"),
    "grass": ("#748552", "meadow"),
    "rock": ("#978d78", "rock"),
    "gold": ("#e1bd69", None),
    "metal": ("#b6bdba", None),
    "ivory": ("#e1d7b6", None),
    "dark": ("#353a37", None),
    "ink": ("#263a3b", None),
    "window": ("#425658", None),
    "red": ("#a34b39", None),
    "wood": ("#744b35", None),
    "jade": ("#537874", None),
    "pink": ("#d69a92", None),
    "ice": ("#a6c7c6", None),
    "ochre": ("#b9854d", None),
    "foliage": ("#5d7851", None),
    "earth": ("#8f7a59", None),
    "world": ("#7195a1", "world"),
    "clock": ("#e0d1af", "clock"),
    "dragon": ("#ab643d", "dragon-wall"),
    "heaven": ("#3c5560", "heaven"),
    "qin": ("#3c5560", "qin"),
    "confucius": ("#3c5560", "confucius"),
}
parts = defaultdict(list)
group = "基台"
transform = (0, 0, 0)


def tag(name):
    global group
    group = name


@contextmanager
def at(x, y, angle=0):
    global transform
    old = transform
    transform = (x, y, angle)
    try:
        yield
    finally:
        transform = old


def p3(v):
    x, y, a = transform
    i, j, k = v
    return (x + i * cos(a) - j * sin(a), y + i * sin(a) + j * cos(a), k)


def face(pts, mat, uv=None):
    if len(pts) < 3:
        return
    pts = [p3(v) for v in pts]
    if uv is None:
        n = (Vector(pts[1]) - Vector(pts[0])).cross(Vector(pts[2]) - Vector(pts[0]))
        axis = max(range(3), key=lambda i: abs(n[i]))
        a, b = [(1, 2), (0, 2), (0, 1)][axis]
        uv = [(pt[a] / 3.2, pt[b] / 3.2) for pt in pts]
    parts[group].append((pts, mat, list(uv)))


def box(x, y, z, w, d, h, mat):
    a = w / 2
    b = d / 2
    low = [(x - a, y - b, z), (x + a, y - b, z), (x + a, y + b, z), (x - a, y + b, z)]
    high = [(i, j, z + h) for i, j, k in low]
    face(low[::-1], mat)
    face(high, mat)
    for i in range(4):
        j = (i + 1) % 4
        face([low[i], low[j], high[j], high[i]], mat)


def lathe(x, y, levels, mat, n=20, phase=0, aspect=1):
    rings = [
        [
            (x + r * cos(phase + i * tau / n), y + r * aspect * sin(phase + i * tau / n), z)
            for i in range(n)
        ]
        for r, z in levels
    ]
    face(rings[0][::-1], mat)
    face(rings[-1], mat)
    for k, (a, b) in enumerate(zip(rings, rings[1:])):
        for i in range(n):
            j = (i + 1) % n
            face([a[i], a[j], b[j], b[i]], mat)


def tube(a, b, r, mat, n=8):
    v = Vector(b) - Vector(a)
    if v.length < 1e-5:
        return
    v.normalize()
    u = v.cross(Vector((0, 0, 1)))
    if u.length < 0.001:
        u = v.cross(Vector((0, 1, 0)))
    u.normalize()
    w = v.cross(u)
    rings = [
        [tuple(Vector(p) + r * (u * cos(i * tau / n) + w * sin(i * tau / n))) for i in range(n)]
        for p in [a, b]
    ]
    A, B = rings
    face(A[::-1], mat)
    face(B, mat)
    for i in range(n):
        j = (i + 1) % n
        face([A[i], A[j], B[j], B[i]], mat)


def stroke(points, r, mat, n=6):
    for a, b in zip(points, points[1:]):
        tube(a, b, r, mat, n)


def arch(cx, cy, z, width, depth, height, r, mat, spring=None):
    # Front and back spandrels extend to the inner arch; opening passes through the wall.
    h = spring if spring is not None else height - r - 0.18
    xs = [-width / 2, -r] + [r * cos(pi - i * pi / 10) for i in range(1, 10)] + [r, width / 2]
    ys = [0, h] + [h + r * sin(pi - i * pi / 10) for i in range(1, 10)] + [h, 0]
    for k in range(len(xs) - 1):
        ax, bx = xs[k : k + 2]
        lo, hi = ys[k : k + 2]
        if k in (0, len(xs) - 2):
            lo = hi = 0
        yf = cy - depth / 2
        yb = cy + depth / 2
        p = [
            (cx + ax, yf, z + lo),
            (cx + bx, yf, z + hi),
            (cx + bx, yf, z + height),
            (cx + ax, yf, z + height),
        ]
        q = [(x, yb, zz) for x, y, zz in p]
        face(p, mat)
        face(q[::-1], mat)
        face([p[0], q[0], q[1], p[1]], mat)
        face([p[3], p[2], q[2], q[3]], mat)
    for sign in [-1, 1]:
        for xx, hh in [(cx + sign * width / 2, height), (cx + sign * r, h)]:
            face(
                [
                    (xx, cy - depth / 2, z),
                    (xx, cy + depth / 2, z),
                    (xx, cy + depth / 2, z + hh),
                    (xx, cy - depth / 2, z + hh),
                ],
                mat,
            )


def panel(x, y, z, w, h, mat, yaxis=False):
    pts = [
        (x - w / 2, y, z - h / 2),
        (x + w / 2, y, z - h / 2),
        (x + w / 2, y, z + h / 2),
        (x - w / 2, y, z + h / 2),
    ]
    if yaxis:
        pts = [(x + (yy - y), y + (xx - x), zz) for xx, yy, zz in pts]
    face(pts, mat, [(0, 0), (1, 0), (1, 1), (0, 1)])


def roof(x, y, z, w, d, h, mat="slate", eave=0.22):
    # Four curved tile pitches plus lifted overhanging corners.
    ridge = max(0.14, (w - d * 0.78) / 2)
    beamz = z + h
    spans = [
        ((x - w / 2, y - d / 2), (x + w / 2, y - d / 2), (x - ridge, y), (x + ridge, y)),
        ((x + w / 2, y - d / 2), (x + w / 2, y + d / 2), (x + ridge, y), (x + ridge + 0.001, y)),
        ((x + w / 2, y + d / 2), (x - w / 2, y + d / 2), (x + ridge, y), (x - ridge, y)),
        ((x - w / 2, y + d / 2), (x - w / 2, y - d / 2), (x - ridge, y), (x - ridge - 0.001, y)),
    ]
    for A, B, C, D in spans:
        rows = []
        for j in range(5):
            v = j / 4
            row = []
            for i in range(9):
                u = i / 8
                X = A[0] * (1 - u) + B[0] * u
                Y = A[1] * (1 - u) + B[1] * u
                tx = C[0] * (1 - u) + D[0] * u
                ty = C[1] * (1 - u) + D[1] * u
                row.append(
                    (
                        X * (1 - v) + tx * v,
                        Y * (1 - v) + ty * v,
                        z + h * (v**1.35) + eave * abs(2 * u - 1) ** 4 * (1 - v),
                    )
                )
            rows.append(row)
        for j in range(4):
            for i in range(8):
                face(
                    [rows[j][i], rows[j][i + 1], rows[j + 1][i + 1], rows[j + 1][i]],
                    mat,
                    [
                        (i / 2, j / 3),
                        ((i + 1) / 2, j / 3),
                        ((i + 1) / 2, (j + 1) / 3),
                        (i / 2, (j + 1) / 3),
                    ],
                )
        for i in range(8):
            a, b = rows[0][i : i + 2]
            face([a, (a[0], a[1], a[2] - 0.12), (b[0], b[1], b[2] - 0.12), b], mat)
    tube((x - ridge, y, beamz), (x + ridge, y, beamz), 0.10, mat, 8)


def stairs(x, y, z, width, depth, height, n, mat="marble"):
    # Ascends along +Y; one continuous cross section with true step profile.
    dy = depth / n
    dz = height / n
    for i in range(n):
        y0 = y + i * dy
        face(
            [
                (x - width / 2, y0, z + i * dz),
                (x + width / 2, y0, z + i * dz),
                (x + width / 2, y0, z + (i + 1) * dz),
                (x - width / 2, y0, z + (i + 1) * dz),
            ],
            mat,
        )
        face(
            [
                (x - width / 2, y0, z + (i + 1) * dz),
                (x + width / 2, y0, z + (i + 1) * dz),
                (x + width / 2, y0 + dy, z + (i + 1) * dz),
                (x - width / 2, y0 + dy, z + (i + 1) * dz),
            ],
            mat,
        )
        for side in [-1, 1]:
            xx = x + side * width / 2
            face(
                [
                    (xx, y0, z),
                    (xx, y0 + dy, z),
                    (xx, y0 + dy, z + (i + 1) * dz),
                    (xx, y0, z + (i + 1) * dz),
                ],
                mat,
            )


def fence(x0, x1, y, z, mat="marble", n=12, h=0.55):
    for i in range(n + 1):
        xx = x0 + (x1 - x0) * i / n
        box(xx, y, z, 0.14, 0.14, h, mat)
        lathe(xx, y, [(0.11, z + h), (0.09, z + h + 0.07), (0.03, z + h + 0.12)], mat, 6)
    for zz in [0.19, h * 0.73]:
        box((x0 + x1) / 2, y, z + zz, x1 - x0, 0.09, 0.075, mat)


def mountain(length, width, height_fn, nx=30, ny=14):
    tag("山脊与植被")
    pts = []
    for iy in range(ny + 1):
        v = iy / ny
        row = []
        for ix in range(nx + 1):
            u = ix / nx
            x = (u - 0.5) * length
            y = (v - 0.5) * width
            z = max(0.12, height_fn(x, y))
            row.append((x, y, z))
        pts.append(row)
    for iy in range(ny):
        for ix in range(nx):
            a, b = pts[iy][ix : ix + 2]
            d, c = pts[iy + 1][ix : ix + 2]
            mat = (
                "grass"
                if (max(abs(a[2] - d[2]), abs(a[2] - b[2])) < 1.35 + (sin(ix * 0.7 + iy) * 0.3))
                else "rock"
            )
            face([a, b, c], mat)
            face([a, c, d], mat)
    for side in [pts[0], pts[-1], [r[0] for r in pts], [r[-1] for r in pts]]:
        for a, b in zip(side, side[1:]):
            face([a, b, (b[0], b[1], 0), (a[0], a[1], 0)], "rock")


def create_objects():
    mats = {}

    def material(k):
        if k in mats:
            return mats[k]
        col, texture = PALETTE[k]
        mat = bpy.data.materials.new(k)
        mat.use_nodes = True
        rgb = [int(col[i : i + 2], 16) / 255 for i in [1, 3, 5]]
        rgb = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
        shader = mat.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = (*rgb, 1)
        mat.diffuse_color = (*rgb, 1)
        shader.inputs["Roughness"].default_value = 0.42 if k in ["gold", "metal", "water"] else 0.76
        if texture:
            fp = next((ROOT / "textures").glob(texture + ".*"))
            img = bpy.data.images.load(str(fp), check_existing=True)
            img.pack()
            t = mat.node_tree.nodes.new("ShaderNodeTexImage")
            t.image = img
            mat.node_tree.links.new(t.outputs["Color"], shader.inputs["Base Color"])
        mats[k] = mat
        return mat

    for name, items in parts.items():
        verts = []
        fs = []
        uvs = []
        which = []
        keys = list(dict.fromkeys(mat for ps, mat, uv in items))
        for ps, mat, uv in items:
            fs.append(list(range(len(verts), len(verts) + len(ps))))
            verts.extend(ps)
            uvs.append(uv)
            which.append(keys.index(mat))
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(verts, [], fs)
        mesh.update()
        o = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(o)
        for k in keys:
            mesh.materials.append(material(k))
        layer = mesh.uv_layers.new(name="材质UV")
        for poly, uv, im in zip(mesh.polygons, uvs, which):
            poly.material_index = im
            for n, pair in zip(poly.loop_indices, uv):
                layer.data[n].uv = pair
    return mats
