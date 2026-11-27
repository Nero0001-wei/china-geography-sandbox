"""Build and render Huangshan's Greeting Guest Pine in Blender 5.x.

Run from any directory with blender -b -t 4 --factory-startup --python build.py.
Use -- --render-only to re-render an existing web GLB without replacing the master.
"""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import math
import random
import struct
import sys

import bpy
from mathutils import Vector

HOME = Path(__file__).resolve().parent
OUTPUT = HOME.parents[2] / 'app/public/models/huangshan.glb'
SEED = 7255
rng = random.Random(SEED)
TAU = math.tau
ZERO = Vector((0, 0, 0))
UP = Vector((0, 0, 1))


def mesh_object(name, points, faces, material, collection, uvs=None, smooth=False):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(points, [], faces)
    mesh.materials.append(material)
    mesh.update()
    if uvs:
        layer = mesh.uv_layers.new(name='UVMap')
        for poly, corners in zip(mesh.polygons, uvs):
            for i, coord in zip(poly.loop_indices, corners):
                layer.data[i].uv = coord
    if smooth:
        for face in mesh.polygons:
            face.use_smooth = True
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    return obj


def material(name, color, texture=None, alpha=False):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Roughness'].default_value = .9
    shader.inputs['Base Color'].default_value = (*color, 1)
    shader.inputs['Specular IOR Level'].default_value = .19
    mat.diffuse_color = (*color, 1)
    if texture:
        tex = mat.node_tree.nodes.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(HOME / 'textures' / texture), check_existing=True)
        tex.image.pack()
        mat.node_tree.links.new(tex.outputs['Color'], shader.inputs['Base Color'])
        if alpha:
            # A hard mask glTF can render depth-correctly even with overlapping crowns.
            threshold = mat.node_tree.nodes.new('ShaderNodeMath')
            threshold.operation = 'GREATER_THAN'
            threshold.inputs[1].default_value = .42
            mat.node_tree.links.new(tex.outputs['Alpha'], threshold.inputs[0])
            mat.node_tree.links.new(threshold.outputs[0], shader.inputs['Alpha'])
            mat.use_backface_culling = False
    return mat


def make_collection(name):
    group = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(group)
    return group


def planar_mapping(vertices, faces, tile):
    coords = []
    for face in faces:
        pts = [Vector(vertices[i]) for i in face]
        n = (pts[1]-pts[0]).cross(pts[2]-pts[0])
        main = max(range(3), key=lambda i: abs(n[i]))
        axes = [(1,2), (0,2), (0,1)][main]
        coords.append([(p[axes[0]]/tile, p[axes[1]]/tile) for p in pts])
    return coords


def rock(name, x, y, rx, ry, low, high, tilt, segments, col, stone):
    # Vertical joints, open shoulders and unequal-radius rings shape the Yuping granite.
    start = rng.random()*6
    outline = []
    for i in range(segments):
        angle = start + TAU*(i+rng.uniform(-.16,.16))/segments
        outline.append((angle, rng.uniform(.86,1.08), rng.uniform(-.12,.12)))
    verts = []
    for k, (t,scale) in enumerate([(0,.89),(.28,1.0),(.71,.91),(.91,.73),(1,.39)]):
        for a, base_radius, rough in outline:
            r = base_radius*scale*(1+rng.uniform(-.05,.05))
            px, py = x+math.cos(a)*rx*r, y+math.sin(a)*ry*r
            z=low+(high-low)*t
            if k:
                z+=((high-low)*rough + (px-x)*tilt[0] + (py-y)*tilt[1])*min(1,t*2.1)
            verts.append((px,py,max(low,z)))
    faces=[tuple(range(segments-1,-1,-1))]
    for k in range(4):
        for i in range(segments):
            j=(i+1)%segments
            f=(k*segments+i,k*segments+j,(k+1)*segments+j,(k+1)*segments+i)
            faces.extend([(f[0],f[1],f[2]),(f[0],f[2],f[3])])
    peak=len(verts)
    verts.append((x+.05*rx,y+.03*ry,high+.04*(high-low)))
    faces.extend([(4*segments+i,4*segments+(i+1)%segments,peak) for i in range(segments)])
    obj=mesh_object(name,verts,faces,stone,col,planar_mapping(verts,faces,1.17),smooth=True)
    obj.data.set_sharp_from_angle(angle=math.radians(43))
    return obj


