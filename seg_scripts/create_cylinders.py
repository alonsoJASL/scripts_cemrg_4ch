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

def cylinder(seg_nrrd,points,plane_name,slicer_radius, slicer_height,origin,spacing):
	
	seg_array, header = nrrd.read(seg_nrrd)

	# print(seg_array[:,:,0].shape)

	seg_array_cylinder = np.zeros(seg_array.shape,np.uint8)

	points_coords = copy.deepcopy(points)
	for i,pts in enumerate(points):
		points_coords[i,:] = origin+spacing*points[i,:]

	cog = np.mean(points_coords,axis=0)

	v1 = points_coords[1,:]-points_coords[0,:]
	v2 = points_coords[2,:]-points_coords[0,:]
	v1 = v1/np.linalg.norm(v1)
	v2 = v2/np.linalg.norm(v2)
	n = np.cross(v1,v2)
	n = n/np.linalg.norm(n)

	p1 = cog - n*slicer_height/2.	
	p2 = cog + n*slicer_height/2.
	n = p2-p1

	n_z = seg_array.shape[2]
	n_x = seg_array.shape[0]
	n_y = seg_array.shape[1]

	if slicer_height>slicer_radius:
		cube_size = max(slicer_height,slicer_radius)+10
	else:
		cube_size = max(slicer_height,slicer_radius)+30

	print("==========================================================")
	print("     Constraining the search to a small cube...")
	print("==========================================================")

	z_cube_coord = []
	count = 0
	for i in range(n_z):
		z = origin[2]+spacing[2]*i
			
		distance = np.abs(cog[2]-z)
		if distance<=cube_size/2.:
			z_cube_coord.append(i)

	y_cube_coord = []	
	for i in range(n_y):
		y = origin[1]+spacing[1]*i
			
		distance = np.abs(cog[1]-y)
		if distance<=cube_size/2.:
			y_cube_coord.append(i)

	x_cube_coord = []	
	for i in range(n_x):
		x = origin[0]+spacing[0]*i
			
		distance = np.abs(cog[0]-x)
		if distance<=cube_size/2.:
			x_cube_coord.append(i)

	print("============================================================================")
	print("Generating cylinder of height "+str(slicer_height)+" and radius "+str(slicer_radius)+"...")
	print("============================================================================")

	for i in x_cube_coord:
		for j in y_cube_coord:
			for k in z_cube_coord:

				test_pts = origin+spacing*np.array([i,j,k])

				v1 = test_pts-p1
				v2 = test_pts-p2
				if np.dot(v1,n)>=0 and np.dot(v2,n)<=0:
					test_radius = np.linalg.norm(np.cross(test_pts-p1,n/np.linalg.norm(n)))
					if test_radius<=slicer_radius:
						seg_array_cylinder[i,j,k] = seg_array_cylinder[i,j,k]+1

	seg_array_cylinder = np.swapaxes(seg_array_cylinder,0,2)

	print("Saving...")
	img.save_itk(seg_array_cylinder, origin, spacing, plane_name)

def main(args) : 
	path2points = args.path_to_points
	path2ptsjson = args.points_json
	path2originjson = args.origin_spacing_json

	if path2ptsjson == "" :
		points_file = f'{path2points}/points.txt'
		labels_file = f'{path2points}/labels.txt'
		points_output_file = f'{path2points}/points.json'
		txt2json(points_file, labels_file, points_output_file)
	else : 
		points_output_file = os.path.join(path2points, path2ptsjson)

	if path2originjson == "" :
		origin_spacing_file = f'{path2points}/origin_spacing.txt'
		origin_spacing_labels_file = f'{path2points}/origin_spacing_labels.txt'
		origin_spacing_output_file = f'{path2points}/origin_spacing.json'
		txt2json(origin_spacing_file, origin_spacing_labels_file, origin_spacing_output_file)
	else :
		origin_spacing_output_file = os.path.join(path2points, path2originjson)
	
	if not os.path.exists(points_output_file):
		print("ERROR: points.json file does not exist. Please run txt_2_json.py first.")
		return
	
	if not os.path.exists(origin_spacing_output_file):
		print("ERROR: origin_spacing.json file does not exist. Please run txt_2_json.py first.")
		return

	with open(points_output_file) as file:
		points_data = json.load(file)

	with open(origin_spacing_output_file) as file:
		origin_data = json.load(file)

	origin = origin_data["origin"]
	spacing = origin_data["spacing"]

	seg_name = f'{path2points}/seg_corrected.nrrd'
	if not os.path.exists(seg_name):
		print("seg_corrected.nrrd file does not exist. Attempting using .nii.")
		seg_name = f'{path2points}/seg_corrected.nii'

	# SVC
	pts1 = points_data['SVC_1']
	pts2 = points_data['SVC_2']
	pts3 = points_data['SVC_3']
	points = np.row_stack((pts1,pts2,pts3))

	slicer_radius = 10
	slicer_height = 30
	cylinder(seg_name,points,path2points+"/SVC.nrrd",slicer_radius, slicer_height,origin,spacing)

	# IVC
	pts1 = points_data['IVC_1']
	pts2 = points_data['IVC_2']
	pts3 = points_data['IVC_3']
	points = np.row_stack((pts1,pts2,pts3))

	slicer_radius = 10
	slicer_height = 30
	cylinder(seg_name,points,path2points+"/IVC.nrrd",slicer_radius, slicer_height,origin,spacing)

	# Aorta slicer
	pts1 = points_data['Ao_1']
	pts2 = points_data['Ao_2']
	pts3 = points_data['Ao_3']
	points = np.row_stack((pts1,pts2,pts3))

	slicer_radius = 30
	slicer_height = 2
	cylinder(seg_name,points,path2points+"/aorta_slicer.nrrd",slicer_radius, slicer_height,origin,spacing)

	# PArt slicer
	pts1 = points_data['PArt_1']
	pts2 = points_data['PArt_2']
	pts3 = points_data['PArt_3']
	points = np.row_stack((pts1,pts2,pts3))

	slicer_radius = 30
	slicer_height = 2
	cylinder(seg_name,points,path2points+"/PArt_slicer.nrrd",slicer_radius, slicer_height,origin,spacing)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='To run: python3 create_cylinders.py [path_to_points]')
	parser.add_argument("path_to_points")
	parser.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
	parser.add_argument("--origin-spacing-json", "-os", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")	
	args = parser.parse_args()
	
	main(args)