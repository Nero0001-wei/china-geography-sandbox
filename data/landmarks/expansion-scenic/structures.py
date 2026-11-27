"""Two recognizable public exteriors, built as local editable geometry."""
from math import cos, hypot, pi, sin, sqrt
from random import Random

from mathutils import Vector

from geometry import annular_arch, sphere
from shapes import (
    base, box, cylinder, face, forest, group, noise, palm, peak,
    plank_line, profile, surface,
)
from natural import INTERIOR, TILE, smooth01


def fast_observatory():
    base("gorgeCanopy","gorgeCut")
    cx,cy=0,-.12
    dish_radius=1.585
    outer_radius=1.99

    def relief(x,y):
        radius=hypot(x-cx,y-cy)
        # Keep the floor below the actual reflector mesh at its lowest point.
        mineral=0.372+0.011*noise(x,y)
        rural=mineral+(.08+.06*noise(x,y))*smooth01((radius-dish_radius+.02)/.65)
        peaks=[(-2.36,.86,.51,.81,1.02),(-1.86,1.51,.59,.44,.98),(-.94,1.75,.64,.48,1.13),
               (.03,1.77,.58,.44,1.29),(.87,1.77,.61,.57,1.09),(1.64,1.47,.54,.62,.97),
               (2.38,.77,.45,.89,1.24),(2.32,-.801,.56,.91,.82),(-2.35,-.93,.53,.70,.58)]
        hills=[peak(x,y,*p,1.3) for p in peaks]
        upland=max(hills)+.23*sum(hills)
        return rural+upland*smooth01((radius-dish_radius+.05)/.45)

    def material(x,y,z):
        r=hypot(x-cx,y-cy)
        if r<1.49:
            return "gorgeShadow"
        if z>.96 and noise(x*.70,y*1.16)>.49:
            return "cliff"
        return "gorgeCanopy" if noise(x*.7,y*.8)>-.065 else "pineDark"
    surface("大窝凼林地与周围喀斯特山肩",TILE,48,42,relief,material)
    forest(15,INTERIOR,36,relief,lambda x,y: hypot(x-cx,y-cy)>1.87 and abs(x)<2.70,
           woodland="broad",min_size=.10,max_size=.31)

    def reflector(rx):
        sphere_radius=2.13
        return .44+sphere_radius-sqrt(sphere_radius*sphere_radius-rx*rx)
    n=72
    ring_count=10
    group("FAST 下凹球面反射盘")
    rings=[]
    for j in range(1,ring_count+1):
        r=dish_radius*j/ring_count
        turn=(j%2)*pi/n
        rings.append([(cx+r*cos(2*pi*i/n+turn),cy+r*sin(2*pi*i/n+turn),reflector(r)) for i in range(n)])
    for i in range(n):
        face([(cx,cy,reflector(0)),rings[0][i],rings[0][(i+1)%n]],"reflectorWhite")
    panel_rng=Random(441)
    for a,b in zip(rings,rings[1:]):
        for i in range(n):
            j=(i+1)%n
            colors=("reflectorWhite","reflectorIce","reflectorPanel","reflectorWhite","reflectorWhite")
            face([a[i],b[i],b[j]],panel_rng.choice(colors))
            face([a[i],b[j],a[j]],panel_rng.choice(colors))
    group("球面外沿")
    rim_z=reflector(dish_radius)+.012
    for i in range(n):
        a,b=2*pi*i/n,2*pi*(i+1)/n
        def rim(t,dr,dz):
            return (cx+(dish_radius+dr)*cos(t),cy+(dish_radius+dr)*sin(t),rim_z+dz)
        face([rim(a,-.009,0),rim(a,.048,0),rim(b,.048,0),rim(b,-.009,0)],"reflectorIce")
        face([rim(a,.048,-.045),rim(b,.048,-.045),rim(b,.048,0),rim(a,.048,0)],"reflectorShadow")
        if i%3==0:
            x,y,z=rim(a,.035,-.048)
            z_ground=relief(x,y)-.025
            if z_ground<z-.05:
                cylinder((x,y,z_ground),(x,y,z),.013,.016,"reflectorPanel",5)

    group("六座公开可见的馈源支撑塔")
    cabin_z=1.54
    for i in range(6):
        phi=2*pi*i/6+pi/6
        tx,ty=cx+outer_radius*cos(phi),cy+outer_radius*sin(phi)
        gz=relief(tx,ty)-.010
        yaw=phi+pi/3
        head_z=max(2.07,gz+1.09)
        w=.141
        floors=[]
        for j in range(4):
            t=j/3
            width=w*(1.0-.59*t)
            floors.append([(tx+width*cos(yaw+k*2*pi/3),ty+width*sin(yaw+k*2*pi/3),
                            gz+(head_z-gz)*t) for k in range(3)])
        for j,(bottom,top) in enumerate(zip(floors,floors[1:])):
            for k in range(3):
                a,b=bottom[k],bottom[(k+1)%3]
                c,d=top[k],top[(k+1)%3]
                cylinder(a,c,.014,.010,"reflectorIce",5)
                cylinder(a,b,.009,.009,"reflectorPanel",4)
                cylinder(a,d,.008,.007,"reflectorPanel",4)
        for k in range(3):
            cylinder(floors[-1][k],floors[-1][(k+1)%3],.010,.010,"reflectorIce",4)
        support=(tx,ty,head_z+.012)
        foot=(cx+.075*cos(phi),cy+.075*sin(phi),cabin_z)
        cylinder(support,foot,.009,.008,"reflectorCable",5)
    group("公开可见的中央馈源舱")
    profile(cx,cy,cabin_z-.054,[(0,.10,.083),(.034,.21,.15),(.082,.21,.15),(.10,.11,.082)],"reflectorWhite")
    box(cx,cy,cabin_z-.077,.115,.087,.028,"reflectorPanel")


