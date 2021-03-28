import yaml
import subprocess

def run_blender_background(blender_exec, blender_script):
    process = subprocess.run([
    blender_exec,
    '--background',
    '--python',
    blender_script]
    , capture_output=True, text=True)
    output = process.stdout
    error = process.stderr
    return output, error

with open("config.yaml") as f:
    config = yaml.safe_load(f)
print(config)

blender_exec = config["blender_exec_path"]
blender_script = config["blender_script"]

output, error = run_blender_background(blender_exec, blender_script)



if "Succesfull render" in output:
    print("Succesful subprocess call of blender")
else:
    print("Blender must have crashed")






