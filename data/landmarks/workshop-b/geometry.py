"""Mesh construction in Blender metres (Z up, front -Y). Components stay editable in the master."""
import math, random
from pathlib import Path
import bpy
from mathutils import Vector
PI=math.pi
TAU=math.tau
R=random.Random()
ROOT=Path(__file__).resolve().parent
mats={}
groups={}
active_group='01 · 地景'

def reset(seed):
    global active_group
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    mats.clear();groups.clear();R.seed(seed);active_group='01 · 地景'

def group(name):
    global active_group
    active_group=name
    if name not in groups:
        c=bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
        groups[name]=c

def mat(key):
    if key not in mats:
        m=bpy.data.materials.new(key);m.use_nodes=True
        tex=m.node_tree.nodes.new('ShaderNodeTexImage')
        im=bpy.data.images.load(str(ROOT/'textures'/(key+'.jpg')),check_existing=True);im.pack()
        tex.image=im
        shader=m.node_tree.nodes.get('Principled BSDF')
        rough=.32 if key in ('steel','gold','river','glaze','jade','clear','fall') else .78
        shader.inputs['Roughness'].default_value=rough
        if key in ('steel','gold'):shader.inputs['Metallic'].default_value=.5
        m.node_tree.links.new(tex.outputs['Color'],shader.inputs['Base Color'])
        mats[key]=m
    return mats[key]

def mesh(name,verts,faces,key,smooth=False,uvscale=1.0):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
    coords=[Vector(p) for p in verts]
    uv=me.uv_layers.new(name='细部纹理')
    for p in me.polygons:
        axis=max(range(3),key=lambda i:abs(p.normal[i]))
        a,b=[(1,2),(0,2),(0,1)][axis]
        for li in p.loop_indices:
            v=coords[me.loops[li].vertex_index];uv.data[li].uv=(v[a]*uvscale,v[b]*uvscale)
        p.use_smooth=smooth
    ob=bpy.data.objects.new(name,me);group(active_group);groups[active_group].objects.link(ob)
    me.materials.append(mat(key))
    return ob

def box(name,center,dims,key):
    x,y,z=center; a,b,c=[i/2 for i in dims]
    verts=[(x+sx*a,y+sy*b,z+sz*c) for sz in (-1,1) for sy in (-1,1) for sx in (-1,1)]
    faces=[(0,2,3,1),(4,5,7,6),(0,1,5,4),(1,3,7,5),(3,2,6,7),(2,0,4,6)]
    return mesh(name,verts,faces,key)

def loft(name,rings,key,smooth=False,caps=True):
    n=len(rings[0]);vs=[p for ring in rings for p in ring];faces=[]
    for k in range(len(rings)-1):
        for i in range(n):
            j=(i+1)%n;faces.append((k*n+i,k*n+j,(k+1)*n+j,(k+1)*n+i))
    if caps:faces+=[tuple(reversed(range(n))),tuple(range(len(vs)-n,len(vs)))]
    return mesh(name,vs,faces,key,smooth)

def ellipse(name,center,radii,key,nu=14,nv=9):
    x,y,z=center;a,b,c=radii
    rows=[]
    for j in range(1,nv):
        lat=-PI/2+PI*j/nv
        rows.append([(x+a*math.cos(lat)*math.cos(i*TAU/nu),y+b*math.cos(lat)*math.sin(i*TAU/nu),z+c*math.sin(lat)) for i in range(nu)])
    vs=[(x,y,z-c)]+[p for row in rows for p in row]+[(x,y,z+c)]
    face=[(0,1+(i+1)%nu,1+i) for i in range(nu)]
    for j in range(len(rows)-1):
        for i in range(nu):
            k=(i+1)%nu;face.append((1+j*nu+i,1+j*nu+k,1+(j+1)*nu+k,1+(j+1)*nu+i))
    face += [(len(vs)-1-nu+i,len(vs)-1-nu+(i+1)%nu,len(vs)-1) for i in range(nu)]
    return mesh(name,vs,face,key,True,2)

def stack(name,cx,cy,profile,key,n=12,phase=0,smooth=False):
    rows=[[(cx+rx*math.cos(i*TAU/n+phase),cy+ry*math.sin(i*TAU/n+phase),z) for i in range(n)] for rx,ry,z in profile]
    return loft(name,rows,key,smooth)

def rod(name,start,end,radius,key,n=8,r2=None):
    a,b=Vector(start),Vector(end);d=(b-a).normalized();u=d.cross(Vector((0,0,1)) if abs(d.z)<.94 else Vector((0,1,0))).normalized();v=d.cross(u)
    return loft(name,[[tuple(c+r*(u*math.cos(i*TAU/n)+v*math.sin(i*TAU/n))) for i in range(n)] for c,r in ((a,radius),(b,r2 if r2 is not None else radius))],key,True)

