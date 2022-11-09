#!/bin/sh

heart_folder=$1
MSHFOLDER="${heart_folder}/meshing/myocardium_OUT"

MESHTOOL_PATH="/home/rb21/Software/2021_1108_CARPentry_KCL_latest/CARPentry_KCL_latest/meshtool/standalones/"

meshtool extract mesh -msh=${MSHFOLDER}/heart_mesh -tags=2,103,104,105,106,107,201,202,203,204,205,206,207,208,209,210,211,221,222,223,224,225,226,227 -submsh=${MSHFOLDER}/myocardium -ifmt=carp_txt

meshtool convert -imsh=${MSHFOLDER}/myocardium -omsh=${MSHFOLDER}/myocardium -ifmt=carp_txt -ofmt=vtk

${MESHTOOL_PATH}/simplify_tag_topology -msh=${MSHFOLDER}/myocardium -outmsh=${MSHFOLDER}/myocardium_clean -neigh=50 -ifmt=carp_txt -ofmt=carp_txt

meshtool smooth mesh -msh=${MSHFOLDER}/myocardium -tags=2,103,104,105,106,107,201,202,203,204,205,206,207,208,209,210,211,221,222,223,224,225,226,227 -smth=0.15 -outmsh=${MSHFOLDER}/myocardium_smooth -ifmt=carp_txt -ofmt=carp_txt

meshtool extract surface -msh=${MSHFOLDER}/myocardium_smooth -surf=${MSHFOLDER}/whole_surface -ofmt=vtk

meshtool extract unreachable -msh=${MSHFOLDER}/whole_surface.surfmesh.vtk -submsh=${MSHFOLDER}/whole_surface_CC -ofmt=vtk

echo "Relabelling mesh..."
cmd="python3 ./relabel_mesh.py ${heart_folder}"
eval $cmd
 