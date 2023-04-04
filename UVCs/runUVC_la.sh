#!/bin/bash

clear

# --------------------------------------------------------------------------------------------------------------------
heart_folder=$1
MESHFOLDER="${heart_folder}/surfaces_uvc_LA/la"
cmd="cp /data/Dropbox/af_hearts/h_template/etags_la.sh ${MESHFOLDER}/etags.sh"
echo $cmd
eval $cmd

cmd="mguvc --ID=$MESH/UVC_ek --model-name $MESHFOLDER/la --input-model lv --output-model lv --np 20 --tags-file $MESHFOLDER/etags.sh --output-dir $MESHFOLDER/uvc/ --laplace-solution --custom-apex"

echo $cmd
eval $cmd

# --------------------------------------------------------------------------------------------------------------------

cmd="GlVTKConvert -m $MESHFOLDER/la -n $MESHFOLDER/uvc/la.uvc_phi.dat -n $MESHFOLDER/uvc/la.uvc_z.dat -n $MESHFOLDER/uvc/la.uvc_ven.dat -n $MESHFOLDER/uvc/la.uvc_rho.dat -o $MESHFOLDER/uvc/uvc --trim-names"

echo $cmd
eval $cmd

# --------------------------------------------------------------------------------------------------------------------

 

