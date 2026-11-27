"""Build one or more editable landmark masters, export national GLBs and photograph the re-import."""
from pathlib import Path
import sys,hashlib,json,struct,math
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import bpy,bmesh
from mathutils import Vector
import geometry as g
import sculptures as s
LANDMARKS=HERE.parent
OUT=LANDMARKS.parents[1]/'app/public/models'
BUILDERS={'longmen':s.longmen,'yellow-crane':s.yellow_crane,'tianmen':s.tianmen,'canton-tower':s.canton,'elephant-hill':s.elephant,'hongyadong':s.hongyadong,'panda-base':s.panda,'jiuzhaigou':s.jiuzhai,'dali':s.dali}

def triangle_count(objects):
    return sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in objects if o.type=='MESH')

def build(key,info,asset,from_master):
    if from_master:
        bpy.ops.wm.open_mainfile(filepath=str(asset/'source.blend'))
    else:
        g.reset(key); BUILDERS[key]()
        meshes=[ob for ob in bpy.context.scene.objects if ob.type=='MESH']
        # Unify outward orientation for closed sculpture parts before exporting and baking PBR.
        for ob in meshes:
            bm=bmesh.new();bm.from_mesh(ob.data)
            if bm.faces and all(e.is_manifold for e in bm.edges):
                bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
            bm.to_mesh(ob.data);bm.free()
        low=min(v.co.z for o in meshes for v in o.data.vertices)
        if abs(low)>.000001:
            for o in meshes:
                for v in o.data.vertices:v.co.z-=low
        bpy.ops.wm.save_as_mainfile(filepath=str(asset/'source.blend'),compress=True)
    meshes=[ob for ob in bpy.context.scene.objects if ob.type=='MESH']
    source_tris=triangle_count(meshes)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in meshes:obj.select_set(True)
    bpy.context.view_layer.objects.active=meshes[0];bpy.ops.object.join();obj=bpy.context.active_object
    # Apply only to the national copy. Building masters keep individual pillars, eaves, figures and terrain.
    if source_tris>7840:
        mod=obj.modifiers.new('全国尺度轮廓简化','DECIMATE');mod.ratio=7530/source_tris;mod.use_collapse_triangulate=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    obj.name=info['name']
    outfile=OUT/(key+'.glb')
    bpy.ops.export_scene.gltf(filepath=str(outfile),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_lights=False,export_cameras=False)
    data=outfile.read_bytes();ln=struct.unpack_from('<I',data,12)[0];d=json.loads(data[20:20+ln])
    prim=[p for m in d['meshes'] for p in m['primitives']];a=d['accessors']
    count=sum(a[p['indices']]['count']//3 for p in prim)
    assert all(im.get('bufferView') is not None for im in d['images'])
    assert 500<=count<=8000,(key,count)
    bounds={k:[(min if k=='min' else max)(a[p['attributes']['POSITION']][k][i] for p in prim) for i in (0,1,2)] for k in ('min','max')}
    stats=dict(id=key,name=info['name'],version='national-v1',file=outfile.name,source=info['reference'],sourceCopy=f'data/landmarks/{key}/source.blend',sourceTriangles=source_tris,sourceSha256=hashlib.sha256((asset/'source.blend').read_bytes()).hexdigest(),triangles=count,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),materials=len(d['materials']),embeddedImages=len(d['images']),bounds=bounds,coordinateConvention='glTF Y-up; local +Z is the declared display front; local Y=0 is the base.')
    (asset/'stats.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2)+'\n')
    print('BUILT',key,source_tris,count,len(data),flush=True)

def render(key,asset):
    bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(OUT/(key+'.glb')))
    sc=bpy.context.scene;points=[o.matrix_world@v.co for o in sc.objects if o.type=='MESH' for v in o.data.vertices]
    lo=Vector(min(p[i] for p in points) for i in (0,1,2));hi=Vector(max(p[i] for p in points) for i in (0,1,2));assert abs(lo.z)<.012,(key,lo.z)
    center=(lo+hi)/2;scl=(hi-lo).length
    sc.render.engine='CYCLES';sc.cycles.samples=12;sc.cycles.use_denoising=True
    sc.render.threads_mode='FIXED';sc.render.threads=3;sc.render.resolution_x=600;sc.render.resolution_y=500;sc.render.resolution_percentage=100
    sc.world=bpy.data.worlds.new('日光');sc.world.use_nodes=True
    sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.78,.85,.91,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.61
    sc.view_settings.view_transform='AgX'
    for xyz,factor,size in [((-.85,-1.25,1.7),75,1.1),((1.2,.40,1.2),50,.86)]:
        l=bpy.data.lights.new('柔光','AREA');l.energy=scl*scl*factor;l.shape='DISK';l.size=scl*size
        ob=bpy.data.objects.new('柔光',l);sc.collection.objects.link(ob);ob.location=center+Vector(xyz)*scl;ob.rotation_euler=(center-ob.location).to_track_quat('-Z','Y').to_euler()
    bpy.ops.mesh.primitive_plane_add(size=1000,location=(0,0,-.012));floor=bpy.context.object
    m=bpy.data.materials.new('暖灰摄影面');m.diffuse_color=(.65,.64,.60,1);floor.data.materials.append(m)
    data=bpy.data.cameras.new('三向摄影');data.type='ORTHO';cam=bpy.data.objects.new('摄影',data);sc.collection.objects.link(cam);sc.camera=cam
    (asset/'renders').mkdir(exist_ok=True)
    for n,vec in [('正面',(0,-1,.14)),('右侧',(1,0,.15)),('侧前方',(.54,-1,.49))]:
        view=Vector(vec).normalized();cam.location=center+view*(scl*2.7)
        rot=(-view).to_track_quat('-Z','Y');cam.rotation_euler=rot.to_euler()
        right=rot@Vector((1,0,0));up=rot@Vector((0,1,0))
        xx=[p.dot(right) for p in points];yy=[p.dot(up) for p in points]
        delta=right*((max(xx)+min(xx))/2-center.dot(right))+up*((max(yy)+min(yy))/2-center.dot(up))
        cam.location+=delta;data.ortho_scale=max((max(xx)-min(xx)),1.2*(max(yy)-min(yy)))*1.15
        sc.render.filepath=str(asset/'renders'/(n+'.png'));bpy.ops.render.render(write_still=True)
    print('RENDERED',key,flush=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    ids=[i for i in args if i in BUILDERS] or list(BUILDERS)
    for key in ids:
        asset=LANDMARKS/key;info=json.loads((asset/'site.json').read_text())
        if '--render-only' not in args:build(key,info,asset,'--from-master' in args)
        if '--build-only' not in args:render(key,asset)
