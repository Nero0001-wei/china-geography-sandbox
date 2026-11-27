"""Garden fragments, canal streets and inhabited courtyard buildings."""

from math import cos, pi, sin

from geometry import annular_arch, box, cylinder, face, floorplan, group, hip, profile, shaft, sphere, steps
from architecture import arch_bridge, cut_base, gray_house, hall, octagon, radial, rectangular_rail, tree
from complexes import stone_peak


def summer_palace():
    z=cut_base(11.75,9.2,"grey-stone","grass")
    group("万寿山·湖畔山脚与崖台")
    stone_peak((5.5,4.06),z,2.39,73)
    box(0,-4.02,z,10.4,.82,.068,"water")
    for i in range(3):
        w=9.6-i*1.42
        profile(0,-1.06+i*.44,z+.23+i*.45,[(0,w,3.7-i*.39),(.51,w-.22,3.56-i*.39)],"grey-stone")
        for side in (-1,1):
            rectangular_rail(side*w*.30-w*.14,side*w*.30+w*.14,-2.81+i*.65,z+.66+i*.45,.24,7)
    steps(0,-3.57,z,1.93,3.45,2.23,17,"marble")
    group("佛香阁·八角阁三层四重金瓦檐")
    center_y=.55
    base=z+2.42
    octagon(0,center_y,base,2.18,1.11,.81,"rouge","goldTile","greenTile")
    octagon(0,center_y,base+1.45,1.84,.87,.71,"rouge","goldTile","greenTile")
    top=octagon(0,center_y,base+2.62,1.44,.81,1.04,"rouge","goldTile","teal")
    radial(0,center_y,top-.12,[(-.17,.87),(-.12,.92),(.08,.72,"goldTile"),(.26,.44,"goldTile"),
                              (.61,.05,"goldTile")],"greenTile",16)
    sphere(0,center_y,top+.57,.104,.104,.143,"gold",12,6)
    group("排云殿翼廊与松柏")
    for side in (-1,1):
        hall(side*3.68,-1.30,z+.78,2.19,1.36,.67,3,"rouge","rouge","goldTile",roof_height=.52)
        hall(side*3.25,2.48,z+.82,2.02,1.57,.78,3,"rouge","rouge","greyTile",roof_height=.52)
        tree(side*4.48,.81,z+.53,.92,33+side,True)
        tree(side*4.87,1.86,z+.40,.81,53+side,True)


def chengde():
    z=cut_base(12.68,7.9,"grey-stone","granite")
    group("山庄湖区·水面与驳岸")
    box(0,0,z,12.25,7.32,.052,"water")
    for sign in (-1,1):
        floorplan(sign*4.79,.80,z+.035,[(-1.37,-1.98),(1.37,-1.68),(1.34,2.72),
                                      (-1.35,2.49),(-1.63,1.61),(-1.44,-.73)],.17,"grass")
        tree(sign*5.40,1.98,z+.19,1.12,23+sign,False)
        tree(sign*4.36,2.81,z+.19,.82,26+sign,False)
    group("水心榭·桥墩与临水步廊")
    box(0,.19,z+.26,10.3,1.54,.22,"marble")
    for j in range(9):
        x=(j-4)*1.11
        for y in (-.38,.76):
            box(x,y,z+.055,.21,.23,.32,"grey-stone")
    for side in (-1,1):
        for scale, start in ((1,1.18),(.75,3.73)):
            rectangular_rail(side*start-.75*scale,side*start+.75*scale,-.55,z+.47,.31,6,"rouge")
    group("水心榭·三亭与连接檐")
    for j,x in enumerate((-3.28,0,3.28)):
        w=2.42 if j==1 else 1.78
        for xx in (-w*.36,w*.36):
            for yy in (-.51,.89):
                shaft(x+xx,yy,z+.48,.076,1.04,"rouge",7)
        profile(x,.19,z+1.42,[(0,w*1.09,1.62),(.125,w*1.04,1.65)],"teal")
        hip(x,.19,z+1.55,w*1.18,2.12,.40,"greyTile","rouge",.20)
        box(x,.19,z+1.78,w*.73,1.17,.31,"rouge")
        hip(x,.19,z+2.04,w*.93,1.59,.60 if j==1 else .50,"greyTile","rouge",.20)
    group("湖畔入口小牌坊")
    for sign in (-1,1):
        x=sign*5.04
        for yy in (-.41,.79):
            shaft(x,yy,z+.48,.067,.92,"rouge",6)
        box(x,.19,z+1.36,.15,1.46,.14,"teal")
        hip(x,.19,z+1.49,.58,1.76,.27,"greyTile","gold",.25)


