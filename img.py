#!/usr/bin/env python3

import SimpleITK as sitk
import numpy as np
from scipy import ndimage

def add_masks_replace_only(imga, imgb, newmask, change_only):
  # only overrides pixels that already belong to a specific mask
  newmask_ind=loc_mask(imgb)
  newmask_ind_trans=np.transpose(newmask_ind)
  # set the new mask values
  for i,n in enumerate(newmask_ind_trans):
    A = imga[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]
    if A == 0:
      imga[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]= newmask;
    elif A == change_only:
      imga[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]= newmask;
  return imga

def add_masks_replace(imga, imgb, newmask):
  # overrides any pixels that already belong to a mask
  newmask_ind=loc_mask(imgb)
  # set the new mask values
  imga[newmask_ind[0], newmask_ind[1], newmask_ind[2]]= newmask;
  return imga

def add_masks(imga, imgb, newmask):
  # does not override any pixels that already belong to a mask
  newmask_ind=loc_mask(imgb)
  newmask_ind_trans=np.transpose(newmask_ind)
  # set the new mask values
  for i,n in enumerate(newmask_ind_trans):
    A = imga[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]
    if A == 0:
      imga[newmask_ind_trans[i][0], newmask_ind_trans[i][1], newmask_ind_trans[i][2]]= newmask;
  return imga

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
  itkimage=array2itk(image_array, origin, spacing)
  sitk.WriteImage(itkimage, filename, True)

