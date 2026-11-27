"""Build, export, re-import and photograph a map-size Hall of Supreme Harmony."""
import hashlib
import json
import math
import struct
from collections import defaultdict
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector

HERE = Path(__file__).resolve().parent
GLB = HERE.parents[2] / 'app/public/models/gugong.glb'
MATERIALS = {}
PARTS = defaultdict(list)
RAIL_POSTS = set()
group = ''
KEEP_NATIONAL = True


def linear(c):
    c = c / 255
    return c / 12.92 if c < .04045 else ((c + .055) / 1.055) ** 2.4


def material(name, rgb, texture=None, roughness=.7):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    rgba = tuple(linear(i) for i in rgb) + (1,)
    mat.diffuse_color = rgba
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = rgba
    shader.inputs['Roughness'].default_value = roughness
    if texture:
        im = bpy.data.images.load(str(HERE / 'textures' / (texture + '.png')))
        im.pack()
        tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image = im
        mat.node_tree.links.new(tex.outputs['Color'], shader.inputs['Base Color'])
    MATERIALS[name] = mat


def face(points, mat, uv=None, *, export=True):
    if not uv:
        n = (Vector(points[1])-Vector(points[0])).cross(Vector(points[2])-Vector(points[0]))
        axis = max(range(3), key=lambda i: abs(n[i]))
        ix, iy = [(1,2),(0,2),(0,1)][axis]
        uv = [(p[ix]/4, p[iy]/4) for p in points]
    PARTS[group].append((points, mat, uv, KEEP_NATIONAL and export))


def box(x0,x1,y0,y1,z0,z1, mat):
    b=[(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)]
    t=[(x,y,z1) for x,y,z in b]
    face(b[::-1],mat,export=z0==0)
    face(t,mat)
    for i in range(4):
        j=(i+1)%4
        face([b[i],b[j],t[j],t[i]],mat)


def ridge(points, radius, mat, sides=5):
    """Low-sided continuous tube with mitred rings."""
    rings=[]
    for i,p in enumerate(points):
        direction=(Vector(points[min(i+1,len(points)-1)])-Vector(points[max(i-1,0)])).normalized()
        cross=direction.cross(Vector((0,0,1)))
        if cross.length < .01: cross=direction.cross(Vector((0,1,0)))
        cross.normalize()
        up=direction.cross(cross).normalized()
        rings.append([tuple(Vector(p)+radius*(cross*math.cos(a*math.tau/sides)+up*math.sin(a*math.tau/sides))) for a in range(sides)])
    face(rings[0][::-1],mat); face(rings[-1],mat)
    for lo,hi in zip(rings,rings[1:]):
        for a in range(sides):
            b=(a+1)%sides
            face([lo[a],lo[b],hi[b],hi[a]],mat)


def shaft(x,y,z,r,height,mat,n=8):
    ridge([(x,y,z),(x,y,z+height)],r,mat,n)


def rectangle_axis(a,b,w,t,h,mat):
    x0,x1=sorted((a[0],b[0])); y0,y1=sorted((a[1],b[1]))
    if x0==x1: x0-=w/2; x1+=w/2
    else: y0-=w/2; y1+=w/2
    box(x0,x1,y0,y1,t,t+h,mat)


def railing(a,b,z):
    global KEEP_NATIONAL
    length=math.dist(a,b)
    count=max(1,round(length/4.3))
    rectangle_axis(a,b,.33,z+.22,.49,'汉白玉')
    rectangle_axis(a,b,.43,z+.71,.13,'白石线脚')
    # Square balusters, with space above and below the panel, form the silhouette.
    for i in range(count+1):
        x=a[0]+(b[0]-a[0])*i/count; y=a[1]+(b[1]-a[1])*i/count
        key=(round(x,3),round(y,3),round(z,3))
        if key in RAIL_POSTS: continue
        RAIL_POSTS.add(key)
        KEEP_NATIONAL = i in (0,count) or i % 4 != 2
        box(x-.23,x+.23,y-.23,y+.23,z,z+1.25,'白石线脚')
        if i%2==0:
            face([(x-.3,y-.3,z+1.25),(x+.3,y-.3,z+1.25),(x,y,z+1.60)],'白石线脚')
            face([(x+.3,y-.3,z+1.25),(x+.3,y+.3,z+1.25),(x,y,z+1.60)],'白石线脚')
            face([(x+.3,y+.3,z+1.25),(x-.3,y+.3,z+1.25),(x,y,z+1.60)],'白石线脚')
            face([(x-.3,y+.3,z+1.25),(x-.3,y-.3,z+1.25),(x,y,z+1.60)],'白石线脚')
        KEEP_NATIONAL = True


