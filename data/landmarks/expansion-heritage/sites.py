"""Six individually modeled landmarks. Local frontage points along Blender -Y."""

from contextlib import contextmanager
from math import cos, pi, sin

from architecture import cut_base, hall, radial, tree
from geometry import PARTS, box, cylinder, face, floorplan, group, hip, profile, shaft, steps, window


@contextmanager
def placement(x, y, bearing):
    """Rotate only the faces created in the block, then translate them into the compound."""
    first = {name: len(faces) for name, faces in PARTS.items()}
    cos_a, sin_a = cos(bearing), sin(bearing)
    yield
    for name, patches in PARTS.items():
        for i in range(first.get(name, 0), len(patches)):
            points, material, uv = patches[i]
            patches[i] = ([(x + a*cos_a - b*sin_a, y + a*sin_a + b*cos_a, z)
                           for a, b, z in points], material, uv)


def square_pier(x, y, z, width, height, stone="limestone"):
    box(x,y,z,width*1.24,width*1.22,.075,stone)
    profile(x,y,z+.075,[(0,width,width),(height-.17,width*.92,width*.94)],stone)
    box(x,y,z+height-.095,width*1.18,width*1.17,.095,stone)


def mosaic_windows(x, y, z, count, span, height, frame="limestone"):
    pitch = span / count
    for i in range(count):
        xc = x + ((i+.5)/count-.5)*span
        window(xc,y,z,pitch*.72,height,frame,"dark")


def national_museum():
    z = cut_base(16.44,10.65,"fieldstone","limestone",.24)
    group("西平台·三级石基与中央台阶")
    podium = z+.47
    box(0,.21,z,15.56,8.97,.47,"limestone")
    box(0,-4.51,z+.04,15.50,.58,.14,"fieldstone")
    steps(0,-5.16,z,7.62,1.62,.47,7,"limestone")
    for side in (-1,1):
        box(side*4.04,-4.14,z+.035,.42,1.70,.42,"limestone")
    group("西入口·前后两列方柱")
    top = podium+3.24
    for y in (-3.43,-2.31):
        for i in range(12):
            x=(i-5.5)*.626
            square_pier(x,y,podium,.23,3.25)
    box(0,-2.70,top,8.14,1.86,.33,"limestone")
    box(0,-3.61,top+.16,8.27,.18,.14,"limestone")
    box(0,-3.61,top+.31,8.29,.17,.074,"whitewash")
    for i in range(15):
        box((i-7)*.53,-3.555,top-.115,.21,.075,.079,"bronze")
    box(0,-1.61,podium,7.80,.70,3.2,"limestone")
    for i in range(11):
        x = (i-5)*.65
        window(x,-1.98,podium+.25,.48,2.42,"bronze","dark")
        box(x,-2.046,podium+2.98,.43,.057,.13,"dark")
    # Small fixed crest and terracotta infill at the centre of the west cornice.
    box(0,-3.66,top+.327,1.46,.10,.216,"rouge")
    cylinder((0,-3.60,top+.43),(0,-3.735,top+.43),.119,.119,"gold",12)
    group("对称西翼·通长窗列及端柱")
    for side in (-1,1):
        x = side*6.01
        top_wing=podium+2.82
        box(x,.17,podium,3.56,7.36,2.82,"limestone")
        for level in range(3):
            group(f"{'北' if side>0 else '南'}翼·第{level+1}层")
            base=podium+.18+level*.788
            mosaic_windows(x,-3.53,base,6,3.23,.53)
            box(x,-3.52,base-.037,3.54,.18,.085,"limestone")
            for k in range(8):
                yy=-2.94+k*.83
                outer=side*7.80
                box(outer,yy,base+.046,.085,.41,.37,"dark")
                box(outer,yy,base+.419,.153,.48,.062,"limestone")
        group("西翼·装饰角墩与挑檐")
        box(x,.17,top_wing,3.67,7.47,.16,"bronze")
        box(x,.17,top_wing+.14,3.68,7.48,.18,"limestone")
        for inner_x,yy in ((side*4.21,-2.88),(side*7.51,-2.90)):
            profile(inner_x,yy,podium,[(0,.71,1.25),(3.37,.67,1.13),(3.48,.76,1.23),
                                     (3.62,.72,1.19)],"limestone")
            box(inner_x,yy,top+.40,.48,.96,.12,"fieldstone")
    group("东侧新馆·退台体量与玻璃格栅")
    for yy,w,d,h in ((.8,8.20,4.76,3.20),(2.71,13.89,2.83,2.98)):
        box(0,yy,podium,w,d,h,"limestone")
        box(0,yy,podium+h,w+.15,d+.16,.15,"fieldstone")
    box(0,4.18,podium+.22,9.69,.082,1.99,"bronze")
    for i in range(27):
        x=(i-13)*.343
        box(x,4.24,podium+.22,.22,.039,1.86,"dark")
    for y in (-.82,.37,1.5,2.62):
        box(0,y,podium+3.37,6.75,.22,.056,"bronze")


