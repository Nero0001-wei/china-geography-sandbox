"""Blender build, GLB inspection and orthographic renders. See README.md for commands."""
import argparse
import hashlib
import json
import struct
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import geometry
import vehicles

PUBLIC=HERE.parent.parent/'app'/'public'/'models'/'vehicles'
BUILDERS={
    'plane':('民航客机', vehicles.airplane, 'air'),
    'car':('自驾汽车', vehicles.automobile, 'core'),
    'train':('普速列车', vehicles.locomotive, 'core'),
    'high-speed-rail':('高铁', vehicles.emu, 'core'),
    'intercity-rail':('城际列车', lambda: vehicles.emu(True), 'regional'),
    'coach':('长途大巴', vehicles.motorcoach, 'regional'),
    'ferry':('城际客轮', vehicles.ferry, 'regional')
}


def setup():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    geometry.collection=None


def bounds(points):
    return [[min(v[i] for v in points) for i in range(3)],
            [max(v[i] for v in points) for i in range(3)]]


def make_asset(key):
    setup()
    name,build,board=BUILDERS[key]
    build()
    objects=list(bpy.context.scene.objects)
    for obj in objects:
        # Aircraft airfoils are mirrored across the centreline. Orient each closed shell outward.
        bm=bmesh.new()
        bm.from_mesh(obj.data)
        if all(edge.is_manifold for edge in bm.edges):
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
            bm.to_mesh(obj.data)
        bm.free()
    bpy.context.view_layer.update()
    raw=[o.matrix_world @ v.co for o in objects for v in o.data.vertices]
    lo,hi=bounds(raw)
    offset=Vector((-(lo[0]+hi[0])/2,-(lo[1]+hi[1])/2,-lo[2]))
    for obj in objects:
        obj.location+=offset
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    source=HERE/key
    source.mkdir(exist_ok=True)
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                view=area.spaces.active
                view.shading.color_type='MATERIAL'
                view.region_3d.view_distance=max(hi[i]-lo[i] for i in range(3))*1.7
                view.region_3d.view_location=(0,0,(hi[2]-lo[2])/2)
                view.region_3d.view_rotation=Vector((-1,1,-.57)).to_track_quat('-Z','Y')
    bpy.ops.wm.save_as_mainfile(filepath=str(source/'source.blend'),compress=True)
    if key == 'train':
        # A locomotive plus coach doubles the number of window frames and axles in one marker.
        for obj in objects:
            for modifier in obj.modifiers:
                if modifier.type=='BEVEL':
                    modifier.segments=1
    bpy.ops.object.select_all(action='SELECT')
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.join()
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    bpy.context.active_object.name=key
    bpy.context.active_object.data.name=name
    PUBLIC.mkdir(parents=True,exist_ok=True)
    bpy.ops.export_scene.gltf(filepath=str(PUBLIC/(key+'.glb')),export_format='GLB',use_selection=True,
                              export_yup=True,export_apply=True,export_cameras=False,export_lights=False,
                              export_animations=False,export_extras=False)
    print('EXPORTED',key,flush=True)


def inspect(key):
    raw=(PUBLIC/(key+'.glb')).read_bytes()
    assert raw[:4]==b'glTF' and struct.unpack_from('<II',raw,4)==(2,len(raw))
    size=struct.unpack_from('<I',raw,12)[0]
    doc=json.loads(raw[20:20+size])
    nodes=doc['nodes']
    assert len(nodes)==1 and nodes[0]['mesh']==0
    assert not any(field in nodes[0] for field in ['translation','rotation','scale','matrix'])
    primitives=doc['meshes'][0]['primitives']
    tri=0
    extrema=[]
    for pr in primitives:
        assert pr.get('mode',4)==4 and 'indices' in pr
        accessor=doc['accessors'][pr['indices']]
        assert accessor['count']%3==0
        tri+=accessor['count']//3
        pos=doc['accessors'][pr['attributes']['POSITION']]
        extrema += [pos['min'],pos['max']]
    lo,hi=bounds(extrema)
    assert abs(lo[1])<.001 and abs(lo[0]+hi[0])<.005 and abs(lo[2]+hi[2])<.005, (key,lo,hi)
    for material in doc['materials']:
        texture=material.get('pbrMetallicRoughness',{}).get('baseColorTexture')
        if texture:
            assert texture.get('texCoord',0)>=0, (key,texture)
    assert all('bufferView' in im for im in doc.get('images',[]))
    name,_,board=BUILDERS[key]
    return dict(id=key,name=name,file=f'/models/vehicles/{key}.glb',version=1,triangles=tri,bytes=len(raw),
                materials=len(doc['materials']),embeddedImages=len(doc.get('images',[])),
                bounds=dict(min=[round(v,5) for v in lo],max=[round(v,5) for v in hi]),
                dimensions=[round(hi[i]-lo[i],5) for i in range(3)],
                source=f'data/vehicles/{key}/source.blend',references=f'data/vehicles/references/{board}.png',
                sha256=hashlib.sha256(raw).hexdigest())


