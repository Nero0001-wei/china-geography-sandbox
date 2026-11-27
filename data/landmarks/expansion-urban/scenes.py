"""Twenty-two individual scenes for the modern national geography map."""

from math import cos, sin, pi, sqrt
from random import Random

from geometry import annular_arch, box, cylinder, face, floorplan, group, hip, profile, ring, roofcone, shaft, sphere, steps, window


def palette_entry(hex_color, pattern="", roughness=0.74):
    channels = [int(hex_color[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = tuple(c / 12.92 if c < 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in channels)
    return linear, pattern, roughness


PALETTE = {name: palette_entry(*spec) for name, spec in {
    "earth": ("665540", "grain"), "grass": ("8d9f60", "grain"), "oak": ("657b43", "grain"),
    "pine": ("355f4b", "grain"), "spring": ("aaba70", "grain"), "water": ("438b9b", "water", 0.38),
    "deepWater": ("347489", "water", 0.39), "waterLine": ("b4d1ca", "", 0.6), "sand": ("bc9c6c", "grain"),
    "ochre": ("b88a58", "brick"), "terracotta": ("976451", "brick"), "redBrick": ("9b5443", "brick"),
    "timber": ("703e2d", "grain"), "brown": ("a47039", "grain"), "white": ("e9e3cd", "grain"),
    "stone": ("adaba0", "brick"), "granite": ("b1a99e", "grain"), "darkStone": ("797a72", "grain"),
    "sculptedStone": ("b1a99e", "coursed"), "sculptedHair": ("89877f", "coursed"),
    "charcoal": ("363e41", "grain"), "dark": ("383236", ""), "slate": ("5a6464", "tile"),
    "jade": ("427b70", "tile"), "blue": ("447e9c", ""), "deepBlue": ("315962", ""), "steel": ("a8b7bb", ""),
    "iron": ("576973", "", 0.72), "goldTile": ("c99536", "tile"), "gold": ("d8ab58", "", 0.48),
    "red": ("ab4c3c", "grain"), "deepRed": ("763329", "grain"), "pearl": ("b95b76", "tile", 0.48),
    "rose": ("d99b85", "grain"), "cream": ("e3caa0", "grain"), "aqua": ("95baa9", "grain"),
    "lavender": ("b4aabc", "grain"), "snow": ("e4edf1", "grain"), "ice": ("83b8cf", "brick", 0.48),
    "paleIce": ("c3deec", "brick"), "cyan": ("d7f0f2", "", 0.46), "bronze": ("8b886a", "grain"),
    "greenBronze": ("657c60", "grain"), "glass": ("39494c", "", 0.36), "brick": ("ac6c50", "brick"),
    "rust": ("77472d", "grain"), "black": ("373330", ""), "honey": ("cc9b58", "grain"),
}.items()}


def base(width, depth, top="grass", body="earth", height=0.26):
    group("场景基座")
    chamfer = min(width, depth) * 0.055
    x, y = width / 2, depth / 2
    outline = [(-x + chamfer, -y), (x - chamfer, -y), (x, -y + chamfer), (x, y - chamfer),
               (x - chamfer, y), (-x + chamfer, y), (-x, y - chamfer), (-x, -y + chamfer)]
    floorplan(0, 0, 0, outline, height - 0.04, body)
    floorplan(0, 0, height - 0.04, outline, 0.04, top)
    return height


def beam(a, b, r, material_name, sides=5):
    cylinder(a, b, r, r, material_name, sides)


def tree(x, y, z, scale=1, version=0):
    shaft(x, y, z, 0.06 * scale, 0.52 * scale, "timber", 5)
    if version % 3 == 0:
        for offset, zz, r in ((0, 0.49, 0.32), (0, 0.72, 0.26), (0, 0.91, 0.17)):
            shaft(x + offset, y, z + zz * scale, r * scale, 0.33 * scale, "pine", 7, r * 0.14 * scale)
    else:
        for dx, dy, dz, size in ((0, 0, 0.72, 0.31), (-0.15, 0.02, 0.58, 0.25), (0.15, 0.03, 0.63, 0.23)):
            sphere(x + dx * scale, y + dy * scale, z + dz * scale, size * scale, size * scale * 0.85,
                   size * scale * 0.86, "spring" if version % 2 else "oak", 7, 4)


def ripples(bounds, z, seed, count=14):
    random = Random(seed)
    left, right, front, back = bounds
    for _ in range(count):
        x = random.uniform(left, right - 0.3)
        y = random.uniform(front, back)
        box(x, y, z, random.uniform(0.16, 0.56), 0.02, 0.007, "waterLine")


def gable(x, y, z, w, d, h, m="slate"):
    floorplan(0, 0, z, [(x - w / 2, y - d / 2), (x + w / 2, y - d / 2),
                         (x + w / 2, y + d / 2), (x - w / 2, y + d / 2)], 0.055, "charcoal")
    a, b, c, e = (x - w / 2, y - d / 2, z + 0.055), (x + w / 2, y - d / 2, z + 0.055), (x + w / 2, y + d / 2, z + 0.055), (x - w / 2, y + d / 2, z + 0.055)
    r0, r1 = (x - w / 2, y, z + h), (x + w / 2, y, z + h)
    face((a, b, r1, r0), m)
    face((r0, r1, c, e), m)
    face((a, r0, e), "white")
    face((b, c, r1), "white")
    beam(r0, r1, 0.055, "charcoal", 6)


def roof8(x, y, z, radius, height, color):
    outline = [(radius * cos(k * pi / 4), radius * sin(k * pi / 4)) for k in range(8)]
    floorplan(x, y, z, outline, 0.064, "timber")
    roofcone(x, y, z + 0.063, radius * 1.01, height, color, n=8)
    shaft(x, y, z + height, radius * 0.075, height * 0.31, "gold", 7, radius * 0.025)


def pavilion(x, y, z, scale, color="goldTile", posts="red"):
    size, height = 0.66 * scale, 0.88 * scale
    box(x, y, z, size * 1.34, size * 1.34, 0.14 * scale, "stone")
    for dx in (-1, 1):
        for dy in (-1, 1):
            shaft(x + dx * size / 2, y + dy * size / 2, z + 0.10 * scale, 0.055 * scale,
                  height * 0.73, posts, 6)
    hip(x, y, z + height * 0.77, size * 1.66, size * 1.66, height * 0.48, color, posts, 0.26)
    if scale > 1.25:
        box(x, y, z + height * 1.01, size * 0.82, size * 0.82, height * 0.22, posts)
        hip(x, y, z + height * 1.20, size * 1.22, size * 1.22, height * 0.49, color, posts, 0.31)
        shaft(x, y, z + height * 1.64, 0.051 * scale, 0.13 * scale, "gold", 6, 0.013)
        return
    shaft(x, y, z + height * 1.23, 0.045 * scale, 0.13 * scale, "gold", 6, 0.012)


def rails(x0, x1, y, z, count, material_name="stone"):
    for i in range(count + 1):
        x = x0 + (x1 - x0) * i / count
        box(x, y, z, 0.069, 0.07, 0.24, material_name)
    box((x0 + x1) / 2, y, z + 0.165, x1 - x0, 0.045, 0.048, material_name)


def geometric_arch(x, y, z, radius, rise, thickness, depth, material_name, segments=13):
    # A single shell with an actual opening, scaled separately in span and height.
    inner, outer = [], []
    for index in range(segments + 1):
        angle = pi * index / segments
        inner.append((x + radius * cos(angle), z + rise * sin(angle)))
        outer.append((x + (radius + thickness) * cos(angle), z + (rise + thickness) * sin(angle)))
    for i in range(segments):
        points = (inner[i], outer[i], outer[i+1], inner[i+1])
        front = [(px, y - depth / 2, pz) for px, pz in points]
        back = [(px, y + depth / 2, pz) for px, pz in points]
        face(front, material_name)
        face(back[::-1], material_name)
        face((front[0], front[3], back[3], back[0]), material_name)
        face((front[1], back[1], back[2], front[2]), material_name)


def boat(x, y, z, scale=1.0, ferry=False):
    hull = [(-1.0, -0.18), (-0.78, -0.39), (0.61, -0.39), (1.05, -0.10), (1.05, 0.10),
            (0.61, 0.39), (-0.78, 0.39), (-1.05, 0.17)]
    floorplan(x, y, z, [(a * scale, b * scale) for a, b in hull], 0.17 * scale, "deepBlue" if ferry else "timber")
    if ferry:
        box(x, y, z + 0.15 * scale, 1.67 * scale, 0.62 * scale, 0.44 * scale, "white")
        for j in range(-4, 5):
            for side in (-1, 1):
                box(x + j * 0.16 * scale, y + side * 0.317 * scale, z + 0.25 * scale,
                    0.114 * scale, 0.021, 0.19 * scale, "deepBlue")
        box(x - 0.07 * scale, y, z + 0.59 * scale, 1.22 * scale, 0.56 * scale, 0.052, "oak")
        shaft(x - 0.05 * scale, y, z + 0.62 * scale, 0.047 * scale, 0.45 * scale, "iron", 6)
    else:
        box(x, y, z + 0.15 * scale, 1.30 * scale, 0.62 * scale, 0.07, "brown")
        for dx in (-0.5, 0.25):
            for dy in (-0.26, 0.26):
                shaft(x + dx * scale, y + dy * scale, z + 0.17, 0.03, 0.41 * scale, "timber", 5)
        gable(x - 0.17 * scale, y, z + 0.58 * scale, 1.08 * scale, 0.76 * scale, 0.16 * scale)


def slender_west_lake():
    z = base(10.8, 6.8, "water", "deepWater")
    group("荷岸与水波")
    for sign in (-1, 1):
        x = sign * 4.65
        box(x, 0, z, 1.25, 3.7, 0.10, "grass")
        box(x - sign * 0.20, 0, z + 0.09, 1.65, 1.14, 0.05, "stone")
        for i in range(3):
            tree(x, 0.97 + (i - 1) * 0.61, z + 0.10, 0.67 + 0.11 * i, i)
    ripples((-4.62, 4.62, -3.14, -0.62), z, 41, 24)
    group("五亭桥·石券")
    for x, r, h in ((0, 1.0, 0.95), (-1.83, 0.56, 0.56), (1.83, 0.56, 0.56), (-3.0, 0.39, 0.38), (3.0, 0.39, 0.38)):
        for y in (-0.19, 0.19):
            geometric_arch(x, y, z, r, h, 0.22, 0.64, "stone", 10)
        box(x, 0, z + h + 0.19, 2 * r + 0.42, 1.23, 0.14, "white")
    for x in (-4.1, 4.1):
        box(x, 0, z + 0.04, 1.53, 1.25, 0.24, "stone")
    group("五座琉璃瓦亭")
    for x, y, pz, size in ((0, 0, 1.27, 1.35), (-1.70, -0.40, 0.91, 0.87), (1.70, -0.40, 0.91, 0.87),
                            (-1.70, 0.51, 0.91, 0.87), (1.70, 0.51, 0.91, 0.87)):
        pavilion(x, y, z + pz, size)
    for y in (-0.61, 0.64):
        rails(-3.66, -2.25, y, z + 0.37, 5)
        rails(2.25, 3.66, y, z + 0.37, 5)


def hongcun():
    z = base(9.6, 7.7, "stone", "earth")
    group("月沼与驳岸")
    pond = [(-2.95, 0.72), (-2.82, -0.13), (-2.29, -0.95), (-1.37, -1.52), (-0.22, -1.81),
            (1.10, -1.62), (2.22, -1.06), (2.88, -0.21), (3.05, 0.72)]
    floorplan(0, -0.23, z, pond, 0.045, "deepWater")
    for a, b in zip(pond, pond[1:] + pond[:1]):
        beam((a[0], a[1] - 0.23, z + 0.06), (b[0], b[1] - 0.23, z + 0.06), 0.067, "darkStone")
    ripples((-1.3, 1.65, -1.40, 0.30), z + 0.043, 12, 9)
    group("月沼北岸·徽派民居")
    for i, (x, y, w, d, height) in enumerate((
        (-3.52, 1.17, 1.32, 1.61, 1.01), (-2.20, 1.61, 1.22, 1.74, 1.49), (-0.82, 1.71, 1.42, 1.78, 1.26),
        (0.75, 1.60, 1.48, 1.92, 1.66), (2.24, 1.48, 1.46, 1.75, 1.27), (3.67, 0.99, 1.24, 1.55, 1.12),
        (-3.85, -0.77, 0.92, 1.66, 1.28), (3.98, -0.49, 1.0, 1.57, 1.41), (-1.8, 3.02, 1.88, 1.10, 1.30),
        (1.43, 3.02, 1.8, 1.03, 1.22),
    )):
        box(x, y, z, w, d, height, "white")
        gable(x, y, z + height, w + 0.08, d + 0.12, 0.41, "slate")
        for side in (-1, 1):
            for step in range(3):
                xx = x + side * w * 0.5
                yy = y + (step - 1) * d / 3
                hh = height + (0.26 if step == 1 else 0.05)
                box(xx, yy, z, 0.10, d / 3 + 0.025, hh, "white")
                box(xx, yy, z + hh, 0.16, d / 3 + 0.08, 0.06, "charcoal")
        for off in (-0.28, 0.28):
            window(x + w * off, y - d / 2 - 0.012, z + height * 0.52, 0.17, 0.26, "timber", "dark")
        window(x, y - d / 2 - 0.014, z, 0.26, 0.61, "timber")
    group("村落细节")
    tree(-3.52, -2.67, z, 0.99, 1)
    tree(3.55, -2.25, z, 0.84, 2)


def fenghuang():
    z = base(10.8, 7.2, "water", "deepWater")
    group("沱江岸与虹桥桥孔")
    for side in (-1, 1):
        box(side * 4.27, 0, z, 1.92, 6.63, 0.23, "darkStone")
    for x in (-2.70, 0, 2.70):
        geometric_arch(x, 0.1, z + 0.06, 1.12, 0.69, 0.24, 1.45, "stone", 12)
        box(x, 0.1, z + 0.94, 2.70, 1.53, 0.14, "stone")
    group("虹桥·两层廊架与绿瓦")
    for side in (-1, 1):
        side_y = 0.1 + side * 0.61
        for x in (-3.53, -2.65, -1.78, -0.88, 0.0, 0.88, 1.78, 2.65, 3.53):
            box(x, side_y, z + 1.07, 0.105, 0.10, 0.77, "red")
            box(x, side_y * 0.83, z + 1.91, 0.10, 0.10, 0.48, "red")
        for zh in (1.12, 1.31, 1.79, 2.19):
            box(0, side_y, z + zh, 7.10, 0.07, 0.062, "timber")
    hip(0, 0.1, z + 2.31, 7.71, 2.06, 0.65, "jade", "red", 0.30)
    hip(0, 0.08, z + 1.77, 7.84, 2.32, 0.21, "slate", "red")
    group("临水吊脚楼")
    for sign in (-1, 1):
        for i, y in enumerate((-2.24, 1.88, 2.79)):
            x, h = sign * (4.02 + 0.15 * (i % 2)), 0.92 + 0.25 * (i % 2)
            for xx in (-0.50, 0.50):
                for yy in (-0.31, 0.31):
                    shaft(x + xx, y + yy, z + 0.06, 0.05, 0.73, "timber", 5)
            box(x, y, z + 0.60, 1.20, 0.83, h, "brown")
            gable(x, y, z + 0.60 + h, 1.36, 1.03, 0.39, "slate")
            for j in range(2):
                window(x + (j - 0.5) * 0.46, y - 0.43, z + 0.93, 0.24, 0.42)
    boat(0.3, -2.14, z + 0.018, 0.66)
    ripples((-3.40, 3.40, -3.39, -1.39), z, 12, 16)


def kaiping_diaolou():
    z = base(8.5, 7.2, "grass")
    group("稻田与村径")
    box(1.84, 0.2, z, 3.86, 6.45, 0.035, "deepWater")
    for i in range(18):
        for j in range(3):
            box(1.83 + (j - 1) * 1.2, (i - 8.5) * 0.34, z + 0.03, 1.12, 0.18, 0.073,
                "spring" if (i + j) % 3 else "oak")
    box(-1.0, -1.95, z, 1.08, 3.28, 0.045, "sand")
    group("铭石楼")
    x, y = -1.39, 0.32
    box(x, y, z, 2.08, 1.81, 0.20, "stone")
    box(x, y, z + 0.17, 1.79, 1.56, 3.44, "granite")
    for j in range(4):
        pz = z + 0.35 + j * 0.75
        box(x, y, pz - 0.08, 1.85, 1.64, 0.07, "stone")
        for dx in (-0.53, 0, 0.53):
            window(x + dx, y - 0.79, pz, 0.20, 0.44, "cream")
        for side in (-1, 1):
            for offset in (-0.39, 0.39):
                box(x + side * 0.911, y + offset, pz + 0.062, 0.04, 0.19, 0.30, "dark")
    box(x, y, z + 3.57, 2.04, 1.87, 0.13, "cream")
    for i in range(4):
        xx = x + (i - 1.5) * 0.43
        geometric_arch(xx, y - 0.83, z + 3.98, 0.16, 0.19, 0.04, 0.15, "cream", 6)
        for d in (-0.19, 0.19):
            box(xx + d, y - 0.83, z + 3.65, 0.06, 0.16, 0.34, "cream")
    box(x, y + 0.12, z + 3.64, 1.52, 1.25, 0.59, "granite")
    box(x, y, z + 4.21, 2.11, 1.90, 0.14, "stone")
    for dx in (-0.86, 0.86):
        for dy in (-0.74, 0.74):
            shaft(x + dx, y + dy, z + 3.55, 0.14, 0.87, "stone", 8)
            shaft(x + dx, y + dy, z + 4.39, 0.18, 0.23, "cream", 8, 0.105)
    ring(x, y + 0.23, z + 4.35, 0.44, 0.04, "cream", 18, 4, plane="xy")
    for tx, ty, size in ((-3.1, -2.5, 0.9), (-3.10, 2.22, 1.1), (1.86, 2.63, 0.74)):
        tree(tx, ty, z, size, 2)


def haikou_arcades():
    z = base(11.0, 6.7, "stone", "darkStone")
    group("中山路铺装")
    box(0, -1.03, z, 10.2, 1.47, 0.045, "granite")
    for x in range(-4, 5):
        box(x, -1.03, z + 0.045, 0.022, 1.40, 0.008, "darkStone")
    group("南洋骑楼连续立面")
    entries = [
        (-4.22, 1.34, 1.97, "cream"), (-2.78, 1.50, 2.32, "rose"), (-1.24, 1.49, 2.12, "white"),
        (0.37, 1.65, 2.50, "aqua"), (2.05, 1.58, 2.16, "cream"), (3.65, 1.53, 2.34, "lavender"),
    ]
    for i, (x, w, h, color) in enumerate(entries):
        y, depth = 1.35 + 0.08 * (i % 2), 2.34
        box(x, y + 0.34, z, w, depth - 0.68, h, color)
        box(x, y, z + 0.77, w, depth, h - 0.77, color)
        front = y - depth / 2
        for dx in (-0.43, 0.43):
            box(x + dx * w, front, z, 0.12, 0.21, 0.66, "white")
            box(x + dx * w, front, z + 0.59, 0.19, 0.27, 0.085, "white")
        geometric_arch(x, front, z + 0.62, 0.40 * w, 0.28, 0.055, 0.17, "white", 8)
        for dz in (1.02, 1.60):
            box(x, front - 0.022, z + dz - 0.09, w * 0.96, 0.12, 0.05, "white")
            for dx in (-0.27, 0, 0.27):
                window(x + dx * w, front - 0.018, z + dz, 0.21, min(h - dz, 0.36), "white", "deepBlue")
        box(x, y, z + h, w + 0.05, depth + 0.07, 0.06, "white")
        outline = [(x - w * 0.31, z + h), (x - w * 0.20, z + h + 0.15),
                   (x, z + h + 0.20 + (i % 2) * 0.11), (x + w * 0.24, z + h + 0.13),
                   (x + w * 0.31, z + h)]
        for a, b in zip(outline, outline[1:]):
            beam((a[0], front, a[1]), (b[0], front, b[1]), 0.055, "white")
        face([(xp, front + 0.016, zp) for xp, zp in outline[::-1]], color)
    for x in (-4.78, 4.58):
        tree(x, -2.2, z, 0.64, 2)


def kashgar_old_city():
    z = base(10.4, 7.6, "sand", "ochre")
    group("东城门·塔墙与拱券")
    box(0, 0.15, z + 2.90, 7.08, 2.19, 0.55, "ochre")
    for s in (-1, 1):
        x = s * 2.72
        box(s * 2.23, 0.2, z, 2.50, 2.03, 3.0, "ochre")
        profile(x, 0.12, z, [(0, 1.72, 2.60), (3.60, 1.6, 2.18), (3.76, 1.76, 2.30)], "sand")
        for h in (0.56, 1.42, 2.18, 3.30):
            box(x, -1.04, z + h, 1.64, 0.065, 0.06, "brown")
        for dx in (-0.56, -0.18, 0.18, 0.56):
            box(x + dx, -1.02, z + 3.73, 0.18, 0.28, 0.38, "ochre")
        for xx in (-0.34, 0.34):
            geometric_arch(x + xx, -1.0, z + 2.31, 0.16, 0.25, 0.06, 0.10, "cream", 8)
            box(x + xx, -0.99, z + 2.06, 0.25, 0.06, 0.29, "timber")
        box(s * 4.03, 0.25, z, 0.92, 1.65, 1.76, "ochre")
        for offset in (0.0, 0.34, 0.69):
            box(s * (3.67 + offset), -0.52, z + 1.75, 0.19, 0.26, 0.24, "sand")
    for face_y in (-0.99, 1.17):
        geometric_arch(0, face_y, z + 1.0, 0.97, 1.78, 0.23, 0.25, "cream", 14)
        geometric_arch(0, face_y - 0.14, z + 1.0, 1.22, 1.81, 0.09, 0.07, "brown", 14)
    for dx in (-1.13, 1.13):
        box(dx, -1.035, z, 0.21, 0.18, 1.05, "cream")
    for i in range(9):
        x = (i - 4) * 0.34
        box(x, -0.96, z + 3.44, 0.19, 0.24, 0.24, "sand")
    group("砖铺与街巷")
    for i in range(7):
        box(0, -3.34 + 0.49 * i, z, 1.82, 0.42, 0.028, "stone")


def tiananmen_square():
    z = base(11.2, 8.9, "stone", "darkStone")
    y = 1.12
    group("天安门广场北段")
    box(0, -1.80, z, 5.45, 4.62, 0.015, "granite")
    for x in (-4.30, 4.30):
        box(x, -1.76, z, 1.9, 4.36, 0.042, "grass")
        for i in range(4):
            tree(x, -3.48 + i * 0.98, z + 0.043, 0.58, i)
    group("红色城台与五券门")
    gate_widths = [0.42, 0.49, 0.54, 0.49, 0.42]
    center_steps = [-2.69, -1.34, 0, 1.34, 2.69]
    box(0, y, z + 1.08, 9.30, 3.0, 0.61, "red")
    for j, (left, right) in enumerate(zip([-4.65] + [x + r for x, r in zip(center_steps, gate_widths)],
                                           [x - r for x, r in zip(center_steps, gate_widths)] + [4.65])):
        box((left + right) / 2, y, z, right - left, 3.0, 1.11, "deepRed" if j % 2 else "red")
    for x, r in zip(center_steps, gate_widths):
        geometric_arch(x, y, z + 0.58, r, 0.49, 0.055, 3.01, "red", 11)
    box(0, y, z + 1.68, 9.45, 3.15, 0.12, "stone")
    for yy in (-0.36, 2.60):
        rails(-4.51, 4.51, yy, z + 1.77, 23)
    group("红柱黄瓦重檐城楼")
    box(0, y, z + 1.78, 7.47, 2.21, 1.10, "red")
    for x in range(-4, 5):
        shaft(x * 0.81, 0.002, z + 1.84, 0.086, 0.95, "deepRed", 7)
        window(x * 0.81 + 0.34, 0.01, z + 2.0, 0.34, 0.55, "timber", "dark")
    hip(0, y, z + 2.80, 8.70, 3.43, 0.59, "goldTile", "jade", 0.24)
    box(0, y, z + 3.13, 7.51, 2.29, 0.18, "red")
    hip(0, y, z + 3.24, 8.15, 2.89, 0.84, "goldTile", "jade", 0.22)
    group("华表与旗杆")
    for x in (-2.4, 2.4):
        shaft(x, -0.95, z, 0.10, 0.81, "white", 8, 0.07)
        box(x, -0.95, z + 0.73, 0.39, 0.083, 0.07, "white")
    shaft(0, -3.35, z + 0.025, 0.017, 1.53, "steel", 6)
    face(((0, -3.35, z + 1.49), (0.55, -3.35, z + 1.45),
          (0.55, -3.32, z + 1.15), (0, -3.35, z + 1.19)), "red")
    group("城台中央画框")
    box(0, y - 1.513, z + 1.14, 0.38, 0.018, 0.45, "gold")
    box(0, y - 1.524, z + 1.164, 0.333, 0.016, 0.403, "aqua")
    silhouette = [(-0.126, 1.165), (0.128, 1.165), (0.085, 1.243), (0.018, 1.277),
                  (-0.066, 1.255), (-0.115, 1.219)]
    face([(x, y - 1.535, z + h) for x, h in silhouette], "darkStone")
    sphere(0.00, y - 1.535, z + 1.352, 0.061, 0.013, 0.093, "cream", 10, 8)
    sphere(-0.011, y - 1.545, z + 1.410, 0.061, 0.02, 0.037, "dark", 8, 5)


def oriental_pearl():
    z = base(5.3, 5.3, "stone", "darkStone")
    group("观光塔底座与三组斜撑")
    shaft(0, 0, z, 1.63, 0.30, "steel", 20, 1.36)
    shaft(0, 0, z + 0.24, 1.15, 0.23, "glass", 20, 1.22)
    for index in range(3):
        a = index * 2 * pi / 3 + pi / 6
        x, y = cos(a), sin(a)
        cylinder((x * 1.41, y * 1.41, z + 0.12), (x * 0.45, y * 0.45, z + 3.23), 0.205, 0.165, "steel", 12)
        shaft(x * 0.40, y * 0.40, z + 0.25, 0.17, 6.16, "white", 10, 0.13)
        sphere(x * 0.72, y * 0.72, z + 2.95, 0.34, 0.34, 0.37, "pearl", 14, 8)
    shaft(0, 0, z + 0.42, 0.37, 6.83, "steel", 14, 0.23)
    group("红紫球体与楼层环")
    for hh, r, tall in ((2.36, 1.01, 0.90), (5.08, 0.77, 0.68), (6.79, 0.35, 0.315)):
        sphere(0, 0, z + hh, r, r, tall, "pearl", 24, 15)
        for k in (-0.27, 0.0, 0.27):
            ring(0, 0, z + hh + tall * k, r * sqrt(1-k*k), 0.024, "steel", 28, 4, plane="xy")
    group("广播天线")
    shaft(0, 0, z + 6.93, 0.18, 0.55, "white", 10, 0.091)
    for lower, upper, wide, narrow, color in (
        (7.42, 7.72, 0.089, 0.067, "red"), (7.72, 8.02, 0.067, 0.054, "white"),
        (8.02, 8.36, 0.054, 0.045, "red"), (8.36, 8.64, 0.045, 0.032, "white"), (8.64, 8.79, 0.032, 0.016, "red"),
    ):
        shaft(0, 0, z + lower, wide, upper - lower, color, 9, narrow)
    for x in (-1.85, 1.85):
        for y in (-1.56, 1.56):
            tree(x, y, z, 0.50, 1)


def three_gorges_dam():
    z = base(12.5, 8.4, "deepWater", "darkStone")
    group("坝前蓄水与下游")
    box(0, 2.46, z, 11.65, 3.25, 0.67, "water")
    for sign in (-1, 1):
        profile(sign * 5.52, 0, z, [(0, 1.1, 7.62), (0.27, 1.02, 7.48), (0.91, 0.70, 4.2)], "stone")
    ripples((-5.2, 5.2, -3.9, -1.36), z, 43, 26)
    ripples((-5.2, 5.2, 1.57, 3.92), z + 0.67, 83, 17)
    group("混凝土重力坝与闸孔")
    for x in (-4.13, 4.13):
        profile(x, 0.16, z, [(0, 2.78, 2.27), (1.18, 2.78, 1.25), (1.26, 2.78, 1.32)], "granite")
    box(0, 0.61, z, 5.47, 0.71, 1.15, "stone")
    box(0, 0.09, z + 1.20, 11.08, 1.50, 0.14, "stone")
    box(0, -0.48, z + 1.33, 10.98, 0.071, 0.084, "white")
    for i in range(15):
        x = (i - 7) * 0.375
        profile(x, -0.04, z, [(0.0, 0.114, 1.76), (1.18, 0.115, 1.17)], "granite")
        profile(x + 0.18, -0.31, z + 0.079, [(0, 0.238, 1.18), (0.31, 0.228, 0.78)], "darkStone")
        box(x + 0.165, -0.81, z + 0.064, 0.214, 1.18, 0.032, "waterLine")
        box(x, -0.19, z + 1.34, 0.14, 0.18, 0.25, "brown")
    group("坝顶附属设施")
    for x in (-4.61, -3.53, 3.51, 4.62):
        box(x, 0.3, z + 1.315, 0.68, 0.42, 0.195, "white")
        box(x, 0.3, z + 1.50, 0.70, 0.45, 0.045, "blue")


def dujiangyan():
    z = base(10.9, 8.2, "water", "deepWater")
    group("鱼嘴楔形分水堤")
    island = [(0.22, -3.45), (0.56, -2.62), (0.92, -1.81), (0.89, -0.57), (0.69, 0.87),
              (0.82, 2.38), (1.52, 3.94), (-0.94, 3.94), (-0.91, 2.38), (-0.73, 0.97), (-0.52, -0.63),
              (-0.44, -1.71), (-0.29, -2.54)]
    floorplan(0, 0, z, island, 0.32, "stone")
    inner = [(0.80 * x, y * 0.95 + 0.12) for x, y in island]
    floorplan(0, 0, z + 0.30, inner, 0.045, "grass")
    for i, (a, b) in enumerate(zip(island, island[1:] + island[:1])):
        beam((a[0], a[1], z + 0.302), (b[0], b[1], z + 0.302), 0.042, "white")
        if i % 2:
            beam((a[0] * 0.91, a[1] * 0.97, z + 0.11), (b[0] * 0.91, b[1] * 0.97, z + 0.11), 0.046, "darkStone")
    group("内外江水色与两岸")
    west = [(-5.24, -3.78), (-3.23, -3.78), (-3.23, -2.41), (-3.50, -0.12), (-3.20, 1.03), (-2.61, 2.36),
            (-2.7, 3.96), (-5.24, 3.96)]
    east = [(3.06, -3.95), (5.24, -3.95), (5.24, 3.94), (2.76, 3.94), (2.58, 2.12),
            (2.81, 0.48), (3.21, -0.81)]
    for outline in (west, east):
        floorplan(0, 0, z, outline, 0.43, "oak")
    ripples((-3.05, -0.86, -3.47, 3.49), z, 21, 21)
    ripples((1.02, 2.54, -3.49, 3.70), z, 18, 20)
    for i in range(8):
        tree(-4.22, -3.22 + i * 0.90, z + 0.43, 0.67 + (i % 3) * 0.10, i)
        tree(4.08, -3.23 + i * 0.91, z + 0.43, 0.64 + (i % 2) * 0.15, i + 1)
    group("索桥与堤面步道")
    beam((-2.77, 2.61, z + 0.53), (2.64, 2.61, z + 0.53), 0.075, "brown")
    for x in (-2.72, -0.71, 0.70, 2.61):
        box(x, 2.61, z + 0.36, 0.13, 0.15, 0.52, "timber")
    for side in (-1, 1):
        for i in range(18):
            a, b = -2.72 + i * 0.296, -2.72 + (i + 1) * 0.296
            m = (a + b) * 0.5
            h = 0.65 + 0.20 * abs(sin((m + 0.71) * 1.35))
            beam((a, 2.61 + side * 0.16, z + h), (b, 2.61 + side * 0.16, z + h), 0.022, "timber", 5)
            beam((m, 2.61 + side * 0.16, z + 0.53), (m, 2.61 + side * 0.16, z + h), 0.014, "timber", 4)


def victoria_harbour():
    z = base(10.7, 7.8, "water", "deepWater")
    group("尖沙咀岸线与前九广铁路钟楼")
    box(0, 2.30, z, 10.1, 2.56, 0.13, "stone")
    box(0, 0.98, z + 0.08, 10.0, 0.13, 0.09, "white")
    x, y = -2.55, 1.94
    box(x, y, z + 0.13, 0.98, 0.93, 0.16, "granite")
    profile(x, y, z + 0.25, [(0, 0.78, 0.75), (2.39, 0.67, 0.66), (2.50, 0.78, 0.77)], "redBrick")
    for h in (0.30, 0.85, 1.70, 2.37, 2.53, 2.98):
        box(x, y, z + h + 0.23, 0.81, 0.79, 0.048, "stone")
    box(x, y, z + 2.72, 0.76, 0.76, 0.62, "redBrick")
    for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        hh = z + 3.06
        start = (x + dx * 0.39, y + dy * 0.39, hh)
        end = (x + dx * 0.405, y + dy * 0.405, hh)
        cylinder(start, end, 0.23, 0.20, "white", 18)
        if dy:
            beam((x, end[1] + dy * 0.007, hh), (x + 0.088, end[1] + dy * 0.007, hh + 0.04), 0.014, "dark")
            beam((x, end[1] + dy * 0.007, hh), (x - 0.027, end[1] + dy * 0.007, hh + 0.102), 0.013, "dark")
    box(x, y, z + 3.33, 0.88, 0.86, 0.12, "granite")
    roofcone(x, y, z + 3.43, 0.52, 0.60, "brown", n=10)
    shaft(x, y, z + 4.01, 0.03, 0.30, "darkStone", 7, 0.014)
    group("天星码头与小轮")
    box(2.18, 0.17, z + 0.07, 2.79, 2.44, 0.13, "stone")
    for xx in (1.07, 3.15):
        for yy in (-0.86, 0.11, 1.13):
            shaft(xx, yy, z + 0.19, 0.060, 0.61, "white", 7)
    box(2.16, 0.19, z + 0.78, 2.67, 2.45, 0.091, "aqua")
    boat(0.02, -1.72, z, 1.22, ferry=True)
    ripples((-4.88, 4.82, -3.53, -0.65), z, 13, 34)


def tianjin_eye():
    z = base(10.8, 7.25, "deepWater", "darkStone")
    group("永乐桥及两岸")
    for side in (-1, 1):
        box(side * 4.63, 0, z, 1.20, 6.86, 0.37, "stone")
    for x in (-3.84, -2.44, 2.44, 3.84):
        box(x, 0.06, z, 0.44, 1.64, 0.75, "stone")
    box(0, 0.06, z + 0.73, 9.91, 1.73, 0.24, "iron")
    box(0, 0.06, z + 0.94, 9.86, 1.83, 0.074, "white")
    for yy in (-0.85, 0.96):
        rails(-4.92, 4.92, yy, z + 1.005, 18, "red")
        beam((-4.90, yy, z + 1.082), (4.90, yy, z + 1.082), 0.025, "white")
    group("摩天轮支架、轮圈与吊舱")
    center, radius = z + 3.93, 2.68
    for x in (-1.85, 1.85):
        for y in (-0.62, 0.79):
            cylinder((x, y, z + 0.99), (0, y * 0.34, center), 0.115, 0.095, "steel", 8)
    beam((0, -0.42, center), (0, 0.43, center), 0.255, "steel", 14)
    for side in (-1, 1):
        ring(0, side * 0.157, center, radius, 0.060, "white", 56, 5)
    for j in range(22):
        a = j * 2 * pi / 22
        x, zz = radius * cos(a), center + radius * sin(a)
        beam((0, -0.04, center), (x, -0.155, zz), 0.026, "steel")
        beam((x, -0.16, zz), (x, 0.16, zz), 0.033, "white")
        beam((x, 0.045, zz), (x, 0.045, zz - 0.15), 0.025, "iron", 5)
        profile(x, 0.10, zz - 0.36, [(0, 0.185, 0.24), (0.055, 0.26, 0.3),
                                      (0.207, 0.26, 0.30), (0.24, 0.15, 0.19)], "glass")
        box(x, 0.10, zz - 0.14, 0.218, 0.26, 0.052, "red")
    ripples((-3.96, 4.01, -3.30, -1.45), z, 16, 18)


def qingdao_zhanqiao():
    z = base(7.4, 11.0, "water", "deepWater")
    group("青岛湾与入海栈桥")
    box(0, 4.39, z, 6.75, 1.58, 0.26, "sand")
    box(0, 0.58, z + 0.05, 1.15, 8.25, 0.31, "darkStone")
    box(0, 0.58, z + 0.34, 1.23, 8.31, 0.08, "stone")
    for sign in (-1, 1):
        y_start = -3.52
        for i in range(39):
            y = y_start + i * 0.205
            box(sign * 0.585, y, z + 0.405, 0.058, 0.058, 0.22, "white")
        box(sign * 0.585, 0.47, z + 0.57, 0.060, 8.10, 0.050, "white")
    y = -3.67
    shaft(0, y, z + 0.04, 1.39, 0.34, "granite", 14)
    shaft(0, y, z + 0.37, 1.42, 0.11, "stone", 14)
    group("回澜阁·八角重檐")
    shaft(0, y, z + 0.46, 0.88, 0.72, "white", 8)
    for j in range(8):
        a = j * pi / 4
        shaft(0.80 * sin(a), y + 0.80 * cos(a), z + 0.45, 0.048, 0.78, "red", 7)
    roof8(0, y, z + 1.17, 1.04, 0.45, "goldTile")
    shaft(0, y, z + 1.37, 0.54, 0.45, "red", 8)
    roof8(0, y, z + 1.79, 0.76, 0.49, "goldTile")
    ripples((-3.45, -0.87, -4.93, 3.2), z, 10, 17)
    ripples((0.87, 3.45, -4.93, 3.2), z, 17, 17)


def portrait_surface(x, y, z):
    from math import exp
    radial_segments, levels = 30, 22
    rings = []
    for k in range(levels + 1):
        t = k / levels
        latitude = -pi / 2 + pi * t
        radius = max(0.007, cos(latitude))
        ring_points = []
        for i in range(radial_segments):
            phi = i * 2 * pi / radial_segments
            angle_center = min(phi, 2 * pi - phi)
            front = max(0.0, cos(phi)) ** 6
            eye = exp(-((angle_center - 0.48) / 0.18) ** 2 - ((t - 0.61) / 0.046) ** 2) * 0.24
            nose = exp(-(angle_center / 0.18) ** 2) * (
                0.35 * exp(-((t - 0.54) / 0.095) ** 2) + 0.15 * exp(-((t - 0.49) / 0.045) ** 2))
            lips = (0.14 * exp(-((t - 0.36) / 0.025) ** 2) + 0.09 * exp(-((t - 0.31) / 0.023) ** 2))
            lips *= exp(-(angle_center / 0.37) ** 2)
            cheek = 0.08 * exp(-((angle_center - 0.60) / 0.22) ** 2 - ((t - 0.49) / 0.085) ** 2)
            brow = 0.12 * exp(-((angle_center - 0.40) / 0.34) ** 2 - ((t - 0.688) / 0.03) ** 2)
            rr = radius * (0.84 + min(t * 0.7, 0.17))
            ring_points.append((x + rr * sin(phi) * 0.95,
                                y - 0.85 * rr * cos(phi) - ((nose + lips + cheek + brow) - eye) * front,
                                z + 1.43 * sin(latitude)))
        rings.append(ring_points)
    for k in range(levels):
        for i in range(radial_segments):
            j = (i + 1) % radial_segments
            face((rings[k][i], rings[k][j], rings[k+1][j], rings[k+1][i]),
                 "sculptedHair" if k > 16 or (k > 10 and radial_segments * 0.20 < i < radial_segments * 0.8)
                 else "sculptedStone")


def orange_isle():
    z = base(8.2, 8.9, "water", "deepWater")
    group("湘江洲头与缓坡")
    shore = [(-0.06, -3.84), (0.96, -3.52), (1.84, -2.44), (2.27, -0.78),
             (2.47, 1.14), (2.72, 4.18), (-2.73, 4.18), (-2.52, 1.00), (-2.32, -0.85),
             (-1.84, -2.44), (-0.95, -3.50)]
    floorplan(0, 0, z, shore, 0.29, "darkStone")
    floorplan(0, 0.04, z + 0.29, [(x * 0.94, y * 0.96) for x, y in shore], 0.10, "grass")
    path = [(-0.32, -3.18), (0.32, -3.18), (0.62, -1.79), (0.39, -0.17),
            (0.31, 3.93), (-0.31, 3.94), (-0.42, -1.09)]
    floorplan(0, 0, z + 0.38, path, 0.035, "sand")
    group("青年毛泽东艺术雕塑")
    profile(0, 0.42, z + 0.39, [(0, 3.58, 2.14), (0.37, 3.73, 2.21), (0.83, 3.32, 1.87),
                                 (1.19, 2.65, 1.67), (1.42, 1.62, 1.16)], "sculptedStone")
    portrait_surface(0.13, 0.43, z + 2.17)
    for sign in (-1, 1):
        sphere(0.13 + sign * 0.90, 0.51, z + 2.10, 0.12, 0.17, 0.30, "granite", 9, 6)
    for j in range(9):
        xx = -0.59 + j * 0.136
        yy = 0.40 + 0.12 * cos(j * 0.49)
        beam((xx, yy - 0.41, z + 3.33), (xx + 0.18, yy + 0.22, z + 3.48), 0.055, "darkStone", 5)
    for i in range(5):
        for sign in (-1, 1):
            tree(sign * (1.72 + i * 0.1), -1.51 + i * 1.13, z + 0.40, 0.49 + 0.07 * (i % 3), i)
    ripples((-3.78, -2.65, -3.66, 3.87), z, 103, 17)
    ripples((2.67, 3.78, -3.66, 3.87), z, 111, 17)


def sanxingdui():
    z = base(10.9, 8.4, "sand", "earth")
    group("新馆覆土缓坡")
    for x, y, width, depth, height in ((-2.60, 1.44, 4.4, 4.7, 0.52), (1.95, 2.41, 5.37, 3.12, 0.69)):
        profile(x, y, z, [(0, width, depth), (height, width * 0.58, depth * 0.60)], "grass")
    group("堆列式展馆·青铜色折面")
    for x, y, w, h, skew in ((-2.73, 1.40, 3.58, 2.02, 0.57), (0.03, 0.23, 3.72, 2.68, 0.97), (2.85, 1.16, 3.67, 1.86, 0.72)):
        bottom = [(x-w*0.55, y-1.50, z+0.03), (x+w*0.50, y-1.50, z+0.03), (x+w*0.53, y+1.51, z+0.03), (x-w*0.54, y+1.43, z+0.03)]
        top = [(x-w*0.41+skew, y-1.21, z+h-0.25), (x+w*0.37+skew, y-1.16, z+h),
               (x+w*0.43+skew, y+1.40, z+h*0.80), (x-w*0.40+skew, y+1.36, z+h*0.79)]
        for j in range(4):
            j2 = (j + 1) % 4
            face((bottom[j], bottom[j2], top[j2], top[j]), "greenBronze" if j < 2 else "stone")
        face(top, "stone")
        for j in range(14):
            t = 0.07 + (j / 14) * 0.86
            a, b = bottom[0], bottom[1]
            p, q = top[0], top[1]
            point = tuple(a[i] * (1-t) + b[i] * t for i in range(3))
            cap = tuple(p[i] * (1-t) + q[i] * t for i in range(3))
            beam((point[0], point[1]-0.025, point[2]+0.37), (cap[0], cap[1]-0.025, cap[2]-0.04),
                 0.027, "bronze", 4)
        box(x + w * 0.12, y-1.52, z+0.032, w * 0.61, 0.045, 0.47, "glass")
    group("前庭铜色纹样")
    box(0, -3.05, z+0.015, 5.80, 1.23, 0.035, "stone")
    mask = [(-0.73,-0.45), (0.73,-0.45), (0.92,-0.19), (1.30,0.11), (1.66,0.09), (1.26,0.48),
            (0.64,0.43), (0.31,0.68), (0,0.46), (-0.31,0.68), (-0.64,0.43), (-1.26,0.48),
            (-1.66,0.09), (-1.30,0.11), (-0.92,-0.19)]
    for i, p in enumerate(mask):
        q = mask[(i+1) % len(mask)]
        beam((p[0], p[1]-2.82, z+0.062), (q[0], q[1]-2.82, z+0.062), 0.046, "greenBronze", 5)
    group("前庭步道及侧坡绿植")
    for side in (-1, 1):
        for i in range(6):
            x = side * (2.65 + i * 0.39)
            box(x, -2.79 + i * 0.074, z + 0.015, 0.28, 0.88, 0.029, "stone")
        for x, y, scale in ((4.65, -1.78, 0.43), (4.74, -0.87, 0.44), (4.79, 2.68, 0.56)):
            tree(side * x, y, z, scale, 1 if side > 0 else 2)


def taipei_palace():
    z = base(10.7, 8.7, "grass", "earth")
    group("博物院花岗石平台与中轴阶梯")
    box(0, 1.47, z, 9.38, 5.13, 0.31, "white")
    box(0, 1.39, z + 0.31, 8.40, 4.68, 0.15, "stone")
    steps(0, -3.93, z, 3.06, 3.04, 0.36, 12, "white")
    for s in (-1, 1):
        box(s*1.56, -2.29, z+0.012, 0.13, 3.28, 0.24, "stone")
    group("院区正馆与绿色琉璃瓦")
    box(0, 0.79, z+0.46, 4.27, 2.41, 2.12, "white")
    hip(0, 0.79, z+2.53, 5.06, 2.95, 0.67, "jade", "jade", 0.28)
    box(0, 0.92, z+2.71, 3.08, 1.82, 0.28, "cream")
    hip(0, 0.93, z+2.95, 4.22, 2.38, 0.67, "jade", "jade", 0.31)
    for x in (-1.72, -0.87, 0, 0.87, 1.72):
        box(x, -0.464, z+0.46, 0.093, 0.10, 1.92, "stone")
        window(x+0.26, -0.441, z+1.08, 0.29, 0.70, "white", "glass")
    for s in (-1, 1):
        xx = s * 3.44
        box(xx, 1.31, z+0.46, 2.69, 2.68, 1.38, "cream")
        hip(xx, 1.32, z+1.82, 3.04, 2.91, 0.48, "jade", "jade", 0.18)
        for n in (-1, 0, 1):
            window(xx+n*0.53, -0.043, z+0.93, 0.30, 0.44, "white", "glass")
        tree(s*3.7, -2.66, z, 0.88, 1)
        tree(s*4.40, -1.63, z, 0.73, 2)


def yalu_broken_bridge():
    z = base(11.4, 7.1, "deepWater", "darkStone")
    group("丹东江岸与石桥台")
    box(-4.76, 0, z, 1.65, 6.72, 0.32, "stone")
    box(-4.75, 1.41, z+0.32, 1.55, 3.21, 0.11, "grass")
    group("断桥连续桁架与桥墩")
    from_x, to_x = -4.73, 2.39
    for x in (-4.34, -2.62, -0.73, 1.19, 2.61, 3.75, 4.91):
        profile(x, 0, z, [(0, 0.42, 1.73), (0.17, 0.41, 1.68), (0.70, 0.29, 1.44)], "stone")
    box((from_x+to_x)*0.5, 0, z+0.67, to_x-from_x, 1.11, 0.18, "iron")
    box((from_x+to_x)*0.5, 0, z+0.84, to_x-from_x, 0.91, 0.04, "granite")
    for sign in (-1, 1):
        yy = sign * 0.51
        for x1, x2 in ((-4.73,-2.89),(-2.89,-0.97),(-0.97,0.91),(0.91,2.39)):
            mid = (x1+x2)*0.5
            corners = [(x1, yy, z+0.79), (x1+0.19, yy, z+1.57), (mid, yy, z+1.83),
                       (x2-0.17, yy, z+1.54), (x2, yy, z+0.79)]
            for a, b in zip(corners, corners[1:]):
                beam(a, b, 0.044, "iron")
            for j in range(6):
                x = x1 + (x2-x1)*j/6
                h = 0.75 + 0.24 * sin(pi*j/6)
                beam((x,yy,z+0.83),(x,yy,z+0.86+h),0.026,"iron")
                beam((x,yy,z+0.86+h),(x+(x2-x1)/6,yy,z+0.83),0.025,"iron")
    for x in (-4.57, -3.69, -2.99, -2.02, -0.92, 0.06, 0.89, 1.72, 2.35):
        beam((x,-0.51,z+1.62),(x,0.51,z+1.62),0.041,"iron")
    for j in range(7):
        beam((to_x,-0.47+j*0.16,z+0.79),(to_x+0.11*(j%3),-0.47+j*0.16,z+0.67-0.04*(j%3)),0.027,"rust")
    ripples((-3.51,5.22,-3.26,-1.14), z, 68, 17)
    ripples((-3.51,5.24,1.23,3.23), z, 53, 14)


def nanjing_museum():
    z = base(10.1, 7.8, "stone", "darkStone")
    group("历史馆台基·仿辽大殿")
    box(0, 0.8, z, 8.63, 4.79, 0.23, "granite")
    box(0, 0.8, z+0.23, 7.93, 4.20, 0.25, "stone")
    steps(0, -3.17, z, 4.67, 1.95, 0.46, 10, "white")
    box(0, 0.65, z+0.47, 6.48, 3.05, 1.39, "deepRed")
    for x in range(-5, 6):
        xx = x * 0.65
        shaft(xx, -0.97, z+0.49, 0.066, 1.39, "red", 8)
        if x < 5:
            window(xx+0.325, -0.922, z+0.65, 0.42, 0.91, "timber")
        box(xx, -1.005, z+1.69, 0.28, 0.17, 0.15, "jade")
    hip(0, 0.66, z+1.86, 8.17, 4.15, 1.19, "goldTile", "jade", 0.27)
    for sign in (-1, 1):
        box(sign*3.61, 0.69, z+0.49, 0.61, 2.74, 1.15, "darkStone")
        gable(sign*3.61, 0.69, z+1.64, 0.82, 2.98, 0.27, "slate")
        tree(sign*4.07, -2.86, z, 0.79, 0)


def kiln_vault(x, y, z, radius, rise, length):
    geometric_arch(x, y, z, radius, rise, 0.13, length, "brick", 18)
    for yy in (y-length/2-0.021, y+length/2+0.021):
        geometric_arch(x, yy, z, radius-0.001, rise-0.001, 0.155, 0.055, "terracotta", 18)
    box(x-radius-0.071, y, z-0.06, 0.16, length, 0.12, "brick")
    box(x+radius+0.071, y, z-0.06, 0.16, length, 0.12, "brick")


def jingdezhen_kiln_museum():
    z = base(11.1, 8.4, "sand", "terracotta")
    group("御窑厂入口及下沉庭院")
    box(0, 2.05, z, 10.33, 3.53, 0.26, "stone")
    box(-3.52, -1.23, z, 3.12, 4.87, 0.18, "stone")
    box(3.59, -1.98, z+0.01, 2.53, 3.60, 0.10, "granite")
    box(1.05, -2.71, z+0.018, 2.13, 1.39, 0.057, "deepWater")
    steps(1.30, -0.92, z, 1.2, 1.12, 0.18, 7, "granite")
    group("回收窑砖拱壳群")
    for x, y, r, rise, length, zz in (
        (-3.48, 0.36, 0.73, 1.54, 5.24, 0.19), (-1.78, 0.59, 0.60, 1.08, 4.83, 0.17),
        (-0.33, 1.52, 0.64, 1.32, 3.73, 0.28), (1.24, 1.73, 0.68, 1.55, 3.64, 0.28),
        (2.93, 0.39, 0.70, 1.21, 4.81, 0.14), (4.23, 1.03, 0.46, 0.91, 3.72, 0.24),
    ):
        kiln_vault(x, y, z+zz, r, rise, length)
    tree(-4.45,-2.94,z+0.18,0.69,0)
    tree(4.53,-2.81,z+0.12,0.84,2)


def ice_spire(x, y, z, radius, height):
    levels = [(0, radius), (0.16, radius), (0.18, radius*0.79), (0.37, radius*0.79),
              (0.40,radius*0.61), (0.62,radius*0.61), (0.65,radius*0.40),
              (0.81,radius*0.40), (0.84,radius*0.30), (0.98,radius*0.055), (1, 0.02)]
    for i, (a, b) in enumerate(zip(levels, levels[1:])):
        shaft(x, y, z+a[0]*height, a[1], (b[0]-a[0])*height,
              ("ice","snow","paleIce")[i%3], 8, b[1])
    for k in range(8):
        angle = k*pi/4
        dx, dy = radius*0.78*cos(angle), radius*0.78*sin(angle)
        shaft(x+dx, y+dy, z+height*0.09, radius*0.13, height*0.37, "paleIce", 6, radius*0.07)


def harbin_ice_world():
    z = base(10.6, 9.0, "snow", "paleIce")
    group("冰雪大世界·冰块广场与走廊")
    box(0, -2.32, z, 9.17, 3.41, 0.13, "paleIce")
    for side in (-1, 1):
        for i in range(5):
            xx = side * (0.85+i*0.73)
            box(xx, -2.92, z+0.13, 0.34, 0.34, 0.24, "ice")
            shaft(xx, -2.92, z+0.33, 0.23, 0.29, "paleIce", 6, 0.02)
    group("冰晶主塔·层叠积冰")
    x, y = 0, 0.78
    profile(x, y, z, [(0, 4.36, 3.45), (0.26, 4.36, 3.45), (0.36, 3.55, 2.93), (0.53, 3.55, 2.93)], "ice")
    ice_spire(x, y, z+0.50, 1.60, 5.62)
    for x, y, size, h in (
        (-1.55, -0.32, 0.62, 2.59), (1.54, -0.32, 0.62, 2.59), (-1.10, 1.97, 0.73, 3.18),
        (1.12, 1.97, 0.71, 3.19), (-3.25, 1.48, 0.66, 2.15), (3.25, 1.48, 0.66, 2.15),
        (-3.62, -1.15, 0.52, 1.56), (3.62, -1.15, 0.52, 1.56),
    ):
        ice_spire(x, y, z+0.05, size, h)
    geometric_arch(0, -0.77, z+0.83, 0.69, 0.74, 0.20, 0.28, "paleIce")


def giraffe(x, y, z, scale, color="honey"):
    def point(px, py, pz):
        return x+px*scale, y+py*scale, z+pz*scale

    sphere(*point(0, 0, 1.0), 0.61*scale, 0.23*scale, 0.27*scale, color, 12, 8)
    for dx in (-0.42, 0.40):
        for dy in (-0.14, 0.14):
            cylinder(point(dx,dy,0.04),point(dx+0.037,dy,0.97),0.052*scale,0.075*scale,color,6)
            beam(point(dx-0.035,dy,0.043),point(dx+0.09,dy,0.043),0.041*scale,"timber",5)
    cylinder(point(0.38,0,1.07),point(0.73,0,2.06),0.16*scale,0.105*scale,color,10)
    sphere(*point(0.86,0,2.10),0.24*scale,0.10*scale,0.108*scale,color,11,7)
    for side in (-1,1):
        beam(point(0.78,side*0.052,2.17),point(0.75,side*0.07,2.31),0.026*scale,"timber",5)
        sphere(*point(0.74,side*0.113,2.13),0.06*scale,0.09*scale,0.037*scale,color,7,5)
    beam(point(-0.53,0,1.1),point(-0.64,0,0.69),0.023*scale,"timber",5)
    for px, pz, ss in ((-0.36,1.04,0.092),(-0.21,1.15,0.073),(0.03,1.08,0.082),(0.22,1.03,0.076),
                        (0.54,1.43,0.070),(0.68,1.82,0.061)):
        side_y = 0.185 if pz < 1.25 else 0.099
        for side in (-1,1):
            sphere(*point(px,side*side_y,pz),ss*scale,0.026*scale,ss*0.68*scale,"rust",7,4)


def chimelong_safari():
    z = base(10.8, 8.1, "grass", "earth")
    group("野生动物世界·南入口")
    path = [(-1.21,-3.79), (1.23,-3.79), (1.13,-1.68), (2.06,0.22), (3.45,2.31),
            (2.75,2.80), (1.54,1.88), (-0.72,0.16), (-1.20,-1.28)]
    floorplan(0,0,z,path,0.045,"sand")
    for s in (-1,1):
        x = s*2.68
        box(x,-1.72,z,2.48,1.31,0.69,"brown")
        gable(x,-1.72,z+0.69,2.73,1.57,0.52,"jade")
        for xx in (-0.82,0.0,0.82):
            window(x+xx,-2.391,z+0.14,0.31,0.33,"timber","glass")
        for xx in (-1.11,1.12):
            shaft(x+xx,-2.42,z+0.06,0.064,0.71,"timber",6)
    geometric_arch(0,-1.57,z+1.01,1.23,0.56,0.17,0.26,"timber",12)
    for x in (-1.41,1.41):
        profile(x,-1.58,z,[(0,0.33,0.42),(0.93,0.33,0.34),(1.09,0.28,0.28)],"ochre")
    group("小型动物活动场")
    floorplan(0,0,z,[(-3.89,0.33),(-0.18,0.23),(1.06,2.38),(-0.64,3.72),(-3.64,3.49)],0.028,"sand")
    giraffe(-1.42,0.86,z+0.026,1.15)
    giraffe(-2.71,1.86,z+0.027,0.86)
    for j in range(12):
        x=-4.56+j*0.81
        y=3.14+0.28*cos(j*0.78)
        tree(x,y,z,0.69+0.13*(j%3),j)
    for x,y in ((-4.23,-0.09),(4.31,-0.89),(3.41,0.49),(4.38,1.53),(-3.78,0.98)):
        tree(x,y,z,0.81,1)


def qingming_park():
    z = base(11.0, 7.25, "water", "deepWater")
    group("汴河两岸与船只")
    for side in (-1,1):
        box(side*4.31,0,z,1.93,6.97,0.23,"grass")
        box(side*3.53,0,z+0.17,0.45,6.9,0.075,"stone")
    ripples((-3.37,3.37,-3.38,-1.15),z,14,18)
    ripples((-3.31,3.31,1.22,3.35),z,78,12)
    boat(-1.11,-2.11,z+0.012,0.77)
    boat(1.67,2.14,z+0.012,0.61)
    group("虹桥木构单跨·镂空桥拱")
    for yy in (-0.54,-0.21,0.21,0.54):
        geometric_arch(0,yy,z+0.17,3.25,1.33,0.15,0.13,"timber",20)
    for i in range(31):
        x=(i-15)*0.220
        h=z+0.18+1.46*sqrt(max(0,1-(x/3.40)**2))
        box(x,0,h,0.246,1.39,0.09,"brown")
        if i%3==0:
            for side in (-1,1):
                shaft(x,side*0.64,h+0.07,0.045,0.31,"red",6)
    for side in (-1,1):
        for i in range(24):
            def top(index):
                x=-3.34+index*(6.68/24)
                return x,side*0.65,z+0.48+1.46*sqrt(max(0,1-(x/3.40)**2))
            beam(top(i),top(i+1),0.036,"red",5)
    group("两岸宋式民居")
    for s in (-1,1):
        for i,y in enumerate((-2.35,1.31,2.56)):
            x=s*(4.24+(i%2)*0.10)
            h=0.67+(i%2)*0.24
            box(x,y,z+0.23,1.22,0.81,h,"white")
            gable(x,y,z+0.23+h,1.38,0.96,0.48,"slate")
            window(x,y-0.42,z+0.24,0.26,0.50,"red","dark")
    for x,y in ((-4.69,0.1),(4.73,-0.78)):
        tree(x,y,z+0.23,0.67,2)


SCENES = {
    "slender-west-lake": slender_west_lake, "hongcun": hongcun, "fenghuang": fenghuang,
    "kaiping-diaolou": kaiping_diaolou, "haikou-arcades": haikou_arcades, "kashgar-old-city": kashgar_old_city,
    "tiananmen-square": tiananmen_square, "oriental-pearl": oriental_pearl, "three-gorges-dam": three_gorges_dam,
    "dujiangyan": dujiangyan, "victoria-harbour": victoria_harbour, "tianjin-eye": tianjin_eye,
    "qingdao-zhanqiao": qingdao_zhanqiao, "orange-isle": orange_isle, "sanxingdui": sanxingdui,
    "taipei-palace": taipei_palace, "yalu-broken-bridge": yalu_broken_bridge, "nanjing-museum": nanjing_museum,
    "jingdezhen-kiln-museum": jingdezhen_kiln_museum, "harbin-ice-world": harbin_ice_world,
    "chimelong-safari": chimelong_safari, "qingming-park": qingming_park,
}
