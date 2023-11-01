import nrrd
import numpy as np
import copy
import os
import SimpleITK as sitk
import img
from img import MaskOperationMode as MM

from common import configure_logging, big_print, make_tmp
logger = configure_logging(log_name=__name__)

import Labels
class FourChamberProcess:
    def __init__(self, path2points: str, origin_spacing: dict, CONSTANTS:Labels):
        self._path2points = path2points
        self._origin_spacing = origin_spacing
        self.CONSTANTS = CONSTANTS

    @property 
    def path2points(self):
        return self._path2points
    
    def DIR(self, x):
        return os.path.join(self.path2points, x)
    
    def TMP(self, x):
        return os.path.join(self.path2points, "tmp", x)
    
    def make_tmp(self, x):
        return make_tmp(self.path2points, x)

    def get_origin_spacing(self):
        origin = self._origin_spacing["origin"]
        spacing = self._origin_spacing["spacing"]
        return origin, spacing
    
    def check_nrrd(self, filename) -> bool: 
        """
        Checks if a file.nrrd exists in the path2points directory, and if not, 
        checks if the .nii version exists and converts it to nrrd.
        """
        if not os.path.exists(self.DIR(filename)):
            logger.info(f'{filename} file does not exist. Attempting using .nii')
            filename_nii = filename.replace('.nrrd','.nii')
            if os.path.exists(self.DIR(filename_nii)):
                logger.info(f'{filename_nii} file exists. Converting to .nrrd')
                img.convert_nii_nrrd(self.path2points, filename_nii)

        return os.path.exists(self.DIR(filename))

    def get_distance_map_dictionaries(self, dist_label, dmap_name, th_label, th_name) :
        CDIC = self.CONSTANTS.get_dictionary()
        ld = {'distance_map': CDIC[dist_label], 'threshold':  CDIC[th_label]}
        td = {'distance_map': dmap_name, 'threshold': th_name}
        return ld, td
    
    def get_distance_map_tuples(self, mom1:MM, label1, arr1, mom2:MM, label2, arr2) : 
        return [ (mom1, label1, arr1),  (mom2, label2, arr2) ]


	
    def cylinder(self, segname, points, plane_name, slicer_radius, slicer_height):
        logger.info(f"Generating cylinder: {plane_name}")
        origin, spacing = self.get_origin_spacing()
        seg_array, _ = nrrd.read(self.DIR(segname))

        seg_array_cylinder = np.zeros(seg_array.shape, np.uint8)

        points_coords = np.copy(points)
        for i, pts in enumerate(points):
            points_coords[i, :] = origin + spacing * points[i, :]

        cog = np.mean(points_coords, axis=0)

        v1 = points_coords[1, :] - points_coords[0, :]
        v2 = points_coords[2, :] - points_coords[0, :]
        v1 = v1 / np.linalg.norm(v1)
        v2 = v2 / np.linalg.norm(v2)
        n = np.cross(v1, v2)
        n = n / np.linalg.norm(n)

        p1 = cog - n * slicer_height / 2.
        p2 = cog + n * slicer_height / 2.
        n = p2 - p1

        n_z = seg_array.shape[2]
        n_x = seg_array.shape[0]
        n_y = seg_array.shape[1]

        if slicer_height > slicer_radius:
            cube_size = max(slicer_height, slicer_radius) + 10
        else:
            cube_size = max(slicer_height, slicer_radius) + 30

        big_print("     Constraining the search to a small cube...")

        z_cube_coord = []
        count = 0
        for i in range(n_z):
            z = origin[2] + spacing[2] * i

            distance = np.abs(cog[2] - z)
            if distance <= cube_size / 2.:
                z_cube_coord.append(i)

        y_cube_coord = []
        for i in range(n_y):
            y = origin[1] + spacing[1] * i

            distance = np.abs(cog[1] - y)
            if distance <= cube_size / 2.:
                y_cube_coord.append(i)

        x_cube_coord = []
        for i in range(n_x):
            x = origin[0] + spacing[0] * i
            distance = np.abs(cog[0] - x)
            if distance <= cube_size / 2.:
                x_cube_coord.append(i)

        big_print(f"Generating cylinder of height {slicer_height}, and radius {slicer_radius}... ")

        x_grid, y_grid, z_grid = np.meshgrid(x_cube_coord, y_cube_coord, z_cube_coord, indexing='ij')
        test_pts = origin + spacing * np.array([x_grid, y_grid, z_grid])
        v1 = test_pts - p1
        v2 = test_pts - p2
        valid_indices = (np.dot(v1, n) >= 0) & (np.dot(v2, n) <= 0)
        test_radius = np.linalg.norm(np.cross(test_pts - p1, n / np.linalg.norm(n)), axis=-1)
        valid_radius = test_radius <= slicer_radius
        seg_array_cylinder[x_grid[valid_indices], y_grid[valid_indices], z_grid[valid_indices]] += valid_radius

        seg_array_cylinder = np.swapaxes(seg_array_cylinder, 0, 2)

        logger.info("Saving...")
        img.save_itk(seg_array_cylinder, origin, spacing, plane_name)
    
    def create_and_save_svc_ivc(self, seg_name: str, svc_name: str, ivc_name: str, output_name: str):

        origin, spacings = self.get_origin_spacing()
        C=self.CONSTANTS

        seg_file = self.DIR(seg_name)
        svc_file = self.DIR(svc_name)
        ivc_file = self.DIR(ivc_name)
        # aorta_slicer_file = self.DIR(aorta_slicer_name)
        # PArt_slicer_file = self.DIR(PArt_slicer_name)
        output_file = self.DIR(output_name)

        seg_s2_array, _ = nrrd.read(seg_file)
        svc_array, _ = nrrd.read(svc_file)
        ivc_array, _ = nrrd.read(ivc_file)
        # aorta_slicer_array, _ = nrrd.read(aorta_slicer_file)
        # PArt_slicer_array, _ = nrrd.read(PArt_slicer_file)

        # ----------------------------------------------------------------------------------------------
        # Add the SVC and IVC 
        # ----------------------------------------------------------------------------------------------
        logger.info('## Adding the SVC, IVC and slicers ##')
        seg_s2a_array = img.add_masks_replace_only(seg_s2_array, svc_array, C.SVC_label,C.RPV1_label)
        seg_s2a_array = img.add_masks(seg_s2a_array, ivc_array, C.IVC_label)

        # ----------------------------------------------------------------------------------------------
        # Format and save the segmentation
        # ----------------------------------------------------------------------------------------------
        logger.info(' ## Formatting and saving the segmentation ##')
        seg_s2a_array = np.swapaxes(seg_s2a_array,0,2)
        img.save_itk(seg_s2a_array, origin, spacings, output_file)
        logger.info(" ## Saved segmentation with SVC/IVC added ##")
    
    def remove_protruding_vessel(self, seed, label, input_name, output_name) :
    
        origin, spacings = self.get_origin_spacing()
        input_file = os.path.join(self.path2points, input_name)
        output_file = os.path.join(self.path2points, output_name)
    
        logger.info(f' ## Removing any protruding {label} ## \n')
        seg_array = img.connected_component_keep(input_file, seed, label, self.path2points)
        seg_array = np.swapaxes(seg_array, 0, 2)
        img.save_itk(seg_array, origin, spacings, output_file)
    
    def add_vessel_masks(self, seg_name, output_name, aorta_pair:tuple, PArt_pair:tuple, SVC_name, IVC_name):
        origin, spacings = self.get_origin_spacing()
        C=self.CONSTANTS
        seg_filename = self.DIR(seg_name)
        output_filename = self.DIR(output_name)
        SVC_filename = self.DIR(SVC_name)
        IVC_filename = self.DIR(IVC_name)
    
        # Load the segmentation and vessel slicer arrays
        input_seg_array, _ = nrrd.read(seg_filename)
        aorta_slicer_array, _ = nrrd.read(self.DIR(aorta_pair[0]))
        PArt_slicer_array, _ = nrrd.read(self.DIR(PArt_pair[0]))
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
    
    def flatten_vessel_base(self, input_name, output_name, seed, label):
        """
        Flattens the base of a vessel in a segmentation array.

        Args:
            input_name (str): The name of the input file containing the segmentation array.
            output_name (str): The name of the output file to save the flattened segmentation array.
            seed (int): The seed value used for connected component analysis.
            label (int): The label value of the vessel to be flattened.

        Returns:
            None. Modifies the segmentation array and saves it as an ITK file.

        Example Usage:
            # Initialize the FourChamberProcess object
            four_chamber = FourChamberProcess(path2points, origin_spacing, CONSTANTS)

            # Call the flatten_vessel_base method
            four_chamber.flatten_vessel_base(input_name, output_name, seed, label)
        """
        input_filename = self.DIR(input_name)
        output_filename = self.DIR(output_name)

        origin, spacings = self.get_origin_spacing()
        C = self.CONSTANTS

        logger.info(f' ## Flattening base of {label} ## \n')

        seg_array = img.connected_component(input_filename, seed, label, self.path2points)
        seg_array = img.add_masks_replace_only(seg_array, seg_array, C.RA_BP_label, label)
        CC_array, header = nrrd.read(self.TMP('CC.nrrd'))

        seg_array = img.add_masks_replace(seg_array, CC_array, label)
        seg_array = np.swapaxes(seg_array, 0, 2)
        img.save_itk(seg_array, origin, spacings, output_filename)

    def dmap_and_threshold(self, input_name, labels:dict, tmp_dict:dict) -> dict: 
        """
        Creates a mask from a distance map and adds it to the segmentation. 
       
        tmp_dict contains the names of the distance map and the thresholded mask.
        tmp_dict = {
            'distance_map': 'LV_DistMap.nrrd',
            'threshold': 'LV_neck.nrrd'
        }       
        labels = { # get these from Labels.py
            'distance_map': Labels.LV_BP_label,
            'threshold': Labels.LV_neck_WT
        } 
        """
        
        dmap_name = tmp_dict['distance_map'][0]
        thresh_name = tmp_dict['threshold'][0]
    
        distance_map = img.distance_map(self.DIR(input_name), labels['distance_map'])
        sitk.WriteImage(distance_map,self.TMP(dmap_name),True)
    
        thresholded_mask = img.threshold_filter_nrrd(self.TMP(dmap_name),0,labels['threshold'])
        sitk.WriteImage(thresholded_mask,self.TMP(thresh_name),True)

        outputs_dic = {
            'distance_map': self.TMP(dmap_name),
            'threshold': self.TMP(thresh_name)
        }

        return outputs_dic


    def create_mask_from_distance_map(self, input_name, output_name, labels:dict, tmp_dict:dict, add_mask_list) : 
        """
        Creates a mask from a distance map and adds it to the segmentation. 
        The add_mask_list is a list of tuples with the following information: 
        For example: 
         [ 
        	(MaskOperationMode.REPLACE, newmask, forbid_changes_list ), 
        	(MaskOperationMode.NO_OVERRIDE, newmask, []) 
         ]      
        tmp_dict contains the names of the distance map and the thresholded mask.
        tmp_dict = {
            'distance_map': 'LV_DistMap.nrrd',
            'threshold': 'LV_neck.nrrd'
        }       
        labels = { # get these from Labels.py
            'distance_map': Labels.LV_BP_label,
            'threshold': Labels.LV_neck_WT
        } 
        """
        origin, spacings = self.get_origin_spacing()
        C=self.CONSTANTS

        files_dic = self.dmap_and_threshold(input_name, labels, tmp_dict)

        thresholded_array, _ = nrrd.read(files_dic['threshold'])
        input_array, _ = nrrd.read(self.DIR(input_name)) 

        mode, newmask, forbid_list = add_mask_list[0]
        thresholded_array = img.process_mask(thresholded_array, thresholded_array, newmask, mode, forbid_changes=forbid_list)

        mode, newmask, forbid_list = add_mask_list[1]
        output_array = img.process_mask(input_array, thresholded_array, newmask, mode, forbid_changes=forbid_list)

        if len(add_mask_list)>2:
            mode, newmask, forbid_list = add_mask_list[2]
            output_array = img.process_mask(output_array, thresholded_array, newmask, mode, forbid_changes=forbid_list)
    
        output_array = np.swapaxes(output_array, 0, 2)
        img.save_itk(output_array, origin, spacings, self.DIR(output_name))

    def push_in_and_save(self, input_name, pusher_wall_lab, pushed_wall_lab, pushed_BP_lab, pushed_WT, outname='')  :
        origin, spacings = self.get_origin_spacing()
        outname = input_name if outname=='' else outname

        seg_array = img.push_inside(self.path2points, self.DIR(input_name), pusher_wall_lab, pushed_wall_lab, pushed_BP_lab, pushed_WT) 
        seg_array = np.swapaxes(seg_array, 0, 2)
        img.save_itk(seg_array, origin, spacings, self.DIR(outname))

    def crop_major_vessels(self, input_name, slicer_tuple_list, output_name) :
        """
        Cropping veins
        slicer_tuple_list is a list of tuples that contain the following information:
            (slicer_name, MoM, newmask, forbid_changes_list)

        for example: 
        slicer_tuple_list = [
            ("aorta_slicer.nrrd", MaskOperationMode.REPLACE_ONLY, 0, [C.Ao_wall_label]),
            ("PArt_slicer.nrrd",  MaskOperationMode.REPLACE_ONLY, 0, [C.PArt_wall_label])
        ]
        
        """
        origin, spacings = self.get_origin_spacing()
        C=self.CONSTANTS

        seg_filename = self.DIR(input_name)
        output_filename = self.DIR(output_name)

        seg_array, _ = nrrd.read(seg_filename)

        for slicer_name, mode, newmask, forbid_list in slicer_tuple_list:
            slicer_array, _ = nrrd.read(self.DIR(slicer_name))
            seg_array = img.process_mask(seg_array, slicer_array, newmask, mode, forbid_changes=forbid_list)

        seg_array = np.swapaxes(seg_array, 0, 2)
        img.save_itk(seg_array, origin, spacings, output_filename)
    
    def get_connected_component_and_save(self, input_name, seed, layer, output_name) : 
        origin, spacings = self.get_origin_spacing()

        seg_array = img.connected_component(self.DIR(input_name), seed, layer, self.path2points)
        seg_array = np.swapaxes(seg_array, 0, 2)
        img.save_itk(seg_array, origin, spacings, self.DIR(output_name))