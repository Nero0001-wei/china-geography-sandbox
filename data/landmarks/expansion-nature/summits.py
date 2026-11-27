"""Volcanic crater, sedimentary pillars and mountain ridges."""
from shapes import (
    GROUND, base, boulder, box, conifer, cylinder, exp, face, forest,
    group, hut, hypot, noise, peak, pi, plank_line, Random,
    sin, cos, sqrt, stack, steps, surface,
)
from waters import REGULAR, TILE


def changbai():
    base("rockDark","basalt")
    n=84
    group("火山口与北坡")
    rings=[]
    for i in range(13):
        ring=[]
        for j in range(n):
            t=j*2*pi/n
            wave=.24*sin(5*t+.3)+.138*sin(9*t+.9)+.069*sin(17*t)
            h=.68+.44*sin(t+.64)+.25*cos(2*t-.21)+wave
            crest=1.26+max(0,h)
            outline=1+.060*sin(3*t+.23)+.043*cos(7*t)
            ratios=[.25,.48,.70,.88,.94,1.02,1.13,1.22,1.30,1.42,1.55,1.68,1.77]
            ridges=[.62,.62,.62,.62,.68,.95,crest,crest*.91,crest*.81,crest*.63,crest*.45,crest*.29,.37]
            erosion=.037*sin(11.0*t+.5*i)+.024*cos(20.2*t+.8*i) if 4<i<12 else 0
            rr=(ratios[i]+erosion)*outline
            shifts=0 if i<=4 else min(.13,(i-4)*.018)*sin(4*t+i*.58)
            ring.append((rr*1.56*cos(t+shifts),.04+rr*1.03*sin(t+shifts),ridges[i]+erosion))
        rings.append(ring)
    for i,(a,b) in enumerate(zip(rings,rings[1:])):
        for j in range(n):
            k=(j+1)%n
            crest=(a[j][2]+a[k][2]+b[j][2]+b[k][2])/4
            t=(j+.5)*2*pi/n
            if i<4:
                mat="craterBlue" if i<3 else "craterLight"
            elif i<6 and crest<.98:
                mat="rockDark"
            elif crest>1.08+.16*sin(t*13+i*.88)+.21*cos(t*3+i*.79):
                mat="snowShadow" if sin(t*15+i*.37)<-.52 else "snow"
            else:
                mat="basalt" if i<8 and sin(t*19+i*.6)<.1 else "scree" if i>9 else "granite"
            face([a[j],b[j],b[k],a[k]],mat)
    face(list(rings[0]),"craterBlue")
    group("火山外侧碎屑")
    for i in range(17):
        x=-2.63+(i%9)*.66
        y=-1.97+(i//9)*.32
        boulder(x,y,.36,.18,.12,.088,i+27,mat="basalt")
    # The lake ring is not extended beyond the rim, so the entrance stays open.
    group("北坡观景平台")
    box(-1.12,-.67,1.332,.24,.12,.032,"rock")
    box(-1.12,-.729,1.365,.24,.014,.06,"timber")


def wulingyuan():
    base("grass","sandstone")
    def terrain(x,y):
        return .365+.082*noise(x,y)+.28*peak(x,y,.3,1.72,2.65,.95,1)
    surface("袁家界底部谷地",TILE,30,24,terrain,lambda x,y,z:"grass" if z<.47 else "pine")
    columns=[(-2.39,.12,.41,.37,1.82),(-1.74,.21,.32,.24,1.47),(-1.95,1.22,.43,.31,2.64),
             (-1.02,.91,.32,.22,1.77),(-.41,.72,.52,.30,2.26),(.29,1.41,.54,.38,2.55),
             (.85,.94,.30,.28,1.98),(1.65,.88,.45,.34,2.76),(2.44,1.26,.38,.30,2.31),
             (2.05,-.32,.43,.25,1.77),(2.44,-.83,.35,.21,1.42),(-1.05,-.59,.32,.23,1.05),
             (1.08,-.23,.37,.24,1.38),(.15,-.23,.30,.23,2.91),(-2.49,-.91,.27,.28,1.20)]
    for i,(x,y,w,d,h) in enumerate(columns):
        z=terrain(x,y)-.07
        sway=.08*sin(11.1*i)
        def material(k,j):
            return "pine" if k>=6 or (k==5 and j%4==0) or (k==0 and j%3) else (
                   "cliffWarm" if j%3 else "sandstone" if k%2 else "scree")
        stack("乾坤柱和袁家界砂岩柱群",x,y,z,[(0,w*1.32,d*1.23,0,0),(.24*h,w*.98,d*.93,0,0),
            (.46*h,w*.71,d*.80,sway,.03),(.68*h,w*.78,d*.74,sway,.04),
            (.84*h,w*.69,d*.78,sway*1.6,.018),(.95*h,w*.75,d*.72,sway*1.45,.02),
            (h,w*.56,d*.54,sway*1.45,.02)], material,n=13,seed=i+20)
        conifer(x+sway*1.45,y+.02,z+h,.18,.072,41+i)
    forest(18,REGULAR,64,terrain,lambda x,y: all(hypot(x-a,y-b)>w*.79 for a,b,w,d,h in columns),
           min_size=.12,max_size=.36)


def emei():
    base("cliff","basalt")
    def hill(x,y):
        lead=peak(x,y,.15,.32,1.85,1.38,2.28,1.63)
        rocky=peak(x,y,-1.77,1.20,.71,1.16,1.09)+peak(x,y,2.13,1.14,.61,1.06,1.07)
        plunge=.46 if y<.04 and lead>.33 else 0
        return .36+max(0,lead+rocky-plunge)+min(1,(lead+rocky))*noise(x,y)*.10
    surface("峨眉金顶峰的裸露南崖",TILE,44,38,hill,lambda x,y,z:
            "cliff" if y<.08 and z>1.02 else "scree" if z>1.88 else "pine")
    forest(24,REGULAR,43,hill,lambda x,y: y>.70 or abs(x)>.98,min_size=.14,max_size=.35)
    x,y=.13,.35
    platform=2.64
    group("金顶白石台基和正面石级")
    box(x,y,platform-.63,1.17,.78,.64,"graniteLight")
    box(x,y,platform-.029,1.25,.85,.066,"white")
    steps(x,y-.63,platform-.43,.51,.52,.425,12,"white")
    hut(x,y+.06,platform+.038,.86,.59,wall="cinnabar",roof="gold",story=.25,tiles=.20)
    group("金顶四面像轮廓")
    for rx,h,z in [(.16,.052,platform+.038),(.13,.058,platform+.09),(.08,.19,platform+.148),
                    (.065,.075,platform+.338),(.041,.035,platform+.413)]:
        cylinder((x-.52,y-.30,z),(x-.52,y-.30,z+h),rx,rx*.70,"gold",12)


def yulong():
    base("snowShadow","basalt")
    def mountain(x,y):
        glacier=peak(x,y,-.28,-.52,.58,1.27,.74)
        main=peak(x,y,.39,.39,1.38,1.50,3.38,1.17)
        left=peak(x,y,-1.19,.74,.78,1.23,2.40,1.12)
        right=peak(x,y,1.74,.72,.86,1.18,2.68,1.04)
        shoulder=.25*peak(x,y,-2.02,.7,1.1,.9,2.2)
        m=max(main,left,right)+.26*max(0,(main+left+right)-max(main,left,right))
        dr=max(0,m+shoulder+glacier*.31-noise(x,y)*min(.31,m*.20))
        return .364+dr
    def mat(x,y,z):
        xx=-.28+.26*y
        snow=z>.80+.50*max(0,abs(x-xx)-.2)+.40*sin(x*4.1+y*.69)+.20*cos(y*5.1)
        if abs(x-xx)<.39 and -1.50<y<.92 and z>.71:
            return "glacier" if noise(x,y*1.31)<-.14 else "snowShadow"
        if snow:
            return "snow" if noise(x,y)>.10 or z>2.6 else "snowShadow"
        return "basalt" if z>1.13 else "scree" if noise(x,y)>.01 else "rock"
    surface("扇子陡山脊、碎岩与冰川",TILE,56,49,mountain,mat)
    forest(92,REGULAR,35,mountain,lambda x,y:y<-.95 and abs(x)>.57 and mountain(x,y)<.95,
           min_size=.13,max_size=.28)


def everest():
    base("scree","basalt")
    def north_face(x,y):
        # Distances to the sharp southeast and west ridge spurs deform the pyramid.
        dx=x-.58+.23*y
        dy=y-.31
        central=max(0,1-max(abs(dx)*.53,abs(dy)*.49,abs(dx+dy*.56)*.44))**1.61
        ridge=max(0,1-hypot((x+1.57)/1.67,(y-.54)/1.72))**1.21
        right=max(0,1-hypot((x-2.1)/1.12,(y-.94)/1.46))**1.27
        v=4.14*central+.96*ridge+1.10*right
        w=abs(sin(4.25*x+2.72*y))*sin(3.36*x-4.79*y)*.27
        return .367+max(0,v+min(1,v*.52)*w)
    def mat(x,y,z):
        gullies=sin((x-.58+.37*y)*7.7)+.39*sin(x*12-y*4.26)
        if z>3.58 or (z>1.42+.18*sin(y*5.31) and gullies>-.29):
            return "snow" if y>.05 or gullies>.29 else "snowShadow"
        if z>1.02:
            return "basalt" if gullies<-.47 else "granite"
        return "scree" if noise(x,y)<.25 else "stoneWarm"
    surface("绒布寺望珠峰金字塔形北壁",TILE,61,48,north_face,mat)
    for i in range(23):
        x,y=-2.66+(i%9)*.64,-1.93+(i//9)*.14
        boulder(x,y,max(.36,north_face(x,y)-.03),.13,.10,.09,42+i,mat="scree")


def huashan():
    base("scree","granite")
    def mountain(x,y):
        west=peak(x,y,-.91,.22,1.34,1.48,2.82,1.48)
        side=peak(x,y,1.72,1.36,.87,1.38,1.76,1.18)
        back=peak(x,y,-1.98,1.18,.87,1.19,.87,1.44)
        return .36+west+side+back+min(1,west*.64)*.12*noise(x,y)
    def mat(x,y,z):
        if z>1.31:
            return "graniteLight" if noise(x*.66,y)>.03 else "granite" if x>.0 else "cliff"
        return "pine" if (x>.0 and y<1.4) or noise(x,y)>.31 else "rock"
    surface("主峰花岗岩险壁",TILE,45,35,mountain,mat)
    forest(70,REGULAR,36,mountain,lambda x,y:y>-.15 and (mountain(x,y)<1.26 or x>1.56),
           min_size=.13,max_size=.38)
    group("鲫鱼背石脊与窄步道")
    path=[]
    for i in range(27):
        t=i/26
        x=-.93+2.39*t
        y=.31+1.57*t-.19*sin(2*pi*t)
        z=mountain(x,y)+.031
        path.append((x,y,z))
    for a,b in zip(path,path[1:]):
        face([(a[0]-.039,a[1],a[2]),(b[0]-.039,b[1],b[2]),(b[0]+.039,b[1],b[2]),(a[0]+.039,a[1],a[2])],"white")
    for side in (-1,1):
        plank_line("石脊铁链",[(x+side*.061,y,z+.047) for x,y,z in path],.011,"dark",4)
    hut(-.86,.29,mountain(-.86,.29)-.043,.34,.265,wall="cliff",story=.10,tiles=.12)


def shennongjia():
    base("pine","rockDark")
    def ridge(x,y):
        spine=1.08*sin(x*.77+.5)+.31
        back=1.68*exp(-((y-spine)/(.66+.28*(x+3)/6))**2)
        summit=peak(x,y,-.78,.26,.89,.77,.88)+peak(x,y,1.4,1.39,.83,.65,.55)
        return .36+(.62+.26*cos(x*.83))*back+summit+.06*noise(x,y)
    surface("神农顶绵长山脊和亚高山草甸",TILE,43,37,ridge,lambda x,y,z:
            "sage" if z>1.42 else "meadow" if z>.99 and noise(x,y)>.01 else
            "pineDark" if noise(x*.66,y*.9)>.22 else "pine")
    forest(37,REGULAR,67,ridge,lambda x,y:.48<ridge(x,y)<1.30,min_size=.16,max_size=.34)
    group("神农顶峰碑")
    x,y=-.72,.28
    z=ridge(x,y)
    box(x,y,z-.034,.32,.21,.072,"oldstone")
    box(x,y,z+.012,.185,.115,.34,"cliff")
    box(x,y-.062,z+.09,.088,.012,.095,"red")
    trail=[]
    for j in range(26):
        t=j/25
        x=-.76+2.74*t
        y=.32+1.04*sin(t*2.38)-.31*t
        trail.append((x,y,ridge(x,y)+.025))
    plank_line("穿行于缓脊的石道",trail,.026,"scree",4)


def fanjingshan():
    base("pine","rockDark")
    def hill(x,y):
        forms=peak(x,y,.04,.34,1.64,1.53,1.16)+peak(x,y,-2.09,1.33,.69,.78,.91)+peak(x,y,1.82,1.80,.80,.54,.83)
        return .36+forms+.09*noise(x,y)*min(1,forms)
    surface("梵净山周围森林与山肩",TILE,35,32,hill,
            lambda x,y,z:"cliff" if z>1.11 else "pineDark" if noise(x,y)>.27 else "pine")
    peaks=[(-.49,.32,2.42,-.04),(.49,.38,2.53,.015)]
    for i,(x,y,h,t) in enumerate(peaks):
        stack("红云金顶裂谷两侧岩柱",x,y,1.08,[(0,.69,.61,0,0),(.25,.65,.60,0,0),(.78,.60,.51,.03,0),
              (1.25,.44,.44,.06,0),(h-.35,.38,.31,.04,t),(h-.15,.37,.30,0,t),
              (h,.32,.24,0,t)],lambda k,j:"pine" if k<2 and j%4==0 else
             "scree" if k==2 and j%3 else "cliffWarm" if 1<k<5 else "rock",n=21,seed=20+i)
        hut(x,y+t,1.08+h-.006,.48,.36,wall="white",story=.13,tiles=.12)
    group("横跨裂缝的桥与两侧栏杆")
    box(0,.21,3.455,.57,.147,.057,"white")
    for yy in (.142,.277):
        box(0,yy,3.515,.57,.026,.054,"oldstone")
    forest(23,REGULAR,60,hill,lambda x,y:hypot(x,y-.30)>.9,min_size=.12,max_size=.33)
    # Visible uphill access stair scales the front-left rock pillar.
    points=[]
    for i in range(23):
        t=i/22
        x=-.55-.43*(1-t)+.10*sin(t*pi*4)
        y=-1.17+.95*t
        z=.97+2.50*t
        points.append((x,y,z))
    plank_line("攀岩折阶",points,.034,"oldstone",5)
