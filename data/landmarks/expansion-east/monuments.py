"""Representative monuments and rock-cut sculpture."""

from math import cos, exp, pi, sin
from random import Random

from geometry import annular_arch, box, cylinder, face, group, hip, profile, shaft, sphere, steps, window
from architecture import curve_rail, cut_base, hall, octagon, radial, tree


def temple_of_heaven():
    group("祈谷坛·三层汉白玉圆台")
    for i, (radius, z) in enumerate(((4.55,0),(3.93,.36),(3.33,.72))):
        radial(0,0,z,[(0,radius*1.007),(.07,radius*1.007),(.11,radius*.98),
                      (.29,radius*.97),(.36,radius)],"marble",40)
        for quadrant in range(4):
            a = (quadrant-.5)*pi/2
            curve_rail(0,0,z+.36,radius*.925,a+.20,a+pi/2-.20,.25,8)
        # Four axial approaches interrupted only at their exposed steps.
        steps(0,-radius-.12,z,1.05,.58,.36,6,"snow")
        for x in (-.64,.64):
            box(x,-radius+.16,z,.12,.68,.25,"marble")
    group("祈年殿·柱廊与彩绘梁")
    radial(0,0,1.08,[(0,2.88),(.125,2.88),(.17,2.73)],"granite",36)
    radial(0,0,1.25,[(0,2.22),(1.60,2.22)],"rouge",36)
    for i in range(24):
        a = 2*pi*i/24
        x,y=cos(a)*2.54,sin(a)*2.54
        shaft(x,y,1.25,.079,1.65,"rouge",7)
        shaft(x,y,1.25,.116,.11,"granite",7)
        shaft(x,y,2.75,.122,.18,"teal",7)
    for x in (-1.35,0,1.35):
        y=-((2.22**2-x*x)**.5)-.019
        window(x,y,1.4,.64,1.17,"gold","dark")
    group("宝蓝琉璃瓦·三重攒尖檐")
    for z,r,h,top in [(2.89,3.07,.66,2.12),(3.86,2.48,.59,1.62),(4.76,1.87,1.33,.09)]:
        radial(0,0,z,[(-.045,r*.938),(0,r),(.055,r*1.009,"cobalt"),(.19*h+.07,r*.86,"cobalt"),
                      (.55*h,r*.68 if top < .2 else r*.79,"cobalt"),(h,top,"cobalt")],
               "beam",40,roof_uv=True)
        if top>.2:
            rz=z+h-.012
            radial(0,0,rz,[(0,top*1.012),(.062,top*1.012),(.09,top*.945,"cobalt"),
                          (.274,top*.945,"teal"),(.32,top*.98,"gold"),(.355,top*.98,"teal")],
                   "rouge",36)
            for i in range(36):
                a=2*pi*i/36
                shaft(top*.949*cos(a),top*.949*sin(a),rz+.084,.022,.207,
                      "gold" if i%3==0 else "mint",5)
    radial(0,0,6.075,[(0,.18),(.10,.23),(.24,.19),(.36,.08),(.45,.051)],"gold",16)


def rock_wall(width, depth, height, base, material, seed, niche=None):
    """Modeled sandstone stratum front, with cavity depth reflected in the silhouette."""
    rng = Random(seed)
    nx, nz = 27, 14
    pts = []
    for j in range(nz+1):
        row=[]
        for i in range(nx+1):
            x=(-.5+i/nx)*width
            frac=j/nz
            z=base+frac*height
            if j==nz:
                z+=.20*sin(i*.77)+.12*cos(i*1.67)
            elif j:
                z+=rng.uniform(-.09,.09)
            y=-depth*.38 + .22*sin(i*.49+frac*6)+.08*cos(i*2.84+j*.79)
            if niche:
                y+=niche(x,frac)
            y+=.42*(i/(nx/2)-1)**4
            row.append((x,y,z))
        pts.append(row)
    for j in range(nz):
        for i in range(nx):
            v=[pts[j][i],pts[j][i+1],pts[j+1][i+1],pts[j+1][i]]
            mat = "clayDark" if j in (2,10) and material=="clayLight" else material
            if material=="sands-red" and (j in (2,6,10) or rng.random()<.17):
                mat="sands-shadow"
            if j%2==0:
                face(v[:3],mat)
                face([v[0],v[2],v[3]],mat)
            else:
                face([v[0],v[1],v[3]],mat)
                face(v[1:],mat)
    rear=depth*.49
    for i in range(nx):
        a,b=pts[-1][i:i+2]
        face([a,b,(b[0],rear,b[2]-.02),(a[0],rear,a[2]-.02)],material)
        a,b=pts[0][i:i+2]
        face([(a[0],rear,a[2]),(b[0],rear,b[2]),b,a],material)
        a,b=pts[-1][i:i+2]
        face([(a[0],rear,base),(a[0],rear,a[2]-.02),(b[0],rear,b[2]-.02),(b[0],rear,base)],material)
    for i in (0,nx):
        for lo,hi in zip(pts,pts[1:]):
            a,b=lo[i],hi[i]
            # Insert the actual split level along the rear side to keep faces planar.
            p,q=(a[0],rear,a[2]),(b[0],rear,b[2])
            face([p,a,b,q] if i==0 else [a,p,q,b],material)