def terraces():
    global group
    # Stair runs reach the rim of the previous stage and never overlap its balustrades.
    stages=[(43,-26,24,0,2.45,-30.7),(40.2,-22.5,21.7,2.45,5.05,-26.2),(37.5,-19.2,19.7,5.05,7.75,-22.7)]
    for index,(w,f,b,base,z,start) in enumerate(stages):
        group=f'{index+1} 层须弥座与石栏'
        box(-w,w,f,b,base,z,'汉白玉')
        for dz,expand,height in [(.10,.16,.23),(z-base-.46,.21,.13),(z-base-.24,.32,.24)]:
            box(-w-expand,w+expand,f-expand,b+expand,base+dz,base+dz+height,'白石线脚')
        box(-w+.12,w-.12,f+.12,b-.12,z,z+.045,'地面金砖')
        rf=f+.43; rw=w-.5; rb=b-.5
        cuts=[-rw,-24.7,-19.3,-6.2,6.2,19.3,24.7,rw]
        for lo,hi in zip(cuts[::2],cuts[1::2]):
            railing((lo,rf),(hi,rf),z)
        railing((-rw,rb),(rw,rb),z)
        for sign in (-1,1): railing((sign*rw,rf),(sign*rw,rb),z)
        # Side flights and two central stair runs leave a clear royal ramp in the middle.
        for cx,width in [(-22,5.5),(-3.6,4.5),(3.6,4.5),(22,5.5)]:
            steps=7
            for i in range(steps):
                y0=start+(f-start)*i/steps
                y1=start+(f-start)*(i+1)/steps+.01
                top=base+(z-base)*(i+1)/steps
                # Only exposed tread and riser faces are required over the solid stair slab.
                x0=cx-width/2; x1=cx+width/2
                face([(x0,y0,top),(x1,y0,top),(x1,y1,top),(x0,y1,top)],'白石线脚')
                face([(x0,y0,top-(z-base)/steps),(x1,y0,top-(z-base)/steps),(x1,y0,top),(x0,y0,top)],'汉白玉')
            for edge in (cx-width/2,cx+width/2):
                face([(edge,start,base),(edge,f,base),(edge,f,z)],'汉白玉')
                ridge([(edge,start,base+.2),(edge,f,z+.2)],.16,'白石线脚',4)
        face([(-1.36,start,base+.14),(1.36,start,base+.14),(1.36,f,z+.15),(-1.36,f,z+.15)],'御道龙纹',[(0,0),(1,0),(1,1),(0,1)])


def facade_panel(x,y,u,z0,z1,mat):
    # A facade panel is oriented consistently from lower-left to upper-right.
    p=(x+u[0],y+u[1])
    face([(x,y,z0),(p[0],p[1],z0),(p[0],p[1],z1),(x,y,z1)],mat,[(0,0),(1,0),(1,1),(0,1)])


