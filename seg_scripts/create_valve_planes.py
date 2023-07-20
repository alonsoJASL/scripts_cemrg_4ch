from img import *
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import copy
import json
import os
import argparse

# ----------------------------------------------------------------------------------------------
# Remake and load points.json
# ----------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='To run: python3 create_myo.py [path_to_points]')
parser.add_argument("path_to_points")
args = parser.parse_args()
path2points = args.path_to_points

os.system("python3 txt_2_json.py "+path2points+"/points.txt "+path2points+"/labels.txt "+path2points+"/points.json")

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

valve_WT = sf*4
valve_WT_svc_ivc = sf*4
ring_thickness = sf*4

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
# Prepare the seed points
# ----------------------------------------------------------------------------------------------
Ao_wall_tip_seed = points_data['Ao_WT_tip']
PArt_wall_tip_seed = points_data['PArt_WT_tip']

# ---------------------------------------------------------------------
# Reference for the header
# ---------------------------------------------------------------------
seg_array_good_header = sitk.ReadImage(path2points+'/seg_s2a.nrrd')

# ----------------------------------------------------------------------------------------------
# Removing parts of Ao and PArt wall remaining from cropping 
# ----------------------------------------------------------------------------------------------
print('\n ## Step 1/8: Cropping major vessels ## \n')
print(' ## Cropping major vessels: Removing remaining wall segments ## \n')
seg_s3r_array = connected_component(path2points+'seg_s3p.nrrd', Ao_wall_tip_seed, Ao_wall_label,path2points)
seg_s3r_array = np.swapaxes(seg_s3r_array,0,2)
# save_itk(seg_s3r_array, origin, spacings, path2points+'/seg_s3r.nrrd')
save_itk_keeping_header(new_image=seg_s3r_array, original_image=seg_array_good_header, filename=path2points+'/seg_s3r.nrrd')

print(" ## Cropping major vessels: Saved segmentation with aorta cropped ## \n")

seg_s3s_array = connected_component(path2points+'seg_s3r.nrrd', PArt_wall_tip_seed, PArt_wall_label,path2points)
seg_s3s_array = np.swapaxes(seg_s3s_array,0,2)
# save_itk(seg_s3s_array, origin, spacings, path2points+'/seg_s3s.nrrd')
save_itk_keeping_header(new_image=seg_s3s_array, original_image=seg_array_good_header, filename=path2points+'/seg_s3s.nrrd')

print(" ## Cropping major vessels: Saved segmentation with pulmonary artery cropped ## \n")

# ----------------------------------------------------------------------------------------------
# Create the mitral valve (MV)
# ----------------------------------------------------------------------------------------------
print('\n ## Step 2/8: Creating the mitral valve ## \n')
print(' ## MV: Executing distance map ## \n')
LA_BP_DistMap = distance_map(path2points+'seg_s3s.nrrd',LA_BP_label)
print(' ## MV: Writing temporary image ## \n')
sitk.WriteImage(LA_BP_DistMap,path2points+'/tmp/LA_BP_DistMap.nrrd',True)

print(' ## MV: Thresholding distance filter ## \n')
LA_BP_thresh = threshold_filter_nrrd(path2points+'/tmp/LA_BP_DistMap.nrrd',0,valve_WT)
sitk.WriteImage(LA_BP_thresh,path2points+'/tmp/LA_BP_thresh.nrrd',True)

