import os
import shutil
import argparse

DS_PROJ_DIR = 'dataset-projects'
DATASET_SUBDIR = 'dataset'
TEMPLATE_DIR = 'template'
CONFIG_NAME = 'config.yaml'
PYTHON_BLENDER_SCRIPT = 'blender_script.py'

description = "Generate folder structure for a new dataset generated with Blender"

parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)


parser.add_argument('dataset_project_name', help="Folder name of the dataset project generation folder")
parser.add_argument('subfolders', nargs="*", help="Subfolder dataset names")

args = parser.parse_args()
dataset_project_name = args.dataset_project_name
subfolders = args.subfolders

# Unique names for subfolders, can not be same
assert(len(subfolders) == len(set(subfolders)))

dataset_project_path = os.path.join(DS_PROJ_DIR, dataset_project_name)

shutil.copytree(TEMPLATE_DIR, dataset_project_path)
dataset_subdir_path = os.path.join(dataset_project_path, DATASET_SUBDIR)
for subfolder in subfolders:
    subfolder_path = os.path.join(dataset_subdir_path, subfolder)
    os.mkdir(subfolder_path)


config_yaml_path = os.path.join(dataset_project_path, CONFIG_NAME)

with open(config_yaml_path, 'a') as f:
    f.write(f'blender_script: {PYTHON_BLENDER_SCRIPT}\n')
    for subfolder in subfolders:
        relative_subfolder_path = os.path.join(DATASET_SUBDIR, subfolder)
        f.write(f'{subfolder}_path: {relative_subfolder_path}\n')

print(f"Created dataset project {dataset_project_name}")
if subfolders:
    print(f'with subfolders {subfolders}')







