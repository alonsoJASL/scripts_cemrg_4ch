import os
import subprocess
import time
import sys
import argparse
import json
import string
import nrrd
import pylab
import glob
import SimpleITK as sitk
import numpy as np
import pydicom as dicom

parser = argparse.ArgumentParser(description='To run: python3 find_origin_and_spacing.py [path_to_points]')
parser.add_argument("path_to_points")
args = parser.parse_args()
path2points=args.path_to_points
seg_nrrd = path2points+'/seg_corrected.nrrd'

dir_name = path2points+'ct/'
list_of_files = sorted(filter(os.path.isfile, glob.glob(dir_name + '*') ) )

ct_image = list_of_files[-1]

ds = dicom.dcmread(ct_image)
image_origin = np.array(ds[0x0020, 0x0032].value,dtype=float)
print(image_origin)


seg_array, header = nrrd.read(seg_nrrd)
imgSpa = header['spacings']
print(imgSpa)