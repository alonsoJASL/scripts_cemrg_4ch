from img import *
import SimpleITK as sitk

import numpy as np
import nrrd
import copy
import json
import os
import argparse

# ----------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='To run: python3 create_myo.py [path_to_points]')
parser.add_argument("path_to_points")
args = parser.parse_args()
path2points = args.path_to_points

os.system("python3 txt_2_json.py "+path2points+"/points.txt "+path2points+"/labels.txt "+path2points+"/points.json")

points_file = open(path2points+'/points.json')
points_data = json.load(points_file)

thickness_file = open(f"{path2points}/thickness.json")
thickness_data = json.load(thickness_file)
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

# ----------------------------------------------------------------------------------------------
# Define the wall thickness
# ----------------------------------------------------------------------------------------------
# sf = 1/0.39844 # scale factor
sf = np.ceil(1.0/spacings[0]) # scale factor

valve_WT = sf*thickness_data["valves"]
valve_WT_svc_ivc = sf*thickness_data["valves"]
ring_thickness = sf*thickness_data["rings"]

LA_WT = sf*thickness_data["LA"]
RA_WT = sf*thickness_data["RA"]
Ao_WT = sf*thickness_data["aorta"]
PArt_WT = sf*thickness_data["RV"]

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

# ---------------------------------------------------------------------
# Reference for the header
# ---------------------------------------------------------------------
seg_array_good_header = sitk.ReadImage(path2points+'/seg_s5.nrrd')

# ----------------------------------------------------------------------------------------------
# Closing gap between pulmonary valve and RV myocardium
# ----------------------------------------------------------------------------------------------
print(' ## PValve corrections: Closing gap between the pulmonary valve and the RV myocardium ## \n')
print(' ## PValve corrections: Executing distance map ## \n')
RV_BP_DistMap = distance_map(path2points+'seg_s5.nrrd',RV_BP_label)
print(' ## PValve corrections: Writing temporary image ## \n')
sitk.WriteImage(RV_BP_DistMap,path2points+'/tmp/RV_myo_DistMap.nrrd',True)

print(' ## PValve corrections: Thresholding distance filter ## \n')
RV_myo_extra = threshold_filter_nrrd(path2points+'/tmp/RV_myo_DistMap.nrrd',0,PArt_WT)
sitk.WriteImage(RV_myo_extra,path2points+'/tmp/RV_myo_extra.nrrd',True)

print(' ## PValve correction: AND filter of distance map and PArt wall thickness ## \n')
RV_myo_extra_array, header = nrrd.read(path2points+'/tmp/RV_myo_extra.nrrd')
seg_5_array, header = nrrd.read(path2points+'/seg_s5.nrrd')
RV_myo_extra_array = and_filter(seg_5_array,RV_myo_extra_array,PArt_wall_label,RV_myo_label)
seg_s6_array = add_masks_replace(seg_5_array,RV_myo_extra_array,RV_myo_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## PValve corrections: Formatting and saving the segmentation ## \n')
seg_s6_array = np.swapaxes(seg_s6_array,0,2)
# save_itk(seg_s4b_array, origin, spacings, path2points+'/seg_s4b.nrrd')
save_itk_keeping_header(new_image=seg_s6_array, original_image=seg_array_good_header, filename=path2points+'/seg_s6.nrrd')

print(" ## PValve extra: Saved segmentation with gap between pulmonary valve and RV myocardium closed ## \n")