print(' ## MV: AND filter of distance map and LV blood pool ## \n')
MV_array, header = nrrd.read(path2points+'/tmp/LA_BP_thresh.nrrd')
seg_s3s_array, header = nrrd.read(path2points+'seg_s3s.nrrd')
MV_array = and_filter(seg_s3s_array,MV_array,LV_BP_label,MV_label)
seg_s4a_array = add_masks_replace(seg_s3s_array,MV_array,MV_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## MV: Formatting and saving the segmentation ## \n')
seg_s4a_array = np.swapaxes(seg_s4a_array,0,2)
# save_itk(seg_s4a_array, origin, spacings, path2points+'/seg_s4a.nrrd')
save_itk_keeping_header(new_image=seg_s4a_array, original_image=seg_array_good_header, filename=path2points+'/seg_s4a.nrrd')

print(" ## MV: Saved segmentation with mitral valve added ## \n")

# ----------------------------------------------------------------------------------------------
# Closing holes around the mitral valve (MV)
# ----------------------------------------------------------------------------------------------
print(' ## MV corrections: Closing holes around the mitral valve ## \n')
print(' ## MV corrections: Executing distance map ## \n')
LV_myo_DistMap = distance_map(path2points+'seg_s4a.nrrd',LV_myo_label)
print(' ## MV corrections: Writing temporary image ## \n')
sitk.WriteImage(LV_myo_DistMap,path2points+'/tmp/LV_myo_DistMap.nrrd',True)

print(' ## MV corrections: Thresholding distance filter ## \n')
LA_myo_extra = threshold_filter_nrrd(path2points+'/tmp/LV_myo_DistMap.nrrd',0,LA_WT)
sitk.WriteImage(LA_myo_extra,path2points+'/tmp/LA_myo_extra.nrrd',True)

print(' ## MV correction: AND filter of distance map and LA blood pool ## \n')
LA_myo_extra_array, header = nrrd.read(path2points+'/tmp/LA_myo_extra.nrrd')
seg_s4a_array, header = nrrd.read(path2points+'/seg_s4a.nrrd')
LA_myo_extra_array = and_filter(seg_s4a_array,LA_myo_extra_array,LA_BP_label,LA_myo_label)
seg_s4b_array = add_masks_replace(seg_s4a_array,LA_myo_extra_array,LA_myo_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## MV corrections: Formatting and saving the segmentation ## \n')
seg_s4b_array = np.swapaxes(seg_s4b_array,0,2)
# save_itk(seg_s4b_array, origin, spacings, path2points+'/seg_s4b.nrrd')
save_itk_keeping_header(new_image=seg_s4b_array, original_image=seg_array_good_header, filename=path2points+'/seg_s4b.nrrd')

print(" ## MV extra: Saved segmentation with holes closed around mitral valve ## \n")

# ----------------------------------------------------------------------------------------------
# Create the tricuspid valve (TV)
# ----------------------------------------------------------------------------------------------
print('\n ## Step 3/8: Creating the tricuspid valve ## \n')
print(' ## TV: Executing distance map ## \n')
RA_BP_DistMap = distance_map(path2points+'/seg_s4b.nrrd',RA_BP_label)
print(' ## TV: Writing temporary image ## \n')
sitk.WriteImage(RA_BP_DistMap,path2points+'/tmp/RA_BP_DistMap.nrrd',True)

print(' ## TV: Thresholding distance filter ## \n')
RA_BP_thresh = threshold_filter_nrrd(path2points+'/tmp/RA_BP_DistMap.nrrd',0,valve_WT)
sitk.WriteImage(RA_BP_thresh,path2points+'/tmp/RA_BP_thresh.nrrd',True)

print(' ## TV: AND filter of distance map and RV blood pool ## \n')
TV_array, header = nrrd.read(path2points+'/tmp/RA_BP_thresh.nrrd')
seg_s4b_array, header = nrrd.read(path2points+'/seg_s4b.nrrd')
TV_array = and_filter(seg_s4b_array,TV_array,RV_BP_label,TV_label)
seg_s4c_array = add_masks_replace(seg_s4b_array,TV_array,TV_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## TV: Formatting and saving the segmentation ## \n')
seg_s4c_array = np.swapaxes(seg_s4c_array,0,2)
# save_itk(seg_s4c_array, origin, spacings, path2points+'/seg_s4c.nrrd')
save_itk_keeping_header(new_image=seg_s4c_array, original_image=seg_array_good_header, filename=path2points+'/seg_s4c.nrrd')

print(" ## TV: Saved segmentation with tricuspid valve added ## \n")

# ----------------------------------------------------------------------------------------------
# Closing holes around the tricuspid valve (TV)
# ----------------------------------------------------------------------------------------------
print(' ## TV corrections: Closing holes around the tricuspid valve ## \n')
print(' ## TV corrections: Executing distance map ## \n')
RV_myo_DistMap = distance_map(path2points+'/seg_s4c.nrrd',RV_myo_label)
print(' ## TV corrections: Writing temporary image ## \n')
sitk.WriteImage(RV_myo_DistMap,path2points+'/tmp/RV_myo_DistMap.nrrd',True)

print(' ## TV corrections: Thresholding distance filter ## \n')
RA_myo_extra = threshold_filter_nrrd(path2points+'/tmp/RV_myo_DistMap.nrrd',0,RA_WT)
sitk.WriteImage(RA_myo_extra,path2points+'/tmp/RA_myo_extra.nrrd',True)

print(' ## TV corrections: AND filter of distance map and RA blood pool ## \n')
RA_myo_extra_array, header = nrrd.read(path2points+'/tmp/RA_myo_extra.nrrd')
seg_s4c_array, header = nrrd.read(path2points+'/seg_s4c.nrrd')
RA_myo_extra_array = and_filter(seg_s4c_array,RA_myo_extra_array,RA_BP_label,RA_myo_label)
seg_s4d_array = add_masks_replace(seg_s4c_array,RA_myo_extra_array,RA_myo_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## TV corrections: Formatting and saving the segmentation ## \n')
seg_s4d_array = np.swapaxes(seg_s4d_array,0,2)
# save_itk(seg_s4d_array, origin, spacings, path2points+'/seg_s4d.nrrd')
save_itk_keeping_header(new_image=seg_s4d_array, original_image=seg_array_good_header, filename=path2points+'/seg_s4d.nrrd')

print(" ## TV corrections: Saved segmentation with holes closed around tricuspid valve ## \n")

# ----------------------------------------------------------------------------------------------
# Create the aortic valve (AV)
# ----------------------------------------------------------------------------------------------
print('\n ## Step 4/8: Creating the aortic valve ## \n')
print(' ## AV: Executing distance map ## \n')
Ao_BP_DistMap = distance_map(path2points+'/seg_s4d.nrrd',Ao_BP_label)
print(' ## AV: Writing temporary image ## \n')
sitk.WriteImage(Ao_BP_DistMap,path2points+'/tmp/Ao_BP_DistMap.nrrd',True)

print(' ## AV: Thresholding distance filter ## \n')
AV = threshold_filter_nrrd(path2points+'/tmp/Ao_BP_DistMap.nrrd',0,valve_WT)
sitk.WriteImage(AV,path2points+'/tmp/AV.nrrd',True)

print(' ## AV: AND filter of distance map and LV blood pool ## \n')
AV_array, header = nrrd.read(path2points+'/tmp/AV.nrrd')
seg_s4d_array, header = nrrd.read(path2points+'/seg_s4d.nrrd')
AV_array = and_filter(seg_s4d_array,AV_array,LV_BP_label,AV_label)
seg_s4e_array = add_masks_replace(seg_s4d_array,AV_array,AV_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## AV: Formatting and saving the segmentation ## \n')
seg_s4e_array = np.swapaxes(seg_s4e_array,0,2)
# save_itk(seg_s4e_array, origin, spacings, path2points+'/seg_s4e.nrrd')
save_itk_keeping_header(new_image=seg_s4e_array, original_image=seg_array_good_header, filename=path2points+'/seg_s4e.nrrd')

print(" ## AV: Saved segmentation with aortic valve added ## \n")

# ----------------------------------------------------------------------------------------------
# Closing holes around the aortic valve (AV)
# ----------------------------------------------------------------------------------------------
print(' ## AV corrections: Closing holes around the aortic valve ## \n')

print(' ## AV corrections: Thresholding distance filter ## \n')
Ao_wall_extra = threshold_filter_nrrd(path2points+'/tmp/LV_myo_DistMap.nrrd',0,Ao_WT)
sitk.WriteImage(Ao_wall_extra,path2points+'/tmp/Ao_wall_extra.nrrd',True)

print(' ## AV corrections: AND filter of distance map and Ao blood pool ## \n')
Ao_wall_extra_array, header = nrrd.read(path2points+'/tmp/Ao_wall_extra.nrrd')
seg_s4e_array, header = nrrd.read(path2points+'/seg_s4e.nrrd')
Ao_wall_extra_array = and_filter(seg_s4e_array,Ao_wall_extra_array,Ao_BP_label,Ao_wall_label)
seg_s4f_array = add_masks_replace(seg_s4e_array,Ao_wall_extra_array,Ao_wall_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## AV corrections: Formatting and saving the segmentation ## \n')
seg_s4f_array = np.swapaxes(seg_s4f_array,0,2)
# save_itk(seg_s4f_array, origin, spacings, path2points+'/seg_s4f.nrrd')
save_itk_keeping_header(new_image=seg_s4f_array, original_image=seg_array_good_header, filename=path2points+'/seg_s4f.nrrd')

print(" ## AV corrections: Saved segmentation with holes closed around aortic valve ## \n")

# ----------------------------------------------------------------------------------------------
# Separating the MV and AV
# ----------------------------------------------------------------------------------------------
print('\n ## AV corrections: Separating MV and AV ## \n')
print(' ## AV: Executing distance map ## \n')
AV_DistMap = distance_map(path2points+'/seg_s4f.nrrd',AV_label)
print(' ## AV: Writing temporary image ## \n')
sitk.WriteImage(AV_DistMap,path2points+'/tmp/AV_DistMap.nrrd',True)

print(' ## AV: Thresholding distance filter ## \n')
AV_sep = threshold_filter_nrrd(path2points+'/tmp/AV_DistMap.nrrd',0,2*valve_WT)
sitk.WriteImage(AV_sep,path2points+'/tmp/AV_sep.nrrd',True)

print(' ## AV: AND filter of distance map and MV ## \n')
AV_sep_array, header = nrrd.read(path2points+'/tmp/AV_sep.nrrd')
seg_s4f_array, header = nrrd.read(path2points+'/seg_s4f.nrrd')
AV_sep_array = and_filter(seg_s4f_array,AV_sep_array,MV_label,LV_myo_label)
seg_s4f_array = add_masks_replace(seg_s4f_array,AV_sep_array,LV_myo_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## AV: Formatting and saving the segmentation ## \n')
seg_s4f_array = np.swapaxes(seg_s4f_array,0,2)
# save_itk(seg_s4f_array, origin, spacings, path2points+'/seg_s4f.nrrd')
save_itk_keeping_header(new_image=seg_s4f_array, original_image=seg_array_good_header, filename=path2points+'/seg_s4f.nrrd')

print(" ## AV: Saved segmentation with AV and MV separated ## \n")

# ----------------------------------------------------------------------------------------------
# Closing new holes around the mitral valve (MV)
# ----------------------------------------------------------------------------------------------
print(' ## MV corrections: Closing holes around the mitral valve ## \n')
print(' ## MV corrections: Executing distance map ## \n')
LV_myo_DistMap = distance_map(path2points+'seg_s4f.nrrd',LV_myo_label)
print(' ## MV corrections: Writing temporary image ## \n')
sitk.WriteImage(LV_myo_DistMap,path2points+'/tmp/LV_myo_DistMap.nrrd',True)

print(' ## MV corrections: Thresholding distance filter ## \n')
LA_myo_extra = threshold_filter_nrrd(path2points+'/tmp/LV_myo_DistMap.nrrd',0,LA_WT)
sitk.WriteImage(LA_myo_extra,path2points+'/tmp/LA_myo_extra.nrrd',True)

print(' ## MV correction: AND filter of distance map and LA blood pool ## \n')
LA_myo_extra_array, header = nrrd.read(path2points+'/tmp/LA_myo_extra.nrrd')
seg_s4ff_array, header = nrrd.read(path2points+'/seg_s4f.nrrd')
LA_myo_extra_array = and_filter(seg_s4ff_array,LA_myo_extra_array,LA_BP_label,LA_myo_label)
seg_s4ff_array = add_masks_replace(seg_s4ff_array,LA_myo_extra_array,LA_myo_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## MV corrections: Formatting and saving the segmentation ## \n')
seg_s4ff_array = np.swapaxes(seg_s4ff_array,0,2)
# save_itk(seg_s4ff_array, origin, spacings, path2points+'/seg_s4ff.nrrd')
save_itk_keeping_header(new_image=seg_s4ff_array, original_image=seg_array_good_header, filename=path2points+'/seg_s4ff.nrrd')

print(" ## MV extra: Saved segmentation with holes closed around mitral valve ## \n")

# ----------------------------------------------------------------------------------------------
# Create the pulmonary valve (PV)
# ----------------------------------------------------------------------------------------------
print('\n ## Step 5/8: Creating the pulmonary valve ## \n')
print(' ## PV: Executing distance map ## \n')
PArt_BP_DistMap = distance_map(path2points+'/seg_s4ff.nrrd',PArt_BP_label)
print(' ## PV: Writing temporary image ## \n')
sitk.WriteImage(PArt_BP_DistMap,path2points+'/tmp/PArt_BP_DistMap.nrrd',True)

print(' ## PV: Thresholding distance filter ## \n')
PV = threshold_filter_nrrd(path2points+'/tmp/PArt_BP_DistMap.nrrd',0,valve_WT)
sitk.WriteImage(PV,path2points+'/tmp/PV.nrrd',True)

print(' ## PV: AND filter of distance map and RV blood pool ## \n')
PV_array, header = nrrd.read(path2points+'/tmp/PV.nrrd')
seg_s4ff_array, header = nrrd.read(path2points+'/seg_s4ff.nrrd')
PV_array = and_filter(seg_s4ff_array,PV_array,RV_BP_label,PV_label)
seg_s4g_array = add_masks_replace(seg_s4ff_array,PV_array,PV_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## PV: Formatting and saving the segmentation ## \n')
seg_s4g_array = np.swapaxes(seg_s4g_array,0,2)
# save_itk(seg_s4g_array, origin, spacings, path2points+'/seg_s4g.nrrd')
save_itk_keeping_header(new_image=seg_s4g_array, original_image=seg_array_good_header, filename=path2points+'/seg_s4g.nrrd')

print(" ## PV: Saved segmentation with pulmonary valve added ## \n")

# ----------------------------------------------------------------------------------------------
# Closing holes around the pulmonary valve (PV)
# ----------------------------------------------------------------------------------------------
print(' ## PV corrections: Closing holes around the pulmonary valve ## \n')

print(' ## PV corrections: Thresholding distance filter ## \n')
PArt_wall_extra = threshold_filter_nrrd(path2points+'/tmp/RV_myo_DistMap.nrrd',0,PArt_WT)
sitk.WriteImage(PArt_wall_extra,path2points+'/tmp/PArt_wall_extra.nrrd',True)

print(' ## PV corrections: AND filter of distance map and PArt blood pool ## \n')
PArt_wall_extra_array, header = nrrd.read(path2points+'/tmp/PArt_wall_extra.nrrd')
seg_s4g_array, header = nrrd.read(path2points+'/seg_s4g.nrrd')
PArt_wall_extra_array = and_filter(seg_s4g_array,PArt_wall_extra_array,PArt_BP_label,PArt_wall_label)
seg_s4h_array = add_masks_replace(seg_s4g_array,PArt_wall_extra_array,PArt_wall_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## PV corrections: Formatting and saving the segmentation ## \n')
seg_s4h_array = np.swapaxes(seg_s4h_array,0,2)
# save_itk(seg_s4h_array, origin, spacings, path2points+'/seg_s4h.nrrd')
save_itk_keeping_header(new_image=seg_s4h_array, original_image=seg_array_good_header, filename=path2points+'/seg_s4h.nrrd')

print(" ## PV corrections: Saved segmentation with holes closed around pulmonary valve ## \n")

# ----------------------------------------------------------------------------------------------
# Creating the distance maps needed to cut the vein rings
# ----------------------------------------------------------------------------------------------
print('\n ## Step 6/8: Create the distance maps needed to cut the vein rings ## \n')
print(' ## Create the distance maps needed to cut the vein rings: Executing distance map ## \n')
LA_myo_DistMap = distance_map(path2points+'/seg_s4h.nrrd',LA_myo_label)
RA_myo_DistMap = distance_map(path2points+'/seg_s4h.nrrd',RA_myo_label)
print(' ## Create the distance maps needed to cut the vein rings: Writing temporary image ## \n')
sitk.WriteImage(LA_myo_DistMap,path2points+'/tmp/LA_myo_DistMap.nrrd',True)
sitk.WriteImage(RA_myo_DistMap,path2points+'/tmp/RA_myo_DistMap.nrrd',True)

print(' ## Cutting vein rings: Thresholding distance filter ## \n')
LA_myo_thresh = threshold_filter_nrrd(path2points+'/tmp/LA_myo_DistMap.nrrd',0,ring_thickness)
RA_myo_thresh = threshold_filter_nrrd(path2points+'/tmp/RA_myo_DistMap.nrrd',0,ring_thickness)
sitk.WriteImage(LA_myo_thresh,path2points+'/tmp/LA_myo_thresh.nrrd',True)
sitk.WriteImage(RA_myo_thresh,path2points+'/tmp/RA_myo_thresh.nrrd',True)

LA_myo_thresh_array, header = nrrd.read(path2points+'/tmp/LA_myo_thresh.nrrd')
RA_myo_thresh_array, header = nrrd.read(path2points+'/tmp/RA_myo_thresh.nrrd')

# ----------------------------------------------------------------------------------------------
# Create ring for LPVeins1
# ----------------------------------------------------------------------------------------------
print('\n ## Step 7/8: Creating the vein rings ## \n')
print(' ## LPVeins1: Executing distance map ## \n')
LPV1_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',LPV1_label)
print(' ## LPVeins1: Writing temporary image ## \n')
sitk.WriteImage(LPV1_BP_DistMap,path2points+'/tmp/LPV1_BP_DistMap.nrrd',True)

print(' ## LPVeins1: Thresholding distance filter ## \n')
LPV1_ring = threshold_filter_nrrd(path2points+'/tmp/LPV1_BP_DistMap.nrrd',0,ring_thickness)
sitk.WriteImage(LPV1_ring,path2points+'/tmp/LPV1_ring.nrrd',True)

print(' ## LPVeins1: Add the ring to the segmentation ## \n')
LPV1_ring_array, header = nrrd.read(path2points+'/tmp/LPV1_ring.nrrd')
seg_s4h_array, header = nrrd.read(path2points+'/seg_s4h.nrrd')
seg_s4i_array = add_masks(seg_s4h_array,LPV1_ring_array,LPV1_ring_label)

LPV1_ring_array = and_filter(seg_s4i_array,LA_myo_thresh_array,LPV1_ring_label,LPV1_ring_label)
seg_s4j_array = add_masks_replace(seg_s4h_array,LPV1_ring_array,LPV1_ring_label)

# ----------------------------------------------------------------------------------------------
# Create ring for LPVeins2
# ----------------------------------------------------------------------------------------------
print('\n ## Creating the vein rings ## \n')
print(' ## LPVeins2: Executing distance map ## \n')
LPV2_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',LPV2_label)
print(' ## LPVeins2: Writing temporary image ## \n')
sitk.WriteImage(LPV2_BP_DistMap,path2points+'/tmp/LPV2_BP_DistMap.nrrd',True)

print(' ## LPVeins2: Thresholding distance filter ## \n')
LPV2_ring = threshold_filter_nrrd(path2points+'/tmp/LPV2_BP_DistMap.nrrd',0,ring_thickness)
sitk.WriteImage(LPV2_ring,path2points+'/tmp/LPV2_ring.nrrd',True)

print(' ## LPVeins2: Add the ring to the segmentation ## \n')
LPV2_ring_array, header = nrrd.read(path2points+'/tmp/LPV2_ring.nrrd')
seg_s4i_array = add_masks(seg_s4i_array,LPV2_ring_array,LPV2_ring_label)

LPV2_ring_array = and_filter(seg_s4i_array,LA_myo_thresh_array,LPV2_ring_label,LPV2_ring_label)
seg_s4j_array = add_masks_replace(seg_s4j_array,LPV2_ring_array,LPV2_ring_label)

# ----------------------------------------------------------------------------------------------
# Create ring for RPVeins1
# ----------------------------------------------------------------------------------------------
print('\n ## Creating the vein rings ## \n')
print(' ## RPVeins1: Executing distance map ## \n')
RPV1_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',RPV1_label)
print(' ## RPVeins1: Writing temporary image ## \n')
sitk.WriteImage(RPV1_BP_DistMap,path2points+'/tmp/RPV1_BP_DistMap.nrrd',True)

print(' ## RPVeins1: Thresholding distance filter ## \n')
RPV1_ring = threshold_filter_nrrd(path2points+'/tmp/RPV1_BP_DistMap.nrrd',0,ring_thickness)
sitk.WriteImage(RPV1_ring,path2points+'/tmp/RPV1_ring.nrrd',True)

print(' ## RPVeins1: Add the ring to the segmentation ## \n')
RPV1_ring_array, header = nrrd.read(path2points+'/tmp/RPV1_ring.nrrd')
seg_s4i_array = add_masks_replace_only(seg_s4i_array,RPV1_ring_array,RPV1_ring_label,SVC_label)

RPV1_ring_array = and_filter(seg_s4i_array,LA_myo_thresh_array,RPV1_ring_label,RPV1_ring_label)
seg_s4j_array = add_masks_replace(seg_s4j_array,RPV1_ring_array,RPV1_ring_label)

# ----------------------------------------------------------------------------------------------
# Create ring for RPVeins2
# ----------------------------------------------------------------------------------------------
print('\n ## Creating the vein rings ## \n')
print(' ## RPVeins2: Executing distance map ## \n')
RPV2_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',RPV2_label)
print(' ## RPVeins2: Writing temporary image ## \n')
sitk.WriteImage(RPV2_BP_DistMap,path2points+'/tmp/RPV2_BP_DistMap.nrrd',True)

print(' ## RPVeins2: Thresholding distance filter ## \n')
RPV2_ring = threshold_filter_nrrd(path2points+'/tmp/RPV2_BP_DistMap.nrrd',0,ring_thickness)
sitk.WriteImage(RPV2_ring,path2points+'/tmp/RPV2_ring.nrrd',True)

print(' ## RPVeins2: Add the ring to the segmentation ## \n')
RPV2_ring_array, header = nrrd.read(path2points+'/tmp/RPV2_ring.nrrd')
seg_s4i_array = add_masks(seg_s4i_array,RPV2_ring_array,RPV2_ring_label)

RPV2_ring_array = and_filter(seg_s4i_array,LA_myo_thresh_array,RPV2_ring_label,RPV2_ring_label)
seg_s4j_array = add_masks_replace(seg_s4j_array,RPV2_ring_array,RPV2_ring_label)

# ----------------------------------------------------------------------------------------------
# Create ring for LAA
# ----------------------------------------------------------------------------------------------
print('\n ## Creating the vein rings ## \n')
print(' ## LAA: Executing distance map ## \n')
LAA_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',LAA_label)
print(' ## LAA: Writing temporary image ## \n')
sitk.WriteImage(LAA_BP_DistMap,path2points+'/tmp/LAA_BP_DistMap.nrrd',True)

print(' ## LAA: Thresholding distance filter ## \n')
LAA_ring = threshold_filter_nrrd(path2points+'/tmp/LAA_BP_DistMap.nrrd',0,ring_thickness)
sitk.WriteImage(LAA_ring,path2points+'/tmp/LAA_ring.nrrd',True)

print(' ## LAA: Add the ring to the segmentation ## \n')
LAA_ring_array, header = nrrd.read(path2points+'/tmp/LAA_ring.nrrd')
seg_s4i_array = add_masks(seg_s4i_array,LAA_ring_array,LAA_ring_label)

LAA_ring_array = and_filter(seg_s4i_array,LA_myo_thresh_array,LAA_ring_label,LAA_ring_label)
seg_s4j_array = add_masks_replace(seg_s4j_array,LAA_ring_array,LAA_ring_label)

# ----------------------------------------------------------------------------------------------
# Create ring for SVC
# ----------------------------------------------------------------------------------------------
print('\n ## Creating the vein rings ## \n')
print(' ## SVC: Executing distance map ## \n')
SVC_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',SVC_label)
print(' ## SVC: Writing temporary image ## \n')
sitk.WriteImage(SVC_BP_DistMap,path2points+'/tmp/SVC_BP_DistMap.nrrd',True)

print(' ## SVC: Thresholding distance filter ## \n')
SVC_ring = threshold_filter_nrrd(path2points+'/tmp/SVC_BP_DistMap.nrrd',0,ring_thickness)
sitk.WriteImage(SVC_ring,path2points+'/tmp/SVC_ring.nrrd',True)

print(' ## SVC: Add the ring to the segmentation ## \n')
SVC_ring_array, header = nrrd.read(path2points+'/tmp/SVC_ring.nrrd')
seg_s4i_array = add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,Ao_wall_label)
seg_s4i_array = add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,LA_myo_label)
seg_s4i_array = add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,RPV1_ring_label)
seg_s4i_array = add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,RPV1_label)

SVC_ring_array = and_filter(seg_s4i_array,RA_myo_thresh_array,SVC_ring_label,SVC_ring_label)
seg_s4j_array = add_masks_replace(seg_s4j_array,SVC_ring_array,SVC_ring_label)

# ----------------------------------------------------------------------------------------------
# Create ring for IVC
# ----------------------------------------------------------------------------------------------
print('\n ## Creating the vein rings ## \n')
print(' ## IVC: Executing distance map ## \n')
IVC_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',IVC_label)
print(' ## IVC: Writing temporary image ## \n')
sitk.WriteImage(IVC_BP_DistMap,path2points+'/tmp/IVC_BP_DistMap.nrrd',True)

print(' ## IVC: Thresholding distance filter ## \n')
IVC_ring = threshold_filter_nrrd(path2points+'/tmp/IVC_BP_DistMap.nrrd',0,ring_thickness)
sitk.WriteImage(IVC_ring,path2points+'/tmp/IVC_ring.nrrd',True)

print(' ## IVC: Add the ring to the segmentation ## \n')
IVC_ring_array, header = nrrd.read(path2points+'/tmp/IVC_ring.nrrd')
seg_s4i_array = add_masks(seg_s4i_array,IVC_ring_array,IVC_ring_label)

IVC_ring_array = and_filter(seg_s4i_array,RA_myo_thresh_array,IVC_ring_label,IVC_ring_label)
seg_s4j_array = add_masks_replace(seg_s4j_array,IVC_ring_array,IVC_ring_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## Vein rings: Formatting and saving the segmentation ## \n')
seg_s4i_array = np.swapaxes(seg_s4i_array,0,2)
# save_itk(seg_s4i_array, origin, spacings, path2points+'/seg_s4i.nrrd')
save_itk_keeping_header(new_image=seg_s4i_array, original_image=seg_array_good_header, filename=path2points+'/seg_s4i.nrrd')

print(" ## Vein rings: Saved segmentation with veins rings added ## \n")

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## Cutting vein rings: Formatting and saving the segmentation ## \n')
seg_s4j_array = np.swapaxes(seg_s4j_array,0,2)
# save_itk(seg_s4j_array, origin, spacings, path2points+'/seg_s4j.nrrd')
save_itk_keeping_header(new_image=seg_s4j_array, original_image=seg_array_good_header, filename=path2points+'/seg_s4j.nrrd')

print(" ## Cutting vein rings: Saved segmentation with veins rings added ## \n")

# ----------------------------------------------------------------------------------------------
# Creating plane for LPV1
# ----------------------------------------------------------------------------------------------
print('\n ## Step 8/8: Creating the valve planes ## \n')
print(' ## Valve planes: LPV1 ## \n')
seg_s4j_array, header = nrrd.read(path2points+'/seg_s4j.nrrd')
LA_BP_thresh_array, header = nrrd.read(path2points+'/tmp/LA_BP_thresh.nrrd')

plane_LPV1_array = and_filter(seg_s4j_array,LA_BP_thresh_array,LPV1_label,plane_LPV1_label)
seg_s4k_array = add_masks_replace(seg_s4j_array,plane_LPV1_array,plane_LPV1_label)

# ----------------------------------------------------------------------------------------------
# Creating plane for LPV2
# ----------------------------------------------------------------------------------------------
print(' ## Valve planes: LPV2 ## \n')
plane_LPV2_array = and_filter(seg_s4k_array,LA_BP_thresh_array,LPV2_label,plane_LPV2_label)
seg_s4k_array = add_masks_replace(seg_s4k_array,plane_LPV2_array,plane_LPV2_label)

# ----------------------------------------------------------------------------------------------
# Creating plane for RPV1
# ----------------------------------------------------------------------------------------------
print(' ## Valve planes: RPV1 ## \n')
plane_RPV1_array = and_filter(seg_s4k_array,LA_BP_thresh_array,RPV1_label,plane_RPV1_label)
seg_s4k_array = add_masks_replace(seg_s4k_array,plane_RPV1_array,plane_RPV1_label)

# ----------------------------------------------------------------------------------------------
# Creating plane for RPV2
# ----------------------------------------------------------------------------------------------
print(' ## Valve planes: RPV2 ## \n')
plane_RPV2_array = and_filter(seg_s4k_array,LA_BP_thresh_array,RPV2_label,plane_RPV2_label)
seg_s4k_array = add_masks_replace(seg_s4k_array,plane_RPV2_array,plane_RPV2_label)

# ----------------------------------------------------------------------------------------------
# Creating plane for LAA
# ----------------------------------------------------------------------------------------------
print(' ## Valve planes: LAA ## \n')
plane_LAA_array = and_filter(seg_s4k_array,LA_BP_thresh_array,LAA_label,plane_LAA_label)
seg_s4k_array = add_masks_replace(seg_s4k_array,plane_LAA_array,plane_LAA_label)

# ----------------------------------------------------------------------------------------------
# Creating plane for SVC
# ----------------------------------------------------------------------------------------------
print(' ## Valve planes: SVC ## \n')
RA_BP_thresh_2mm = threshold_filter_nrrd(path2points+'/tmp/RA_BP_DistMap.nrrd',0,valve_WT_svc_ivc)
sitk.WriteImage(RA_BP_thresh_2mm,path2points+'/tmp/RA_BP_thresh_2mm.nrrd',True)

RA_BP_thresh_2mm_array, header = nrrd.read(path2points+'/tmp/RA_BP_thresh_2mm.nrrd')

plane_SVC_array = and_filter(seg_s4k_array,RA_BP_thresh_2mm_array,SVC_label,plane_SVC_label)
plane_SVC_extra_array = and_filter(seg_s4k_array,RA_BP_thresh_2mm_array,RPV1_ring_label,plane_SVC_label)
seg_s4k_array = add_masks_replace(seg_s4k_array,plane_SVC_array,plane_SVC_label)
seg_s4k_array = add_masks_replace(seg_s4k_array,plane_SVC_extra_array,plane_SVC_label)

# ----------------------------------------------------------------------------------------------
# Creating plane for IVC
# ----------------------------------------------------------------------------------------------
print(' ## Valve planes: IVC ## \n')
plane_IVC_array = and_filter(seg_s4k_array,RA_BP_thresh_2mm_array,IVC_label,plane_IVC_label)
seg_s4k_array = add_masks_replace(seg_s4k_array,plane_IVC_array,plane_IVC_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## Valve planes: Formatting and saving the segmentation ## \n')
seg_s4k_array = np.swapaxes(seg_s4k_array,0,2)
# save_itk(seg_s4k_array, origin, spacings, path2points+'/seg_s4k.nrrd')
save_itk_keeping_header(new_image=seg_s4k_array, original_image=seg_array_good_header, filename=path2points+'/seg_s4k.nrrd')

print(" ## Valve planes: Saved segmentation with all valve planes added ## \n")