def prince_kung():
    z=cut_base(12.46,10.30,"fieldstone","ashlar",.25)
    group("银安殿·石月台与抄手台阶")
    box(0,1.86,z,6.77,4.35,.42,"whitewash")
    box(0,-2.48,z+.012,11.53,4.52,.046,"fieldstone")
    for x in (-2.28,0,2.28):
        box(x,-2.29,z+.065,.37,4.95,.014,"marble")
    box(0,-.20,z+.045,6.22,1.28,.36,"fieldstone")
    box(0,-.84,z+.40,6.58,.16,.071,"whitewash")
    for side in (-1,1):
        steps(side*2.34,-1.41,z+.064,1.36,1.41,.35,7,"whitewash")
        for j in range(2):
            x,y=side*(2.29+j*1.05),-1.25-j*.94
            square_pier(x,y,z+.064,.13,.61,"marble")
            profile(x,y,z+.67,[(0,.28,.27),(.28,.29,.28),(.32,.33,.33)],"dark")
            box(x,y,z+.75,.16,.161,.158,"gold")
            hip(x,y,z+1.0,.42,.44,.17,"dark","bronze")
    group("银安殿·五间歇山正殿")
    h=hall(0,1.86,z+.422,6.38,3.71,1.52,5,"plum","rouge","glaze-green","teal",
           base="marble", roof_height=1.17, platform=False)
    for dx in (-3.39,3.39):
        shaft(dx,1.87,h-.15,.059,.255,"glaze-green",7,.025)
    for i in range(13):
        x=(i-6)*.46
        box(x,.033,z+1.76,.20,.132,.098,"teal")
        box(x,.030,z+1.72,.092,.130,.052,"gold")
    for i in range(5):
        x=(i-2)*1.032
        y=1.86+.055*3.71-3.71*.34-.065
        for j in range(1,6):
            box(x,y,z+.51+j*.151,.72,.024,.021,"gold")
        for j in (-.26,-.083,.083,.26):
            box(x+j,y,z+.51,.023,.024,.90,"gold")
    group("中院·东西灰瓦配殿")
    for side in (-1,1):
        with placement(side*4.62,-.92,-side*pi/2):
            hall(0,0,z+.082,4.83,1.62,1.33,5,"fieldstone","rouge","greyTile","teal",
                 base="marble",roof_height=.83,plaque=False)
        box(side*5.56,2.31,z,1.28,3.68,1.01,"fieldstone")
        box(side*5.55,2.31,z+1.0,1.45,3.76,.13,"greyTile")
        tree(side*5.16,3.92,z,.69,72+side)


