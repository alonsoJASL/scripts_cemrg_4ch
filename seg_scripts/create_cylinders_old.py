import os
import subprocess
import time
import json
import string
import argparse

from seg_scripts.img import *
import SimpleITK as sitk

import numpy as np
import nrrd
import pylab

parser = argparse.ArgumentParser(description='To run: python3 create_cylinders.py [path_to_points]')
parser.add_argument("path_to_points")
args = parser.parse_args()

path2points = args.path_to_points
scriptsPath = "/data/Dropbox/scripts_cemrgapp/seg_scripts/"

os.system("python3 txt_2_json.py "+path2points+"/origin_spacing.txt "+path2points+"/origin_spacing_labels.txt "+path2points+"/origin_spacing.json")

os.system("python3 txt_2_json.py "+path2points+"/points.txt "+path2points+"/labels.txt "+path2points+"/points.json")

seg_corrected_nrrd = path2points+'/seg_corrected.nrrd'

file = open(path2points+'/points.json')
points_data = json.load(file)

# SVC
SVC_1 = points_data['SVC_1']
SVC_2 = points_data['SVC_2']
SVC_3 = points_data['SVC_3']

slicer_points = [SVC_1[0],SVC_1[1],SVC_1[2],SVC_2[0],SVC_2[1],SVC_2[2],SVC_3[0],SVC_3[1],SVC_3[2]]
slicer_radius = 10
slicer_height = 120
mask_plane_creator(seg_corrected_nrrd,slicer_points,'SVC',slicer_radius=slicer_radius,slicer_height=slicer_height,segPath=path2points,scriptsPath=scriptsPath)

# IVC
IVC_1 = points_data['IVC_1']
IVC_2 = points_data['IVC_2']
IVC_3 = points_data['IVC_3']
slicer_points = [IVC_1[0],IVC_1[1],IVC_1[2],IVC_2[0],IVC_2[1],IVC_2[2],IVC_3[0],IVC_3[1],IVC_3[2]]
slicer_radius = 10
slicer_height = 100
mask_plane_creator(seg_corrected_nrrd,slicer_points,'IVC',slicer_radius=slicer_radius,slicer_height=slicer_height,segPath=path2points,scriptsPath=scriptsPath)

aorta_1 = points_data['Ao_1']
aorta_2 = points_data['Ao_2']
aorta_3 = points_data['Ao_3']
slicer_points = [aorta_1[0],aorta_1[1],aorta_1[2],aorta_2[0],aorta_2[1],aorta_2[2],aorta_3[0],aorta_3[1],aorta_3[2]]
slicer_radius = 30
slicer_height = 4
mask_plane_creator(seg_corrected_nrrd,slicer_points,'aorta_slicer',slicer_radius=slicer_radius,slicer_height=slicer_height,segPath=path2points,scriptsPath=scriptsPath)

PArt_1 = points_data['PArt_1']
PArt_2 = points_data['PArt_2']
PArt_3 = points_data['PArt_3']
slicer_points = [PArt_1[0],PArt_1[1],PArt_1[2],PArt_2[0],PArt_2[1],PArt_2[2],PArt_3[0],PArt_3[1],PArt_3[2]]
slicer_radius = 30
slicer_height = 2
mask_plane_creator(seg_corrected_nrrd,slicer_points,'PArt_slicer',slicer_radius=slicer_radius,slicer_height=slicer_height,segPath=path2points,scriptsPath=scriptsPath)
