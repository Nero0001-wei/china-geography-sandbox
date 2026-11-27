"""Desert geomorphology, bedrock formations and the Alishan railway."""
from shapes import (
    GROUND, base, boulder, box, bush, conifer, currents, cylinder, exp,
    face, floorplan, forest, group, hut, hypot, noise, peak, pi,
    plank_line, Random, sin, cos, sqrt, stack, surface,
)
from waters import REGULAR, TILE


def dune(x,y,centre,rise,reverse=False):
    margin=centre+.35*sin(x*.79)+.13*sin(x*1.63)
    d=(y-margin)*(-1 if reverse else 1)
    a=1.24 if d>0 else .63
    return rise*exp(-(abs(d)/a)**1.48)


def crescent_lake():
    base("sand","desertSoil")
    def basin(x,y):
        d=dune(x,y,1.13,1.86)*(.62+.27*cos(x*.68+.80))
        d=max(d,dune(x,y,1.95,1.73,True)*(.73+.20*sin(x*.88-.41)))
        side=peak(x,y,2.50,-.12,.67,1.40,.78)+peak(x,y,-2.38,-.39,.65,1.3,.62)
        flat=.07+.025*sin(x*4.1+y*3.7)
        return .36+max(.02,d+side-.34)+flat
    surface("鸣沙山弧形沙脊",TILE,55,40,basin,lambda x,y,z:
            "creamSand" if noise(x*.75,y*.54)>.25 else "sand" if y>.2 else "goldSand")
    group("新月状湖盆的水体与苇岸")
    n=54
    for i in range(n):
        t,u=i/n,(i+1)/n
        def point(v,k,z):
            x=-1.56+2.98*v
            y=-.98+.57*(2*v-1)**2
            return (x,y+(k-.5)*.69*max(0,sin(pi*v))**.72,z)
        for j in range(6):
            mat="reed" if j in (0,5) else "yellowLakeShallow" if j in (1,4) else "yellowLake"
            h=.540 if j not in (0,5) else .539
            face([point(t,j/6,h),point(u,j/6,h),point(u,(j+1)/6,h),point(t,(j+1)/6,h)],mat)
    hut(.58,.19,basin(.58,.19),.52,.36,wall="ochre",roof="roof",story=.17,tiles=.16)
    hut(1.21,.31,basin(1.21,.31),.34,.28,wall="clay",roof="roof",story=.13,tiles=.12)
    for i in range(20):
        x=-1.55+i*.146
        y=-.69+.31*(x/1.5)**2
        bush(x,y,max(.51,basin(x,y)-.02),.060,i,greens=("reed","weed","sage"))


def xiangshawan():
    base("goldSand","desertSoil")
    def ridges(x,y):
        front=dune(x*.80,y,-.58,1.18,True)*(.58+.37*sin(x*.57+.81))
        high=dune(x*1.31+.4,y,.68,2.37)*(.75+.17*cos(x*.71-.46))
        back=dune(x*.58-2,y,1.76,2.02,True)*(.73+.24*sin(x*.75-1.4))
        return .36+max(.03,front,high,back)+.030*sin(x*6.6-y*8.7)
    def color(x,y,z):
        s=sin(13*y+2.8*x+cos(x*2.1))
        return "creamSand" if s>.84 else "goldSand" if y<-.1 else "sand"
    surface("库布齐沙漠的大沙脊和小波纹",TILE,62,49,ridges,color)
    group("沙脊驼队")
    for i in range(6):
        x=-1.47+i*.44
        y=-1.12+.071*i
        z=ridges(x,y)
        cylinder((x-.08,y,z+.094),(x+.09,y,z+.11),.055,.046,"camel",7)
        for xx in (-.045,.028):
            cylinder((x+xx,y,z+.081),(x+xx-.022,y,z+.158),.035,0,"camel",6)
        cylinder((x+.074,y,z+.098),(x+.15,y,z+.194),.026,.017,"camel",6)
        cylinder((x+.135,y,z+.192),(x+.17,y,z+.195),.024,.012,"soil",6)
        for dx in (-.050,.061):
            for dy in (-.025,.023):
                cylinder((x+dx,y+dy,z+.08),(x+dx-.023,y+dy,z-.012),.012,.009,"soil",5)


def shapotou():
    base("riverBlue","siltriver")
    def banks(x,y):
        river=-.96+.30*sin(x*.75)+.31*x*x/9
        realbank=max(0,y-river)
        gradual=min(.30,realbank*.47)
        duneheight=dune(x*.8,y,1.38,2.7)*(.73+.14*cos(x*.68+.3)) if realbank>.46 else 0
        return .315+gradual+max(0,duneheight-.09)+.015*noise(x,y)
    surface("黄河弯道上方的腾格里沙陡坡",TILE,58,45,banks,lambda x,y,z:
            "reed" if z<.635 else "grassLight" if -.19<y<.05 and z<.76 else
            "goldSand" if z>1.21 and sin(x*3.2-y*5.5)>.32 else "sand")
    currents(84,(-2.80,2.80,-1.94,-.80),79,.369,lambda x,y:banks(x,y)<.349,material="glacialRipple")
    # Twelve sheep's bladders under a small timber raft are visible at close zoom.
    group("黄河羊皮筏子")
    cx,cy=.24,-1.43
    for i in range(3):
        for j in range(4):
            x,y=cx+(i-1)*.12,cy+(j-1.5)*.098
            cylinder((x-.045,y,.397),(x+.045,y,.397),.039,.032,"clay",7)
    for j in range(5):
        yy=cy+(j-2)*.068
        cylinder((cx-.17,yy,.435),(cx+.17,yy,.435),.012,.012,"timber",5)
    for i in range(24):
        x=-2.58+i*.214
        y=-.27+.32*sin(x*.75)+x*x*.029
        bush(x,y,banks(x,y),.076,seed=32+i,greens=("meadow","reed","sage"))


