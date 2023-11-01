#!/usr/bin/env python3
import nrrd
import copy
import numpy as np
import os
import SimpleITK as sitk
import string
import subprocess
import time
import multiprocessing as mp
import pydicom as dicom 
from scipy import ndimage
from enum import Enum

class MaskOperationMode(Enum):
  REPLACE_EXCEPT = 1
  REPLACE_ONLY = 2
  REPLACE = 3
  ADD = 4

def get_origin_from_dicom(list_of_files: list) -> np.ndarray :
  """
  Returns the origin of the image as a numpy array.
  Args:
      list_of_files (list): A list of file paths representing DICOM files.
  Returns:
      np.ndarray: A numpy array representing the origin of the image.
  """
  
  ds = dicom.dcmread(list_of_files[0])
  image_origin_option_A = np.array(ds[0x0020, 0x0032].value,dtype=float)
  ds = dicom.dcmread(list_of_files[-1])
  image_origin_option_B = np.array(ds[0x0020, 0x0032].value,dtype=float)

  if image_origin_option_A[2] < image_origin_option_B[2]:
    image_origin = image_origin_option_A
  else:
    image_origin = image_origin_option_B

  return image_origin

def get_image_spacing(path_to_seg:str) :
  seg_array, header = nrrd.read(path_to_seg)
  
  try : 
    img_spacing = header['spacings']
  
  except Exception :
    img_spacing = header['space directions']
    img_spacing = [img_spacing[0,0],img_spacing[1,1],img_spacing[2,2]]
  
  return img_spacing

  # try:
  # 	imgSpa = header['spacings']
  #   print(imgSpa)
  # except Exception:
  # imgSpa = header['space directions']
  #   imgSpa = [imgSpa[0,0],imgSpa[1,1],imgSpa[2,2]]
  #   print(imgSpa)


def convert_to_nrrd(base_directory: str, filename: str):
  strt = 4
  if 'nii.gz' in filename:
    strt = 7
  elif 'nii' not in filename:
    filename += '.nii'

  path_to_nii = os.path.join(base_directory, filename)
  path_to_save = os.path.join(base_directory, f'{filename[:-strt]}.nrrd')
  im = sitk.ReadImage(path_to_nii)
  sitk.WriteImage(im, path_to_save)

  return path_to_save
  

def pad_image(img_array):
  padded_img_array = np.pad(img_array, ((10,10),(10,10),(10,10)), 'constant', constant_values=((0,0),(0,0),(0,0)))

  return padded_img_array


def push_inside(path2points,img_nrrd,pusher_wall_lab,pushed_wall_lab,pushed_BP_lab,pushed_WT):
  output_path = os.path.join(path2points, 'tmp', 'pushed_wall.nrrd')
  # distance map of the pusher wall
  pusher_wall_DistMap = distance_map(img_nrrd,pusher_wall_lab)

  # threshold of the pusher wall
  new_pushed_wall = threshold_filter(pusher_wall_DistMap,0,pushed_WT)
  sitk.WriteImage(new_pushed_wall,output_path,True)
  
  # arrays of the whole seg and the new wall section
  img_array, _ = nrrd.read(img_nrrd)
  new_pushed_wall_array, _ = nrrd.read(output_path)

  new_pushed_wall_array = and_filter(img_array,new_pushed_wall_array,pushed_BP_lab,pushed_wall_lab)
  img_array = add_masks_replace(img_array,new_pushed_wall_array,pushed_wall_lab)

  return img_array

