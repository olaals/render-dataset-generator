import yaml
import subprocess
import glob
import time

CONFIG_NAME = 'config.yaml'
STL_PATH_CONFIG = 'stl_path'
STL_INDEX_CONFIG = 'stl_index'
NUM_IMAGES_TO_GENERATE = 999

def run_blender_background(blender_exec, blender_script):
    bl_command = [
    blender_exec,
    '--background',
    'scene.blend',
    '--python',
    blender_script]
    print(bl_command)
    process = subprocess.run( bl_command
    , capture_output=True, text=True)
    output = process.stdout
    error = process.stderr
    return output, error

def change_config_stl(config_name, config, stl_path, index):
    config[STL_PATH_CONFIG] = stl_path
    config[STL_INDEX_CONFIG] = index
    print("Config before edit")
    print(config)
    with open(CONFIG_NAME, 'w') as f:
        yaml.safe_dump(config, f)
        


with open(CONFIG_NAME) as f:
    config = yaml.safe_load(f)
print(config)

blender_exec = config["blender_exec_path"]
blender_script = config["blender_script"]
stl_corners_path = config["stl_corners_path"]

stl_list = glob.glob(stl_corners_path+"/*.stl")
stl_list.sort()


successfull = 0
failed = 0
for stl_index in range(NUM_IMAGES_TO_GENERATE):
    stl_path = stl_list[stl_index]

    change_config_stl(CONFIG_NAME, config, stl_path, stl_index)
    time.sleep(0.1)

    output, error = run_blender_background(blender_exec, blender_script)

    if "Succesfull render" in output:
        print("Succesful subprocess call of blender")
        successfull += 1
    else:
        print("Blender must have crashed")
        print(error)
        failed += 1
        print(f'Failed with index {stl_index}')

print("Succesfull")
print(successfull)
print("Failed")
print(failed)