def torso(x, y, z, levels, mat, sc, sides=22):
    loops=[[(x+rx*sc*cos(a),y+(dy+ry*sin(a))*sc,z+hh*sc)
            for a in (2*pi*i/sides for i in range(sides))]
           for hh,dy,rx,ry in levels]
    face(loops[0][::-1],mat)
    face(loops[-1],mat)
    for lo,hi in zip(loops,loops[1:]):
        for i in range(sides):
            k=(i+1)%sides
            face([lo[i],lo[k],hi[k],hi[i]],mat)


def seated_buddha(x, y, z, s, mat, relief, relaxed=False):
    group("坐佛·结跏趺坐" if not relaxed else "坐佛·双手扶膝")
    torso(x,y,z,[(0,.09,.38,.32),(.12,.10,.66,.39),(.26,.13,.64,.38),
                 (.53,.13,.42,.32),(.80,.16,.36,.29),(1.01,.18,.41,.27),
                 (1.16,.19,.48,.26),(1.32,.17,.43,.24),(1.43,.13,.26,.19),
                 (1.52,.11,.14,.12)],mat,s)
    for side in (-1,1):
        sphere(x+side*.43*s,y-.085*s,z+.22*s,.35*s,.35*s,.24*s,mat,15,8)
        if relaxed:
            sphere(x+side*.36*s,y-.36*s,z+.08*s,.22*s,.29*s,.10*s,mat,12,5)
        shoulder=(x+side*.42*s,y+.08*s,z+1.21*s)
        elbow=(x+side*(.51 if relaxed else .42)*s,y+.03*s,z+.70*s)
        hand=(x+side*(.53 if relaxed else .25)*s,y-.24*s,z+(.31 if relaxed else .51)*s)
        cylinder(shoulder,elbow,.142*s,.115*s,mat,12)
        sphere(*elbow,.116*s,.115*s,.125*s,mat,10,7)
        cylinder(elbow,hand,.113*s,.079*s,mat,12)
        sphere(*hand,.11*s,.115*s,.07*s,mat,10,5)
        for i in range(3):
            xx=x+side*(.34+.045*i)*s
            cylinder((xx,y-.115*s,z+(1.23-.028*i)*s),
                     (x+side*.25*s,y-.15*s,z+(.94-.07*i)*s),.025*s,.018*s,relief,5)
    group("坐佛·面相与螺髻")
    hz=z+1.73*s
    sphere(x,y+.08*s,hz,.308*s,.217*s,.335*s,mat,22,11)
    sphere(x,y+.105*s,z+2.01*s,.285*s,.198*s,.172*s,relief,20,7)
    sphere(x,y+.115*s,z+2.14*s,.113*s,.103*s,.079*s,relief,12,6)
    for side in (-1,1):
        sphere(x+side*.272*s,y+.036*s,hz-.08*s,.068*s,.062*s,.153*s,mat,10,5)
        sphere(x+side*.105*s,y-.112*s,hz+.022*s,.079*s,.030*s,.019*s,relief,10,4)
    sphere(x,y-.137*s,hz-.035*s,.053*s,.060*s,.073*s,mat,11,6)
    sphere(x,y-.111*s,hz-.142*s,.087*s,.029*s,.018*s,relief,10,4)
    for k in range(12):
        a=2*pi*k/12
        sphere(x+.238*s*cos(a),y+.08*s+.163*s*sin(a),z+1.995*s,
               .047*s,.047*s,.042*s,relief,6,4)