def push_ring_inside(path2points,img_nrrd,pusher_wall_lab,pushed_wall_lab,pushed_BP_lab,pushed_WT):
  output_path = os.path.join(path2points, 'tmp', 'pushed_wall.nrrd')
  # distance map of the pusher wall
  pusher_wall_DistMap = distance_map(img_nrrd,pusher_wall_lab)

  # threshold of the pusher wall
  new_pushed_wall = threshold_filter(pusher_wall_DistMap,0,pushed_WT)
  sitk.WriteImage(new_pushed_wall,output_path,True)
  
  # arrays of the whole seg and the new wall section
  img_array, _ = nrrd.read(img_nrrd)
  new_pushed_wall_array, _ = nrrd.read(output_path)

  new_pushed_wall_array = and_filter(img_array,new_pushed_wall_array,pushed_BP_lab,pushed_wall_lab)
  img_array = add_masks(img_array,new_pushed_wall_array,pushed_wall_lab)

  return img_array

def and_filter(imga_array,imgb_array,label_a,new_label):
  # looks at everywhere in image_a and image_b that has label_a and replaces with new_label
  newmask_ind=loc_mask(imgb_array)
  newmask_ind_trans=np.transpose(newmask_ind)

  imgb_array_new = copy.deepcopy(imgb_array)

  for i,n in enumerate(newmask_ind_trans):
    A = imga_array[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]
    if A == label_a :
      imgb_array_new[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]] = new_label
    else:
      imgb_array_new[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]] = 0
  return imgb_array_new 

def remove_filter(imga_array,imgb_array,label_remove):
  # imga = seg, imgb = mask
  imga_array_new = copy.deepcopy(imga_array)

  newmask_ind=loc_mask(imgb_array)
  newmask_ind_trans=np.transpose(newmask_ind)
  # set the new mask values
  for i,n in enumerate(newmask_ind_trans):
    A = imga_array_new[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]
    if A == label_remove:
      imga_array_new[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]= 0;
  return imga_array_new

def threshold_filter_nrrd(img_nrrd,lower,upper):
  img_itk = sitk.ReadImage(img_nrrd)
  return threshold_filter(img_itk,lower,upper)

def threshold_filter(img_itk,lower,upper):
  thresh = sitk.ThresholdImageFilter()
  thresh.SetLower(lower)
  thresh.SetUpper(upper)
  thresh.SetOutsideValue(0)
  thresh_img = thresh.Execute(img_itk)
  return thresh_img

def distance_map(img_nrrd,label):
  img_itk = threshold_filter_nrrd(img_nrrd,label,label)
  distance_map = sitk.DanielssonDistanceMapImageFilter()
  distance_map.InputIsBinaryOff()
  distance_map.SquaredDistanceOff()
  distance_map.UseImageSpacingOff()
  DistMap = distance_map.Execute(img_itk)
  return DistMap

def mask_plane_creator_alternative(seg_nrrd,origin,spacing,points,plane_name,slicer_radius, slicer_height, segPath, scriptsPath):
  # used when header has different labels
  seg_array, header = nrrd.read(seg_nrrd)
  imgMin = origin
  imgSpa = spacing
  imgSiz = header['sizes']
  imgDim = str(len(imgSiz))
  tmpPara = subprocess.check_output(['python',scriptsPath+'/postSlicer_optimised.py',\
    str(points[0]),str(points[1]),str(points[2]),\
    str(points[3]),str(points[4]),str(points[5]),\
    str(points[6]),str(points[7]),str(points[8]),\
    str(imgSiz[0]),str(imgSiz[1]),str(imgSiz[2]),\
    str(imgSpa[0]),str(imgSpa[1]),str(imgSpa[2]),\
    str(imgMin[0]),str(imgMin[1]),str(imgMin[2]),\
    plane_name,segPath,str(slicer_height),str(slicer_radius)])