def pingyao():
    z=cut_base(10.95,9.85,"grey-stone","ashlar")
    group("南大街·开敞街巷与基础券洞")
    for side in (-1,1):
        box(side*1.46,.35,z,1.03,2.17,1.50,"grey-stone")
    annular_arch(0,.35,z+.93,.89,.16,2.17,"granite",16)
    box(0,.35,z+1.95,3.98,2.25,.24,"grey-stone")
    for side in (-1,1):
        box(side*1.14,.35,z+1.31,.54,2.17,.67,"grey-stone")
    group("市楼·跨街金瓦与重檐")
    for i,(w,d,h) in enumerate(((3.78,2.22,1.09),(3.31,2.05,1.04),(2.74,1.75,.84))):
        z0=z+2.18+i*1.48
        hall(0,.35,z0,w,d,h,3,"rouge","rouge","goldTile","teal",roof_height=.75 if i==2 else .49,
             platform=i==0,upper_eave=False)
        rectangular_rail(-w*.45,w*.45,.35-d*.42,z0+.12,.23,7,"rouge")
    group("古城民居·灰瓦商铺")
    for sk in (-1,1):
        for i,y in enumerate((-3.08,.48,3.25)):
            x=sk*(3.93+.13*(i%2))
            # The sides of the miniature reveal the deep house plots.
            gray_house(x,y,z,2.15,2.25,1.34+.14*(i%2),2,"grey-stone")
            for k in range(3):
                yy=y+(k-1)*.53
                box(x-sk*1.101,yy,z+.12,.058,.39,1.1,"timber")
            box(x-sk*1.18,y,z+1.36,.16,2.11,.1,"timber")
    for i in range(8):
        box(0,-4.13+i*.45,z+.009,.76,.026,.023,"grey-stone")


def suzhou():
    z=cut_base(12.45,8.84,"grey-stone","grass")
    group("荷池·青水、石岸和曲桥")
    outline=[(-5.73,-2.82),(-4.53,-3.83),(-1.88,-3.91),(.30,-3.24),
             (2.90,-3.12),(5.51,-2.67),(5.81,-1.14),(4.55,.52),(2.75,.57),
             (.73,.88),(-.26,1.46),(-2.48,1.39),(-4.15,.57),(-5.67,.23)]
    floorplan(0,0,z,outline,.075,"water")
    for i,(p,q) in enumerate(zip(outline,outline[1:]+outline[:1])):
        cylinder((*p,z+.088),(*q,z+.088),.116,.116,"granite" if i%3 else "scree",6)
    for i in range(11):
        x=-3.25+i*.40
        y=-1.29+.48*cos(i*.75)
        sphere(x,y,z+.083,.225,.163,.018,"pine" if i%2==0 else "grass",8,4)
        if i in {1,4,6,10}:
            sphere(x+.03,y+.02,z+.102,.084,.069,.048,"lilac",9,5)
    for x,y,w,d in ((2.82,-2.68,.72,1.29),(3.72,-2.15,1.79,.54),(4.64,-1.39,.54,1.39)):
        box(x,y,z+.14,w,d,.10,"graniteLight")
    group("远香堂·四面厅、灰瓦与白墙游廊")
    hall(-.37,2.18,z+.15,5.52,2.24,1.37,5,"whitewash","timber","greyTile","beam",
         roof_height=.89,upper_eave=False,plaque=False)
    for i,x in enumerate((-4.66,-3.67,3.40,4.55,5.17)):
        y=1.93+(i%2)*.09
        box(x,y+.50,z+.07,1.24,.16,.94,"whitewash")
        for xx in (-.40,.40):
            shaft(x+xx,y-.37,z+.08,.062,.92,"beam",6)
        hip(x,y,z+.98,1.37,1.08,.34,"greyTile","beam")
    group("太湖石与山茶")
    for i,(x,y) in enumerate(((-4.82,-2.68),(-3.83,-3.57),(4.53,1.23),(4.84,2.87),(5.21,-2.84))):
        sphere(x,y,z+.26,.29,.36,.42,"scree",8,5)
        sphere(x+.08,y+.03,z+.58,.24,.19,.33,"granite",8,5)
        if i%2==0:
            tree(x+.36,y+.22,z+.03,.64,i+11,False)