def tube(name, coords, radii, mat, col, sides=6):
    pts=[Vector(p) for p in coords]
    vertices=[]
    faces=[]
    uv=[]
    lengths=[0]
    for a,b in zip(pts,pts[1:]):
        lengths.append(lengths[-1]+(b-a).length)
    prev=None
    for i,(pt,r) in enumerate(zip(pts,radii)):
        tangent=(pts[min(i+1,len(pts)-1)]-pts[max(i-1,0)]).normalized()
        xaxis=(prev - tangent*tangent.dot(prev)).normalized() if prev is not None else tangent.orthogonal().normalized()
        yaxis=tangent.cross(xaxis).normalized()
        prev=xaxis
        for j in range(sides):
            a=TAU*j/sides+.06*math.sin(i*.8)
            jitter=1+.07*math.sin(3*a+i*.17)
            v=pt+jitter*r*(xaxis*math.cos(a)+yaxis*math.sin(a))
            vertices.append(v)
    for k in range(len(pts)-1):
        for j in range(sides):
            a=k*sides+j
            b=k*sides+(j+1)%sides
            faces.append((a,b,b+sides,a+sides))
            u0,u1=j/sides,(j+1)/sides
            v0,v1=lengths[k]/1.1,lengths[k+1]/1.1
            uv.append([(u0,v0),(u1,v0),(u1,v1),(u0,v1)])
    tip=tuple(range((len(pts)-1)*sides,len(pts)*sides))
    faces.append(tip)
    uv.append([(.5+.4*math.cos(TAU*j/sides),.5+.4*math.sin(TAU*j/sides)) for j in range(sides)])
    return mesh_object(name,vertices,faces,mat,col,uv,smooth=True)


def fork(start, end, gauge, bark, col, name):
    start,end = Vector(start),Vector(end)
    d=end-start
    perpendicular=Vector((-d.y,d.x,0)).normalized()
    mid=start+d*.43+perpendicular*rng.uniform(-.11,.11)
    mid.z-=min(.14,d.length*.10)
    tube(name,[start,mid,end],[gauge,gauge*.69,gauge*.25],bark,col,5)


def crown(center, size, canopy, bark, sprays, col, label):
    """Opaque tapered core plus arched, alpha-tested shoots keep volume and fine edges."""
    sx,sy,sz=size
    center=Vector(center)
    n=9
    verts=[]
    shape=[rng.uniform(.81,1.12) for _ in range(n)]
    theta=rng.uniform(0,TAU)
    for height,ring in [(-.09,.46),(.14,.79),(.60,.60)]:
        for j,factor in enumerate(shape):
            a=theta+TAU*j/n
            verts.append(tuple(center+Vector((ring*sx*factor*math.cos(a),ring*sy*factor*math.sin(a),
                                              sz*(height+rng.uniform(-.12,.12))))))
    faces=[tuple(range(n-1,-1,-1))]
    for k in range(2):
        for j in range(n):
            v=k*n+j
            w=k*n+(j+1)%n
            faces.append((v,w,w+n,v+n))
    peak=len(verts)
    verts.append(tuple(center+Vector((.11*sx,-.08*sy,.85*sz))))
    faces.extend([(2*n+j,2*n+(j+1)%n,peak) for j in range(n)])
    mesh_object(label+' · 密针冠心',verts,faces,canopy,col,uvs=planar_mapping(verts,faces,.39),smooth=True)
    # Each leaf card is an arch with a narrow rising tip, textured with real cutouts.
    verts, faces, uvs=[],[],[]
    for j in range(12):
        angle=theta+TAU*j/12+rng.uniform(-.22,.22)
        d=Vector((math.cos(angle)*sx,math.sin(angle)*sy,0))*rng.uniform(.83,1.14)
        normal=Vector((-math.sin(angle)*sx,math.cos(angle)*sy,0))*rng.uniform(.24,.39)
        origin=center+Vector((0,0,sz*rng.uniform(.08,.35)))
        tilt=rng.uniform(-.050,.055)
        for h,width,z in [(0,.39,.18),(.56,1,.60),(1,.86,.34)]:
            mid=origin+d*h+UP*sz*z
            for side in (-1,1):
                verts.append(tuple(mid+side*width*(normal + tilt*UP)))
        idx=len(verts)-6
        for k in range(2):
            a=idx+2*k
            faces.append((a,a+1,a+3,a+2))
            v0,v1=[(0,.55),(.55,1)][k]
            uvs.append([(0,v0),(1,v0),(1,v1),(0,v1)])
    # Rising tufts add needle tips along the silhouette at eye level.
    for j in range(3):
        angle=theta+TAU*(j+.4)/3
        d=Vector((math.cos(angle)*sx,math.sin(angle)*sy,0))
        side=Vector((-math.sin(angle)*sx,math.cos(angle)*sy,0))*.30
        bottom=center+d*.53+UP*sz*.20
        tip=bottom+d*.36+UP*sz*(1.02+.13*j)
        idx=len(verts)
        verts.extend([tuple(bottom-side*.78),tuple(bottom+side*.78),tuple(tip+side),tuple(tip-side)])
        faces.append((idx,idx+1,idx+2,idx+3))
        uvs.append([(0,0),(1,0),(1,1),(0,1)])
    mesh_object(label+' · 放射针束',verts,faces,sprays,col,uvs)


