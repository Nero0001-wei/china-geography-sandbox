"""Individual scenes for nine identifiable Chinese landmarks."""

import math, random
from math import sin, cos, pi, tau
from geometry import (
    tag,
    at,
    box,
    lathe,
    tube,
    stroke,
    face,
    panel,
    arch,
    roof,
    stairs,
    fence,
    mountain,
)


def boulder(x, y, z, r, height, angle):
    # Irregular tapered outcrop with a flattened, sloping top and exposed faces.
    low = []
    mid = []
    top = []
    for i in range(7):
        t = angle + i * tau / 7
        rr = r * (0.84 + 0.16 * sin(i * 4.37 + angle))
        dx = rr * cos(t)
        dy = rr * 0.72 * sin(t)
        low.append((x + 1.1 * dx, y + 1.1 * dy, z - 0.22 * height))
        mid.append((x + dx, y + dy, z + height * (0.35 + 0.15 * cos(t))))
        top.append(
            (
                x + 0.64 * dx + 0.14 * r,
                y + 0.59 * dy + 0.12 * r,
                z + height * (0.77 + 0.22 * cos(t)),
            )
        )
    for ring, other, m in [(low, mid, "rock"), (mid, top, "rock")]:
        for i in range(7):
            face([ring[i], ring[(i + 1) % 7], other[(i + 1) % 7], other[i]], m)
    face(top, "stone")


def pine(x, y, z, height, angle):
    tube((x, y, z - 0.12), (x, y, z + height * 0.65), 0.065 * height, "wood", 6)
    for i in range(2):
        k = i * 0.27
        lathe(
            x + 0.035 * i,
            y,
            [
                (0.28 * height, z + height * (0.25 + k)),
                (0.4 * height, z + height * (0.41 + k)),
                (0.21 * height, z + height * (0.61 + k)),
                (0.04 * height, z + height * (0.83 + k)),
            ],
            "foliage",
            7,
            angle + i * 0.31,
        )


def badaling():
    def cy(x):
        return 0.55 * sin(x * 0.43)

    def ht(x):
        return 2.55 + 0.09 * x + 0.58 * sin(x * 0.48) + 0.30 * sin(x * 0.94)

    def h(x, y):
        d = abs(y - cy(x))
        return max(
            0.12,
            ht(x)
            - 0.52 * d
            + min(1, d / 2) * (0.32 * sin(x * 0.86 + y) + 0.17 * cos(x * 1.24 - y * 2.20)),
        )

    mountain(22, 7.4, h, 40, 15)
    tag("山脊岩石与树丛")
    rng = random.Random(114)
    for i in range(38):
        x = rng.uniform(-10.5, 10.5)
        y = rng.choice([-1, 1]) * rng.uniform(1.28, 3.32)
        if i % 3 == 0:
            pine(x, y, h(x, y), rng.uniform(0.37, 0.76), rng.uniform(0, tau))
        else:
            boulder(
                x, y, h(x, y), rng.uniform(0.32, 0.67), rng.uniform(0.19, 0.51), rng.uniform(0, tau)
            )
    tag("北四楼与城墙")
    for k in range(48):
        x = -10.3 + k * 0.43
        xx = x + 0.432
        z = ht(x)
        zz = ht(xx)
        y = cy(x)
        yy = cy(xx)
        for side in [-1, 1]:
            ya = y + side * 0.57
            yb = yy + side * 0.57
            face(
                [
                    (x, ya, max(0.02, h(x, ya) - 0.2)),
                    (xx, yb, max(0.02, h(xx, yb) - 0.2)),
                    (xx, yb, zz + 0.96),
                    (x, ya, z + 0.96),
                ],
                "stone",
            )
            a = math.atan2(yy - y, xx - x)
            length = math.hypot(xx - x, yy - y)
            with at((x + xx) / 2, (ya + yb) / 2, a):
                box(0, 0, (z + zz) / 2 + 0.82, length + 0.015, 0.15, 0.23, "stone")
                if k % 2 == 0:
                    box(0, 0, (z + zz) / 2 + 1.02, length * 0.85, 0.18, 0.3, "stone")
        face(
            [
                (x, y - 0.55, z + 0.69),
                (xx, yy - 0.55, zz + 0.69),
                (xx, yy + 0.55, zz + 0.69),
                (x, y + 0.55, z + 0.69),
            ],
            "marble",
        )

    for x in [-10.3, -10.3 + 47 * 0.43 + 0.432]:
        y, z = cy(x), ht(x)
        face(
            [
                (x, y - 0.57, max(0.02, h(x, y - 0.57) - 0.18)),
                (x, y + 0.57, max(0.02, h(x, y + 0.57) - 0.18)),
                (x, y + 0.57, z + 0.69),
                (x, y - 0.57, z + 0.69),
            ],
            "stone",
        )

    def tower(x):
        y = cy(x)
        z = ht(x) + 0.43
        with at(x, y):
            box(0, 0, max(0.03, z - 2), 2.64, 2.1, z + 0.63 - max(0.03, z - 2), "stone")
            for yy in [-0.89, 0.89]:
                for xx in [-0.62, 0.62]:
                    arch(xx, yy, z + 0.62, 1.25, 0.27, 1.18, 0.32, "stone", 0.63)
            for xx in [-1.12, 1.12]:
                box(xx, 0, z + 0.62, 0.24, 1.62, 1.18, "stone")
            box(0, 0, z + 1.79, 2.7, 2.2, 0.24, "sandstone")
            for j in range(7):
                for yy in [-1, 1]:
                    box(-1.12 + j * 0.375, yy, z + 2, 0.23, 0.21, 0.32, "stone")
            for j in range(4):
                for xx in [-1.23, 1.23]:
                    box(xx, -0.64 + 0.4 * j, z + 2, 0.22, 0.24, 0.32, "stone")

    tower(0)
    tower(-7.4)


