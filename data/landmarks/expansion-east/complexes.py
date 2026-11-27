"""Temple compounds, towers, stone carvings and desert fortifications."""

from math import cos, exp, pi, sin
from random import Random

from geometry import annular_arch, box, cylinder, face, floorplan, group, hip, profile, shaft, sphere, steps, window
from architecture import arch_bridge, cut_base, hall, radial, rectangular_rail, tree
from monuments import rock_wall


def putuo():
    z=cut_base(10.85,8.75,"grey-stone","ashlar")
    group("海印池·石栏、池中亭与圆拱桥")
    floorplan(0,-1.42,z,[(-4.72,-2.17),(4.32,-2.17),(5.08,-1.5),(5.08,.78),
              (4.45,1.48),(-4.70,1.48),(-5.07,.88),(-5.07,-1.69)],.042,"water")
    for x in (-3.55,3.56):
        box(x, -3.46,z,.85,1.18,.17,"granite")
    arch_bridge(0,-1.54,z+.02,1.04,4.28,.77,"graniteLight")
    for side in (-1,1):
        rectangular_rail(side*2.75-1.68,side*2.75+1.68,-3.55,z+.05,.26,9,"granite")
    for i,(x,y) in enumerate(((-3.5,-.99),(-2.1,-1.24),(2.5,-2.22),(3.4,-1.77),(-2.6,-1.7),(3.6,-2.55))):
        sphere(x,y,z+.052,.29,.23,.025,"pine",8,4)
        if i%2==0:
            sphere(x+.019,y,z+.077,.087,.083,.067,"lilac",7,5)
    group("普济禅寺·天王殿与殿前牌楼")
    hall(0,2.0,z,6.39,2.96,1.48,7,"ochre","rouge","goldTile",trim="plum",upper_eave=True,roof_height=.86)
    for side in (-1,1):
        box(side*4.15,.71,z,2.2,.34,1.03,"ochre")
        box(side*4.15,.71,z+.99,2.24,.51,.12,"greyTile")
        tree(side*4.33,2.89,z,.78,392+side,True)


def tengwang():
    z=cut_base(12.9,8.0,"grey-stone","granite")
    group("赣江高台·汉白玉栏与中轴")
    profile(0,.20,z,[(0,10.94,4.9),(1.22,10.45,4.58),(1.36,10.82,4.71)],"grey-stone")
    for side in (-1,1):
        for xoff in (1.8,3.2,4.6):
            box(side*xoff,-2.11,z+.43,.36,.12,.54,"dark")
        rectangular_rail(side*3.75-1.43,side*3.75+1.43,-2.15,z+1.36,.22,9)
    steps(0,-3.92,z,2.28,2.07,1.36,12,"graniteLight")
    group("主阁·绿琉璃重檐和外回廊")
    for idx,(zz,w,d,h) in enumerate(((1.36,6.65,3.98,1.24),(3.00,5.48,3.38,1.03),(4.36,4.35,2.70,1.17))):
        hall(0,.42,z+zz,w,d,h,7 if idx==0 else 5,"plum","rouge","greenTile",
                  trim="teal",base="granite",roof_height=.67 if idx<2 else 1.0,upper_eave=idx==2)
        rectangular_rail(-w*.46,w*.46,.42-d*.54,z+zz+.17,.27,12,"rouge")
    for side in (-1,1):
        hall(side*4.18,1.44,z+1.36,2.34,1.8,.93,3,"rouge","rouge","greenTile",roof_height=.60)
        hip(side*3.44,-.23,z+2.66,1.96,2.0,.44,"greenTile","teal")
    group("江畔草坡")
    box(0,3.48,z+.035,12.3,.76,.036,"water")


def qufu():
    z=cut_base(12.35,8.65,"grey-stone","ashlar")
    group("大成殿·石基与龙阶")
    for n in range(2):
        profile(0,.77,z+n*.32,[(0,10.1-n*.66,5.8-n*.50),(.30,9.87-n*.66,5.55-n*.50)],"marble")
    steps(0,-3.90,z,3.6,2.41,.64,9,"marble")
    for s in (-1,1):
        rectangular_rail(s*3.17-1.25,s*3.17+1.25,-2.0,z+.62,.27,7)
    group("大成殿·黄色琉璃瓦重檐")
    hall(0,.79,z+.61,8.96,4.72,1.98,9,"plum","graniteLight","goldTile","teal",
         upper_eave=True,roof_height=1.10,platform=False)
    group("十根浮雕蟠龙檐柱")
    for i in range(10):
        x=(i-4.5)*.922
        y=-1.411
        for j in range(9):
            k=j+1
            cylinder((x+.129*cos(j*.84),y+.129*sin(j*.84),z+.74+j*.196),
                     (x+.129*cos(k*.84),y+.129*sin(k*.84),z+.74+k*.196),.039,.037,"granite",5)
        box(x,y,z+.61,.265,.25,.11,"marble")
    for side in (-1,1):
        tree(side*5.38,2.72,z,1.32,616+side,True)


