"""Site-specific sculptures. Front is -Y; X=Y=0 is the surveyed subject."""
from geometry import *

def buddha(x,y,z,s,seated=False):
    def el(n,p,r,matkey='limestone',nu=12,nv=8):
        return ellipse(n,(x+s*p[0],y+s*p[1],z+s*p[2]),tuple(s*v for v in r),matkey,nu,nv)
    def stroke(name,pts,r=.025):
        return tube(name,[(x+s*a,y+s*b,z+s*c) for a,b,c in pts],r*s,'limestone',6)
    if seated:
        stack('八棱佛座',x,y,[(1.27*s,.76*s,z),(1.22*s,.74*s,z+.18*s),(1.09*s,.66*s,z+.28*s)],'oldstone',12)
        el('盘坐膝部',(0,-.06,.49),(1.04,.65,.36))
        torsoz=1.19
        for i in range(6):
            a=.51+i*.09
            stroke('衣褶',[(-a,-.46,-.02+.53+i*.07),(-.52*a,-.60,.42+i*.045),(0,-.66,.40+i*.041),(.6*a,-.57,.43+i*.047),(a,-.39,.52+i*.077)],.018)
    else:
        el('垂裳',(0,.02,.60),(.44,.275,.61));torsoz=1.21
        for sign in [-1,1]:el('足',(sign*.17,-.1,.10),(.16,.23,.10))
    el('躯干',(0,0,torsoz),(.67 if seated else .48,.35,.70))
    for sign in [-1,1]:
        el('袖臂',(sign*(.53 if seated else .40),-.035,torsoz-.15),(.19,.23,.46))
        el('手',(sign*(.60 if seated else .43),-.18,torsoz-.50),(.11,.15,.17))
    for i in range(4):stroke('袈裟胸前衣纹',[(-.46,-.17,1.71-i*.04),(-.22,-.32,1.53-i*.05),(0,-.355,1.43-i*.055),(.23,-.31,1.49-i*.04),(.41,-.21,1.63-i*.03)],.012)
    el('颈',(0,0,1.86),(.19,.18,.23))
    el('颊与额',(0,-.035,2.09),(.31,.275,.36),'limestone',20,14)
    el('发冠',(0,.005,2.31),(.31,.248,.20),'sandstone')
    el('高髻',(0,.035,2.48),(.17,.16,.12),'sandstone')
    for sign in [-1,1]:
        el('长耳',(sign*.30,-.005,2.08),(.066,.079,.15))
        stroke('眉弓',[(sign*.047,-.291,2.19),(sign*.13,-.291,2.20),(sign*.213,-.238,2.175)],.021)
        stroke('眼睑',[(sign*.055,-.294,2.126),(sign*.125,-.291,2.104),(sign*.20,-.254,2.128)],.012)
    el('鼻梁',(0,-.301,2.08),(.047,.056,.11))
    el('唇',(0,-.278,1.982),(.091,.029,.022))
    el('下颌',(0,-.200,1.920),(.151,.085,.09))

def longmen():
    group('01 · 露天石窟');island('洞窟前地',0,-.1,3.55,1.54,.24,'oldstone',26)
    # Layered open horseshoe-shaped rock wall; back face, crown and flanks retain the excavation.
    n=35;rows=[]
    for lvl,(radius,h) in enumerate([(3.25,.13),(3.2,.77),(3.12,1.9),(3.17,3.21),(3.20,3.54)]):
        row=[]
        for j in range(n):
            a=PI*j/(n-1);X=radius*math.cos(a);Y=-.85+2.15*math.sin(a)
            zz=h*(.57+.43*math.sin(a))+.08*math.sin(6*a+.4)
            row.append((X+.045*math.sin(j*8+lvl),Y+.08*math.cos(j*2+lvl),max(.05,zz)))
        rows.append(row)
    v=[v for row in rows for v in row];f=[]
    for k in range(4):
        for j in range(n-1):
            a=k*n+j;f+=[(a+1,a,a+n),(a+1,a+n,a+1+n)]
    o=len(v)
    for x,y,z in rows[-1]:v.extend([(x*1.03,y+.53,z+.15),(x*1.04,y+.66,.1)])
    for j in range(n-1):
        a=4*n+j;b=o+2*j;f.extend([(a,a+1,b+2,b),(b,b+2,b+3,b+1)])
    mesh('石窟弧壁与凿痕',v,f,'cliff')
    group('02 · 卢舍那与胁侍')
    buddha(0,0,.23,1.30,True)
    for sign in [-1,1]:
        buddha(sign*1.50,.12,.26,.77)
        buddha(sign*2.33,-.11,.24,.64)
    group('03 · 石阶与平台')
    for j in range(4):box('石阶',(0,-1.02-j*.1,.16-j*.035),(2.03,.36,.12),'oldstone')

