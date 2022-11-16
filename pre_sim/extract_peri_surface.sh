#!/bin/bash

clear

# conda activate

heart_folder=$1

folder="${heart_folder}/pre_simulation/"

meshname="myocardium_AV_FEC_BB"

mesh="${folder}/$meshname"

meshtool extract surface -msh=$mesh -surf=${folder}/peri_surface -ofmt=vtk -op=1,2,3,4,26,27-5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,30,31,32

meshtool extract unreachable -msh=${folder}/peri_surface.surfmesh -ifmt=vtk -ofmt=vtk -submsh=${folder}/peri_surface_CC

python peri_surface_mapping.py ${folder}/peri_surface_CC.part0 ${folder}/peri_surface.surf ${folder}/epicardium_for_sim ${mesh}

rm ${folder}/*CC*