def universal():
    tag("环形喷泉")
    lathe(
        0,
        0,
        [
            (5.2, 0),
            (5.28, 0.15),
            (5.25, 0.29),
            (4.9, 0.32),
            (4.88, 0.48),
            (4.55, 0.49),
            (4.50, 0.58),
        ],
        "marble",
        56,
    )
    lathe(0, 0, [(4.52, 0.51), (4.51, 0.61)], "water", 64)
    lathe(0, 0, [(2.18, 0.58), (1.8, 0.81), (0.9, 1.02), (0.65, 1.4)], "metal", 32)
    tag("地球仪与大陆")
    n = 44
    nr = 23
    R = 2.78
    zc = 3.6

    def sph(i, j):
        a = i * tau / n
        b = -pi / 2 + j * pi / nr
        return (R * cos(b) * sin(a), -R * cos(b) * cos(a), zc + R * sin(b))

    for i in range(n):
        for j in range(nr):
            face(
                [sph(i, j), sph(i + 1, j), sph(i + 1, j + 1), sph(i, j + 1)],
                "world",
                [
                    (0.58 + i / n, j / nr),
                    (0.58 + (i + 1) / n, j / nr),
                    (0.58 + (i + 1) / n, (j + 1) / nr),
                    (0.58 + i / n, (j + 1) / nr),
                ],
            )
    tag("地球环带")
    for i in range(72):
        a = i * tau / 72
        b = (i + 1) * tau / 72

        def band(t, delta):
            return (2.94 * sin(t), -2.94 * cos(t), 3.57 + 0.65 * sin(t) + delta)

        face([band(a, -0.24), band(b, -0.24), band(b, 0.24), band(a, 0.24)], "ink")
        for z in [-0.24, 0.24]:
            tube(band(a, z), band(b, z), 0.038, "gold", 5)
    # Text is a semantic part of the sculptural band and wraps around the blue sphere.
    import bpy

    for i, ch in enumerate("UNIVERSAL"):
        t = (i - 4) * 0.218
        bpy.ops.object.text_add(location=(3.00 * sin(t), -3.00 * cos(t), 3.57 + 0.65 * sin(t)))
        obj = bpy.context.object
        obj.name = "金属环带字 " + ch
        obj.rotation_euler = (pi / 2, 0, t)
        cu = obj.data
        cu.body = ch
        cu.align_x = "CENTER"
        cu.align_y = "CENTER"
        cu.extrude = 0.038
        cu.size = 0.82
        cu.resolution_u = 3
        bpy.ops.object.convert(target="MESH")
        mat = bpy.data.materials.get("铂金环带字") or bpy.data.materials.new("铂金环带字")
        mat.diffuse_color = (0.78, 0.75, 0.62, 1)
        obj.data.materials.append(mat)
    tag("喷泉水柱")
    for i in range(18):
        a = i * tau / 18
        path = []
        for j in range(6):
            t = j / 5
            r = 3.42 + t * 0.66
            path.append((r * cos(a), r * sin(a), 0.62 + 0.49 * sin(t * pi)))
        stroke(path, 0.033, "ice", 4)


