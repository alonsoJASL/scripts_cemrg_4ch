#!/bin/bash

clear

heart_folder=$1
mshPath="${heart_folder}/surfaces_uvc_LA"

echo "extracting la mesh..."
cmd="mkdir ${mshPath}/la/"
eval $cmd

cmd="meshtool extract mesh -msh=${heart_folder}/surfaces_uvc/myocardium -submsh=${mshPath}/la/la -tags=3"
echo $cmd
eval $cmd

echo "mapping vtx files from four-chamber to la..."
cmd="meshtool map -submsh=${mshPath}/la/la 
				  -files=${mshPath}/la.apex.vtx,${mshPath}/la.base.surf.vtx,${mshPath}/la.epi.vtx,${mshPath}/la.lvendo.vtx
				  -outdir=${mshPath}/la"
echo $cmd
eval $cmd

cmd="meshtool convert -imsh=${mshPath}/la/la -omsh=${mshPath}/la/la -ofmt=vtk_bin"
echo $cmd
eval $cmd

cmd="cp /data/Dropbox/scripts_cemrgapp/h_template/la.lvapex.vtx ${mshPath}/la/la.lvapex.vtx"
echo $cmd
eval $cmd

cmd="cp /data/Dropbox/scripts_cemrgapp/h_template/la.rvsept_pt.vtx ${mshPath}/la/la.rvsept_pt.vtx"
echo $cmd
eval $cmd
