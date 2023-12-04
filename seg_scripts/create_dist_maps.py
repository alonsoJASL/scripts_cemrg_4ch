from seg_scripts.img import mask_plane_creator
from seg_scripts.img import add_masks
from seg_scripts.img import add_masks_replace
from seg_scripts.img import add_masks_replace_only
from seg_scripts.img import add_masks_replace_except
from seg_scripts.img import add_masks_replace_except_2
from seg_scripts.img import save_itk
from seg_scripts.img import connected_component
from seg_scripts.img import distance_map
from seg_scripts.img import threshold_filter
from seg_scripts.img import threshold_filter_nrrd
from seg_scripts.img import push_inside
from seg_scripts.img import remove_filter
from seg_scripts.img import and_filter
import SimpleITK as sitk

import numpy as np
import nrrd
import pylab
import json
import argparse

# ----------------------------------------------------------------------------------------------
# Load points.json
# ----------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='To run: python3 create_dist_maps.py [path_to_points]')
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

# ----------------------------------------------------------------------------------------------
# Define the wall thickness
# ----------------------------------------------------------------------------------------------
sf = 1/0.39844 # scale factor

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

# ----------------------------------------------------------------------------------------------
# Create distance maps of the valve planes
# ----------------------------------------------------------------------------------------------
print('\n ## Step 1/9: Creating distance maps of the valve planes ## \n')
print(' ## plane_LPV1: Executing distance map ## \n')
plane_LPV1_DistMap = distance_map(path2points+'seg_s4k.nrrd',plane_LPV1_label)
print(' ## plane_LPV1: Writing temporary image ## \n')
sitk.WriteImage(plane_LPV1_DistMap,path2points+'/tmp/plane_LPV1_DistMap.nrrd',True)

print('\n ## Step 2/9: Creating distance maps of the valve planes ## \n')
print(' ## plane_LPV2: Executing distance map ## \n')
plane_LPV2_DistMap = distance_map(path2points+'seg_s4k.nrrd',plane_LPV2_label)
print(' ## plane_LPV2: Writing temporary image ## \n')
sitk.WriteImage(plane_LPV2_DistMap,path2points+'/tmp/plane_LPV2_DistMap.nrrd',True)

print('\n ## Step 3/9: Creating distance maps of the valve planes ## \n')
print(' ## plane_RPV1: Executing distance map ## \n')
plane_RPV1_DistMap = distance_map(path2points+'seg_s4k.nrrd',plane_RPV1_label)
print(' ## plane_RPV1: Writing temporary image ## \n')
sitk.WriteImage(plane_RPV1_DistMap,path2points+'/tmp/plane_RPV1_DistMap.nrrd',True)

print('\n ## Step 4/9: Creating distance maps of the valve planes ## \n')
print(' ## plane_RPV2: Executing distance map ## \n')
plane_RPV2_DistMap = distance_map(path2points+'seg_s4k.nrrd',plane_RPV2_label)
print(' ## plane_RPV2: Writing temporary image ## \n')
sitk.WriteImage(plane_RPV2_DistMap,path2points+'/tmp/plane_RPV2_DistMap.nrrd',True)

print('\n ## Step 5/9: Creating distance maps of the valve planes ## \n')
print(' ## plane_LAA: Executing distance map ## \n')
plane_LAA_DistMap = distance_map(path2points+'seg_s4k.nrrd',plane_LAA_label)
print(' ## plane_LAA: Writing temporary image ## \n')
sitk.WriteImage(plane_LAA_DistMap,path2points+'/tmp/plane_LAA_DistMap.nrrd',True)

print('\n ## Step 6/9: Creating distance maps of the valve planes ## \n')
print(' ## plane_SVC: Executing distance map ## \n')
plane_SVC_DistMap = distance_map(path2points+'seg_s4k.nrrd',plane_SVC_label)
print(' ## plane_SVC: Writing temporary image ## \n')
sitk.WriteImage(plane_SVC_DistMap,path2points+'/tmp/plane_SVC_DistMap.nrrd',True)

print('\n ## Step 7/9: Creating distance maps of the valve planes ## \n')
print(' ## plane_IVC: Executing distance map ## \n')
plane_IVC_DistMap = distance_map(path2points+'seg_s4k.nrrd',plane_IVC_label)
print(' ## plane_IVC: Writing temporary image ## \n')
sitk.WriteImage(plane_IVC_DistMap,path2points+'/tmp/plane_IVC_DistMap.nrrd',True)


