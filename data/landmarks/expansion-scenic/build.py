"""Build the second grouping of terrain and public attraction exteriors."""
from pathlib import Path
import json
import sys

import bpy

HERE = Path(__file__).resolve().parent
COMMON = HERE.parent / "expansion-nature"
sys.path[:0] = [str(COMMON), str(HERE)]
import build as pipeline
from shapes import PARTS

from natural import erhai, hukou_falls, qutang_kuimen
from structures import chimelong_ocean_kingdom, fast_observatory, shark_skin_texture

SCENES = {
    "hukou-falls": hukou_falls,
    "qutang-kuimen": qutang_kuimen,
    "erhai": erhai,
    "fast-observatory": fast_observatory,
    "chimelong-ocean-kingdom": chimelong_ocean_kingdom,
}

SCENIC_COLORS = {
    "hukouStone0": "4B3D34", "hukouStone1": "77614E", "hukouStone2": "97826E",
    "hukouStone3": "AA987B", "hukouStone4": "665950", "riverOchre": "B2763E",
    "riverHoney": "CC8D48", "riverGold": "DBA85A", "riverIvory": "F4DBA5",
    "riverDusk": "976231", "gorgeWater": "427C79",
    "gorgeRipple": "719E95", "gorgeBlue": "345F73", "gorgeCanopy": "526346",
    "gorgeShadow": "5C5B52", "gorgeWall": "7E7B6B", "gorgeCut": "605B4F",
    "redLime": "AA8B78", "paleLime": "B0AAA0", "gorgePale": "AEA08A",
    "erhaiLake": "428F99", "erhaiWaterCut": "376976", "erhaiRipple": "7CADAC",
    "erhaiRoof": "4E4B42", "erhaiWood": "875A44", "erhaiReed": "7C8356",
    "erhaiSand": "C1AB8E", "erhaiGrey": "8F8978", "erhaiDistant": "798B97",
    "erhaiDistantLight": "9CAAAE", "reflectorWhite": "CFD7D7", "reflectorIce": "C4CED0",
    "reflectorShadow": "797F7D", "reflectorPanel": "B6C2C6", "reflectorCable": "858C8D",
    "oceanPlaza": "C8BDA3", "oceanPlazaLight": "DDCEB8", "oceanPlazaBlue": "8BC3C8",
    "marineDark": "183D4C", "marineBlue": "3D819B",
    "marineShadow": "245A70", "waveDark": "1F6574", "waveDeep": "2C7D8D",
    "waveTeal": "448B8F", "waveShallow": "63A7A9", "waveCrest": "8DBAB1",
    "coralRose": "C87765", "coralGold": "D5AC72", "coralOrange": "D3966B",
}


def polish_materials():
    for material, mat in pipeline.MATERIALS.items():
        shader = mat.node_tree.nodes.get("Principled BSDF")
        if material in ("gorgeWater", "erhaiLake", "riverOchre", "riverHoney", "riverGold"):
            shader.inputs["Roughness"].default_value = .36
        elif material.startswith("reflector"):
            shader.inputs["Metallic"].default_value = .22
            shader.inputs["Roughness"].default_value = .48
        elif material.startswith(("marine","wave")):
            shader.inputs["Roughness"].default_value = .53


def smooth(label):
    if obj := bpy.data.objects.get(label):
        for poly in obj.data.polygons:
            poly.use_smooth = True


def map_shark_skin():
    label="昂首的立体鲸鲨"
    shark=bpy.data.objects[label]
    uv=shark.data.uv_layers.active
    for poly, (_, _, coordinates) in zip(shark.data.polygons, PARTS[label]):
        for loop, pair in zip(poly.loop_indices,coordinates):
            uv.data[loop].uv=pair
        poly.use_smooth=len(poly.vertices)==4
    sculpt=pipeline.MATERIALS["sharkSkin"]
    principled=sculpt.node_tree.nodes.get("Principled BSDF")
    principled.inputs["Roughness"].default_value=.55
    node=sculpt.node_tree.nodes.new("ShaderNodeTexImage")
    node.image=shark_skin_texture(bpy)
    node.extension="REPEAT"
    sculpt.node_tree.links.new(node.outputs["Color"],principled.inputs["Base Color"])
    smooth("外张的胸鳍")


def make_master(sm, directory):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version = 0
    pipeline.COLORS.update(SCENIC_COLORS)
    if sm=="hukou-falls":
        pipeline.COLORS["cutSoil"]="826449"
    SCENES[sm]()
    pipeline.assemble()
    polish_materials()
    if sm=="chimelong-ocean-kingdom":
        map_shark_skin()
    if sm=="fast-observatory":
        smooth("FAST 下凹球面反射盘")
    bpy.ops.wm.save_as_mainfile(filepath=str(directory/"source.blend"),compress=True)


def main():
    args=sys.argv[sys.argv.index("--")+1:]
    slug=args[0]
    directory=HERE.parent/slug
    meta=json.loads((directory/"site.json").read_text())
    glb=pipeline.ROOT/"app/public/models"/(slug+".glb")
    if "--render-only" not in args:
        if "--from-master" in args:
            bpy.ops.wm.open_mainfile(filepath=str(directory/"source.blend"))
        else:
            make_master(slug,directory)
        pipeline.export(glb,directory,meta)
    if "--no-render" not in args:
        pipeline.previews(glb,directory)


if __name__=="__main__":
    main()