def hall():
    global group, KEEP_NATIONAL
    group='殿身／朱柱与十一间隔扇'
    # Columns enclose eleven bays across and five deep. The door walls sit behind the colonnade.
    xw,yw=29,13.2; floor=8.25
    box(-31,31,-15.5,15.5,7.80,floor,'地面金砖')
    box(-27,27,-10.8,10.8,floor,16.55,'朱漆')
    for sign in (-1,1):
        y=sign*yw
        for j in range(12):
            x=-xw+2*xw*j/11
            shaft(x,y,floor,.72,.43,'汉白玉')
            shaft(x,y,floor+.4,.50,7.7,'朱漆',10)
        for j in range(11):
            x=-26.9+j*53.8/11
            facade_panel(x if sign==-1 else x+53.8/11, sign*10.83,(-sign*53.8/11,0),floor+.14,15.0,'朱金菱花')
        for j in range(1,5):
            y=-yw+2*yw*j/5
            shaft(sign*xw,y,floor,.70,.43,'汉白玉')
            shaft(sign*xw,y,floor+.4,.50,7.7,'朱漆',10)
        for j in range(5):
            sy=-10.8+j*21.6/5
            facade_panel(sign*27.03,sy if sign==1 else sy+21.6/5,(0,sign*21.6/5),floor+.14,14.85,'朱金菱花')
    group='檐下／斗栱、彩画和匾额'
    box(-30.2,30.2,-14.4,14.4,15.7,16.7,'翡翠檐枋')
    for side in (-1,1):
        for j in range(11):
            start=-30+j*60/11
            facade_panel(start if side==-1 else start+60/11,side*14.42,(-side*60/11,0),15.15,16.5,'和玺彩画')
        for j in range(5):
            sy=-14.4+j*28.8/5
            facade_panel(side*30.23,sy if side==1 else sy+28.8/5,(0,side*28.8/5),15.15,16.5,'和玺彩画')
        brackets=23
        for j in range(brackets):
            KEEP_NATIONAL = j % 2 == 0
            x=-29+j*58/(brackets-1)
            box(x-.43,x+.43,side*14.4-.4,side*14.4+.4,16.45,17.0,'翡翠檐枋')
            box(x-.68,x+.68,side*14.4-.55,side*14.4+.55,16.96,17.30,'青绿斗栱')
        KEEP_NATIONAL = True
    facade_panel(-2.4,-14.74,(4.8,0),14.1,16,'匾额')


def roofs():
    global group
    for upper in (False,True):
        group=('上檐／庑殿正脊' if upper else '下檐／腰檐')
        if upper:
            x0,y0,x1,y1=32.6,16.4,17.5,0; z0,z1=22.35,31.5
        else:
            x0,y0,x1,y1=35.1,18.1,26.8,10.5; z0,z1=17.75,20.95

        def position(side,s,t):
            x=x0+(x1-x0)*t; y=y0+(y1-y0)*t
            # Edge ends curl gently upward; the field stays broad and only slightly concave.
            z=z0+(z1-z0)*(.63*t+.37*t*t)+1.12*(abs(s)**5)*(1-t)**2
            return ((s*x,-y,z),(x,s*y,z),(-s*x,y,z),(-x,-s*y,z))[side]
        for side in range(4):
            ns=12 if side%2==0 else 6
            samples=[-1+2*i/ns for i in range(ns+1)]
            ts=[0,.23,.51,.76,1]
            def uv(point,t):
                direction=(point[0],point[1],-point[0],-point[1])[side]
                return direction/1.8,t*(y0-y1)/2.55
            for s0,s1 in zip(samples,samples[1:]):
                a,b=position(side,s0,0),position(side,s1,0)
                da=(a[0],a[1],a[2]-.43);db=(b[0],b[1],b[2]-.43)
                face([a,da,db,b],'琉璃檐口')
                # Actual overhang underside encloses the eaves over the red columns.
                p=(da[0]*.80,da[1]*.80,z0-.62);q=(db[0]*.80,db[1]*.80,z0-.62)
                face([db,da,p,q],'暗红椽底')
                for t0,t1 in zip(ts,ts[1:]):
                    corners=[position(side,s0,t0),position(side,s1,t0),position(side,s1,t1),position(side,s0,t1)]
                    tt=[t0,t0,t1,t1]
                    if corners[2]==corners[3]: corners.pop(); tt.pop()
                    face(corners,'黄琉璃瓦',[uv(p,t) for p,t in zip(corners,tt)])
            positions=[position(side,1,t) for t in ts]
            positions=[(x,y,z+.10) for x,y,z in positions]
            ridge(positions,.23 if upper else .19,'鎏黄脊瓦')
            # A reduced set of tiny silhouettes suggests the ridge procession at miniature scale.
            for animal in range(4):
                t=.04+animal*.049
                x,y,z=position(side,1,t)
                shaft(x,y,z+.12,.20-.015*animal,.32+.04*animal,'鎏黄脊瓦',4)
        if upper:
            ridge([(-17.7,0,31.6),(17.7,0,31.6)],.40,'鎏黄脊瓦',8)
            for sign in (-1,1):
                # Profile of each chiwen curls up and back toward the ridge.
                outline=[(15.9,31.46),(18.15,31.42),(18.8,31.85),(18.62,32.40),(18.26,33.10),(18.30,33.66),(17.68,33.98),(17.30,33.58),(17.47,33.21),(17.71,33.04),(17.39,32.74),(16.92,32.48),(16.49,32.20)]
                lo=[(x*sign,-.30,z) for x,z in outline];hi=[(x*sign,.30,z) for x,z in outline]
                if sign==-1: lo.reverse();hi.reverse()
                face(lo,'鎏黄脊瓦');face(hi[::-1],'鎏黄脊瓦')
                for i in range(len(lo)):
                    j=(i+1)%len(lo);face([lo[i],hi[i],hi[j],lo[j]],'鎏黄脊瓦')
        else:
            box(-28.4,28.4,-12.7,12.7,20.3,22.45,'暗红椽底')
            for side in (-1,1):
                for j in range(11):
                    x=-28.4+j*56.8/11
                    facade_panel(x if side==-1 else x+56.8/11,side*12.72,(-side*56.8/11,0),20.32,22.30,'和玺彩画')


