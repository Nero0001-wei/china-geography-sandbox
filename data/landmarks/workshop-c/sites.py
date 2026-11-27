"""Individual historic buildings, landscape sections and visitor viewpoints."""

from geometry import *
from math import sqrt, exp
import random


def lijiang():
    group("玉河·驳岸与水面")
    floorplan(
        0, 0, 0, [(-5, -3), (2, -3.1), (5, -2.5), (5.3, 2.6), (1, 3.4), (-5.1, 2.6)], 0.24, "ashlar"
    )
    box(0, -1.12, 0.24, 10, 0.0 + 2.6, 0.07, "water")
    for y in [-2.53, 0.29]:
        box(0, y, 0.24, 10, 0.22, 0.27, "granite")
    for i, (x, r) in enumerate([(-1.45, 2.05), (1.58, 1.34)]):
        z = 0.29 + r
        y = -0.9
        group("玉河·大水车" if i == 0 else "玉河·小水车")
        for yy in [y - 0.34, y + 0.34]:
            ring(x, yy, z, r, 0.103, "timber", 32, 5)
            ring(x, yy, z, r * 0.83, 0.075, "beam", 32, 5)
            for k in range(14):
                t = k * 2 * pi / 14
                cylinder((x, yy, z), (x + r * cos(t), yy, z + r * sin(t)), 0.085, 0.055, "beam", 5)
        cylinder((x, y - 0.8, z), (x, y + 0.8, z), 0.20, 0.20, "timber", 10)
        for k in range(18):
            a = k * pi / 9
            cylinder(
                (x + r * cos(a), y - 0.42, z + r * sin(a)),
                (x + r * cos(a), y + 0.42, z + r * sin(a)),
                0.12,
                0.12,
                "beam",
                5,
            )
        for yy in [y - 0.72, y + 0.72]:
            for xx in [x - r * 0.44, x + r * 0.44]:
                cylinder((xx, yy, 0.31), (x, yy, z), 0.11, 0.12, "timber", 5)
    group("纳西民居·瓦屋")
    for x, y, w, d, h in [
        (-3.25, 1.59, 3.3, 1.75, 1.35),
        (0.05, 1.7, 2.9, 1.9, 1.75),
        (3.12, 1.5, 2.92, 1.7, 1.5),
    ]:
        box(x, y, 0.28, w, d, h, "whitewash")
        hip(x, y, 0.28 + h, w + 0.56, d + 0.59, 0.86, "greyTile")
        for xx in [x - w * 0.45, x - w * 0.17, x + w * 0.17, x + w * 0.45]:
            box(xx, y - d / 2 - 0.03, 0.31, 0.1, 0.11, h - 0.03, "timber")
        for xx in [x - w * 0.31, x, x + w * 0.31]:
            window(xx, y - d / 2 - 0.07, 0.65, 0.52, 0.67)
        box(x, y - d / 2 - 0.08, h * 0.98, w, 0.12, 0.13, "timber")


def terraced_rock(x, y, z, rx, ry, h, mat, seed=81):
    rng = random.Random(seed)
    n = 24
    angles = [j * 2 * pi / n for j in range(n)]
    ridges = [rng.uniform(0.94, 1.08) for _ in angles]
    loops = []
    for t, k in [(0, 0.96), (0.12, 1), (0.38, 0.79), (0.65, 0.66), (1, 0.50)]:
        loops.append(
            [
                (
                    x + rx * k * ridges[j] * cos(a),
                    y + ry * k * ridges[j] * sin(a),
                    z + h * t + (0 if t == 0 else 0.10 * sin(a * 4 + t)),
                )
                for j, a in enumerate(angles)
            ]
        )
    face(loops[0][::-1], mat)
    face(loops[-1], mat)
    for i in range(4):
        for j in range(n):
            k = (j + 1) % n
            a, b = loops[i][j], loops[i][k]
            c, d = loops[i + 1][k], loops[i + 1][j]
            face([a, b, c], mat)
            face([a, c, d], mat)


