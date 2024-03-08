import numpy as np
import pydicom as dicom
import os
import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description='To run: python3 check_slices.py [image_folder]')
parser.add_argument("image_folder")
args = parser.parse_args()
FOLDER=args.image_folder

imageList = os.listdir(FOLDER)
print(imageList)

slice_positions=[]

for i, slice in enumerate(imageList):
	ds = dicom.dcmread(FOLDER+slice)
	#print(ds)
	image_position = ds[0x0020, 0x0032]
	slice_positions.append(float(image_position[2]))

print(slice_positions)

# z_max = max(slice_positions)
# z_min = min(slice_positions)

# num_slices = len(slice_positions)

# z_spacing = (z_max-z_min)/num_slices

# print("Voxel spacing (z direction) = "+str(z_spacing))

# sortedImageList = os.listdir(FOLDER)
# ds = dicom.dcmread(FOLDER+"image_0.dcm")
# image_position = ds[0x0020, 0x0032]
# print("Position of image_0.dcm = "+str(image_position))

# ds = dicom.dcmread(FOLDER+"image_"+str(num_slices-1)+".dcm")
# image_position = ds[0x0020, 0x0032]
# print("Position of image_"+str(num_slices-1)+".dcm = "+str(image_position))


retain_slices = []
remove_slices = []

for i in slice_positions:
	if i not in retain_slices:
		retain_slices.append(i)
	else:
		remove_slices.append(i)

# # remove_slices.sort()
# # retain_slices.sort()

# # print(remove_slices)
# # print(retain_slices)

# # check_against = np.arange(1388.5,1521,0.5).tolist()

# # if retain_slices == check_against:
# # 	print('The lists are identical')
# # else:
# # 	print('The lists are NOT idential')

new_order = np.argsort(slice_positions)
print(np.sort(slice_positions))
print(new_order)
unsortedFolder = FOLDER+'/unsorted/'
sortedFolder = FOLDER+'/sorted/'
os.system('mkdir '+unsortedFolder)
os.system('cp '+FOLDER+'/* '+unsortedFolder)
os.system('rm '+FOLDER+'/* ')
os.system('mkdir '+sortedFolder)

for i, slice in enumerate(imageList):
	idx = new_order[i]
	ds = dicom.dcmread(unsortedFolder+imageList[idx])
	ds.save_as(sortedFolder+"/image_"+str(i)+'.dcm')

