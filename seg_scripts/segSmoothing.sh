#!/bin/bash

clear

# -----------------------------------------------------------
RESOLUTION=0.15
# -----------------------------------------------------------

path2points=$1

IMGFILE="${path2points}/seg_final_rotated.nrrd"
OUTFILE="${path2points}/seg_final_smooth_rotated"

# cmd="/home/common/carpusers-segtools/bin/segsmooth
#                 -l 1 2 3 4 5 6 7 103 104 105 106 107 201 202 203 204 205 206 207 208 209 210 211 221 222 223 224 225 226 227
#                --fuzz-factor 3.0
#                -r $RESOLUTION $RESOLUTION $RESOLUTION
#                --padding 0 0 0 
#                --voxel-units
#            $IMGFILE
#                ${OUTFILE}.nrrd
#                "
# echo $cmd
# eval $cmd

cmd="/home/common/carpusers-segtools/bin/segsmooth
                -l 1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37
               --fuzz-factor 3.0
               -r $RESOLUTION $RESOLUTION $RESOLUTION
               --padding 0 0 0 
               --voxel-units
           $IMGFILE
               ${OUTFILE}.nrrd
               "
echo $cmd
eval $cmd


cmd="/home/common/carpusers-segtools/bin/segconvert ${OUTFILE}.nrrd  ${OUTFILE}.inr"
echo $cmd
eval $cmd
