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

from process_handler import create_slicers 

def main(args) : 
	path2points = args.path_to_points
	path2ptsjson = args.points_json
	path2originjson = args.origin_spacing_json
	seg_name = args.seg_name

	create_slicers(path2points, path2ptsjson, path2originjson, seg_name)

if __name__ == '__main__' :

	parser = argparse.ArgumentParser(description='To run: python3 create_cylinders.py [path_to_points]')
	parser.add_argument("path_to_points")
	parser.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
	parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
	parser.add_argument("--seg-name", "-seg-name", type=str, default="seg_s2a.nrrd")
	args = parser.parse_args()
	main(args)