# Cross sections from the buried tail to the raised blunt head. The curve and
# visible belly follow the aquarium's public entrance sculpture.
SHARK_RINGS = [
    (.07,.63,.70,.18,.13),(.03,.66,.89,.26,.20),(-.16,.51,1.12,.40,.25),
    (-.21,.32,1.42,.52,.33),(-.18,.09,1.76,.66,.40),(-.11,-.02,2.12,.77,.46),
    (.02,-.03,2.47,.77,.48),(.16,-.09,2.82,.74,.43),(.27,-.22,3.06,.62,.38),
    (.31,-.27,3.22,.50,.28),(.32,-.29,3.28,.13,.12),
]


def interpolate(t):
    pos=t*(len(SHARK_RINGS)-1)
    i=min(len(SHARK_RINGS)-2,int(pos))
    q=pos-i
    a,b,c,d=(SHARK_RINGS[max(0,i-1)],SHARK_RINGS[i],SHARK_RINGS[i+1],
             SHARK_RINGS[min(len(SHARK_RINGS)-1,i+2)])
    return tuple(.5*((2*v)+(-u+w)*q+(2*u-5*v+4*w-x)*q*q+(-u+3*v-3*w+x)*q*q*q)
                 for u,v,w,x in zip(a,b,c,d))


def shark_point(t, angle, offset=0):
    x,y,z,a,b=interpolate(t)
    p=Vector(interpolate(max(0,t-.001))[:3])
    q=Vector(interpolate(min(1,t+.001))[:3])
    axis=(q-p).normalized()
    lateral=(Vector((1,0,0))-axis*axis.x).normalized()
    dorsal=axis.cross(lateral)
    return tuple(Vector((x,y,z))+cos(angle)*(a+offset)*lateral+sin(angle)*(b+offset)*dorsal)


def shark_fin(label, root, outline, material, bottom):
    group(label)
    # Two cupped sides joined continuously along the fin edge.
    low=(root[0],root[1]-.036,root[2]-.009)
    high=(root[0],root[1]+.042,root[2]+.015)
    for a,b in zip(outline,outline[1:]+outline[:1]):
        face([high,a,b],material)
        face([low,b,a],bottom)