def potala():
    group("红山·山体与雪城基座")
    terraced_rock(0, 0, 0, 6.35, 2.55, 2.05, "rock")
    group("白宫与红宫·收分墙体")
    volumes = [
        (-3.73, 0.12, 1.08, 3.8, 2.5, 1.78, "whitewash"),
        (3.43, 0.12, 1.10, 4.38, 2.76, 2.3, "whitewash"),
        (-2.25, 0.17, 2.1, 2.6, 2.17, 1.64, "whitewash"),
        (2.15, 0.02, 2.37, 3.0, 2.6, 1.55, "whitewash"),
        (-0.36, 0.32, 2.38, 4.14, 2.88, 2.56, "plum"),
        (-0.35, 0.55, 4.72, 2.67, 1.76, 0.54, "plum"),
    ]
    for x, y, z, w, d, h, mat in volumes:
        # Stepped stone podiums follow the slope below the two outer wings.
        if abs(x) > 3:
            profile(x, y, 0.05, [(0, w * 1.12, d * 1.20), (z - 0.05, w * 0.99, d * 0.985)], "rock")
        profile(x, y, z, [(0, w, d), (h, w * 0.91, d * 0.88)], mat)
        box(x, y, z + h - 0.09, w * 0.93, d * 0.92, 0.115, "dark")
        box(
            x, y, z + h + 0.024, w * 0.92, d * 0.91, 0.07, "whitewash" if mat == "whitewash" else "ochre"
        )
        n = max(3, int(w / 0.43))
        nr = max(2, round(h / 0.58))
        for a in range(n):
            for b in range(nr):
                t = (b + 0.54) / nr
                yy = y - d / 2 * (1 - 0.12 * t) - 0.025
                window(
                    x + w * 0.84 * ((a + 0.5) / n - 0.5),
                    yy,
                    z + h * (b + 0.21) / nr,
                    0.205,
                    0.235,
                    "dark",
                    "ochre" if (b + a) % 5 == 0 else "dark",
                )
        for side in [-1, 1]:
            for j in range(3):
                for row in range(2):
                    xx = x + side * w * 0.5 * (1 - 0.09 * (row + 0.45) / 2)
                    box(
                        xx,
                        y + (j - 1) * d * 0.25,
                        z + h * (0.18 + row * 0.41),
                        0.060,
                        0.18,
                        0.216,
                        "dark",
                    )
        box(x, y - d * 0.45, z + h - 0.20, w * 0.91, 0.12, 0.09, "plum")
    group("殿顶·铜鎏金屋面")
    for x, y, z, w in [
        (-1.27, 0.35, 5.28, 1.06),
        (0.2, 0.42, 5.35, 1.19),
        (-3.06, 0.17, 3.82, 0.90),
        (2.04, 0.2, 4.06, 0.91),
    ]:
        box(x, y, z, w * 0.73, 0.49, 0.26, "ochre")
        hip(x, y, z + 0.26, w, 0.75, 0.33, "goldTile", "gold")
        shaft(x, y, z + 0.49, 0.035, 0.27, "gold", 7)
    group("南立面·曲折登宫石阶")
    for xx, yy, w, h in [
        (-2.70, -1.60, 3.6, 0.56),
        (2.52, -1.67, 2.95, 0.57),
        (-1.79, -1.37, 2.71, 0.91),
    ]:
        profile(xx, yy - 0.05, 0.09, [(0, w, 0.46), (h, w * 0.94, 0.38)], "whitewash")
    for i, (x, y, z, w, rev) in enumerate(
        [
            (-2.46, -1.72, 0.22, 2.75, 1),
            (-1.45, -1.43, 0.69, 1.85, -1),
            (-2.2, -1.26, 0.98, 1.85, 1),
            (2.60, -1.84, 0.28, 2.35, -1),
            (2.1, -1.5, 0.75, 1.7, 1),
        ]
    ):
        for j in range(9):
            xx = x + (j - 4) * w / 9
            hh = 0.09 + ((j + 1) if rev > 0 else (9 - j)) * 0.046
            box(xx, y, z, w / 9 + 0.008, 0.32, hh, "whitewash")
            box(xx, y - 0.18, z + hh, w / 9 + 0.01, 0.07, 0.15, "whitewash")


