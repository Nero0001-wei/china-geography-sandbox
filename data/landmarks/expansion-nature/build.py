"""Blender 5.2.1. Usage: blender -b -t 2 -P build.py -- SITE [--from-master|--render-only|--no-render]."""
from pathlib import Path
from mathutils import Vector
import hashlib
import json
import struct
import sys

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from shapes import PARTS
from summits import changbai, emei, everest, fanjingshan, huashan, shennongjia, wulingyuan, yulong
from terrain import alishan, crescent_lake, shapotou, stone_forest, wulong, xiangshawan, zhangye_danxia
from waters import detian, huangguoshu, hulunbuir, kanas, lushan, qinghai_lake, sun_moon_lake, tianyahaijiao, wuyishan, yangshuo

ROOT = HERE.parents[2]
SCENES = {
    f.__name__.replace("_", "-"): f for f in [
        alishan, changbai, crescent_lake, detian, emei, everest, fanjingshan, huangguoshu,
        hulunbuir, huashan, kanas, lushan, qinghai_lake, shapotou, shennongjia, stone_forest,
        sun_moon_lake, tianyahaijiao, wulingyuan, wulong, wuyishan, xiangshawan, yangshuo,
        yulong, zhangye_danxia,
    ]
}
TEXTURES = {
    "basalt":"dark", "clay":"clay", "clayDark":"clayDark", "cliff":"rock", "cliffWarm":"granite",
    "deepwater":"deepwater", "fall":"water", "foam":"snow", "gold":"gold", "granite":"granite",
    "graniteLight":"graniteLight", "grass":"grass", "leaf":"pine", "oldstone":"ashlar",
    "ochre":"ochre", "pine":"pine", "rock":"rock", "roof":"greyTile", "sand":"sand",
    "scree":"scree", "snow":"snow", "timber":"timber", "white":"whitewash",
}
COLORS = {
    "base":"5A4934", "camel":"AD673B", "cinnabar":"B93F25", "craterBlue":"167FAD",
    "craterLight":"349EBF", "creamSand":"E6C892", "danxiaCream":"E7BB83", "danxiaOchre":"CB904A",
    "danxiaPurple":"887179", "danxiaRed":"A74632", "danxiaRust":"C96943", "danxiaWine":"824444",
    "dark":"352B26", "desertSoil":"A2754B", "fall":"E6F7EF", "foam":"EAECE1", "glacial":"5BADB1",
    "glacialRipple":"94C5B8", "glacier":"92B3C2", "goldSand":"D6A371", "grassLight":"75863D",
    "jade":"539288", "jadeRipple":"8AB5A1", "lakeBlue":"326F9F", "meadow":"7F8650",
    "pineDark":"263C27", "pineLight":"647850", "red":"9F4C3B", "reed":"9A9958",
    "ripple":"70A9BE", "riverBlue":"548991", "rockDark":"4C4A42", "sage":"8E9061",
    "cutSoil":"6E6253", "coastalGranite":"77736D", "coastalShale":"655F56",
    "sandstone":"AB8963", "siltriver":"5D6750", "snowShadow":"B3CFD3", "soil":"73664B",
    "stoneWarm":"998779", "surfRipple":"81BABC", "trainRed":"AB3F35", "waterLight":"70A7AA",
    "weed":"78854B", "wuyiRed":"955945", "wuyiStone":"AB7E66", "yellowLake":"58857A",
    "yellowLakeShallow":"769678",
}
MATERIALS = {}


def linear(c):
    return ((c+.055)/1.055)**2.4 if c>.04045 else c/12.92


def col(hex_color):
    return tuple(linear(int(hex_color[i:i+2],16)/255) for i in (0,2,4))+(1.0,)


