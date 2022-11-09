#!/bin/bash

clear

# ./extract_bivmesh.sh /path/to/fourchmesh heartmeshname

heart_folder=$1
msh="${heart_folder}/meshing/myocardium_OUT/myocardium"	

mkdir ${heart_folder}/surfaces_uvc/BiV/

cmd="meshtool extract mesh -msh=$msh -submsh=${heart_folder}/surfaces_uvc/BiV/BiV -tags=1,2"
eval $cmd
echo "biv extracted"

echo "mapping vtx files from four-chamber to biv..."
cmd="meshtool map -submsh=${heart_folder}/surfaces_uvc/BiV/BiV
				  -files=${heart_folder}/surfaces_uvc/myocardium.apex.vtx,${heart_folder}/surfaces_uvc/myocardium.base.surf.vtx,${heart_folder}/surfaces_uvc/myocardium.epi.surf.vtx,${heart_folder}/surfaces_uvc/myocardium.lvendo.surf.vtx,${heart_folder}/surfaces_uvc/myocardium.rvendo.surf.vtx,${heart_folder}/surfaces_uvc/myocardium.rvendo_nosept.surf.vtx,${heart_folder}/surfaces_uvc/myocardium.rvsept.surf.vtx 
				  -outdir=${heart_folder}/surfaces_uvc/BiV"
eval $cmd

cmd="meshtool map -submsh=${heart_folder}/surfaces_uvc/BiV/BiV
				  -files=${heart_folder}/surfaces_uvc/myocardium.base.surf,${heart_folder}/surfaces_uvc/myocardium.epi.surf,${heart_folder}/surfaces_uvc/myocardium.lvendo.surf,${heart_folder}/surfaces_uvc/myocardium.rvendo.surf,${heart_folder}/surfaces_uvc/myocardium.rvendo_nosept.surf,${heart_folder}/surfaces_uvc/myocardium.rvsept.surf 
				  -outdir=${heart_folder}/surfaces_uvc/BiV"
eval $cmd
echo "everything mapped"

cmd="mv ${heart_folder}/surfaces_uvc/BiV/myocardium.base.surf ${heart_folder}/surfaces_uvc/BiV/BiV.base.surf"
eval $cmd

cmd="mv ${heart_folder}/surfaces_uvc/BiV/myocardium.apex.vtx ${heart_folder}/surfaces_uvc/BiV/BiV.apex.vtx"
eval $cmd

cmd="mv ${heart_folder}/surfaces_uvc/BiV/myocardium.base.surf.vtx ${heart_folder}/surfaces_uvc/BiV/BiV.base.surf.vtx"
eval $cmd

cmd="mv ${heart_folder}/surfaces_uvc/BiV/myocardium.epi.surf ${heart_folder}/surfaces_uvc/BiV/BiV.epi.surf"
eval $cmd

cmd="mv ${heart_folder}/surfaces_uvc/BiV/myocardium.epi.surf.vtx ${heart_folder}/surfaces_uvc/BiV/BiV.epi.surf.vtx"
eval $cmd

cmd="mv ${heart_folder}/surfaces_uvc/BiV/myocardium.lvendo.surf ${heart_folder}/surfaces_uvc/BiV/BiV.lvendo.surf"
eval $cmd

cmd="mv ${heart_folder}/surfaces_uvc/BiV/myocardium.lvendo.surf.vtx ${heart_folder}/surfaces_uvc/BiV/BiV.lvendo.surf.vtx"
eval $cmd

cmd="mv ${heart_folder}/surfaces_uvc/BiV/myocardium.rvendo.surf ${heart_folder}/surfaces_uvc/BiV/BiV.rvendo.surf"
eval $cmd

cmd="mv ${heart_folder}/surfaces_uvc/BiV/myocardium.rvendo.surf.vtx ${heart_folder}/surfaces_uvc/BiV/BiV.rvendo.surf.vtx"
eval $cmd

cmd="mv ${heart_folder}/surfaces_uvc/BiV/myocardium.rvendo_nosept.surf.vtx ${heart_folder}/surfaces_uvc/BiV/BiV.rvendo_nosept.surf.vtx"
eval $cmd

cmd="mv ${heart_folder}/surfaces_uvc/BiV/myocardium.rvendo_nosept.surf ${heart_folder}/surfaces_uvc/BiV/BiV.rvendo_nosept.surf"
eval $cmd

cmd="mv ${heart_folder}/surfaces_uvc/BiV/myocardium.rvsept.surf.vtx ${heart_folder}/surfaces_uvc/BiV/BiV.rvsept.surf.vtx"
eval $cmd

cmd="mv ${heart_folder}/surfaces_uvc/BiV/myocardium.rvsept.surf ${heart_folder}/surfaces_uvc/BiV/BiV.rvsept.surf"
eval $cmd