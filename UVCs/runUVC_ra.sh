#!/bin/bash

clear

# --------------------------------------------------------------------------------------------------------------------
heart_folder=$1
MESHFOLDER="${heart_folder}/surfaces_uvc_RA/ra"
cmd="cp /data/Dropbox/af_hearts/h_template/etags_ra.sh ${MESHFOLDER}/etags.sh"
echo $cmd
eval $cmd

cmd="mguvc --ID=$MESH/UVC_ek --model-name $MESHFOLDER/ra --input-model lv --output-model lv --np 20 --tags-file $MESHFOLDER/etags.sh --output-dir $MESHFOLDER/uvc/ --custom-apex"

echo $cmd
eval $cmd

# --------------------------------------------------------------------------------------------------------------------

cmd="GlVTKConvert -m $MESHFOLDER/ra -n $MESHFOLDER/uvc/ra.uvc_phi.dat -n $MESHFOLDER/uvc/ra.uvc_z.dat -n $MESHFOLDER/uvc/ra.uvc_ven.dat -n $MESHFOLDER/uvc/ra.uvc_rho.dat -o $MESHFOLDER/uvc/uvc --trim-names"

echo $cmd
eval $cmd

# --------------------------------------------------------------------------------------------------------------------

 

