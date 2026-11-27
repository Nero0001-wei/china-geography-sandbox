"""River bends, lakes, waterfalls and coastline dioramas."""
from shapes import (
    GROUND, PARTS, base, boulder, box, bush, conifer, currents, cylinder, exp, face,
    falling_water, floorplan, forest, group, hut, hypot, noise, peak, pi, Random,
    palm, project_strokes, ribbon, sin, cos, sqrt, stack, surface, tree_shade,
)

TILE=(-2.97,2.97,-2.04,2.04)
REGULAR=(-2.82,2.82,-1.97,1.97)


def hulunbuir():
    base("grass","soil")
    river=lambda y:.85*sin(2.34*y+.23)+.29*sin(4.18*y-.52)
    def relief(x,y):
        dist=abs(x-river(y))
        slope=min(1,max(0,(dist-.2)*2))
        return GROUND+.035+slope*(.067+.074*noise(x,y)+peak(x,y,2.2,1.45,1.4,1.5,.34)
                                                  +peak(x,y,-2.25,.8,1.4,1.7,.22))
    surface("莫尔格勒河草原缓坡",TILE,37,35,relief,lambda x,y,z:
            ("sage" if z>.62 else "grassLight" if noise(x*.7,y)>.16 else "grass"))
    ribbon("反复回转的河曲",lambda t:(river(4.05*t-2.025),4.05*t-2.025),.36,.420,
           lambda i,j:"waterLight" if j in (0,4) else "riverBlue",segments=72,bands=5)
    rng=Random(47)
    for i in range(25):
        x=rng.choice((-1,1))*rng.uniform(1.5,2.66)
        y=rng.uniform(-1.7,1.85)
        if abs(x-river(y)) < .55:
            continue
        z=relief(x,y)
        group("草场上的牛马点缀")
        mat=("camel","soil","white","dark")[i%4]
        cylinder((x-.04,y,z+.027),(x+.08,y,z+.03),.027,.022,mat,5)
        cylinder((x+.06,y,z+.03),(x+.10,y,z+.05),.018,.011,mat,5)


def yangshuo():
    base("jade","siltriver")
    def river(y):
        return -.40+.54*sin(1.24*y+.46)
    towers=[(-2.21,-1.52,.49,.50,.76),(-2.31,-.72,.39,.54,1.25),(-1.77,-.45,.32,.38,.79),
            (-2.34,.44,.41,.6,1.59),(-1.77,.94,.49,.58,1.14),(-1.31,1.50,.37,.40,1.28),
            (-2.52,1.48,.43,.52,1.74),(1.97,-1.35,.47,.40,1.01),(2.40,-.63,.36,.45,1.52),
            (1.75,.21,.38,.52,1.68),(2.44,.55,.38,.44,1.91),(2.31,1.63,.49,.32,1.60),
            (1.48,1.53,.35,.49,1.16),(.75,1.72,.4,.39,.87)]
    def height(x,y):
        side=abs(x-river(y))
        if side<.82:
            return GROUND-.017
        ground=min(.24,(side-.82)*.51)
        summits=[peak(x,y,a,b,c,d,h,1.34) for a,b,c,d,h in towers]
        return .363+ground+max(summits)+.38*sum(sorted(summits,reverse=True)[1:4])+.045*noise(x,y)
    surface("兴坪两岸锥状喀斯特峰丛",TILE,42,38,height,
            lambda x,y,z: "jade" if abs(x-river(y))<.82 else
            ("cliff" if z>1.03 and noise(x,y)>.40 else "pine" if z>.85 else
            "sand" if z<.470 else "grass"))
    for i in range(26):
        y=-1.82+(i%13)*.29
        x=river(y)+(-1 if i<13 else 1)*(.86+(i%3)*.078)
        tree_shade(x,y,height(x,y),.10+.012*(i%3),25+i)
    currents(5,(-1.1,.7,-1.94,1.84),42,.371,lambda x,y:abs(x-river(y))<.75,material="jadeRipple")
    group("漓江竹筏")
    for offset in (-.06,-.03,0,.03,.06):
        cylinder((-.18+offset,-.95,.393),(.25+offset,-1.24,.393),.013,.013,"reed",5)
    box(.022,-1.09,.40,.13,.082,.047,"timber")