def make_meshes():
    for name, patches in PARTS.items():
        vertices=[];faces=[];used={}
        for coords,mat,uv,keep in patches:
            start=len(vertices);vertices.extend(coords)
            faces.append(list(range(start,len(vertices))))
            if mat not in used: used[mat]=len(used)
        mesh=bpy.data.meshes.new(name)
        mesh.from_pydata(vertices,[],faces);mesh.update()
        obj=bpy.data.objects.new(name,mesh)
        bpy.context.scene.collection.objects.link(obj)
        for mat in used: mesh.materials.append(MATERIALS[mat])
        uv_layer=mesh.uv_layers.new(name='建筑UV')
        detail=mesh.attributes.new('近景细部','BOOLEAN','FACE')
        for poly,(_,mat,uv,keep) in zip(mesh.polygons,patches):
            detail.data[poly.index].value=not keep
            poly.material_index=used[mat]
            for idx,coord in zip(poly.loop_indices,uv):
                uv_layer.data[idx].uv=coord


def get_stats():
    blob=GLB.read_bytes()
    length=struct.unpack_from('<I',blob,12)[0];doc=json.loads(blob[20:20+length])
    prim=[p for m in doc['meshes'] for p in m['primitives']]
    a=doc['accessors']; tri=sum(a[p['indices']]['count']//3 for p in prim)
    bounds=[a[p['attributes']['POSITION']] for p in prim]
    low=[min(v['min'][i] for v in bounds) for i in range(3)]
    high=[max(v['max'][i] for v in bounds) for i in range(3)]
    assert all('bufferView' in im for im in doc['images'])
    assert not doc.get('cameras') and not doc.get('animations')
    assert abs(low[1])<1e-5 and 2000<=tri<=8000, (low, high, tri)
    return dict(id='gugong',name='北京故宫·太和殿',file=GLB.name,version='national-v1',source='https://www.dpm.org.cn/explore/building/236465.html',sourceCopy='data/landmarks/gugong/source.blend',triangles=tri,bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),materials=len(doc['materials']),embeddedImages=len(doc['images']),bounds=dict(min=low,max=high),coordinateConvention='glTF Y-up, +Z south-facing facade; origin directly below hall ridge midpoint')


def area(name,where,energy,size):
    light=bpy.data.lights.new(name,'AREA');light.energy=energy;light.shape='DISK';light.size=size
    obj=bpy.data.objects.new(name,light);bpy.context.scene.collection.objects.link(obj)
    obj.location=where;obj.rotation_euler=(Vector((0,0,7))-obj.location).to_track_quat('-Z','Y').to_euler()