def material(name):
    if name in MATERIALS:
        return MATERIALS[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    pigment = col(COLORS.get(name,"CBC0A7"))
    mat.diffuse_color = pigment
    shader.inputs["Base Color"].default_value = pigment
    shader.inputs["Roughness"].default_value = .78
    if name in ("waterLight", "craterLight", "craterBlue", "deepwater", "jade", "lakeBlue",
                "glacial", "yellowLake", "yellowLakeShallow", "riverBlue"):
        shader.inputs["Roughness"].default_value = .39
    if name == "gold":
        shader.inputs["Metallic"].default_value = .19
    if name in TEXTURES:
        path = HERE.parent / "workshop-c" / "textures" / (TEXTURES[name]+".png")
        image = bpy.data.images.load(str(path), check_existing=True)
        image.pack()
        node = mat.node_tree.nodes.new("ShaderNodeTexImage")
        node.image = image
        mat.node_tree.links.new(node.outputs["Color"],shader.inputs["Base Color"])
        if name in ("fall","foam"):
            glaze = mat.node_tree.nodes.new("ShaderNodeMixRGB")
            glaze.blend_type = "MIX"
            glaze.inputs[0].default_value = .72
            glaze.inputs[2].default_value = pigment
            mat.node_tree.links.new(node.outputs["Color"],glaze.inputs[1])
            # The GLB exporter supports a base image or color factor rather than a node mix.
            # Preserve the white water in all viewers by baking the tint to the image once.
            baked = image.copy()
            baked.name = name
            pixels = list(baked.pixels)
            for i in range(0,len(pixels),4):
                for k in range(3):
                    pixels[i+k] = .28*pixels[i+k] + .72*pigment[k]
            baked.pixels = pixels
            baked.pack()
            node.image = baked
            mat.node_tree.nodes.remove(glaze)
    MATERIALS[name]=mat
    return mat


def assemble():
    for label, polygons in PARTS.items():
        points, faces, face_materials = [], [], []
        point_ids, slots = {}, {}
        for positions, mn, _ in polygons:
            ids=[]
            for vector in positions:
                key=tuple(round(v,6) for v in vector)
                if key not in point_ids:
                    point_ids[key]=len(points)
                    points.append(key)
                ids.append(point_ids[key])
            ids=list(dict.fromkeys(ids))
            if len(ids)<3:
                continue
            faces.append(ids)
            slots.setdefault(mn,len(slots))
            face_materials.append(mn)
        mesh=bpy.data.meshes.new(label)
        mesh.from_pydata(points,[],faces)
        mesh.update()
        if not len(mesh.polygons):
            continue
        obj=bpy.data.objects.new(label,mesh)
        bpy.context.scene.collection.objects.link(obj)
        for mat in slots:
            mesh.materials.append(material(mat))
        uvs=mesh.uv_layers.new(name="地貌与植被")
        for f,mn in zip(mesh.polygons,face_materials):
            f.material_index=slots[mn]
            n=f.normal
            if abs(n.z)>=max(abs(n.x),abs(n.y))*.78:
                axes=0,1
            elif abs(n.y)>abs(n.x):
                axes=0,2
            else:
                axes=1,2
            for loopid in f.loop_indices:
                p=points[mesh.loops[loopid].vertex_index]
                uvs.data[loopid].uv=(p[axes[0]]*.67,p[axes[1]]*.67)
        mesh.validate(clean_customdata=False)
        mesh.update()
        obj["part"]=label


def read_stats(glb, directory, metadata):
    data=glb.read_bytes()
    size=struct.unpack_from("<I",data,12)[0]
    record=json.loads(data[20:20+size])
    primitives=[p for m in record["meshes"] for p in m["primitives"]]
    triangles=sum(record["accessors"][p["indices"]]["count"]//3 for p in primitives)
    accessors=[record["accessors"][p["attributes"]["POSITION"]] for p in primitives]
    images=record.get("images",[])
    assert all("uri" not in image for image in images)
    return dict(id=metadata["id"],name=metadata["name"],file=glb.name,version="national-v1",
                source=metadata["visualSource"],sourceCopy=f"data/landmarks/{directory.name}/source.blend",
                sourceSha256=hashlib.sha256((directory/"source.blend").read_bytes()).hexdigest(),
                triangles=triangles,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),
                materials=len(record["materials"]),embeddedImages=len(images),
                bounds={
                    "min":[min(a["min"][i] for a in accessors) for i in range(3)],
                    "max":[max(a["max"][i] for a in accessors) for i in range(3)],
                },
                coordinateConvention="glTF Y-up; +Z front; Blender Z-up; underside at zero")


def export(glb, directory, metadata):
    bpy.ops.object.select_all(action="DESELECT")
    objects=[ob for ob in bpy.context.scene.objects if ob.type=="MESH"]
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.object.join()
    out=bpy.context.object
    out.name=metadata["name"]
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    out.data.calc_loop_triangles()
    source_triangles=len(out.data.loop_triangles)
    if source_triangles>7900:
        mod=out.modifiers.new("全国模型地貌优化","DECIMATE")
        mod.ratio=7690/source_triangles
        mod.use_collapse_triangulate=True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format="GLB",use_selection=True,
                             export_yup=True,export_apply=True,export_cameras=False,export_lights=False)
    stats=read_stats(glb,directory,metadata)
    stats["sourceTriangles"]=source_triangles
    assert 2000<=stats["triangles"]<=8000,stats
    assert abs(stats["bounds"]["min"][1])<.0001,stats
    (directory/"stats.json").write_text(json.dumps(stats,ensure_ascii=False,indent=2)+"\n")
    print(metadata["id"],"source",source_triangles,"web",stats["triangles"],stats["bytes"],flush=True)


