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

# from scipy import ndimage

def pad_image(img_array):
  padded_img_array = np.pad(img_array, ((10,10),(10,10),(10,10)), 'constant', constant_values=((0,0),(0,0),(0,0)))

  return padded_img_array


def push_inside(path2points,img_nrrd,pusher_wall_lab,pushed_wall_lab,pushed_BP_lab,pushed_WT):
  # distance map of the pusher wall
  pusher_wall_DistMap = distance_map(img_nrrd,pusher_wall_lab)

  # threshold of the pusher wall
  new_pushed_wall = threshold_filter(pusher_wall_DistMap,0,pushed_WT)
  sitk.WriteImage(new_pushed_wall,path2points+'/tmp/new_pushed_wall.nrrd',True)
  
  # arrays of the whole seg and the new wall section
  img_array, header = nrrd.read(img_nrrd)
  new_pushed_wall_array, header = nrrd.read(path2points+'/tmp/new_pushed_wall.nrrd')

  new_pushed_wall_array = and_filter(img_array,new_pushed_wall_array,pushed_BP_lab,pushed_wall_lab)
  img_array = add_masks_replace(img_array,new_pushed_wall_array,pushed_wall_lab)

  return img_array

def push_ring_inside(path2points,img_nrrd,pusher_wall_lab,pushed_wall_lab,pushed_BP_lab,pushed_WT):
  # distance map of the pusher wall
  pusher_wall_DistMap = distance_map(img_nrrd,pusher_wall_lab)

  # threshold of the pusher wall
  new_pushed_wall = threshold_filter(pusher_wall_DistMap,0,pushed_WT)
  sitk.WriteImage(new_pushed_wall,path2points+'/tmp/new_pushed_wall.nrrd',True)
  
  # arrays of the whole seg and the new wall section
  img_array, header = nrrd.read(img_nrrd)
  new_pushed_wall_array, header = nrrd.read(path2points+'/tmp/new_pushed_wall.nrrd')

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
  thresh = sitk.ThresholdImageFilter()
  thresh.SetLower(lower)
  thresh.SetUpper(upper)
  thresh.SetOutsideValue(0)
  thresh_img = thresh.Execute(img_itk)
  return thresh_img

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

def connected_component(imga_nrrd,seed,layer,path2points):
  imga = sitk.ReadImage(imga_nrrd)
  CC = sitk.ConnectedThreshold(imga, seedList=[(int(seed[0]),int(seed[1]),int(seed[2]))], lower=layer, upper=layer, replaceValue = layer+100)
  sitk.WriteImage(CC,path2points+'/tmp/CC.nrrd',True)
  CC_nrrd = path2points+'/tmp/CC.nrrd'
  imga_array, header1 = nrrd.read(imga_nrrd)
  CC_array, header2 = nrrd.read(CC_nrrd)
  imgb = add_masks_replace(imga_array, CC_array, 0)
  return imgb

def connected_component_keep(imga_nrrd,seed,layer,path2points):
  imga = sitk.ReadImage(imga_nrrd)
  CC = sitk.ConnectedThreshold(imga, seedList=[(int(seed[0]),int(seed[1]),int(seed[2]))], lower=layer, upper=layer, replaceValue = layer+100)
  sitk.WriteImage(CC,path2points+'/tmp/CC.nrrd',True)
  CC_nrrd = path2points+'/tmp/CC.nrrd'
  imga_array, header1 = nrrd.read(imga_nrrd)
  CC_array, header2 = nrrd.read(CC_nrrd)
  imga_array = remove_filter(imga_array,imga_array,layer)
  imgb_array = add_masks_replace(imga_array, CC_array, layer)
  return imgb_array

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