def mask_plane_creator(seg_nrrd,points,plane_name,slicer_radius, slicer_height, segPath, scriptsPath):
  
  seg_array, header = nrrd.read(seg_nrrd)
  imgMin = header['axis mins']
  imgSpa = header['spacings']
  imgSiz = header['sizes']
  imgDim = str(len(imgSiz))
  tmpPara = subprocess.check_output(['python',scriptsPath+'/postSlicer_optimised.py',\
    str(points[0]),str(points[1]),str(points[2]),\
    str(points[3]),str(points[4]),str(points[5]),\
    str(points[6]),str(points[7]),str(points[8]),\
    str(imgSiz[0]),str(imgSiz[1]),str(imgSiz[2]),\
    str(imgSpa[0]),str(imgSpa[1]),str(imgSpa[2]),\
    str(imgMin[0]),str(imgMin[1]),str(imgMin[2]),\
    plane_name,segPath,str(slicer_height),str(slicer_radius)])
  
def connected_component_full(imga_nrrd, seed, layer, path2points, to_keep=False) :
  imga = sitk.ReadImage(imga_nrrd)
  CC_nrrd_path = os.path.join(path2points,'tmp','CC.nrrd')

  CC = sitk.ConnectedThreshold(imga, seedList=[(int(seed[0]),int(seed[1]),int(seed[2]))], lower=layer, upper=layer, replaceValue = layer+100)
  sitk.WriteImage(CC,CC_nrrd_path,True)
  imga_array, _ = nrrd.read(imga_nrrd)
  CC_array, _ = nrrd.read(CC_nrrd_path)

  label_to_replace = 0
  if to_keep :
    imga_array = remove_filter(imga_array,imga_array,layer)
    label_to_replace = layer

  imgb = add_masks_replace(imga_array, CC_array, label_to_replace)
  return imgb

def connected_component(imga_nrrd,seed,layer,path2points):
  return connected_component_full(imga_nrrd,seed,layer,path2points,False)

def connected_component_keep(imga_nrrd,seed,layer,path2points):
  return connected_component_full(imga_nrrd,seed,layer,path2points,True)

def process_mask(imga: np.ndarray, imgb: np.ndarray, newmask: int, operation_mode: MaskOperationMode, forbid_changes=None):
  """
  Process the mask on the given image based on the specified operation mode.
  Args:
      imga (numpy.ndarray): The original image.
      imgb (numpy.ndarray): The mask image.
      newmask (int): The new mask value.
      operation_mode (MaskOperationMode): The operation mode for processing the mask.
      forbid_changes (list, optional): The list of values that should not be changed. Defaults to None.
  Returns:
      numpy.ndarray: The processed image.
  """
  if imga.shape != imgb.shape:
    raise ValueError("imga and imgb must have the same shape.")
  
  if forbid_changes is None:
    forbid_changes = [] 

  imga_new = imga.copy(deep=True)
  newmask_ind = loc_mask(imgb)
  newmask_ind_trans = np.transpose(newmask_ind)

  for i, n in enumerate(newmask_ind_trans):
    i_0 = newmask_ind_trans[i][0]
    i_1 = newmask_ind_trans[i][1]
    i_2 = newmask_ind_trans[i][2]

    A = imga_new[i_0, i_1, i_2]
    if operation_mode == MaskOperationMode.REPLACE_EXCEPT and A not in forbid_changes:
        imga_new[i_0, i_1, i_2] = newmask
    elif operation_mode == MaskOperationMode.REPLACE_ONLY and A in forbid_changes:
        imga_new[i_0, i_1, i_2] = newmask
    elif operation_mode == MaskOperationMode.REPLACE:
        imga_new[i_0, i_1, i_2] = newmask
    elif operation_mode == MaskOperationMode.NO_OVERRIDE and A == 0:
        imga_new[i_0, i_1, i_2] = newmask
  return imga_new

def add_masks_replace_except(imga, imgb, newmask, forbid_change):
  # overrides all pixels except those belonging to a given mask
  newmask_ind=loc_mask(imgb)
  newmask_ind_trans=np.transpose(newmask_ind)
  # set the new mask values
  for i,n in enumerate(newmask_ind_trans):
    A = imga[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]
    if A == forbid_change:
      pass
    else:
      imga[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]= newmask;
  return imga