def wulong():
    base("pine","rockDark")
    def canyon(x,y):
        wall=min(1,max(0,(abs(x)-1.02)*.67))
        spires=peak(x,y,-2.41,1.24,.66,1.08,.87)+peak(x,y,2.48,.75,.58,1.1,1.01)
        return .363+wall*(1.45+noise(x,y)*.18)+spires
    surface("武隆钙岩天坑与峡谷底面",TILE,41,34,canyon,lambda x,y,z:
            "pine" if z<.8 or y>1.4 else "rockDark" if noise(x,y)>.22 else "cliff")
    group("天龙桥实体岩拱与真实洞孔")
    front,back=-.36,.72
    n=38
    layers=[(front,1.00),(front+.17,.98),(.18,1.13),(back-.14,1.03),(back,.97)]
    outside=[]
    inside=[]
    for d,(y,q) in enumerate(layers):
        inring=[]
        outring=[]
        for j in range(n+1):
            t=j*pi/n
            ripple=.09*sin(t*5.7+.51*d)+.055*cos(t*16.2+.65*d)
            inring.append((1.38*q*cos(t)+.13*sin(2*t),y+.033*sin(5*t),.38+(1.83+ripple)*sin(t)))
            outring.append(((1.38+.52+q*.16)*cos(t),y+.073*cos(5*t),.38+(2.77+ripple+q*.17)*sin(t)))
        outside.append(outring)
        inside.append(inring)
    for ring in (0,len(layers)-1):
        lo,hi=inside[ring],outside[ring]
        for j in range(n):
            quad=[lo[j],lo[j+1],hi[j+1],hi[j]]
            face(quad[::-1] if ring==0 else quad,"cliff" if j%8 in (1,3,6) else "rock")
    for a,b in zip(outside,outside[1:]):
        for j in range(n):
            face([a[j],b[j],b[j+1],a[j+1]],"pine" if j%5 else "rock")
    for a,b in zip(inside,inside[1:]):
        for j in range(n):
            face([a[j],a[j+1],b[j+1],b[j]],"cliff" if j%3 else "rockDark")
    hut(.29,-.82,.402,.65,.52,wall="clay",roof="roof",story=.19,tiles=.19)
    hut(.62,-.64,.402,.33,.36,wall="timber",roof="roof",story=.12,tiles=.13)
    forest(19,REGULAR,55,canyon,lambda x,y:abs(x)>1.72 or (y<-.35 and x<-1),min_size=.11,max_size=.35)
    for i in range(15):
        t=i*pi/14
        x=(1.93)*cos(t)
        z=.36+(2.78)*sin(t)
        conifer(x,.31,z,.21+(i%3)*.054,.079,31+i)


