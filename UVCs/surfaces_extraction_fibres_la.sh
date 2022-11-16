#!/bin/bash

clear

heart_folder=$1
mesh="${heart_folder}/meshing/myocardium_OUT/myocardium"
surf_folder="${heart_folder}/surfaces_uvc_LA/"
mkdir $surf_folder

################################################################################
# base
################################################################################
meshtool extract surface -msh=$mesh -surf=${surf_folder}/la.base -ofmt=vtk -op=3:7,1

################################################################################
# epicardium, LV endo and RV endo
################################################################################
meshtool extract surface -msh=$mesh -surf=${surf_folder}/epi_endo -ofmt=vtk -op=3-1,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24

meshtool extract unreachable -msh=${surf_folder}/epi_endo.surfmesh -ifmt=vtk -ofmt=vtk -submsh=${surf_folder}/epi_endo_CC

python surface_mapping.py ${surf_folder}/epi_endo_CC.part0 ${surf_folder}/epi_endo.surf ${surf_folder}/la.epi ${mesh}
python surface_mapping.py ${surf_folder}/epi_endo_CC.part1 ${surf_folder}/epi_endo.surf ${surf_folder}/la.lvendo ${mesh}

# python surface_mapping.py ${surf_folder}/epi_endo_CC.part0 ${surf_folder}/epi_endo.surf ${surf_folder}/la.lvendo ${mesh}
# python surface_mapping.py ${surf_folder}/epi_endo_CC.part1 ${surf_folder}/epi_endo.surf ${surf_folder}/la.epi ${mesh}

cmd="cp ${heart_folder}/meshing/myocardium_OUT/myocardium.* ${heart_folder}/surfaces_uvc"
eval $cmd