#!/usr/bin/env python3
import nrrd
import copy
import numpy as np
import os
import SimpleITK as sitk
import string
import img
import subprocess
import time
import multiprocessing as mp
import json
import argparse

from txt_2_json import txt2json
from create_cylinders import cylinder

def main(args) : 
	path2points = args.path_to_points
	points_json = f'{os.path.join(path2points,"points.json")}'
	origin_spacing_json = f'{os.path.join(path2points,"origin_spacing.json")}'

	txt2json(os.path.join(path2points,"points.txt"), os.path.join(path2points,"labels.txt"), points_json)
	txt2json(os.path.join(path2points,"origin_spacing.txt"), os.path.join(path2points,"origin_spacing_labels.txt"), origin_spacing_json)

	with open(points_json) as f :
		points_data = json.load(f)

	with open(origin_spacing_json) as f :
		origin_data = json.load(f)

	origin = origin_data["origin"]
	spacing = origin_data["spacing"]

	seg_name = os.path.join(path2points, "seg_s2a.nrrd")

	# SVC slicer
	pts1 = points_data['SVC_slicer_1']
	pts2 = points_data['SVC_slicer_2']
	pts3 = points_data['SVC_slicer_3']
	points = np.row_stack((pts1,pts2,pts3))

	slicer_radius = 30
	slicer_height = 2
	cylinder(seg_name,points,path2points+"/SVC_slicer.nrrd",slicer_radius, slicer_height,origin,spacing)

	# IVC slicer
	pts1 = points_data['IVC_slicer_1']
	pts2 = points_data['IVC_slicer_2']
	pts3 = points_data['IVC_slicer_3']
	points = np.row_stack((pts1,pts2,pts3))

	slicer_radius = 30
	slicer_height = 2
	cylinder(seg_name,points,path2points+"/IVC_slicer.nrrd",slicer_radius, slicer_height,origin,spacing)

if __name__ == '__main__' :

	parser = argparse.ArgumentParser(description='To run: python3 create_cylinders.py [path_to_points]')
	parser.add_argument("path_to_points")
	args = parser.parse_args()
	main(args)
