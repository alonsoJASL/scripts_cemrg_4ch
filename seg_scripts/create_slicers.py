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

from create_cylinders import cylinder
from common import parse_txt_to_json, get_json_data


def main(args) : 
	path2points = args.path_to_points
	path2ptsjson = args.points_json
	path2originjson = args.origin_spacing_json
	
	points_output_file = parse_txt_to_json(path2points, path2ptsjson, "points", "labels")
	points_data = get_json_data(points_output_file)

	origin_spacing_output_file = parse_txt_to_json(path2points, path2originjson, "origin_spacing", "origin_spacing_labels")
	origin_data = get_json_data(origin_spacing_output_file)

	origin = origin_data["origin"]
	spacing = origin_data["spacing"]

	DIR = lambda x: os.path.join(path2points, x)

	seg_name = DIR("seg_s2a.nrrd")

	# SVC slicer
	pts1 = points_data['SVC_slicer_1']
	pts2 = points_data['SVC_slicer_2']
	pts3 = points_data['SVC_slicer_3']
	points = np.row_stack((pts1,pts2,pts3))

	slicer_radius = 30
	slicer_height = 2
	cylinder(seg_name,points,DIR("SVC_slicer.nrrd"),slicer_radius, slicer_height,origin,spacing)

	# IVC slicer
	pts1 = points_data['IVC_slicer_1']
	pts2 = points_data['IVC_slicer_2']
	pts3 = points_data['IVC_slicer_3']
	points = np.row_stack((pts1,pts2,pts3))

	slicer_radius = 30
	slicer_height = 2
	cylinder(seg_name,points,DIR("IVC_slicer.nrrd"),slicer_radius, slicer_height,origin,spacing)

if __name__ == '__main__' :

	parser = argparse.ArgumentParser(description='To run: python3 create_cylinders.py [path_to_points]')
	parser.add_argument("path_to_points")
	parser.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
	parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
	args = parser.parse_args()
	main(args)
