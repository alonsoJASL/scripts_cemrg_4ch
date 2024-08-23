import nrrd
import copy
import numpy as np
import os
import SimpleITK as sitk
import multiprocessing as mp
import inspect

from enum import Enum

from seg_scripts.common import configure_logging, big_print, make_tmp

ZERO_LABEL = 0
SEG_LABEL = 1
class MaskOperationMode(Enum):
  REPLACE_EXCEPT = 1
  REPLACE_ONLY = 2
  REPLACE = 3
  ADD = 4
  NO_OVERRIDE = 5

ORIENT_CHOICES = ['LPS', 'RAI', 'LAI', 'RPS']
class ImageAnalysis: 
    def __init__(self, path2points="", debug=False):
        self._path2points = path2points
        self._debug = debug
        self.logger = configure_logging(log_name=__name__, is_debug=self._debug)

    @property
    def path2points(self):
        return self._path2points
    
    @path2points.setter
    def path2points(self, path2points):
        self._path2points = path2points

    @property
    def debug(self):
        return self._debug
    
    @debug.setter
    def debug(self, debug):
        self._debug = debug

    def DIR(self, x=""):
        return os.path.join(self.path2points, x)
    
    def TMP(self, x=""):
        return os.path.join(self.path2points, "tmp", x)
    
    def set_debug(self, debug, pth2points):
        self.debug = debug
        self.path2points = pth2points
    
    def loc_mask(self, img_array: np.ndarray):
        """
        Get the locations of the mask in an image array.
        """ 
        mask_ind = np.array(img_array.nonzero())
        return mask_ind
    
    def find_maskloc(self, img_array: np.ndarray, spacing: np.ndarray, img_offset: np.ndarray) -> np.ndarray:
        origin_ind = img_offset / spacing
        origin_ind.round() 
        mask_ind=np.array(img_array.nonzero())
        mask_ind[0]+=int(origin_ind.round()[0]); 
        mask_ind[1]+=int(origin_ind.round()[1]); 
        mask_ind[2]+=int(origin_ind.round()[2]);

        return mask_ind


    def pad_image(self, img_array: np.ndarray, pad_x=10, pad_y=10, pad_z=10, pad_value=0) -> np.ndarray:
        """
        Pad an image array with specified values.

        Parameters:
            img_array (np.ndarray): The input image array.
            pad_x (int): The amount of padding to add along the x-axis. Default is 10.
            pad_y (int): The amount of padding to add along the y-axis. Default is 10.
            pad_z (int): The amount of padding to add along the z-axis. Default is 10.
            pad_value (int): The value to use for padding. Default is 0.

        Returns:
            np.ndarray: The padded image array.

        """
        constant_pad_values = ((pad_value, pad_value), (pad_value, pad_value), (pad_value, pad_value))
        padded_img_array = np.pad(img_array, ((pad_x, pad_x), (pad_y, pad_y), (pad_z, pad_z)), mode='constant', constant_values=constant_pad_values)
        return padded_img_array
    
    def distance_map(self, img: sitk.Image, label: int, outname="") -> sitk.Image:
        """
        Generate a distance map from an image.

        Parameters:
            img (sitk.Image): The input image.
            label (int): The label to use for the distance map.

        Returns:
            sitk.Image: The distance map.

        """
        thresholded_img = self.threshold_filter(img, label, label)
        distance_map_filter = sitk.DanielssonDistanceMapImageFilter()
        distance_map_filter.InputIsBinaryOff()
        distance_map_filter.SquaredDistanceOff()
        distance_map_filter.UseImageSpacingOff()
        DistMap = distance_map_filter.Execute(thresholded_img)

        if self.debug:
            outname = outname if outname != "" else "DistMap.nrrd"
            outname += ".nrrd" if not outname.endswith(".nrrd") else ""
            save_path = self.TMP(outname)
            sitk.WriteImage(DistMap, save_path)

        return DistMap

    def threshold_filter(self, img: sitk.Image, lower, upper, outname="", binarise=False) -> sitk.Image: 
        """
        Apply a threshold filter to an image.

        Parameters:
            img (sitk.Image): The input image.
            lower (int): The lower threshold value.
            upper (int): The upper threshold value.

        Returns:
            sitk.Image: The thresholded image.

        """

        if binarise:
            threshold_filter = sitk.BinaryThresholdImageFilter()
            threshold_filter.SetLowerThreshold(lower)
            threshold_filter.SetUpperThreshold(upper)
            threshold_filter.SetOutsideValue(ZERO_LABEL)
            threshold_filter.SetInsideValue(SEG_LABEL)
        else:    
            threshold_filter = sitk.ThresholdImageFilter()
            threshold_filter.SetLower(lower)
            threshold_filter.SetUpper(upper)
            threshold_filter.SetOutsideValue(ZERO_LABEL)

        thresholded_img = threshold_filter.Execute(img)

        if self.debug:
            outname = outname if outname != "" else "Thresh.nrrd"
            outname += ".nrrd" if not outname.endswith(".nrrd") else ""
            # check TMP folder 
            make_tmp(self.TMP())
            save_path = self.TMP(outname)
            sitk.WriteImage(thresholded_img, save_path)

        return thresholded_img
    
    def threshold_filter_array(self, img: sitk.Image, lower, upper, outname="") -> np.ndarray:
        """
        Apply a threshold filter to an image array.

        Parameters:
            img (sitk.Image): The input image.
            lower (int): The lower threshold value.
            upper (int): The upper threshold value.

        Returns:
            np.ndarray: The thresholded image array.

        """
        thresholded_img = self.threshold_filter(img, lower, upper, outname)
        thresholded_img_array = sitk.GetArrayFromImage(thresholded_img)

        return thresholded_img_array

    def and_filter(self, imga_array: np.ndarray, imgb_array: np.ndarray, label_a, new_label) -> np.ndarray:
        """
        Apply an 'and' filter to two image arrays.

        Parameters:
            imga_array (np.ndarray): The first input image array.
            imgb_array (np.ndarray): The second input image array.
            label_a (int): The label value in imga_array to compare against.
            new_label (int): The new label value to assign in imgb_array.

        Returns:
            np.ndarray: The resulting image array after applying the 'and' filter.

        """
        self.logger.debug(f"Applying AND filter to values where imga_array == {label_a} setting to {new_label}")
        # Get indices where imgb_array is nonzero
        imgb_indices = np.transpose(np.nonzero(imgb_array))

        # Apply filtering
        imga_values = imga_array[imgb_indices[:, 0], imgb_indices[:, 1], imgb_indices[:, 2]]
        imgb_array_new = np.zeros_like(imgb_array)
        imgb_array_new[imgb_indices[:, 0], imgb_indices[:, 1], imgb_indices[:, 2]] = np.where(imga_values == label_a, new_label, 0)
        
        return imgb_array_new

    def remove_filter(self, imga_array: np.ndarray, imgb_array: np.ndarray, label_remove) -> np.ndarray:
        """
        Apply a mask to an image array, replacing the pixels that belong to the mask with a new value.

        Parameters:
            imga_array (np.ndarray): The first input image array.
            imgb_array (np.ndarray): The second input image array.
            label_remove: The value to assign to the pixels in imga_array that belong to the mask.

        Returns:
            np.ndarray: The resulting image array after applying the mask and replacing the pixels.
        """
        imga_array_new = copy.deepcopy(imga_array)
        mask_indices = np.transpose(np.where(imgb_array != ZERO_LABEL))

        for n in mask_indices:
            test_value_a = imga_array_new[n[0], n[1], n[2]]
            if test_value_a == label_remove:
                imga_array_new[n[0], n[1], n[2]] = ZERO_LABEL
        
        return imga_array_new
    
    def add_masks_mode(self, imga_array: np.ndarray, imgb_array: np.ndarray, mode: MaskOperationMode, newmask, special_case_labels = None) -> np.ndarray:
        switcher = {
            MaskOperationMode.REPLACE_EXCEPT: self.add_masks_replace_except,
            MaskOperationMode.REPLACE_ONLY: self.add_masks_replace_only,
            MaskOperationMode.REPLACE: self.add_masks_replace,
            MaskOperationMode.ADD: self.add_masks,
            MaskOperationMode.NO_OVERRIDE: self.add_masks
        }

        func = switcher.get(mode)
        if func is None:
            raise ValueError(f'Invalid mode: {mode}')

        if mode == MaskOperationMode.REPLACE_EXCEPT and special_case_labels is not None:
            func_array = func(imga_array, imgb_array, newmask, except_these=special_case_labels)
            return func_array
        elif mode == MaskOperationMode.REPLACE_ONLY and special_case_labels is not None:
            func_array = func(imga_array, imgb_array, newmask, only_override_this=special_case_labels)
            return func_array
        else:
            func_array = func(imga_array, imgb_array, newmask)
            return func_array

    
    def add_masks(self, imga_array: np.ndarray, imgb_array: np.ndarray, newmask) -> np.ndarray:
        """
        Apply a mask (imgb) to an image array without overriding any pixels that already belong to the image array.

        Parameters:
            imga_array (np.ndarray): The first input image array.
            imgb_array (np.ndarray): The second input image array.
            newmask: The value to assign to the pixels in imga_array that are not already part of the image array.

        Returns:
            np.ndarray: The resulting image array after applying the mask.

        """
        
        # does not override any pixels that already belong to imga_array 
        imga_array_new = copy.deepcopy(imga_array)
        mask_indices = np.transpose(np.where(imgb_array != ZERO_LABEL))

        for n in mask_indices: 
            test_value_a = imga_array_new[n[0], n[1], n[2]]
            if test_value_a == ZERO_LABEL:
                imga_array_new[n[0], n[1], n[2]] = newmask

        return imga_array_new
    
    def add_masks_replace(self, imga_array: np.ndarray, imgb_array: np.ndarray, newmask) -> np.ndarray:
        """
        Apply a mask to an image array, replacing the pixels that belong to the mask with a new value.

        Parameters:
            imga_array (np.ndarray): The first input image array.
            imgb_array (np.ndarray): The second input image array.
            newmask: The value to assign to the pixels in imga_array that belong to the mask.

        Returns:
            np.ndarray: The resulting image array after applying the mask and replacing the pixels.

        """

        # overrides any pixels that already belong to a mask
        imga_array_new = copy.deepcopy(imga_array)
        mask_indices = np.transpose(np.where(imgb_array != ZERO_LABEL))

        imga_array_new[mask_indices[:, 0], mask_indices[:, 1], mask_indices[:, 2]] = newmask

        return imga_array_new
    
    
    def add_masks_replace_only(self, imga_array: np.ndarray, imgb_array: np.ndarray, newmask, only_override_this) -> np.ndarray:
        """
        Apply a mask to an image array, replacing the pixels that belong to the mask with a new value.

        Parameters:
            imga_array (np.ndarray): The first input image array.
            imgb_array (np.ndarray): The second input image array.
            newmask: The value to assign to the pixels in imga_array that belong to the mask.
            only_override_this: The value of pixels in imga_array that should be overridden with the newmask.

        Returns:
            np.ndarray: The resulting image array after applying the mask and replacing the pixels.
        """

        # only overrides pixels that already belong to a specific mask
        if imga_array.shape != imgb_array.shape:
            imga_array = np.swapaxes(imga_array, 0, 2)
            # raise ValueError("Input arrays must have the same shape")
            
        imga_array_new = copy.deepcopy(imga_array)
        mask_indices = np.transpose(np.where(imgb_array != ZERO_LABEL))

        for n in mask_indices:
            test_value_a = imga_array_new[n[0], n[1], n[2]]
            if test_value_a == ZERO_LABEL or test_value_a == only_override_this:
                imga_array_new[n[0], n[1], n[2]] = newmask
            
        return imga_array_new
    
    def add_masks_replace_except(self, imga_array: np.ndarray, imgb_array: np.ndarray, newmask, except_these: list) -> np.ndarray:
        """
        Apply a mask to an image array, replacing the pixels that belong to the mask with a new value, except for specific values.

        Parameters:
            imga_array (np.ndarray): The first input image array.
            imgb_array (np.ndarray): The second input image array.
            newmask: The value to assign to the pixels in imga_array that belong to the mask.
            except_these (list): A list of values that should not be overridden with the newmask.

        Returns:
            np.ndarray: The resulting image array after applying the mask and replacing the pixels, except for the specified values.

        """
        # overrides all pixels except those belonging to a given mask
        imga_array_new = copy.deepcopy(imga_array)
        mask_indices = np.transpose(np.where(imgb_array != ZERO_LABEL))

        for n in mask_indices:
            test_value_a = imga_array_new[n[0], n[1], n[2]]
            if test_value_a not in except_these:
                imga_array_new[n[0], n[1], n[2]] = newmask
        
        return imga_array_new
    
    def push_inside(self, img: sitk.Image, pusher_wall_label, pushed_wall_label, pushed_bp_label, pushed_wt) -> np.ndarray:
        pusher_wall_dist_map = self.distance_map(img, pusher_wall_label)
        new_pushed_wall = self.threshold_filter(pusher_wall_dist_map, 0, pushed_wt)

        if self.debug:
            sitk.WriteImage(new_pushed_wall, self.TMP("pushed_wall.nrrd"))
        
        img_array = sitk.GetArrayFromImage(img)
        new_pushed_wall_array = sitk.GetArrayFromImage(new_pushed_wall)
        new_pushed_wall_array = self.and_filter(img_array, new_pushed_wall_array, pushed_bp_label, pushed_wall_label)

        img_array = self.add_masks_replace(img_array, new_pushed_wall_array, pushed_wall_label)

        return img_array
    
    def push_ring_inside(self, img: sitk.Image, pusher_wall_label, pushed_wall_label, pushed_bp_label, pushed_wt) -> np.ndarray:
        pusher_wall_dist_map = self.distance_map(img, pusher_wall_label)
        new_pushed_wall = self.threshold_filter(pusher_wall_dist_map, 0, pushed_wt)

        if self.debug:
            sitk.WriteImage(new_pushed_wall, self.TMP("pushed_wall.nrrd"))
        
        img_array = sitk.GetArrayFromImage(img)
        new_pushed_wall_array = sitk.GetArrayFromImage(new_pushed_wall)

        new_pushed_wall_array = self.and_filter(img_array, new_pushed_wall_array, pushed_bp_label, pushed_wall_label)
        img_array = self.add_masks(img_array, new_pushed_wall_array, pushed_wall_label)

        return img_array
    
    def connected_component(self, imga: sitk.Image, seed: list, layer: int, keep=False) -> np.ndarray : 
        # cast seed as list of uint8
        # seed_int = list(map(int, seed))
        seed_int = [list(map(int, seed[i:i+3])) for i in range(0, len(seed), 3)]
        new_layer = layer + 100
        CC = sitk.ConnectedThreshold(imga, seedList=seed_int, lower=layer, upper=layer, replaceValue=new_layer)

        imga_array = sitk.GetArrayFromImage(imga)
        CC_array = sitk.GetArrayFromImage(CC)

        if self.debug:
            origin = imga.GetOrigin()
            spacing = imga.GetSpacing()
            self.save_itk(CC_array, origin, spacing, self.TMP("CC.nrrd"))
            # sitk.WriteImage(CC, self.TMP("CC.nrrd"))
        if keep:
            imga_array = self.remove_filter(imga_array, imga_array, layer)

        imgb_array = self.add_masks_replace(imga_array, CC_array, ZERO_LABEL)

        return imgb_array
    
    def connected_component_keep(self, imga: sitk.Image, seed: list, layer: int) -> np.ndarray:
        return self.connected_component(imga, seed, layer, True)
    
    def connected_component_keep_largest(self, imga: sitk.Image, layer: int) -> sitk.Image:
        component_img = sitk.ConnectedComponent(imga)
        sorted_cc_img = sitk.RelabelComponent(component_img, sortByObjectSize=True)

        cc_filter = sitk.ConnectedThresholdImageFilter()
        cc_filter.SetLower(1)
        cc_filter.SetUpper(1)
        cc_filter.SetReplaceValue(layer)

        largest_cc_img = cc_filter.Execute(sorted_cc_img)
        return largest_cc_img
    

    def mask_plane_creator(self, img_path:str , points: list, plane_name: str, slicer_radius: float, slicer_height: float, pro_path: str, o_origin=None, o_spac=None) -> None : 
        """
        Create a masked plane using the specified points and parameters.

        Parameters:
            img_path (str): The path to the image file.
            points (list): List of coordinates for the points.
            plane_name (str): Name of the plane.
            slicer_radius (float): Radius for the slicer.
            slicer_height (float): Height for the slicer.
            pro_path (str): Path for saving the plane.
            
            o_origin (optional): Origin information, overrides the origin in the image header
            o_spac (optional): Spacing information, overrides the spacing in the image header
        """
        import post_slicer as pslicer
        _, header = nrrd.read(img_path)
        img_min = header['axis mins'] if o_origin is None else o_origin
        img_spa = header['spacings'] if o_spac is None else o_spac
        img_siz = header['sizes']   
        # img_dim = str(len(img_siz))

        # coordinates 
        ppsa = np.array([(points[0] - 0.5) * img_spa[0], (points[1] - 0.5) * img_spa[1], (points[2] - 0.5) * img_spa[2]])
        ppsb = np.array([(points[3] - 0.5) * img_spa[0], (points[4] - 0.5) * img_spa[1], (points[5] - 0.5) * img_spa[2]])
        ppsc = np.array([(points[6] - 0.5) * img_spa[0], (points[7] - 0.5) * img_spa[1], (points[8] - 0.5) * img_spa[2]])

        img_siz_x = int(img_siz[0])
        img_siz_y = int(img_siz[1])
        img_siz_z = int(img_siz[2])

        img_min_x = float(img_min[0])
        img_min_y = float(img_min[1])
        img_min_z = float(img_min[2])

        size_tuple = (img_siz_x, img_siz_y, img_siz_z)
        spacing_tuple = (img_spa[0], img_spa[1], img_spa[2])
        min_tuple = (img_min_x, img_min_y, img_min_z)

        wh_im, he = pslicer.slice_segmentation(ppsa, ppsb, ppsc, size_tuple, spacing_tuple, min_tuple, slicer_height, slicer_radius)
        nrrd.write(f'{pro_path}/{plane_name}.nrrd', wh_im, he)     

    def mask_plane_creator_alternative(self, img_path:str, origin, spacing, points, plane_name, slicer_radius, slicer_height, segPath) -> None:
        """
        Create a masked plane using the specified points and parameters.

        Parameters:
            img_path (str): The path to the image file.

            origin: Origin information, overrides the origin in the image header.
            spacing: Spacing information, overrides the spacing in the image header.

            points (list): List of coordinates for the points.
            plane_name (str): Name of the plane.
            slicer_radius (float): Radius for the slicer.
            slicer_height (float): Height for the slicer.
            segPath (str): Path for saving the plane.
        """
        self.mask_plane_creator(img_path, points, plane_name, slicer_radius, slicer_height, segPath, o_origin=origin, o_spac=spacing)
    
    # helper functions 
    def array2itk(self, img_array: np.ndarray, origin, spacing) -> sitk.Image:
        """
        Convert an image array to a SimpleITK image.

        Parameters:
            img_array (np.ndarray): The input image array.
            origin: The origin of the image.
            spacing: The spacing of the image.

        Returns:
            sitk.Image: The resulting SimpleITK image.

        """
        img = sitk.GetImageFromArray(img_array)
        img.SetOrigin(origin)
        img.SetSpacing(spacing)
        return img
    
    def itk2array(self, img: sitk.Image) -> np.ndarray:
        """
        Convert a SimpleITK image to an image array.

        Parameters:
            img (sitk.Image): The input SimpleITK image.

        Returns:
            np.ndarray: The resulting image array.

        """
        img_array = sitk.GetArrayFromImage(img)
        return img_array
    
    def save_itk(self, img_array: np.ndarray, origin, spacing, filename, swap_axes=False, ref_image=None) -> None:
        """
        Save an image array as a SimpleITK image.

        Parameters:
            img_array (np.ndarray): The input image array.
            origin: The origin of the image.
            spacing: The spacing of the image.
            filename: The filename to save the image as.

        """
        if swap_axes:
            img_array = np.swapaxes(img_array, 0, 2)
        
        img = self.array2itk(img_array, origin, spacing)

        if ref_image is not None: # save the image keeping header 
            self.save_itk_keeping_header(img_obj=img, reference_img_obj=ref_image, filename=filename) 
        else: 
            sitk.WriteImage(img, filename)
    
    def save_itk_like_image(self, img:sitk.Image, reference_img:sitk.Image, filename, img_orient='LPS') -> None:
        """
        Save an image array as a SimpleITK image, preserving the header info of reference_img.

        Parameters:
            img (sitk.Image): The input image array.
            reference_img: The origin of the image.
            filename: The filename to save the image as.

        """
        if img_orient not in ORIENT_CHOICES:
            raise ValueError(f"Invalid orientation choice: {img_orient}")

        img.CopyInformation(reference_img)
        img.SetDirection(reference_img.GetDirection())
        img.SetOrigin(reference_img.GetOrigin())

        for key in reference_img.GetMetaDataKeys():
            img.SetMetaData(key, reference_img.GetMetaData(key))
        
        new_img = sitk.DICOMOrient(img, img_orient)
        sitk.WriteImage(new_img, filename, useCompression=True)
    
    def parse_obj(self, obj):
        if isinstance(obj, str):
            img = self.load_sitk_image(obj)
        elif isinstance(obj, np.ndarray):
            img = sitk.GetArrayFromImage(obj)
        elif isinstance(obj, sitk.Image):
            img = obj
        else:
            raise ValueError(f"Invalid image object: {obj}")
        return img
    
    def save_itk_keeping_header(self, img_obj, reference_img_obj, filename, img_orient='LPS') -> None:
        """
        Save an image array as a SimpleITK image.
        """

        img = self.parse_obj(img_obj)
        reference_img = self.parse_obj(reference_img_obj)

        self.save_itk_like_image(img, reference_img, filename, img_orient)
    
    def transfer_header_keeping_spacings(self, img_obj, reference_img_obj, filename) -> None:
        img = self.parse_obj(img_obj)
        reference_img = self.parse_obj(reference_img_obj)

        img.SetSpacing(reference_img.GetSpacing())
        img.SetOrigin(reference_img.GetOrigin())

        sitk.WriteImage(img, filename, useCompression=True)


    def load_image_array(self, filename) -> np.ndarray:
        """
        Load an image array from a file.

        Parameters:
            filename: The filename of the image.

        Returns:
            np.ndarray: The resulting image array.

        """
        img_array, _ = nrrd.read(filename)
        return img_array
    
    def load_sitk_image(self, filename) -> sitk.Image:
        """
        Load an image from a NIfTI file.

        Parameters:
            filename: The filename of the NIfTI file.

        Returns:
            sitk.Image: The resulting SimpleITK image.

        """
        img = sitk.ReadImage(filename)
        return img
        
