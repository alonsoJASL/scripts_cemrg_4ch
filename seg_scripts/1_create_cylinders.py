#!/usr/bin/env python3
import nrrd
import numpy as np
import os
from img import *
import json
import argparse
import tqdm

parser = argparse.ArgumentParser(description='To run: python3 create_cylinders.py [path_to_points]')
parser.add_argument("path_to_points")
args = parser.parse_args()    


path2points = args.path_to_points

os.system("python3 txt_2_json.py "+path2points+"/origin_spacing.txt "+path2points+"/origin_spacing_labels.txt "+path2points+"/origin_spacing.json")

file = open(path2points+'/origin_spacing.json')
origin_data = json.load(file)
origin = origin_data["origin"]
spacing = origin_data["spacing"]

if not os.path.isfile(f"{path2points}/points.json"):
    print("points.json not found, looking for points.txt...")

    if not os.path.isfile(f"{path2points}/points.txt"):
        print("point.txt not found.\n")
        print("Reading world coordinates instead of voxel indices...")
        world_coord_json = json.load(open(f"{path2points}/physical_points.json"))

        points_voxels=[]

        def world_to_voxel(x,origin,spacing):
            sub=(np.array(x)-np.array(origin))
            res = [int(i) for i in np.divide(sub,spacing)]
            return res
        
        points_voxels.append(world_to_voxel(world_coord_json['SVC_1'],origin,spacing))
        points_voxels.append(world_to_voxel(world_coord_json['SVC_2'],origin,spacing))
        points_voxels.append(world_to_voxel(world_coord_json['SVC_3'],origin,spacing))
        points_voxels.append(world_to_voxel(world_coord_json['IVC_1'],origin,spacing))
        points_voxels.append(world_to_voxel(world_coord_json['IVC_2'],origin,spacing))
        points_voxels.append(world_to_voxel(world_coord_json['IVC_3'],origin,spacing))
        
        np.savetxt(f"{path2points}/points.txt",points_voxels,delimiter=' ')

    os.system("python3 txt_2_json.py "+path2points+"/points.txt "+path2points+"/labels.txt "+path2points+"/points.json")
else:
    print("Using points.json...")

np.savetxt(f"{path2points}/labels.txt",[['SVC_1'],['SVC_2'],['SVC_3'],['IVC_1'],['IVC_2'],['IVC_3']],delimiter=' ',fmt="%s")



def cylinder(seg_nrrd, points, plane_name, slicer_radius, slicer_height, origin, spacing):
    seg_array, header = nrrd.read(seg_nrrd)

    # Precompute values
    points_coords = origin + spacing * points
    cog = np.mean(points_coords, axis=0)

    v1 = points_coords[1] - points_coords[0]
    v2 = points_coords[2] - points_coords[0]
    v1 = v1 / np.linalg.norm(v1)
    v2 = v2 / np.linalg.norm(v2)
    n = np.cross(v1, v2)
    n = n / np.linalg.norm(n)

    p1 = cog - n * slicer_height / 2.
    p2 = cog + n * slicer_height / 2.

    n_z, n_x, n_y = seg_array.shape

    cube_size = max(slicer_height, slicer_radius) + 10 if slicer_height > slicer_radius else max(slicer_height, slicer_radius) + 30

    print("==========================================================")
    print("     Constraining the search to a small cube...")
    print("==========================================================")

    z_coords = origin[2] + spacing[2] * np.arange(n_z)
    z_cube_coord = np.where(np.abs(cog[2] - z_coords) <= cube_size / 2.)[0]

    y_coords = origin[1] + spacing[1] * np.arange(n_y)
    y_cube_coord = np.where(np.abs(cog[1] - y_coords) <= cube_size / 2.)[0]

    x_coords = origin[0] + spacing[0] * np.arange(n_x)
    x_cube_coord = np.where(np.abs(cog[0] - x_coords) <= cube_size / 2.)[0]

    print("============================================================================")
    print("Generating cylinder of height " + str(slicer_height) + " and radius " + str(slicer_radius) + "...")
    print("============================================================================")

    seg_array_cylinder = np.zeros(seg_array.shape, dtype=np.uint8)

    with tqdm.tqdm(total=len(x_cube_coord)) as pbar:
        for i in x_cube_coord:
            for j in y_cube_coord:
                for k in z_cube_coord:
                    test_pts = origin + spacing * np.array([i, j, k])
                    v1 = test_pts - p1
                    v2 = test_pts - p2
                    dot_v1 = np.dot(v1, n)
                    dot_v2 = np.dot(v2, n)
                    cross_norm = np.linalg.norm(np.cross(test_pts - p1, n / np.linalg.norm(n)))

                    if dot_v1 >= 0 and dot_v2 <= 0 and cross_norm <= slicer_radius:
                        seg_array_cylinder[i, j, k] += 1
		
            pbar.update(1)  # Update the progress bar

    seg_array_cylinder = np.swapaxes(seg_array_cylinder, 0, 2)

    print("Saving...")
    save_itk(seg_array_cylinder, origin, spacing, plane_name)


file = open(path2points+'/points.json')
points_data = json.load(file)



seg_name = path2points+"/seg_corrected.nrrd"

# SVC
pts1 = points_data['SVC_1']
pts2 = points_data['SVC_2']
pts3 = points_data['SVC_3']
points = np.row_stack((pts1,pts2,pts3))

slicer_radius_mm = 25
slicer_height_mm = 70

slicer_radius = int(np.ceil(np.min(spacing)*slicer_radius_mm))
slicer_height = int(np.ceil(np.min(spacing)*slicer_height_mm))

# slicer_radius = 10
# slicer_height = 30
cylinder(seg_name,points,path2points+"/SVC.nrrd",slicer_radius, slicer_height,origin,spacing)

# IVC
pts1 = points_data['IVC_1']
pts2 = points_data['IVC_2']
pts3 = points_data['IVC_3']
points = np.row_stack((pts1,pts2,pts3))

slicer_radius_mm = 25
slicer_height_mm = 70

slicer_radius = int(np.ceil(np.min(spacing)*slicer_radius_mm))
slicer_height = int(np.ceil(np.min(spacing)*slicer_height_mm))

# slicer_radius = 10
# slicer_height = 30
cylinder(seg_name,points,path2points+"/IVC.nrrd",slicer_radius, slicer_height,origin,spacing)

"""
# Aorta slicer
pts1 = points_data['Ao_1']
pts2 = points_data['Ao_2']
pts3 = points_data['Ao_3']
points = np.row_stack((pts1,pts2,pts3))

slicer_radius_mm = 70
slicer_height_mm = 10

slicer_radius = int(np.ceil(np.min(spacing)*slicer_radius_mm))
slicer_height = int(np.ceil(np.min(spacing)*slicer_height_mm))

# slicer_radius = 30
# slicer_height = 5
cylinder(seg_name,points,path2points+"/aorta_slicer.nrrd",slicer_radius, slicer_height,origin,spacing)

# PArt slicer
pts1 = points_data['PArt_1']
pts2 = points_data['PArt_2']
pts3 = points_data['PArt_3']
points = np.row_stack((pts1,pts2,pts3))

slicer_radius_mm = 100
slicer_height_mm = 10

slicer_radius = int(np.ceil(np.min(spacing)*slicer_radius_mm))
slicer_height = int(np.ceil(np.min(spacing)*slicer_height_mm))

# slicer_radius = 30
# slicer_height = 5
cylinder(seg_name,points,path2points+"/PArt_slicer.nrrd",slicer_radius, slicer_height,origin,spacing)

print("Note: the positions of the slicers are not reliable at this stage. Continue with the pipeline.")
"""