def cross(x, y, z, length=0.55):
    tube((x, y, z), (x, y, z + length), 0.035, "gold", 6)
    tube(
        (x - length * 0.24, y, z + length * 0.64),
        (x + length * 0.24, y, z + length * 0.64),
        0.029,
        "gold",
        6,
    )


def sophia():
    tag("砖石台阶与十字堂身")
    box(0, 0, 0, 12.8, 14.9, 0.23, "marble")
    box(0, 0, 0.23, 6.8, 8.5, 4.4, "redbrick")
    box(0, -0.05, 0.23, 10.6, 5.45, 3.58, "redbrick")
    for xx in [-4.52, 4.52]:
        lathe(xx, 0, [(1.78, 0.3), (1.78, 2.48), (1.58, 2.84)], "redbrick", 12)
        lathe(xx, 0, [(1.84, 2.83), (1.56, 3.3), (1.03, 3.68), (0.24, 4.1)], "copper", 12)
    for x in [-2.9, 2.9]:
        for y in [-3.58, 3.58]:
            box(x, y, 0.27, 1.69, 1.6, 3.76, "redbrick")
            box(x, y, 3.85, 1.88, 1.81, 0.22, "ivory")
            lathe(
                x,
                y,
                [(1.28, 4.05), (1.31, 4.19), (0.53, 5.48), (0.19, 5.64), (0.1, 5.84)],
                "copper",
                4,
                pi / 4,
            )
            cross(x, y, 5.82, 0.42)
    tag("中堂与铜绿洋葱穹顶")
    lathe(
        0,
        0.3,
        [(3.0, 4.09), (3.07, 4.32), (2.53, 4.82), (2.39, 5.02), (2.39, 6.32), (2.62, 6.44)],
        "redbrick",
        12,
    )
    for i in range(12):
        a = i * tau / 12
        with at(2.33 * sin(a), 0.3 - 2.33 * cos(a), a):
            box(0, 0, 5.13, 0.47, 0.18, 0.88, "window")
            tube((-0.28, -0.11, 5.11), (-0.28, -0.11, 6.0), 0.055, "ivory", 5)
            tube((0.28, -0.11, 5.11), (0.28, -0.11, 6.0), 0.055, "ivory", 5)
            box(0, -0.11, 6.03, 0.78, 0.15, 0.12, "ivory")
    levels = [
        (2.6, 6.39),
        (2.76, 6.49),
        (2.87, 6.85),
        (2.94, 7.2),
        (2.88, 7.68),
        (2.61, 8.24),
        (2.22, 8.73),
        (1.77, 9.10),
        (1.25, 9.46),
        (0.66, 9.82),
        (0.29, 10.1),
        (0.20, 10.45),
    ]
    lathe(0, 0.3, levels, "copper", 32)
    for k in range(16):
        a = k * tau / 16
        stroke([(r * cos(a), 0.3 + r * sin(a), z) for r, z in levels[1::2]], 0.028, "jade", 5)
    cross(0, 0.3, 10.45, 0.72)
    tag("门厅钟楼")
    for y in [-5.38]:
        arch(0, y, 0.32, 3.56, 2.15, 2.86, 0.83, "redbrick", 1.52)
        box(0, y, 3.17, 3.76, 2.47, 0.3, "ivory")
        arch(0, y, 3.46, 2.52, 1.78, 1.77, 0.65, "redbrick", 0.73)
        box(0, y, 5.19, 2.88, 2.27, 0.22, "ivory")
        lathe(
            0,
            y,
            [(1.94, 5.37), (1.78, 5.55), (0.62, 7.35), (0.38, 7.63), (0.16, 8.15)],
            "copper",
            4,
            pi / 4,
        )
        cross(0, y, 8.15, 0.53)
    for side in [-1, 1]:
        with at(side * 3.37, 0.2, side * pi / 2):
            for j in range(-2, 3):
                box(j * 1.05, -0.06, 1.14, 0.58, 0.18, 1.52, "window")
                box(j * 1.05, -0.13, 2.48, 0.13, 0.12, 0.36, "ivory")

    # Romanesque arched windows, stepped masonry and pilasters on the transepts.
    def window(x, y, z, w, h):
        # The dark arched glass is set behind a terracotta archivolt and a stone sill.
        r = w / 2
        spring = z + h - r
        pts = [(x - r, y, z), (x + r, y, z)] + [
            (x + r * cos(k * pi / 9), y, spring + r * sin(k * pi / 9)) for k in range(10)
        ]
        face(pts, "window")
        stroke(
            [(x + r * cos(k * pi / 9), y - 0.03, spring + r * sin(k * pi / 9)) for k in range(10)],
            0.054,
            "sandstone",
            5,
        )
        box(x, y - 0.06, z - 0.07, w + 0.15, 0.13, 0.12, "sandstone")
        box(x, y - 0.05, z, 0.055, 0.07, h - 0.08, "ivory")

    for sign in [-1, 1]:
        with at(sign * 4.52, 0.0, sign * pi / 2):
            for xx in [-0.83, 0, 0.83]:
                window(xx, -1.67, 1.03, 0.48, 1.55)
        with at(sign * 2.93, -4.44):
            window(0, -0.03, 1.35, 0.76, 1.62)
            for xx in [-0.67, 0.67]:
                box(xx, 0, 0.36, 0.18, 0.23, 3.23, "sandstone")
        for y0 in [-4.24, 4.24]:
            box(sign * 2.45, y0, 3.33, 1.68, 0.19, 0.13, "sandstone")
            box(sign * 2.45, y0, 3.58, 1.70, 0.21, 0.09, "sandstone")
    for x0 in [-1.36, 1.36]:
        box(x0, -6.52, 0.42, 0.26, 0.25, 2.61, "sandstone")
        box(x0, -6.52, 0.35, 0.43, 0.41, 0.22, "sandstone")
    # Front archivolt picks out the main entry at national-map zoom.
    stroke(
        [(0.87 * cos(k * pi / 12), -6.49, 1.84 + 0.87 * sin(k * pi / 12)) for k in range(13)],
        0.095,
        "sandstone",
        7,
    )
    stairs(0, -7.22, 0, 3.54, 0.9, 0.35, 5)