def terracotta():
    group("一号坑·剖切夯土与甬道")
    box(0, 0, 0, 9.8, 7.9, 0.22, "rock")
    box(0, 0, 0.22, 9.68, 7.8, 0.15, "sand")
    for j in range(6):
        x = -4.54 + j * 1.82
        profile(
            x,
            0,
            0.35,
            [(0, 0.61, 7.62), (0.21, 0.55, 7.57), (0.55, 0.43, 7.46), (0.72, 0.33, 7.32)],
            "sand",
        )
        for k in range(13):
            z = 0.64 + 0.07 * math.sin(k * 2 + j)
            box(x, (-6 + k) * 0.53, z, 0.44, 0.28, 0.1, "rock")
    box(0, 3.71, 0.35, 9.54, 0.37, 0.61, "sand")
    for j in range(5):
        group("陶俑军阵·第%d列" % (j + 1))
        for k in range(6):
            x = (j - 2) * 1.82 + 0.075 * sin(k * 2 + j)
            y = -2.94 + k * 1.08
            z = 0.37
            a = ["clay", "clayLight", "clayDark"][(j + k * 2) % 3]
            for dx in [-0.13, 0.13]:
                box(x + dx, y - 0.045, z, 0.16, 0.32, 0.10, a)
                shaft(x + dx, y, z + 0.09, 0.085, 0.28, a, 5, 0.115)
            profile(x, y, z + 0.33, [(0, 0.52, 0.33), (0.31, 0.39, 0.28), (0.64, 0.53, 0.3)], a)
            box(x, y - 0.143, z + 0.59, 0.41, 0.03, 0.34, "clayDark")
            for row in range(3):
                box(x, y - 0.165, z + 0.64 + row * 0.09, 0.35, 0.035, 0.022, a)
            for dx in [-1, 1]:
                cylinder(
                    (x + dx * 0.22, y, z + 0.91),
                    (x + dx * 0.29, y - 0.035, z + 0.66),
                    0.088,
                    0.074,
                    a,
                    5,
                )
                cylinder(
                    (x + dx * 0.29, y - 0.035, z + 0.66),
                    (x + dx * 0.23, y - 0.19, z + 0.54),
                    0.074,
                    0.059,
                    a,
                    5,
                )
            sphere(x, y, z + 1.11, 0.166, 0.14, 0.192, a, 7, 4)
            sphere(x + 0.026, y + 0.016, z + 1.29, 0.087, 0.089, 0.10, "clayDark", 6, 3)
            box(x, y - 0.132, z + 1.075, 0.055, 0.055, 0.072, a)


def tang():
    group("芙蓉池·露台与湖岸")
    box(0, -0.58, 0, 9.4, 6.3, 0.18, "ashlar")
    box(0, -2.2, 0.18, 9.31, 2.86, 0.05, "water")
    box(0, 0.29, 0.17, 7.77, 4.25, 0.39, "marble")
    steps(0, -2.28, 0.23, 2.05, 0.80, 0.34, 6, "marble")
    group("高台·台座底层与城门")
    profile(0, 0.36, 0.55, [(0, 7.58, 3.84), (0.9, 7.30, 3.60)], "ochre")
    box(0, 0.36, 1.41, 7.65, 3.91, 0.08, "marble")
    for a in [-1, 1]:
        for j in range(4):
            box(a * (1 + j * 0.55), -1.48, 0.66, 0.11, 0.07, 0.49, "dark")
    # The visitor sees a grey-tiled timber pavilion rising above the fourth storey within the platform.
    for i, (z, w, d, h) in enumerate(
        [(0.56, 6.7, 3.45, 1.05), (2.36, 5.14, 2.7, 0.88), (3.92, 3.73, 2.04, 0.82)]
    ):
        z += 0.94
        group("紫云楼·第%d层" % (i + 2))
        box(0, 0.45, z, w * 0.83, d * 0.75, h, "rouge")
        for j in range(9 - i * 2):
            xx = (j / (8 - i * 2) - 0.5) * w * 0.94
            for yy in [0.45 - d * 0.49, 0.45 + d * 0.49]:
                shaft(xx, yy, z, 0.085, h + 0.09, "rouge", 7)
        for j in range(7 - i * 2):
            xx = (j / (6 - i * 2) - 0.5) * w * 0.74
            window(xx, 0.45 - d * 0.375 - 0.03, z + 0.14, w / (11 - i * 2), h * 0.72, "gold", "dark")
        box(0, 0.45, z + h, w, d, 0.12, "greenTile")
        hip(0, 0.45, z + h + 0.1, w + 1.02, d + 0.77, 0.83 if i < 2 else 1.1, "greyTile", "rouge")
        if i:
            for yy in [0.45 - d * 0.54, 0.45 + d * 0.54]:
                box(0, yy, z + 0.3, w, 0.072, 0.055, "rouge")
                for j in range(15):
                    box((j / 14 - 0.5) * w, yy, z, 0.055, 0.055, 0.33, "rouge")
    group("水廊·瓦檐与虬柱")
    for side in [-1, 1]:
        x = side * 3.7
        box(x, 0.19, 0.43, 0.69, 3.23, 0.19, "marble")
        for y in [-1.15, -0.5, 0.22, 0.88, 1.53]:
            for xx in [x - 0.2, x + 0.2]:
                shaft(xx, y, 0.60, 0.05, 0.63, "rouge", 6)
        for i in range(4):
            hip(x, -0.82 + i * 0.67, 1.23, 0.91, 0.84, 0.24, "greyTile")
        for y in [-1.22, 1.51]:
            box(x, y, 0.60, 0.82, 0.76, 0.85, "ochre")
            box(x, y, 1.43, 1.0, 0.91, 0.1, "marble")
            for dx in [-0.29, 0.29]:
                for dy in [-0.24, 0.24]:
                    shaft(x + dx, y + dy, 1.53, 0.06, 0.50, "rouge", 7)
            hip(x, y, 2.03, 1.08, 0.98, 0.33, "greyTile")