def yungang():
    z=cut_base(10.6,4.45,"clayDark","clayLight")
    group("昙曜五窟·第二十窟崩塌崖壁")
    rock_wall(10.25,3.1,5.1,z,"clayLight",182,lambda x,t:1.40*exp(-(x/2.35)**4)*(1-0.80*t**7))
    group("供养人小窟与石刻轮廓")
    for x,zz,s in ((-3.70,1.6,.37),(-3.17,3.20,.33),(3.38,1.83,.46),(3.96,3.62,.29)):
        yy=-1.08
        sphere(x,yy,zz,.42*s,.13,.79*s,"clayDark",9,6)
        shaft(x,yy-.11,zz-.44*s,.17*s,.53*s,"granite",7,.12*s)
        sphere(x,yy-.13,zz+.13*s,.15*s,.09,.18*s,"granite",8,5)
    seated_buddha(0,-.65,z+.06,2.05,"graniteLight","granite")
    group("风化崖脚")
    for i,x in enumerate((-4.3,-3.8,3.2,3.92,4.21)):
        sphere(x,-1.32,z+.04,.33,.27,.21,"rock" if i%2 else "clayDark",7,4)


def wutai():
    z=cut_base(9.1,7.5,"granite","graniteLight")
    group("塔院寺·大白塔")
    radial(0,.3,z,[(0,1.48),(.30,1.48),(.38,1.30),(.52,1.30),(.62,1.04),(.79,1.04)],
           "whitewash",32)
    radial(0,.3,z+.77,[(0,.74),(.19,.71),(.33,.78),(.56,.98),(.95,1.17),
                     (1.31,1.18),(1.62,1.10),(1.82,.94),(1.96,.80),(2.02,.79)],"snow",36)
    radial(0,.3,z+2.77,[(0,.64),(.18,.64),(.20,.46),(.37,.38)],"whitewash",16)
    for i in range(13):
        rr=.42-.018*i
        radial(0,.3,z+3.14+.100*i,[(0,rr),(.052,rr),(.092,rr*.79)],"whitewash",18)
    radial(0,.3,z+4.43,[(0,.31),(.13,.35),(.20,.31),(.31,.18),(.40,.16),
                       (.49,.08)],"gold",16)
    sphere(0,.3,z+4.98,.115,.115,.17,"gold",12,7)
    group("塔前门楼、红墙与山门")
    hall(0,-2.44,z,2.10,1.1,.64,3,"rouge","rouge","greyTile",roof_height=.49)
    for side in (-1,1):
        box(side*2.64,-2.44,z,3.02,.17,.61,"rouge")
        box(side*2.64,-2.44,z+.61,3.08,.26,.07,"greyTile")
        hall(side*2.80,.63,z,1.76,1.87,.77,3,"rouge","rouge","greyTile",roof_height=.53,plaque=False)
        tree(side*3.87,2.73,z,.66,313+side,True)
    for k in range(5):
        box((k-2)*.39,-1.4,z+.02,.30,.43,.045,"ashlar")


def shaolin():
    z=cut_base(9.55,6.45,"granite","ashlar")
    group("少林寺·清式山门三开间")
    box(0,.52,z,6.36,3.4,.40,"granite")
    steps(0,-2.66,z,2.56,1.53,.40,11,"graniteLight")
    zz=z+.40
    # True arched through-passage beneath the brick lintel.
    r, w, depth, spring = .74, 5.98, 2.66, 1.16
    for side in (-1,1):
        box(side*((w/2+r)/2),.54,zz,w/2-r,depth,1.16,"plum")
        box(side*2.47,-.83,zz+.38,.78,.19,1.41,"rouge")
        shaft(side*.94,-.86,zz,.109,1.94,"rouge",8)
    annular_arch(0,.54,zz+spring,r,.19,depth,"graniteLight",16)
    for side in (-1,1):
        box(side*1.95,.54,zz+1.16,2.08,depth,.81,"grey-stone")
    box(0,.54,zz+1.91,5.99,depth,.18,"grey-stone")
    box(0,-.86,zz+1.91,1.80,.19,.35,"gold")
    box(0,-.967,zz+1.962,1.66,.042,.24,"dark")
    for i in range(3):
        box((i-1)*.38,-.992,zz+2.01,.105,.014,.12,"gold")
    for side in (-1,1):
        for i in range(11):
            xx=side*(.15+i*.25)
            box(xx,-.81,zz+2.11,.100,.16,.16,"teal")
    hip(0,.54,zz+2.24,7.65,4.43,1.44,"greyTile","beam",.24)
    for side in (-1,1):
        box(side*4.30,.48,z,2.1,.39,1.1,"plum")
        box(side*4.30,.48,z+1.04,2.14,.50,.12,"greyTile")
        tree(side*3.94,1.55,z,1.03,401+side,True)
        sphere(side*1.85,-2.22,z+.34,.27,.19,.35,"graniteLight",10,7)
        box(side*1.85,-2.22,z,.53,.45,.21,"grey-stone")


