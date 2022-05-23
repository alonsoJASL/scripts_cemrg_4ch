# ---------------------------------------------------------------------------
#
# Python Script for Slicing during Segmentation using Seg3D (Version 2.2.3)
#
# ---------------------------------------------------------------------------

import os
import sys
import numpy
import nrrd
import itertools
from joblib import Parallel, delayed
import multiprocessing
import time
import math


# ---------------------------------------------------------------------------

def processVoxel(position):

    tmpI = numpy.uint8(0)

    # calculate rotated [cartesian] slicer coordinates
    rotO = numpy.matrix(position)-numpy.matrix(circCenter)
    rotP = rotationMatrix*rotO.T
    
    # calculate rotated [cylindrical] slicer coordinates
    rotZ = rotP[2]
    rotR = numpy.sqrt(rotP[0]**2+rotP[1]**2)

    # generate temporary slicer mask vector
    imgSpaM = numpy.amax([imgSpaX,imgSpaY,imgSpaZ])
    if ((rotZ >= -slicer_height/2) and (rotZ <= slicer_height/2) and (rotR <= radPPSA)):
        tmpI = numpy.uint8(1)

    return tmpI

# ---------------------------------------------------------------------------
#Inputs:
#---------------------------------------

imgSpaX = float(sys.argv[13])
imgSpaY = float(sys.argv[14])
imgSpaZ = float(sys.argv[15])

# store triangle corner nodes in vertex vectors
coordPPSA = numpy.array([(float(sys.argv[1])-0.5)*imgSpaX,(float(sys.argv[2])-0.5)*imgSpaY,(float(sys.argv[3])-0.5)*imgSpaZ])
coordPPSB = numpy.array([(float(sys.argv[4])-0.5)*imgSpaX,(float(sys.argv[5])-0.5)*imgSpaY,(float(sys.argv[6])-0.5)*imgSpaZ])
coordPPSC = numpy.array([(float(sys.argv[7])-0.5)*imgSpaX,(float(sys.argv[8])-0.5)*imgSpaY,(float(sys.argv[9])-0.5)*imgSpaZ])

# restore meta data for image
imgSizX = int(float(sys.argv[10]))
imgSizY = int(float(sys.argv[11]))
imgSizZ = int(float(sys.argv[12]))

imgMinX = float(sys.argv[16])
imgMinY = float(sys.argv[17])
imgMinZ = float(sys.argv[18])
slicerPPI = str(sys.argv[19])

proPath = sys.argv[20]

slicer_height = sys.argv[21]
slicer_radius = sys.argv[22]

#-------------------------------------

# process data and round to six digits
imgSpaX = round(imgSpaX,6)
imgSpaY = round(imgSpaY,6)
imgSpaZ = round(imgSpaZ,6)
imgMinX = round(imgMinX-imgSpaX/2.00,6)
imgMinY = round(imgMinY-imgSpaY/2.00,6)
imgMinZ = round(imgMinZ-imgSpaZ/2.00,6)

# generate dictionary with header information
header = {'keyvaluepairs': {}}
header['type'] = 'unsigned char'
header['sizes'] = [imgSizX,imgSizY,imgSizZ]
header['encoding'] = 'gzip'
header['spacings'] = [imgSpaX,imgSpaY,imgSpaZ]
header['dimension'] = 3
header['axis mins'] = [imgMinX,imgMinY,imgMinZ]
header['centerings'] = ['cell','cell','cell']

# calculate triangle edge vectors>
triSideA = coordPPSC-coordPPSB
triSideB = coordPPSC-coordPPSA
triSideC = coordPPSB-coordPPSA

# calculate geometrical parameters
tmpPlane = numpy.cross(triSideB,triSideC)
tmpLine1 = numpy.cross(triSideC,tmpPlane)
tmpLine2 = numpy.cross(triSideA,tmpPlane)
tmpPoint1 = (coordPPSC-coordPPSA)/2.00
tmpPoint2 = (coordPPSA+coordPPSB)/2.00

# solve linear equation system and calculate center
# lstsq instead of solve since coefficient matrix not square
coeffMat = numpy.column_stack((tmpLine1,-tmpLine2))
linSolve = numpy.linalg.lstsq(coeffMat,tmpPoint1)[0]
circCenter = tmpPoint2+linSolve[0]*tmpLine1

# import|calculate applied slicer radius
radPPS1 = numpy.linalg.norm(coordPPSA-circCenter)
radPPS2 = numpy.linalg.norm(coordPPSB-circCenter)
radPPS3 = numpy.linalg.norm(coordPPSC-circCenter)
radPPSC = numpy.amax([radPPS1,radPPS2,radPPS3])