def mogao():
    group("鸣沙山麓·窟崖与洞口")
    box(0, 0, 0, 10.6, 3.28, 0.18, "sand")
    # Keep the desert escarpment continuous. The cut cells have shaded reveals and recessed backs.
    xs = [-5.25 + i * 0.35 for i in range(31)]
    zs = [0.16, 0.65, 1.11, 1.55, 2.10, 2.54, 3.11, 3.64, 4.21, 4.77]
    holes = {
        (2, 1),
        (5, 1),
        (24, 1),
        (25, 1),
        (28, 1),
        (5, 4),
        (6, 4),
        (22, 4),
        (27, 5),
        (3, 6),
        (8, 5),
        (23, 6),
        (25, 3),
        (7, 2),
        (20, 1),
        (1, 3),
    }

    def cliff(i, j):
        xx = xs[i]
        fray = sin(0.63 * i + 1.7 * j) * 0.5 + 0.5 * sin(1.21 * i - 0.6 * j)
        top = 4.67 + 0.29 * sin(i * 0.38) + 0.16 * cos(i * 0.88) + 0.14 * sin(i * 1.32)
        return (
            xx + (0.07 * fray if i not in (0, 30) else 0),
            0.08 + 0.08 * j + 0.15 * cos(i * 0.39) + 0.09 * fray,
            zs[j] * top / zs[-1] + (0 if j == 0 else 0.063 * fray),
        )

    for j in range(len(zs) - 1):
        for i in range(len(xs) - 1):
            a, b, c, d = [cliff(i + ix, j + jz) for ix, jz in [(0, 0), (1, 0), (1, 1), (0, 1)]]
            if (i, j) in holes:
                inner = [(x, y + 0.36, z) for x, y, z in [a, b, c, d]]
                face(inner, "dark")
                for k, (p, q) in enumerate([(a, b), (b, c), (c, d), (d, a)]):
                    face([p, q, inner[(k + 1) % 4], inner[k]], "rock")
            else:
                tone = "loessDark" if (j in (3, 6) and sin(i * 0.23 + j) > 0.1) else "loess"
                face([a, b, c], tone)
                face([a, c, d], tone)
    for i in range(len(xs) - 1):
        a = cliff(i, 9)
        b = cliff(i + 1, 9)
        c = (b[0], 1.67, b[2] + 0.11)
        d = (a[0], 1.67, a[2] + 0.11)
        face([a, b, c, d], "loess")
        face([c, (c[0], c[1], 0.16), (d[0], d[1], 0.16), d], "loess")
    for i in (0, 30):
        for j in range(9):
            a = cliff(i, j)
            b = cliff(i, j + 1)
            side = [a, b, (b[0], 1.67, b[2] + 0.11), (a[0], 1.67, a[2] + 0.11)]
            face(side if i == 0 else side[::-1], "loess")
    group("第96窟·九层窟檐")
    for i in range(9):
        z = 0.19 + i * 0.59
        w = 3.65 - i * 0.22
        d = 1.66 - i * 0.075
        box(0, -0.29, z, w * 0.78, d * 0.73, 0.48, "plum")
        for j in range(5 if i < 6 else 3):
            n = 5 if i < 6 else 3
            xx = (j / (n - 1) - 0.5) * w * 0.78
            shaft(xx, -0.29 - d * 0.43, z, 0.061, 0.43, "rouge", 7)
        box(0, -0.29 - d * 0.39, z + 0.14, w * 0.79, 0.085, 0.071, "gold")
        hip(0, -0.29, z + 0.42, w, d, 0.29 if i < 8 else 0.53, "greyTile", "rouge", 0.23)
    group("窟前台阶")
    steps(0, -1.57, 0.18, 2, 0.55, 0.17, 4, "granite")


