"""Editable scene geometry for six modern museums and civic sites."""

from math import cos, pi, sin
from random import Random

from mathutils import Vector

from geometry import box, face, floorplan, group, hip, profile, steps
from scenes import PALETTE as URBAN_PALETTE, base, beam, palette_entry, tree

PALETTE = {**URBAN_PALETTE, **{
    name: palette_entry(*value) for name, value in {
        "ivoryMetal": ("deded8", "grain", 0.64), "silverSteel": ("bfc7cc", "", 0.47),
        "brightSteel": ("e1e4e3", "", 0.45), "shadowSteel": ("8d969d", "", 0.55),
        "perforated": ("b6bec2", "tile", 0.72), "blueglass": ("647d87", "", 0.42),
        "reflectGlass": ("819694", "", 0.42), "nightGlass": ("364f5a", "", 0.49),
        "brightGlass": ("abc0c0", "", 0.52), "metalDark": ("545c5d", "grain", 0.64),
        "lakeCanopy": ("716859", "tile", 0.67), "roofCopper": ("71615a", "tile", 0.68),
        "sandStone": ("cfc2a8", "brick", 0.82), "travertine": ("dfd5bd", "grain", 0.74),
        "chalkStone": ("dfdfd2", "brick", 0.82), "whiteStone": ("e1ded3", "grain", 0.80),
        "darkBrick": ("656969", "brick", 0.83), "monumentStone": ("565a59", "brick", 0.85),
        "shadowStone": ("777872", "grain", 0.85), "ledgeStone": ("acada0", "grain", 0.78),
        "carvedName": ("969896", "", 0.83),
        "warmConcrete": ("b4b6ae", "grain", 0.80), "paving": ("afada1", "tile", 0.83),
        "redSeats": ("a74440", "", 0.83), "darkRedSeats": ("713d38", "", 0.85),
        "trackRed": ("a16360", "", 0.81), "fieldGreen": ("839c5f", "grain", 0.79),
    }.items()
}}


def clean_edge(points, thickness, color, closed=False):
    pairs = zip(points, points[1:] + points[:1] if closed else points[1:])
    for a, b in pairs:
        beam(a, b, thickness, color, 4)