def shaanxi_history_museum():
    z=cut_base(14.98,11.96,"fieldstone","limestone",.24)
    group("小寨本馆·入口广场及中庭")
    box(0,-4.19,z+.019,11.25,2.61,.055,"graniteLight")
    box(0,.39,z+.035,10.44,8.48,.14,"ashlar")
    for side in (-1,1):
        box(side*4.16,-3.31,z+.05,2.66,1.61,.048,"grass")
    box(0,-3.17,z+.08,4.30,1.02,.11,"graniteLight")
    box(0,-3.17,z+.195,4.02,.83,.025,"deepwater")
    steps(0,-2.25,z+.13,4.08,1.56,.53,11,"graniteLight")
    for side in (-1,1):
        box(side*2.17,-1.8,z+.113,.156,2.03,.39,"whitewash")
    group("序厅·唐式中央殿堂")
    deck=z+.64
    hall(0,1.14,deck,7.67,4.30,1.74,7,"limestone","whitewash","greyTile","limestone",
         base="graniteLight",roof_height=1.04,upper_eave=True,platform=False)
    box(0,-.914,deck+1.43,7.30,.191,.23,"limestone")
    for i in range(17):
        x=(i-8)*.411
        box(x,-.95,deck+1.22,.18,.18,.15,"granite")
    y=1.14+.055*4.30-4.30*.34-.051
    mosaic_windows(0,y,deck+.19,7,6.33,1.22,"timber")
    group("四隅崇楼与衔接廊房")
    for side in (-1,1):
        for a,yy in enumerate((-2.71,3.63)):
            x=side*(5.56 if a==0 else 5.11)
            platform=deck-(.20 if a==0 else .04)
            hall(x,yy,platform,2.66,2.56,1.31,3,"limestone","whitewash","greyTile","limestone",
                 roof_height=.78,upper_eave=a==1,plaque=False)
        box(side*5.11,.55,deck-.26,2.28,4.96,1.10,"whitewash")
        hip(side*5.11,.55,deck+.86,2.62,5.18,.54,"greyTile","limestone")
        box(side*3.79,-2.87,z+.05,.11,1.07,.53,"limestone")
        tree(side*6.76,4.98,z,.83,235+side,True)
    group("后部展馆·白墙黛瓦")
    box(0,4.36,deck-.25,6.40,2.34,1.37,"limestone")
    hip(0,4.36,deck+1.12,6.65,2.64,.68,"greyTile","limestone")


def arched_wall(y, z, width, depth, height, half_open, spring):
    """Manifold masonry portal, including the underside of the true opening."""
    for side in (-1,1):
        w=width/2-half_open
        box(side*(half_open+w/2),y,z,w,depth,height,"fieldstone")
    front, rear=y-depth/2,y+depth/2
    seg=16
    for i in range(seg):
        a=pi*(1-i/seg)
        b=pi*(1-(i+1)/seg)
        x0,x1=half_open*cos(a),half_open*cos(b)
        h0,h1=z+spring+half_open*sin(a),z+spring+half_open*sin(b)
        peak=z+height
        face([(x0,front,h0),(x1,front,h1),(x1,front,peak),(x0,front,peak)],"fieldstone")
        face([(x1,rear,h1),(x0,rear,h0),(x0,rear,peak),(x1,rear,peak)],"fieldstone")
        face([(x0,rear,h0),(x1,rear,h1),(x1,front,h1),(x0,front,h0)],"granite")
        face([(x0,front,peak),(x1,front,peak),(x1,rear,peak),(x0,rear,peak)],"fieldstone")
    for sign in (-1,1):
        for i in range(2):
            box(sign*(half_open+.060), front-.015,z+i*spring/2,.09,.076,spring/2,"granite")


def parapet(x, y, z, width, count):
    box(x,y,z,width,.19,.13,"fieldstone")
    for i in range(count):
        p=x+((i+.5)/count-.5)*width
        box(p,y,z+.13,width/count*.56,.22,.21,"fieldstone")