def sayram():
    group("克勒涌珠·西岸与水色")
    rng = random.Random(37)
    nx, ny = 24, 19
    coords = {}

    def coast(x):
        return -0.7 + 0.26 * x + 0.46 * sin(x * 1.19) + 0.18 * sin(x * 2.17)

    def height(x, y):
        f = y - coast(x)
        if f <= 0:
            return 0.20
        m = max(0, y - 1.18)
        return (
            0.21
            + min(0.14, 0.11 * f)
            + m * (0.36 + 0.15 * cos(x * 1.64))
            + 0.05 * sin(x * 2 + y) * min(2, f)
            + 0.57 * exp(-(((x + 2.1) / 0.80) ** 2) - ((y - 2.8) / 0.8) ** 2)
        )

    for j in range(ny):
        for i in range(nx):
            x = (i / (nx - 1) - 0.5) * 10.6
            y = (j / (ny - 1) - 0.5) * 6.6
            if 0 < i < nx - 1 and 0 < j < ny - 1:
                x += rng.uniform(-0.10, 0.1)
                y += rng.uniform(-0.09, 0.09)
            coords[i, j] = (x, y, height(x, y))

    def shade(v):
        x, y, z = [sum(pt[k] for pt in v) / 3 for k in range(3)]
        dd = y - coast(x)
        if dd < -0.48:
            return "deepwater"
        if dd < 0:
            return "water"
        if dd < 0.24:
            return "graniteLight"
        return "grass"

    for j in range(ny - 1):
        for i in range(nx - 1):
            a, b, c, d = [coords[i + ii, j + jj] for ii, jj in [(0, 0), (1, 0), (1, 1), (0, 1)]]
            for patch in [[a, b, c], [a, c, d]]:
                face(patch, shade(patch))
    boundary = (
        [coords[i, 0] for i in range(nx)]
        + [coords[nx - 1, j] for j in range(1, ny)]
        + [coords[i, ny - 1] for i in range(nx - 2, -1, -1)]
        + [coords[0, j] for j in range(ny - 2, 0, -1)]
    )
    for i, p in enumerate(boundary):
        q = boundary[(i + 1) % len(boundary)]
        face([q, p, (p[0], p[1], 0), (q[0], q[1], 0)], "ashlar")
    face([(p[0], p[1], 0) for p in boundary[::-1]], "ashlar")
    group("天山·雪线与山脊")
    # A continuous, layered watershed avoids isolated cones and keeps the lake as the subject.
    rng = random.Random(191)
    cols, rows = 47, 8
    hill = {}
    peaks = [
        (-4.70, 0.69, 0.66),
        (-3.59, 0.76, 0.83),
        (-2.54, 0.81, 0.50),
        (-1.82, 1.18, 0.72),
        (-0.48, 1.62, 0.81),
        (0.13, 1.00, 0.41),
        (1.06, 1.39, 0.61),
        (2.23, 1.12, 0.77),
        (3.26, 0.84, 0.69),
        (4.13, 0.94, 0.66),
        (4.94, 0.64, 0.49),
    ]
    for i in range(cols):
        x = -5.23 + i * 10.46 / (cols - 1)
        profile = max(amp * exp(-abs((x - center) / sigma) * 0.96) for center, amp, sigma in peaks)
        crest = 2.73 + 0.15 * sin(1.1 * x)
        for j in range(rows):
            t = j / (rows - 1)
            y = 1.22 + 2.1 * t
            shoulder = max(0, 1 - abs(y - crest) / (1.35 if y < crest else 1.04))
            z = (
                0.64
                + 0.58 * t
                + shoulder * (0.27 + profile * 1.28)
                + 0.11 * sin(x * 4.21 - 3 * t) * shoulder
                + 0.11 * rng.random() * shoulder
            )
            # Blend the leading slope into the meadow, without an exposed mesh edge.
            blend = min(1, j / 2)
            z = (height(x, y) - 0.045) * (1 - blend) + z * blend
            hill[i, j] = (x + rng.uniform(-0.041, 0.041), y + rng.uniform(-0.036, 0.036), z)
    for j in range(rows - 1):
        for i in range(cols - 1):
            a, b, c, d = [hill[i + ii, j + jj] for ii, jj in [(0, 0), (1, 0), (1, 1), (0, 1)]]
            for patch in [[a, b, c], [a, c, d]]:
                x, y, z = [sum(pt[m] for pt in patch) / 3 for m in range(3)]
                snowline = 1.84 + 0.18 * sin(x * 5.41 + y) + 0.22 * sin(x * 3.7 - y)
                tone = (
                    "snow" if z > snowline else ("scree" if z > 1.45 + 0.11 * sin(x * 3.4) else "pine")
                )
                face(patch, tone)
    edge = (
        [hill[0, j] for j in range(rows - 1)]
        + [hill[i, rows - 1] for i in range(cols)]
        + [hill[cols - 1, j] for j in reversed(range(rows - 1))]
    )
    for a, b in zip(edge, edge[1:]):
        face([a, b, (b[0], b[1], 0.24), (a[0], a[1], 0.24)], "scree")
    group("泉眼·湿地")
    for xc, yc, rx, ry in [
        (-2.4, 0.05, 0.82, 0.22),
        (-3.55, 0.64, 0.55, 0.20),
        (0.59, 0.92, 0.41, 0.16),
    ]:
        shoreline = []
        for k in range(19):
            a = k * 2 * pi / 19
            w = 1 + 0.14 * sin(a * 3 + xc)
            xx = xc + rx * w * cos(a)
            yy = yc + ry * w * sin(a)
            shoreline.append((xx, yy, height(xx, yy) + 0.055))
        center = (xc, yc, height(xc, yc) + 0.06)
        for i, p in enumerate(shoreline):
            face([center, p, shoreline[(i + 1) % 19]], "water")
    group("湖岸·冰碛卵石")
    rng = random.Random(37)
    for k in range(115):
        x = rng.uniform(-5.0, 5.0)
        y = coast(x) + rng.uniform(-0.13, 0.32)
        r = rng.uniform(0.025, 0.13)
        sphere(
            x, y, height(x, y) + 0.010, r, r * 0.65, r * 0.43, "graniteLight" if k % 3 else "scree", 6, 3
        )
    group("临湖·植被与清泉")
    for j in range(42):
        x = rng.uniform(-4.95, 5.0)
        y = rng.uniform(0.23, 2.6)
        if y < coast(x) + 0.42:
            continue
        z = height(x, y)
        h = rng.uniform(0.32, 0.65)
        shaft(x, y, z, 0.035, h * 0.38, "timber", 5)
        for t in [0, 0.29, 0.55]:
            cylinder(
                (x, y, z + h * (0.17 + t)),
                (x, y, z + h * (0.79 + t * 0.7)),
                h * (0.22 - 0.14 * t),
                0.01,
                "pine",
                6,
            )


