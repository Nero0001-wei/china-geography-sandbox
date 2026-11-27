"""Build the national Zhongshan Mausoleum GLB from the local Blender copy."""

import hashlib
import json
from pathlib import Path
import struct

import bpy
from mathutils import Vector


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = HERE / 'source.blend'
PUBLIC_MODELS = ROOT / 'app' / 'public' / 'models'
OUTPUT = PUBLIC_MODELS / 'zhongshan.glb'
VIEWS = {'正面': '相机_正面', '右侧': '相机_右侧正交', '侧前方': '相机_侧前方'}


def select_only(obj):
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj


def check_glb():
    blob = OUTPUT.read_bytes()
    if blob[:4] != b'glTF' or struct.unpack_from('<II', blob, 4) != (2, len(blob)):
        raise RuntimeError('The output is not a complete glTF 2.0 binary.')
    length = struct.unpack_from('<I', blob, 12)[0]
    doc = json.loads(blob[20:20 + length])
    primitives = [item for mesh in doc['meshes'] for item in mesh['primitives']]
    accessors = doc['accessors']
    triangles = sum(accessors[item['indices']]['count'] // 3 for item in primitives)
    images = doc.get('images', [])
    if not 2_000 <= triangles <= 8_000:
        raise RuntimeError(f'Triangle budget not met: {triangles}')
    if not images or any('bufferView' not in image for image in images):
        raise RuntimeError('Expected every material image to be embedded in the GLB.')
    if any('COLOR_0' not in item['attributes'] for item in primitives):
        raise RuntimeError('Vertex contact shading was lost.')
    roof = next(material for material in doc['materials'] if '钴蓝琉璃瓦' in material['name'])
    red, green, blue, _ = roof['pbrMetallicRoughness']['baseColorFactor']
    if not blue > green > red:
        raise RuntimeError('The blue roof color was lost.')
    bounds = [accessors[item['attributes']['POSITION']] for item in primitives]
    minimum = [min(part['min'][i] for part in bounds) for i in range(3)]
    maximum = [max(part['max'][i] for part in bounds) for i in range(3)]
    if abs(minimum[1]) > 1e-5 or any(abs(minimum[i] + maximum[i]) > 1e-4 for i in (0, 2)):
        raise RuntimeError(f'Expected Y-up geometry over a centered base at Y = 0: {minimum}, {maximum}')
    return {
        'id': 'zhongshan',
        'name': '中山陵',
        'file': OUTPUT.name,
        'version': 'national-v1',
        'source': '南京城市沙盘/中山陵模型/web/中山陵_网页版.blend',
        'sourceCopy': 'data/landmarks/zhongshan/source.blend',
        'sourceSha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'sourceTriangles': 36_774,
        'sourceGlbBytes': 4_261_256,
        'triangles': triangles,
        'bytes': len(blob),
        'sha256': hashlib.sha256(blob).hexdigest(),
        'materials': len(doc['materials']),
        'embeddedImages': len(images),
        'vertexAO': True,
        'bounds': {'min': minimum, 'max': maximum},
        'coordinateConvention': 'glTF Y-up, +Z front, bottom-center origin',
    }


def export_model(asset):
    matrix = asset.matrix_world.copy()
    asset.parent = None
    asset.matrix_world = matrix
    select_only(asset)
    reduction = asset.modifiers.new('全国沙盘精度', 'DECIMATE')
    reduction.ratio = 0.205
    reduction.use_collapse_triangulate = True
    bpy.ops.object.modifier_apply(modifier=reduction.name)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)

    coordinates = [vertex.co for vertex in asset.data.vertices]
    minimum = Vector(min(point[i] for point in coordinates) for i in range(3))
    maximum = Vector(max(point[i] for point in coordinates) for i in range(3))
    offset = Vector(((minimum.x + maximum.x) / 2, (minimum.y + maximum.y) / 2, minimum.z))
    for vertex in asset.data.vertices:
        vertex.co -= offset
    asset.data.validate(verbose=False, clean_customdata=False)
    asset.data.update()
    asset.name = '中山陵'
    asset.data.name = '中山陵_全国版'

    # The copied preview applies vertex AO with a shader mix. glTF already
    # multiplies by COLOR_0, so export the original color or texture directly.
    for material in asset.data.materials:
        tree = material.node_tree
        shader = next(node for node in tree.nodes if node.type == 'BSDF_PRINCIPLED')
        base = shader.inputs['Base Color']
        if not base.links or base.links[0].from_node.type != 'MIX_RGB':
            continue
        link = base.links[0]
        original = link.from_node.inputs[1]
        tree.links.remove(link)
        if original.links:
            tree.links.new(original.links[0].from_socket, base)
        else:
            base.default_value = original.default_value

    images = {
        node.image for material in asset.data.materials for node in material.node_tree.nodes
        if node.type == 'TEX_IMAGE' and node.image
    }
    for image in images:
        if max(image.size) > 512:
            image.scale(512, 512)
            image.pack()

    PUBLIC_MODELS.mkdir(parents=True, exist_ok=True)
    bpy.ops.export_scene.gltf(
        filepath=str(OUTPUT), export_format='GLB', use_selection=True, export_apply=True,
        export_yup=True, export_vertex_color='ACTIVE', export_all_vertex_colors=False,
        export_cameras=False, export_lights=False,
    )


def render_views(original):
    bpy.data.objects.remove(original, do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(OUTPUT))
    imports = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    if len(imports) != 1:
        raise RuntimeError('Expected one landmark mesh when re-importing the exported GLB.')
    if any(not image.packed_file for image in bpy.data.images if image.users and image.source == 'FILE'):
        raise RuntimeError('A re-imported material depends on an external image.')

    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 20
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 768
    scene.render.resolution_y = 768
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    target = HERE / 'renders'
    target.mkdir(exist_ok=True)
    floor = bpy.data.objects.get('摄影棚地面')
    for name, camera in VIEWS.items():
        scene.camera = bpy.data.objects[camera]
        if floor:
            floor.hide_render = name == '右侧'
        scene.render.filepath = str(target / f'{name}.png')
        bpy.ops.render.render(write_still=True)


def main():
    if Path(bpy.data.filepath).resolve() != SOURCE:
        raise RuntimeError('Open the project-local source.blend to build, keeping the original project untouched.')
    asset = bpy.data.objects['中山陵_WEB_建筑']
    export_model(asset)
    stats = check_glb()
    (HERE / 'stats.json').write_text(json.dumps(stats, ensure_ascii=False, indent=2) + '\n')
    manifest_file = PUBLIC_MODELS / 'manifest.json'
    manifest = json.loads(manifest_file.read_text()) if manifest_file.exists() else {'models': []}
    manifest['models'] = [model for model in manifest['models'] if model['id'] != stats['id']]
    manifest['models'].append(stats)
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    print(f'National model exported: {stats["triangles"]} triangles, {stats["bytes"]} bytes', flush=True)
    render_views(asset)


if __name__ == '__main__':
    main()
