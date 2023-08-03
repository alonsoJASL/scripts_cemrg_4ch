from img import mask_plane_creator
from img import add_masks
from img import add_masks_replace
from img import add_masks_replace_only
from img import add_masks_replace_except
from img import add_masks_replace_except_2
from img import save_itk
from img import connected_component
from img import distance_map
from img import threshold_filter
from img import threshold_filter_nrrd
from img import push_inside
from img import remove_filter
from img import and_filter
from img import save_itk_keeping_header
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import json
import argparse
import os

# ----------------------------------------------------------------------------------------------
# Load points.json
# ----------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='To run: python3 clean_seg.py [path_to_points]')
parser.add_argument("path_to_points")
args = parser.parse_args()
path2points = args.path_to_points

points_file = open(path2points+'/points.json')
points_data = json.load(points_file)

# ----------------------------------------------------------------------------------------------
# Find the origin and spacing
# ----------------------------------------------------------------------------------------------
# NOTE - We save the origin and spacings because the "save_itk" function used in
# the next step makes the format of the header difficult to work with.
# ----------------------------------------------------------------------------------------------
origin_spacing_file = open(path2points+'/origin_spacing.json')
origin_spacing_data = json.load(origin_spacing_file)
origin = origin_spacing_data['origin']
spacings = origin_spacing_data['spacing']

# ---------------------------------------------------------------------
# Reference for the header
# ---------------------------------------------------------------------
seg_array_good_header = sitk.ReadImage(path2points+'/seg_s2a.nrrd')

# ----------------------------------------------------------------------------------------------
# Define the wall thickness
# ----------------------------------------------------------------------------------------------
# sf = 1/0.39844 # scale factor
sf = np.ceil(1.0/spacings[0]) # scale factor

valve_WT = sf*2.5
ring_thickness = sf*4

LV_WT = sf*2.00;
RV_WT = sf*3.50;
LA_WT = sf*2.00;
RA_WT = sf*2.00;
Ao_WT = sf*2.00;
PArt_WT = sf*2.00;

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

# REMINDER ON HOW TO USE PUSH_INSIDE FUNCTION
# Pushing A_ring with B_ring
# seg_s5_array = push_inside(path2points,path2points+'seg_s5.nrrd',B_ring_label,A_ring_label,A_label,ring_thickness)

# ----------------------------------------------------------------------------------------------
# Create seg_s5
# ----------------------------------------------------------------------------------------------
print(' ## Creating seg_s5 ## \n')
os.system("cp "+path2points+"/seg_s4k.nrrd "+path2points+"/seg_s5.nrrd")

# ----------------------------------------------------------------------------------------------
# RPV2_ring is pushed by RPV1_ring
# ----------------------------------------------------------------------------------------------
print(' ## Correcting rings: Pushing RPV2_ring with RPV1_ring ## \n')
seg_s5_array = push_inside(path2points,path2points+'seg_s5.nrrd',RPV1_ring_label,RPV2_ring_label,RPV2_label,ring_thickness)
seg_s5_array = np.swapaxes(seg_s5_array,0,2)
# save_itk(seg_s5_array, origin, spacings, path2points+'/seg_s5.nrrd')
save_itk_keeping_header(new_image=seg_s5_array, original_image=seg_array_good_header, filename=path2points+'/seg_s5.nrrd')

print(" ## Correcting rings: Formatted and saved segmentation ## \n")

# ----------------------------------------------------------------------------------------------
# LPV2_ring is pushed by LPV1_ring
# ----------------------------------------------------------------------------------------------
print(' ## Correcting rings: Pushing LPV2_ring with LPV1_ring ## \n')
seg_s5_array = push_inside(path2points,path2points+'seg_s5.nrrd',LPV1_ring_label,LPV2_ring_label,LPV2_label,ring_thickness)
seg_s5_array = np.swapaxes(seg_s5_array,0,2)
# save_itk(seg_s5_array, origin, spacings, path2points+'/seg_s5.nrrd')
save_itk_keeping_header(new_image=seg_s5_array, original_image=seg_array_good_header, filename=path2points+'/seg_s5.nrrd')

print(" ## Correcting rings: Formatted and saved segmentation ## \n")

# ----------------------------------------------------------------------------------------------
# LAA_ring is pushed by LPV1_ring
# ----------------------------------------------------------------------------------------------
print(' ## Correcting rings: Pushing LAA_ring with LPV1_ring ## \n')
seg_s5_array = push_inside(path2points,path2points+'seg_s5.nrrd',LPV1_ring_label,LAA_ring_label,LAA_label,ring_thickness)
seg_s5_array = np.swapaxes(seg_s5_array,0,2)
# save_itk(seg_s5_array, origin, spacings, path2points+'/seg_s5.nrrd')
save_itk_keeping_header(new_image=seg_s5_array, original_image=seg_array_good_header, filename=path2points+'/seg_s5.nrrd')

print(" ## Correcting rings: Formatted and saved segmentation ## \n")

# # ----------------------------------------------------------------------------------------------
# # Ao_wall is pushed by SVC_ring
# # ----------------------------------------------------------------------------------------------
# print(' ## Pushing Ao wall with SVC_ring ## \n')
# seg_s5_array = push_inside(path2points,path2points+'seg_s5.nrrd',SVC_ring_label,Ao_wall_label,Ao_BP_label,Ao_WT)
# seg_s5_array = np.swapaxes(seg_s5_array,0,2)
# save_itk(seg_s5_array, origin, spacings, path2points+'/seg_s5.nrrd')
# print(" ## Correcting rings: Formatted and saved segmentation ## \n")

# ----------------------------------------------------------------------------------------------
# Ao_wall is pushed by RV_myo
# ----------------------------------------------------------------------------------------------
print(' ## Pushing Ao wall with RV_myo ## \n')
seg_s5_array = push_inside(path2points,path2points+'seg_s5.nrrd',RV_myo_label,Ao_wall_label,Ao_BP_label,Ao_WT)
seg_s5_array = np.swapaxes(seg_s5_array,0,2)
# save_itk(seg_s5_array, origin, spacings, path2points+'/seg_s5.nrrd')
save_itk_keeping_header(new_image=seg_s5_array, original_image=seg_array_good_header, filename=path2points+'/seg_s5.nrrd')

print(" ## Correcting rings: Formatted and saved segmentation ## \n")

# ----------------------------------------------------------------------------------------------
# LA_myo is pushed by SVC_ring
# ----------------------------------------------------------------------------------------------
print(' ## Pushing LA_myo with SVC_ring ## \n')
seg_s5_array = push_inside(path2points,path2points+'seg_s5.nrrd',SVC_ring_label,LA_myo_label,LA_BP_label,LA_WT)
seg_s5_array = np.swapaxes(seg_s5_array,0,2)
# save_itk(seg_s5_array, origin, spacings, path2points+'/seg_s5.nrrd')
save_itk_keeping_header(new_image=seg_s5_array, original_image=seg_array_good_header, filename=path2points+'/seg_s5.nrrd')

print(" ## Correcting rings: Formatted and saved segmentation ## \n")

