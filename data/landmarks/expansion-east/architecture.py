"""Shared architectural parts, in Blender coordinates with the public face towards -Y."""

from math import cos, pi, sin
from random import Random

from geometry import box, cylinder, face, floorplan, group, hip, shaft, sphere, window


def radial(x, y, z, levels, mat, sides=24, phase=0, aspect=1, caps=True, roof_uv=False):
    """Continuous polygonal profile with optional material changes by band."""
    loops = [[(x + radius * cos(a), y + radius * sin(a) * aspect, z + h)
              for a in (phase + 2 * pi * i / sides for i in range(sides))]
             for h, radius in (level[:2] for level in levels)]
    if caps:
        face(loops[0][::-1], mat)
        face(loops[-1], mat)
    for i, (lo, hi) in enumerate(zip(loops, loops[1:])):
        band = levels[i + 1][2] if len(levels[i + 1]) > 2 else mat
        for j in range(sides):
            k = (j + 1) % sides
            uv = None
            if roof_uv:
                left, right = j*.19, (j+1)*.19
                below, above = levels[i][0], levels[i+1][0]
                uv = [(left,below),(right,below),(right,above),(left,above)]
            face([lo[j], lo[k], hi[k], hi[j]], band, uv)


def cut_base(w, d, material="granite", top="ashlar", h=.25, x=0, y=0):
    group("地物基座")
    r = min(w, d) * .10
    outline = [(-w/2+r, -d/2), (w/2-r, -d/2), (w/2, -d/2+r), (w/2, d/2-r),
               (w/2-r, d/2), (-w/2+r, d/2), (-w/2, d/2-r), (-w/2, -d/2+r)]
    floorplan(x, y, 0, outline, h * .62, material)
    floorplan(x, y, h * .62, [(a * .994, b * .994) for a, b in outline], h * .38, top)
    return h


def rectangular_rail(x1, x2, y, z, height=.25, div=12, mat="marble"):
    box((x1+x2)/2, y, z+height*.8, x2-x1, .079, height*.16, mat)
    box((x1+x2)/2, y, z+.025, x2-x1, .066, height*.15, mat)
    for i in range(div + 1):
        box(x1 + (x2-x1) * i / div, y, z, .062, .087, height, mat)


def curve_rail(cx, cy, z, r, start, end, height, div, mat="marble"):
    for i in range(div + 1):
        a = start + (end - start) * i / div
        x, y = cx + cos(a) * r, cy + sin(a) * r
        shaft(x, y, z, .06, height, mat, 5)
        if i:
            cylinder((px, py, z+height*.84), (x, y, z+height*.84), .042, .042, mat, 4)
            cylinder((px, py, z+height*.38), (x, y, z+height*.38), .022, .022, mat, 4)
        px, py = x, y


def arch_bridge(x, y, z, width, span, rise, mat="granite", deck="ashlar", rails=True, segments=12):
    """Single arch with an open waterway below the stone ring."""
    def point(t, side, upper):
        weight = sin(pi * t) ** .85
        return (x + side * width/2, y + (t-.5) * span, z + rise * weight + (.20 if upper else 0))
    for i in range(segments):
        a, b = i/segments, (i+1)/segments
        f0, f1, f2, f3 = point(a,-1,False), point(b,-1,False), point(b,-1,True), point(a,-1,True)
        b0, b1, b2, b3 = point(a,1,False), point(b,1,False), point(b,1,True), point(a,1,True)
        face([f0, f3, f2, f1], mat)
        face([b0, b1, b2, b3], mat)
        face([f3, b3, b2, f2], deck)
        face([f0, f1, b1, b0], mat)
        if rails:
            for side in (-1, 1):
                P, Q = point(a, side, True), point(b, side, True)
                if i % 2 == 0:
                    shaft(P[0], P[1], P[2], .05, .23, mat, 5)
                cylinder((P[0], P[1], P[2]+.21), (Q[0], Q[1], Q[2]+.21), .032, .032, mat, 4)
    for y0 in (y-span/2, y+span/2):
        box(x, y0, max(0, z-.12), width+.09, .23, .33, mat)


