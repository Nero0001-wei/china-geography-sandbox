"""The three terrain scenes each follow the surveyed display viewpoint."""
from math import cos, exp, hypot, sin
from random import Random

from shapes import (
    GROUND, base, boulder, box, bush, currents, face, floorplan, forest,
    group, hip, hut, noise, peak, plank_line, stack, steps, surface, tree_shade,
)

TILE = (-2.97, 2.97, -2.04, 2.04)
INTERIOR = (-2.77, 2.77, -1.91, 1.96)


def smooth01(t):
    t = max(0, min(1, t))
    return t*t*(3 - 2*t)


def hukou_falls():
    base("hukouStone2", "hukouStone0")
    lip_y = .18
    lower_z = .454

    def cleft(y):
        return .081*sin(3.6*y) + .049*sin(7.4*y + .56)

    def slot_half_width(y):
        return .48 + .051*cos(y*3.54 + .48) + .066*sin(7.20*y) + .14*(y+2.04)/2.16

    def sandstone(x, y):
        d = abs(x - cleft(y))
        ledge = .14*max(0, d - 1.04) + .072*noise(x/1.8, y*.94)
        shelf = 1.30 + ledge + .07*y
        groove = slot_half_width(y) + .034*sin(y*24)
        valley = smooth01((d - groove) / .26)
        upstream = smooth01((y - lip_y + .10) / .29)
        valley = max(valley, upstream)
        # A longitudinal fault deepens into the downstream 'dragon trough'.
        return .394 + valley * (shelf - .394)

    stone = ("hukouStone0", "hukouStone1", "hukouStone2", "hukouStone3", "hukouStone1", "hukouStone4")
    def strata(x, y, z):
        band = (z + .017*sin(x*2.3 + y*3.22))*17.4
        return stone[int(band) % len(stone)]

    surface("黄河壶口两岸的水平砂岩台沿和峡槽", TILE, 45, 45, sandstone, strata)
    group("峡槽水平层理")
    for side in (-1,1):
        for bed in range(7):
            z=.535+.118*bed
            rows=[]
            for j in range(25):
                y=-1.98+j*.080
                lo=slot_half_width(y)-.07
                hi=slot_half_width(y)+.37
                for _ in range(8):
                    middle=(lo+hi)/2
                    if sandstone(cleft(y)+side*middle,y)<z:
                        lo=middle
                    else:
                        hi=middle
                x=cleft(y)+side*hi
                extension=.018+.027*(.5+.5*sin(y*6+bed))
                rows.append(((x,y,z),(x-side*extension,y,z+.002),(x-side*extension,y,z-.038)))
            for a,b in zip(rows,rows[1:]):
                face([a[0],a[1],b[1],b[0]],stone[(bed+2)%len(stone)])
                face([a[1],a[2],b[2],b[1]],stone[bed%len(stone)])
    group("延展至河槽两侧的岩层断口")
    rng = Random(6)
    for hand in (-1, 1):
        for i in range(8):
            y = -1.74 + .26*i
            x = hand*(slot_half_width(y)+.24+rng.uniform(.02,.15))
            z = sandstone(x,y)-.15
            stack("河槽断层基岩",x,y,z,[(0,.27,.21,0,0),(.07,.285,.22,0,0),
                  (.14,.28,.18,.021,0),(.22,.20,.15,.04,0)],strata_face,n=9,seed=i+12*hand)
    for i in range(14):
        x = (1 if i%2 else -1)*rng.uniform(1.58, 2.77)
        y = rng.uniform(-1.72, 1.83)
        z = sandstone(x,y)-.024
        boulder(x,y,z,.10,.083,.075,i+15,mat="hukouStone4",label="岩面散石")

    # The upper run is much wider than the downstream trough.
    group("上游铺开的黄褐色河水")
    top_rows = []
    for i in range(33):
        y = .24 + (2.036-.24)*i/32
        f = (y-.24)/(2.036-.24)
        width = 1.24 + 3.32*smooth01(f*.96)
        row = []
        for j in range(17):
            u = 2*j/16 - 1
            x = cleft(y) - f*.13 + width/2*u + .029*sin(y*15+j*.88)
            z = max(1.41+.029*y, sandstone(x,y)+max(.022,.049*(1-u*u))) + .008*sin(x*17+y*11)
            row.append((x,y,z))
        top_rows.append(row)
    for i, (near, far) in enumerate(zip(top_rows, top_rows[1:])):
        for j in range(16):
            mat = ("riverOchre","riverHoney","riverHoney","riverGold")[int(8*abs(sin(i*.32-j*1.15)))%4]
            face([near[j],near[j+1],far[j+1],far[j]],mat)

    group("主瀑水帘")
    rng = Random(83)
    flows = []
    for j in range(43):
        u = -1+2*j/42
        x = .62*u
        fall_lip = lip_y + .10*(u**2) + rng.uniform(-.038,.038)
        bottom = -.335 + .09*sin(u*9.0)
        z_top = 1.44 + .034*sin(j*.95)
        path = [(x,fall_lip+.08,z_top),(x*.98,fall_lip,z_top-.045),
                (x*.90,fall_lip-.064,1.20),(x*.87,fall_lip-.13,.98),
                (x*.75,fall_lip-.218,.74),(x*.69,bottom+.08,.56),(x*.80,bottom,lower_z + .014)]
        flows.append(path)
    for j,(left,right) in enumerate(zip(flows,flows[1:])):
        for k in range(6):
            phase=(j*8+k*3)%21
            mat="riverIvory" if phase<4 or (k>=4 and phase<10) else "riverGold" if phase<17 else "riverOchre"
            face([left[k],left[k+1],right[k+1],right[k]],mat)

    group("窄峡槽下游翻涌")
    for i in range(51):
        ya=-2.025+1.83*i/51
        yb=-2.025+1.83*(i+1)/51
        for j in range(9):
            def at(y,k):
                u=(k/9-.5)*2
                return cleft(y)+u*(slot_half_width(y)-.021),y,lower_z+.009*sin(y*17+u*12)
            colors=("riverDusk","riverOchre","riverGold","riverGold","riverIvory")
            face([at(ya,j),at(ya,j+1),at(yb,j+1),at(yb,j)],colors[(i*2+j*3)%5])
    currents(22,(-.58,.58,-1.94,-.28),120,lower_z+.014,
             lambda x,y:abs(x-cleft(y))<slot_half_width(y)-.05,material="riverIvory",along=(.085,1))
    group("瀑脚卷起的层叠涌浪")
    rng=Random(61)
    for i in range(47):
        x=rng.uniform(-.42,.43)
        y=rng.uniform(-.78,-.20)
        z = lower_z + rng.uniform(.022,.050)
        w=rng.uniform(.025,.105)
        face([(x-w,y,z),(x-w*.12,y-.055,z+w*.77),(x+w,y-.084,z+w*.51),
              (x+w*.72,y-.076,z)],"riverIvory" if i%5 else "riverGold")


