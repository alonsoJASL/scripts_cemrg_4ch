#!/bin/bash

clear

# conda activate

patient_folder="/data/Dropbox/Segmentations/2016111001EP/heart_example"
				

meshname="myocardium"

################################################################################
# base
################################################################################
# mesh="${patient_folder}/$meshname"
mesh="${patient_folder}/$meshname"
surf_folder="${patient_folder}/surfaces_uvc/"


################################################################################
# apex
################################################################################
segmentation="${patient_folder}/myocardium.nrrd"
lv_cavity=1
base=3
pts="${patient_folder}/$meshname.pts"
vtx="${surf_folder}/BiV.epi.vtx"

pickapex $segmentation $lv_cavity $base $pts $vtx > "${surf_folder}/BiV.apex.vtx"