def wuzhen():
    z=cut_base(13.1,7.65,"grey-stone","granite")
    group("西市河·桥里桥与水巷")
    box(0,-.42,z,12.73,2.48,.055,"water")
    box(3.56,-2.35,z,2.28,2.90,.055,"water")
    for x,w in ((-2.52,7.53),(5.54,1.44)):
        box(x,-1.77,z,w,.18,.36,"grey-stone")
    box(0,.86,z,12.78,.23,.34,"grey-stone")
    arch_bridge(1.13,-.41,z+.22,1.04,3.89,.76,"grey-stone","granite")
    # The perpendicular bridge has a genuine arch over the tributary.
    annular_arch(3.56,-2.21,z+.22,1.04,.18,.84,"grey-stone",15)
    for side in (-1,1):
        box(3.56+side*1.18,-2.21,z+.07,.32,.96,.61,"grey-stone")
    group("两岸·明清木屋与水廊")
    for i,(x,w,d,h) in enumerate(((-5.15,2.30,1.90,1.23),(-2.82,2.12,2.07,1.58),(-.56,2.21,1.99,1.32),
                                  (1.85,2.37,2.04,1.61),(4.64,2.65,2.14,1.48))):
        gray_house(x,2.12+.12*(i%2),z+.14,w,d,h,2,"whitewash" if i in (0,2,4) else "beam")
        for t in (-.36,.36):
            box(x+w*t,.94,z+.16,.096,.16,.94,"timber")
    for i,(x,w) in enumerate(((-4.88,2.24),(-2.49,2.15),(-.44,1.46))):
        gray_house(x,-2.76,z+.12,w,1.68,1.0+i*.09,1,"beam",True)
    group("乌篷船")
    for x,y in ((-2.6,-.52),(-4.45,.24)):
        center=z+.11
        floorplan(x,y,center,[(-.92,0),(-.54,-.20),(.64,-.20),(.93,0),(.60,.20),(-.60,.20)],.11,"timber")
        profile(x+.05,y,center+.08,[(0,.72,.36),(.30,.59,.30),(.345,.47,.23)],"dark")


def gulangyu():
    z=cut_base(10.8,8.20,"grey-stone","grass")
    group("八卦楼·浅色高台与红砖主楼")
    box(0,.34,z,8.69,6.72,.41,"whitewash")
    steps(0,-3.90,z,3.52,1.74,.41,9,"marble")
    base=z+.41
    radial(0,.48,base,[(0,3.48),(1.81,3.48),(1.93,3.54),(2.71,3.54)],
           "soft-wall",8,pi/8)
    for i in range(8):
        a=pi/4*i
        radial_pos=(cos(a),sin(a))
        tangent=(-sin(a),cos(a))
        for off in (-.73,0,.73):
            x=3.27*radial_pos[0]+off*tangent[0]
            y=.48+3.27*radial_pos[1]+off*tangent[1]
            shaft(x,y,base+.08,.105,1.68,"whitewash",8)
            shaft(x,y,base+.06,.152,.103,"graniteLight",8)
            shaft(x,y,base+1.68,.149,.125,"whitewash",8,.124)
        x=3.26*radial_pos[0]; y=.48+3.26*radial_pos[1]
        x0,y0=x-tangent[0]*.30,y-tangent[1]*.30
        x1,y1=x+tangent[0]*.30,y+tangent[1]*.30
        face([(x0,y0,base+2.08),(x1,y1,base+2.08),(x1,y1,base+2.59),(x0,y0,base+2.59)],"dark")
    radial(0,.48,base+.04,[(0,3.67),(.12,3.67)],"whitewash",8,pi/8)
    for zz in (1.81,2.65):
        radial(0,.48,base+zz,[(0,3.55),(.1,3.73),(.18,3.73)],"whitewash",8,pi/8)
    group("八角红色穹顶及塔亭")
    radial(0,.48,base+2.70,[(0,2.28),(.19,2.30),(.28,2.32),(.56,2.41),
                           (.85,2.36),(1.12,2.22),(1.41,1.97),(1.78,1.48),
                           (2.10,.91),(2.27,.5)],"plum",32,pi/8)
    for i in range(8):
        a=2*pi*i/8
        for j,((h0,r0),(h1,r1)) in enumerate(zip(((.22,2.31),(.58,2.43),(1.12,2.24),(1.56,1.80)),
                                                ((.58,2.43),(1.12,2.24),(1.56,1.80),(2.18,.74)))):
            cylinder((r0*cos(a),.48+r0*sin(a),base+2.70+h0),
                     (r1*cos(a),.48+r1*sin(a),base+2.70+h1),.045,.041,"rouge",5)
    radial(0,.48,base+4.91,[(0,.52),(.65,.52),(.75,.61),(.87,.57),(1.11,.15)],
           "soft-wall",8,pi/8)
    shaft(0,.48,base+5.96,.042,.31,"gold",8,.015)


