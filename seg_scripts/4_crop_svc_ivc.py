from img import *
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import json
import os
import argparse
# ----------------------------------------------------------------------------------------------
# Remake and load points.json
# ----------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description='To run: python3 crop_svc_ivc.py [path_to_points]')
parser.add_argument("path_to_points")
args = parser.parse_args()
path2points = args.path_to_points
scriptsPath = "/data/Dropbox/scripts_cemrgapp/seg_scripts/"

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
# Prepare info from json files
# ----------------------------------------------------------------------------------------------

# SVC
SVC_seed = points_data['SVC_tip']
# IVC
IVC_seed = points_data['IVC_tip']

# Ideally this step will be done by reading a json file but 
# currently can't make sitk.ConnectedThreshold work - 
# ERROR = argument of type 'uint8_t
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

# ----------------------------------------------------------------------------------------------
# Make a folder to hold temporary images
# ----------------------------------------------------------------------------------------------
os.system("mkdir "+path2points+"/tmp")

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

# # ----------------------------------------------------------------------------------------------
# # Slice svc and ivc
# # ---------------------------------------------------------------------------------------------
# SVC_slicer_1 = points_data['SVC_slicer_1']
# SVC_slicer_2 = points_data['SVC_slicer_2']
# SVC_slicer_3 = points_data['SVC_slicer_3']
# slicer_points = [SVC_slicer_1[0],SVC_slicer_1[1],SVC_slicer_1[2],SVC_slicer_2[0],SVC_slicer_2[1],SVC_slicer_2[2],SVC_slicer_3[0],SVC_slicer_3[1],SVC_slicer_3[2]]
# slicer_radius = 30
# slicer_height = 1
# mask_plane_creator_alternative(path2points+'/seg_s2a.nrrd',origin,spacings,slicer_points,'SVC_slicer',slicer_radius=slicer_radius,slicer_height=slicer_height,segPath=path2points,scriptsPath=scriptsPath)

# IVC_slicer_1 = points_data['IVC_slicer_1']
# IVC_slicer_2 = points_data['IVC_slicer_2']
# IVC_slicer_3 = points_data['IVC_slicer_3']
# slicer_points = [IVC_slicer_1[0],IVC_slicer_1[1],IVC_slicer_1[2],IVC_slicer_2[0],IVC_slicer_2[1],IVC_slicer_2[2],IVC_slicer_3[0],IVC_slicer_3[1],IVC_slicer_3[2]]
# slicer_radius = 30
# slicer_height = 1
# mask_plane_creator_alternative(path2points+'/seg_s2a.nrrd',origin,spacings,slicer_points,'IVC_slicer',slicer_radius=slicer_radius,slicer_height=slicer_height,segPath=path2points,scriptsPath=scriptsPath)

# ----------------------------------------------------------------------------------------------
# Give the paths to the SVC/IVC cylinders and the aorta/pulmonary artery slicers
# Give the associated labels
# ----------------------------------------------------------------------------------------------
aorta_slicer_nrrd = path2points+'/aorta_slicer.nrrd'
aorta_slicer_label = 0

PArt_slicer_nrrd = path2points+'/PArt_slicer.nrrd'
PArt_slicer_label = 0

SVC_slicer_nrrd = path2points+'/SVC_slicer.nrrd'
IVC_slicer_nrrd = path2points+'/IVC_slicer.nrrd'

# ----------------------------------------------------------------------------------------------
# Convert all of the segmentations to arrays
# ----------------------------------------------------------------------------------------------
aorta_slicer_array, header = nrrd.read(aorta_slicer_nrrd)
PArt_slicer_array, header = nrrd.read(PArt_slicer_nrrd)
SVC_slicer_array, header = nrrd.read(SVC_slicer_nrrd)
IVC_slicer_array, header = nrrd.read(IVC_slicer_nrrd)

# ----------------------------------------------------------------------------------------------------
# Read the segmentation with the right header
# --------------------------------------------------------------------------------------------
seg_array_good_header = sitk.ReadImage(path2points+'/seg_s2a.nrrd')