def disney():
    group("奇妙梦想城堡·前院与城墙")
    floorplan(
        0,
        0.04,
        0,
        [
            (-4.35, -2.15),
            (-3.53, -2.59),
            (2.82, -2.6),
            (4.35, -1.77),
            (4.15, 1.64),
            (2.54, 2.52),
            (-2.94, 2.37),
            (-4.34, 1.62),
        ],
        0.31,
        "graniteLight",
    )
    for side in [-1, 1]:
        box(side * 1.57, -1.37, 0.30, 1.86, 0.54, 1.12, "pink")
        for i in range(6):
            box(side * (0.72 + i * 0.31), -1.37, 1.42, 0.17, 0.57, 0.20, "whitewash")
    group("门楼·拱洞与塔肩")
    for side in [-1, 1]:
        box(side * 0.76, -0.72, 0.30, 0.45, 1.38, 1.18, "pink")
    annular_arch(0, -0.72, 1.20, 0.55, 0.25, 1.38, "graniteLight")
    box(0, -0.47, 1.96, 1.81, 1.73, 0.86, "pink")
    for j in range(3):
        window((j - 1) * 0.49, -1.35, 2.13, 0.32, 0.47, "graniteLight", "teal")
    hip(0, -0.45, 2.82, 2.12, 1.86, 0.74, "sky", "gold")
    group("后殿与立面")
    box(0, 0.77, 0.30, 4.14, 1.78, 2.42, "pink")
    hip(0, 0.73, 2.70, 4.56, 2.3, 1.12, "lilac", "gold")
    towers = [
        (-3.49, -1.31, 0.47, 1.71, "sky", "cone"),
        (3.38, -1.05, 0.48, 1.63, "lilac", "dome"),
        (-2.23, -0.86, 0.50, 2.82, "sky", "cone"),
        (2.34, -0.68, 0.43, 2.65, "turquoise", "dome"),
        (-1.03, 0.70, 0.49, 3.99, "lilac", "cone"),
        (0.56, 0.90, 0.45, 4.40, "gold", "needle"),
        (-2.61, 1.10, 0.37, 3.12, "turquoise", "dome"),
        (1.80, 0.98, 0.49, 3.84, "sky", "cone"),
        (0.02, -0.43, 0.29, 3.36, "gold", "needle"),
        (2.84, 0.72, 0.30, 2.65, "lilac", "cone"),
    ]
    for i, (x, y, r, h, mat, form) in enumerate(towers):
        group("塔楼·%02d" % (i + 1))
        z = 0.3
        shaft(x, y, z, r * 0.93, h, "pink" if i % 3 else "graniteLight", 12, r)
        shaft(x, y, z + h * 0.56, r * 1.035, h * 0.06, "whitewash", 12)
        shaft(x, y, z + h - 0.18, r * 1.18, 0.20, "graniteLight", 14)
        window(x, y - r * 0.96, z + h - 0.77, r * 0.57, 0.49, "graniteLight", "dark")
        if form == "dome":
            sphere(x, y, z + h + 0.22, r * 1.14, r * 1.14, 0.64, mat, 14, 7)
            ht = 0.83
        else:
            ht = r * (3.65 if form == "needle" else 2.73)
            roofcone(x, y, z + h, r * 1.28, ht, mat, n=14)
            if form == "needle":
                shaft(x, y, z + h + ht * 0.73, r * 0.32, ht * 0.14, "gold", 9)
        shaft(x, y, z + h + ht - 0.03, 0.04, 0.33, "gold", 7, 0.012)
        sphere(x, y, z + h + ht, 0.065, 0.065, 0.07, "gold", 7, 4)


