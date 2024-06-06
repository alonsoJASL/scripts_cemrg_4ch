#!/bin/sh

clear 

heart_folder=$1
tag_option=${2:-1}

echo $tag_option

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

echo "tag_option value: $tag_option"
if [ "$tag_option" -eq 1 ]; then

meshtool extract mesh -msh=${MSHFOLDER}/heart_mesh -tags=2,103,104,105,106,107,201,202,203,204,205,206,207,208,209,210,211,221,222,223,224,225,226,227 -submsh=${MSHFOLDER}/myocardium_coarse -ifmt=carp_txt

else

meshtool extract mesh -msh=${MSHFOLDER}/heart_mesh -tags=2,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37 -submsh=${MSHFOLDER}/myocardium_coarse -ifmt=carp_txt -ofmt=carp_txt

fi

${MESHTOOL_PATH}/simplify_tag_topology -msh=${MSHFOLDER}/myocardium_coarse -outmsh=${MSHFOLDER}/myocardium_clean -neigh=50 -ifmt=carp_txt -ofmt=carp_txt

if [ "$tag_option" -eq 1 ]; then

meshtool smooth mesh -msh=${MSHFOLDER}/myocardium_clean -tags=2,103,104,105,106,107,201,202,203,204,205,206,207,208,209,210,211,221,222,223,224,225,226,227 -smth=0.15 -outmsh=${MSHFOLDER}/myocardium_smooth -ifmt=carp_txt -ofmt=carp_txt

else

meshtool smooth mesh -msh=${MSHFOLDER}/myocardium_clean -tags=2,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37 -smth=0.15 -outmsh=${MSHFOLDER}/myocardium_smooth -ifmt=carp_txt -ofmt=carp_txt

fi
cp ${MSHFOLDER}/myocardium_smooth.elem ${MSHFOLDER}/myocardium.elem
cp ${MSHFOLDER}/myocardium_smooth.pts ${MSHFOLDER}/myocardium.pts

echo "Relabelling mesh..."

if [ "$tag_option" -eq 1 ]; then
 cmd="python3 ./relabel_mesh.py ${heart_folder}"

 else
cmd="python3 ./relabel_mesh_MRI.py ${heart_folder}"
fi
eval $cmd