def yellow_crane():
    group('01 · 石台南阶')
    for z,rx,ry,h in [(0,2.43,2.12,.14),(.14,2.27,1.97,.17),(.31,2.16,1.85,.13)]:
        box('平台',(0,0,z+h/2),(2*rx,2*ry,h),'chalk')
    for k in range(6):box('前阶',(0,-2.10-k*.11,.04+(5-k)*.032),(1.45,.27,.08+(5-k)*.064),'oldstone')
    for k in range(5):
        group(f'0{k+2} · 楼层')
        z=.44+k*.81;rx=1.73-k*.135;ry=1.51-k*.119
        box('楼身',(0,0,z+.32),(rx*1.59,ry*1.60,.64),'windows')
        box('朱漆梁',(0,0,z+.58),(rx*1.91,ry*1.89,.12),'red')
        box('回廊台基',(0,0,z+.039),(rx*1.98,ry*1.98,.078),'darkwood')
        for sign in (-1,1):
            for j in range(7):
                x=rx*(-.93+j*.31)
                rod('朱柱',(x,sign*ry*.92,z+.07),(x,sign*ry*.92,z+.58),.038,'red',8)
            for j in [-1,0,1]:rod('侧廊柱',(sign*rx*.91,j*ry*.49,z+.08),(sign*rx*.91,j*ry*.49,z+.56),.043,'red',8)
            for rail in (.17,.26):
                box('围栏',(0,sign*ry*.96,z+rail),(rx*1.91,.040,.035),'red')
        roof('黄琉璃飞檐',0,0,z+.63,rx*1.22,ry*1.22,.47 if k<4 else .92,'goldroof',.15 if k==4 else .42)
    plaque('黄鹤楼金字匾额',0,-1.10,3.99,.74,.27,'yellow-sign')
    stack('宝顶',0,0,[(.11,.11,5.22),(.13,.13,5.31),(.045,.045,5.47),(.02,.02,5.59)],'gold',12)

def natural_arch(name,outer,inner,yfront,thick,key,fault=.065):
    # Pair two traced silhouettes with a tunnel; the hole is clean from both sides and cutting through rock.
    n=len(outer);layers=[];faces=[]
    def wall_depth(x,z):
        # Spatially continuous bedding and vertical fissures avoid spokes radiating from the opening.
        return .105*math.sin(x*2.1+.22*z)+.073*math.cos(2.9*x-.50*z)+.047*math.sin(4.8*z-.5*x)+.029*math.sin(11*x+.85*z)
    for t in (0,.26,.55,.81,1):
        for loop_i,points in enumerate((outer,inner)):
            for i,(x,z) in enumerate(points):
                bump=math.sin(t*PI)*fault*math.sin(i*7.7+t)
                layers.append((x+bump,yfront+t*thick+wall_depth(x,z)+.035*math.sin(t*PI)*math.cos(x*2.5+.2*z),max(.01,z+.03*math.sin(t*PI+i))))
    for level in range(4):
        for ring_i in [0,1]:
            base=level*2*n+ring_i*n;dst=base+2*n
            for i in range(n):
                j=(i+1)%n;face=(base+i,base+j,dst+j,dst+i)
                faces.append(face if ring_i==0 else face[::-1])
    for level in (0,4):
        # Interpolate a craggy front transition between the outside and the aperture, adding strata.
        start=level*2*n; prev=list(range(start,start+n));a=0
        for frac in (.15,.30,.47,.66,.83,1):
            row=[]
            for i in range(n):
                if frac==1:row.append(start+n+i);continue
                x,z=outer[i];u,w=inner[i]
                xx=(1-frac)*x+frac*u;zz=max(.012,(1-frac)*z+frac*w)
                natural=wall_depth(xx,zz)
                row.append(len(layers));layers.append((xx,yfront+thick*level/4+natural,zz))
            for i in range(n):
                j=(i+1)%n;f=(prev[i],prev[j],row[j],row[i]);faces.append(f if level==4 else f[::-1])
            prev=row
    return mesh(name,layers,faces,key,True,.42)

