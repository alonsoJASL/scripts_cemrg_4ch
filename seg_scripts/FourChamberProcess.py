import nrrd
import numpy as np
import copy
import os
import SimpleITK as sitk
import seg_scripts.img as img
from seg_scripts.ImageAnalysis import MaskOperationMode as MM
from seg_scripts.ImageAnalysis import ImageAnalysis 

from seg_scripts.common import configure_logging, big_print, make_tmp

import seg_scripts.Labels as Labels

DISTANCE_MAP_KEY = 'distance_map'
THRESHOLD_KEY = 'threshold'
class FourChamberProcess:
    def __init__(self, path2points: str, origin_spacing: dict, CONSTANTS:Labels, debug=False):
        self._path2points = path2points
        self._origin_spacing = origin_spacing
        self._is_mri = False
        self.CONSTANTS = CONSTANTS
        self._debug = debug
        self._save_seg_steps = True
        self.swap_axes = True
        self.logger = configure_logging(log_name=__name__, is_debug=self._debug)
        
    @property 
    def path2points(self):
        return self._path2points
    
    @property
    def debug(self):
        return self._debug
    
    @debug.setter
    def debug(self, value:bool):
        self._debug = value

    @property
    def save_seg_steps(self):
        return self._save_seg_steps
    
    @save_seg_steps.setter
    def save_seg_steps(self, value:bool):
        self._save_seg_steps = value
    
    @property 
    def is_mri(self):
        return self._is_mri
    
    def DIR(self, x):
        return os.path.join(self.path2points, x)
    
    def TMP(self, x):
        return os.path.join(self.path2points, "tmp", x)
    
    def make_tmp(self):
        return make_tmp(self.path2points)

    def get_origin_spacing(self):
        origin = self._origin_spacing["origin"]
        spacing = self._origin_spacing["spacing"]
        return origin, spacing
    
    def get_dimensions(self) : 
        if "dimensions" in self._origin_spacing:
            return self._origin_spacing["dimensions"]
        else:
            return None
    
    def check_nrrd(self, filename) -> bool: 
        """
        Checks if a file.nrrd exists in the path2points directory, and if not, 
        checks if the .nii version exists and converts it to nrrd.
        """
        if not filename.endswith('.nrrd'):
            filename = filename + '.nrrd'

        if not os.path.exists(self.DIR(filename)):
            self.logger.info(f'{filename} file does not exist. Attempting using .nii')
            filename_nii = filename.replace('.nrrd','.nii')
            if os.path.exists(self.DIR(filename_nii)):
                self.logger.info(f'{filename_nii} file exists. Converting to .nrrd')
                img.convert_to_nrrd(self.path2points, filename_nii)

        return os.path.exists(self.DIR(filename))
    
    def cylinder_process(self, seg_array: np.array, points, plane_name, slicer_radius, slicer_height) -> np.array:
        origin, spacing = self.get_origin_spacing()
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

        return seg_array_cylinder
	
    def cylinder(self, segname, points, plane_name, slicer_radius, slicer_height):
        self.logger.info(f"Generating cylinder: {plane_name}")
        origin, spacing = self.get_origin_spacing()
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)

        seg_array = ima.load_image_array(self.DIR(segname))
        # seg_array, _ = nrrd.read(self.DIR(segname))
        seg_array_cylinder = self.cylinder_process(seg_array, points, plane_name, slicer_radius, slicer_height)

        self.logger.info("Saving...")
        # seg_array_cylinder = np.swapaxes(seg_array_cylinder, 0, 2)
        ima.save_itk(seg_array_cylinder, origin, spacing, plane_name, self.swap_axes)
    
    def create_and_save_svc_ivc(self, seg_name: str, svc_name: str, ivc_name: str, output_name: str):

        origin, spacings = self.get_origin_spacing()
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)
        C=self.CONSTANTS

        seg_s2_array = ima.load_image_array(self.DIR(seg_name))
        svc_array = ima.load_image_array(self.DIR(svc_name))
        ivc_array = ima.load_image_array(self.DIR(ivc_name))

        output_file = self.DIR(output_name)

        # ----------------------------------------------------------------------------------------------
        # Add the SVC and IVC 
        # ----------------------------------------------------------------------------------------------
        self.logger.info('## Adding the SVC, IVC and slicers ##')
        seg_s2a_array = img.add_masks_replace_only(seg_s2_array, svc_array, C.SVC_label,C.RPV1_label)
        seg_s2a_array = img.add_masks(seg_s2a_array, ivc_array, C.IVC_label)

        # ----------------------------------------------------------------------------------------------
        # Format and save the segmentation
        # ----------------------------------------------------------------------------------------------
        self.logger.info(' ## Formatting and saving the segmentation ##')
        ima.save_itk(seg_s2a_array, origin, spacings, output_file, self.swap_axes)

        self.logger.info(" ## Saved segmentation with SVC/IVC added ##")
    
    def remove_protruding_vessel(self, seed, label, input_name, output_name) :
    
        origin, spacings = self.get_origin_spacing()
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)

        input_array = ima.load_image_array(self.DIR(input_name))
        input_image = ima.array2itk(input_array, origin, spacings)
        self.logger.info(f' ## Removing any protruding {label} ## \n')
        seg_array = ima.connected_component_keep(input_image, seed, label)
        ima.save_itk(seg_array, origin, spacings, self.DIR(output_name), self.swap_axes)
    
    def add_vessel_masks(self, seg_name, output_name, aorta_pair:tuple, PArt_pair:tuple, SVC_name, IVC_name):
        origin, spacings = self.get_origin_spacing()
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)
        C=self.CONSTANTS
    
        # Load the segmentation and vessel slicer arrays
        input_seg_array = ima.load_image_array(self.DIR(seg_name))
        aorta_slicer_array = ima.load_image_array(self.DIR(aorta_pair[0]))
        PArt_slicer_array = ima.load_image_array(self.DIR(PArt_pair[0]))
        SVC_slicer_array = ima.load_image_array(self.DIR(SVC_name))
        IVC_slicer_array = ima.load_image_array(self.DIR(IVC_name))

        # Add masks for the aorta and pulmonary artery
        seg_array = ima.add_masks_replace_only(input_seg_array, aorta_slicer_array, aorta_pair[1], C.Ao_BP_label)
        seg_array = ima.add_masks_replace_only(seg_array, PArt_slicer_array, PArt_pair[1], C.PArt_BP_label)

        # Replace the RA label with the SVC or IVC label
        new_RA_array = ima.and_filter(seg_array, SVC_slicer_array, C.SVC_label, C.RA_BP_label)
        seg_array = ima.add_masks_replace_only(seg_array, new_RA_array, C.RA_BP_label, C.SVC_label)

        new_RA_array = ima.and_filter(seg_array, IVC_slicer_array, C.IVC_label, C.RA_BP_label)
        seg_array = ima.add_masks_replace_only(seg_array, new_RA_array, C.RA_BP_label, C.IVC_label)
    
        self.logger.info(' ## Formatting and saving the segmentation ##')
        seg_array = np.swapaxes(seg_array, 0, 2)
        ima.save_itk(seg_array, origin, spacings, self.DIR(output_name), self.swap_axes)
    
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
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)
        C = self.CONSTANTS

        self.logger.info(f' ## Flattening base of {label} ## \n')

        seg_array = img.connected_component(input_filename, seed, label, self.path2points)
        seg_array = img.add_masks_replace_only(seg_array, seg_array, C.RA_BP_label, label)
        CC_array, header = nrrd.read(self.TMP('CC.nrrd'))

        seg_array = img.add_masks_replace(seg_array, CC_array, label)
        seg_array = np.swapaxes(seg_array, 0, 2)
        img.save_itk(seg_array, origin, spacings, output_filename)

    def get_distance_map_dictionaries(self, dist_label, dmap_name, th_label, th_name) :
        CDIC = self.CONSTANTS.get_dictionary()
        ld = {DISTANCE_MAP_KEY: CDIC[dist_label], THRESHOLD_KEY:  CDIC[th_label]}
        td = {DISTANCE_MAP_KEY: dmap_name, THRESHOLD_KEY: th_name}
        return ld, td
    
    def get_distance_map_tuples(self, mom1:MM, label1, arr1, mom2:MM, label2, arr2) : 
        return self.get_distance_map_tuples_from_lists([mom1, mom2], [label1, label2], [arr1, arr2])
    
    def get_distance_map_tuples_from_lists(self, mom_list, label_list, arr_list) : 
        return [ (mom, label, arr) for mom, label, arr in zip(mom_list, label_list, arr_list) ]

    def distance_map_and_save(self, input_name, output_name, label) :
        distance_map = img.distance_map(self.DIR(input_name), label)
        sitk.WriteImage(distance_map,self.TMP(output_name),True)

    def threshold_and_save(self, input_name, output_name, label) :
        thresholded_mask = img.threshold_filter_nrrd(self.TMP(input_name),0, label)
        sitk.WriteImage(thresholded_mask,self.TMP(output_name),True)
    
    def threshold_distance_map(self, input_name, labels:dict, tmp_dict:dict, skip_processed=False) -> dict: 
        """
        Creates a mask from a distance map and adds it to the segmentation. 
       
        tmp_dict contains the names of the distance map and the thresholded mask.
        tmp_dict = {
            DISTANCE_MAP_KEY: 'LV_DistMap.nrrd',
            THRESHOLD_KEY: 'LV_neck.nrrd'
        }       
        labels = { # get these from Labels.py
            DISTANCE_MAP_KEY: Labels.LV_BP_label,
            THRESHOLD_KEY: Labels.LV_neck_WT
        } 

        skip_processed: if True, will skip the processing of the distance map calculation if exists
        """
        dmap_name = tmp_dict[DISTANCE_MAP_KEY]
        thresh_name = tmp_dict[THRESHOLD_KEY]

        if skip_processed and os.path.exists(self.TMP(dmap_name)):
            self.logger.info(f"Skipping distance map calculation for {dmap_name}")
        else :
            self.distance_map_and_save(input_name, dmap_name, labels[DISTANCE_MAP_KEY])
    
        self.threshold_and_save(dmap_name, thresh_name, labels[THRESHOLD_KEY])

        outputs_dic = {
            DISTANCE_MAP_KEY: self.TMP(dmap_name),
            THRESHOLD_KEY: self.TMP(thresh_name)
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
            DISTANCE_MAP_KEY: 'LV_DistMap.nrrd',
            THRESHOLD_KEY: 'LV_neck.nrrd'
        }       
        labels = { # get these from Labels.py
            DISTANCE_MAP_KEY: Labels.LV_BP_label,
            THRESHOLD_KEY: Labels.LV_neck_WT
        } 
        """
        origin, spacings = self.get_origin_spacing()
        C=self.CONSTANTS

        files_dic = self.threshold_distance_map(input_name, labels, tmp_dict)

        thresholded_array, _ = nrrd.read(files_dic[THRESHOLD_KEY])
        input_array, _ = nrrd.read(self.DIR(input_name)) 

        io_tuple_list = [
            (thresholded_array, thresholded_array), 
            (input_array, thresholded_array), 
        ]

        if len(add_mask_list)>2:
            io_tuple_list.append((None, thresholded_array))

        output_array = np.empty(input_array.shape, np.uint8)

        for ix, images in enumerate(io_tuple_list): 
            imga, imgb = images
            mode, newmask, forbid_list = add_mask_list[ix]
            if imga is not None:           
                output_array = img.process_mask(imga, imgb, newmask, mode, forbid_changes=forbid_list)
            else:
                output_array = img.process_mask(output_array, imgb, newmask, mode, forbid_changes=forbid_list)            
    
        output_array = np.swapaxes(output_array, 0, 2)
        img.save_itk(output_array, origin, spacings, self.DIR(output_name))

    def extract_structure_w_distance_map(self, image_name, output_name, labels:dict, tmp_dict:dict, label_a, new_label, skip_dmap=False) : 
        """
        tmp_dict contains the names of the distance map and the thresholded mask.
        tmp_dict = {
            DISTANCE_MAP_KEY: 'LV_DistMap.nrrd',
            THRESHOLD_KEY: 'LV_neck.nrrd'
        }       
        labels = { # get these from Labels.py
            DISTANCE_MAP_KEY: Labels.LV_BP_label,
            THRESHOLD_KEY: Labels.LV_neck_WT
        } 
        """
        origin, spacings = self.get_origin_spacing()
        C=self.CONSTANTS

        files_dic = self.threshold_distance_map(image_name, labels, tmp_dict, skip_processed=skip_dmap)

        thresholded_array, _ = nrrd.read(files_dic[THRESHOLD_KEY])
        input_array, _ = nrrd.read(self.DIR(image_name)) 

        thresholded_array = img.and_filter(input_array,thresholded_array,label_a,new_label)
        seg_array = img.process_mask(input_array, thresholded_array, new_label, MM.REPLACE_ONLY)

        seg_array = np.swapaxes(seg_array, 0, 2)
        img.save_itk(seg_array, origin, spacings, self.DIR(output_name))

    def creating_vein_rings(self, image_name, output_name_i, output_name_j, list_of_rings, list_of_processes):

        origin, spacings = self.get_origin_spacing()
        C=self.CONSTANTS
        CDIC = C.get_dictionary()
        def convert_labels(labels_str) : 
            if labels_str == '':
                return []
            else :
                return [CDIC[x] for x in labels_str.split(',')]

        LA_myo_thresh_array, _ = nrrd.read(list_of_rings.pop(0))
        RA_myo_thresh_array, _ = nrrd.read(list_of_rings.pop(0))

        input_array, _ = nrrd.read(self.DIR(image_name))
        seg_i_array = copy.deepcopy(input_array)
        seg_j_array = copy.deepcopy(input_array)
        #('LPV1_ring_label', mom.NO_OVERRIDE, [], mom.REPLACE, []
        for ring_path, processable in zip(list_of_rings, list_of_processes):
            ring_label_str, mode1, forbid_labels_str1 = processable
            ring_label = CDIC[ring_label_str]
            ring_array, _ = nrrd.read(ring_path)
            forbid_labels1 = convert_labels(forbid_labels_str1)
            mode2 = MM.REPLACE

            for fb_label in forbid_labels1 :
                seg_i_array = img.process_mask(seg_i_array, ring_array, ring_label, mode1, forbid_changes=[fb_label])
            ring_array = img.and_filter(seg_i_array, LA_myo_thresh_array, ring_label, ring_label)
            seg_j_array = img.process_mask(seg_j_array, ring_array, ring_label, mode2, forbid_changes=[])
        
        seg_i_array = np.swapaxes(seg_i_array, 0, 2)
        seg_j_array = np.swapaxes(seg_j_array, 0, 2)

        img.save_itk(seg_i_array, origin, spacings, self.DIR(output_name_i))
        img.save_itk(seg_j_array, origin, spacings, self.DIR(output_name_j))

    def creating_valve_planes(self, image_name, LA_BP_name, RA_BP_name, output_name, list_of_la_labels, list_of_ra_labels):
        origin, spacings = self.get_origin_spacing()
        C=self.CONSTANTS
        CDIC = C.get_dictionary()

        LA_BP_array, _ = nrrd.read(self.TMP(LA_BP_name))
        RA_BP_array, _ = nrrd.read(self.TMP(RA_BP_name))

        input_array, _ = nrrd.read(self.DIR(image_name))
        seg_array = copy.deepcopy(input_array)

        for label, plane_label in list_of_la_labels : 
            plane_array = img.and_filter(seg_array, LA_BP_array, label, plane_label)
            seg_array = img.process_mask(seg_array, plane_array, plane_label, MM.REPLACE)

        for label, plane_label in list_of_ra_labels :
            extra_processing = (label == C.SVC_label)
            plane_array = img.and_filter(seg_array, RA_BP_array, label, plane_label)
            if extra_processing : 
                plane_extra_array = img.and_filter(seg_array, RA_BP_array, C.RPV1_ring_label, plane_label)
            seg_array = img.process_mask(seg_array, plane_array, plane_label, MM.REPLACE)
            if extra_processing : 
                seg_array = img.process_mask(seg_array, plane_extra_array, plane_label, MM.REPLACE)

        seg_array = np.swapaxes(seg_array, 0, 2)
        img.save_itk(seg_array, origin, spacings, self.DIR(output_name))

    def pushing_in(self, img_array: np.ndarray, pusher_wall_lab, pushed_wall_lab, pushed_bp_lab, pushed_wt) -> np.ndarray :
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)
        origin, spacings = self.get_origin_spacing()
        im = ima.array2itk(img_array, origin, spacings)
        
        return ima.push_inside(im, pusher_wall_lab, pushed_wall_lab, pushed_bp_lab, pushed_wt)

    def push_in_and_save(self, input_name, pusher_wall_lab, pushed_wall_lab, pushed_BP_lab, pushed_WT, outname='') -> np.ndarray :
        origin, spacings = self.get_origin_spacing()
        outname = input_name if outname=='' else outname

        # seg_array = img.push_inside(self.path2points, self.DIR(input_name), pusher_wall_lab, pushed_wall_lab, pushed_BP_lab, pushed_WT) 
        # seg_array = np.swapaxes(seg_array, 0, 2)
        # img.save_itk(seg_array, origin, spacings, self.DIR(outname))
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)
        im = ima.load_sitk_image(self.DIR(input_name))
        seg_array = ima.push_inside(im, pusher_wall_lab, pushed_wall_lab, pushed_BP_lab, pushed_WT)

        if outname != "":
            self.logger.debug(f"Saving pushed segmentation array to {outname}", exc_info=self.debug)
            self.save_if_seg_steps(seg_array, outname)

    def cropping_veins(self, input_name, slicer_tuple_list, output_name) :
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
    
    def get_connected_component(self, input_name, seed, layer) : 
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)
        input_array = ima.load_sitk_image(self.DIR(input_name))
        
        return ima.connected_component(input_array, seed, layer)
    def get_connected_component_and_save(self, input_name, seed, layer, output_name) : 
        origin, spacings = self.get_origin_spacing()
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)

        seg_array = self.get_connected_component(input_name, seed, layer)
        self.save_if_seg_steps(seg_array, output_name)
        # ima.save_itk(seg_array, origin, spacings, self.DIR(output_name), self.swap_axes)

    def connected_component_process(self, seg_array, seed, layer, outname) : 
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)
        origin, spacing = self.get_origin_spacing()

        seg_itk = ima.array2itk(seg_array, origin, spacing)
        seg_new_array = ima.connected_component(seg_itk, seed, layer)

        self.save_if_seg_steps(seg_new_array, outname)

        return seg_new_array
    

    def extract_distmap_and_threshold(self, seg_array, labels:list, dm_name, th_name, dmap_array=None): 
        """
        Extracts a distance map and threshold array from a segmentation array.

        Args:
            seg_array (np.array): The input segmentation array.
            labels (list): A list containing two labels. The first label is used for generating the distance map, and the second label is used for thresholding.
            dm_name (str): The name of the output file to save the distance map array.
            th_name (str): The name of the output file to save the threshold array.
            dmap_array (np.array, optional): An optional pre-computed distance map array. If provided, this array will be used instead of generating a new distance map.

        Returns:
            tuple: A tuple containing the distance map array and the threshold array.

        Example Usage:
            four_chamber = FourChamberProcess(path2points, origin_spacing, CONSTANTS)
            seg_array = ...
            labels = [label1, label2] # get labels from Labels.py
            dm_name = "distance_map.nrrd"
            th_name = "threshold.nrrd"
            distmap_array, thresh_array = four_chamber.extract_distmap_and_threshold(seg_array, labels, dm_name, th_name)
        """
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)
        origin, spacing = self.get_origin_spacing()

        seg_itk = ima.array2itk(seg_array, origin, spacing)
        skip_dmap = dmap_array is not None
        if skip_dmap:
            distmap_itk = ima.array2itk(dmap_array, origin, spacing)
        else:
            distmap_itk = ima.distance_map(seg_itk, labels[0], dm_name)

        thresh_array = ima.threshold_filter_array(distmap_itk, 0, labels[1], th_name)
        distmap_array = dmap_array if (skip_dmap) else ima.itk2array(distmap_itk)

        return distmap_array, thresh_array

    def intersect_and_replace(self, seg_array: np.ndarray, thresh_array: np.ndarray, intrsct_label1, intrsct_label2, replace_label, outname="") -> np.ndarray :
        """
        Intersects two segmentation arrays and replaces the intersected region with a specified label.

        Args:
            seg_array (np.array): The segmentation array to be modified.
            thresh_array (np.array): The threshold array used for intersection.
            intrsct_label1 (int): The label value of the first segmentation array to be intersected.
            intrsct_label2 (int): The label value of the second segmentation array to be intersected.
            replace_label (int): The label value to replace the intersected region with.

        Returns:
            np.array: The modified segmentation array with the intersected region replaced.

        Example Usage:
            four_chamber = FourChamberProcess(path2points, origin_spacing, CONSTANTS)
            seg_array_new = four_chamber.intersect_and_replace(seg_array, thresh_array, intrsct_label1, intrsct_label2, replace_label)
        """
        origin, spacings = self.get_origin_spacing()
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)

        self.logger.debug(f"Intersecting structures with labels {intrsct_label1} and {intrsct_label2}")
        struct_array = ima.and_filter(seg_array, thresh_array, intrsct_label1, intrsct_label2)

        self.logger.debug(f"AND filter unique values: {np.unique(struct_array)}")

        self.logger.debug(f"Replacing intersected structures with label {replace_label}")
        seg_array_new = ima.add_masks_replace(seg_array, struct_array, replace_label)

        if outname != "":
            self.logger.debug(f"Saving intersected and replaced segmentation array to {outname}", exc_info=self.debug)
            self.save_if_seg_steps(seg_array_new, outname)

        return seg_array_new, struct_array
    
    def extract_structure(self, seg_array, labels: list, dm_name: str, th_name: str, outname: str, dmap_array=None): 
        """
        Extracts a specific structure from a segmentation array using a series of image processing operations.

        Args:
            seg_array (np.array): The input segmentation array.
            labels (list): A list of labels used for different image processing operations. The list should contain the following labels in the specified order:
                - labels[0] (int): The label of the structure used for distance map calculation.
                - labels[1] (int): The label of the structure used for thresholding.
                - labels[2] (int): The label of the structure used for the AND filter operation.
                - labels[3] (int): The label of the structure used as the mask for the AND filter operation.
                - labels[4] (int): The label of the structure to be added to the segmentation array.
            dm_name (str): The name of the distance map file to be saved.
            th_name (str): The name of the thresholded array file to be saved.
            outname (str): The name of the output segmentation array file to be saved.

        Returns:
            tuple: A tuple containing the following arrays in the specified order:
                - seg_array_new (np.array): The modified segmentation array with the extracted structure added.
                - distmap_array (np.array): The distance map array.
                - thresh_array (np.array): The thresholded array.
                - struct_array (np.array): The structure array obtained from the AND filter operation.

        Example Usage:
            four_chamber = FourChamberProcess(path2points, origin_spacing, CONSTANTS)
            seg_array = ...
            labels = [label1, label2, label3, label4, label5]
            dm_name = "distance_map.nrrd"
            th_name = "thresholded_array.nrrd"
            outname = "output_segmentation.nrrd"
            result = four_chamber.extract_structure(seg_array, labels, dm_name, th_name, outname)
        """
        origin, spacings = self.get_origin_spacing()
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)

        self.logger.debug(f"Extracting distance map for label {labels[0]} and threshold at: {labels[1]}")
        distmap_array, thresh_array = self.extract_distmap_and_threshold(seg_array, labels, dm_name, th_name, dmap_array)

        self.logger.debug(f"Intersecting and replacing structures with labels {labels[2]}, {labels[3]}, and {labels[4]}")
        seg_array_new, struct_array = self.intersect_and_replace(seg_array, thresh_array, labels[2], labels[3], labels[4])

        self.save_if_seg_steps(seg_array_new, outname)
        
        return seg_array_new, distmap_array, thresh_array, struct_array
    
    def extract_atrial_rings(self, seg_array, acc_array, ring_array, atrial_myo_thresh, pv_ring_label, outname, replace_only_label:list=[]) : 
        """
        Extracts the atrial rings from the segmentation array by adding or replacing the ring array.
        
        Args:
            seg_array (np.array): The segmentation array.
            acc_array (np.array): The array representing the finsl output of all the veins (seg_s4j)
            ring_array (np.array): The array representing the atrial rings.
            atrial_myo_thresh (float): The threshold value for the left atrial myocardium.
            pv_ring_label (int): The label value of the pulmonary vein ring.
            outname (str): The name of the output file to save the modified segmentation array.
            replace_only_label (list, optional): A list of label values for which the ring array should be replaced instead of added. Defaults to [].
        
        Returns:
            np.array: The modified segmentation array with the atrial rings added or replaced.
        
        Example Usage:
            four_chamber = FourChamberProcess(path2points, origin_spacing, CONSTANTS)
            seg_array = ...
            ring_array = ...
            atrial_myo_thresh = ...
            pv_ring_label = ...
            outname = ...
            replace_only_label = ...
            result = four_chamber.extract_atrial_rings(seg_array, ring_array, atrial_myo_thresh, pv_ring_label, outname, replace_only_label)
        """
        origin, spacings = self.get_origin_spacing()
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)

        # intermediate_array = ima.add_masks(seg_array, ring_array, pv_ring_label) 
        if not replace_only_label :
            intermediate_array = ima.add_masks(seg_array, ring_array, pv_ring_label)
        else:
            # in LA: only for rpv1 where replace_only_label == [SVC_label]
            # in RA: only for SVC where replace_only_label == [Ao_wall_label, LA_myo_label, RPV1_ring_label, RPV1_label, RPV2_ring_label, RPV2_label]
            for label in replace_only_label:
                intermediate_array = ima.add_masks_replace_only(seg_array, ring_array, pv_ring_label, label)
        
        # seg_array_new, _ = self.intersect_and_replace(intermediate_array, atrial_myo_thresh, pv_ring_label, pv_ring_label, pv_ring_label)
        ring_array = ima.and_filter(intermediate_array, atrial_myo_thresh, pv_ring_label, pv_ring_label)
        seg_array_new = ima.add_masks_replace(acc_array, ring_array, pv_ring_label)


        self.save_if_seg_steps(intermediate_array, outname)

        return seg_array_new, intermediate_array
    
    def create_myocardium(self, seg_array: np.ndarray, labels: list, mode:MM, mode_labels, seg_out, mode2: MM = None, mode2_labels = None, dmname="", thname="") -> np.array:
        """
    Create myocardium segmentation based on the input segmentation array.

    Args:
        seg_array (np.ndarray): The input segmentation array.
        labels (list): A list of labels to be used for myocardium segmentation.
            labels[0,1] (int): labels for extracting the distance map and threshold array.
            labels[2] (int): label for the structure to be added to the segmentation array (add_masks_replace).
            labels[3] (int): label for the structure to be added to the segmentation array (add_masks_mode:newmask).
            labels[4] (int): OPTIONAL: label for the structure to be added to the segmentation array (add_masks_mode:newmask).
        mode (MM): The mode of mask operation to be used.
        mode_labels: The labels to be used for the mode mask operation.
        seg_out: The name of the output segmentation file.
        mode2 (MM, optional): The second mode of mask operation to be used. Defaults to None.
        mode2_labels (optional): The labels to be used for the second mode mask operation. Defaults to None.
        dmname (str, optional): The name of the distance map file. Defaults to "".
        thname (str, optional): The name of the threshold file. Defaults to "".

    Returns:
        np.array: The myocardium segmentation array.