def stpauls():
    group("大三巴·石阶与平台")
    box(0, 0.26, 0, 6.86, 2.10, 0.47, "ashlar")
    steps(0, -3.44, 0, 6.55, 2.68, 0.48, 14, "granite")
    group("遗址前壁·三座正门")
    width = 6.17
    depth = 0.53
    base = 0.47
    # The front wall is built up between openings. No plane covers the doorways.
    for x, w in [(-2.67, 0.81), (-0.91, 1.06), (0.91, 1.06), (2.67, 0.81)]:
        box(x, 0, base, w, depth, 1.74, "granite")
    for x in [-1.76, 0, 1.76]:
        r = 0.49 if x else 0.56
        # The measured south elevation shows flat door lintels beneath framed panels.
        for side in [-1, 1]:
            box(x + side * (r + 0.055), -0.052, base, 0.13, depth + 0.105, 1.41, "graniteLight")
        box(x, -0.036, base + 1.37, 2 * r + 0.24, depth + 0.10, 0.28, "graniteLight")
        box(x, -0.312, base + 1.70, 2 * r, 0.056, 0.15, "ashlar")
    box(0, 0, base + 1.69, width, depth, 0.38, "granite")
    for x in [-2.91, -2.66, -1.06, -0.86, -0.67, 0.67, 0.86, 1.06, 2.66, 2.91]:
        shaft(x, -0.34, base + 0.11, 0.104, 1.71, "graniteLight", 9, 0.087)
        box(x, -0.34, base + 0.055, 0.25, 0.2, 0.13, "graniteLight")
        box(x, -0.34, base + 1.78, 0.27, 0.23, 0.14, "graniteLight")
    group("第二层·窗列与壁龛")
    for x, w in [(-2.76, 0.65), (-1.00, 0.98), (1.00, 0.98), (2.76, 0.65)]:
        box(x, 0, 2.50, w, depth, 1.28, "granite")
    for x in [-1.88, 0, 1.88]:
        r = 0.32 if x else 0.39
        annular_arch(x, 0, 3.20, r, 0.18, depth, "graniteLight", 12)
        for side in [-1, 1]:
            box(x + side * (r + 0.09), -0.12, 2.51, 0.18, 0.37, 0.70, "graniteLight")
        box(x, -0.03, 2.51, r * 2 + 0.18, 0.54, 0.11, "graniteLight")
    for x in [-2.83, -1.14, -0.81, 0.81, 1.14, 2.83]:
        shaft(x, -0.33, 2.52, 0.09, 1.20, "graniteLight", 8)
        box(x, -0.33, 3.69, 0.23, 0.19, 0.14, "graniteLight")
    for x in [-0.95, 0.95, -2.76, 2.76]:
        box(x, -0.273, 2.74, 0.31, 0.045, 0.66, "dark")
        shaft(x, -0.33, 2.77, 0.073, 0.34, "bronze", 6, 0.045)
        sphere(x, -0.34, 3.17, 0.071, 0.064, 0.083, "bronze", 8, 4)
    group("上层·涡卷山花与十字架")
    for z, w, h in [(3.8, 5.13, 0.71), (4.6, 3.49, 0.64)]:
        box(0, 0, z, w, depth * 0.84, h, "granite")
        for side in [-1, 1]:
            shaft(side * (w * 0.4), -0.27, z + 0.04, 0.095, h - 0.02, "graniteLight", 9)
            for j in range(4):
                x = side * (w * 0.49 + 0.09 * j)
                box(x, 0, z, 0.21, 0.38, h * (1 - (j + 1) * 0.19), "granite")
            ring(side * w * 0.4, -0.25, z + h * 0.4, 0.15, 0.05, "graniteLight", 14, 5)
        box(0, -0.248, z + 0.04, 0.50, 0.032, h * 0.84, "dark")
        shaft(0, -0.30, z + 0.13, 0.098, h * 0.43, "bronze", 8, 0.074)
        sphere(0, -0.32, z + h * 0.74, 0.087, 0.063, 0.092, "bronze", 8, 4)
        for sign in [-1, 1]:
            for off in [0.20, 0.31]:
                xx = sign * w * off
                box(xx, -0.238, z + 0.09, 0.26, 0.05, h * 0.76, "graniteLight")
                sphere(xx, -0.30, z + 0.32, 0.077, 0.033, 0.13, "granite", 8, 4)
    for z, w in [(2.35, 6.41), (3.77, 6.38), (4.49, 5.30), (5.21, 3.59)]:
        box(0, 0, z, w, 0.72, 0.11, "graniteLight")
        box(0, 0, z + 0.115, w - 0.12, 0.61, 0.06, "granite")
    # The carved, curved gable crowns a thin facade.
    tri = [(-1.78, 5.39), (1.78, 5.39), (0, 6.46)]
    fr = [(x, -0.24, z) for x, z in tri]
    bk = [(x, 0.24, z) for x, z in tri]
    face(fr, "granite")
    face(bk[::-1], "granite")
    for k in range(3):
        kk = (k + 1) % 3
        face([fr[k], bk[k], bk[kk], fr[kk]], "graniteLight")
        cylinder(fr[k], fr[kk], 0.095, 0.095, "graniteLight", 8)
    sphere(0, -0.27, 5.72, 0.19, 0.048, 0.092, "bronze", 9, 5)
    for x in [-0.15, 0.15]:
        sphere(x, -0.26, 5.77, 0.18, 0.044, 0.064, "bronze", 9, 4)
    box(0, 0, 6.48, 0.095, 0.13, 0.49, "bronze")
    box(0, 0, 6.71, 0.36, 0.13, 0.075, "bronze")
    for x in [-2.98, 2.98, -2.43, 2.43, -1.70, 1.70]:
        z = 4.0 if abs(x) > 2.8 else (4.62 if abs(x) > 2 else 5.31)
        shaft(x, 0, z, 0.13, 0.20, "graniteLight", 9, 0.06)
        sphere(x, 0, z + 0.26, 0.13, 0.13, 0.18, "graniteLight", 9, 4)