# ----------------------------------------------------------------------------------------------
# Remove protruding SVC/IVC and add the slicers
# ----------------------------------------------------------------------------------------------
print(' ## Removing any protruding SVC/IVC ## \n')
seg_s2b_array = connected_component_keep(path2points+'/seg_s2a.nrrd', SVC_seed, SVC_label,path2points)
seg_s2b_array = np.swapaxes(seg_s2b_array,0,2)
# save_itk(seg_s2b_array, origin, spacings, path2points+'/seg_s2b.nrrd')
save_itk_keeping_header(new_image=seg_s2b_array, original_image=seg_array_good_header, filename=path2points+'/seg_s2b.nrrd')
seg_s2c_array = connected_component_keep(path2points+'/seg_s2b.nrrd', IVC_seed, IVC_label,path2points)
seg_s2c_array = np.swapaxes(seg_s2c_array,0,2)
# save_itk(seg_s2c_array, origin, spacings, path2points+'/seg_s2c.nrrd')
save_itk_keeping_header(new_image=seg_s2c_array, original_image=seg_array_good_header, filename=path2points+'/seg_s2c.nrrd')


seg_s2c_array, header1 = nrrd.read(path2points+'/seg_s2c.nrrd')
seg_s2d_array = add_masks_replace_only(seg_s2c_array, aorta_slicer_array, aorta_slicer_label, Ao_BP_label)
seg_s2d_array = add_masks_replace_only(seg_s2d_array, PArt_slicer_array, PArt_slicer_label, PArt_BP_label)

new_RA_array = and_filter(seg_s2d_array,SVC_slicer_array,SVC_label,RA_BP_label)
seg_s2d_array = add_masks_replace_only(seg_s2d_array, new_RA_array, RA_BP_label, SVC_label)

new_RA_array = and_filter(seg_s2d_array,IVC_slicer_array,IVC_label,RA_BP_label)
seg_s2d_array = add_masks_replace_only(seg_s2d_array, new_RA_array, RA_BP_label, IVC_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## Formatting and saving the segmentation ##')
seg_s2d_array = np.swapaxes(seg_s2d_array,0,2)
# save_itk(seg_s2d_array, origin, spacings, path2points+'/seg_s2d.nrrd')
save_itk_keeping_header(new_image=seg_s2d_array, original_image=seg_array_good_header, filename=path2points+'/seg_s2d.nrrd')

print(" ## Saved segmentation with SVC/IVC added and aorta/pulmonary artery cropped ##")

# ----------------------------------------------------------------------------------------------
# Flattening base of SVC/IVC
# ----------------------------------------------------------------------------------------------
print(' ## Flattening base of SVC/IVC ## \n')
seg_s2e_array = connected_component(path2points+'/seg_s2d.nrrd', SVC_seed, SVC_label,path2points)
seg_s2e_array = add_masks_replace_only(seg_s2e_array,seg_s2e_array,RA_BP_label,SVC_label)
CC_array, header = nrrd.read(path2points+'/tmp/CC.nrrd')
seg_s2e_array = add_masks_replace(seg_s2e_array, CC_array, SVC_label)

seg_s2e_array = np.swapaxes(seg_s2e_array,0,2)
# save_itk(seg_s2e_array, origin, spacings, path2points+'/seg_s2e.nrrd')
save_itk_keeping_header(new_image=seg_s2e_array, original_image=seg_array_good_header, filename=path2points+'/seg_s2e.nrrd')


seg_s2f_array = connected_component(path2points+'/seg_s2e.nrrd', IVC_seed, IVC_label,path2points)
seg_s2f_array = add_masks_replace_only(seg_s2f_array,seg_s2f_array,RA_BP_label,IVC_label)
CC_array, header = nrrd.read(path2points+'/tmp/CC.nrrd')
seg_s2f_array = add_masks_replace(seg_s2f_array, CC_array, IVC_label)

seg_s2f_array = np.swapaxes(seg_s2f_array,0,2)
# save_itk(seg_s2f_array, origin, spacings, path2points+'/seg_s2f.nrrd')
save_itk_keeping_header(new_image=seg_s2f_array, original_image=seg_array_good_header, filename=path2points+'/seg_s2f.nrrd')