def kanas():
    base("pine","rockDark")
    river=lambda y: .82*sin(y*1.42-.40)+.22*sin(y*3.1)
    def hill(x,y):
        d=abs(x-river(y))
        s=max(0,d-.41)
        return GROUND+.035+min(1,s*.7)*(.26+.28*sin(y*.8+.27)+
               peak(x,y,-2.1,1.4,2,1.2,1.16)+peak(x,y,2.4,.1,1.8,1.8,.78)+.15*noise(x,y))
    surface("月亮湾连续曲流与松林山坡",TILE,39,35,hill,lambda x,y,z:
            "sand" if z<.495 else "pineDark" if noise(x*.8,y*1.1)>.30 else "pine")
    ribbon("喀纳斯河月亮湾",lambda t:(river(4.04*t-2.02),4.04*t-2.02),
           lambda t:.57+.23*exp(-((t-.48)/.27)**2),.438,lambda i,j:
           "waterLight" if j in (0,4) else "glacial",segments=64,bands=5)
    forest(44,REGULAR,87,hill,lambda x,y:abs(x-river(y))>.48,min_size=.13,max_size=.42)
    currents(67,(-1.05,1.13,-1.88,1.86),30,.447,lambda x,y:abs(x-river(y))<.25,material="glacialRipple")


def qinghai_lake():
    base("lakeBlue","deepwater")
    def peninsula(x,y):
        neck=.27+.48*exp(-((y-1.85)/1.02)**2)
        cx=-1.16+.69*(1.72-y)/2.81+.12*sin(y*2.0)
        return max(0,neck-abs(x-cx))*max(0,1-(abs(y-1.81)/3.05)**6)
    def land(x,y):
        v=peninsula(x,y)
        distance=peak(x,y,-2.26,1.94,1.21,.24,.36)+peak(x,y,.58,1.96,1.5,.30,.44)
        distance+=peak(x,y,2.69,1.95,.65,.23,.35)
        return GROUND-.037+min(.28,v*1.1)+(.17 if y>1.45 and x<-.92 else 0)*v+distance
    surface("二郎剑狭长沙嘴",TILE,48,40,land,lambda x,y,z:
            "granite" if y>1.68 and z>.65 else "reed" if .366<=z<.415 else "meadow" if noise(x,y)>.15 else "sage")
    currents(57,(-2.78,2.84,-1.90,1.90),100,.367,lambda x,y:land(x,y)<.352,material="ripple")
    for x,y,h in [(-1.05,1.48,.11),(-.83,1.19,.10),(-.71,.99,.081),(-.62,.81,.08)]:
        bush(x,y,land(x,y)-.025,.072,21,greens=("meadow","reed","sage"))
    group("窄堤和浅水岸线")
    ribbon("二郎剑步道",lambda t:(-1.12+.54*t,1.90-t*2.29),.037,.43,"sand",segments=21,bands=1)


