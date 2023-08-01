from img import *
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import json
import argparse
import os

parser = argparse.ArgumentParser(description='To run: python3 add_extra_veins_to_seg.py [path_to_points]')
parser.add_argument("path_to_points")
args = parser.parse_args()
path2points = args.path_to_points

points_file = open(path2points+'/vein_points.json')
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
# Give the path to the segmentation (with pulmonary veins separated)
# ----------------------------------------------------------------------------------------------
seg_corrected_nrrd = path2points+'/seg_corrected.nrrd'

# seg_array, header = nrrd.read(seg_corrected_nrrd)

# We read the image with Simple ITK so we don't lose the header information.
seg_array = sitk.ReadImage(seg_corrected_nrrd)

# ----------------------------------------------------------------------------------------------
# Give the paths to the SVC/IVC cylinders and the aorta/pulmonary artery slicers
# Give the associated labels
# ----------------------------------------------------------------------------------------------
LSPV_nrrd = path2points+'/LSPV.nrrd'
LIPV_nrrd = path2points+'/LIPV.nrrd'
RSPV_nrrd = path2points+'/RSPV.nrrd'
RIPV_nrrd = path2points+'/RIPV.nrrd'
LAA_nrrd = path2points+'/LAA.nrrd'

# ----------------------------------------------------------------------------------------------
# Convert all of the segmentations to arrays
# ----------------------------------------------------------------------------------------------
seg_corrected_array, header1 = nrrd.read(seg_corrected_nrrd)
LSPV_array, header2 = nrrd.read(LSPV_nrrd)
LIPV_array, header3 = nrrd.read(LIPV_nrrd)
RSPV_array, header4 = nrrd.read(RSPV_nrrd)
RIPV_array, header5 = nrrd.read(RIPV_nrrd)
LAA_array, header6 = nrrd.read(LAA_nrrd)


# ----------------------------------------------------------------------------------------------
# Add the SVC and IVC 
# ----------------------------------------------------------------------------------------------
print('\n ## Adding the extra veins ## \n')
# seg_corrected_array = add_masks(seg_corrected_array, LSPV_array, LPV1_label)
seg_corrected_array = add_masks(seg_corrected_array, LIPV_array, LPV2_label)
# seg_corrected_array = add_masks(seg_corrected_array, RSPV_array, RPV1_label)
# seg_corrected_array = add_masks(seg_corrected_array, RIPV_array, RPV2_label)
# seg_corrected_array = add_masks(seg_corrected_array, LAA_array, LAA_label)


# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## Formatting and saving the segmentation ##')
seg_corrected_array = np.swapaxes(seg_corrected_array,0,2)
# save_itk(seg_corrected_array, origin, spacings, path2points+'/seg_corrected.nrrd')
save_itk_keeping_header(new_image = seg_corrected_array, original_image=seg_array, filename=path2points+'/seg_corrected.nrrd')
print(" ## Saved segmentation with extra veins added ##")
