import bpy
import yaml

with open("config.yaml") as f:
    config = yaml.safe_load(f)

print(config)

print("Test a render, change this")
bpy.context.scene.render.filepath = "test.png"
bpy.ops.render.render(write_still=True)





print("Succesfull render")
