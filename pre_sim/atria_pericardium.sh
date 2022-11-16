#!/bin/bash

surfaces_UVC_chamber=$1
chamber=$2

mesh="/data/Dropbox/Segmentations/2016111001EP/final_heart/${surfaces_UVC_chamber}/${chamber}/"
uvcs="${mesh}/uvc/"
cmd="python motion_atria_BCs.py --mesh $mesh --uvcs $uvcs --chamber $chamber"
eval $cmd