def tianmen():
    group('01 · 穿山洞岩脊')
    n=58;out=[];inn=[]
    for i in range(n):
        a=i*TAU/n; cs,sn=math.cos(a),math.sin(a)
        x=3.2*cs*(1+.045*math.sin(7*a))
        z=max(.23,2.17+2.11*sn+.19*math.sin(5*a)+.11*math.cos(13*a))
        out.append((x,z))
        inn.append((.47*cs*(1+.14*math.sin(5*a))+.095*sn,2.05+1.12*sn+.10*math.cos(3*a)))
    natural_arch('天门洞真实开口',out,inn,-.6,1.23,'karst',.11)
    island('山门岩基',0,-.22,3.25,1.48,.30,'cliff',30)
    for sign in (-1,1):
        # Two sloping talus shoulders tie the stairway to the mountain.
        levels=[]
        for j in range(10):
            t=j/9;y=-3.20+2.86*t;w=.27+1.58*t
            top=.13+.99*t
            levels.append([(sign*.54,y,.025),(sign*.54,y,top*.74),(sign*(.54+.42*w),y,top),(sign*(.54+.76*w),y,top*.60),(sign*(.54+w),y,.03)])
        rock=loft('天梯两侧山脚',levels,'cliff')
        for k in range(48):
            t=R.uniform(.02,.98);u=R.uniform(.30,.88);width=.27+1.58*t
            h=(.13+.99*t)*(1-max(0,u-.40)*1.55)
            shrub('梯边林带',sign*(.54+u*width),-3.20+2.86*t,h,R.uniform(.12,.26),R.choice(['pines','leaf','leaf','leaflight']))
    group('02 · 山脊植被')
    for i,(x,z) in enumerate(out[:n//2]):
        for k in range(3):
            shrub('崖顶山林',x+R.uniform(-.15,.15),R.uniform(-.38,.53),z+R.uniform(-.06,.04),R.uniform(.19,.39),R.choice(['pines','leaf','leaflight','leaf']))
    for sign in (-1,1):
        for k in range(18):
            x=sign*R.uniform(1.17,2.13);z=R.uniform(.51,1.68)
            if abs(x)>1.52:z+=.35
            shrub('石缝灌木',x,-.60,z,R.uniform(.12,.28),R.choice(['leaf','pines']))
    group('03 · 上天梯')
    for i in range(23):
        h=.92*(i+1)/23;y=-3.20+i*.113
        box('天梯石阶',(0,y,h/2),(.91,.136,h),'oldstone')
    for s in [-1,1]:
        rod('天梯侧缘',(s*.51,-3.26,.09),(s*.51,-.61,1.05),.053,'chalk',7)

def canton():
    group('01 · 塔基')
    stack('椭圆塔基',0,0,[(.785,.63,0),(.87,.71,.12),(.79,.65,.20)],'oldstone',32)
    group('02 · 主筒与观光层')
    stack('玻璃核心筒',0,0,[(.35,.33,.18),(.32,.29,1.5),(.325,.29,3.36),(.41,.35,4.86),(.36,.32,5.17)],'glaze',32,smooth=True)
    def at(t,a):
        # Straight skewed posts spanning two offset, rotated ellipses create the hyperboloid waist.
        p=(.75*math.cos(a),.605*math.sin(a));ang=a+2.00
        q=(.58*math.cos(ang)+.075,.48*math.sin(ang)+.025)
        return ((1-t)*p[0]+t*q[0],(1-t)*p[1]+t*q[1],.18+5.02*t)
    group('03 · 扭转钢格网')
    cols=24;tiers=15
    for i in range(cols):
        a=i*TAU/cols
        rod('倾斜外柱',at(0,a),at(1,a),.019,'steel',6,.016)
    for j in range(tiers+1):
        t=j/tiers
        tube('水平环梁',[at(t,i*TAU/cols) for i in range(cols+1)],.014 if j%3 else .022,'steel',5)
        if j<tiers:
            for i in range(cols):
                if i%2==j%2:rod('交叉斜撑',at(t,i*TAU/cols),at((j+1)/tiers,(i-1.05)*TAU/cols),.011,'steel',5)
    group('04 · 塔冠与桅杆')
    stack('顶部观景层',.075,.025,[(.47,.40,4.86),(.57,.49,5.05),(.51,.43,5.21),(.35,.31,5.3)],'glaze',28)
    for z,rad in [(5.06,.55),(5.16,.54),(5.24,.42)]:
        tube('顶沿',[(.075+rad*math.cos(i*TAU/32),.025+rad*.85*math.sin(i*TAU/32),z) for i in range(33)],.025,'steel',6)
    stack('无线电天线',.075,.025,[(.13,.13,5.22),(.105,.105,5.64),(.074,.074,5.66),(.065,.065,6.05),(.039,.039,6.06),(.025,.025,6.45),(.006,.006,6.54)],'steel',14)
    for z,r in ((5.66,.105),(5.88,.09),(6.15,.05)):stack('天线带',.075,.025,[(r,r,z),(r,r,z+.055)],'red',12)

def elephant():
    group('01 · 江岸与水月洞')
    island('漓江岸水',.72,-.04,3.18,1.40,.13,'river',43)
    n=54;out=[];inn=[]
    for i in range(n):
        a=i*TAU/n;c,s=math.cos(a),math.sin(a)
        # Outer silhouette puts a steep trunk left of the hole and the broad body to its right.
        x=.78+2.65*c+.12*math.sin(5*a)
        z=max(.15,1.45+1.40*s+.38*s*c+.10*math.sin(7*a))
        out.append((x,z));inn.append((.64*c*(1+.08*math.sin(3*a)),.69+.56*s-.12*c))
    natural_arch('象鼻与水月岩洞',out,inn,-.55,1.16,'karst',.16)
    group('02 · 崖顶林冠')
    for i in range(92):
        a=R.uniform(.03,PI-.02); xx=.78+2.65*math.cos(a);yy=R.uniform(-.47,.57)
        zz=1.45+1.4*math.sin(a)+.38*math.sin(a)*math.cos(a)+.10*math.sin(7*a)
        shrub('崖顶林地',xx,yy,zz,R.uniform(.18,.37),R.choice(['leaf','leaf','pines','leaflight']))
    for i in range(22):
        a=R.uniform(.36,2.67); xx=.78+2.65*math.cos(a);zz=1.45+1.4*math.sin(a)+.38*math.sin(a)*math.cos(a)+.10*math.sin(7*a)
        shrub('临江垂落植被',xx,-.52,zz-R.uniform(.12,.36),R.uniform(.125,.25),R.choice(['leaf','pines']))
    group('03 · 普贤塔')
    stack('山顶实心砖塔',1.22,.17,[(.16,.16,2.98),(.18,.18,3.04),(.105,.105,3.08),(.095,.095,3.19),(.13,.13,3.22),(.10,.10,3.29),(.06,.06,3.35),(.037,.037,3.44),(.014,.014,3.54)],'oldstone',12)
    for i in range(11):
        px=R.uniform(-1.28,1.65);py=R.uniform(-1.17,-.65)
        tube('倒影水纹',[(px,py,.137),(px+.13,py-.015,.137),(px+.28,py+.018,.137)],.011,'clear',4)

def hongyadong():
    group('01 · 江崖台地')
    for j in range(4):
        box('临江阶地',(0,-.75+j*.48,.11+j*.31),(6.18-j*.08,.89,.22+j*.57),'cliff')
    group('02 · 临江吊脚楼与重叠街廊')
    # Stagger the roofs horizontally and vertically, forming one continuous eleven-storey riverfront.
    terraces=[(-1.14,.26,[-2.32,-.84,.66,2.17], [2,2,2,2]),(-.61,1.02,[-2.10,-.51,1.13,2.35],[2,3,2,2]),(.12,1.86,[-2.18,-.58,1.03,2.29],[2,2,3,2]),(.73,2.75,[-1.55,.15,1.87],[2,3,2])]
    for tier,(y,z,xs,fs) in enumerate(terraces):
        for i,(x,floors) in enumerate(zip(xs,fs)):
            rx=.70 if len(xs)==4 else .82
            ry=.39 if tier<3 else .43
            for k in range(floors):
                zz=z+k*.32
                box('穿斗楼身',(x,y,zz+.14),(rx*1.76,ry*1.45,.29),'windows')
                box('木挑廊',(x,y-.02,zz+.01),(rx*2.04,ry*2,.06),'wood')
                box('腰檐',(x,y-.02,zz+.30),(rx*2.02,ry*2,.049),'darkwood')
                for col in (-.87,-.44,0,.44,.87):box('临江木柱',(x+rx*col,y-ry*.82,zz+.14),(.043,.05,.3),'rust')
                box('凭栏',(x,y-ry*.91,zz+.12),(rx*1.97,.047,.041),'wood')
            roof('错层灰瓦屋面',x,y,z+floors*.32,rx*1.09,ry*1.12,.34,'bluegray',.5)
            if tier==0:
                for col in (-.70,0,.70):rod('吊脚支柱',(x+col*rx,y-ry*.76,.04),(x+col*rx,y-ry*.76,z),.045,'darkwood',6)
    group('03 · 千厮门方向的栈桥与岸线')
    box('沿江走廊',(0,-1.64,.14),(6.6,.26,.12),'oldstone')
    for j in range(23):
        x=-3.08+j*.28;rod('栈桥栏杆柱',(x,-1.76,.18),(x,-1.76,.35),.022,'oldstone',5)
    rod('栈桥上栏',(-3.08,-1.76,.34),(3.10,-1.76,.34),.022,'chalk',6)

def panda():
    group('01 · 生境微地形')
    island('草土地台',0,0,2.95,2.05,.28,'soil',32)
    stack('草甸',0,0,[(2.93,1.98,.22),(2.77,1.89,.32)],'leaflight',33)
    group('02 · 黑白大熊猫')
    start=set(bpy.context.scene.objects)
    elevation=.29
    def el(name,at,r,key,nu=16,nv=10):
        return ellipse(name,(at[0],at[1],at[2]+elevation),r,key,nu,nv)
    el('躯干',(0,.10,.85),(.62,1.09,.58),'whitefur',22,14)
    el('肩背黑带',(0,-.47,.88),(.64,.39,.64),'blackfur',21,13)
    for sign in [-1,1]:
        for zz, yy in ((.38,-.51),(.36,.78)):
            el('熊掌与四肢',(sign*.40,yy,zz),(.235,.28,.38),'blackfur')
            el('前掌',(sign*.40,yy-.09,.14),(.235,.30,.14),'blackfur',12,8)
    el('短尾',(0,1.13,.83),(.17,.17,.15),'whitefur')
    el('熊猫头部',(0,-.93,.93),(.54,.45,.47),'whitefur',24,16)
    for s in (-1,1):
        el('圆耳',(s*.38,-.87,1.35),(.17,.116,.19),'blackfur')
        # Tilt the teardrop-shaped black eye patches towards the cheeks.
        eye=el('眼斑',(s*.244,-1.285,1.011),(.135,.072,.16),'blackfur',14,10)
        for v in eye.data.vertices:
            dx=v.co.x-s*.244;dz=v.co.z-(1.011+elevation);ang=-s*.52
            v.co.x=s*.244+dx*math.cos(ang)+dz*math.sin(ang)
            v.co.z=1.011+elevation-dx*math.sin(ang)+dz*math.cos(ang)
        el('眼',(s*.215,-1.354,1.04),(.040,.023,.041),'darkwood',10,6)
        el('眼高光',(s*.211,-1.376,1.055),(.013,.009,.012),'chalk',8,5)
    el('吻部',(0,-1.32,.83),(.221,.137,.157),'whitefur')
    el('鼻',(0,-1.43,.911),(.103,.071,.069),'blackfur',14,8)
    for ob in set(bpy.context.scene.objects)-start:
        for v in ob.data.vertices:
            x,y,z=v.co;t=-.63;v.co=(x*math.cos(t)-y*math.sin(t)-.42,x*math.sin(t)+y*math.cos(t)-.15,z)
    group('03 · 行为丰富化木架')
    for x in [.72,1.87]:
        for y in [.46,1.16]:rod('平台木撑',(x,y,.26),(x,y,1.62),.092,'wood',9)
    for j in range(7):rod('木架平台',(.62+j*.22,.31,1.49),(.62+j*.22,1.26,1.49),.085,'wood',8)
    for x in [.87,1.51]:rod('攀爬斜木',(x,-.45,.31),(x,.44,1.47),.086,'wood',8)
    for j in range(4):
        y=-.34+j*.195;z=.46+j*.247
        rod('横档',(.80,y,z),(1.58,y,z),.045,'wood',7)
    group('04 · 熊猫竹林')
    for i in range(13):
        x=R.uniform(-2.1,-.92);y=R.uniform(.63,1.25);h=R.uniform(1.4,2.5)
        rod('竹竿',(x,y,.25),(x+.07,y+.05,h),.035,'bamboo',6,.02)
        for j in range(3):
            k=(j+1)/4;xx=x+R.uniform(-.32,.32);yy=y+R.uniform(-.15,.17);zz=h*(.43+.15*j)
            rod('竹枝',(x,y,zz),(xx,yy,zz+.28),.016,'bamboo',5)
            for m in range(3):
                a=R.uniform(0,TAU);rad=.27;tx=xx+rad*math.cos(a);ty=yy+rad*math.sin(a);dz=.065
                mesh('披针竹叶',[(xx,yy,zz+.27),(tx+.043*math.sin(a),ty-.043*math.cos(a),zz+.36),(tx+.13*math.cos(a),ty+.13*math.sin(a),zz+.27+dz),(tx-.043*math.sin(a),ty+.043*math.cos(a),zz+.35)],[(0,1,2),(0,2,3)],'leaf')

def jiuzhai():
    group('01 · 钙华台地与上下海子')
    island('下游水潭',0,-.45,3.92,1.65,.17,'jade',43)
    n=37; v=[];f=[]
    def brink(t):return (.17*math.sin(PI*t)+.21*math.cos(4*t)+.23*t,1.43+.105*math.cos(5*t)-.14*t*t)
    for i in range(n):
        t=-1+2*i/(n-1);x=3.50*t;y,h=brink(t)
        v.extend([(x,y-.11,.18),(x,y,h),(x,y+.34,h+.095),(x,1.54,h+.09),(x,1.54,.15)])
    for i in range(n-1):
        for j in range(5):
            a=i*5+j;b=i*5+(j+1)%5;f.append((a,a+5,b+5,b))
    mesh('曲折钙华瀑崖',v,f,'tufa')
    vs=[];fs=[]
    for i in range(n):
        t=-1+2*i/(n-1);y,h=brink(t);vs.extend([(3.50*t,y+.19,h+.08),(3.50*t,1.42,h+.105)])
        if i:fs.append((2*i-2,2*i,2*i+1,2*i-1))
    mesh('上游青色积水',vs,fs,'clear')
    group('02 · 水帘、露岩与水花')
    for i in range(73):
        t=-.98+1.96*i/72+R.uniform(-.005,.005);x=3.5*t;y,h=brink(t)
        intensity=.56+.32*math.sin(6.1*x+.4)+.19*math.cos(3.2*x)
        w=.06+.064*intensity+R.uniform(-.015,.019);bottom=.16+.18*(1-intensity)*R.random()
        xoff=.03*math.sin(11*t);vs=[];fs=[]
        for j in range(6):
            frac=j/5;dr=(.21+.17*intensity)*math.sin(frac*PI/2);z=h+.065-(h+.065-bottom)*frac
            spread=w*(.85+.22*frac+.10*math.cos(j+2*i));wind=.035*math.sin(i*.7+frac*3)*frac
            vs.extend([(x-spread*.65+xoff*frac+wind,y-dr+.014*math.cos(i*4+j),z),(x+spread*.60+xoff*frac+wind,y-dr-.006*math.sin(j),z-.009)])
            if j:fs.append((2*j-2,2*j,2*j+1,2*j-1))
        mesh('水帘',vs,fs,'fall' if i%4 else 'clear')
        if i%3==0:
            ellipse('瀑脚飞沫',(x+R.uniform(-.06,.06),y-.32-R.uniform(0,.13),.186),(.18*intensity+.04,R.uniform(.07,.17),R.uniform(.012,.035)),'foam',8,4)
    group('03 · 原始针叶林')
    for i in range(39):
        t=R.uniform(-.99,.99);x=3.50*t;y=R.uniform(.61,1.57);h=brink(t)[1]
        if i%2==0:shrub('瀑顶灌木',x,y-.19,h+.11,R.uniform(.19,.35),'leaflight' if i%4 else 'leaf')
        conifer(x,y,h+.07,R.uniform(.45,1.00),'pines' if i%3 else 'leaf')

def dali():
    group('01 · 南门城台和拱券')
    archwall('穿城拱道',0,0,6.13,1.57,0,1.59,.49,.52,'oldstone',25)
    # Cut stone voussoirs frame both sides of the real arch.
    for sign in (-1,1):
        for i in range(17):
            lo=i*PI/17+.006;hi=(i+1)*PI/17-.006
            vs=[(r*math.cos(a),sign*(.79+d),.52+r*math.sin(a)) for d in [0,.05] for r,a in ((.50,lo),(.669,lo),(.669,hi),(.5,hi))]
            mesh('券石',vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'chalk')
        for i in range(26):
            x=-2.99+i*.24;box('垛口',(x,sign*.744,1.70),(.154,.13,.22),'oldstone')
        box('石砌压顶',(0,sign*.71,1.56),(6.25,.21,.10),'oldstone')
    group('02 · 白族城楼')
    for lvl in range(2):
        z=1.62+lvl*.85;rx=1.88-lvl*.43;ry=.79-lvl*.14
        box('白墙木构',(0,0,z+.345),(rx*1.68,ry*1.39,.65),'windows' if lvl else 'paper')
        for side in (-1,1):
            for i in range(7):
                x=rx*(-.9+.30*i);rod('城楼朱柱',(x,side*ry*.86,z+.02),(x,side*ry*.86,z+.66),.040,'red',8)
            for j in range(9):
                x=rx*(-.78+.195*j); box('隔扇门',(x,side*ry*.715,z+.32),(.205,.035,.38),'darkwood')
        box('梁枋',(0,0,z+.60),(rx*1.99,ry*1.88,.115),'red')
        roof('青瓦城楼',0,0,z+.67,rx*1.19,ry*1.29,.67,'bluegray',.58)
    plaque('大理南城楼匾额',0,-.805,1.34,.69,.25,'dali-sign')
    group('03 · 额枋与栏杆')
    for side in (-1,1):
        for i in range(19):
            x=-2.46+i*.273
            box('石栏柱',(x,side*.81,1.72),(.064,.065,.25),'chalk')
        box('长石栏',(0,side*.808,1.82),(4.99,.07,.064),'chalk')
