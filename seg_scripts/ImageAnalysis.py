import nrrd
import copy
import numpy as np
import os
import SimpleITK as sitk
import string
import subprocess
import time
import multiprocessing as mp

from enum import Enum

ZERO_LABEL = 0
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

    def DIR(self, x):
        return os.path.join(self.path2points, x)
    
    def TMP(self, x):
        return os.path.join(self.path2points, "tmp", x)
    
    def set_debug(self, debug, pth2points):
        self.debug = debug
        self.path2points = pth2points
    
    def loc_mask(self, img_array: np.array):
        """
        Get the locations of the mask in an image array.
        """ 
        mask_ind = np.array(img_array.nonzero())
        return mask_ind

    def pad_image(self, img_array: np.array, pad_x=10, pad_y=10, pad_z=10, pad_value=0) -> np.array:
        """
        Pad an image array with specified values.

        Parameters:
            img_array (np.array): The input image array.
            pad_x (int): The amount of padding to add along the x-axis. Default is 10.
            pad_y (int): The amount of padding to add along the y-axis. Default is 10.
            pad_z (int): The amount of padding to add along the z-axis. Default is 10.
            pad_value (int): The value to use for padding. Default is 0.

        Returns:
            np.array: The padded image array.

        """
        constant_pad_values = ((pad_value, pad_value), (pad_value, pad_value), (pad_value, pad_value))
        padded_img_array = np.pad(img_array, ((pad_x, pad_x), (pad_y, pad_y), (pad_z, pad_z)), mode='constant', constant_values=constant_pad_values)
        return padded_img_array
    
    def distance_map(self, img: sitk.Image, label: int) -> sitk.Image:
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

        return DistMap

    def threshold_filter(self, img: sitk.Image, lower, upper) : 
        """
        Apply a threshold filter to an image.

        Parameters:
            img (sitk.Image): The input image.
            lower (int): The lower threshold value.
            upper (int): The upper threshold value.

        Returns:
            sitk.Image: The thresholded image.

        """
        threshold_filter = sitk.ThresholdImageFilter()
        threshold_filter.SetLower(lower)
        threshold_filter.SetUpper(upper)
        thresholded_img = threshold_filter.Execute(img)
        return thresholded_img

    def and_filter(self, imga_array: np.array, imgb_array: np.array, label_a, new_label) -> np.array:
        """
        Apply an 'and' filter to two image arrays.

        Parameters:
            imga_array (np.array): The first input image array.
            imgb_array (np.array): The second input image array.
            label_a (int): The label value in imga_array to compare against.
            new_label (int): The new label value to assign in imgb_array.

        Returns:
            np.array: The resulting image array after applying the 'and' filter.

        """
        imgb_indices = self.loc_mask(imgb_array)
        imgb_indices_trans = np.transpose(imgb_indices)
        # imgb_array_new = copy.deepcopy(imgb_array)

        imgb_array_new = np.where(imga_array[imgb_indices_trans[:,0], 
                                             imgb_indices_trans[:,1], 
                                             imgb_indices_trans[:,2]] == label_a, new_label, 0)
        return imgb_array_new

    def remove_filter(self, imga_array: np.array, imgb_array: np.array, label_remove) -> np.array:
        """
        Apply a mask to an image array, replacing the pixels that belong to the mask with a new value.

        Parameters:
            imga_array (np.array): The first input image array.
            imgb_array (np.array): The second input image array.
            label_remove: The value to assign to the pixels in imga_array that belong to the mask.

        Returns:
            np.array: The resulting image array after applying the mask and replacing the pixels.
        """
        imga_array_new = copy.deepcopy(imga_array)
        mask_indices = np.transpose(np.where(imgb_array != ZERO_LABEL))

        for n in mask_indices:
            test_value_a = imga_array_new[n[0], n[1], n[2]]
            if test_value_a == label_remove:
                imga_array_new[n[0], n[1], n[2]] = ZERO_LABEL
        
        return imga_array_new
    
    def add_masks(self, imga_array: np.array, imgb_array: np.array, newmask) -> np.array:
        """
        Apply a mask (imgb) to an image array without overriding any pixels that already belong to the image array.

        Parameters:
            imga_array (np.array): The first input image array.
            imgb_array (np.array): The second input image array.
            newmask: The value to assign to the pixels in imga_array that are not already part of the image array.

        Returns:
            np.array: The resulting image array after applying the mask.

        """
        
        # does not override any pixels that already belong to imga_array 
        imga_array_new = copy.deepcopy(imga_array)
        mask_indices = np.transpose(np.where(imgb_array != ZERO_LABEL))

        for n in mask_indices: 
            test_value_a = imga_array_new[n[0], n[1], n[2]]
            if test_value_a == ZERO_LABEL:
                imga_array_new[n[0], n[1], n[2]] = newmask

        return imga_array_new
    
    def add_masks_replace(self, imga_array: np.array, imgb_array: np.array, newmask) -> np.array:
        """
        Apply a mask to an image array, replacing the pixels that belong to the mask with a new value.

        Parameters:
            imga_array (np.array): The first input image array.
            imgb_array (np.array): The second input image array.
            newmask: The value to assign to the pixels in imga_array that belong to the mask.

        Returns:
            np.array: The resulting image array after applying the mask and replacing the pixels.

        """

        # overrides any pixels that already belong to a mask
        imga_array_new = copy.deepcopy(imga_array)
        mask_indices = np.transpose(np.where(imgb_array != ZERO_LABEL))

        imga_array_new[mask_indices[:, 0], mask_indices[:, 1], mask_indices[:, 2]] = newmask

        return imga_array_new
    
    def add_masks_replace_only(imga_array: np.array, imgb_array: np.array, newmask, only_override_this) -> np.array:
        """
        Apply a mask to an image array, replacing the pixels that belong to the mask with a new value.

        Parameters:
            imga_array (np.array): The first input image array.
            imgb_array (np.array): The second input image array.
            newmask: The value to assign to the pixels in imga_array that belong to the mask.
            only_override_this: The value of pixels in imga_array that should be overridden with the newmask.

        Returns:
            np.array: The resulting image array after applying the mask and replacing the pixels.
        """

        # only overrides pixels that already belong to a specific mask
        imga_array_new = copy.deepcopy(imga_array)
        mask_indices = np.transpose(np.where(imgb_array != ZERO_LABEL))

        for n in mask_indices:
            test_value_a = imga_array_new[n[0], n[1], n[2]]
            if test_value_a == ZERO_LABEL or test_value_a == only_override_this:
                imga_array_new[n[0], n[1], n[2]] = newmask
            
        return imga_array_new
    
    def add_masks_replace_except(imga_array: np.array, imgb_array: np.array, newmask, except_these: list) -> np.array:
        """
        Apply a mask to an image array, replacing the pixels that belong to the mask with a new value, except for specific values.

        Parameters:
            imga_array (np.array): The first input image array.
            imgb_array (np.array): The second input image array.
            newmask: The value to assign to the pixels in imga_array that belong to the mask.
            except_these (list): A list of values that should not be overridden with the newmask.

        Returns:
            np.array: The resulting image array after applying the mask and replacing the pixels, except for the specified values.

        """
        # overrides all pixels except those belonging to a given mask
        imga_array_new = copy.deepcopy(imga_array)
        mask_indices = np.transpose(np.where(imgb_array != ZERO_LABEL))

        for n in mask_indices:
            test_value_a = imga_array_new[n[0], n[1], n[2]]
            if test_value_a not in except_these:
                imga_array_new[n[0], n[1], n[2]] = newmask
        
        return imga_array_new
    
    def push_inside(self, img: sitk.Image, pusher_wall_label, pushed_wall_label, pushed_bp_label, pushed_wt) -> np.array:
        pusher_wall_dist_map = self.distance_map(img, pusher_wall_label)
        new_pushed_wall = self.threshold_filter(pusher_wall_dist_map, 0, pushed_wt)

        if self.debug:
            sitk.WriteImage(new_pushed_wall, self.TMP("pushed_wall.nrrd"))
        
        img_array = sitk.GetArrayFromImage(img)
        new_pushed_wall_array = sitk.GetArrayFromImage(new_pushed_wall)
        new_pushed_wall_array = self.and_filter(img_array, new_pushed_wall_array, pushed_bp_label, pushed_wall_label)

        img_array = self.add_masks_replace(img_array, new_pushed_wall_array, pushed_wall_label)

        return img_array
    
    def push_ring_inside(self, img: sitk.Image, pusher_wall_label, pushed_wall_label, pushed_bp_label, pushed_wt) -> np.array:
        pusher_wall_dist_map = self.distance_map(img, pusher_wall_label)
        new_pushed_wall = self.threshold_filter(pusher_wall_dist_map, 0, pushed_wt)

        if self.debug:
            sitk.WriteImage(new_pushed_wall, self.TMP("pushed_wall.nrrd"))
        
        img_array = sitk.GetArrayFromImage(img)
        new_pushed_wall_array = sitk.GetArrayFromImage(new_pushed_wall)

        new_pushed_wall_array = self.and_filter(img_array, new_pushed_wall_array, pushed_bp_label, pushed_wall_label)
        img_array = self.add_masks(img_array, new_pushed_wall_array, pushed_wall_label)

        return img_array
    
    def connected_component(self, imga: sitk.Image, seed: list, layer: int, keep=False) -> np.array : 
        # cast seed as list of int
        seed_int = list(map(int, seed))
        new_layer = layer + 100
        CC = sitk.ConnectedCommponent(imga, seedList=seed_int, lower=layer, upper=layer, replaceValue=new_layer)
        if self.debug:
            sitk.WriteImage(CC, self.TMP("CC.nrrd"))

        imga_array = sitk.GetArrayFromImage(imga)
        CC_array = sitk.GetArrayFromImage(CC)

        if keep:
            imga_array = self.remove_filter(imga_array, imga_array, layer)

        imgb_array = self.add_masks_replace(imga_array, CC_array, ZERO_LABEL)

        return imgb_array
    
    def connected_component_keep(self, imga: sitk.Image, seed: list, layer: int) -> np.array:
        return self.connected_component(imga, seed, layer, True)
    
    # helper functions 
    def array2itk(self, img_array: np.array, origin, spacing) -> sitk.Image:
        """
        Convert an image array to a SimpleITK image.

        Parameters:
            img_array (np.array): The input image array.
            origin: The origin of the image.
            spacing: The spacing of the image.

        Returns:
            sitk.Image: The resulting SimpleITK image.

        """
        img = sitk.GetImageFromArray(img_array)
        img.SetOrigin(origin)
        img.SetSpacing(spacing)
        return img
    
    def save_itk(self, img_array: np.array, origin, spacing, filename, swap_axes=False) -> None:
        """
        Save an image array as a SimpleITK image.

        Parameters:
            img_array (np.array): The input image array.
            origin: The origin of the image.
            spacing: The spacing of the image.
            filename: The filename to save the image as.

        """
        if swap_axes:
            img_array = np.swapaxes(img_array, 0, 2)
        
        img = self.array2itk(img_array, origin, spacing)
        sitk.WriteImage(img, filename)

    def load_image_array(self, filename) -> np.array:
        """
        Load an image array from a file.

        Parameters:
            filename: The filename of the image.

        Returns:
            np.array: The resulting image array.

        """
        img_array, _ = nrrd.read(filename)
        return img_array
    
    def load_nii(self, filename) -> sitk.Image:
        """
        Load an image from a NIfTI file.

        Parameters:
            filename: The filename of the NIfTI file.

        Returns:
            sitk.Image: The resulting SimpleITK image.

        """
        img = sitk.ReadImage(filename)
        return img
        