def previews():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(GLB))
    scene=bpy.context.scene
    assert any(o.type=='MESH' for o in bpy.context.selected_objects)
    assert all(im.packed_file for im in bpy.data.images if im.source=='FILE' and im.users)
    scene.render.engine='CYCLES';scene.cycles.samples=16;scene.cycles.use_denoising=True
    scene.render.resolution_x=880;scene.render.resolution_y=650;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.view_settings.view_transform='AgX'
    scene.world=bpy.data.worlds.new('暖灰影棚');scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.78,.83,.9,1);bg.inputs[1].default_value=.38
    bpy.ops.mesh.primitive_plane_add(size=2500,location=(0,0,-.03));floor=bpy.context.object
    floor_mat=bpy.data.materials.new('背景');floor_mat.diffuse_color=(.75,.73,.66,1);floor.data.materials.append(floor_mat)
    area('主光',(-48,-70,98),110000,65);area('柔光',(70,-25,52),35000,60);area('轮廓光',(40,65,72),55000,55)
    cdata=bpy.data.cameras.new('正交相机');cdata.type='ORTHO'
    cam=bpy.data.objects.new('相机',cdata);scene.collection.objects.link(cam);scene.camera=cam
    for name,location,scale,z in [('正面',(0,-150,25),103,13),('右侧',(158,0,24),84,13),('侧前方',(94,-139,83),106,11)]:
        cam.location=location;cam.rotation_euler=(Vector((0,-2,z))-cam.location).to_track_quat('-Z','Y').to_euler()
        cdata.ortho_scale=scale;cdata.clip_end=2000
        scene.render.filepath=str(HERE/'renders'/(name+'.png'));bpy.ops.render.render(write_still=True)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    material('汉白玉',(214,208,189),'marble')
    material('白石线脚',(218,214,196))
    material('御道龙纹',(207,202,183),'imperial-ramp')
    material('地面金砖',(205,197,177),'flagstones')
    material('朱漆',(157,55,41),roughness=.46)
    material('暗红椽底',(104,48,42))
    material('青绿斗栱',(67,108,101))
    material('翡翠檐枋',(43,78,81))
    material('和玺彩画',(66,111,99),'bracket-paint')
    material('朱金菱花',(154,64,42),'lattice-doors')
    material('匾额',(38,54,66),'taihe-plaque')
    material('琉璃檐口',(190,120,52),roughness=.42)
    material('黄琉璃瓦',(218,158,64),'amber-tiles',roughness=.43)
    material('鎏黄脊瓦',(218,150,69),roughness=.42)
    terraces();hall();roofs();make_meshes()
    scene=bpy.context.scene
    for area_ in bpy.context.screen.areas:
        if area_.type=='VIEW_3D':
            region=area_.spaces.active.region_3d
            region.view_distance=115; region.view_location=(0,0,11)
            region.view_rotation=(Vector((0,0,11))-Vector((90,-145,90))).to_track_quat('-Z','Y')
    bpy.ops.wm.save_as_mainfile(filepath=str(HERE/'source.blend'),compress=True)
    export_master()

def export_master():
    # The low-detail faces are selected on a working copy; hand-editing a vertex
    # in the saved Blender master therefore also changes the exported model.
    scene=bpy.context.scene
    for obj in scene.objects:
        if obj.type!='MESH':
            continue
        attr=obj.data.attributes.get('近景细部')
        if not attr:
            continue
        hi_only=[i for i,v in enumerate(attr.data) if v.value]
        obj.data.attributes.remove(attr)
        bm=bmesh.new();bm.from_mesh(obj.data);bm.faces.ensure_lookup_table()
        bmesh.ops.delete(bm,geom=[bm.faces[i] for i in hi_only],context='FACES')
        bm.to_mesh(obj.data);bm.free()
    bpy.ops.object.select_all(action='SELECT');bpy.context.view_layer.objects.active=next(iter(scene.objects))
    bpy.ops.object.join(); asset=bpy.context.view_layer.objects.active;asset.name='太和殿_全国版'
    bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_selection=True,export_apply=True,export_yup=True,export_cameras=False,export_lights=False)
    stats=get_stats();(HERE/'stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
    print('TAIHE VERIFIED',stats,flush=True)
    previews()


if __name__=='__main__':
    import sys
    if '--from-master' in sys.argv:
        export_master()
    else:
        main()
