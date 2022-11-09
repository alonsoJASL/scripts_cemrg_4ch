#!/bin/bash

clear

echo "WARNING: SET THE CARPFOLDER PATH TO WHERE YOU HAVE CARPFOLDER/FEMLIB/GlRuleFibers and CARPFOLDER/FEMLIB/GlElemCenters"

CARPFOLDER="/home/rb21/Software/CARPentry_KCL_latest/bin/"

heart_folder=$1
mshPath="${heart_folder}/surfaces_uvc/BiV/"
ENDO=60
EPI=-60
fchPath="${heart_folder}/surfaces_uvc/"
fchName="myocardium"

echo "Computing fibres on biv mesh..."
cmd="GlRuleFibers 
			-m ${mshPath}/BiV
			--type biv
			-a ${mshPath}/uvc/BiV.sol_apba_lap.dat
			-e ${mshPath}/uvc/BiV.sol_endoepi_lap.dat
			-l ${mshPath}/uvc/BiV.sol_lvendo_lap.dat
			-r ${mshPath}/uvc/BiV.sol_rvendo_lap.dat
			--alpha_endo ${ENDO}	
			--alpha_epi ${EPI}
			--beta_endo -65
			--beta_epi 25
			-o ${mshPath}fibres_bayer_${ENDO}_${EPI}.lon
			"
echo $cmd
eval $cmd

# -----------------------------------------------------------

echo "Substituted biv.lon with new fibres..."
cmd="cp ${mshPath}/fibres_bayer_${ENDO}_${EPI}.lon ${mshPath}/BiV.lon"
echo $cmd
eval $cmd  

echo "Generating elements centres..."
cmd="GlElemCenters -m ${mshPath}/BiV -o ${mshPath}/BiV_elem_centres.pts"
echo $cmd
eval $cmd  

echo "Correcting fibre orientation..."
cmd="./correct_fibres.py ${mshPath}/BiV"
echo $cmd
eval $cmd  

echo "Substituted biv.lon with new fibres..."
cmd="cp ${mshPath}/BiV_corrected.lon ${mshPath}/BiV.lon"
echo $cmd
eval $cmd  

echo "Converting for visualisation with Paraview..."
cmd="meshtool convert -imsh=${mshPath}/BiV -ifmt=carp_txt -ofmt=vtk -omsh=${mshPath}/BiV_fibres"
echo $cmd
eval $cmd  

echo "Copying myocardium mesh into surfaces folder..."
cmd="cp ${heart_folder}/meshing/myocardium_OUT/myocardium.* ${fchPath}"

echo $cmd
eval $cmd

echo "Inserting in submesh..."
cmd="meshtool generate fibres -msh=${fchPath}/${fchName}
							 -op=2
							 -outmsh=${fchPath}/${fchName}"
echo $cmd
eval $cmd  

cmd="meshtool insert submesh -submsh=${mshPath}/BiV 
							 -msh=${fchPath}/${fchName}
							 -outmsh=${fchPath}/${fchName}_bayer_${ENDO}_${EPI}
							 -ofmt=carp_txt"
echo $cmd
eval $cmd  

cmd="meshtool convert -imsh=${fchPath}/${fchName}_bayer_60_-60
					  -omsh=${fchPath}/${fchName}_bayer_60_-60
					  -ofmt=vtk_bin"

echo $cmd
eval $cmd  
