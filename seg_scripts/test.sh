#!/bin/bash

clear

# -----------------------------------------------------------
RESOLUTION=0.15
# -----------------------------------------------------------

path2points=$1

IMGFILE="${path2points}/seg_final.nrrd"
OUTFILE="${path2points}/seg_final_smooth"
VTK_SURF="${path2points}/seg_final_smooth_with_BPs"

cmd="/home/rb21/Software/segtools/bin/segsmooth 
                -l 227
               --fuzz-factor 3.0
               -r $RESOLUTION $RESOLUTION $RESOLUTION
               --padding 0 0 0 
               --voxel-units
	       --save-surfaces $VTK_SURF
           $IMGFILE
               ${OUTFILE}.nrrd
               "
echo $cmd
eval $cmd


cmd="/home/rb21/Software/segtools/bin/segconvert ${OUTFILE}.nrrd  ${OUTFILE}.inr"
echo $cmd
eval $cmd
