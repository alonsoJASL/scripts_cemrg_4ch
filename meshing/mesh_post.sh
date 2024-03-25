#!/bin/sh

heart_folder=$1
MSHFOLDER="${heart_folder}/meshing/myocardium_OUT"

CMD="cp ${MSHFOLDER}/myocardium_original.elem ${MSHFOLDER}/heart_mesh.elem"
eval $CMD
CMD="cp ${MSHFOLDER}/myocardium_original.lon ${MSHFOLDER}/heart_mesh.lon"
eval $CMD
CMD="cp ${MSHFOLDER}/myocardium_original.pts ${MSHFOLDER}/heart_mesh.pts"
eval $CMD
CMD="cp ${MSHFOLDER}/myocardium_original.vtk ${MSHFOLDER}/heart_mesh.vtk"
eval $CMD

MESHTOOL_PATH="/home/common/CARPentry_KCL_latest/meshtool/standalones/"

# meshtool extract mesh -msh=${MSHFOLDER}/heart_mesh -tags=2,103,104,105,106,107,201,202,203,204,205,206,207,208,209,210,211,221,222,223,224,225,226,227 -submsh=${MSHFOLDER}/myocardium_coarse -ifmt=carp_txt

meshtool extract mesh -msh=${MSHFOLDER}/heart_mesh -tags=2,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37 -submsh=${MSHFOLDER}/myocardium_coarse -ifmt=carp_txt -ofmt=carp_txt

# meshtool convert -imsh=${MSHFOLDER}/myocardium -omsh=${MSHFOLDER}/myocardium -ifmt=carp_txt -ofmt=vtk

${MESHTOOL_PATH}/simplify_tag_topology -msh=${MSHFOLDER}/myocardium_coarse -outmsh=${MSHFOLDER}/myocardium_clean -neigh=50 -ifmt=carp_txt -ofmt=carp_txt

# meshtool smooth mesh -msh=${MSHFOLDER}/myocardium_clean -tags=2,103,104,105,106,107,201,202,203,204,205,206,207,208,209,210,211,221,222,223,224,225,226,227 -smth=0.15 -outmsh=${MSHFOLDER}/myocardium_smooth -ifmt=carp_txt -ofmt=carp_txt
meshtool smooth mesh -msh=${MSHFOLDER}/myocardium_clean -tags=2,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37 -smth=0.15 -outmsh=${MSHFOLDER}/myocardium_smooth -ifmt=carp_txt -ofmt=carp_txt

cp ${MSHFOLDER}/myocardium_smooth.elem ${MSHFOLDER}/myocardium.elem
cp ${MSHFOLDER}/myocardium_smooth.pts ${MSHFOLDER}/myocardium.pts
# meshtool extract surface -msh=${MSHFOLDER}/myocardium_smooth -surf=${MSHFOLDER}/whole_surface -ofmt=vtk

# meshtool extract unreachable -msh=${MSHFOLDER}/whole_surface.surfmesh.vtk -submsh=${MSHFOLDER}/whole_surface_CC -ofmt=vtk

echo "Relabelling mesh..."
cmd="python3 ./relabel_mesh.py ${heart_folder}"
# cmd="python3 ./relabel_mesh_MRI.py ${heart_folder}"
eval $cmd
 