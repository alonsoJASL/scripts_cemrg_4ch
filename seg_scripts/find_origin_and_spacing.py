import os
import subprocess
import time
import sys
import argparse
import json
import string
import nrrd
# import pylab
import glob
import SimpleITK as sitk
import numpy as np
import pydicom as dicom

parser = argparse.ArgumentParser(description='To run: python3 find_origin_and_spacing.py [path_to_points]')
parser.add_argument("path_to_points")
args = parser.parse_args()
path2points=args.path_to_points
seg_nrrd = path2points+'/seg_corrected.nrrd'

dir_name = path2points+'/ct/'
list_of_files = sorted(filter(os.path.isfile, glob.glob(dir_name + '*') ) )

ds = dicom.dcmread(list_of_files[0])
image_origin_option_A = np.array(ds[0x0020, 0x0032].value,dtype=float)
ds = dicom.dcmread(list_of_files[-1])
image_origin_option_B = np.array(ds[0x0020, 0x0032].value,dtype=float)

if image_origin_option_A[2] < image_origin_option_B[2]:
	image_origin = image_origin_option_A
else:
	image_origin = image_origin_option_B

print(image_origin)


seg_array, header = nrrd.read(seg_nrrd)

try:
	imgSpa = header['spacings']
	print(imgSpa)
except Exception:
	imgSpa = header['space directions']
	imgSpa = [imgSpa[0,0],imgSpa[1,1],imgSpa[2,2]]
	print(imgSpa)