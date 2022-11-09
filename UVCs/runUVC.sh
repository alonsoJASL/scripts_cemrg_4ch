#!/bin/bash

clear

# --------------------------------------------------------------------------------------------------------------------
heart_folder=$1
MESHFOLDER="${heart_folder}/surfaces_uvc/BiV/"

cmd="cp /data/Dropbox/af_hearts/h_template/etags.sh ${MESHFOLDER}/etags.sh"
eval $cmd

cmd="mguvc --ID=$MESH/UVC_ek --model-name $MESHFOLDER/BiV --input-model biv --output-model biv --np 20 --tags-file $MESHFOLDER/etags.sh --output-dir $MESHFOLDER/uvc/ --laplace-solution"
echo $cmd
eval $cmd

# --------------------------------------------------------------------------------------------------------------------

cmd="GlVTKConvert -m $MESHFOLDER/BiV -n $MESHFOLDER/uvc/BiV.uvc_phi.dat -n $MESHFOLDER/uvc/BiV.uvc_z.dat -n $MESHFOLDER/uvc/BiV.uvc_ven.dat -n $MESHFOLDER/uvc/BiV.uvc_rho.dat -o $MESHFOLDER/uvc/uvc --trim-names"
echo $cmd
eval $cmd

# --------------------------------------------------------------------------------------------------------------------

 
# --------------------------------------------------------------------------------------------------------------------

cmd="GlVTKConvert -m $MESHFOLDER/BiV -n $MESHFOLDER/uvc/BiV.sol_apba_lap.dat -n $MESHFOLDER/uvc/BiV.sol_rvendo_lap.dat -n $MESHFOLDER/uvc/BiV.sol_endoepi_lap.dat -n $MESHFOLDER/uvc/BiV.sol_lvendo_lap.dat -o $MESHFOLDER/uvc/laplace --trim-names"
echo $cmd
eval $cmd

# --------------------------------------------------------------------------------------------------------------------

 