def xian_city_wall():
    z=cut_base(15,12.48,"fieldstone","ashlar",.26)
    group("护城河两岸·独立桥面与桥墩")
    box(0,-5.09,z,14.48,1.80,.042,"deepwater")
    for yy in (-5.995,-4.17):
        box(0,yy,z,14.49,.192,.194,"granite")
    for yy in (-5.43,-4.59):
        box(0,yy,z+.042,1.12,.19,.24,"fieldstone")
    box(0,-5.10,z+.27,1.45,2.21,.115,"beam")
    for x in (-.71,.71):
        for i in range(7):
            box(x,-6.10+i*.336,z+.37,.095,.12,.22,"timber")
        box(x,-5.08,z+.565,.098,2.12,.074,"beam")
    group("月城闸楼·南侧悬桥通道")
    arched_wall(-3.68,z,5.61,1.04,1.78,.53,.66)
    hall(0,-3.68,z+1.78,2.75,1.15,.82,3,"limestone","timber","greyTile","timber",
         base="granite",roof_height=.53,plaque=False)
    for side in (-1,1):
        parapet(side*2.1,-4.15,z+1.78,1.25,4)
    group("瓮城箭楼·墙上连续箭孔")
    arched_wall(-.70,z,9.48,1.17,2.30,.65,.90)
    top=z+2.30
    profile(0,-.73,top,[(0,5.40,2.02),(1.64,5.17,1.85)],"limestone")
    for row in range(4):
        for col in range(11):
            x=(col-5)*.422
            yy=-1.743 + row*.022
            box(x,yy,top+.19+row*.33,.214,.072,.179,"dark")
            if col%3==0:
                box(x,yy-.011,top+.151+row*.33,.246,.109,.05,"fieldstone")
    hip(0,-.73,top+1.64,6.28,2.67,.87,"greyTile","beam")
    for side in (-1,1):
        parapet(side*3.90,-1.16,top,1.59,5)
    group("主城楼·正楼及内城砖墙")
    arched_wall(2.69,z,14.12,1.58,2.63,.73,1.02)
    for side in (-1,1):
        parapet(side*4.58,1.98,z+2.63,4.78,13)
        parapet(side*4.58,3.40,z+2.63,4.78,13)
    hall(0,2.69,z+2.63,6.00,2.58,1.33,7,"plum","rouge","greyTile","teal",
         roof_height=.81,upper_eave=True)
    group("瓮城及月城接墙")
    for side in (-1,1):
        profile(side*4.56,1.03,z,[(0,.75,3.73),(2.30,.63,3.59)],"fieldstone")
        for n in range(9):
            box(side*4.56,-.66+n*.407,z+2.30,.27,.232,.21,"fieldstone")
        profile(side*2.56,-2.35,z,[(0,.71,2.52),(1.74,.55,2.44)],"fieldstone")
        for n in range(5):
            box(side*2.56,-3.26+n*.48,z+1.74,.28,.277,.20,"fieldstone")


def thatched_hip(x, y, z, width, depth, h):
    # A broad, shallow thatch roof with thick eaves and a red-brown ridge cap.
    w=width/2
    d=depth/2
    lower=[(-w,-d),(w,-d),(w,d),(-w,d)]
    ridge=w-d*.75
    loops=[]
    for f in (0,.23,.58,.83,.98):
        rw=w+(ridge-w)*f
        rd=d*(1-f)
        loops.append([(x+sx*rw,y+sy*rd,z+(0.82*f+0.18*f*f)*h)
                      for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))])
    face([(x+a,y+b,z-.082) for a,b in lower[::-1]],"timber")
    for j in range(4):
        k=(j+1)%4
        a,b=loops[0][j],loops[0][k]
        face([(a[0],a[1],z-.082),(b[0],b[1],z-.082),b,a],"plum")
    for lower,upper in zip(loops,loops[1:]):
        for j in range(4):
            k=(j+1)%4
            a,b,c,d=lower[j],lower[k],upper[k],upper[j]
            face([a,b,c,d],"thatch",[(0,0),(1.6,0),(1.35,.35),(.15,.35)])
    face(loops[-1],"thatch")
    cylinder((x-ridge,y,z+h),(x+ridge,y,z+h),.055,.055,"plum",6)