def manifest():
    if not all((PUBLIC/(k+'.glb')).exists() for k in BUILDERS):
        return
    specs=[inspect(k) for k in BUILDERS]
    (PUBLIC/'manifest.json').write_text(json.dumps(dict(version=1,up='+Y',forward='+Z',groundY=0,
                                      models=specs),indent=2,ensure_ascii=False)+'\n')
    for spec in specs:
        print('VERIFIED',spec['id'],spec['triangles'],spec['bytes'],flush=True)


def light(name,position,target,power,size):
    lamp=bpy.data.lights.new(name,'AREA')
    lamp.energy=power
    lamp.shape='DISK'
    lamp.size=size
    obj=bpy.data.objects.new(name,lamp)
    bpy.context.scene.collection.objects.link(obj)
    obj.location=position
    obj.rotation_euler=(Vector(target)-Vector(position)).to_track_quat('-Z','Y').to_euler()


def render(key):
    setup()
    bpy.ops.import_scene.gltf(filepath=str(PUBLIC/(key+'.glb')))
    sc=bpy.context.scene
    bpy.context.view_layer.update()
    points=[o.matrix_world @ v.co for o in sc.objects if o.type=='MESH' for v in o.data.vertices]
    lo,hi=bounds(points)
    reach=max(hi[i]-lo[i] for i in range(3))
    mid=Vector([(lo[i]+hi[i])/2 for i in range(3)])
    sc.render.engine='CYCLES'
    sc.cycles.samples=10
    sc.cycles.use_denoising=True
    sc.render.resolution_x=600
    sc.render.resolution_y=400
    sc.render.resolution_percentage=100
    sc.render.threads_mode='FIXED'
    sc.render.threads=6
    sc.world=bpy.data.worlds.new('Neutral softbox')
    sc.world.use_nodes=True
    sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.82,.87,.96,1)
    sc.world.node_tree.nodes['Background'].inputs[1].default_value=.245
    sc.view_settings.view_transform='AgX'
    sc.view_settings.look='AgX - Medium High Contrast'
    sc.render.image_settings.file_format='PNG'
    sc.render.image_settings.color_mode='RGB'
    bpy.ops.mesh.primitive_plane_add(size=1000,location=(0,0,-.023))
    floor=bpy.context.active_object
    floor.name='Studio cyclorama'
    studio=bpy.data.materials.new('Warm neutral studio')
    studio.diffuse_color=(.75,.73,.68,1)
    floor.data.materials.append(studio)
    power=reach*reach
    light('Large key',(-reach*.65,-reach*.63,reach*1.05),mid,power*21,reach*.72)
    light('Side fill',(reach*.85,-reach*.10,reach*.64),mid,power*6,reach*.86)
    light('Rear rim',(reach*.15,reach*.79,reach*.83),mid,power*12,reach*.67)
    camera_data=bpy.data.cameras.new('Orthographic camera')
    camera_data.type='ORTHO'
    camera_data.clip_end=1000
    camera=bpy.data.objects.new('Orthographic camera',camera_data)
    sc.collection.objects.link(camera)
    sc.camera=camera
    result=HERE/key/'renders'
    result.mkdir(exist_ok=True)
    for view,dir in [('front',(0,-1,.055)),('side',(1,0,.07)),('three-quarter',(.93,-1.05,.57))]:
        towards=Vector(dir).normalized()
        q=(-towards).to_track_quat('-Z','Y')
        right=q@Vector((1,0,0));up=q@Vector((0,1,0))
        xx=[p.dot(right) for p in points]; yy=[p.dot(up) for p in points]
        target=mid+right*((min(xx)+max(xx))/2-mid.dot(right))+up*((min(yy)+max(yy))/2-mid.dot(up))
        camera.location=target+towards*reach*3
        camera.rotation_euler=q.to_euler()
        camera_data.ortho_scale=max(max(xx)-min(xx),(max(yy)-min(yy))*1.5)*1.18
        sc.render.filepath=str(result/(view+'.png'))
        bpy.ops.render.render(write_still=True)
    print('RENDERED',key,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--stage',choices=['export','render','all'],default='all')
    parser.add_argument('keys',nargs='*')
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    keys=args.keys or list(BUILDERS)
    if args.stage in ['export','all']:
        for key in keys: make_asset(key)
        manifest()
    if args.stage in ['render','all']:
        for key in keys: render(key)