def leshan():
    z=cut_base(10.85,5.0,"dark","rock")
    group("凌云山·临江红砂岩")
    rock_wall(10.65,4.48,5.15,z,"sands-red",703,lambda x,t:1.12*exp(-(x/2.35)**4)*(1-.87*t**6))
    group("三江汇流·岸边一隅")
    box(0,-1.85,z,.97*10.85,1.1,.065,"water")
    box(0,-1.11,z+.015,4.8,.60,.18,"rock")
    seated_buddha(0,-.86,z+.14,2.10,"graniteLight","granite",True)
    group("九曲栈道")
    for i, (xoff, y, h) in enumerate(((3.5,-1.89,.25),(3.05,-1.78,1.19),(3.62,-1.7,2.03),
                                     (3.21,-1.66,2.95),(3.90,-1.55,3.9))):
        for j in range(7):
            f=j/6 if i%2==0 else 1-j/6
            xx=xoff+(j-3)*.23
            zz=z+h+.76*f
            box(xx,y,zz,.28,.31,.13,"granite")
            box(xx,y-.14,zz+.10,.11,.12,.23,"rock")
    for i, (x,y) in enumerate(((-4.1,1.2),(-3.2,1.5),(2.4,1.2),(4.1,1.3),(4.8,1.4))):
        tree(x,y,z+5.02,.53,i+1,False)


def shanhaiguan():
    z=cut_base(11.8,6.9,"grey-stone","ashlar")
    group("明长城·灰砖垒砌关台")
    for side in (-1,1):
        profile(side*2.94,.35,z,[(0,4.32,2.44),(2.15,4.19,2.25)],"grey-stone")
        profile(side*4.35,.87,z,[(0,1.63,1.79),(1.46,1.51,1.62)],"grey-stone")
    annular_arch(0,.35,z+.73,.92,.23,2.32,"granite",15)
    box(-.95,.35,z,.35,2.32,.81,"grey-stone")
    box(.95,.35,z,.35,2.32,.81,"grey-stone")
    box(0,.35,z+1.87,2.40,2.32,.35,"grey-stone")
    for side in (-1,1):
        for j in range(6):
            xx=side*(.80+j*.75)
            box(xx,-.85,z+2.12,.44,.28,.38,"grey-stone")
            box(xx,1.47,z+2.12,.44,.28,.38,"grey-stone")
    group("天下第一关·镇东楼")
    hall(0,.35,z+2.22,5.62,2.35,1.10,5,"rouge","rouge","greyTile",upper_eave=True,roof_height=.93)
    box(0,-.863,z+3.10,1.96,.12,.28,"whitewash")
    for i in range(5):
        box((i-2)*.28,-.942,z+3.15,.068,.022,.14,"dark")
    for side in (-1,1):
        steps(side*4.21,-2.27,z,1.01,1.40,.39,7,"granite")


def shenyang():
    z=cut_base(10.9,7.5,"granite","ashlar")
    group("大政殿·八角重檐与金龙柱")
    radial(0,.52,z,[(0,3.12),(.13,3.14),(.22,3.03),(.42,2.91)],"marble",8,pi/8)
    steps(0,-3.55,z,1.9,1.58,.42,8,"marble")
    roof_z=octagon(0,.52,z+.42,2.40,1.37,1.25,"rouge","goldTile","greenTile",True,base="marble")
    radial(0,.52,roof_z-.21,[(-.26,1.59),(-.17,1.61),(.03,1.48,"goldTile"),
                           (.20,1.11,"goldTile"),(.54,.78,"goldTile"),(.94,.075,"goldTile")],
           "greenTile",8,pi/8)
    sphere(0,.52,roof_z+.81,.143,.143,.192,"gold",12,7)
    for side in (-1,1):
        x=side*.90
        shaft(x,-1.77,z+.55,.105,1.32,"rouge",9)
        for j in range(12):
            k=j+1
            cylinder((x+.108*cos(j*.70),-1.77+.108*sin(j*.70),z+.63+j*.096),
                     (x+.108*cos(k*.70),-1.77+.108*sin(k*.70),z+.63+k*.096),.036,.037,"gold",5)
    group("两翼旗亭·十王亭取样")
    for side in (-1,1):
        for i,(x,y) in enumerate(((4.33,1.42),(4.63,-1.1))):
            hall(x*side,y,z,1.18,1.56,.75,3,"rouge","rouge","greyTile",roof_height=.56,plaque=False)
