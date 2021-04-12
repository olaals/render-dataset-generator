import bpy
import yaml
from oa_blender import *
from oa_luxcore import *
import glob
import random
from random import uniform
import numpy as np
import math
from oa_luxcore_materials import *
from oa_bl_dataset_utils import *
import matplotlib.pyplot as plt
import time

GT_HALT_TIME = 10
TRAIN_FILT_HALT_TIME = 20
TRAIN_RAW_HALT_TIME = 30

def polar2cart(r, theta, phi):
    return (
         r * math.cos(theta),
         r * math.sin(theta),
         r * math.cos(theta)
    )


with open("config.yaml") as f:
    config = yaml.safe_load(f)

print(config)

delete_all()

luxcore_setup(120)

r_min, r_max = 1.0, 3.0
theta_min, theta_max = -math.pi/6, math.pi/6
phi_min, phi_max = math.pi/6, math.pi/3


stl_path = config["stl_path"]
print(stl_path)
stl_index = config["stl_index"]
print(stl_index)
train_filt_path = config["train_filt_path"]
print(train_filt_path)
train_raw_path = config["train_raw_path"]
print(train_raw_path)
ground_truth_path = config["ground_truth_path"]
print(ground_truth_path)
pbrs_path = config["pbrs_path"]
print(pbrs_path)
hdrs_path = config["hdrs_path"]
print(hdrs_path)

r = uniform(r_min,r_max)
theta = uniform(theta_min, theta_max)
phi = uniform(phi_min, phi_max)

camera_px_size = uniform(2e-2, 3e-2)


obj = import_stl(stl_path)
time.sleep(2)
print("")
intra_axial_dist = uniform(0.2,2.0)
cam_laser_angle = 2*np.arctan((intra_axial_dist/2)/(r+0.1))
laser_scanner = LuxcoreLaserScanner("laserScanner", camera_resolution=(500,500), camera_pixel_size=camera_px_size, intra_axial_dist=intra_axial_dist, angle=cam_laser_angle)
print(f'r {r}, theta {theta}, phi {phi}')
loc = polar2cart(r, theta, phi)
laser_scanner.set_location(loc)
print("")
print("Wait for look at")
print("")
laser_scanner.look_at((0,0,0))
time.sleep(1)
print("")



# GROUND TRUTH RENDER
bpy.context.scene.world.luxcore.light = 'none'
bpy.context.scene.luxcore.halt.time = GT_HALT_TIME
bpy.context.scene.luxcore.config.path.depth_total = 1
gt_img = laser_scanner.camera.get_image()
gt_img = convert_to_binary(gt_img)
gt_img = row_wise_mean_index(gt_img)
cv2.imwrite(os.path.join(ground_truth_path, "img"+('%03d' % stl_index)+".png"), gt_img)

# ASSIGN MATERIAL
if random.random() < 0.8:
    set_random_pbr(obj, pbrs_path)
else:
    assign_mix_material(obj,"Metal", "Metal")

# REFLECTION SETUP
bpy.context.scene.luxcore.config.path.depth_total = 3
bpy.context.scene.luxcore.config.path.depth_specular = 3
bpy.context.scene.luxcore.config.path.depth_diffuse = 3
bpy.context.scene.luxcore.config.path.depth_glossy = 3

# TRAIN FILTERED RENDER
bpy.context.scene.luxcore.halt.time = TRAIN_FILT_HALT_TIME
train_img = laser_scanner.camera.get_image()
train_img = cv2.cvtColor(train_img, cv2.COLOR_RGB2BGR)
cv2.imwrite(os.path.join(train_filt_path, "img"+('%03d' % stl_index)+".png"), train_img)

# TRAIN RAW RENDER
set_random_hdri_luxcore(hdrs_path)
bpy.context.scene.luxcore.halt.time = TRAIN_RAW_HALT_TIME
train_img = laser_scanner.camera.get_image()
train_img = cv2.cvtColor(train_img, cv2.COLOR_RGB2BGR)
cv2.imwrite(os.path.join(train_raw_path, "img"+('%03d' % stl_index)+".png"), train_img)
bpy.data.objects.remove(obj, do_unlink=True)





print("Succesfull render")