def previews(glb, directory):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb))
    meshes=[o for o in bpy.context.scene.objects if o.type=="MESH"]
    verts=[o.matrix_world @ Vector(p) for o in meshes for p in o.bound_box]
    low=Vector(tuple(min(p[i] for p in verts) for i in range(3)))
    high=Vector(tuple(max(p[i] for p in verts) for i in range(3)))
    ctr=(low+high)*.5
    span=max(high-low)
    scene=bpy.context.scene
    scene.world=bpy.data.worlds.new("柔和天光")
    scene.world.use_nodes=True
    bg=scene.world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value=(.76,.79,.83,1)
    bg.inputs["Strength"].default_value=.61
    scene.render.engine="CYCLES"
    scene.cycles.samples=8
    scene.cycles.use_denoising=True
    scene.cycles.max_bounces=4
    scene.cycles.diffuse_bounces=2
    scene.cycles.glossy_bounces=2
    scene.render.resolution_x=600
    scene.render.resolution_y=450
    scene.render.resolution_percentage=100
    scene.view_settings.view_transform="AgX"
    bpy.ops.mesh.primitive_plane_add(size=span*100,location=(0,0,low.z-.009))
    plane=bpy.context.object
    paper=bpy.data.materials.new("暖灰无缝背景")
    paper.diffuse_color=(.65,.63,.59,1)
    plane.data.materials.append(paper)
    for label, direction, energy, size in [
        ("主光",(-1.08,-1.30,1.81),108,.86),
        ("填充光",(1.30,-.3,1.21),31,1.24),
        ("轮廓光",(.24,1.4,1.4),45,1.20),
    ]:
        lamp=bpy.data.lights.new(label,"AREA")
        lamp.energy=energy*span*span
        lamp.shape="DISK"
        lamp.size=span*size
        obj=bpy.data.objects.new(label,lamp)
        scene.collection.objects.link(obj)
        obj.location=ctr+Vector(direction)*span
        obj.rotation_euler=(ctr-obj.location).to_track_quat("-Z","Y").to_euler()
    cam=bpy.data.cameras.new("GLB 回读验证")
    cam.type="ORTHO"
    camera=bpy.data.objects.new("相机",cam)
    scene.collection.objects.link(camera)
    scene.camera=camera
    render_dir=directory/"renders"
    render_dir.mkdir(exist_ok=True)
    for label, direction in [("正面",(0,-1,.35)),("右侧",(1,0,.35)),("侧前方",(.63,-1,1.07))]:
        vector=Vector(direction).normalized()
        camera.location=ctr+vector*(span*4)
        rot=(-vector).to_track_quat("-Z","Y")
        camera.rotation_euler=rot.to_euler()
        horizontal=[p.dot(rot@Vector((1,0,0))) for p in verts]
        vertical=[p.dot(rot@Vector((0,1,0))) for p in verts]
        cam.ortho_scale=1.17*max(max(horizontal)-min(horizontal),(max(vertical)-min(vertical))*600/450)
        cam.clip_end=span*90
        scene.render.filepath=str(render_dir/(label+".png"))
        bpy.ops.render.render(write_still=True)


def main():
    args=sys.argv[sys.argv.index("--")+1:]
    directory=HERE.parent/args[0]
    meta=json.loads((directory/"site.json").read_text())
    glb=ROOT/"app/public/models"/(meta["id"]+".glb")
    if "--render-only" not in args:
        if "--from-master" in args:
            bpy.ops.wm.open_mainfile(filepath=str(directory/"source.blend"))
        else:
            bpy.ops.wm.read_factory_settings(use_empty=True)
            bpy.context.preferences.filepaths.save_version=0
            SCENES[meta["id"]]()
            assemble()
            bpy.ops.wm.save_as_mainfile(filepath=str(directory/"source.blend"),compress=True)
        export(glb,directory,meta)
    if "--no-render" not in args:
        previews(glb,directory)


if __name__=="__main__":
    main()