def stone_peak(radii, z0, height, seed=0):
    rng=Random(seed)
    n=29
    ridges=[rng.uniform(.89,1.10) for _ in range(n)]
    loops=[]
    for k,(a,b,shift) in enumerate(((1,1,-.18),(.96,.86,-.05),(.76,.73,-.16),
                                 (.60,.62,.08),(.51,.51,.43),(.41,.43,.28),(.34,.32,.18))):
        h=k/6*height
        loops.append([(cos(i*2*pi/n)*radii[0]*a*ridges[i]+shift,
                       sin(i*2*pi/n)*radii[1]*b*ridges[i]+.13*k/2, z0+h+(rng.uniform(-.20,.20) if k not in (0,6) else 0))
                      for i in range(n)])
    face(loops[0][::-1],"rock")
    face(loops[-1],"scree")
    for k,(low,high) in enumerate(zip(loops,loops[1:])):
        for i in range(n):
            j=(i+1)%n
            m="scree" if i%7<4 else "clayDark"
            if (k+i)%11==0:
                m="pine"
            face([low[i], low[j],high[j]],m)
            face([low[i], high[j],high[i]],m)


def wudang():
    z=cut_base(10.05,8.06,"clayDark","scree")
    group("天柱峰·断层岩壁")
    stone_peak((4.79,3.9),z,4.94,193)
    group("紫金城·顶峰围墙与登顶石阶")
    x,y=.19,.49
    radial(x,y,z+4.92,[(0,1.71),(.31,1.57),(.40,1.57)],"grey-stone",16)
    for i in range(14):
        a=i*2*pi/14
        box(x+1.51*cos(a),y+1.51*sin(a),z+5.30,.31,.24,.27,"grey-stone")
    for (x0,y0,d,h,zz) in ((.63,-3.01,1.55,1.03,.40),
                            (1.03,-2.3,1.1,1.63,1.33),(.50,-1.55,.85,1.25,2.98),
                            (.24,-1.24,.77,1.11,4.00)):
        steps(x0,y0,z+zz,.49,d,h,8,"granite")
    group("金顶·鎏金铜殿")
    hall(.19,.49,z+5.34,1.84,1.39,.79,3,"gold","gold","goldTile","gold",base="marble",
         upper_eave=True,roof_height=.54)
    for i,(x1,y1,zz) in enumerate(((2.52,.12,2.57),(-2.82,.2,2.49),(2.94,1.00,2.07),
                                    (-1.98,1.77,3.46),(1.28,1.97,3.37),(-3.09,-1.27,1.21))):
        tree(x1,y1,z+zz,.61,i+10,True)


def helmet(x,y,z,w,d,h):
    """Bent hip profile for the stepped, up-curved helmet-roof outline."""
    ring_specs = [(0,1,1),(.06,.995,.99),(.16,.84,.84),(.34,.73,.72),
                  (.62,.68,.61),(.82,.52,.41),(.95,.31,.19),(1,.19,.076)]
    def ring(level, sx, sy):
        pts=[]
        for (a,b),(c,e) in zip(((-1,-1),(1,-1),(1,1),(-1,1)),((1,-1),(1,1),(-1,1),(-1,-1))):
            for j in range(8):
                t=j/8
                u,v=a+(c-a)*t,b+(e-b)*t
                ridge=(1-t*2 if t<.5 else t*2-1)**3
                pts.append((x+u*w*.5*sx,y+v*d*.5*sy,z+h*(level+ridge*.18*(1-level))))
        return pts
    rings=[ring(*r) for r in ring_specs]
    face(rings[0][::-1],"beam")
    face(rings[-1],"goldTile")
    for low,high in zip(rings,rings[1:]):
        for i in range(len(low)):
            j=(i+1)%len(low)
            face([low[i],low[j],high[j],high[i]],"goldTile")
    for s in (-1,1):
        for t in (-1,1):
            cylinder((x+s*w*.485,y+t*d*.48,z+.11*h),(x+s*w*.55,y+t*d*.54,z+.27*h),.044,.019,"gold",5)


