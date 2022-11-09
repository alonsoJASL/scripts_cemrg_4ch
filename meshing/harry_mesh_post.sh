#!/bin/sh

MSHFOLDER="/data/Dropbox/harry_test/meshing/myocardium_OUT"

MESHTOOL_PATH="/home/rb21/Software/2021_1108_CARPentry_KCL_latest/CARPentry_KCL_latest/meshtool/standalones/"

meshtool extract mesh -msh=${MSHFOLDER}/heart_mesh -tags=1,3,5,7,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28 -submsh=${MSHFOLDER}/myocardium -ifmt=carp_txt

meshtool convert -imsh=${MSHFOLDER}/myocardium -omsh=${MSHFOLDER}/myocardium -ifmt=carp_txt -ofmt=vtk

${MESHTOOL_PATH}/simplify_tag_topology -msh=${MSHFOLDER}/myocardium -outmsh=${MSHFOLDER}/myocardium_clean -neigh=50 -ifmt=carp_txt -ofmt=carp_txt



meshtool smooth mesh -msh=${MSHFOLDER}/myocardium -tags=1,3,5,7,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28 -smth=0.15 -outmsh=${MSHFOLDER}/myocardium_smooth -ifmt=carp_txt -ofmt=carp_txt

meshtool extract surface -msh=${MSHFOLDER}/myocardium_smooth -surf=${MSHFOLDER}/whole_surface -ofmt=vtk

meshtool extract unreachable -msh=${MSHFOLDER}/whole_surface.surfmesh.vtk -submsh=${MSHFOLDER}/whole_surface_CC -ofmt=vtk

