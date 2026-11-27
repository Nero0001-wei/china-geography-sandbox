"""Blender 5: -b -t 2 -P build.py -- <site ID> [--from-master] [--no-render]."""

from pathlib import Path
import sys, math, json, hashlib, struct
import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from geometry import PARTS
from sites import SCENES

ARGS = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
SITE = ARGS[0]
DIR = HERE.parent / SITE
GLB = ROOT / "app/public/models" / (SITE + ".glb")
META = json.loads((DIR / "site.json").read_text())
MATS = {}


def material(name):
    if name in MATS:
        return MATS[name]
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    tile = bpy.data.images.load(str(HERE / "textures" / (name + ".png")), check_existing=True)
    tile.pack()
    node = mat.node_tree.nodes.new("ShaderNodeTexImage")
    node.image = tile
    mat.node_tree.links.new(node.outputs["Color"], shader.inputs["Base Color"])
    shader.inputs["Roughness"].default_value = (
        0.44 if name in ["teal", "water", "mint", "gold", "goldTile"] else 0.80
    )
    if name in ["gold", "mint", "bronze"]:
        shader.inputs["Metallic"].default_value = 0.34
    MATS[name] = mat
    return mat


def meshes():
    for name, patches in PARTS.items():
        points = []
        faces = []
        data = []
        indices = {}
        slots = {}
        for poly, mat, custom_uv in patches:
            ids = []
            for vert in poly:
                key = tuple(round(c, 6) for c in vert)
                if key not in indices:
                    indices[key] = len(points)
                    points.append(key)
                ids.append(indices[key])
            if len(set(ids)) < 3:
                continue
            faces.append(ids)
            data.append((mat, custom_uv))
            if mat not in slots:
                slots[mat] = len(slots)
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(points, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        for mn in slots:
            mesh.materials.append(material(mn))
        uvs = mesh.uv_layers.new(name="表面纹理")
        for f, (mn, custom) in zip(mesh.polygons, data):
            f.material_index = slots[mn]
            n = f.normal
            if abs(n.z) >= max(abs(n.x), abs(n.y)) * 0.80:
                ax, ay = 0, 1
            elif abs(n.y) > abs(n.x):
                ax, ay = 0, 2
            else:
                ax, ay = 1, 2
            factor = (
                0.51
                if mn in ["teal", "greyTile", "greenTile", "goldTile", "lilac", "sky", "turquoise"]
                else 0.66
            )
            for j, i in enumerate(f.loop_indices):
                co = points[mesh.loops[i].vertex_index]
                uvs.data[i].uv = custom[j] if custom else (co[ax] * factor, co[ay] * factor)
        # Touching masonry blocks and stacked turret collars may share a cap.
        mesh.validate(clean_customdata=False)
        mesh.update()
        obj["part"] = name


def measure():
    blob = GLB.read_bytes()
    n = struct.unpack_from("<I", blob, 12)[0]
    j = json.loads(blob[20 : 20 + n])
    assert not any("uri" in a for a in j["images"])
    mesh_seen = [p for mesh in j["meshes"] for p in mesh["primitives"]]
    triangles = sum(j["accessors"][p["indices"]]["count"] // 3 for p in mesh_seen)
    aa = [j["accessors"][p["attributes"]["POSITION"]] for p in mesh_seen]
    return dict(
        id=SITE,
        name=META["name"],
        file=GLB.name,
        version="national-v1",
        source=META["visualSource"],
        sourceCopy=f"data/landmarks/{SITE}/source.blend",
        sourceSha256=hashlib.sha256((DIR / "source.blend").read_bytes()).hexdigest(),
        triangles=triangles,
        bytes=len(blob),
        sha256=hashlib.sha256(blob).hexdigest(),
        materials=len(j["materials"]),
        embeddedImages=len(j["images"]),
        bounds={
            "min": [min(a["min"][i] for a in aa) for i in range(3)],
            "max": [max(a["max"][i] for a in aa) for i in range(3)],
        },
        coordinateConvention="glTF Y-up; +Z front; Z-up editable master; local XY origin over geographic anchor",
    )


def export():
    bpy.ops.object.select_all(action="DESELECT")
    objects = [ob for ob in bpy.context.scene.objects if ob.type == "MESH"]
    for ob in objects:
        ob.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    out = bpy.context.object
    out.name = META["name"]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    out.data.calc_loop_triangles()
    raw = len(out.data.loop_triangles)
    if raw > 7700:
        mod = out.modifiers.new("全国视图几何简化", "DECIMATE")
        mod.ratio = 7450 / raw
        mod.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier=mod.name)
    out.data.validate(clean_customdata=False)
    out.data.update()
    bpy.ops.export_scene.gltf(
        filepath=str(GLB),
        export_format="GLB",
        use_selection=True,
        export_yup=True,
        export_apply=True,
        export_cameras=False,
        export_lights=False,
    )
    stats = measure()
    stats["sourceTriangles"] = raw
    assert stats["triangles"] <= 8000, (SITE, stats["triangles"])
    (DIR / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n")
    print(SITE, "source", raw, "web", stats["triangles"], stats["bytes"], flush=True)
    return stats


def previews():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(GLB))
    objects = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    points = [o.matrix_world @ Vector(p) for o in objects for p in o.bound_box]
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    ctr = (low + high) * 0.5
    size = high - low
    span = max(size)
    world = bpy.data.worlds.new("中性日光")
    world.use_nodes = True
    bpy.context.scene.world = world
    bg = world.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.72, 0.75, 0.80, 1)
    bg.inputs["Strength"].default_value = 0.70
    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 5
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 540
    scene.render.resolution_y = 420
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = "AgX"
    bpy.ops.mesh.primitive_plane_add(size=span * 150, location=(0, 0, low.z - 0.006))
    plane = bpy.context.object
    mat = bpy.data.materials.new("纸灰")
    mat.diffuse_color = (0.71, 0.715, 0.68, 1)
    plane.data.materials.append(mat)
    for label, direction, power, radius in [
        ("主光", (-1.0, -1.5, 2), 95, 1),
        ("填充", (1.6, -0.4, 1.2), 40, 1.45),
    ]:
        light = bpy.data.lights.new(label, "AREA")
        light.energy = power * span**2
        light.shape = "DISK"
        light.size = span * radius
        ob = bpy.data.objects.new(label, light)
        scene.collection.objects.link(ob)
        ob.location = ctr + Vector(direction) * span
        ob.rotation_euler = (ctr - ob.location).to_track_quat("-Z", "Y").to_euler()
    cam = bpy.data.cameras.new("回读验证相机")
    cam.type = "ORTHO"
    camera = bpy.data.objects.new("相机", cam)
    scene.collection.objects.link(camera)
    scene.camera = camera
    directory = DIR / "renders"
    directory.mkdir(exist_ok=True)
    for label, vec in [("正面", (0, -1, 0.13)), ("右侧", (1, 0, 0.14)), ("侧前方", (0.59, -1, 0.62))]:
        direction = Vector(vec).normalized()
        camera.location = ctr + direction * (span * 4)
        rot = (-direction).to_track_quat("-Z", "Y")
        camera.rotation_euler = rot.to_euler()
        vright = rot @ Vector((1, 0, 0))
        vup = rot @ Vector((0, 1, 0))
        px = [p.dot(vright) for p in points]
        py = [p.dot(vup) for p in points]
        cam.ortho_scale = 1.13 * max(max(px) - min(px), (max(py) - min(py)) * 540 / 420)
        cam.clip_end = span * 80
        scene.render.filepath = str(directory / (label + ".png"))
        bpy.ops.render.render(write_still=True)


if "--render-only" in ARGS:
    previews()
else:
    if "--from-master" in ARGS:
        bpy.ops.wm.open_mainfile(filepath=str(DIR / "source.blend"))
    else:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.preferences.filepaths.save_version = 0
        SCENES[SITE]()
        meshes()
        bpy.ops.wm.save_as_mainfile(filepath=str(DIR / "source.blend"), compress=True)
    export()
    if "--no-render" not in ARGS:
        previews()