def yueyang():
    z=cut_base(9.25,7.3,"grey-stone","ashlar")
    group("洞庭湖岸及巴陵城台")
    box(0,3.15,z,8.7,.82,.09,"water")
    box(0,-.05,z,7.84,5.74,.43,"grey-stone")
    for i in range(9):
        box((i-4)*.79,2.76,z+.42,.40,.31,.26,"grey-stone")
    steps(0,-3.33,z,1.68,1.33,.43,8,"marble")
    for n,(zz,w,d,h) in enumerate(((.43,5.73,3.84,1.17),(2.09,5.08,3.28,1.09),(3.56,3.97,2.62,1.06))):
        group(f"岳阳楼·第{n+1}层如意斗拱")
        base=z+zz
        box(0,.32,base,w*.91,d*.96,.11,"rouge")
        box(0,.35,base+.10,w*.69,d*.70,h-.09,"rouge")
        for y in (.35-d*.45,.35+d*.45):
            for i in range(6):
                xx=(i-2.5)*w*.176
                shaft(xx,y,base+.05,.081,h,"rouge",7)
                box(xx,y,base+h-.15,.23,.145,.115,"teal")
            rectangular_rail(-w*.45,w*.45,y,base+.12,.25,11,"rouge")
        for x in (-w*.48,w*.48):
            for yy in (-.12, .80):
                shaft(x,yy,base+.07,.077,h,"rouge",7)
        for i in range(4):
            window((i-1.5)*w*.161,.35-d*.36,base+.31,w*.108,h*.53,"timber","dark")
        helmet(0,.35,base+h,w*1.19,d*1.18,.67 if n<2 else 1.10)
    box(0,-.91,z+4.18,1.17,.095,.28,"gold")
    box(0,-.968,z+4.215,1.01,.035,.18,"dark")


def dazu():
    z=cut_base(12.8,5.55,"scree","graniteLight")
    group("宝顶山大佛湾·龛壁与石层")
    rock_wall(12.25,4.23,4.6,z,"clayLight",72,lambda x,t:1.13*exp(-((x-1)/4.8)**6)*(1-.88*t**5))
    box(.59,-.83,z+.69,10.5,.94,.63,"rock")
    group("释迦涅槃圣迹·卧佛浮雕")
    sphere(2.12,-.88,z+1.61,3.18,.53,.54,"graniteLight",25,10)
    sphere(-.31,-.97,z+1.82,.97,.54,.52,"graniteLight",20,9)
    sphere(-1.20,-1.01,z+1.89,.64,.43,.47,"graniteLight",20,11)
    sphere(-1.63,-1.04,z+1.95,.33,.35,.40,"clayDark",16,9)
    sphere(-1.13,-1.40,z+1.96,.105,.085,.043,"granite",9,4)
    sphere(-1.02,-1.42,z+2.045,.106,.09,.081,"graniteLight",10,6)
    sphere(-.92,-1.42,z+1.92,.085,.05,.034,"granite",9,4)
    for i in range(6):
        cylinder((.36+i*.36,-1.02,z+2.04),(1.12+i*.56,-1.37,z+1.38),.073,.022,"granite",7)
    group("龛前胁侍与上方众像")
    for i in range(11):
        x=-5.3+i*.90
        h=.77+.16*sin(i*2.29)
        box(x,-.38,z+2.19,.48,.37,.12,"clayDark")
        profile(x,-.46,z+2.32,[(0,.41,.28),(.30*h,.37,.27),(.64*h,.30,.24)],"graniteLight")
        sphere(x,-.47,z+2.36+.74*h,.18,.157,.19,"graniteLight",10,6)
        sphere(x,-.456,z+2.40+.85*h,.155,.14,.11,"granite",8,5)
        for dx in (-.17,.17):
            cylinder((x+dx,-.49,z+2.32+.63*h),(x+.77*dx,-.61,z+2.32+.26*h),
                     .060,.039,"granite",6)
    steps(-4.4,-2.58,z,1.05,1.66,.66,9,"granite")


def jiayuguan():
    z=cut_base(13.55,8.36,"loessDark","sand")
    group("明代关城·两重夯土与马道")
    for y in (-1.83,1.81):
        for side in (-1,1):
            profile(side*3.72,y,z,[(0,5.82,1.19),(1.44,5.46,1.02),(1.59,5.44,1.03)],"loess")
            for i in range(6):
                box(side*(1.49+i*.84),y-.43,z+1.58,.47,.27,.30,"loessDark")
        annular_arch(0,y,z+.62,.59,.17,1.14,"loessDark",13)
        for side in (-1,1):
            box(side*.82,y,z,.48,1.10,1.47,"loess")
        box(0,y,z+1.34,2.29,1.17,.22,"loess")
    for side in (-1,1):
        box(side*6.18,.02,z,.78,4.63,1.45,"loess")
        steps(side*4.99,-2.93,z,1.11,3.1,1.54,12,"loessDark")
    group("光化楼、柔远楼与外关")
    base=z+1.64
    for row,(x,y,w,d) in enumerate(((0,-1.72,4.17,1.78),(0,1.82,3.56,1.68),(4.82,1.81,1.50,1.38))):
        levels=3 if row<2 else 1
        for i in range(levels):
            f=1-i*.158
            hall(x,y,base+i*1.04,w*f,d*f,.68 if i<2 else .85,5 if row<2 else 3,
                 "loessDark","timber","greyTile","rouge",roof_height=.48,platform=i==0,plaque=i==0)


