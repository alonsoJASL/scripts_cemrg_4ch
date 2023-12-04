#!/usr/bin/env python3
import nrrd
import copy
import numpy as np
import os
import SimpleITK as sitk
import string
from seg_scripts.img import *
import subprocess
import time
import multiprocessing as mp
import json
import argparse

parser = argparse.ArgumentParser(description='To run: python3 pad.py [path_to_points]')
parser.add_argument("path_to_points")
args = parser.parse_args()


path2points = args.path_to_points
os.system("python3 txt_2_json.py "+path2points+"/points.txt "+path2points+"/labels.txt "+path2points+"/points.json")
os.system("python3 txt_2_json.py "+path2points+"/origin_spacing.txt "+path2points+"/origin_spacing_labels.txt "+path2points+"/origin_spacing.json")

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
# Pad the image with zeros
# ----------------------------------------------------------------------------------------------
seg_corrected_array, header = nrrd.read(path2points+'/seg_corrected.nrrd')
print(seg_corrected_array.shape)
seg_corrected_array = pad_image(seg_corrected_array)
print(seg_corrected_array.shape)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
print(' ## Pad image: Formatting and saving the segmentation ## \n')
seg_corrected_array = np.swapaxes(seg_corrected_array,0,2)
save_itk(seg_corrected_array, origin, spacings, path2points+'/seg_corrected.nrrd')
print(" ## Pad image: Saved segmentation padding added ## \n")
