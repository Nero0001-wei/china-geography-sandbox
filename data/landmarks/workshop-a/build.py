"""Rebuild one or more editable landmarks, export the web GLB and photograph its re-import."""

import bpy, bmesh, hashlib, json, shutil, struct, sys
from pathlib import Path
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import geometry, models

BUILDERS = {
    "badaling": models.badaling,
    "beijing-universal": models.universal,
    "saint-sophia": models.sophia,
    "qinhuai": models.qinhuai,
    "bund": models.bund,
    "shanghai-disney": models.disney,
    "west-lake": models.westlake,
    "hengdian": models.hengdian,
    "taishan": models.taishan,
}


def triangle_count(obj):
    obj.data.calc_loop_triangles()
    return len(obj.data.loop_triangles)


def export(id, from_master=False):
    folder = HERE.parent / id
    site = json.loads((folder / "site.json").read_text())
    glb_path = HERE.parents[2] / "app/public/models" / (id + ".glb")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    if from_master:
        bpy.ops.wm.open_mainfile(filepath=str(folder / "source.blend"))
    else:
        geometry.parts.clear()
        geometry.tag("展示基台")
        BUILDERS[id]()
        geometry.create_objects()
        meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
        for obj in meshes:
            # Preserve UV loops while welding the custom-built face patches.
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.000006)
            bm.to_mesh(obj.data)
            bm.free()
            obj.data.update()
        for area in bpy.context.screen.areas:
            if area.type == "VIEW_3D":
                v = area.spaces.active.region_3d
                v.view_location = (0, 0, 2)
                v.view_distance = 23
                v.view_rotation = (Vector((0, 0, 2)) - Vector((12, -20, 11))).to_track_quat(
                    "-Z", "Y"
                )
        bpy.ops.wm.save_as_mainfile(filepath=str(folder / "source.blend"), compress=True)
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    source_faces = sum(triangle_count(o) for o in meshes)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in meshes:
        obj.select_set(True)
    anchor = next(
        o for o in meshes if o.location.length < 1e-8 and o.rotation_euler.to_matrix().is_identity
    )
    bpy.context.view_layer.objects.active = anchor
    bpy.ops.object.join()
    obj = bpy.context.view_layer.objects.active
    obj.name = site["name"]
    if source_faces > 7700:
        modifier = obj.modifiers.new("全国版减面", "DECIMATE")
        modifier.ratio = 7200 / source_faces
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.ops.export_scene.gltf(
        filepath=str(glb_path),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_cameras=False,
        export_lights=False,
        export_apply=True,
    )
    (folder / "web").mkdir(exist_ok=True)
    shutil.copyfile(glb_path, folder / "web" / glb_path.name)
    blob = glb_path.read_bytes()
    doc = json.loads(blob[20 : 20 + struct.unpack_from("<I", blob, 12)[0]])
    primitives = [p for m in doc["meshes"] for p in m["primitives"]]
    low = [
        min(doc["accessors"][p["attributes"]["POSITION"]]["min"][i] for p in primitives)
        for i in range(3)
    ]
    high = [
        max(doc["accessors"][p["attributes"]["POSITION"]]["max"][i] for p in primitives)
        for i in range(3)
    ]
    tri = sum(doc["accessors"][p["indices"]]["count"] // 3 for p in primitives)
    assert abs(low[1]) < 0.001 and 2000 <= tri <= 8000, (id, low, tri)
    assert all("bufferView" in image for image in doc["images"])
    stats = dict(
        id=id,
        name=site["name"],
        file=glb_path.name,
        version="national-v1",
        source=site["reference"],
        sourceCopy="data/landmarks/" + id + "/source.blend",
        sourceTriangles=source_faces,
        sourceSha256=hashlib.sha256((folder / "source.blend").read_bytes()).hexdigest(),
        triangles=tri,
        bytes=len(blob),
        sha256=hashlib.sha256(blob).hexdigest(),
        materials=len(doc["materials"]),
        embeddedImages=len(doc["images"]),
        bounds=dict(min=low, max=high),
        coordinateConvention="glTF Y-up, +Z front; ground anchor at local X=Z=0",
    )
    (folder / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
    print("EXPORTED", id, source_faces, tri, len(blob), flush=True)
    return glb_path, stats


def render(id):
    folder = HERE.parent / id
    glb_path = HERE.parents[2] / "app/public/models" / (id + ".glb")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(glb_path))
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    assert meshes and all(i.packed_file for i in bpy.data.images if i.source == "FILE" and i.users)
    points = [obj.matrix_world @ Vector(p) for obj in meshes for p in obj.bound_box]
    target = (
        Vector(tuple(min(p[i] for p in points) for i in range(3)))
        + Vector(tuple(max(p[i] for p in points) for i in range(3)))
    ) / 2
    size = max(max(p[i] for p in points) - min(p[i] for p in points) for i in range(3))
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 7
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 600
    scene.render.resolution_y = 460
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.view_settings.view_transform = "AgX"
    scene.world = bpy.data.worlds.new("柔和天光")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    bg.inputs[0].default_value = (0.81, 0.86, 0.9, 1)
    bg.inputs[1].default_value = 0.52
    bpy.ops.mesh.primitive_plane_add(size=size * 100, location=(0, 0, -0.012))
    plane = bpy.context.object
    m = bpy.data.materials.new("中性灰底")
    m.diffuse_color = (0.69, 0.68, 0.62, 1)
    plane.data.materials.append(m)
    for name, vec, eng in [
        ("主光", (-0.63, -1.2, 1.7), 125),
        ("辅光", (0.9, -0.3, 0.9), 32),
        ("后光", (0, 1.1, 1.3), 44),
    ]:
        li = bpy.data.lights.new(name, "AREA")
        li.energy = eng * size**2 / 4
        li.shape = "DISK"
        li.size = size * 1.05
        o = bpy.data.objects.new(name, li)
        scene.collection.objects.link(o)
        o.location = target + Vector(vec) * size
        o.rotation_euler = (target - o.location).to_track_quat("-Z", "Y").to_euler()
    cam = bpy.data.cameras.new("转台相机")
    cam.type = "ORTHO"
    cam.clip_end = 2000
    co = bpy.data.objects.new("镜头", cam)
    scene.collection.objects.link(co)
    scene.camera = co
    views = [("正面", (0, -2, 0.42)), ("右侧", (2, 0, 0.43)), ("侧前方", (1.12, -1.72, 1.12))]
    (folder / "renders").mkdir(exist_ok=True)
    for label, vec in views:
        co.location = target + Vector(vec).normalized() * size * 3
        q = (target - co.location).to_track_quat("-Z", "Y")
        co.rotation_euler = q.to_euler()
        proj = [q.inverted() @ (p - target) for p in points]
        rw = max(p.x for p in proj) - min(p.x for p in proj)
        rh = max(p.y for p in proj) - min(p.y for p in proj)
        cam.ortho_scale = max(rw, rh * 600 / 460) * 1.1
        scene.render.filepath = str(folder / "renders" / (label + ".png"))
        bpy.ops.render.render(write_still=True)
    print("RENDERED", id, flush=True)


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else list(BUILDERS)
    for name in [a for a in args if not a.startswith("--")]:
        if "--render-only" not in args:
            export(name, "--from-master" in args)
        if "--export-only" not in args:
            render(name)