def western_xia():
    z=cut_base(10.35,9.04,"loessDark","sand")
    group("三号陵·现存八角密檐夯土陵塔")
    rng=Random(24)
    n=32
    levels=[(0,2.80),(.24,2.69),(.53,2.33),(.72,2.27),(.85,2.40),
            (1.16,2.17),(1.33,2.10),(1.53,2.26),(1.74,1.94),(1.94,1.88),
            (2.12,2.05),(2.32,1.78),(2.52,1.65),(2.73,1.74),(2.94,1.49),
            (3.18,1.34),(3.30,1.41),(3.61,1.05),(3.85,.78),(4.12,.59),(4.23,.48)]
    jitter=[rng.uniform(.924,1.06) for _ in range(n)]
    rings=[]
    for k,(h,r) in enumerate(levels):
        rings.append([(r*cos(2*pi*i/n)*jitter[i]+h*.037,
                       1.1+r*sin(2*pi*i/n)*jitter[i],z+h+(rng.uniform(-.07,.07) if k else 0))
                      for i in range(n)])
    face(rings[0][::-1],"loess")
    face(rings[-1],"loess")
    for k,(low, high) in enumerate(zip(rings,rings[1:])):
        for i in range(n):
            j=(i+1)%n
            mat="loessDark" if k in (3,6,9,12,15) else "loess"
            face([low[i],low[j],high[j],high[i]],mat)
    group("陵园·残垣和献殿遗址")
    for side in (-1,1):
        for i in range(9):
            yy=(i-4)*.88
            h=(.39+.12*sin(i*1.63))
            profile(side*3.74,yy,z,[(0,.57,.86),(h,.47,.83)],"loessDark")
        for i in range(4):
            xx=side*(2.09+i*.43)
            profile(xx,-3.3,z,[(0,.47,.41),(.21+.22*sin(i+1)**2,.41,.34)],"loess")
        sphere(side*3.73,-3.36,z+.16,.64,.62,.24,"loess",10,6)
        profile(side*1.23,-2.49,z,[(0,.75,.83),(.32,.69,.72),(.45,.51,.62)],"loessDark")
    box(0,-2.67,z+.004,.68,2.27,.025,"loess")


def a_ma():
    z=cut_base(10.1,8.02,"grey-stone","ashlar")
    group("妈阁庙前地·海滨山脚")
    profile(1.56,1.44,z,[(0,6.85,5.30),(.50,6.52,5.22),(1.43,5.92,4.33),
                           (2.23,4.83,3.31)],"rock")
    box(-1.82,-1.37,z,5.12,3.98,.13,"granite")
    for i in range(8):
        box(-1.89,-2.99+i*.40,z+.131,4.67,.019,.016,"grey-stone")
    group("石牌坊·花岗岩柱脚与曲脊")
    for side in (-1,1):
        x=-1.05+side*.69
        box(x,-.90,z+.13,.37,.45,.32,"granite")
        shaft(x,-.90,z+.44,.126,1.39,"graniteLight",8,.105)
        sphere(x,-1.05,z+.54,.19,.14,.23,"granite",9,5)
    box(-1.05,-.90,z+1.78,1.65,.31,.21,"graniteLight")
    hip(-1.05,-.90,z+1.99,2.34,1.13,.54,"greenTile","grey-stone",.27)
    for x in (-1.91,-.19):
        shaft(x,-.90,z+1.96,.062,.30,"grey-stone",8,.025)
    group("院落与石阶·沿坡递升的小殿")
    hall(1.59,1.60,z+2.13,3.45,2.14,1.00,5,"ochre","rouge","greenTile","rouge",roof_height=.69)
    hall(-2.21,1.68,z+.47,2.22,1.52,.79,3,"ochre","rouge","greenTile",roof_height=.52)
    for (x,y,w,d,zz,h) in ((.57,-1.19,.98,1.25,.11,.59),(1.54,-.45,1.05,1.27,.69,.75),
                           (2.92,.25,.71,1.31,1.42,.74)):
        steps(x,y,z+zz,w,d,h,10,"granite")
    for i,(xx,y,zz) in enumerate(((3.96,1.39,1.3),(3.30,2.95,2.16),(-2.7,2.9,.64),(.9,2.93,2.13))):
        tree(xx,y,z+zz,.85,i+20,False)