def add_masks_replace_except_2(imga, imgb, newmask, forbid_change1, forbid_change2):
  # overrides all pixels except those belonging to a given mask
  newmask_ind=loc_mask(imgb)
  newmask_ind_trans=np.transpose(newmask_ind)
  # set the new mask values
  for i,n in enumerate(newmask_ind_trans):
    A = imga[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]
    if A == forbid_change1:
      pass
    elif A == forbid_change2:
      pass
    else:
      imga[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]= newmask;
  return imga

def add_masks_replace_except_3(imga, imgb, newmask, forbid_change1, forbid_change2, forbid_change3):
  # overrides all pixels except those belonging to a given mask
  newmask_ind=loc_mask(imgb)
  newmask_ind_trans=np.transpose(newmask_ind)
  # set the new mask values
  for i,n in enumerate(newmask_ind_trans):
    A = imga[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]
    if A == forbid_change1:
      pass
    elif A == forbid_change2:
      pass
    elif A == forbid_change3:
      pass
    else:
      imga[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]= newmask;
  return imga

def add_masks_replace_except_4(imga, imgb, newmask, forbid_change1, forbid_change2, forbid_change3, forbid_change4):
  # overrides all pixels except those belonging to a given mask
  newmask_ind=loc_mask(imgb)
  newmask_ind_trans=np.transpose(newmask_ind)
  # set the new mask values
  for i,n in enumerate(newmask_ind_trans):
    A = imga[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]
    if A == forbid_change1:
      pass
    elif A == forbid_change2:
      pass
    elif A == forbid_change3:
      pass
    elif A == forbid_change4:
      pass
    else:
      imga[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]= newmask;
  return imga

def add_masks_replace_only(imga, imgb, newmask, change_only):
  # only overrides pixels that already belong to a specific mask

  imga_new = copy.deepcopy(imga)

  newmask_ind=loc_mask(imgb)
  newmask_ind_trans=np.transpose(newmask_ind)
  # set the new mask values
  for i,n in enumerate(newmask_ind_trans):
    A = imga_new[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]
    if A == 0:
      imga_new[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]= newmask;
    elif A == change_only:
      imga_new[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]= newmask;
  return imga_new

def add_masks_replace(imga, imgb, newmask):
  # overrides any pixels that already belong to a mask

  imga_new = copy.deepcopy(imga)

  newmask_ind=loc_mask(imgb)
  # set the new mask values
  imga_new[newmask_ind[0], newmask_ind[1], newmask_ind[2]]= newmask;
  return imga_new

def add_masks(imga, imgb, newmask):
  # does not override any pixels that already belong to a mask

  imga_new = copy.deepcopy(imga)

  newmask_ind=loc_mask(imgb)
  newmask_ind_trans=np.transpose(newmask_ind)
  # set the new mask values
  for i,n in enumerate(newmask_ind_trans):
    A = imga_new[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]
    if A == 0:
      imga_new[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]= newmask;
  return imga_new

def loc_mask(image_array): 
  mask_ind=np.array(image_array.nonzero())
  return mask_ind

def add_image(imga, origa, imgb, origb, spacb, maska=1, maskb=2):
  # Adds 2 masks together, if they have different origins, we need to account for that - here we are assuming that the spacing is the same
  # If we want to remove maskb from mask1, set maskb value to 0
  # Find the minimum bounds box of 2 images as the new origin of the combined image
  relOffset=np.minimum(origa, origb)
  # readjust the indices to the new origins of the image
  imga_offset=origa-relOffset  
  imgb_offset=origb-relOffset
  mask_ind_a=find_maskloc(imga, spacb, imga_offset)
  mask_ind_b=find_maskloc(imgb, spacb, imgb_offset)
  # Find the upper bound of the image (image size/shape)
  c=np.concatenate((mask_ind_a,mask_ind_b),1)   
  newImage=np.zeros((c.max(1)+1))
  # set the new mask values 
  newImage[mask_ind_a[0], mask_ind_a[1], mask_ind_a[2]]=maska; 
  newImage[mask_ind_b[0], mask_ind_b[1], mask_ind_b[2]]=maskb;
  return newImage, relOffset

