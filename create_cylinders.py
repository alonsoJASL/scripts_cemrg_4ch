import os
import subprocess
import time
import json
import string

from img import add_masks
from img import save_itk
import SimpleITK as sitk

import numpy as np
import nrrd
import pylab

segPath = "/data/Dropbox/henry/segmentations/"
scriptsPath = "/data/Dropbox/henry/segmentations/seg_scripts/"

seg_corrected_nrrd = segPath+'/seg_corrected.nrrd'

def mask_plane_creator(points,plane_name,slicer_radius = None, slicer_height = None):
	
	seg_corrected_array, header1 = nrrd.read(seg_corrected_nrrd)
	imgMin = header1['axis mins']
	imgSpa = header1['spacings']
	imgSiz = header1['sizes']
	imgDim = str(len(imgSiz))
	tmpPara = subprocess.check_output(['python',scriptsPath+'/postSlicer_optimised.py',\
		str(points[0]),str(points[1]),str(points[2]),\
		str(points[3]),str(points[4]),str(points[5]),\
		str(points[6]),str(points[7]),str(points[8]),\
		str(imgSiz[0]),str(imgSiz[1]),str(imgSiz[2]),\
		str(imgSpa[0]),str(imgSpa[1]),str(imgSpa[2]),\
		str(imgMin[0]),str(imgMin[1]),str(imgMin[2]),\
		plane_name,segPath,str(slicer_height),str(slicer_radius)])


path2points = '/data/Dropbox/henry/segmentations/'
file = open(path2points+'/points.json')
data = json.load(file)

# SVC
SVC_1 = data['SVC_1']
SVC_2 = data['SVC_2']
SVC_3 = data['SVC_3']

print(SVC_1)
print(SVC_2)
print(SVC_3)

slicer_points = [SVC_1[0],SVC_1[1],SVC_1[2],SVC_2[0],SVC_2[1],SVC_2[2],SVC_3[0],SVC_3[1],SVC_3[2]]
slicer_radius = 10
slicer_height = 120
mask_plane_creator(slicer_points,'SVC',slicer_radius=slicer_radius,slicer_height=slicer_height)

# IVC
IVC_1 = data['IVC_1']
IVC_2 = data['IVC_2']
IVC_3 = data['IVC_3']
slicer_points = [IVC_1[0],IVC_1[1],IVC_1[2],IVC_2[0],IVC_2[1],IVC_2[2],IVC_3[0],IVC_3[1],IVC_3[2]]
slicer_radius = 10
slicer_height = 30
mask_plane_creator(slicer_points,'IVC',slicer_radius=slicer_radius,slicer_height=slicer_height)


# file = open(path2points+'/aorta_PArt_points.json')
# data = json.load(file)

# aorta_1 = data['aorta_1']
# aorta_2 = data['aorta_2']
# aorta_3 = data['aorta_3']
# slicer_points = [aorta_1[0],aorta_1[1],aorta_1[2],aorta_2[0],aorta_2[1],aorta_2[2],aorta_3[0],aorta_3[1],aorta_3[2]]
# slicer_radius = 30
# slicer_height = 4
# mask_plane_creator(slicer_points,'aorta_slicer',slicer_radius=slicer_radius,slicer_height=slicer_height)

# PArt_1 = data['PArt_1']
# PArt_2 = data['PArt_2']
# PArt_3 = data['PArt_3']
# slicer_points = [PArt_1[0],PArt_1[1],PArt_1[2],PArt_2[0],PArt_2[1],PArt_2[2],PArt_3[0],PArt_3[1],PArt_3[2]]
# slicer_radius = 30
# slicer_height = 4
# mask_plane_creator(slicer_points,'PArt_slicer',slicer_radius=slicer_radius,slicer_height=slicer_height)