def hall(x, y, z, w, d, h, bays=5, wall="rouge", column="rouge", tile="greyTile",
         trim="beam", base="granite", roof_height=None, upper_eave=False, panels=True,
         platform=True, plaque=True):
    """Timber hall with a stepped stylobate and an independently modeled verandah."""
    if platform:
        box(x, y, z, w*1.10, d*1.16, .16, base)
        z += .16
    core_w, core_d = w*.82, d*.68
    box(x, y+.055*d, z, core_w, core_d, h, wall)
    fy = y-d*.46
    for i in range(bays+1):
        xx = x+w*.46*(2*i/bays-1)
        for yy in (fy, y+d*.46):
            shaft(xx, yy, z, max(.048, w*.0135), h+.035, column, 7)
            box(xx, yy, z, w*.029, w*.029, .058, base)
        if i == bays or not panels:
            continue
        mid = xx + w*.46/bays
        front = y+.055*d-core_d*.5-.01
        if bays % 2 == 1 and i == bays//2:
            window(mid, front, z+.06, w*.72/bays, h*.79, trim, "dark")
        else:
            window(mid, front, z+h*.29, w*.68/bays, h*.48, trim, "dark")
            box(mid, front-.064, z+h*.29, w*.025, .025, h*.48, column)
    for yy in (fy, y+d*.46):
        box(x, yy, z+h*.90, w*.96, .10, h*.10, trim)
    if plaque:
        box(x, fy-.067, z+h*.78, w*.19, .080, h*.14, "gold")
        box(x, fy-.116, z+h*.806, w*.16, .025, h*.09, "dark")
    rz = z+h
    rh = roof_height if roof_height is not None else h*.63
    hip(x, y, rz, w*1.16, d*1.20, rh, tile, trim, .20)
    if upper_eave:
        box(x, y, rz+rh*.32, w*.70, d*.63, rh*.36, trim)
        hip(x, y, rz+rh*.57, w*.86, d*.95, rh*.79, tile, trim, .20)
        return rz+rh*1.36
    return rz+rh


def octagon(x, y, z, radius, h, roof_h, wall="rouge", tile="goldTile", eave="greenTile",
            columns=True, tip="gold", base="marble"):
    phase = pi/8
    radial(x,y,z,[(0,radius*1.21),(.06,radius*1.21),(.14,radius*1.13)],base,8,phase)
    radial(x,y,z+.14,[(0,radius*.82),(h,radius*.82)],wall,8,phase)
    for i in range(8):
        a = phase + i*pi/4
        if columns:
            shaft(x+radius*cos(a),y+radius*sin(a),z+.14,.065,h,"rouge",6)
        mid = a + pi/8
        rx, ry = cos(mid), sin(mid)
        p, q = (rx,ry), (-ry,rx)
        rr = radius*.82*cos(pi/8)+.008
        cz = z+.14+h*.24
        face([(x+rx*rr-q[0]*radius*.20,y+ry*rr-q[1]*radius*.20,cz),
              (x+rx*rr+q[0]*radius*.20,y+ry*rr+q[1]*radius*.20,cz),
              (x+rx*rr+q[0]*radius*.20,y+ry*rr+q[1]*radius*.20,cz+h*.55),
              (x+rx*rr-q[0]*radius*.20,y+ry*rr-q[1]*radius*.20,cz+h*.55)],"dark")
    roof_z = z+h+.14
    radial(x,y,roof_z,[(-.035,radius*1.19),(0,radius*1.26),(.09*roof_h,radius*1.27),
                       (.24*roof_h,radius*.99,tile),(.54*roof_h,radius*.53,tile),(roof_h,.07,tile)],
           eave,8,phase)
    shaft(x,y,roof_z+roof_h*.92,.077,roof_h*.29,tip,8,.037)
    return roof_z+roof_h


def tree(x, y, z, scale=1, seed=0, cypress=False):
    rng = Random(seed)
    shaft(x,y,z,.063*scale,.80*scale,"beam",6,.037*scale)
    if cypress:
        for j in range(3):
            sphere(x,y,z+scale*(.57+j*.24),scale*(.39-j*.064),scale*(.36-j*.057),
                   scale*(.43-j*.022),"pine" if j != 1 else "grass",8,4)
    else:
        for j in range(5):
            a = pi*j*.77
            r = rng.uniform(.15,.42)*scale
            sphere(x+cos(a)*r, y+sin(a)*r, z+scale*(.73+rng.uniform(.02,.31)), .40*scale,
                   .34*scale,.33*scale,"pine" if j<3 else "grass",7,4)


def gray_house(x, y, z, width, depth, height, floors=1, wall="whitewash", mirrored=False):
    """Narrow wall-and-timber shop with a distinct ridge and gable ends."""
    box(x,y,z,width,depth,height,wall)
    roof_z=z+height
    hip(x,y,roof_z,width+.24,depth+.32,height*.39,"greyTile","timber",.15)
    fy=y-depth/2-.009 if not mirrored else y+depth/2+.008
    for i in range(floors):
        h=height/floors
        box(x,fy,z+i*h+.03,width,.049,.062,"timber")
        for k in range(3):
            xx=x+(k-1)*width*.285
            if not mirrored:
                window(xx,fy,z+i*h+h*.16,width*.19,h*.68,"timber","dark")
            else:
                box(xx,fy,z+i*h+h*.23,width*.14,.045,h*.53,"dark")
    for xx in (x-width*.45,x+width*.45):
        box(xx,fy,z,width*.065,.09,height,"beam")