def sun_moon_lake():
    base("jade","siltriver")
    peaks=[(-2.3,1.33,1.1,.65,1.28),(-1.06,1.72,.9,.55,1.11),(.23,1.82,1.11,.54,1.28),
           (1.56,1.61,1.0,.64,1.27),(2.43,.69,.49,1.27,1.17),(-2.67,.36,.46,1.26,1.11),
           (-2.36,-1.46,.65,.70,.59),(2.72,-1.60,.60,.54,.55)]
    def relief(x,y):
        hills=[peak(x,y,*data,1.17) for data in peaks]
        return .23 + max(hills)+.23*sum(hills)+.056*noise(x,y)
    surface("湖盆与弧形的树林山岸",TILE,44,36,relief,lambda x,y,z:
            "sand" if z<.432 else "grassLight" if noise(x,y)<-.24 else "pineLight")
    def island(x,y):
        return .30+peak(x,y,.36,-.02,.58,.31,.30,1.2)
    surface("湖心拉鲁岛",(-.35,1.05,-.52,.49),18,12,island,
            lambda x,y,z:"sand" if z<.438 else ("grass" if x<.44 else "leaf"))
    forest(39,REGULAR,34,relief,lambda x,y:relief(x,y)>.52,woodland="broad",min_size=.16,max_size=.33)
    for j in range(6):
        x=.12+.078*j
        y=-.05+.07*sin(j)
        tree_shade(x,y,island(x,y),.095,5+j)
    currents(33,(-2.82,2.81,-1.91,1.59),83,.370,
             lambda x,y:max(relief(x,y),island(x,y))<.350,material="jadeRipple")
    group("湖畔码头与游船")
    box(-2.1,-.95,.366,.57,.083,.039,"timber")
    floorplan(-1.06,-.88,.36,[(-.20,-.055),(.13,-.055),(.22,0),(.13,.055),(-.20,.055)],.047,"white")
    box(-1.10,-.88,.402,.21,.083,.061,"roof")


def wuyishan():
    base("jade","siltriver")
    def river(y):
        return -.27+.89*sin(y*1.34+.51)
    def hill(x,y):
        d=abs(x-river(y))
        return .322+max(0,d-.75)*(.094+.13*peak(x,y,-2.35,1.2,1,1.6,.8))
    surface("九曲溪河岸",TILE,38,32,hill,lambda x,y,z:
            "jade" if z<GROUND else "weed" if z<.455 else "pine")
    def rock(i,j):
        return "pine" if (i>=5 or (i==0 and j%2)) else ("wuyiRed" if j%3==0 else "wuyiStone")
    stack("九曲溪旁玉女峰",.98,.33,GROUND,[(0,.66,.73,0,0),(.20,.54,.67,0,0),
          (.79,.41,.51,-.06,0),(1.38,.31,.39,-.11,.05),(1.93,.30,.29,-.12,.08),
          (2.1,.27,.24,-.15,.10),(2.15,.17,.13,-.15,.11)],rock,n=21,seed=32)
    stack("近岸成层红砂岩山壁",-2.4,1.37,.445,[(0,.55,.63,0,0),(.27,.76,.60,0,0),
          (.83,.72,.60,.05,0),(1.10,.65,.53,-.03,0),(1.38,.44,.50,0,0)],rock,n=17,seed=28)
    forest(84,REGULAR,39,hill,lambda x,y:hill(x,y)>.425,woodland="broad",min_size=.11,max_size=.26)
    currents(34,(-1.46,1.5,-1.9,1.84),54,.366,lambda x,y:abs(x-river(y))<.66,material="jadeRipple")
    for i in range(3):
        group("九曲溪小竹筏")
        y=-1.46+i*.68
        x=river(y)
        for j in range(5):
            off=(j-2)*.032
            cylinder((x+off-.18,y-.12,.382),(x+off+.13,y+.12,.384),.013,.011,"reed",5)
        box(x-.053,y-.002,.388,.075,.077,.054,"timber")


