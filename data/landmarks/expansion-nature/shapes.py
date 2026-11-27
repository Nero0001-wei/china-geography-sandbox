"""Shared low-poly terrain operations. Blender XY is horizontal and -Y is front."""
from math import atan2, cos, exp, hypot, pi, sin, sqrt
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "workshop-c"))
from geometry import PARTS, box, cylinder, face, floorplan, group, hip, profile, sphere, steps

GROUND = 0.36


def base(top="grass", rim="soil", width=6.15, depth=4.25):
    """Model underside stays at zero and the real position is the tile centre."""
    group("剖面底座")
    def outline(w, d, z):
        a, b = w / 2, d / 2
        c = .17
        return [(x, y, z) for x, y in [(-a+c,-b),(a-c,-b),(a,-b+c),(a,b-c),
                                         (a-c,b),(-a+c,b),(-a,b-c),(-a,-b+c)]]
    rings = [outline(width-.21, depth-.21, 0), outline(width, depth, .10),
             outline(width, depth, .265), outline(width-.13, depth-.13, GROUND)]
    face(rings[0][::-1], "base")
    face(rings[-1], top)
    for low, high, material in zip(rings, rings[1:], ("base", rim, top)):
        for i in range(8):
            j = (i + 1) % 8
            face([low[i], low[j], high[j], high[i]], material)


def noise(x, y):
    return (.49 * sin(x * 3.1 + y * 2.7) + .32 * cos(x * 4.7 - y * 3.6)
            + .16 * sin(x * 10.8 + y * 7.2))


def peak(x, y, cx, cy, wx, wy, height, sharp=1):
    return height * exp(-(((x-cx)/wx)**2 + ((y-cy)/wy)**2)**sharp)


def surface(label, box_bounds, nx, ny, height, material, *, organic=True):
    """Triangulated heightfield with a deterministic stagger to break grid faceting."""
    group(label)
    x0, x1, y0, y1 = box_bounds
    dx, dy = (x1-x0)/nx, (y1-y0)/ny
    rng = Random(71)
    rows = []
    for j in range(ny + 1):
        row = []
        for i in range(nx + 1):
            x, y = x0+i*dx, y0+j*dy
            if organic and 0 < i < nx and 0 < j < ny:
                x += rng.uniform(-.3, .3)*dx
                y += rng.uniform(-.3, .3)*dy
            row.append((x, y, height(x,y)))
        rows.append(row)
    for q, r in zip(rows, rows[1:]):
        for a, b, c, d in zip(q, q[1:], r[1:], r):
            for tri in ((a,b,c), (a,c,d)):
                x, y, z = (sum(p[k] for p in tri)/3 for k in range(3))
                face(tri, material(x,y,z) if callable(material) else material)
    if box_bounds != (-2.97, 2.97, -2.04, 2.04):
        return
    # Close the cut faces where terrain extends to the perimeter of its base.
    # Low river and lake beds remain behind the water/soil lid.
    group("地形剖面")
    bounds = (rows[0], [row[-1] for row in rows],
              list(reversed(rows[-1])), [row[0] for row in reversed(rows)])
    for edge in bounds:
        for a, b in zip(edge,edge[1:]):
            if max(a[2],b[2]) <= GROUND:
                continue
            a=(a[0],a[1],max(GROUND-.005,a[2]))
            b=(b[0],b[1],max(GROUND-.005,b[2]))
            lo=(a[0],a[1],GROUND-.008)
            hi=(b[0],b[1],GROUND-.008)
            mat="cutSoil" if (a[2]+b[2])*.5>.61 else "soil"
            if label.startswith(("受剥蚀","库布齐","鸣沙山","黄河弯道")):
                mat="desertSoil"
            face([lo,hi,b,a],mat)


def stack(label, x, y, z, rings, material, n=12, seed=1):
    """Closed weathered stone volume defined by horizontal rings and an uneven crest."""
    group(label)
    rng = Random(seed)
    bias = [rng.uniform(.83, 1.17) for _ in range(n)]
    levels = []
    for h, rx, ry, dx, dy in rings:
        levels.append([
            (x+dx+rx*bias[j]*cos(2*pi*j/n), y+dy+ry*bias[j]*sin(2*pi*j/n),
             z+h+min(h,.25)*.27*sin(j*2.3+seed))
            for j in range(n)])
    face(levels[0][::-1], material if isinstance(material,str) else material(0,0))
    end = levels[-1]
    centre = tuple(sum(p[k] for p in end) / n for k in range(3))
    for j in range(n):
        face([end[j], end[(j+1)%n], centre], material if isinstance(material,str) else material(len(levels)-1,j))
    for i, (lo, hi) in enumerate(zip(levels, levels[1:])):
        for j in range(n):
            k = (j+1)%n
            mat = material if isinstance(material,str) else material(i,j)
            face([lo[j],lo[k],hi[k]], mat)
            face([lo[j],hi[k],hi[j]], mat)


