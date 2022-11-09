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
import pydicom as dicom

parser = argparse.ArgumentParser(description='To run: python3 find_origin_and_spacing.py [path_to_points]')
parser.add_argument("path_to_points")
args = parser.parse_args()
path2points=args.path_to_points
seg_nrrd = path2points+'/seg_corrected.nrrd'
ct_image = path2points+'/Prospective 0.6mm Best Diastolic 76 % - 4/IM-0001-0314-0001.dcm'

# specify your image path
ds = dicom.dcmread(ct_image)
image_origin = np.array(ds[0x0020, 0x0032].value,dtype=float)
print(image_origin)


seg_array, header = nrrd.read(seg_nrrd)
# imgMin = header['axis mins']
imgSpa = header['spacings']
# imgSiz = header['sizes']
print(imgSpa)
# print(str(imgMin))