def stone_forest():
    base("stoneWarm","basalt")
    def hills(x,y):
        return .371+.072*(noise(x,y)+1)+peak(x,y,-.95,1.7,1.9,.72,.49)
    surface("石林区风化基底与青苔地面",TILE,31,27,hills,lambda x,y,z:
            "scree" if abs(x)>.95 and noise(x,y)>.20 else "grass" if z<.42 else "sage")
    positions=[(0,-.11,.41,.25,2.21),(-.67,-.36,.23,.19,1.27),(.58,.01,.26,.21,1.51),
               (-.79,.59,.37,.27,1.89),(.71,.76,.36,.25,2.04),(-1.48,.67,.36,.25,2.71),
               (-1.17,-.55,.24,.27,1.15),(-1.99,-.67,.23,.28,1.61),(-2.35,.31,.36,.33,2.46),
               (-2.43,1.26,.44,.35,2.94),(1.37,.23,.34,.23,2.36),(1.87,.46,.29,.30,2.13),
               (2.32,-.02,.26,.43,2.10),(2.42,.74,.37,.31,2.72),(1.59,1.32,.43,.43,2.44),
               (.55,1.46,.46,.32,2.57),(-.43,1.44,.39,.29,2.51)]
    for i,(x,y,w,d,h) in enumerate(positions):
        sway=.12*sin(i*3.62+.8)
        if i==0:
            rings=[(0,w*1.26,d*1.29,0,0),(.26*h,w,d,0,0),(.56*h,w*.72,d*.71,.06,0),
                   (.71*h,w*.82,d*.73,.13,.01),(.84*h,w*.61,d*.64,.22,-.02),
                   (.92*h,w*.77,d*.69,.27,-.04),(h,w*.32,d*.49,.27,-.04)]
        else:
            rings=[(0,w*1.25,d*1.13,0,0),(.24*h,w*.98,d*.94,0,0),(.58*h,w*.84,d*.77,sway,0),
                   (.79*h,w*.73,d*.51,sway*1.9,0),(h,w*.21,d*.28,sway*2.5,.083*sin(i))]
        stack("阿诗玛主峰" if i==0 else "小石林灰岩剑峰",x,y,hills(x,y)-.055,rings,
              lambda k,j:"graniteLight" if k>=3 and j%5 in (0,2) else "granite" if j%3 else
              "rockDark" if k>0 else "sage",n=9,seed=i+3)
    for i in range(21):
        x=-2.73+(i%10)*.56
        y=-1.78+(i//10)*.37
        boulder(x,y,hills(x,y),.12+.044*(i%3),.13,.14+.074*(i%3),40+i)
    forest(16,REGULAR,28,hills,lambda x,y:y<-1.1 or y>1.62,woodland="broad",min_size=.15,max_size=.25)


def zhangye_danxia():
    base("clayDark","desertSoil")
    ridges=[(-2.21,.2,.82,.58,1.06),(-1.45,1.39,.78,.63,1.58),(-.90,.16,.77,.72,1.50),(.02,1.24,.94,.65,1.98),
            (.79,.37,.78,.65,1.52),(1.55,1.53,.82,.57,1.82),(2.06,.28,.68,.72,1.57),(2.55,1.23,.48,.63,1.50)]
    def hills(x,y):
        weights=[peak(x,y,*r,1.04) for r in ridges]
        erosion=abs(sin(8.83*x+5.45*y))*max(weights)*.15
        return .36+max(weights)*.91+.21*sum(weights)-erosion+.038*noise(x,y)
    bands=("danxiaOchre","danxiaRust","danxiaRed","danxiaCream","danxiaPurple","danxiaRust",
           "danxiaCream","danxiaOchre","danxiaWine","danxiaRed","danxiaPurple")
    def mat(x,y,z):
        layer=(z-.244*x+.19*y+.085*sin(.91*x+.64*y)+.08*sin(x*3.51+y*.18))*8.15
        # Different slopes expose the same tilted layers, not a repeated rainbow decal.
        return bands[int(layer)%len(bands)]
    surface("受剥蚀的倾斜多色沉积岩山岭",TILE,63,52,hills,mat)
    group("沿沟谷短木栈道")
    for j in range(10):
        s=j/9
        x=-1.73+3.6*s
        y=-1.57+.29*sin(s*3.14)
        z=hills(x,y)
        box(x,y,z+.007,.39,.059,.018,"timber")


def alishan():
    base("pine","rockDark")
    def floor(x,y):
        cut=peak(x,y,-1.6,1.62,.99,.61,1.51)+peak(x,y,.0,1.64,1.32,.59,1.04)+peak(x,y,2.51,.94,.63,1.48,1.17)
        return .37+cut+.11*noise(x,y)*min(1,cut)
    surface("阿里山林场坡地",TILE,38,32,floor,lambda x,y,z:
            "pineDark" if y>1.0 else "meadow" if noise(x,y)<-.25 else "pine")
    forest(82,REGULAR,74,floor,lambda x,y:y>.66 or (abs(x)>2.19 and y>-.5),min_size=.24,max_size=.72)
    def track(s,offset=0):
        x=-2.67+5.35*s
        y=-1.18+.86*s*s+.071*sin(pi*s)+offset
        return x,y,max(.41,floor(x,y)+.031)
    for off in (-.106,.106):
        plank_line("阿里山林业铁路窄轨", [track(j/28,off) for j in range(29)],.012,"dark",5)
    for i in range(32):
        x,y,z=track(i/31)
        group("铁路枕木")
        box(x,y,z-.028,.041,.30,.028,"timber")
    hut(-1.22,-.56,floor(-1.22,-.56),.83,.58,wall="white",roof="roof",story=.21,tiles=.17)
    group("沼平车站平台")
    box(-1.14,-.90,.399,1.34,.28,.055,"granite")
    cars=[(-.60,-.97,.74,.27),(.20,-.895,.68,.26),(.93,-.814,.66,.26),(1.56,-.72,.52,.245)]
    for i,(x,y,l,w) in enumerate(cars):
        z=floor(x,y)+.055
        group("森林铁路红色列车")
        box(x,y,z+.030,l,w,.258,"trainRed")
        roof=[(-l*.5,-w*.45),(l*.5,-w*.45),(l*.5,w*.45),(-l*.5,w*.45)]
        floorplan(x,y,z+.282,roof,.048,"dark")
        box(x,y-w/2-.008,z+.131,l,.014,.070,"creamSand")
        for j in range(5):
            xx=x+(j-2)*l*.173
            box(xx,y-w/2-.018,z+.147,l*.105,.013,.054,"basalt")
        for side in (-1,1):
            for xx in (x-l*.28,x+l*.28):
                cylinder((xx,y+side*w*.42,z+.043),(xx,y+side*w*.53,z+.043),.048,.048,"dark",9)