# finalize slicer radius (in mm)
if (slicer_radius == 'None'):
    radPPSA = 1.5*radPPSC
else:
    radPPSA = float(slicer_radius)

if (slicer_height == 'None'):
    slicer_height = 2.0
else:
    slicer_height = float(slicer_height)


# calculate [cartesian] slicer coordinate system
axisZcar = tmpPlane/numpy.linalg.norm(tmpPlane)
axisYcar = numpy.cross([0,0,1],axisZcar)/numpy.linalg.norm(numpy.cross([0,0,1],axisZcar))
axisXcar = numpy.cross(axisYcar,axisZcar)/numpy.linalg.norm(numpy.cross(axisYcar,axisZcar))

# generate slicer coordinate rotation matrix
rotationMatrix = numpy.matrix([axisXcar,axisYcar,axisZcar])

# initialize image space vectors and arrays
voxX = numpy.arange(imgSpaX/2,imgSpaX*imgSizX,imgSpaX)
voxY = numpy.arange(imgSpaY/2,imgSpaY*imgSizY,imgSpaY)
voxZ = numpy.arange(imgSpaZ/2,imgSpaZ*imgSizZ,imgSpaZ)

# Create a cube containing the cylinder

radius_in_pixels = []
circCenter_in_pixels = []
lower_bound_in_pixels = []
upper_bound_in_pixels = []
starting_point = []
ending_point = []

# It was easier for me to work directly with the voxels

imgSpam = numpy.amin([imgSpaX,imgSpaY,imgSpaZ])

radius_in_pixels = radPPSA/imgSpam + 0.5

circCenter_in_pixels.append(math.floor(circCenter[0]/imgSpaX + 0.5))
circCenter_in_pixels.append(math.floor(circCenter[1]/imgSpaY + 0.5))
circCenter_in_pixels.append(math.floor(circCenter[2]/imgSpaZ + 0.5))

# The cube is between the center and 2 times the radius per each side. This can be improved.


lower_bound_in_pixels = [el - 1.1*max(radius_in_pixels,slicer_height/2) for el in circCenter_in_pixels]
lower_bound_in_pixels = [int(el) for el in lower_bound_in_pixels]

upper_bound_in_pixels = [el + 1.1*max(radius_in_pixels,slicer_height/2) for el in circCenter_in_pixels]
upper_bound_in_pixels = [int(el) for el in upper_bound_in_pixels]

#If lower_bound is the pixel 0, it should start in imgSpaX/2, to mimic the structure of voxX
starting_point.append(lower_bound_in_pixels[0]*imgSpaX + imgSpaX/2)
starting_point.append(lower_bound_in_pixels[1]*imgSpaY + imgSpaY/2)
starting_point.append(lower_bound_in_pixels[2]*imgSpaZ + imgSpaZ/2)

ending_point.append(upper_bound_in_pixels[0]*imgSpaX + imgSpaX/2)
ending_point.append(upper_bound_in_pixels[1]*imgSpaY + imgSpaY/2)
ending_point.append(upper_bound_in_pixels[2]*imgSpaZ + imgSpaZ/2)

# Just in case we are out of bounds

starting_point[0] = max(starting_point[0],voxX[0])
starting_point[1] = max(starting_point[1],voxY[0])
starting_point[2] = max(starting_point[2],voxZ[0])

ending_point[0] = min(ending_point[0],voxX[-1])
ending_point[1] = min(ending_point[1],voxY[-1])
ending_point[2] = min(ending_point[2],voxZ[-1])

mini_voxX = numpy.arange(starting_point[0],ending_point[0],imgSpaX)
mini_voxY = numpy.arange(starting_point[1],ending_point[1],imgSpaY)
mini_voxZ = numpy.arange(starting_point[2],ending_point[2],imgSpaZ)

# parallelized for loop

tmpI = Parallel(n_jobs=-1)(delayed(processVoxel)(position) for position in itertools.product(mini_voxX,mini_voxY,mini_voxZ))

small_image = numpy.reshape(tmpI,(len(mini_voxX),len(mini_voxY),len(mini_voxZ)))
whole_image = numpy.zeros((imgSizX,imgSizY,imgSizZ),dtype=numpy.uint8)

for i in range(len(mini_voxX)):
    for j in range(len(mini_voxY)):
        for k in range(len(mini_voxZ)):
            whole_image[int(lower_bound_in_pixels[0] + i), int(lower_bound_in_pixels[1] + j), int(lower_bound_in_pixels[2] + k)] = small_image[i,j,k]

nrrd.write(proPath+'/'+slicerPPI+'.nrrd',whole_image,header)

# ---------------------------------------------------------------------------