def boulder(x, y, z, w, d, h, seed=4, mat=None, label="风化石块"):
    def stone(i,j):
        return ("rockDark", "granite", "granite", "cliff", "sandstone")[(i*2+j)%5]
    stack(label,x,y,z,[(0,w*.78,d*.83,0,0),(.20*h,w,d,.02,0),(.69*h,w*.74,d*.82,.04,0),
                       (h,w*.26,d*.31,.13,0)],mat or stone,n=8,seed=seed)


def conifer(x, y, z, h, radius, seed=1, *, snow=False):
    rng = Random(seed)
    group("针叶林")
    cylinder((x,y,z),(x+.01,y,z+h*.64),radius*.17,radius*.08,"timber",5)
    for j in range(3):
        low = z+h*(.16+j*.19)
        high = z+h*(.62+j*.19)
        rr = radius*(1-.23*j)
        material = "snow" if snow and j == 2 else ("pineDark" if j == 0 else rng.choice(("pine","pineLight","pine")))
        cylinder((x,y,low),(x+.015*j,y,high),rr,0,material,5)


def bush(x,y,z,r, seed=1, *, greens=("pine","leaf","grass")):
    rng = Random(seed)
    group("阔叶灌木")
    for i in range(2):
        rx = r*rng.uniform(.57,.90)
        sphere(x+(i-.5)*r*.9,y+r*rng.uniform(-.27,.27),z+rx*.38,rx,rx*.90,rx*.72,rng.choice(greens),6,3)


def forest(seed, bounds, count, height, test=lambda x,y:True, *, woodland="pine", min_size=.14, max_size=.37):
    x0,x1,y0,y1 = bounds
    rng=Random(seed)
    placed=0
    for i in range(count*14):
        x,y=rng.uniform(x0,x1),rng.uniform(y0,y1)
        if not test(x,y):
            continue
        h=rng.uniform(min_size,max_size)
        if woodland=="pine":
            conifer(x,y,height(x,y)-.022,h,h*rng.uniform(.21,.35),seed+i)
        else:
            bush(x,y,height(x,y)-.022,h*.53,seed+i)
        placed+=1
        if placed>=count:
            break


def ribbon(label, path, width, z, material, *, segments=44, bands=4):
    """Draw a continuous watercourse along y=-2.04…2.04 or any sampled path."""
    group(label)
    rows=[]
    for i in range(segments+1):
        t=i/segments
        x,y=path(t)
        before=path(max(0,t-.005))
        after=path(min(1,t+.005))
        tx,ty=after[0]-before[0],after[1]-before[1]
        length=hypot(tx,ty) or 1
        nx,ny=-ty/length,tx/length
        current=width(t) if callable(width) else width
        rows.append([(x+current*(j/bands-.5)*nx,y+current*(j/bands-.5)*ny,z) for j in range(bands+1)])
    for i,(lo,hi) in enumerate(zip(rows,rows[1:])):
        for j in range(bands):
            m=material(i,j) if callable(material) else material
            face([lo[j],hi[j],hi[j+1],lo[j+1]],m)


def currents(seed, bounds, amount, plane, mask=lambda x,y:True, *, material="ripple", along=(1,0)):
    """Short tapered strokes on still water; masked at shore."""
    group("细水纹")
    rng=Random(seed)
    x0,x1,y0,y1=bounds
    dx,dy=along
    nx,ny=-dy,dx
    drawn=0
    for _ in range(amount*10):
        x,y=rng.uniform(x0,x1),rng.uniform(y0,y1)
        l=rng.uniform(.04,.26)
        if not all(mask(x+s*dx*l,y+s*dy*l) for s in (-1,0,1)):
            continue
        w=rng.uniform(.002,.011)
        face([(x-l*dx,y-l*dy,plane),(x+nx*w,y+ny*w,plane),
              (x+l*dx,y+l*dy,plane),(x-nx*w,y-ny*w,plane)],material)
        drawn+=1
        if drawn>=amount:
            break


def falling_water(label, x, y, z, width, drop, seed=1, *, arch=.30, folds=24):
    group(label)
    rng=Random(seed)
    flows=[]
    for j in range(folds+1):
        u=j/folds
        q=2*u-1
        offset_drop=rng.uniform(-.05,.065)*drop
        lipy=y+arch*(q*q)+rng.uniform(-.028,.028)
        flows.append([(x+q*width*.50,lipy,z+drop+offset_drop),
                      (x+q*width*.48,lipy-.035,z+drop*.90+offset_drop*.40),
                      (x+q*width*.47,lipy-.11,z+drop*.57),
                      (x+q*width*.50,lipy-.245,z+drop*.15),
                      (x+q*width*.53,lipy-.35,z)])
    for j,(left,right) in enumerate(zip(flows,flows[1:])):
        for k in range(4):
            mat=("foam","fall","fall","waterLight","foam")[(j*3+k)%5]
            face([left[k],left[k+1],right[k+1],right[k]],mat)
    for i in range(24):
        s=rng.uniform(-.57,.57)*width
        py=y-.40+rng.uniform(-.32,.12)
        w=rng.uniform(.03,.12)
        face([(x+s-w,py,z+.010),(x+s,py-w*.25,z+.013),(x+s+w,py,z+.014),
              (x+s+w*.15,py+w*.19,z+.012)],"foam")