def qinhuai():
    tag("照壁与岸线")
    # The wall, not the distant boat or the center of the miniature, is anchored at the origin.
    box(0, -2.55, 0, 16, 6.8, 0.42, "sandstone")
    box(0, -3.4, 0.39, 15.85, 4.85, 0.14, "water")
    box(0, 0, 0.46, 13.9, 0.86, 2.63, "red")
    roof(0, 0, 3.11, 14.41, 1.29, 0.57, "slate", 0.2)
    panel(0, -0.437, 1.88, 10.94, 1.94, "dragon")
    for x in [-6.6, -5.78, 5.78, 6.6]:
        box(x, -0.1, 0.48, 0.29, 1, 2.78, "redbrick")
        box(x, -0.1, 0.42, 0.49, 1.14, 0.31, "sandstone")
    box(0, -0.59, 0.5, 14.5, 0.48, 0.34, "marble")
    tag("沿岸石栏")
    for x in [-6.65, 6.65]:
        with at(x, -2.0, pi / 2):
            fence(-1.5, 1.5, 0, 0.5, n=7, h=0.55)
    tag("秦淮画舫")

    def boat(x, y):
        # Slim pointed hull with genuine open bays and a dark tiled canopy.
        for sign in [-1, 1]:
            points = [
                (x - 3.35, y, 0.82),
                (x - 2.45, y + 0.63 * sign, 0.68),
                (x + 2.05, y + 0.67 * sign, 0.68),
                (x + 3.45, y, 0.87),
            ]
            rim = [(a, b, c + 0.34) for a, b, c in points]
            for j in range(3):
                face([points[j], points[j + 1], rim[j + 1], rim[j]], "wood")
        box(x, y, 0.83, 4.35, 1.11, 0.31, "ochre")
        for xx in [-1.96, -1.18, -0.4, 0.4, 1.18, 1.96]:
            for yy in [-0.47, 0.47]:
                tube((x + xx, y + yy, 1.08), (x + xx, y + yy, 2.09), 0.067, "red", 8)
        roof(x, y, 2.06, 4.54, 1.59, 0.44, "slate", 0.2)
        for yy in [-0.49, 0.49]:
            fence(x - 2.15, x + 2.15, y + yy, 1.05, "gold", n=10, h=0.34)

    boat(0.75, -3.84)
    tag("两端岸柳")
    for i, x in enumerate([-7.18, 7.14]):
        y = -1.04
        z = 0.52
        height = 2.03
        tube((x, y, z), (x + 0.08, y + 0.06, z + height), 0.105, "wood", 7)
        for j in range(9):
            ang = j * tau / 9 + i
            ex = x + 0.69 * cos(ang)
            ey = y + 0.54 * sin(ang)
            h = z + height + 0.23 * sin(j * 2)
            stroke(
                [
                    (x, y, z + 1.48),
                    (ex, ey, h),
                    (ex + 0.14 * cos(ang), ey + 0.12 * sin(ang), h - 0.82 - 0.18 * cos(j)),
                ],
                0.077,
                "foliage",
                6,
            )
            lathe(
                ex,
                ey,
                [(0.13, h - 0.53), (0.28, h - 0.24), (0.33, h), (0.16, h + 0.21)],
                "foliage",
                7,
                ang,
            )
    tag("水岸瓦垄")
    for i in range(40):
        x = -6.8 + i * 0.35
        tube((x, -0.08, 3.65), (x, -0.59, 3.19), 0.047, "slate", 6)
        tube((x, 0.08, 3.65), (x, 0.59, 3.19), 0.047, "slate", 6)