def taipei():
    group("塔身·裙楼与斜收基座")
    box(0, 0.13, 0, 3.1, 3.08, 0.12, "granite")
    profile(0, 0, 0.12, [(0, 2.45, 2.45), (0.38, 2.35, 2.35), (2.16, 1.51, 1.51)], "teal")
    for i in range(11):
        hh = 0.34 + i * 0.15
        ww = 2.42 - hh * 0.40
        box(0, 0, hh, ww, ww, 0.032, "mint")
    for i in range(8):
        group("竹节塔身·第%d节" % (i + 1))
        z = 2.27 + i * 0.72
        profile(
            0,
            0,
            z,
            [(0, 1.42, 1.42), (0.12, 1.46, 1.46), (0.655, 1.84, 1.84), (0.70, 1.84, 1.84)],
            "teal",
        )
        box(0, 0, z + 0.64, 1.91, 1.91, 0.08, "mint")
        for j in range(1, 6):
            hh = 0.10 + j * 0.091
            w = 1.45 + (hh - 0.10) * 0.72
            box(0, 0, z + hh, w, w, 0.022, "mint")
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                cylinder(
                    (dx * 0.704, dy * 0.704, z + 0.02),
                    (dx * 0.916, dy * 0.916, z + 0.642),
                    0.044,
                    0.05,
                    "mint",
                    5,
                )
            for frac in [-0.61, 0, 0.61]:
                cylinder(
                    (frac * 0.71, dx * 0.716, z + 0.04),
                    (frac * 0.91, dx * 0.911, z + 0.64),
                    0.018,
                    0.018,
                    "mint",
                    4,
                )
                cylinder(
                    (dx * 0.716, frac * 0.71, z + 0.04),
                    (dx * 0.911, frac * 0.91, z + 0.64),
                    0.018,
                    0.018,
                    "mint",
                    4,
                )
    group("如意与吉祥铜钱")
    for x, y in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        a = Vector((x * 0.945, y * 0.945, 2.1))
        b = a + Vector((x * 0.08, y * 0.08, 0))
        cylinder(a, b, 0.30, 0.30, "gold", 28)
        cylinder(b, b + Vector((x * 0.02, y * 0.02, 0)), 0.238, 0.238, "bronze", 28)
        box(x * 1.06, y * 1.06, 2.00, 0.04 if x else 0.14, 0.04 if y else 0.14, 0.17, "mint")
    group("塔冠与天线")
    z = 8.02
    for k, (w, d, h) in enumerate(
        [(1.37, 1.37, 0.28), (0.98, 0.98, 0.29), (0.65, 0.65, 0.29), (0.44, 0.44, 0.36)]
    ):
        box(0, 0, z, w, d, h, "teal")
        box(0, 0, z + h - 0.035, w + 0.055, d + 0.055, 0.06, "mint")
        z += h
    shaft(0, 0, z, 0.15, 0.39, "mint", 12, 0.10)
    shaft(0, 0, z + 0.36, 0.076, 0.90, "graniteLight", 10, 0.012)


SCENES = {
    "lijiang": lijiang,
    "potala": potala,
    "terracotta": terracotta,
    "tang-paradise": tang,
    "mogao": mogao,
    "sayram": sayram,
    "hk-disney": disney,
    "st-pauls": stpauls,
    "taipei-101": taipei,
}