"""
        dmname = dmname if dmname != "" else "myo_distmap.nrrd"
        thname = thname if thname != "" else "myo_threshold.nrrd"
        
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)

        _, myo_array = self.extract_distmap_and_threshold(seg_array, labels, dmname, thname)
        myo_array = ima.add_masks_replace(myo_array, myo_array, labels[2])
        seg_new_array = ima.add_masks_mode(seg_array, myo_array, mode, newmask=labels[3], special_case_labels=mode_labels)

        if mode2 is not None and mode2_labels is not None:
            seg_new_array = ima.add_masks_mode(seg_new_array, myo_array, mode2, newmask=labels[4], special_case_labels=mode2_labels)
        
        self.save_if_seg_steps(seg_new_array, seg_out)

        return seg_new_array
        
    
    def load_image_array(self, filename:str) -> np.array:
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)
        return ima.load_image_array(self.DIR(filename))
    
    def save_image_array(self, array:np.array, filename:str):
        ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)
        origin, spacings = self.get_origin_spacing()

        ima.save_itk(array, origin, spacings, self.DIR(filename), self.swap_axes)

    def save_if_seg_steps(self, array:np.array, filename:str, saving_itk=True):
        if self.save_seg_steps:
            if saving_itk:
                origin, spacings = self.get_origin_spacing()
                ima = ImageAnalysis(path2points=self.path2points, debug=self.debug)
                ima.save_itk(array, origin, spacings, self.DIR(filename), self.swap_axes)
            else:
                self.save_image_array(array, filename)