def yinxu():
    z=cut_base(12.45,9.15,"earth","grass",.24)
    group("宫殿宗庙区·露出台基与草地")
    box(.25,-.36,z,7.34,6.20,.035,"grass")
    box(.33,2.26,z+.03,11.31,4.23,.27,"earth")
    steps(.09,-.37,z,2.28,1.15,.32,6,"granite")
    group("仿殷大殿·现代保护展示建筑")
    base=z+.31
    box(.32,2.26,base,8.80,2.81,1.20,"graniteLight")
    for i in range(15):
        x=.32+(i-7)*.63
        for yy in (.73,3.78):
            shaft(x,yy,base,.076,1.21,"plum",7)
            box(x,yy,base,.15,.16,.095,"granite")
        if i<14:
            window(x+.303,.823,base+.192,.31,.66,"plum","dark")
    for i in range(7):
        x=(i-3)*1.42+.32
        box(x,.83,base+1.083,1.22,.16,.14,"beam")
    thatched_hip(.32,2.26,base+1.22,10.56,4.12,.79)
    box(.32,2.26,base+1.80,9.10,2.97,.29,"plum")
    thatched_hip(.32,2.26,base+2.080,9.72,3.29,.83)
    group("殷墟夯土基址·低台基与柱础")
    for x,y,w,d in ((-3.24,-1.5,4.67,1.38),(-3.04,-3.28,4.72,1.30)):
        box(x,y,z+.021,w,d,.16,"earth")
        for p in range(7):
            xx=x+((p+.5)/7-.5)*w
            shaft(xx,y-d*.26,z+.177,.111,.081,"granite",7)
        for yy in (y-d*.43,y+d*.43):
            box(x,yy,z+.16,w,.11,.07,"rock")
    group("妇好墓享堂·现代复原展示")
    x,y=3.53,-2.52
    box(x,y,z+.029,3.46,3.01,.234,"earth")
    box(x,y,z+.26,2.79,1.88,.93,"whitewash")
    for xx in (x-1.21,x-.43,x+.43,x+1.21):
        shaft(xx,y-1.02,z+.26,.061,.94,"plum",7)
    thatched_hip(x,y,z+1.20,3.55,2.81,.62)
    steps(x,y-1.51,z,1.16,.68,.26,5,"granite")


def horsehead_gable(x,y,z,w,d,h,side):
    xx = x+side*(w/2+.033)
    # The firebreak is a single stepped wall, with tile caps on the horizontal runs.
    dims = [(d*.50,h+.14),(d*.365,h+.38),(d*.23,h+.62)]
    left = [(-dims[0][0],0)]
    for end, elevation in dims:
        if len(left)>1:
            left.append((-end,left[-1][1]))
        left.append((-end,elevation))
    points = left + [(-py,pz) for py,pz in left[::-1]]
    outside = [(xx+side*.068,y+py,z+pz) for py,pz in points]
    inside = [(xx-side*.055,y+py,z+pz) for py,pz in points]
    face(outside[::-1] if side>0 else outside,"whitewash")
    face(inside if side>0 else inside[::-1],"whitewash")
    for i in range(len(outside)):
        j=(i+1)%len(outside)
        face([outside[i],outside[j],inside[j],inside[i]] if side>0
             else [outside[j],outside[i],inside[i],inside[j]],"whitewash")
        dy=abs(points[j][0]-points[i][0])
        if dy>.04 and points[j][1]==points[i][1] and points[i][1]>0:
            box(xx,y+(points[j][0]+points[i][0])/2,z+points[i][1],.184,dy+.08,.070,"greyTile")


def huizhou_house(x,y,z,w,d,h):
    box(x,y,z,w,d,.11,"fieldstone")
    box(x,y,z+.11,w,d,h,"whitewash")
    for i in range(3):
        xx=x+(i-1)*w*.285
        window(xx,y-d*.5-.018,z+.68,w*.132,.41,"timber","dark")
    box(x,y-d*.5-.008,z+.126,w*.27,.12,.51,"timber")
    for side in (-1,1):
        horsehead_gable(x,y,z+.1,w,d,h,side)
    hip(x,y,z+h+.1,w*1.06,d*1.17,.64,"greyTile","timber",.11)


def drying_tray(x,y,z,r,i):
    # Woven bamboo lip surrounds a raised bed of crops.
    radial(x,y,z,[(0,r*.83),(.055,r),(.103,r),(.119,r*.96)],"ochre",12)
    crop=("rouge","gold","rouge","ochre")[i%4]
    radial(x,y,z+.10,[(0,r*.86),(.017,r*.84),(.032,r*.73)],crop,12)
    for k in range(4):
        a=2*pi*k/4+.44*i
        px=x+r*.48*cos(a)
        py=y+r*.48*sin(a)
        shaft(px,py,z+.117,.051,.024,crop,5)


