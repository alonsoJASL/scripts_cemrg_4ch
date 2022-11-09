import os
import subprocess
import time
import sys
import argparse
import json
import string
import SimpleITK as sitk
import numpy as np
import nrrd
import pylab


from img import save_itk
import SimpleITK as sitk

parser = argparse.ArgumentParser(description='To run: python3 nrrd_change_origin.py [path_to_nrrd]')
parser.add_argument("path")
args = parser.parse_args()

path=args.path

os.system("python3 txt_2_json.py "+path+"/origin_spacing.txt "+path+"/origin_spacing_labels.txt "+path+"/origin_spacing.json")

origin_spacing_file = open(path+'/origin_spacing.json')
origin_spacing_data = json.load(origin_spacing_file)
origin = origin_spacing_data['origin']
spacings = origin_spacing_data['spacing']

seg_nrrd = path+'/dcm-0_label_maps.nrrd'
seg_array, header1 = nrrd.read(seg_nrrd)

seg_array = np.swapaxes(seg_array,0,2)
save_itk(seg_array, origin, spacings, path+'/seg_shift.nrrd')