def terrain(groups,mats):
    rock('连体崖座',.10,.22,2.18,1.35,0,1.00,(-.17,.12),17,groups['rock'],mats['stone'])
    rock('青狮石后侧脊',-.73,.46,.76,.72,.10,2.1,(-.22,.24),12,groups['rock'],mats['stone'])
    rock('主干岩隙',-.23,.08,.84,.75,.15,1.27,(-.16,.13),11,groups['rock'],mats['stone'])
    rock('下层岩肩',1.22,.13,.89,.82,.03,.78,(-.25,.12),10,groups['rock'],mats['stone'])
    rock('侧面节理',-1.20,-.05,.49,.59,.02,1.46,(.04,.22),9,groups['rock'],mats['stone'])
    rock('前沿石肩',.18,-.69,.69,.54,.02,.72,(-.23,.15),9,groups['rock'],mats['stone'])
    for i,(x,y,z,s) in enumerate([(-1.4,.28,1.20,.27),(-.82,-.40,.88,.28),(.55,-.33,.98,.32),
                                  (.88,.44,.97,.24),(1.46,.34,.66,.30),(.2,.78,1.10,.33)]):
        rock('岩隙苔斑 '+str(i+1),x,y,s,s*.66,z-.10,z+.04,(0,0),7,groups['rock'],mats['moss'])


def tree(groups,mats):
    bark=mats['bark']
    col=groups['wood']
    trunk=[(0,0,1.13),(-.06,0,1.48),(.01,-.025,1.90),(.14,.035,2.44),
           (.17,.055,2.90),(.25,.065,3.42),(.30,.06,3.89),(.43,.09,4.19),
           (.50,.09,4.53),(.63,.06,4.78),(.69,.11,4.96)]
    tube('主干 · 迎客松',trunk,[.237,.211,.173,.145,.134,.123,.105,.098,.073,.056,.024],bark,col,10)
    for i,(x,y,z) in enumerate([(-.76,-.28,1.17),(.84,-.65,.88),(-.32,-1,.66),
                                 (.65,.73,.98),(-.50,.75,1.23),(1.04,-.08,.83)]):
        v=Vector((x,y,0))
        pts=[(0,0,1.50),(v.x*.15,v.y*.15,1.28),(v.x*.52,v.y*.52,1.14),(v.x*.73,v.y*.73,z+.09),(x,y,z)]
        tube('裸露岩根 '+str(i+1),pts,[.115,.10,.071,.044,.014],bark,col,6)
    branches=[
        # The primary welcome bough forks along its outer half and almost equals tree height.
        ('横迎主枝',[(.12,-.02,2.48),(.43,-.11,2.77),(.75,-.20,2.9),(1.08,-.26,2.85),
                   (1.58,-.33,2.66),(2.04,-.42,2.62),(2.48,-.57,2.57),(2.95,-.56,2.59),(3.34,-.62,2.64)],.129,.57),
        ('横迎副枝',[(.97,-.23,2.86),(1.29,.05,3.00),(1.59,.23,3.13),(1.96,.35,3.22),(2.27,.43,3.20)],.071,.54),
        ('右上长枝',[(.30,.08,3.86),(.71,.01,4.03),(1.10,-.07,4.05),(1.54,-.15,3.96),(1.91,-.15,3.90),(2.34,-.29,3.87),(2.71,-.34,3.88)],.105,.60),
        ('左下横枝',[(.27,.05,3.56),(-.12,-.02,3.68),(-.53,-.15,3.56),(-.96,-.32,3.43),(-1.28,-.30,3.42)],.075,.48),
        ('左冠主枝',[(.39,.08,4.12),(.02,.09,4.28),(-.34,.11,4.27),(-.69,.17,4.22),(-1.07,.29,4.13)],.089,.65),
        ('冠前斜枝',[(.45,.04,4.19),(.30,-.25,4.30),(.19,-.63,4.20),(.08,-1.00,4.19),(-.12,-1.28,4.24)],.070,.59),
        ('冠后侧枝',[(.38,.08,4.15),(.49,.44,4.35),(.55,.78,4.35),(.57,1.11,4.30),(.65,1.39,4.37)],.072,.61),
        ('顶部左梢',[(.48,.09,4.49),(.23,.07,4.68),(-.10,.10,4.73),(-.45,.11,4.67)],.066,.62),
        ('顶部右梢',[(.53,.07,4.59),(.83,.16,4.70),(1.12,.18,4.67),(1.48,.18,4.61)],.061,.62),
        ('顶部迎面枝',[(.59,.08,4.69),(.68,-.21,4.83),(.84,-.46,4.81),(1.02,-.73,4.75)],.051,.53),
        ('顶部背面枝',[(.62,.08,4.71),(.35,.35,4.85),(.14,.58,4.84),(-.01,.77,4.80)],.045,.52),
        ('最高梢',[(.65,.1,4.77),(.73,.09,4.93),(.77,.11,5.05),(.87,.08,5.12)],.047,.47)]
    leaves=groups['leaves']
    for label,pts,radius,spread in branches:
        pts=list(map(Vector,pts))
        radii=[radius*(1-.78*i/(len(pts)-1)) for i in range(len(pts))]
        tube(label,pts,radii,bark,col,8 if radius>.10 else 6)
        start_index=4 if label=='横迎主枝' else (2 if len(pts)>4 else 1)
        for i in range(start_index,len(pts)):
            anchor=pts[i]
            projected=Vector((anchor.x-pts[i-1].x,anchor.y-pts[i-1].y,0)).normalized()
            perp=Vector((-projected.y,projected.x,0))
            for side in (-1,1):
                far=anchor + projected*rng.uniform(.06,.30) + perp*side*rng.uniform(.19,.44)
                far.z+=rng.uniform(.14,.28)
                fork(anchor,far,.032 if i<len(pts)-1 else .025,bark,col,label+' · 分梢')
                s=spread*rng.uniform(.73,1.12)
                crown(far,(s*1.18,s*.85,s*.29),rng.choice(mats['cores']),bark,mats['needles'],leaves,label+' '+str(i)+str(side))


