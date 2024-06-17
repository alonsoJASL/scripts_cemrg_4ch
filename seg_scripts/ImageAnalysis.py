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
    
    def save_itk(self, img_array: np.ndarray, origin, spacing, filename, swap_axes=False) -> None:
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
        sitk.WriteImage(img, filename)

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
        
