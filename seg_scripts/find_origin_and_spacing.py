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

from seg_scripts.common import configure_logging
logger = configure_logging(log_name=__name__)

from process_handler import get_origin_and_spacing
def main(args):
	"""
	Find origin and spacing of the file. 
	Needs a segmentation for spacing and dicom for origin.

	USAGE:
	python3 find_origin_and_spacing.py [path_to_points] [--seg-name [seg_name]] [--dicom-dir [dicom_dir]] [--output-file [output_file]]
	
	"""
	path2points=args.path_to_points
	seg_name="seg_corrected.nrrd"
	dicom_dir=args.dicom_dir
	output_file=args.output_file

	get_origin_and_spacing(path2points, seg_name, dicom_dir, output_file)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='To run: python3 find_origin_and_spacing.py [path_to_points]', 
								  usage=main.__doc__)
	parser.add_argument("path_to_points")
	parser.add_argument("--seg-name", "-seg-name", type=str, default="seg_corrected.nrrd")
	parser.add_argument("--dicom-dir", "-dicom-dir", type=str, default="ct")
	parser.add_argument("--output-file", "-output-file", type=str, default="")
	args = parser.parse_args()
	main(args)