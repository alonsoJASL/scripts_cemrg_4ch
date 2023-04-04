#!/bin/bash

clear

heart_folder=$1
mshPath="${heart_folder}/surfaces_uvc_RA/"

echo "extracting ra mesh..."
cmd="mkdir ${mshPath}/ra/"
eval $cmd

cmd="meshtool extract mesh -msh=${heart_folder}/surfaces_uvc/myocardium -submsh=${mshPath}/ra/ra -tags=4"
echo $cmd
eval $cmd

echo "mapping vtx files from four-chamber to ra..."
cmd="meshtool map -submsh=${mshPath}/ra/ra 
				  -files=${mshPath}/ra.apex.vtx,${mshPath}/ra.base.surf.vtx,${mshPath}/ra.epi.vtx,${mshPath}/ra.lvendo.vtx
				  -outdir=${mshPath}/ra"
echo $cmd
eval $cmd

cmd="meshtool convert -imsh=${mshPath}/ra/ra -omsh=${mshPath}/ra/ra -ofmt=vtk_bin"
echo $cmd
eval $cmd

cmd="cp /data/Dropbox/scripts_cemrgapp/h_template/ra.lvapex.vtx ${mshPath}/ra/ra.lvapex.vtx"
echo $cmd
eval $cmd

cmd="cp /data/Dropbox/scripts_cemrgapp/h_template/ra.rvsept_pt.vtx ${mshPath}/ra/ra.rvsept_pt.vtx"
echo $cmd
eval $cmd