
from seg_scripts.img import save_itk, push_inside
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import json
import argparse
import os

from seg_scripts.common import parse_txt_to_json, get_json_data, mycp

# ----------------------------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------------------------
SCALE_FACTOR = 1/0.39844 # scale factor

valve_WT = SCALE_FACTOR*2.5
ring_thickness = SCALE_FACTOR*4

LV_WT = SCALE_FACTOR*2.00
RV_WT = SCALE_FACTOR*3.50
LA_WT = SCALE_FACTOR*2.00
RA_WT = SCALE_FACTOR*2.00
Ao_WT = SCALE_FACTOR*2.00
PArt_WT = SCALE_FACTOR*2.00

LV_BP_label = 1
LV_myo_label = 2
RV_BP_label = 3
LA_BP_label = 4
RA_BP_label = 5
Ao_BP_label = 6
PArt_BP_label = 7
LPV1_label = 8
LPV2_label = 9
RPV1_label = 10
RPV2_label = 11
LAA_label = 12
SVC_label = 13
IVC_label = 14

LV_neck_label = 101
RV_myo_label = 103
LA_myo_label = 104
RA_myo_label = 105
Ao_wall_label = 106
PArt_wall_label = 107

MV_label = 201
TV_label = 202
AV_label = 203
PV_label = 204
plane_LPV1_label = 205
plane_LPV2_label = 206
plane_RPV1_label = 207
plane_RPV2_label = 208
plane_LAA_label = 209
plane_SVC_label = 210
plane_IVC_label = 211

LPV1_ring_label = 221
LPV2_ring_label = 222
RPV1_ring_label = 223
RPV2_ring_label = 224
LAA_ring_label = 225
SVC_ring_label = 226
IVC_ring_label = 227

def correct_rings(base_dir, img_file, origin, spacings, pusher_wall_lab,pushed_wall_lab,pushed_BP_lab,pushed_WT, output_path=""): 
    if output_path == "":
        output_path = img_file
    seg_array = push_inside(base_dir, img_file, pusher_wall_lab, pushed_wall_lab, pushed_BP_lab, pushed_WT)
    seg_array = np.swapaxes(seg_array,0,2)
    save_itk(seg_array, origin, spacings, output_path)
    print(" ## Correcting rings: Formatted and saved segmentation ## \n")

def main(args):
    # ----------------------------------------------------------------------------------------------
    # Load points.json
    # ----------------------------------------------------------------------------------------------
    path2points = args.path_to_points
    path2originjson = args.origin_spacing_json

    origin_spacing_output_file = parse_txt_to_json(path2points, path2originjson, "origin_spacing", "origin_spacing_labels")
    origin_data = get_json_data(origin_spacing_output_file)

    origin = origin_data['origin']
    spacings = origin_data['spacing']

    DIR = lambda x: os.path.join(path2points, x)

    # REMINDER ON HOW TO USE PUSH_INSIDE FUNCTION
    # Pushing A_ring with B_ring
    # seg_s5_array = push_inside(path2points,path2points+'seg_s5.nrrd',B_ring_label,A_ring_label,A_label,ring_thickness)

    # ----------------------------------------------------------------------------------------------
    # Create seg_s5
    # ----------------------------------------------------------------------------------------------
    print(' ## Creating seg_s5 ## \n')
    mycp(DIR('seg_s4k.nrrd'), DIR('seg_s5.nrrd'))

    # ----------------------------------------------------------------------------------------------
    # RPV2_ring is pushed by RPV1_ring
    # ----------------------------------------------------------------------------------------------
    print(' ## Correcting rings: Pushing RPV2_ring with RPV1_ring ## \n')
    correct_rings(path2points,DIR('seg_s5.nrrd'),origin,spacings,RPV1_ring_label,RPV2_ring_label,RPV2_label,ring_thickness)

    # ----------------------------------------------------------------------------------------------
    # LPV2_ring is pushed by LPV1_ring
    # ----------------------------------------------------------------------------------------------
    print(' ## Correcting rings: Pushing LPV2_ring with LPV1_ring ## \n')
    correct_rings(path2points,DIR('seg_s5.nrrd'),origin,spacings,LPV1_ring_label,LPV2_ring_label,LPV2_label,ring_thickness)

    # ----------------------------------------------------------------------------------------------
    # LAA_ring is pushed by LPV1_ring
    # ----------------------------------------------------------------------------------------------
    print(' ## Correcting rings: Pushing LAA_ring with LPV1_ring ## \n')
    correct_rings(path2points,DIR('seg_s5.nrrd'),origin,spacings,LPV1_ring_label,LAA_ring_label,LAA_label,ring_thickness)
    seg_s5_array = push_inside(path2points,DIR('seg_s5.nrrd'),LPV1_ring_label,LAA_ring_label,LAA_label,ring_thickness)

    # # ----------------------------------------------------------------------------------------------
    # # Ao_wall is pushed by SVC_ring
    # # ----------------------------------------------------------------------------------------------
    # print(' ## Pushing Ao wall with SVC_ring ## \n')
    # seg_s5_array = push_inside(path2points,DIR('seg_s5.nrrd'),SVC_ring_label,Ao_wall_label,Ao_BP_label,Ao_WT)
    # seg_s5_array = np.swapaxes(seg_s5_array,0,2)
    # save_itk(seg_s5_array, origin, spacings, DIR('seg_s5.nrrd'))
    # print(" ## Correcting rings: Formatted and saved segmentation ## \n")

    # ----------------------------------------------------------------------------------------------
    # Ao_wall is pushed by RV_myo
    # ----------------------------------------------------------------------------------------------
    print(' ## Pushing Ao wall with RV_myo ## \n')
    correct_rings(path2points,DIR('seg_s5.nrrd'),origin,spacings,RV_myo_label,Ao_wall_label,Ao_BP_label,Ao_WT)
   
    # ----------------------------------------------------------------------------------------------
    # LA_myo is pushed by SVC_ring
    # ----------------------------------------------------------------------------------------------
    print(' ## Pushing LA_myo with SVC_ring ## \n')
    correct_rings(path2points,DIR('seg_s5.nrrd'),origin,spacings,SVC_ring_label,LA_myo_label,LA_BP_label,LA_WT)

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description='To run: python3 clean_seg.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    args = parser.parse_args()
    main(args)
# ring_thickness
# LPV1_ring_label
# LPV2_ring_label
# RPV1_ring_label
# RPV2_ring_label
# LAA_ring_label
# SVC_ring_label
# LPV2_label
# RPV2_label
# LAA_label
# RV_myo_label
# LA_myo_label
# LA_BP_label
# Ao_BP_label
# LA_WT
# Ao_WT
# Ao_wall_label