def curtain_wall(x, y, z, width, height, columns, rows, dark=False):
    glass = ("blueglass", "nightGlass", "reflectGlass") if dark else ("reflectGlass", "blueglass", "brightGlass")
    ww, hh = width / columns, height / rows
    for i in range(columns):
        xx = x - width / 2 + (i + 0.5) * ww
        for j in range(rows):
            pane = glass[(i // 2 + j * 2) % len(glass)] if (i + j) % 7 == 0 else glass[0]
            box(xx, y, z + j * hh + 0.019, ww * 0.966, 0.035, hh - 0.035, pane)
        box(xx - ww / 2, y - 0.020, z, 0.024, 0.055, height, "metalDark")
    for j in range(rows + 1):
        box(x, y - 0.018, z + hh * j, width, 0.049, 0.032, "silverSteel")


def ellipse(count, x, y, rx, ry):
    return [(x + rx * cos(2 * pi * i / count), y + ry * sin(2 * pi * i / count)) for i in range(count)]


def beam_section(point, axis, width, thickness):
    across = Vector((0, 0, 1)).cross(axis)
    if across.length < 0.00001:
        across = Vector((0, 1, 0)).cross(axis)
    across.normalize()
    up = axis.cross(across).normalized()
    return [point + (across * width * a + up * thickness * b) for a, b in (
        (-0.5, -0.5), (0.5, -0.5), (0.5, 0.5), (-0.5, 0.5))]


def square_ribbon(points, width, depth, palette):
    closed = points[0] == points[-1]
    vertices = [Vector(p) for p in (points[:-1] if closed else points)]
    last = len(vertices) - 1
    sections = []
    for i, vertex in enumerate(vertices):
        previous = vertices[i-1] if i or closed else vertex
        following = vertices[(i+1) % len(vertices)] if i != last or closed else vertex
        direction = (following - previous).normalized()
        sections.append(beam_section(vertex, direction, width, depth))
    following_sections = sections[1:] + ([sections[0]] if closed else [])
    for idx, (start, end) in enumerate(zip(sections, following_sections)):
        for i in range(4):
            j = (i + 1) % 4
            face((start[i], start[j], end[j], end[i]), palette[idx % len(palette)])
    if not closed:
        face(sections[0][::-1], palette[0])
        face(sections[-1], palette[-1])


def square_beam(a, b, width, thickness, material_name):
    if (Vector(b) - Vector(a)).length > 0.000001:
        square_ribbon([a,b], width, thickness, [material_name])


def china_science_museum():
    z = base(10.9, 9.3, "paving", "shadowStone")
    group("入口广场与绿带")
    box(0.78, -2.93, z + 0.014, 4.65, 2.01, 0.018, "chalkStone")
    for side in (-1, 1):
        box(side * 4.10, -2.68, z + 0.028, 1.51, 2.88, 0.061, "grass")
        for j in range(3):
            tree(side * 4.10, -3.53 + j * 0.86, z + 0.089, 0.52 + j * 0.09, j + 1)
    steps(0.64, -3.05, z, 4.56, 1.44, 0.21, 8, "warmConcrete")
    group("鲁班锁主体·相互咬合的体块")
    box(0.07, 0.59, z + 0.18, 8.39, 6.03, 2.26, "warmConcrete")
    box(-2.43, 0.98, z + 0.20, 3.79, 6.29, 3.45, "ivoryMetal")
    box(2.87, 0.88, z + 0.22, 3.25, 6.35, 2.93, "ivoryMetal")
    box(0.70, 1.24, z + 2.49, 3.47, 5.55, 1.23, "ivoryMetal")
    box(0.34, 0.46, z + 2.79, 2.94, 6.82, 0.84, "silverSteel")
    box(-1.72, -1.38, z + 1.95, 2.75, 2.42, 0.81, "chalkStone")
    box(2.42, -1.62, z + 1.92, 3.65, 2.57, 1.17, "ivoryMetal")
    box(-2.01, 3.03, z + 3.61, 3.57, 1.68, 0.16, "whiteStone")
    box(2.48, 2.66, z + 3.12, 3.89, 2.03, 0.16, "paving")
    group("立面凹槽与方形穿孔窗")
    curtain_wall(0.61, -2.476, z + 0.23, 4.28, 1.61, 14, 4, True)
    curtain_wall(-2.80, -2.163, z + 0.89, 2.81, 0.43, 10, 1, True)
    curtain_wall(-2.67, -2.181, z + 2.69, 2.70, 0.39, 11, 1, True)
    curtain_wall(2.62, -2.919, z + 2.39, 3.06, 0.38, 12, 1, True)
    curtain_wall(0.18, -2.946, z + 3.08, 2.64, 0.39, 12, 1, True)
    for a, b, y, h in ((-4.24, -2.1, -2.20, 2.46), (1.04, 4.14, -2.906, 3.08)):
        for j in range(14):
            xx = a + j * (b - a) / 13
            box(xx, y, z + h, 0.077, 0.035, 0.088, "metalDark")
    for x in (-4.354, 4.54):
        for index in range(14):
            box(x, -1.68 + index * 0.357, z + 1.36, 0.04, 0.258, 0.25, "nightGlass")
    group("入口门廊")
    box(0.61, -2.83, z + 1.86, 4.54, 1.03, 0.075, "silverSteel")
    for x in (-1.34, -0.38, 0.63, 1.63, 2.63):
        box(x, -3.11, z + 0.21, 0.063, 0.064, 1.69, "brightSteel")


def low_chu_roof(x, y, z, width, depth, height, color):
    hip(x, y, z, width, depth, height, color, "metalDark", 0.20)
    box(x, y, z-0.05, width*0.96, depth*0.94, 0.09, "charcoal")
    for mul in (-1, 1):
        square_beam((x - width * 0.34, y + mul * depth * 0.474, z + 0.02),
                    (x + width * 0.34, y + mul * depth * 0.474, z + 0.02),
                    0.049, 0.047, "slate")


def hubei_museum():
    z = base(11.3, 9.26, "paving", "warmConcrete")
    group("南馆入口中轴与台基")
    box(0, 0.23, z, 9.95, 7.56, 0.17, "stone")
    box(0, 0.34, z + 0.17, 9.47, 7.13, 0.12, "chalkStone")
    steps(0, -3.98, z + 0.02, 4.45, 1.27, 0.27, 10, "chalkStone")
    for s in (-1, 1):
        box(s * 3.75, -3.64, z + 0.018, 2.43, 1.41, 0.041, "grass")
        for i in range(4):
            tree(s * (3.00 + 0.56 * i), -3.81 + 0.16 * (i % 2), z + 0.056, 0.54+0.03*i, i + 1)
    group("文展大楼·鼎形南主馆")
    box(0, -1.01, z+0.28, 8.27, 3.74, 0.58, "nightGlass")
    curtain_wall(0, -2.903, z + 0.29, 8.06, 0.56, 23, 2, True)
    box(0, -0.92, z+0.86, 3.4, 3.36, 1.10, "blueglass")
    curtain_wall(0, -2.641, z+0.88, 3.31, 1.09, 14, 3, True)
    box(0, -1.57, z+0.78, 3.93, 2.27, 0.15, "silverSteel")
    box(0, -0.96, z+1.96, 4.04, 3.48, 0.083, "metalDark")
    box(0, 0.34, z+2.02, 3.67, 0.52, 0.026, "blueglass")
    for s in (-1, 1):
        x = s * 3.24
        profile(x,-1.01,z+0.78,[(0,2.29,3.22),(0.19,2.59,3.61),(1.27,3.07,4.02)],"travertine")
        box(x,-1.01,z+2.04,2.94,3.89,0.07,"shadowStone")
        for row in range(3):
            box(x + (row-1)*0.65,-0.84,z+2.11,0.32,1.27,0.043,"chalkStone")
        box(s*4.54,-1.39,z+0.37,0.075,2.17,0.43,"blueglass")
    group("后景·楚式屋檐与连廊")
    box(0,2.40,z+0.27,8.89,2.96,0.21,"chalkStone")
    box(0,2.50,z+0.47,4.15,2.20,1.96,"warmConcrete")
    for zz, width, depth, height in ((1.45,4.63,2.66,0.32),(2.02,4.95,2.88,0.39),(2.44,5.17,3.01,0.67)):
        low_chu_roof(0,2.53,z+zz,width,depth,height,"slate")
    for s in (-1,1):
        x = s * 3.49
        box(x,2.30,z+0.47,2.28,2.15,1.23,"sandStone")
        low_chu_roof(x,2.30,z+1.67,2.57,2.58,0.61,"slate")


def octagon(width, depth, corner):
    x, y = width / 2, depth / 2
    return [(-x + corner, -y), (x - corner, -y), (x, -y + corner), (x, y - corner),
            (x - corner, y), (-x + corner, y), (-x, y - corner), (-x, -y + corner)]


def hunan_museum():
    z = base(11.4, 8.6, "paving", "shadowStone")
    group("馆前木栈与景观浅池")
    box(0, -2.56, z + 0.016, 6.12, 2.72, 0.046, "chalkStone")
    box(0.04, -2.42, z + 0.058, 3.13, 2.18, 0.023, "deepWater")
    box(0, -2.56, z + 0.081, 1.22, 2.68, 0.036, "brown")
    for index in range(18):
        box(0, -3.82 + index * 0.147, z + 0.116, 1.22, 0.010, 0.004, "rust")
    for s in (-1, 1):
        box(s * 4.64, -2.6, z + 0.038, 1.34, 2.31, 0.049, "grass")
        tree(s * 4.64, -3.17, z + 0.085, 0.71, 1)
        tree(s * 4.64, -2.25, z + 0.085, 0.60, 2)
    group("展馆侧翼")
    for s in (-1, 1):
        x = s * 3.59
        box(x, 0.85, z + 0.086, 3.00, 5.18, 2.45, "sandStone")
        box(x - s * 0.22, 1.29, z + 2.53, 2.78, 4.31, 0.12, "shadowStone")
        box(x + s * 0.42, 1.69, z + 2.66, 1.55, 3.14, 0.045, "grass")
        curtain_wall(x, -1.753, z + 0.39, 2.89, 0.60, 9, 1)
        for i in range(7):
            box(x + (-0.97 + i * 0.31), -1.755, z + 0.82, 0.116, 0.026, 1.42, "ledgeStone")
    group("鼎盛洞庭·悬挑顶棚与中庭立面")
    box(0, 0.73, z + 0.083, 4.40, 5.28, 2.58, "metalDark")
    curtain_wall(0, -1.938, z + 0.09, 4.31, 2.47, 15, 8)
    canopy = octagon(7.44, 6.59, 1.62)
    floorplan(0, 0.47, z + 2.64, canopy, 0.19, "metalDark")
    smaller = [(xx * 0.92, yy * 0.90) for xx, yy in canopy]
    floorplan(0, 0.47, z + 2.82, smaller, 0.14, "lakeCanopy")
    inner_top = [(xx * 0.80, yy * 0.82) for xx, yy in canopy]
    for i in range(len(canopy)):
        a,b = canopy[i], canopy[(i+1) % len(canopy)]
        c,d = inner_top[i], inner_top[(i+1) % len(canopy)]
        face(((a[0],0.47+a[1],z+2.85),(b[0],0.47+b[1],z+2.85),
              (d[0],0.47+d[1],z+3.05),(c[0],0.47+c[1],z+3.05)), "roofCopper")
    floorplan(0, 0.47, z + 3.045, inner_top, 0.035, "lakeCanopy")
    box(0, -2.037, z + 0.10, 2.36, 0.88, 0.06, "travertine")
    for x in (-1.77,-1.34,1.34,1.77):
        box(x, -2.29, z + 0.11, 0.085, 0.076, 2.57, "whiteStone")
    for index in range(9):
        box(-1.25 + index * 0.32, -2.023, z + 1.41, 0.033, 0.023, 1.24, "brightSteel")


def shanghai_museum_east():
    z = base(11.9, 9.0, "paving", "ledgeStone")
    group("东馆前庭与台阶")
    steps(0.12, -3.89, z, 5.16, 1.39, 0.29, 9, "chalkStone")
    box(0.17, -2.85, z + 0.03, 6.73, 2.08, 0.145, "warmConcrete")
    for sign in (-1, 1):
        box(sign * 4.60, -3.13, z + 0.018, 2.03, 1.73, 0.052, "grass")
        for j in range(3):
            tree(sign * (4.29 + j * 0.49), -3.63 + j * 0.30, z + 0.071, 0.43 + j * 0.09, j + 1)
    group("浅色矩形馆体和夹层玻璃")
    y = 0.53
    box(0, y, z+0.17, 9.87, 5.57, 1.20, "warmConcrete")
    box(0, y + 0.11, z + 1.37, 9.72, 5.35, 2.32, "whiteStone")
    box(-2.50, 1.50, z + 3.68, 3.69, 3.30, 0.27, "travertine")
    box(2.52, 1.40, z + 3.68, 3.62, 3.15, 0.28, "travertine")
    box(0, 0.82, z + 3.68, 2.21, 2.84, 0.21, "reflectGlass")
    curtain_wall(0.08, -2.272, z + 0.21, 5.20, 0.82, 18, 2, True)
    curtain_wall(0, -2.283, z + 1.11, 9.51, 0.62, 25, 2, True)
    for sign in (-1, 1):
        x = sign * 4.869
        box(x, 0.41, z + 1.35, 0.07, 5.07, 0.44, "nightGlass")
        for i in range(13):
            box(x, -1.88 + i * 0.383, z + 1.36, 0.082, 0.033, 0.43, "silverSteel")
    group("大理石波浪幕墙")
    # Lower edge climbs toward the visitor's right. The wall rolls away in depth as it rises.
    n = 33
    panel_nodes = []
    for index in range(n + 1):
        t = index / n
        wave = (0.5 - 0.5 * cos(pi * t))
        xx = -4.93 + 9.86 * t
        eased = wave * (0.84 + 0.17 * sin(pi*t))
        bottom = z + 1.82 + 1.29 * eased
        bulge = 0.19 + 0.39 * sin(pi * t) ** 1.15
        yy = -2.243 - bulge * (0.96 - wave * 0.25)
        panel_nodes.append([(xx, yy + bulge * row / 5, bottom + (z+3.73-bottom)*row/5) for row in range(6)])

    for col, (a, b) in enumerate(zip(panel_nodes, panel_nodes[1:])):
        for row in range(5):
            face((a[row], b[row], b[row+1], a[row+1]),
                 "travertine" if (col * 17 + row * 3) % 11 == 0 else "whiteStone")
        qa, qb = a[0], b[0]
        face((qb, qa, (qa[0], -2.18, qa[2] - 0.026), (qb[0], -2.18, qb[2] - 0.026)), "sandStone")
        if col % 2 == 0:
            clean_edge(a, 0.010, "chalkStone")
    for i in (0, -1):
        start = panel_nodes[i]
        for a, b in zip(start, start[1:]):
            face((a, b, (b[0], -2.13, b[2]), (a[0], -2.13, a[2])), "travertine")
    for j in (1, 2, 3, 4):
        clean_edge([shape[j] for shape in panel_nodes], 0.007, "chalkStone")
    group("顶棚步道与玻璃护栏")
    for xx in (-4.08,-3.51,3.50,4.12):
        box(xx, 2.09, z + 3.86, 0.36, 1.01, 0.048, "grass")
    box(0, 1.62, z + 3.70, 2.44, 0.085, 0.13, "blueglass")
    box(0.08, -2.59, z + 1.11, 4.45, 0.76, 0.064, "silverSteel")


def wedge_wall(bottom, top, z, heights, material_name="monumentStone"):
    lower = [(x, y, z) for x, y in bottom]
    upper = [(x, y, z + h) for (x, y), h in zip(top, heights)]
    face(lower[::-1], material_name)
    face(upper, "shadowStone")
    for i in range(len(lower)):
        j = (i + 1) % len(lower)
        face((lower[i], lower[j], upper[j], upper[i]), material_name)


def nanjing_massacre_memorial():
    z = base(11.0, 8.6, "paving", "shadowStone")
    group("江东门·悼念广场")
    box(0, -2.46, z + 0.015, 9.35, 2.74, 0.033, "warmConcrete")
    for x in range(-8, 9):
        box(x * 0.535, -2.45, z + 0.049, 0.009, 2.71, 0.004, "ledgeStone")
    for j in range(6):
        box(0.04, -3.62 + j * 0.48, z + 0.050, 9.27, 0.010, 0.005, "ledgeStone")
    steps(1.88, -2.52, z + 0.036, 4.02, 2.00, 0.28, 11, "chalkStone")
    for x in (-0.18, 3.98):
        box(x, -1.59, z + 0.088, 0.10, 1.74, 0.10, "shadowStone")
        square_beam((x,-2.45,z+0.21), (x,-0.60,z+0.42), 0.033, 0.038, "shadowSteel")
    group("灰石纪念墙与史料陈列厅入口")
    wedge_wall([(-4.87,-0.83), (-0.47,-0.83),(-0.42,2.35),(-4.82,2.64)],
               [(-4.51,-0.70),(-0.58,-0.70),(-0.62,2.30),(-4.44,2.50)],
               z+0.22, [1.02,1.87,1.81,1.19])
    label = [(-4.42,-0.786,z+0.91),(-0.72,-0.786,z+0.91),
             (-0.72,-0.761,z+1.19),(-4.42,-0.761,z+1.19)]
    face(label,"carvedName",[(0,0),(1,0),(1,1),(0,1)])
    wedge_wall([(2.82,-0.56),(4.97,-0.26),(4.93,2.83),(2.63,2.47)],
               [(3.02,-0.49),(4.68,-0.18),(4.62,2.83),(2.73,2.45)],
               z+0.24,[1.56,1.80,1.66,1.49])
    box(1.19, 0.66, z + 0.24, 3.84, 2.73, 1.07, "darkBrick")
    curtain_wall(1.18, -0.727, z + 0.28, 3.58, 1.02, 12, 3, True)
    box(1.20, 0.48, z + 1.30, 4.12, 3.14, 0.17, "monumentStone")
    for x in (-0.47, 0.11, 2.29, 2.83):
        box(x, -0.87, z + 0.24, 0.085, 0.095, 1.07, "darkStone")
    group("石铺缓坡与窄绿篱")
    box(-2.65, -1.035, z + 0.057, 4.19, 0.27, 0.09, "shadowStone")
    for i in range(12):
        xx = -4.53 + i * 0.34
        box(xx, -1.06, z+0.145, 0.312, 0.248, 0.159, "pine")
    box(-2.73, 2.97, z + 0.013, 4.33, 1.46, 0.077, "grass")
    for i in range(6):
        tree(-4.30 + i*0.69, 3.10, z+0.085, 0.47+0.04*(i%3), 0)
    box(3.57, 3.08, z + 0.018, 2.19, 1.09, 0.050, "grass")


def birds_nest():
    z = base(11.7, 12.15, "paving", "shadowStone")
    group("体育场外围平台与广场")
    footprint = ellipse(40, 0, 0, 5.42, 5.76)
    footprint_inner = [(x * 0.969, y * 0.968) for x, y in footprint]
    floorplan(0, 0, z + 0.016, footprint, 0.14, "warmConcrete")
    floorplan(0, 0, z + 0.153, footprint_inner, 0.06, "chalkStone")
    for side in (-1, 1):
        for i in range(4):
            tree(side * (4.94 + (i%2)*0.19), -3.98 + (i//2)*0.77, z+0.045, 0.47, i+1)
    group("跑道、中央场地与红色看台")
    floorplan(0, 0, z+0.212, ellipse(40, 0, 0, 2.51, 3.02), 0.044, "trackRed")
    floorplan(0, 0, z+0.256, ellipse(40, 0, 0, 1.96, 2.39), 0.012, "fieldGreen")
    for factor in (0.87,0.94,0.988):
        poly = ellipse(36,0,0,2.51*factor,3.02*factor)
        for a, b in zip(poly, poly[1:] + poly[:1]):
            face(((*a,z+0.258),(*b,z+0.258),(b[0]*0.99,b[1]*0.99,z+0.258),
                  (a[0]*0.99,a[1]*0.99,z+0.258)), "whiteStone")
    for a, b in (((-1.53,-2.20),(1.53,-2.20)),((1.53,-2.20),(1.53,2.20)),
                 ((1.53,2.20),(-1.53,2.20)),((-1.53,2.20),(-1.53,-2.20)),((-1.53,0),(1.53,0))):
        square_beam((*a,z+0.272),(*b,z+0.272),0.027,0.009,"chalkStone")
    rings = [(2.52,3.03,0.27),(2.78,3.26,0.48),(2.98,3.43,0.75),(3.18,3.66,0.99),
        (3.20,3.69,1.10),(3.48,3.94,1.38),(3.63,4.09,1.67),(3.87,4.27,1.91),
        (4.16,4.58,2.04)]
    count = 44
    for row, ((ar,br,az),(cr,dr,bz)) in enumerate(zip(rings,rings[1:])):
        for sector in range(count):
            a = sector*2*pi/count
            b = (sector+1)*2*pi/count
            lift = lambda t: 0.105 * cos(2*t+0.27)
            face(((ar*cos(a),br*sin(a),z+az+lift(a)), (cr*cos(a),dr*sin(a),z+bz+lift(a)),
                  (cr*cos(b),dr*sin(b),z+bz+lift(b)), (ar*cos(b),br*sin(b),z+az+lift(b))),
                  "chalkStone" if sector%5==2 else ("darkRedSeats" if row%3==0 else "redSeats"))
    group("轮廓开敞的钢罩")
    rng = Random(2008)

    def outer(t, height, inset=0):
        r = 0.884 + 0.123*sin(height*pi/1.94) - inset
        saddle = -0.21*cos(2*t - 0.09)
        return (5.28*r*cos(t),5.71*r*sin(t),z+0.27+2.42*height+saddle*height)

    for j in range(25):
        angle = j * 2*pi/25 + 0.029
        twist = (0.29 + rng.uniform(0.0,0.13)) * (1 if j%2 else -1)
        prime = [outer(angle+twist*f, f, 0.015) for f in (0.0,0.30,0.63,1.0)]
        secondary = [outer(angle - twist*0.93*f + 0.155, f, 0.004) for f in (0.03,0.30,0.66,1.0)]
        square_ribbon(prime, 0.138, 0.167, ["silverSteel","brightSteel"])
        square_ribbon(secondary, 0.111, 0.128, ["brightSteel","shadowSteel"])
    rim_count = 46
    for fraction, height, thickness in ((0.0,1.0,0.095),(0.0,0.025,0.070),(0.015,0.69,0.052),(0.02,0.32,0.055)):
        points=[outer(i*2*pi/rim_count, height, fraction) for i in range(rim_count)]
        square_ribbon(points+[points[0]], thickness, thickness*0.92, ["shadowSteel","silverSteel"])
    group("顶棚桁架与椭圆露天开口")

    def cover(t, amount):
        outside = outer(t, 1.0, -0.003)
        r = 1.0 - amount
        inner = (3.13*cos(t),3.60*sin(t),z+2.43-0.17*cos(2*t-0.09))
        return (outside[0]*r+inner[0]*amount, outside[1]*r+inner[1]*amount,
                outside[2]*r+inner[2]*amount+0.21*sin(pi*amount))

    for j in range(26):
        a = j*2*pi/26 + 0.022
        theta = -0.26 if j%2 else 0.33
        chord = [cover(a+theta*step, step) for step in (0.0,0.30,0.68,1.0)]
        square_ribbon(chord, 0.108,0.102,["brightSteel","silverSteel"])
        path = [cover(a + 0.11 - theta*0.92*step, step) for step in (0.0,0.23,0.62,1.0)]
        square_ribbon(path, 0.081,0.073,["silverSteel","brightSteel"])
    for amount, thickness in ((0.72,0.076),(1.0,0.106)):
        perimeter=[cover(i*2*pi/rim_count,amount) for i in range(rim_count)]
        square_ribbon(perimeter+[perimeter[0]],thickness,thickness*1.05,["brightSteel","silverSteel"])


SCENES = {
    "china-science-museum": china_science_museum,
    "hubei-museum": hubei_museum,
    "hunan-museum": hunan_museum,
    "shanghai-museum-east": shanghai_museum_east,
    "nanjing-massacre-memorial": nanjing_massacre_memorial,
    "birds-nest": birds_nest,
}
