import nrrd
import copy
import os
import numpy as np
import img

from common import configure_logging, big_print
logger = configure_logging(log_name=__name__)

import Labels

def cylinder(seg_nrrd,points,plane_name,slicer_radius, slicer_height,origin,spacing):
	
	logger.info(f"Generating cylinder: {plane_name}")	
	seg_array, _ = nrrd.read(seg_nrrd)

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

	big_print("     Constraining the search to a small cube...")

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

	big_print(f"Generating cylinder of height {slicer_height}, and radius {slicer_radius}... ")

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

	logger.info("Saving...")
	img.save_itk(seg_array_cylinder, origin, spacing, plane_name)
	
def create_and_save_svc_ivc(
        seg_file: str, 
        svc_file: str, 
        ivc_file: str, 
        # aorta_slicer_file: str, 
        # PArt_slicer_file: str, 
        output_file: str,
        origin_spacing_data: dict,
        labels: dict):
    seg_s2_array, _ = nrrd.read(seg_file)
    svc_array, _ = nrrd.read(svc_file)
    ivc_array, _ = nrrd.read(ivc_file)
    # aorta_slicer_array, _ = nrrd.read(aorta_slicer_file)
    # PArt_slicer_array, _ = nrrd.read(PArt_slicer_file)

    origin = origin_spacing_data['origin']
    spacings = origin_spacing_data['spacing']
    RPV1_label = labels['RPV1_label']
    SVC_label = labels['SVC_label']
    IVC_label = labels['IVC_label']
    
    # ----------------------------------------------------------------------------------------------
    # Add the SVC and IVC 
    # ----------------------------------------------------------------------------------------------
    logger.info('## Adding the SVC, IVC and slicers ##')
    seg_s2a_array = img.add_masks_replace_only(seg_s2_array, svc_array, SVC_label,RPV1_label)
    seg_s2a_array = img.add_masks(seg_s2a_array, ivc_array, IVC_label)
    
    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    logger.info(' ## Formatting and saving the segmentation ##')
    seg_s2a_array = np.swapaxes(seg_s2a_array,0,2)
    img.save_itk(seg_s2a_array, origin, spacings, output_file)
    logger.info(" ## Saved segmentation with SVC/IVC added ##")

def remove_protruding_vessel(path2points:str, seed, label, input_name, output_name, origin_spacing:dict) :
    
    origin = origin_spacing['origin']
    spacings = origin_spacing['spacing']
    input_file = os.path.join(path2points, input_name)
    output_file = os.path.join(path2points, output_name)
	
    logger.info(f' ## Removing any protruding {label} ## \n')
    seg_array = img.connected_component_keep(input_file, seed, label, path2points)
    seg_array = np.swapaxes(seg_array, 0, 2)
    img.save_itk(seg_array, origin, spacings, output_file)

def add_vessel_masks(seg_filename, output_filename, aorta_pair:tuple, PArt_pair:tuple, SVC_filename, IVC_filename, origin_spacing_data:dict, C:Labels):
    origin = origin_spacing_data['origin']
    spacings = origin_spacing_data['spacing']
	
    # Load the segmentation and vessel slicer arrays
    input_seg_array, _ = nrrd.read(seg_filename)
    aorta_slicer_array, _ = nrrd.read(aorta_pair[0])
    PArt_slicer_array, _ = nrrd.read(PArt_pair[0])
    SVC_slicer_array, _ = nrrd.read(SVC_filename)
    IVC_slicer_array, _ = nrrd.read(IVC_filename)

    # Add masks for the aorta and pulmonary artery
    seg_array = img.add_masks_replace_only(input_seg_array, aorta_slicer_array, aorta_pair[1], C.Ao_BP_label)
    seg_array = img.add_masks_replace_only(seg_array, PArt_slicer_array, PArt_pair[1], C.PArt_BP_label)

    # Replace the RA label with the SVC or IVC label
    new_RA_array = img.and_filter(seg_array, SVC_slicer_array, C.SVC_label, C.RA_BP_label)
    seg_array = img.add_masks_replace_only(seg_array, new_RA_array, C.RA_BP_label, C.SVC_label)

    new_RA_array = img.and_filter(seg_array, IVC_slicer_array, C.IVC_label, C.RA_BP_label)
    seg_array = img.add_masks_replace_only(seg_array, new_RA_array, C.RA_BP_label, C.IVC_label)
	
    logger.info(' ## Formatting and saving the segmentation ##')
    seg_array = np.swapaxes(seg_array, 0, 2)
    img.save_itk(seg_array, origin, spacings, output_filename)
	
def flatten_vessel_base(input_name, output_name, seed, label, path2points, tmp_name:str, origin_spacing:dict, C:Labels):	
    input_filename = os.path.join(path2points, input_name)
    output_filename = os.path.join(path2points, output_name)
    tmp_dir = os.path.join(path2points, tmp_name)
	
    origin = origin_spacing['origin']
    spacings = origin_spacing['spacing']
	
    logger.info(f' ## Flattening base of {label} ## \n')
	
    seg_array = img.connected_component(input_filename, seed, label, path2points)
    seg_array = img.add_masks_replace_only(seg_array, seg_array, C.RA_BP_label, label)
    CC_array, header = nrrd.read(os.path.join(tmp_dir, 'CC.nrrd'))
	
    seg_array = img.add_masks_replace(seg_array, CC_array, label)
    seg_array = np.swapaxes(seg_array, 0, 2)
    img.save_itk(seg_array, origin, spacings, output_filename) 
	