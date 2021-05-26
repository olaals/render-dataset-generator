from oa_blender import *
from oa_luxcore import *
import numpy as np
from oa_pointcloud_utils import *
from oa_luxcore_materials import *
from oa_bl_dataset_utils import *
import math
import matplotlib.pyplot as plt
from oa_filter import *
from oa_dev import *
import yaml
import random

def material_assigner(obj, pbrs_path, index):
    if index < 400:
        set_random_anisotropic(obj)
    else:
        set_random_pbr(obj, pbrs_path)
    
def log10_random(a,b):
    min_log = math.log10(a)
    max_log = math.log10(b)
    rand_log = random.uniform(min_log, max_log)
    return 10**rand_log
    

def set_random_anisotropic(obj):
    lowest_diff = 0.001
    highest_diff = 0.003
    lowest_u = 0.001
    highest_u = 0.2
    lowest_v = 0.001
    highest_v = 0.2
    
    diffuse = log10_random(lowest_diff, highest_diff)
    u = log10_random(lowest_u, highest_u)
    v = log10_random(lowest_v, highest_v)
    
    assign_alu_low_matte(obj, diffuse, u, v)
    return diffuse, u, v

def position_assigner(obj):
    min_phi_deg = -10
    max_phi_deg = -60
    min_theta_deg = 40
    max_theta_deg = 60
    min_r = 0.8
    max_r = 2.0
    
    phi = random.uniform(min_phi_deg, max_phi_deg)*math.pi/180
    print("phi", phi)
    theta = random.uniform(min_theta_deg, max_theta_deg)*math.pi/180
    r = random.uniform(min_r, max_r)
    loc_cart = sphere2cart(r, theta,phi)
    obj.set_location(loc_cart)
    print("")
    obj.look_at((0,0,0))
    print("")
    

def sphere2cart(r, theta, phi):
    return (
         r * math.sin(theta)*math.cos(phi),
         r * math.sin(theta)*math.sin(phi),
         r * math.cos(theta)
    )    

def main():
    
    # INIT SETUP
    delete_all()
    luxcore_setup(25)
    with open("config.yaml") as f:
        config = yaml.safe_load(f)
    index = config["stl_index"]
    
    # IMPORT OBJECT
    stl_path = config["stl_path"]
    obj = import_stl(stl_path)
    pbrs_path = config["pbrs_path"]
    
    dataset_folder = "double-scan-v1"
    scan_folder = os.path.join(dataset_folder, "scan"+('%04d' % index))
    os.makedirs(scan_folder, exist_ok=True)
    
    material_assigner(obj, pbrs_path, index)
    
    # SETUP HDR
    hdrs_path = config["hdrs_path"]
    set_random_hdri_luxcore(hdrs_path)

    # INIT SCANNER
    resolutions=[(1024,1024), (1024, 2048), (1024, 1024)]
    lumens = 2000
    intra_axial_dists = [0.2,0.2]
    sensor_widths = [24,12,24]

    ls = LuxcoreStereoLaserScanner("ls", location=(0.8,-0.4,1.0), resolutions=resolutions, sensor_widths= sensor_widths, intra_axial_dists=intra_axial_dists, lumens=lumens)
    ls.look_at((0,0,0))
    loc_cart = position_assigner(ls)
    
    ls.write_matrices(os.path.join(scan_folder, "matrices"))
    
    gt_scan, gt_mask, subpix = ls.get_ground_truth_scan(exposure=-8) 
    cv2_imwrite(os.path.join(scan_folder, "gt_scan.png"), gt_scan)

    
    img_l_e0 = ls.camera_left.get_image(halt_time=5, exposure=0)
    cv2_imwrite(os.path.join(scan_folder, "img_l_e0.png"), img_l_e0)
    img_r_e0 = ls.camera_right.get_image(halt_time=5, exposure=0)
    cv2_imwrite(os.path.join(scan_folder, "img_r_e0.png"), img_r_e0)
    
    img_l_e5 = ls.camera_left.get_image(halt_time=5, exposure=-6)
    cv2_imwrite(os.path.join(scan_folder, "img_l_e5.png"), img_l_e5)
    img_r_e5 = ls.camera_right.get_image(halt_time=5, exposure=-6)
    cv2_imwrite(os.path.join(scan_folder, "img_r_e5.png"), img_r_e5)
    
    bpy.context.scene.world.luxcore.gain = 0.0
    img_l = ls.camera_left.get_image(halt_time=5, exposure=-8)
    cv2_imwrite(os.path.join(scan_folder, "img_l.png"), img_l)
    img_r = ls.camera_right.get_image(halt_time=5, exposure=-8)
    cv2_imwrite(os.path.join(scan_folder, "img_r.png"), img_r)
    
    """
    fig,ax = plt.subplots(2,3)
    ax[0,0].imshow(img_l_e0)
    ax[1,0].imshow(img_r_e0)
    ax[0,1].imshow(img_l_e5)
    ax[1,1].imshow(img_r_e5)
    ax[0,2].imshow(img_l)
    ax[1,2].imshow(img_r)
    plt.show()
    """
    
    
    filter_func = lambda img: filter_value(img, 20)

    projected = ls.get_projected_view_img(filter_func,  cam_left_img=img_l, cam_right_img=img_r)
    cv2_imwrite(os.path.join(scan_folder, "proj.png"), projected)

    # POST PROCESSING
    
    img_l_gray = filter_value_gray(cv2.cvtColor(img_l, cv2.COLOR_RGB2GRAY), 20)
    proj_gray = cv2.cvtColor(projected, cv2.COLOR_RGB2GRAY)
    avg = average_channels_if_bitwise_nonzero(img_l_gray, proj_gray)
    cv2_imwrite(os.path.join(scan_folder, "nonzero_avg.png"), avg)
    
    
    """
    fig,ax = plt.subplots(2,3)
    ax[0,0].imshow(projected)
    ax[0,1].imshow(img_l_gray)
    ax[0,2].imshow(proj_gray)
    ax[1,0].imshow(avg)
    ax[1,1].imshow(gt_scan)
    ax[1,2].plot(subpix)
    plt.show()
    """

if __name__ == '__main__':
    main()