def materials():
    m={'stone':material('细粒花岗岩',(.47,.46,.41),'granite.jpg'),
       'bark':material('黄山松古干',(.27,.17,.10),'bark.jpg'),
       'moss':material('石隙苔衣',(.13,.16,.062)),
       'needles':material('双针叶 · 透隙针束',(.19,.28,.12),'pine-spray.png',True)}
    m['cores']=[material('老针阴面',(.11,.17,.085),'dense-needles.jpg')]
    return m


def stats(source_triangles):
    blob=OUTPUT.read_bytes()
    n=struct.unpack_from('<I',blob,12)[0]
    doc=json.loads(blob[20:20+n])
    prims=[p for mesh in doc['meshes'] for p in mesh['primitives']]
    a=doc['accessors']
    count=sum(a[p['indices']]['count']//3 for p in prims)
    if not 2000<=count<=8000:
        raise ValueError(f'Triangle count outside national budget: {count}')
    if any('bufferView' not in im for im in doc['images']):
        raise ValueError('External surface map after export')
    if not any(mat.get('alphaMode')=='MASK' for mat in doc['materials']):
        raise ValueError('Missing alpha-tested shoots')
    bounds=[a[p['attributes']['POSITION']] for p in prims]
    limits={key:[(min if key=='min' else max)(part[key][i] for part in bounds) for i in range(3)] for key in ('min','max')}
    result={'id':'huangshan','name':'黄山迎客松','file':OUTPUT.name,'version':'national-v1',
            'source':'黄山市政府迎客松资料与玉屏实景，原创 Blender 程序建模','sourceCopy':'data/landmarks/huangshan/source.blend',
            'sourceTriangles':source_triangles,'sourceSha256':hashlib.sha256((HOME/'source.blend').read_bytes()).hexdigest(),
            'triangles':count,'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),'materials':len(doc['materials']),
            'embeddedImages':len(doc['images']),'bounds':limits,
            'coordinateConvention':'glTF Y-up, +Z front, trunk-ground projection at X=Z=0, stone base Y=0, primary bough points mainly +X'}
    (HOME/'stats.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Validated web model',count,'triangles;',len(blob),'bytes.',flush=True)


def national_lod(groups):
    # Rebuild crown cores from the actual master rings, retaining the upper profile.
    # Keep eight curved sprays per core, distributed around the full circumference.
    for obj in list(groups['leaves'].objects):
        mesh=obj.data
        points=[v.co.copy() for v in mesh.vertices]
        if '密针冠心' in obj.name:
            indices=[0,2,4,6,8]
            points=[points[k*9+i] for k in (1,2) for i in indices]+[points[-1]]
            faces=[(4,3,2,1,0)]+[(j,(j+1)%5,(j+1)%5+5,j+5) for j in range(5)]+[(5+j,5+(j+1)%5,10) for j in range(5)]
            uvs=planar_mapping(points,faces,.39)
            smooth=True
        else:
            faces=[]
            uvs=[]
            active_uv=mesh.uv_layers.active.data
            for poly in mesh.polygons:
                if poly.index<24 and (poly.index//2)%3==1:
                    continue
                faces.append(list(poly.vertices))
                uvs.append([tuple(active_uv[i].uv) for i in poly.loop_indices])
            smooth=False
        mesh_object(obj.name+' · 全国',points,faces,mesh.materials[0],groups['leaves'],uvs,smooth)
        bpy.data.objects.remove(obj,do_unlink=True)
    for obj in list(groups['wood'].objects)+list(groups['rock'].objects):
        if '分梢' in obj.name or '苔斑' in obj.name:
            bpy.context.view_layer.objects.active=obj
            mod=obj.modifiers.new('全国细枝与苔衣','DECIMATE')
            mod.ratio=.63
            mod.use_collapse_triangulate=True
            bpy.ops.object.modifier_apply(modifier=mod.name)


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    groups={name:make_collection(label) for name,label in [('rock','01 | 玉屏花岗岩与苔衣'),('wood','02 | 岩根、主干与枝梢'),('leaves','03 | 分层松冠与针束')]}
    mats=materials()
    terrain(groups,mats)
    tree(groups,mats)
    bpy.ops.wm.save_as_mainfile(filepath=str(HOME/'source.blend'),compress=True)
    source_triangles=sum(sum(len(face.vertices)-2 for face in obj.data.polygons) for obj in bpy.context.scene.objects if obj.type=='MESH')
    national_lod(groups)
    # Join only after saving the editable, individually grouped tree and outcrop.
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active=next(obj for obj in bpy.context.selected_objects if obj.type=='MESH')
    bpy.ops.object.join()
    obj=bpy.context.active_object
    obj.name='黄山 · 玉屏迎客松'
    bpy.ops.export_scene.gltf(filepath=str(OUTPUT),export_format='GLB',use_selection=True,export_yup=True,
                              export_apply=True,export_lights=False,export_cameras=False)
    stats(source_triangles)


def render():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(OUTPUT))
    scene=bpy.context.scene
    points=[o.matrix_world@Vector(p) for o in scene.objects if o.type=='MESH' for p in o.bound_box]
    lower=Vector(min(p[i] for p in points) for i in range(3))
    upper=Vector(max(p[i] for p in points) for i in range(3))
    center=(upper+lower)/2
    assert abs(lower.z)<1e-5
    scene.render.engine='CYCLES'
    scene.cycles.samples=35
    scene.cycles.use_denoising=True
    scene.render.resolution_x=720
    scene.render.resolution_y=720
    scene.render.resolution_percentage=100
    scene.world=bpy.data.worlds.new('日光摄影棚')
    scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.76,.81,.85,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.49
    scene.view_settings.view_transform='AgX'
    for (pos,power,size) in [((-4,-7,10),980,7),((5,3,9),1100,6)]:
        light=bpy.data.lights.new('柔光','AREA')
        light.energy=power
        light.shape='DISK'
        light.size=size
        obj=bpy.data.objects.new('柔光',light)
        scene.collection.objects.link(obj)
        obj.location=pos
        obj.rotation_euler=(center-obj.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.018))
    ground=bpy.context.object
    ground.data.materials.append(material('摄影台',(.55,.55,.51)))
    data=bpy.data.cameras.new('正交摄影')
    data.type='ORTHO'
    data.ortho_scale=max((upper-lower).x,(upper-lower).z)*1.19
    camera=bpy.data.objects.new('正交摄影',data)
    scene.collection.objects.link(camera)
    scene.camera=camera
    for name,view in [('正面',(0,-1,.13)),('右侧',(1,0,.12)),('侧前方',(.46,-1,.45))]:
        camera.location=center+Vector(view).normalized()*16
        camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(HOME/'renders'/f'{name}.png')
        bpy.ops.render.render(write_still=True)

if __name__=='__main__':
    if '--render-only' not in sys.argv:
        build()
    render()