def huangling():
    z=cut_base(13.46,9.80,"earth","grass",.265)
    group("天街村坡·外缘田埂和石砌坡脚")
    for i in range(4):
        yy=-3.67+i*.68
        x0=-6.10+i*.30
        w=12.25-i*.48
        zz=z+i*.17
        outline=[(x0,yy-.46),(x0+w*.31,yy-.50),(x0+w*.71,yy-.38),
                 (x0+w,yy-.49),(x0+w,yy+.31),(x0+w*.65,yy+.32),
                 (x0+w*.3,yy+.29),(x0,yy+.34)]
        floorplan(0,0,z,outline,.18+i*.17,"grass")
        for a,b in zip(outline[:3],outline[1:4]):
            cylinder((*a,zz+.14),(*b,zz+.14),.061,.061,"ochre",5)
    group("连续村坡·层台和挡土坡")
    rises = [(-2.54,.29),(-2.31,.45),(-2.30,.69),(-.72,.97),(-.70,1.18),
             (1.03,1.51),(1.07,1.69),(2.61,2.02),(2.64,2.37),(4.78,2.64)]
    for (ya,ha),(yb,hb) in zip(rises,rises[1:]):
        ta=(ya+2.54)/7.32
        tb=(yb+2.54)/7.32
        wa,wb=6.48-.57*ta,6.48-.57*tb
        a,b=(-wa,ya,z+ha),(wa,ya,z+ha)
        c,d=(wb,yb,z+hb),(-wb,yb,z+hb)
        mat="fieldstone" if yb-ya<.2 else "grass"
        face([a,b,c,d],mat)
        face([(a[0],ya,z),(d[0],yb,z),d,a],"earth")
        face([(c[0],yb,z),(b[0],ya,z),b,c],"earth")
    for yy,hh in (rises[0],rises[-1]):
        w=6.48-.57*(yy+2.54)/7.32
        vertices=[(-w,yy,z),(w,yy,z),(w,yy,z+hh),(-w,yy,z+hh)]
        face(vertices if yy<0 else vertices[::-1],"earth")
    group("徽派民居·马头墙和灰瓦")
    houses=[(-3.48,-1.27,1.06,2.27,1.94,1.47),(1.25,-1.19,1.03,2.75,1.81,1.56),
            (4.22,.44,1.67,2.20,1.77,1.45),(-2.71,1.50,2.03,2.83,2.19,1.60),
            (.72,2.47,2.64,2.57,2.32,1.65),(-4.81,2.68,2.31,2.14,1.93,1.55),
            (3.98,3.34,2.89,2.38,1.64,1.40)]
    # Low stone retaining walls are visible beneath the houses along the steep front.
    for i,(x,y,hh,w,d,h) in enumerate(houses):
        profile(x,y,z+hh-.47,[(0,w*1.20,d*1.27),(.47,w*1.09,d*1.13)],"fieldstone")
        huizhou_house(x,y,z+hh,w,d,h)
        if i in (2,4,6):
            tree(x+w*.57,y+.48,z+hh*.8,.55,193+i,False)
    group("晒工坊·成排木晒架与竹匾")
    for n,(x,y,hh,w,d,h) in enumerate(houses[:5]):
        yy=y-d*.67-.31
        high=z+hh+.82
        for side in (-1,1):
            xx=x+side*w*.43
            cylinder((xx,y-d*.5,z+hh+.48),(xx,yy,high),.045,.043,"timber",6)
            box(xx,yy,z+hh*.57,.08,.095,hh*.43+.84,"beam")
        box(x,yy,high,w*1.10,.70,.085,"beam")
        for i in range(3):
            drying_tray(x+(i-1)*w*.327,yy+.038*sin(i*2+n),high+.088,.289+(i==1)*.035,n+i)
    group("顺坡石阶·晒秋村巷")
    for x,y,base,h,w in ((-.96,-2.87,.18,.90,.78),(-.48,-.67,1.01,.98,.72),(2.84,1.1,1.69,1.07,.67)):
        steps(x,y,z+base,w,1.80,h,12,"granite")


SCENES = {
    "national-museum-china": national_museum,
    "prince-kung": prince_kung,
    "shaanxi-history-museum": shaanxi_history_museum,
    "xian-city-wall": xian_city_wall,
    "yinxu": yinxu,
    "huangling": huangling,
}
