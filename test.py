import os
import subprocess
import time
import json
import string

from img import add_masks
from img import add_masks_replace
from img import save_itk
import SimpleITK as sitk

import numpy as np
import nrrd
import pylab

# ----------------------------------------------------------------------------------------------
# Load all of the saved seeds and the origin and spacing saved previous
# ----------------------------------------------------------------------------------------------
# NOTE - We save the origin and spacings because the "save_itk" function used in
# the next step makes the format of the header difficult to work with.
# ----------------------------------------------------------------------------------------------
path2points = '/data/Dropbox/henry/segmentations/'
points_file = open(path2points+'/points.json')
points_data = json.load(points_file)

origin_spacing_file = open(path2points+'/origin_spacing.json')
origin_spacing_data = json.load(origin_spacing_file)

# Prepare relevant seeds
Ao_tip_seed = points_data['Ao_tip']
origin = origin_spacing_data['origin']
spacings = origin_spacing_data['spacing']

# ----------------------------------------------------------------------------------------------
# Load up the segmentation (with SVC, IVC, aorta and PArt) and read the image in sitk format
# ----------------------------------------------------------------------------------------------
seg_s2_nrrd = '/data/Dropbox/henry/segmentations/seg_s2.nrrd'
img1 = sitk.ReadImage(seg_s2_nrrd)

# ----------------------------------------------------------------------------------------------
# Find all voxel connected to the aorta tip and assign them a new mask value (100+6)
# ----------------------------------------------------------------------------------------------
aorta_tip = sitk.ConnectedThreshold(img1, seedList=[(int(Ao_tip_seed[0]),int(Ao_tip_seed[1]),int(Ao_tip_seed[2]))], lower=6, upper=6, replaceValue = 106)
print("ConnectedThreshold done")

# ----------------------------------------------------------------------------------------------
# Save the separated aorta tip as a mask
sitk.WriteImage(aorta_tip,'/data/Dropbox/henry/segmentations/aorta_tip.nrrd',True)
# ----------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------
# Read in the segmentation and aorta tip (nrrd files) as arrays
# ----------------------------------------------------------------------------------------------
aorta_tip_nrrd = '/data/Dropbox/henry/segmentations/aorta_tip.nrrd'
seg_s2_array, header1 = nrrd.read(seg_s2_nrrd)
aorta_tip_array, header2 = nrrd.read(aorta_tip_nrrd)

# ----------------------------------------------------------------------------------------------
# Remove the aorta tip from the segmentation (by replacing all voxels with 0)
# ----------------------------------------------------------------------------------------------
seg_s2b = add_masks_replace(seg_s2_array, aorta_tip_array, 0)
print("add_masks_replace done")

# ----------------------------------------------------------------------------------------------
# Format and save the new segmentation
# ----------------------------------------------------------------------------------------------
seg_s2b = np.swapaxes(seg_s2b,0,2)
print("swapaxes done")

save_itk(seg_s2b, origin, spacings, '/data/Dropbox/henry/segmentations/seg_s2b.nrrd')
print("Saved segmentation with aorta tip removed")
