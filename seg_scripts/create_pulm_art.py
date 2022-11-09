# BEWARE - copying point and label templates 
# from /data/Dropbox/etc so change if appropriate
scriptsPath = "/data/Dropbox/scripts_cemrgapp/seg_scripts/"

from img import mask_plane_creator
from img import mask_plane_creator_alternative
from img import add_masks
from img import add_masks_replace

from img import add_masks_replace_only
from img import save_itk
from img import connected_component
from img import connected_component_keep
from img import remove_filter
import SimpleITK as sitk

import numpy as np
import nrrd
import pylab
import json
import argparse
import os

parser = argparse.ArgumentParser(description='To run: python3 create_pulm_art.py [path_to_seg]')
parser.add_argument("path_to_seg")
args = parser.parse_args()
path2seg = args.path_to_seg

os.system("python3 txt_2_json.py "+path2seg+"/pulm_art_points.txt "+path2seg+"/pulm_art_labels.txt "+path2seg+"/pulm_art_points.json")

pulm_art_points_file = open(path2seg+'/pulm_art_points.json')
pulm_art_points_data = json.load(pulm_art_points_file)

# ----------------------------------------------------------------------------------------------
# Find the origin and spacing
# ----------------------------------------------------------------------------------------------
# NOTE - We save the origin and spacings because the "save_itk" function used in
# the next step makes the format of the header difficult to work with.
# ----------------------------------------------------------------------------------------------
origin_spacing_file = open(path2seg+'/origin_spacing.json')
origin_spacing_data = json.load(origin_spacing_file)
origin = origin_spacing_data['origin']
spacings = origin_spacing_data['spacing']

# ----------------------------------------------------------------------------------------------
# Create a cylinder for the pulmonary artery
# ----------------------------------------------------------------------------------------------
PArt_1 = pulm_art_points_data['PArt_1']
PArt_2 = pulm_art_points_data['PArt_2']
PArt_3 = pulm_art_points_data['PArt_3']

slicer_points = [PArt_1[0],PArt_1[1],PArt_1[2],PArt_2[0],PArt_2[1],PArt_2[2],PArt_3[0],PArt_3[1],PArt_3[2]]
slicer_radius = 40
slicer_height = 2
mask_plane_creator_alternative(path2seg+'/seg_shift.nrrd',origin,spacings,slicer_points,'PArt',slicer_radius=slicer_radius,slicer_height=slicer_height,segPath=path2seg,scriptsPath=scriptsPath)

# ----------------------------------------------------------------------------------------------
# Give the path to the PArt cylinder
# Give the associated labels
# ----------------------------------------------------------------------------------------------
PArt_nrrd = path2seg+'/PArt.nrrd'
PArt_label = 7
RV_label = 3

# ----------------------------------------------------------------------------------------------
# Convert all of the segmentations to arrays
# ----------------------------------------------------------------------------------------------
seg_shift_array, header1 = nrrd.read(path2seg+'/seg_shift.nrrd')
PArt_array, header2 = nrrd.read(PArt_nrrd)

# ----------------------------------------------------------------------------------------------
# Add the SVC and IVC 
# ----------------------------------------------------------------------------------------------
print('\n ## Adding the PArt cylinder ## \n')
seg_array = add_masks_replace_only(seg_shift_array, PArt_array, PArt_label,RV_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## Formatting and saving the segmentation ##')
seg_array = np.swapaxes(seg_array,0,2)
save_itk(seg_array, origin, spacings, path2seg+'/seg.nrrd')
print(" ## Saved segmentation with pulmonary artery corrected added ##")