def bund():
    tag("滨江石座")
    box(-1.15, 0, 0, 16.7, 6.45, 0.32, "marble")
    box(-1.15, -3.67, 0.02, 16.7, 1.0, 0.20, "water")

    def fac(x, y, z, w, d, stories, n):
        box(x, y, z, w, d, stories * 0.64 + 0.55, "sandstone")
        for floor in range(stories):
            zz = z + 0.27 + floor * 0.64
            for col in range(n):
                xx = x + (col + 0.5) * w / n - w / 2
                box(xx, y - d / 2 - 0.025, zz, 0.50, 0.07, 0.42, "window")
                if floor % 2 == 0:
                    box(xx, y - d / 2 - 0.074, zz + 0.48, 0.61, 0.10, 0.07, "ivory")
        for side in [-1, 1]:
            with at(x + side * w / 2, y, side * pi / 2):
                for f in range(stories):
                    for j in range(4):
                        panel((j - 1.5) * d / 4, -0.024, z + 0.47 + f * 0.64, 0.41, 0.42, "window")
        for k in [0, stories // 2, stories]:
            box(x, y, z + 0.15 + k * 0.64, w + 0.17, d + 0.16, 0.14, "marble")

    tag("海关大楼与四面钟")
    fac(0, 0, 0.32, 6.5, 4.25, 6, 8)
    for x in [-2.22, -1.33, -0.44, 0.44, 1.33, 2.22]:
        tube((x, -2.32, 0.44), (x, -2.32, 2.08), 0.18, "marble", 10)
        box(x, -2.32, 2.08, 0.48, 0.48, 0.13, "ivory")
    box(0, -2.23, 2.2, 5.64, 0.72, 0.32, "marble")
    box(0.13, -0.52, 4.7, 3.52, 2.98, 0.43, "marble")
    fac(0.13, -0.52, 5.12, 2.56, 2.29, 3, 3)
    box(0.13, -0.52, 7.44, 2.6, 2.42, 2.05, "sandstone")
    for ang in [0, pi / 2, pi, 3 * pi / 2]:
        with at(0.13, -0.52, ang):
            panel(0, -(1.32 if ang in [pi / 2, 3 * pi / 2] else 1.23), 8.43, 1.54, 1.54, "clock")
    box(0.13, -0.52, 9.43, 2.85, 2.56, 0.27, "marble")
    lathe(0.13, -0.52, [(1.64, 9.68), (0.99, 10.16), (0.46, 10.32)], "slate", 4, pi / 4)
    tube((0.13, -0.52, 10.32), (0.13, -0.52, 11.04), 0.055, "gold", 7)
    tag("原汇丰银行与铜穹顶")
    fac(-6.2, 0.12, 0.32, 5.8, 4.24, 4, 7)
    for xx in [-7.79, -7, -6.19, -5.39, -4.59]:
        tube((xx, -2.13, 0.44), (xx, -2.13, 2.6), 0.19, "marble", 12)
    box(-6.19, -2.12, 2.65, 4.39, 0.86, 0.32, "marble")
    lathe(-6.18, 0.12, [(1.58, 3.37), (1.65, 3.51), (1.44, 3.70), (1.39, 4.16)], "marble", 20)
    lathe(
        -6.18,
        0.12,
        [
            (1.52, 4.12),
            (1.56, 4.24),
            (1.47, 4.57),
            (1.23, 4.89),
            (0.84, 5.12),
            (0.33, 5.3),
            (0.22, 5.59),
            (0.09, 5.68),
        ],
        "copper",
        22,
    )
    tag("钟楼北侧相邻街面")
    fac(4.99, 0.14, 0.32, 3.32, 4.04, 5, 4)


def disney():
    tag("基座与正门拱廊")
    lathe(0, 0.15, [(5.5, 0), (5.61, 0.15), (5.28, 0.39)], "marble", 12, pi / 12, 0.76)
    arch(0, -2.12, 0.37, 5.29, 1.10, 3.39, 1.05, "pink", 1.4)
    arch(0, -2.74, 0.4, 3.12, 0.25, 3.15, 1.04, "ivory", 1.38)
    box(0, 0.0, 2.14, 5.14, 3.4, 2.29, "pink")
    box(0, 0.0, 4.3, 5.25, 3.49, 0.21, "ivory")
    roof(0, 0.2, 4.47, 5.35, 3.65, 1.55, "blue", 0.06)
    tag("不等高塔身与旗尖")

    def turret(x, y, r, z, h, cap, mat):
        levels = [
            (r * 1.08, z),
            (r * 1.12, z + 0.16),
            (r, z + 0.32),
            (r, z + h * 0.68),
            (r * 1.11, z + h * 0.70),
            (r * 1.18, z + h * 0.76),
            (r * 1.18, z + h * 0.96),
            (r * 1.31, z + h),
        ]
        lathe(x, y, levels, mat, 12, pi / 12)
        for zc in [z + 0.33, z + h * 0.69, z + h * 0.95]:
            lathe(x, y, [(r * 1.15, zc), (r * 1.2, zc + 0.08)], "ivory", 12, pi / 12)
        for j in range(6):
            a = j * tau / 6
            with at(x + (r * 1.15) * sin(a), y - (r * 1.15) * cos(a), a):
                panel(0, -0.01, z + h * 0.84, r * 0.29, max(0.31, h * 0.13), "window")
        top = z + h
        lathe(
            x,
            y,
            [
                (r * 1.36, top),
                (r * 1.24, top + 0.16),
                (r * 0.86, top + cap * 0.34),
                (r * 0.50, top + cap * 0.57),
                (r * 0.25, top + cap * 0.83),
                (0.055, top + cap),
            ],
            "blue",
            14,
            pi / 14,
        )
        tube((x, y, top + cap - 0.03), (x, y, top + cap + 0.36), 0.031, "gold", 6)
        face(
            [(x, y, top + cap + 0.32), (x + 0.47, y, top + cap + 0.28), (x, y, top + cap + 0.09)],
            "gold",
        )

    for x, y, r, z, h, cap, col in [
        (0, 0.68, 1.14, 2.14, 5.44, 3.4, "pink"),
        (-1.6, 0.76, 0.76, 0.36, 6.43, 2.38, "pink"),
        (1.8, 1.05, 0.75, 0.36, 6, 2.17, "pink"),
        (-3.14, -0.78, 0.83, 0.36, 4.55, 2.09, "pink"),
        (3.06, -1.06, 0.85, 0.36, 5.13, 2.4, "pink"),
        (-2.05, -2.54, 0.56, 0.37, 3.3, 1.76, "ivory"),
        (1.98, -2.65, 0.58, 0.37, 3.64, 1.78, "pink"),
        (0.88, -0.87, 0.52, 3.68, 2.38, 1.6, "ivory"),
    ]:
        turret(x, y, r, z, h, cap, col)
    tag("正门尖山花")
    for y in [-2.7, -2.85]:
        face([(-1.2, y, 3.47), (1.2, y, 3.47), (0, y, 5.43)], "pink")
    for s in [-1, 1]:
        tube((s * 1.22, -2.88, 3.46), (0, -2.88, 5.45), 0.09, "gold", 6)
    lathe(0, -2.51, [(0.25, 5.09), (0.15, 5.47), (0.05, 5.91)], "gold", 8)


def westlake():
    tag("西湖湖面")
    lathe(0, 0, [(7.93, 0), (8, 0.12), (7.94, 0.23)], "water", 48, 0, 0.75)
    tag("三塔与湖面倒影")
    # Map east points to +X. Compress the triangle uniformly and enlarge each tower for the national view.
    for x, y in [(3.68, 0.71), (-1.86, 3.53), (-1.41, -2.69)]:
        z = 0.24
        lathe(
            x,
            y,
            [
                (0.71, z),
                (0.75, z + 0.12),
                (0.59, z + 0.24),
                (0.43, z + 0.38),
                (0.39, z + 0.57),
                (0.60, z + 0.68),
            ],
            "marble",
            32,
        )
        # Five circular openings in the curved, hollow lantern. Mesh each panel as an annulus with an aperture.
        steps = 16
        n = 5
        mid = z + 1.17
        for j in range(n):
            a = j * tau / n - pi / 2
            pv = []
            for k in range(steps):
                t = k * tau / steps
                u = cos(t)
                v = sin(t)
                boxrad = max(abs(u), abs(v))
                tang = u / boxrad * pi / 5
                dz = v / boxrad * 0.52
                b = a + tang
                r = 0.86 * math.sqrt(max(0.01, 1 - (dz / 0.76) ** 2))
                outer = (x + r * cos(b), y + r * sin(b), mid + dz)
                da = u * 0.29
                dr = v * 0.23
                ri = 0.86 * math.sqrt(1 - (dr / 0.76) ** 2)
                inner = (x + ri * cos(a + da), y + ri * sin(a + da), mid + dr)
                deep = (x + (ri - 0.11) * cos(a + da), y + (ri - 0.11) * sin(a + da), mid + dr)
                pv.append((outer, inner, deep))
            for k in range(steps):
                o, i, d = pv[k]
                O, I, D = pv[(k + 1) % steps]
                face([o, O, I, i], "marble")
                face([i, I, D, d], "stone")
        lathe(
            x,
            y,
            [
                (0.64, mid + 0.50),
                (0.58, mid + 0.61),
                (0.88, mid + 0.68),
                (1.07, mid + 0.78),
                (0.94, mid + 0.85),
                (0.68, mid + 1.00),
                (0.37, mid + 1.12),
            ],
            "marble",
            32,
        )
        lathe(
            x,
            y,
            [
                (0.36, mid + 1.1),
                (0.26, mid + 1.2),
                (0.31, mid + 1.30),
                (0.28, mid + 1.42),
                (0.14, mid + 1.52),
                (0.18, mid + 1.62),
                (0.10, mid + 1.72),
                (0.04, mid + 1.78),
            ],
            "stone",
            24,
        )
        for rr in [1.05, 1.37]:
            for k in range(20):
                a = k * tau / 20
                b = (k + 0.86) * tau / 20
                tube(
                    (x + rr * cos(a), y + rr * sin(a), 0.25),
                    (x + rr * cos(b), y + rr * sin(b), 0.25),
                    0.012,
                    "ice",
                    4,
                )


def hengdian():
    tag("广场和层层夯土高台")
    box(0, -1.25, 0, 17.2, 13.1, 0.18, "sandstone")
    for x, y, w, d, z, h in [
        (0, 0.3, 13.2, 6.5, 0.18, 0.77),
        (0, 0.57, 12.3, 5.8, 0.95, 0.70),
        (0, 0.6, 11.7, 5.4, 1.65, 0.62),
    ]:
        box(x, y, z, w, d, h, "redbrick")
        box(x, y, z + h - 0.08, w + 0.2, d + 0.17, 0.18, "marble")
    stairs(0, -5.58, 0.18, 4.35, 3.64, 2.24, 22)
    tag("四海归一殿")
    box(0, 0.81, 2.31, 9.43, 3.7, 2.15, "wood")
    for x in [-4.95, -3.97, -2.98, -1.98, -0.99, 0, 0.99, 1.98, 2.98, 3.97, 4.95]:
        for y in [-1.6, 2.69]:
            tube((x, y, 2.38), (x, y, 4.46), 0.15, "red", 8)
        if x > -4.94:
            panel(x - 0.48, -1.065, 3.40, 0.67, 1.42, "ink")
    for z, w, d, m in [(4.47, 11.08, 5.32, "red"), (4.60, 11.38, 5.57, "ochre")]:
        box(0, 0.6, z, w, d, 0.16, m)
    roof(0, 0.58, 4.76, 12.48, 6.17, 1.70, "slate", 0.1)
    box(0, 0.59, 5.70, 7.48, 3.16, 0.96, "red")
    roof(0, 0.59, 6.68, 8.92, 4.20, 1.48, "slate", 0.07)
    panel(0, -1.02, 6.15, 2.08, 0.52, "qin")
    for side in [-1, 1]:
        tag("阙楼 " + str(side))
        xx = side * 6.83
        box(xx, -4.83, 0.18, 1.84, 2.34, 1.75, "redbrick")
        box(xx, -4.82, 1.86, 2, 2.47, 0.23, "stone")
        box(xx, -4.83, 2.07, 1.16, 1.48, 1.33, "wood")
        roof(xx, -4.83, 3.37, 2.38, 2.13, 0.99, "slate", 0.1)
    for x in [-5, 5]:
        with at(x, 0.45, pi / 2):
            fence(-2.33, 2.33, 0, 2.33, n=11, h=0.37)
    tag("台基石栏")
    fence(-6, -2.25, -2.37, 1.72, n=11, h=0.48)
    fence(2.25, 6, -2.37, 1.72, n=11, h=0.48)


def taishan():
    def slope(x, y):
        walkway = 3.75 + 0.50 * min(y, 1.25) - 0.38 * max(0, y - 1.25)
        outer = max(0, abs(x) - 1.63)
        shoulder = outer * (0.40 + 0.29 * sin(y * 0.76 + x * 0.98)) + 0.39 * sin(
            x * 1.3 - y * 0.55
        ) * min(1, outer)
        return max(0.12, walkway + shoulder)

    mountain(12.0, 15.2, slope, 29, 39)
    tag("山道两侧花岗岩")
    rng = random.Random(51)
    for i in range(46):
        x = rng.choice([-1, 1]) * rng.uniform(2.0, 5.76)
        y = rng.uniform(-7.1, 6.96)
        boulder(
            x, y, slope(x, y), rng.uniform(0.38, 0.84), rng.uniform(0.24, 0.66), rng.uniform(0, tau)
        )
    tag("十八盘末段")
    # Center the gate above the survey origin; stairs run downhill to the south.
    stairs(0, -7.53, 0.02, 2.7, 7.5, 3.95, 42)
    for side in [-1, 1]:
        for j in range(22):
            y = -7.45 + j * 0.348
            z = max(0.11, slope(0, y)) + 0.22
            box(side * 1.53, y, z, 0.29, 0.365, 0.48, "marble")
    box(0, 0, 3.74, 5.53, 2.58, 0.33, "marble")
    tag("红墙门洞与上层门楼")
    arch(0, 0.08, 3.96, 5.36, 2.16, 2.35, 0.79, "red", 1.03)
    arch(0, -1.02, 3.96, 2.28, 0.15, 2.04, 0.78, "sandstone", 1.03)
    box(0, 0.08, 6.30, 5.62, 2.49, 0.17, "marble")
    box(0, 0.09, 6.45, 3.37, 1.65, 1.03, "redbrick")
    for x in [-1.75, -0.87, 0, 0.87, 1.75]:
        tube((x, -0.88, 6.46), (x, -0.88, 7.52), 0.09, "red", 7)
    for x in [-1.2, -0.4, 0.4, 1.2]:
        panel(x, -0.743, 6.98, 0.52, 0.71, "window")
    panel(0, -1.07, 6.02, 1.38, 0.46, "heaven")
    roof(0, 0.07, 7.49, 4.48, 2.82, 1.19, "goldroof", 0.30)
    # Greens remain on the flanking slopes, preserving the staircase silhouette.
    tag("山坡松林")
    rng = random.Random(43)
    for j in range(17):
        x = rng.choice([-1, 1]) * rng.uniform(2.2, 5.7)
        y = rng.uniform(-6.7, 6.3)
        z = slope(x, y)
        ht = rng.uniform(0.57, 1.18)
        tube((x, y, z - 0.06), (x, y, z + ht * 0.63), 0.052, "wood", 5)
        for k in range(2):
            lathe(
                x + k * 0.05,
                y,
                [
                    (0.41 * ht, z + ht * (0.30 + k * 0.28)),
                    (0.43 * ht, z + ht * (0.39 + k * 0.28)),
                    (0.19 * ht, z + ht * (0.62 + k * 0.28)),
                    (0.04, z + ht * (0.81 + k * 0.28)),
                ],
                "foliage",
                7,
                phase=rng.random(),
            )
