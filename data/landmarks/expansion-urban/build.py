"""Build urban landmark masters, GLBs and previews from separate editable meshes."""

import argparse
import hashlib
import json
import math
import random
import struct
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(HERE), str(HERE.parent / "workshop-c")]

from geometry import PARTS
from scenes import SCENES, PALETTE


def load_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("sites", nargs="*")
    parser.add_argument("--no-render", action="store_true")
    parser.add_argument("--render-only", action="store_true")
    parser.add_argument("--from-master", action="store_true")
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])


def material(name):
    if name in bpy.data.materials:
        return bpy.data.materials[name]
    color, pattern, roughness = PALETTE[name]
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1)
    mat.use_nodes = True
    shader = mat.node_tree.nodes.get("Principled BSDF")
    shader.inputs["Base Color"].default_value = (*color, 1)
    shader.inputs["Roughness"].default_value = roughness
    if name in {"steel", "bronze", "pearl", "ice"}:
        shader.inputs["Metallic"].default_value = 0.17
    if not pattern:
        return mat

    width = 64
    noise = random.Random(name)
    tile = bpy.data.images.new(name + "-颜色", width=width, height=width, alpha=False)
    tile.colorspace_settings.name = "sRGB"
    rgba = []
    for y in range(width):
        for x in range(width):
            shade = 0.93 + 0.12 * noise.random()
            if pattern == "brick" and (y % 8 == 0 or (x + 8 * (y // 8)) % 16 == 0):
                shade *= 0.75
            if pattern == "tile" and (y % 16 == 0 or x % 8 == 0):
                shade *= 0.76
            if pattern == "coursed" and (y % 13 == 0 or (x + 9 * (y // 13)) % 31 == 0):
                shade *= 0.64
            if pattern == "water":
                shade += 0.075 * math.sin(y * math.pi / 8 + math.sin(x * math.pi / 16))
            # Image pixel assignment uses linear floats, which Blender packs into the image color space.
            rgba.extend([min(1, component * shade) for component in color] + [1])
    tile.pixels.foreach_set(rgba)
    tile.pack()
    tex = mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image = tile
    mat.node_tree.links.new(tex.outputs["Color"], shader.inputs["Base Color"])
    return mat


def build_meshes():
    for part_name, patches in PARTS.items():
        points, faces, attributes = [], [], []
        vertex_lookup, material_slots = {}, {}
        for polygon, material_name, custom_uv in patches:
            indexes = []
            for vertex in polygon:
                key = tuple(round(x, 6) for x in vertex)
                if key not in vertex_lookup:
                    vertex_lookup[key] = len(points)
                    points.append(key)
                indexes.append(vertex_lookup[key])
            if len(set(indexes)) < 3:
                continue
            faces.append(indexes)
            attributes.append((material_name, custom_uv))
            if material_name not in material_slots:
                material_slots[material_name] = len(material_slots)
        mesh = bpy.data.meshes.new(part_name)
        mesh.from_pydata(points, [], faces)
        mesh.update()
        obj = bpy.data.objects.new(part_name, mesh)
        bpy.context.scene.collection.objects.link(obj)
        for name in material_slots:
            mesh.materials.append(material(name))
        uv = mesh.uv_layers.new(name="表面纹理")
        for polygon, (name, custom_uv) in zip(mesh.polygons, attributes):
            polygon.material_index = material_slots[name]
            direction = max(range(3), key=lambda axis: abs(polygon.normal[axis]))
            u, v = [axis for axis in range(3) if axis != direction]
            for j, index in enumerate(polygon.loop_indices):
                co = points[mesh.loops[index].vertex_index]
                uv.data[index].uv = custom_uv[j] if custom_uv else (co[u] * 0.47, co[v] * 0.47)
        mesh.validate(clean_customdata=False)
        mesh.update()


def export_and_measure(directory, meta, filename):
    objs = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objs:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.join()
    model = bpy.context.object
    model.name = meta["name"]
    model.data.calc_loop_triangles()
    source_triangles = len(model.data.loop_triangles)
    if source_triangles > 7800:
        modifier = model.modifiers.new("全国模型几何简化", "DECIMATE")
        modifier.ratio = 7400 / source_triangles
        modifier.use_collapse_triangulate = True
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.ops.export_scene.gltf(filepath=str(filename), export_format="GLB", use_selection=True,
                              export_yup=True, export_cameras=False, export_lights=False)
    blob = filename.read_bytes()
    length = struct.unpack_from("<I", blob, 12)[0]
    gltf = json.loads(blob[20:20 + length])
    images = gltf.get("images", [])
    assert all("bufferView" in image for image in images)
    primitives = [primitive for mesh in gltf["meshes"] for primitive in mesh["primitives"]]
    positions = [gltf["accessors"][primitive["attributes"]["POSITION"]] for primitive in primitives]
    triangle_count = sum(gltf["accessors"][primitive["indices"]]["count"] // 3 for primitive in primitives)
    assert 0 < triangle_count <= 8000, (meta["id"], triangle_count)
    assert abs(min(p["min"][1] for p in positions)) < 0.002, (meta["id"], "base height")
    result = {
        "id": meta["id"], "name": meta["name"], "file": filename.name,
        "version": "national-v1", "source": meta["visualSource"],
        "sourceCopy": f"data/landmarks/{meta['id']}/source.blend",
        "sourceSha256": hashlib.sha256((directory / "source.blend").read_bytes()).hexdigest(),
        "triangles": triangle_count, "bytes": len(blob), "sha256": hashlib.sha256(blob).hexdigest(),
        "materials": len(gltf["materials"]), "embeddedImages": len(images), "sourceTriangles": source_triangles,
        "bounds": {"min": [min(p["min"][i] for p in positions) for i in range(3)],
                   "max": [max(p["max"][i] for p in positions) for i in range(3)]},
        "coordinateConvention": "glTF Y-up and +Z front; Blender Z-up and -Y front; ground at Y=0",
    }
    (directory / "stats.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(f"URBAN {meta['id']} {triangle_count} {len(blob)}", flush=True)
    return result


def render_views(directory, filename):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(filename))
    objects = [obj for obj in bpy.context.scene.objects if obj.type == "MESH"]
    corners = [obj.matrix_world @ Vector(point) for obj in objects for point in obj.bound_box]
    low = Vector([min(point[i] for point in corners) for i in range(3)])
    high = Vector([max(point[i] for point in corners) for i in range(3)])
    aim = (low + high) * 0.5
    span = max(high - low)
    scene = bpy.context.scene
    scene.world = bpy.data.worlds.new("日光环境")
    scene.world.use_nodes = True
    background = scene.world.node_tree.nodes.get("Background")
    background.inputs["Color"].default_value = (0.63, 0.69, 0.8, 1)
    background.inputs["Strength"].default_value = 0.65
    bpy.ops.mesh.primitive_plane_add(size=span * 150, location=(0, 0, low.z - 0.006))
    clay = bpy.data.materials.new("浅灰摄影台")
    clay.diffuse_color = (0.58, 0.57, 0.54, 1)
    bpy.context.object.data.materials.append(clay)

    for label, direction, power, radius in (
        ("主光", (-1, -1.55, 2.25), 104, 1.0),
        ("补光", (1.65, 0.75, 1.4), 64, 1.45),
    ):
        light = bpy.data.lights.new(label, "AREA")
        light.energy = power * span ** 2
        light.shape = "DISK"
        light.size = span * radius
        obj = bpy.data.objects.new(label, light)
        scene.collection.objects.link(obj)
        obj.location = aim + span * Vector(direction)
        obj.rotation_euler = (aim - obj.location).to_track_quat("-Z", "Y").to_euler()
    camera = bpy.data.cameras.new("GLB 验收相机")
    camera.type = "ORTHO"
    camera.clip_end = span * 100
    view = bpy.data.objects.new("相机", camera)
    scene.collection.objects.link(view)
    scene.camera = view
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 4
    scene.cycles.use_denoising = True
    scene.render.resolution_x, scene.render.resolution_y = 440, 340
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"

    output = directory / "renders"
    output.mkdir(exist_ok=True)
    for label, direction in (
        ("正面", (0, -1, 0.20)), ("右侧", (1, 0, 0.20)), ("侧前方", (0.68, -1, 0.72)),
    ):
        delta = Vector(direction).normalized()
        view.location = aim + delta * 4 * span
        rotation = (-delta).to_track_quat("-Z", "Y")
        view.rotation_euler = rotation.to_euler()
        right, up = rotation @ Vector((1, 0, 0)), rotation @ Vector((0, 1, 0))
        xs = [point.dot(right) for point in corners]
        ys = [point.dot(up) for point in corners]
        camera.ortho_scale = 1.14 * max(max(xs) - min(xs), (max(ys) - min(ys)) * 440 / 340)
        scene.render.filepath = str(output / f"{label}.png")
        bpy.ops.render.render(write_still=True)


def main():
    options = load_options()
    for landmark_id in options.sites or SCENES:
        directory = HERE.parent / landmark_id
        meta = json.loads((directory / "site.json").read_text())
        filename = ROOT / "app/public/models" / f"{landmark_id}.glb"
        if not options.render_only:
            if options.from_master:
                bpy.ops.wm.open_mainfile(filepath=str(directory / "source.blend"))
            else:
                bpy.ops.wm.read_factory_settings(use_empty=True)
                bpy.context.preferences.filepaths.save_version = 0
                PARTS.clear()
                SCENES[landmark_id]()
                build_meshes()
                bpy.ops.wm.save_as_mainfile(filepath=str(directory / "source.blend"), compress=True)
            export_and_measure(directory, meta, filename)
        if not options.no_render:
            render_views(directory, filename)


if __name__ == "__main__":
    main()
