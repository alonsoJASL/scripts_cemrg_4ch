#!/bin/bash

heartFolder=$1

mesh="${heartFolder}/surfaces_uvc_LA/la"
uvcs="${mesh}/uvc/"
cmd="python motion_atria_BCs.py --mesh $mesh --uvcs $uvcs --chamber la"
eval $cmd

mesh="${heartFolder}/surfaces_uvc_RA/ra"
uvcs="${mesh}/uvc/"
cmd="python motion_atria_BCs.py --mesh $mesh --uvcs $uvcs --chamber ra"
eval $cmd