def lushan():
    base("rockDark","soil")
    def hill(x,y):
        walls=.83+peak(x,y,-2.12,.07,1.40,3.5,1.48)+peak(x,y,2.25,.57,1.25,3.8,1.63)
        canyon=exp(-((x-.09+.11*y)/.68)**2*2)
        return .348 + (walls*.91+.12*noise(x,y))*(1-canyon)*(.53+.19*(y+2))
    surface("三叠泉谷两侧的高陡山壁",TILE,42,34,hill,lambda x,y,z:
            "rockDark" if z>.64 and abs(x-.09+.11*y)<.95 else "rock" if noise(x,y)>.40 else "pine")
    terraces=[(-.14,1.21,1.34,.62,.61),(0,.55,.92,.68,.41),(.18,-.12,.43,.90,.49)]
    for i,(x,y,z,w,drop) in enumerate(terraces):
        stack("瀑布下层岩坎",x,y+.43,.36,[(0,w*.7,.47,0,0),(z+drop-.50,w*.70,.50,0,0),
                (z+drop-.37,w*.70,.47,0,0)],"rockDark",n=16,seed=i+5)
        falling_water("三叠泉第%d叠"%(i+1),x,y,z,w,drop,17+i,folds=14,arch=.21)
        stack("潭面",x,y-.42,z-.018,[(0,w*.68,.33,0,0),(.015,w*.68,.33,0,0)],"glacial",n=20)
    forest(32,REGULAR,52,hill,lambda x,y:abs(x-.09+.11*y)>1.08,min_size=.12,max_size=.31)
    for i in range(11):
        x=(-1 if i%2 else 1)*(.67+i*.103)
        y=-1.81+(i%6)*.34
        boulder(x,y,hill(x,y),.18,.17,.20,i+5)


def huangguoshu():
    base("jade","reed")
    def hill(x,y):
        wall=min(1,max(0,(y-.20)*1.42))
        return .30+wall*(1.38+.065*noise(x,y))+peak(x,y,2.52,.22,.52,1.46,1.01)+peak(x,y,-2.43,.14,.50,1.42,.98)
    surface("宽阔钙华台地和犀牛潭岸",TILE,43,34,hill,lambda x,y,z:
            "jade" if z<GROUND else "rockDark" if y<1.0 and z>.72 else "pine")
    def rock(i,j):
        if i==1:
            return "rockDark"
        return "rock" if j%4 else "cliff"
    stack("主瀑崖面和水帘洞檐",0,.80,.37,[(0,1.58,.35,0,0),(.41,1.57,.32,0,.065),
          (.92,1.63,.29,0,.11),(1.18,1.67,.40,0,.01),(1.29,1.70,.46,0,0)],rock,n=26,seed=73)
    falling_water("黄果树弧形主瀑",0,.41,.37,3.21,1.24,43,arch=.23,folds=41)
    forest(55,REGULAR,39,hill,lambda x,y: y>1.02 or (abs(x)>2.28 and y>-.42),woodland="broad",
           min_size=.17,max_size=.43)
    currents(83,(-2.53,2.53,-1.88,-.26),53,.369,lambda x,y: hill(x,y)<.35,material="glacialRipple")


def detian():
    base("jade","siltriver")
    def hill(x,y):
        back=min(1,max(0,(y-.12)*.95))
        east=peak(x,y,2.44,1.19,.86,.99,1.15)
        west=peak(x,y,-2.56,1.64,.60,.65,.91)
        return .338+back*(.77+.07*noise(x,y))+east+west
    surface("归春河中国侧喀斯特台地",TILE,38,34,hill,lambda x,y,z:
            "jade" if z<.39 else "grass" if z<.73 else "pine")
    for i,(x,y,z,w,drop) in enumerate(((-.31,.95,.64,2.90,.55),(.04,.26,.38,3.73,.54),(1.55,-.25,.37,.86,.29))):
        stack("多台阶瀑岸岩层",x,y+.34,.36,[(0,w*.49,.28,0,0),(z+drop-.41,w*.52,.35,0,0),
              (z+drop-.35,w*.50,.36,0,0)],lambda l,j:"rockDark" if j%3==0 else "rock",n=20,seed=42+i)
        layer="三级瀑流水帘 %s"%(i+1)
        falling_water(layer,x,y,z,w,drop,76+i,arch=.13,folds=23)
    forest(56,REGULAR,50,hill,lambda x,y:y>1.23 or (abs(x)>2.42 and y>.03),min_size=.13,max_size=.34)
    currents(12,(-2.47,2.52,-1.94,-.35),59,.369,lambda x,y:hill(x,y)<.352,material="jadeRipple")
    group("归春河观瀑小筏")
    for k in range(5):
        cylinder((-1.06+k*.028,-.95,.38),(-.81+k*.028,-.87,.384),.010,.01,"reed",5)