def choppy_wave(label, x, y, z, length, height, curl, phase):
    group(label)
    rows=[]
    for i in range(25):
        t=i/24
        rise=(.26+.74*max(0,sin(pi*t))**.83)*height*(.84+.15*cos(t*7.5+phase))
        xx=x+length*(t-.5)
        through=y+.083*sin(t*5.7+phase)
        at=[]
        for j in range(8):
            k=j/7
            yy=through+.22*k+curl*max(0,k-.56)**1.75*sin(t*pi)
            zz=z+rise*sin(k*1.73)+.035*sin(t*18+phase)*k
            at.append((xx,yy,zz))
        rows.append(at)
    for i,(a,b) in enumerate(zip(rows,rows[1:])):
        for j in range(7):
            m="waveCrest" if j==6 else "waveTeal" if j in (1,4) else "waveDeep" if i%5 else "waveShallow"
            face([a[j],b[j],b[j+1],a[j+1]],m)
    left,right=rows[0],rows[-1]
    face([*left,(left[-1][0],left[-1][1],z)],"waveDark")
    face([*right[::-1],(right[-1][0],right[-1][1],z)],"waveDark")


def coral(x,y,z,scale,seed):
    rng=Random(seed)
    group("入口海底珊瑚立饰")
    color=rng.choice(("coralOrange","coralRose","coralGold"))
    root=(x,y,z)
    for i in range(5):
        az=i*2*pi/5+rng.uniform(-.28,.28)
        arm=(x+cos(az)*scale*.31,y+sin(az)*scale*.17,z+scale*rng.uniform(.41,.54))
        tip=(x+cos(az)*scale*.63,y+sin(az)*scale*.34,z+scale*rng.uniform(.71,1.0))
        cylinder(root,arm,.045*scale,.035*scale,color,5)
        cylinder(arm,tip,.035*scale,.018*scale,color,5)
        branch=(tip[0]+cos(az+1.2)*scale*.19,tip[1]+sin(az+1.2)*scale*.10,tip[2]-.034)
        cylinder(arm,branch,.029*scale,.014*scale,color,5)