def strata_face(i,j):
    return ("hukouStone0","hukouStone3","hukouStone1","hukouStone2")[(i*3+j//4)%4]


def qutang_kuimen():
    base("gorgeWater","gorgeCut")
    def centre(y):
        return -.14+.29*sin(y*.82 + .50) + .12*sin(y*2.3)
    def half_width(y):
        f=smooth01((y+1.92)/3.3)
        return 1.63-.88*f+.07*sin(y*2.4)

    def walls(x,y):
        dx = x-centre(y)
        d = abs(dx) - half_width(y)
        if d < -.11:
            return .312
        north = dx < 0
        # The rock foot is near vertical along the bend and broadens into karst ridges.
        phase = .091*sin(y*11.7 + (.3 if north else .8)) + .061*cos(y*17.8)
        height = ((2.96 + .32*sin(y*1.55 + .45) + .57*exp(-((y-.81)/.83)**2)) if north else
                  (2.59 + .33*cos(y*1.75+.05) + .52*exp(-((y-1.02)/.77)**2)))
        head = 1- exp(-max(0, d+phase+.001)**1.16/(.19 if north else .22))
        gully = .22*sin(7.10*y+1.87*x)+.11*sin(y*13.2 + x*5.1)
        plunge = .21*max(0,d-.95)
        return .30+head*(height+gully-plunge)

    def stone(x,y,z):
        d=abs(x-centre(y))-half_width(y)
        shade=noise(x*.6,y*1.35)
        bastion=sin(y*9.67+.89*x + z*.3)
        if z<.40:
            return "gorgeWater"
        if z<.52:
            return "gorgePale"
        if z>2.45+(0.38 if x<0 else -.23)*sin(y*.86) or d>1.03 or (z>.62 and shade>.54):
            return "gorgeCanopy" if shade>.05 else "pine"
        if x<centre(y):
            return "redLime" if bastion>.21 else "gorgeShadow" if bastion<-.68 else "gorgeWall"
        return "paleLime" if bastion>.10 else "gorgeWall" if bastion<-.33 else "gorgePale"

    surface("赤甲与白盐两侧的石壁和峡底",TILE,52,43,walls,stone)
    forest(81,INTERIOR,47,walls,lambda x,y:walls(x,y)>2.48 and abs(x-centre(y))>half_width(y)+.53,
           min_size=.12,max_size=.31,woodland="broad")
    for s in (-1,1):
        for j in range(10):
            y=-1.72+j*.36
            d=half_width(y)+.31+.095*sin(j*4.88)
            x=centre(y)+s*d
            if walls(x,y)>.69:
                bush(x,y,walls(x,y)-.023,.108,j*7+s,greens=("pine","gorgeCanopy","leaf"))
    currents(91,(-1.63,1.64,-1.94,1.97),110,GROUND+.010,
             lambda x,y: abs(x-centre(y))<half_width(y)-.13,material="gorgeRipple")
    group("夔门江上取景小游船")
    cx,cy=-.05,-.94
    hull=[(-.11,-.32),(.10,-.29),(.13,.16),(.085,.30),(0,.35),(-.08,.29),(-.13,.19)]
    floorplan(cx,cy,.361,hull,.089,"gorgeBlue")
    floorplan(cx,cy+.03,.437,[(-.082,-.22),(.086,-.22),(.085,.17),(0,.26),(-.082,.18)],.057,"white")
    box(cx,cy+.04,.491,.142,.28,.071,"white")
    box(cx,cy+.12,.531,.159,.124,.056,"white")
    box(cx+.073,cy+.12,.518,.015,.235,.042,"gorgeBlue")
    box(cx-.073,cy+.12,.518,.015,.235,.042,"gorgeBlue")
    plank_line("游船尾迹",[(cx-.12,cy-.20,.371),(cx-.30,cy-.55,.371),(cx-.47,cy-.73,.371)],.007,"gorgeRipple",4)
    plank_line("游船尾迹",[(cx+.10,cy-.20,.371),(cx+.30,cy-.55,.371),(cx+.49,cy-.75,.371)],.007,"gorgeRipple",4)


def erhai():
    base("erhaiLake","erhaiWaterCut")

    def shore(y):
        return -1.91 + .39*sin(y*.90 + .35) + .17*sin(y*2.6+.7)

    def silhouette(x,y):
        near = min(.35,max(0,(shore(y)-x)*.57))
        # Cangshan on the far bank is compressed so the expansive lake stays visible.
        ridge=0.0
        for i,(cx,w,h) in enumerate(((-2.45,.57,.41),(-1.46,.65,.58),(-.38,.64,.66),(.52,.68,.59),
                                     (1.38,.54,.66),(2.18,.52,.49),(2.71,.45,.38))):
            ridge=max(ridge,peak(x,y,cx,1.89,w,.253,h,1.22))
        ridge *= (.89 + .10*sin(x*10.7+y*3.1))
        return .297+near+.05*noise(x,y)*min(1,near*5)+ridge

    def terrain_material(x,y,z):
        if y>1.48 and x>shore(y):
            return "erhaiDistant" if z<.81 else "erhaiDistantLight" if sin(x*15.6)>-.42 else "paleLime"
        return "erhaiSand" if z<.43 else "erhaiReed" if noise(x,y)<.10 else "gorgeCanopy"

    surface("洱海东岸与苍山远景",TILE,45,36,silhouette,terrain_material)
    cx,cy=.54,-.28
    stack("小普陀湖中岩屿",cx,cy,.358,[(0,.68,.48,0,0),(.076,.65,.461,0,0),
          (.190,.53,.39,-.017,.015),(.28,.46,.34,.015,.009),(.31,.415,.322,.02,.01)],
          lambda j,i:("erhaiGrey","erhaiSand","cliff","oldstone")[(j*2+i//3)%4],n=21,seed=78)
    group("观音阁方形石基与临水台阶")
    box(cx,cy+.012,.631,.76,.61,.085,"oldstone")
    box(cx,cy+.012,.699,.69,.55,.070,"erhaiSand")
    steps(cx,cy-.431,.552,.25,.234,.214,7,"oldstone")
    # Open portico stays visible below the flared lower eaves.
    group("小普陀观音阁下层")
    box(cx,cy+.078,.770,.58,.39,.34,"white")
    for x in (cx-.24,cx+.24):
        box(x,cy-.245,.770,.054,.054,.335,"erhaiWood")
    box(cx,cy-.221,1.038,.61,.056,.065,"erhaiWood")
    box(cx,cy-.124,.790,.13,.015,.20,"dark")
    hip(cx,cy+.014,1.089,.836,.715,.162,"erhaiRoof",trim="erhaiRoof",lift=.20)
    group("小普陀观音阁上层")
    box(cx,cy+.020,1.217,.38,.315,.253,"white")
    for x in (cx-.11,cx+.11):
        box(x,cy-.141,1.255,.074,.040,.124,"erhaiWood")
    box(cx,cy-.123,1.431,.412,.067,.040,"erhaiWood")
    hip(cx,cy+.016,1.449,.575,.525,.16,"erhaiRoof",trim="erhaiRoof",lift=.23)

    for i,(x,y,r) in enumerate(((cx-.43,cy+.17,.20),(cx+.42,cy+.20,.25),(cx-.30,cy-.15,.12),
                                (cx+.12,cy+.33,.19),(cx-.13,cy+.34,.15))):
        tree_shade(x,y,.56,r,seed=32+i)
    for i,y in enumerate((-1.52,-.99,-.65,-.21,.27,.76,1.18)):
        x=shore(y)-.44
        tree_shade(x,y,silhouette(x,y)-.04,.12+.042*(i%3),seed=82+i)
    for x,y,w,d in ((-2.66,-.61,.52,.37),(-2.41,.10,.45,.32),(-2.56,.76,.54,.33),(-2.30,1.19,.35,.29)):
        hut(x,y,silhouette(x,y)-.033,w,d,wall="white",roof="erhaiRoof",story=.20,tiles=.12)
    for i in range(19):
        y=-1.82+i*.147
        x=shore(y)+.02
        boulder(x,y,.351,.07,.094,.079,seed=19+i,mat="erhaiGrey",label="海印村岸边的护石")
    currents(62,(-1.82,2.77,-1.87,1.58),120,GROUND+.009,
             lambda x,y:silhouette(x,y)<.347 and hypot((x-cx)*.75,y-cy)>.54,material="erhaiRipple")
    group("短摆渡舟")
    floorplan(-.63,-.83,.369,[(-.19,0),(-.10,-.053),(.12,-.051),(.19,0),(.08,.052),(-.12,.050)],
              .057,"erhaiWood")
    box(-.65,-.823,.418,.126,.056,.047,"white")