def round_tulou(x,y,z,r,aspect=1,sides=36):
    def loop(rr,hh,k):
        a=2*pi*k/sides
        return (x+rr*cos(a),y+aspect*rr*sin(a),z+hh)
    h=r*.67
    wall=[(r*.99,0),(r,h*.13),(r*.982,h*.96),(r*1.032,h),
          (r*1.08,h+.10),(r*.86,h+.30),(r*.76,h+.47),
          (r*.67,h+.31),(r*.65,h+.16),(r*.71,h+.028),
          (r*.73,h*.78),(r*.74,0)]
    for j,(a,b) in enumerate(zip(wall,wall[1:]+wall[:1])):
        mat=("sand" if j in (0,1,2,10) else "greyTile" if j in (3,4,5,6,7,8) else "timber")
        for i in range(sides):
            k=(i+1)%sides
            face([loop(*a,i),loop(*a,k),loop(*b,k),loop(*b,i)],mat)
    for i in range(0,sides,2):
        a=2*pi*i/sides
        xx,yy=x+r*.985*cos(a),y+r*.993*aspect*sin(a)
        for k in range(2):
            # Window recesses read as glazed slots from the map's viewing distance.
            box(xx,yy,z+h*(.49+.24*k),.09,.081,.129,"timber")
    for h0 in (h*.31,h*.60):
        for i in range(0,sides,2):
            a=2*pi*i/sides
            xx,yy=x+r*.721*cos(a),y+r*.721*aspect*sin(a)
            shaft(xx,yy,z+h0-.17,.023,.20,"timber",5)
    box(x,y-r*aspect*.977,z+.063,.26,.13,h*.37,"timber")


def square_tulou(x,y,z,w,d):
    h=w*.35
    group("步云楼·方楼内院")
    for yy in (y-d*.42,y+d*.42):
        box(x,yy,z,w,d*.16,h,"sand")
        for i in range(7):
            box(x+(i-3)*w*.136,yy-d*.08-.02,z+h*.59,.11,.047,.13,"timber")
    for xx in (x-w*.42,x+w*.42):
        box(xx,y,z,w*.16,d*.84,h,"sand")
    p0=[(-w*.53,-d*.53),(w*.53,-d*.53),(w*.53,d*.53),(-w*.53,d*.53)]
    p1=[(a*.86,b*.86) for a,b in p0]
    p2=[(a*.69,b*.69) for a,b in p0]
    for i in range(4):
        j=(i+1)%4
        face([(x+p0[i][0],y+p0[i][1],z+h),(x+p0[j][0],y+p0[j][1],z+h),
              (x+p1[j][0],y+p1[j][1],z+h+.30),(x+p1[i][0],y+p1[i][1],z+h+.30)],"greyTile")
        face([(x+p1[i][0],y+p1[i][1],z+h+.30),(x+p1[j][0],y+p1[j][1],z+h+.30),
              (x+p2[j][0],y+p2[j][1],z+h+.025),(x+p2[i][0],y+p2[i][1],z+h+.025)],"greyTile")


def tulou():
    z=cut_base(12.15,9.76,"grey-stone","grass")
    group("田螺坑·顺等高线叠起的山地")
    profile(0,1.31,z,[(0,10.92,6.42),(.90,9.72,5.53),(1.28,8.72,4.71)],"grass")
    box(0,-1.43,z,10.12,3.69,.19,"grass")
    group("和昌楼、振昌楼、瑞云楼、文昌楼")
    for x,y,h,r,a in ((-3.36,.83,.80,1.84,1),(3.36,.90,.77,1.68,1),
                      (-1.93,-2.63,.19,1.60,1),(2.00,-2.49,.20,1.67,.79)):
        profile(x,y,z,[(0,r*2.14,2.19*r*a),(h,r*2.02,2.03*r*a)],"grass")
        round_tulou(x,y,z+h,r,a)
    square_tulou(0,1.46,z+1.22,2.72,2.36)
    group("山路与竹林")
    for i in range(10):
        box(-4.42+i*.89,-3.99+.14*sin(i*.48),z+.013,.9,.44,.035,"sand")
    for i,(x,y,h) in enumerate(((-5.34,1.94,.23),(5.34,1.99,.22),(-4.92,-2.10,.20),(4.81,-2.42,.17),
                                (-2.95,3.36,1.01),(2.82,3.25,1.01))):
        tree(x,y,z+h,.55,i+20,True)