def tube(name,points,radius,key,n=6):
    p=[Vector(i) for i in points];rings=[]
    for j,c in enumerate(p):
        d=(p[min(len(p)-1,j+1)]-p[max(0,j-1)]).normalized()
        u=d.cross(Vector((0,0,1)) if abs(d.z)<.94 else Vector((0,1,0))).normalized();v=d.cross(u)
        rings.append([tuple(c+radius*(u*math.cos(i*TAU/n)+v*math.sin(i*TAU/n))) for i in range(n)])
    return loft(name,rings,key,True)

def island(name,cx,cy,rx,ry,h,key,n=22,top=1):
    shapes=[1+R.uniform(-.09,.09) for i in range(n)]
    rings=[]
    for mul,z,noise in ((.89,0,0),(1,h*.42,.09),(top,h,.035)):
        rings.append([(cx+rx*mul*shapes[i]*math.cos(i*TAU/n),cy+ry*mul*shapes[i]*math.sin(i*TAU/n),z*(1+noise*math.sin(i*2.1))) for i in range(n)])
    return loft(name,rings,key)

def conifer(x,y,z,s,key='pines'):
    rod('树干',(x,y,z),(x,y,z+.88*s),.055*s,'wood',6)
    for k in range(3):
        rad=(.32-.052*k)*s; z0=z+(.16+.22*k)*s
        stack('针叶层',x,y,[(rad,rad,z0),(.65*rad,.65*rad,z0+.11*s),(.008,.008,z0+.49*s)],key,8,phase=k*.32)

def roof(name,x,y,z,rx,ry,ht,key='bluegray',hips=.52):
    # Rectangular hip roof with rising eaves, sagging slope and a proper horizontal ridge.
    per=6
    def ring(sx,sy,base,camber):
        out=[]
        for side in range(4):
            for k in range(per):
                t=-1+2*k/per
                a,b=[(t,-1),(1,t),(-t,1),(-1,-t)][side]
                edge=(abs(t)**3)
                out.append((x+a*sx,y+b*sy,base+camber*edge))
        return out
    topx=max(rx*hips,.04)
    rs=[ring(rx*.975,ry*.975,z-.075*ht,.15*ht),ring(rx,ry,z,.17*ht),ring(rx*.76+topx*.24,ry*.64,z+.16*ht,.06*ht),ring(rx*.49+topx*.51,ry*.30,z+.49*ht,.018*ht),ring(topx,ry*.018,z+ht,0)]
    loft(name,rs,key)
    rod('正脊',(x-topx,y,z+ht*1.015),(x+topx,y,z+ht*1.015),.045*ht,key,8)
    for ax in (-1,1):
        for ay in (-1,1):
            points=[r[([0,per,2*per,3*per][{(-1,-1):0,(1,-1):1,(1,1):2,(-1,1):3}[(ax,ay)]])] for r in rs[1:]]
            tube('垂脊',points,.028*ht,key,5)
    return z+ht

def archwall(name,x,y,width,thick,zbase,height,r,zc,key,n=24):
    # Solid flank panels and a curved arch soffit; the central opening is real empty space.
    for sign in (-1,1):
        box('城墙侧体',(x+sign*(width/4+r/2),y,zbase+height/2),(width/2-r,thick,height),key)
    v=[];f=[]
    for i in range(n+1):
        phi=PI-i*PI/n; xx=x+r*math.cos(phi);zz=zc+r*math.sin(phi)
        v.extend([(xx,y-thick/2,zz),(xx,y+thick/2,zz),(xx,y+thick/2,zbase+height),(xx,y-thick/2,zbase+height)])
    for i in range(n):
        for j in (0,1,2,3):
            k=(j+1)%4;f.append((4*i+j,4*(i+1)+j,4*(i+1)+k,4*i+k))
    return mesh(name,v,f,key)

def plaque(name,x,y,z,w,h,key):
    vs=[(x-w/2,y,z-h/2),(x+w/2,y,z-h/2),(x+w/2,y,z+h/2),(x-w/2,y,z+h/2)]
    ob=mesh(name,vs,[(0,1,2,3)],key)
    for loop,coord in zip(ob.data.uv_layers.active.data,((0,0),(1,0),(1,1),(0,1))):
        loop.uv=coord

def shrub(name,x,y,z,s,key):
    # A fractured, overlapping canopy with a shaded underside and irregular silhouette.
    nv=9
    rough=[R.uniform(.76,1.21) for _ in range(nv)]
    rows=[]
    for at,r,zoff in [(0,.69,-.22),(.11,1,0),(.25,.72,.41),(.30,.24,.65)]:
        rows.append([(x+s*r*rough[i]*math.cos(i*TAU/nv+at),y+s*r*.77*rough[i]*math.sin(i*TAU/nv+at),z+(zoff+.09*math.sin(i*3.8+at))*s) for i in range(nv)])
    return loft(name,rows,key)