def array2itk(image_array, origin, spacing): 
  itkimage = sitk.GetImageFromArray(image_array, isVector=False)
  # origin = origin[::-1]
  # spacing = spacing[::-1]
  itkimage.SetSpacing(spacing)
  itkimage.SetOrigin(origin)
  return itkimage

def dilate_image(image_array, pad, orig, spac):
  # pad the image with zeros all around (make sure new image array is large enough to hold the padded image)
  padimage=np.pad(image_array, ((pad, pad), (pad, pad), (pad, pad)), 'constant', constant_values=((0,0),(0,0),(0,0)))
  struct1 = ndimage.generate_binary_structure(3, 2)
  # dilate the image by struct 
  newimage=ndimage.binary_dilation(padimage, structure=struct1,iterations=pad).astype(image_array.dtype)
  neworig=orig-(pad*spac)
  return (newimage,padimage, neworig)

def erode_image(image_array, pad):
  # pad the image with zeros all around (make sure new image array is large enough to hold the padded image)
  struct1 = ndimage.generate_binary_structure(3, 1)
  # dilate the image by struct 
  newimage=ndimage.binary_erosion(image_array, structure=struct1,iterations=pad).astype(image_array.dtype)
  return (newimage)

def find_maskloc(image_array,spacing,img_offset): 
  origin_ind=(img_offset/spacing)
  origin_ind.round(); 
  mask_ind=np.array(image_array.nonzero())
  mask_ind[0]+=int(origin_ind.round()[0]); 
  mask_ind[1]+=int(origin_ind.round()[1]); 
  mask_ind[2]+=int(origin_ind.round()[2]); 
  return mask_ind

def itk2array(itkimage): 
  # Convert the image to a  numpy array first and then shuffle the dimensions to get axis in the order z,y,x
  image_array = sitk.GetArrayFromImage(itkimage)
  # Read the origin of the ct_scan, will be used to convert the coordinates from world to voxel and vice vers  
  origin = np.array(list(reversed(itkimage.GetOrigin())))
  # Read the spacing along each dimension
  spacing = np.array(list(reversed(itkimage.GetSpacing())))
  return (image_array, origin, spacing)

# read in mhd image
def load_itk(filename):
  # Reads the image using SimpleITK
  itkimage = sitk.ReadImage(filename)
  # Convert the image to a  numpy array first and then shuffle the dimensions to get axis in the order z,y,x
  image_array = sitk.GetArrayFromImage(itkimage)
  # Read the origin of the ct_scan, will be used to convert the coordinates from world to voxel and vice vers  
  origin = np.array(list(reversed(itkimage.GetOrigin())))
  # Read the spacing along each dimension
  spacing = np.array(list(reversed(itkimage.GetSpacing())))
  return (image_array, origin, spacing)

def rotation2unity(v):

  theta_x = np.arctan(v[1]/v[2])
  R_x = np.array( [[1, 0, 0 ],[ 0, np.cos(theta_x), -np.sin(theta_x)],[ 0, np.sin(theta_x), np.cos(theta_x)]])
  v_x = np.dot(R_x,v.reshape(3,1)).reshape(3)
   
  theta_y = np.arctan(-v_x[0]/v_x[2]);
  R_y = np.array( [[np.cos(theta_y), 0, np.sin(theta_y)],[ 0, 1, 0],[-np.sin(theta_y), 0, np.cos(theta_y)]]);
  R = np.matmul(R_y,R_x)
  return R

def save_itk(image_array, origin, spacing, filename):
  # always do np.swapaxes(seg_array,0,2) before using save_itk
  itkimage=array2itk(image_array, origin, spacing)
  sitk.WriteImage(itkimage, filename, True)

