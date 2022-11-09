#!/bin/bash

clear

heart_folder=$1
mesh="${heart_folder}/meshing/myocardium_OUT/myocardium"	

surf_folder="${heart_folder}/surfaces_uvc/"
mkdir $surf_folder

# ----------------------------------------------------------------------------------------------
# Extract the base
# ----------------------------------------------------------------------------------------------
echo " ## Extracting the base ## "
meshtool extract surface -msh=$mesh -surf=${surf_folder}/myocardium.base -ofmt=vtk -op=1,2:7,8,9,10

# ----------------------------------------------------------------------------------------------
# Extract the epicardium, LV endo and RV endo
# ----------------------------------------------------------------------------------------------
echo " ## Extracting epi, LV endo and RV endo ## "
meshtool extract surface -msh=$mesh -surf=${surf_folder}/epi_endo -ofmt=vtk -op=1,2-7,8,9,10
meshtool extract unreachable -msh=${surf_folder}/epi_endo.surfmesh -ifmt=vtk -ofmt=vtk -submsh=${surf_folder}/epi_endo_CC

# ----------------------------------------------------------------------------------------------
# Extract the RV septum
# ----------------------------------------------------------------------------------------------
echo " ## Extracting septum ## "
meshtool extract surface -msh=$mesh -surf=${surf_folder}/myocardium.rvsept -ofmt=vtk -op=1-2
meshtool extract unreachable -msh=${surf_folder}/myocardium.rvsept.surfmesh -ifmt=vtk -ofmt=vtk -submsh=${surf_folder}/myocardium.rvsept_CC

# ----------------------------------------------------------------------------------------------
# Surface mapping
# ----------------------------------------------------------------------------------------------
echo " ## Mapping surfaces ## "
# python /data/Dropbox/scripts_cemrgapp/UVCs/surface_mapping.py ${surf_folder}/epi_endo_CC.part0 ${surf_folder}/epi_endo.surf ${surf_folder}/myocardium.lvendo ${mesh}
# python /data/Dropbox/scripts_cemrgapp/UVCs/surface_mapping.py ${surf_folder}/epi_endo_CC.part1 ${surf_folder}/epi_endo.surf ${surf_folder}/myocardium.epi ${mesh}
# python /data/Dropbox/scripts_cemrgapp/UVCs/surface_mapping.py ${surf_folder}/epi_endo_CC.part2 ${surf_folder}/epi_endo.surf ${surf_folder}/myocardium.rvendo ${mesh}

python /data/Dropbox/scripts_cemrgapp/UVCs/surface_mapping.py ${surf_folder}/epi_endo_CC.part0 ${surf_folder}/epi_endo.surf ${surf_folder}/myocardium.lvendo ${mesh}
python /data/Dropbox/scripts_cemrgapp/UVCs/surface_mapping.py ${surf_folder}/epi_endo_CC.part1 ${surf_folder}/epi_endo.surf ${surf_folder}/myocardium.rvendo ${mesh}
python /data/Dropbox/scripts_cemrgapp/UVCs/surface_mapping.py ${surf_folder}/epi_endo_CC.part2 ${surf_folder}/epi_endo.surf ${surf_folder}/myocardium.epi ${mesh}

# python /data/Dropbox/scripts_cemrgapp/UVCs/surface_mapping.py ${surf_folder}/epi_endo_CC.part0 ${surf_folder}/epi_endo.surf ${surf_folder}/myocardium.rvendo ${mesh}
# python /data/Dropbox/scripts_cemrgapp/UVCs/surface_mapping.py ${surf_folder}/epi_endo_CC.part1 ${surf_folder}/epi_endo.surf ${surf_folder}/myocardium.lvendo ${mesh}
# python /data/Dropbox/scripts_cemrgapp/UVCs/surface_mapping.py ${surf_folder}/epi_endo_CC.part2 ${surf_folder}/epi_endo.surf ${surf_folder}/myocardium.epi ${mesh}

python /data/Dropbox/scripts_cemrgapp/UVCs/surface_mapping.py ${surf_folder}/myocardium.rvsept_CC.part0 ${surf_folder}/myocardium.rvsept.surf ${surf_folder}/lvepi ${mesh}
python /data/Dropbox/scripts_cemrgapp/UVCs/surface_mapping.py ${surf_folder}/myocardium.rvsept_CC.part1 ${surf_folder}/myocardium.rvsept.surf ${surf_folder}/myocardium.rvsept ${mesh}

# ----------------------------------------------------------------------------------------------
# Picking the apex
# ----------------------------------------------------------------------------------------------
echo " ## Picking the apex ## "

segmentation="${heart_folder}/meshing/myocardium.nrrd"
lv_cavity=1
base=104
pts="${mesh}.pts"
vtx="${surf_folder}/myocardium.epi.vtx"

pickapex $segmentation $lv_cavity $base $pts $vtx > "${surf_folder}/myocardium.apex.vtx"

cmd="python3 remove_sept.py ${heart_folder}"
eval $cmd 

cmd="python3 surf2vtx.py ${heart_folder}"
eval $cmd 

