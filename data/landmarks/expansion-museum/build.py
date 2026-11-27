"""Build the six museum and civic models with the shared urban export pipeline."""

import importlib.util
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
SHARED = HERE.parent / "expansion-urban"
sys.dont_write_bytecode = True
sys.path.insert(0, str(HERE))


def main():
    spec = importlib.util.spec_from_file_location("urban_export", SHARED / "build.py")
    pipeline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pipeline)
    from civic_scenes import PALETTE, SCENES

    default_material = pipeline.material

    def material(name):
        if name != "carvedName" or name in bpy.data.materials:
            return default_material(name)
        surface = default_material(name)
        image = bpy.data.images.load(str(HERE / "stone-inscription.png"), check_existing=True)
        image.pack()
        texture = surface.node_tree.nodes.new("ShaderNodeTexImage")
        texture.image = image
        shader = surface.node_tree.nodes.get("Principled BSDF")
        surface.node_tree.links.new(texture.outputs["Color"], shader.inputs["Base Color"])
        return surface

    pipeline.PALETTE = PALETTE
    pipeline.SCENES = SCENES
    pipeline.HERE = HERE
    pipeline.material = material
    pipeline.main()


if __name__ == "__main__":
    main()