def hut(x, y, z, w, d, *, wall="white", roof="roof", story=.22, tiles=.22):
    group("景区建筑")
    box(x,y,z,w,d,story,wall)
    hip(x,y,z+story,w*1.22,d*1.31,tiles,roof,trim=roof,lift=.15)
    box(x,y-d/2-.008,z+.016,w*.235,.022,story*.70,"timber")
    for s in (-1,1):
        box(x+s*w*.30,y-d/2-.009,z+story*.32,w*.19,.02,story*.32,"dark")


def plank_line(label, points, r, material, n=6):
    group(label)
    for a,b in zip(points,points[1:]):
        cylinder(a,b,r,r,material,n)


def tree_shade(x,y,z,r,seed=1):
    """Asymmetrical broadleaf crown with a trunk and a few connected main boughs."""
    rng=Random(seed)
    group("岸边阔叶树")
    top=(x+.035,y,z+r*.95)
    cylinder((x,y,z),top,r*.10,r*.055,"timber",5)
    for j in range(4):
        t=2*pi*j/4+.3
        co=(x+cos(t)*r*.38,y+sin(t)*r*.40,z+r*(1.12+rng.uniform(-.13,.18)))
        cylinder((x,y,z+r*.57),co,r*.052,r*.025,"timber",4)
        sphere(*co,r*.50,r*.44,r*.37,("leaf","pine","pineLight","grass")[j],7,3)


def palm(x,y,z,h,seed):
    """A coastal coconut palm with a curved stem and ribbed, pendant fronds."""
    group("海岸椰林")
    rng=Random(seed)
    skew=rng.uniform(-.19,.19)*h
    points=[(x+skew*(i/5)**1.4,y+.07*h*(i/5)**2,z+h*i/5) for i in range(6)]
    for i,(a,b) in enumerate(zip(points,points[1:])):
        cylinder(a,b,.046*h*(1-.10*i),.046*h*(.90-.105*i),"timber",7)
    x,y,z=points[-1]
    for j in range(9):
        f=2*pi*j/9+rng.uniform(-.19,.19)
        r=rng.uniform(.33,.59)*h
        a=(x,y,z)
        mid=(x+cos(f)*r*.48,y+sin(f)*r*.48,z+h*.11)
        end=(x+cos(f)*r,y+sin(f)*r,z-h*.17)
        tx,ty=-sin(f)*r*.125,cos(f)*r*.125
        face([a,(mid[0]+tx,mid[1]+ty,mid[2]-.023*h),end,mid],"pine")
        face([a,mid,end,(mid[0]-tx,mid[1]-ty,mid[2]-.038*h)],"leaf")


def project_strokes(source,x,z,size,strokes):
    """Lay short mineral pigment strips directly over a rock's surveyed-facing surface."""
    points=[p for polygon,_,_ in source for p in polygon]
    low_x, high_x=min(p[0] for p in points),max(p[0] for p in points)
    low_z, high_z=min(p[2] for p in points),max(p[2] for p in points)
    x,z=max(low_x+size,min(high_x-size,x)),max(low_z+size,min(high_z-size,z))
    def front(px,pz):
        depths=[]
        for polygon,_,_ in source:
            anchor=polygon[0]
            for b,c in zip(polygon[1:],polygon[2:]):
                ux,uz=b[0]-anchor[0],b[2]-anchor[2]
                vx,vz=c[0]-anchor[0],c[2]-anchor[2]
                determinant=ux*vz-vx*uz
                if abs(determinant)<1e-8:
                    continue
                dx,dz=px-anchor[0],pz-anchor[2]
                u,v=(dx*vz-dz*vx)/determinant,(ux*dz-uz*dx)/determinant
                if min(u,v,1-u-v)>=-1e-6:
                    depths.append(anchor[1]+u*(b[1]-anchor[1])+v*(c[1]-anchor[1]))
        return (px,min(depths)-.007,pz) if depths else None
    group("花岗岩朱红题刻")
    for stroke in strokes:
        for a,b in zip(stroke,stroke[1:]):
            ax,az=x+size*a[0],z+size*a[1]
            bx,bz=x+size*b[0],z+size*b[1]
            run=hypot(bx-ax,bz-az)
            if run<.001:
                continue
            dx,dz=-(bz-az)*size*.039/run,(bx-ax)*size*.039/run
            count=max(2,int(run/.022))
            ribs=[]
            for i in range(count+1):
                t=i/count
                px,pz=ax+t*(bx-ax),az+t*(bz-az)
                ribs.append((front(px+dx,pz+dz),front(px-dx,pz-dz)))
            for (l,r),(n,m) in zip(ribs,ribs[1:]):
                if all((l,r,n,m)):
                    face([l,r,m,n],"cinnabar")