def chimelong_ocean_kingdom():
    base("oceanPlaza","gorgeCut",width=6.15,depth=4.25)
    # Two actual public doorways are modeled as arches above the stone plaza.
    group("鲸鲨馆主体与临广场入口")
    box(0,1.14,.365,5.41,1.74,.54,"waveDark")
    for cx,w in ((-.89,.39),(.51,.52)):
        annular_arch(cx,-.56,.60,w,.14,.38,"waveTeal",n=17)
        for s in (-1,1):
            box(cx+s*(w+.071),-.56,.365,.154,.37,.239,"waveDark")
        box(cx,-.244,.369,2*w+.28,.66,.082,"gorgeCut")
        box(cx, .20,.439,2*w+.24,.049,.67,"marineDark")
        box(cx,-.55,.361,2*w,.38,.023,"oceanPlazaLight")

    for data in ((-2.02,-.69,.38,1.86,.82,1.62,1.77),
                              (1.96,-.66,.38,1.92,.70,1.42,-.85),
                              (-1.25,-.38,.82,1.48,.58,1.19,.3),
                              (.94,-.43,.75,1.78,.65,1.22,-1.1),
                              (-.04,.44,.96,2.67,.55,1.30,.5),
                              (-.07,.71,.84,4.92,.37,1.2,1.4),
                              (0,1.07,.82,5.22,.35,1.09,-.4),
                              (.03,1.39,.80,5.15,.33,.81,2.4),
                              (-2.14,-.22,.60,1.27,.57,1.11,.88),
                              (2.01,-.16,.60,1.31,.51,1.09,.15)):
        choppy_wave("鲸鲨馆青蓝卷浪外墙",*data)

    label="昂首的立体鲸鲨"
    group(label)
    n,height_sections=44,28
    rows=[]
    for i in range(height_sections+1):
        t=i/height_sections
        rows.append([shark_point(t,2*pi*j/n) for j in range(n)])
    for i,(a,b) in enumerate(zip(rows,rows[1:])):
        v0=i/height_sections
        v1=(i+1)/height_sections
        for j in range(n):
            k=(j+1)%n
            u0,u1=j/n,(j+1)/n
            face([a[j],a[k],b[k],b[j]],"sharkSkin",[(u0,v0),(u1,v0),(u1,v1),(u0,v1)])
    face(rows[0][::-1],"marineShadow",[(.25,0)]*n)
    face(rows[-1],"sharkSkin",[(.06,.985)]*n)
    points=[shark_point(.917+.015*sin(j*pi/18),3.69+2.03*j/18,.004) for j in range(19)]
    plank_line("昂首鲸鲨吻部细纹",points,.009,"marineDark",5)

    for side in (-1,1):
        angle=0 if side>0 else pi
        x,y,z=shark_point(.65,angle,.012)
        outline=[(x-.04*side,y-.13,z+.12),(x+.38*side,y-.09,z+.085),
                 (x+.78*side,y+.021,z-.16),(x+1.05*side,y+.16,z-.53),
                 (x+.81*side,y+.27,z-.51),(x+.34*side,y+.16,z-.28),(x-.03*side,y+.15,z-.16)]
        shark_fin("外张的胸鳍",(x+.39*side,y+.04,z-.19),outline,"marineBlue","marineBlue")
        eye_angle=-.24 if side>0 else pi+.24
        a=shark_point(.86,eye_angle,.018)
        group("眼和鳃裂")
        sphere(*a,.051,.054,.044,"marineDark",s=10,n=5)
        sphere(a[0]+side*.010,a[1]-.039,a[2]+.016,.017,.012,.014,"reflectorWhite",s=7,n=4)
        for i in range(5):
            left=[shark_point(.677+i*.019,eye_angle-.38*side-.23*side*j/10,.005+.006*sin(j*pi/10))
                  for j in range(11)]
            plank_line("眼和鳃裂",left,.011,"marineDark",4)
    # The short dorsal fin faces away from the pavilion approach.
    a=shark_point(.52,pi/2)
    back=[(a[0]-.16,a[1],a[2]+.2),(a[0]-.04,a[1]+.22,a[2]+.15),
          (a[0]+.12,a[1]+.61,a[2]-.02),(a[0]+.14,a[1]+.49,a[2]-.16),
          (a[0]+.12,a[1]+.07,a[2]-.24)]
    shark_fin("背鳍",(a[0]+.03,a[1]+.28,a[2]-.02),back,"marineBlue","marineShadow")
    for i,(x,y,s) in enumerate(((-2.22,-1.30,.33),(-1.91,-1.15,.27),(-1.35,-1.12,.31),
                               (.05,-1.13,.27),(1.35,-1.17,.39),(1.67,-1.16,.29),(2.23,-.89,.33))):
        coral(x,y,.365,s,i+16)
    for i,(x,y,h) in enumerate(((-2.57,-.50,.62),(2.62,-.39,.67),(-2.62,.80,.77),(2.62,.69,.69))):
        palm(x,y,.365,h,81+i)
    group("广场浅蓝拼花")
    for i in range(34):
        t=2*pi*i/34
        u=2*pi*(i+1)/34
        def tile(a,r):
            return (.33+r*cos(a),-1.38+r*.40*sin(a),.364)
        face([tile(t,.92),tile(t,1.17),tile(u,1.17),tile(u,.92)],"oceanPlazaBlue")


def shark_skin_texture(bpy):
    """Create an embedded livery with mottled white spots and a lighter belly."""
    from array import array

    def linear(c):
        return (c/12.92) if c<=.04045 else ((c+.055)/1.055)**2.4

    n=384
    pixels=array("f")
    for y in range(n):
        t=y/n
        row=int(t*27)
        for x in range(n):
            u=x/n
            belly=smooth01((-sin(2*pi*u)-.11)/.92)
            speckle=.035*sin(x*2.16+y*3.82)+.055*sin(x*.51-y*.29)
            dark=(.145,.388,.552)
            pale=(.41,.66,.749)
            fx=(u*24+.5*(row%2))%1-.5
            fy=(t*27)%1-.49
            amount=max(0,.21-hypot(fx,fy))/0.15
            spot=smooth01(amount)*(.75-.27*belly)
            ribs=.018*sin(u*2*pi*16+t*2.7)
            for a,b in zip(dark,pale):
                v=a+(b-a)*belly+ribs+.034*speckle
                v=v*(1-spot)+(.92+.05*speckle)*spot
                pixels.append(linear(v))
            pixels.append(1.)
    image=bpy.data.images.new("原创鲸鲨斑点彩绘",width=n,height=n,alpha=False)
    image.colorspace_settings.name="sRGB"
    image.pixels.foreach_set(pixels)
    image.pack()
    return image