def tianyahaijiao():
    base("deepwater","ochre")
    def beach(x,y):
        shore=-.67+.46*sin(x*.61)+.13*sin(x*1.39)
        return .29+min(.23,max(0,(y-shore)*.21))+.029*noise(x,y)
    surface("题刻石组的沙滩与海缘",TILE,38,32,beach,
            lambda x,y,z:"foam" if z<.405 else "creamSand" if z<.480 else "sand")
    locations=[(-.80,.41,.93,.69,1.67),(.61,.63,.70,.60,1.22),
               (1.49,.57,.66,.59,.69),(-1.74,.74,.66,.65,.64),(-.19,1.37,.81,.58,.69)]
    label="海蚀花岗岩题刻石组"
    engraved=[]
    for i,(x,y,w,d,h) in enumerate(locations):
        offset=len(PARTS.get(label,[]))
        stack(label,x,y,beach(x,y),[(0,w*.8,d*.78,0,0),(.15*h,w,d,.0,0),
              (.63*h,w*.78,d*.78,.06,-.03),(.88*h,w*.58,d*.62,.079,-.005),
              (h,w*.19,d*.37,.13,0)],lambda k,j:"stoneWarm" if j%5==0 else
              "coastalGranite" if k%3 else "coastalShale",n=14,seed=71+i)
        if i<2:
            engraved.append(PARTS[label][offset:])
    sky=[[(-.43,.32),(.37,.37)],[(-.47,.05),(.46,.09)],[(.02,.40),(-.06,.0),(-.27,-.24),(-.49,-.39)],
         [(.04,.015),(.23,-.24),(.49,-.39)]]
    water_radical=[[(-.47,.33),(-.34,.23)],[(-.47,.12),(-.36,.02)],[(-.47,-.28),(-.33,-.12)]]
    cliff=water_radical+[[(-.17,.38),(.46,.39)],[(-.17,.38),(-.17,-.07),(-.27,-.36)],
          [(-.07,.21),(.39,.22)],[(.17,.32),(.17,.02)],[(-.08,.01),(.46,.02)],
          [(-.07,-.16),(.38,-.16)],[(.16,-.05),(.16,-.34)],[(-.11,-.32),(.46,-.31)]]
    sea=water_radical+[[(-.18,.29),(.45,.32)],[(-.09,.44),(-.21,.23)],[(-.17,.12),(.35,.13),
          (.31,-.39),(.19,-.43)],[(-.06,.13),(-.12,-.26),(.43,-.25)],[(-.24,-.06),(.46,-.04)],
          [(.081,.051),(.17,-.006)],[(.074,-.15),(.16,-.22)]]
    corner=[[(.073,.43),(-.25,.22)],[(.0,.35),(.33,.35),(.18,.19)],
            [(-.25,.17),(.32,.18),(.32,-.39),(.15,-.36)],[(-.24,.17),(-.24,-.19),(-.38,-.39)],
            [(-.25,-.005),(.29,.0)],[(-.24,-.17),(.27,-.17)],[(.04,.17),(.04,-.31)]]
    for patch,x,z,size,char in [(0,-1.04,1.60,.235,sky),(0,-.76,1.59,.235,cliff),
                                  (1,.46,1.23,.18,sea),(1,.67,1.22,.18,corner)]:
        project_strokes(engraved[patch],x,z,size,char)
    forest(12,REGULAR,29,beach,lambda x,y:y>1.29,woodland="broad",min_size=.17,max_size=.42)
    for i,(x,y,h) in enumerate([(-2.44,1.23,.82),(-1.76,1.53,.73),(-1.38,1.83,1.12),
                                  (1.52,1.28,.91),(2.11,1.46,1.12),(2.65,1.29,.85)]):
        palm(x,y,beach(x,y),h,23+i)
    currents(32,(-2.81,2.80,-1.91,.04),74,.368,lambda x,y:beach(x,y)<.35,material="surfRipple")
