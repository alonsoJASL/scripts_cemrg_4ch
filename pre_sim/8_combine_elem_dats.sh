#!/bin/bash

heartFolder=$1

la_map_dat="${heartFolder}/surfaces_uvc_LA/la/uvc/map_rotational_z.dat"
ra_map_dat="${heartFolder}/surfaces_uvc_RA/ra/uvc/map_rotational_z.dat"
pre_sim_folder="${heartFolder}/pre_simulation"

cp $la_map_dat ${pre_sim_folder}/map_rotational_z_la.dat

cp $ra_map_dat ${pre_sim_folder}/map_rotational_z_ra.dat

CMD="meshtool interpolate node2elem 
	-omsh=${heartFolder}/surfaces_uvc_LA/la/la 
	-idat=${heartFolder}/pre_simulation/map_rotational_z_la.dat 
	-odat=${heartFolder}/pre_simulation/map_rotational_z_la_e.dat"
eval $CMD

CMD="meshtool interpolate node2elem 
	-omsh=${heartFolder}/surfaces_uvc_RA/ra/ra 
	-idat=${heartFolder}/pre_simulation/map_rotational_z_ra.dat 
	-odat=${heartFolder}/pre_simulation/map_rotational_z_ra_e.dat"
eval $CMD

CMD="meshtool insert data 
	-msh=${heartFolder}/pre_simulation/myocardium_AV_FEC_BB 
	-submsh=${heartFolder}/surfaces_uvc_LA/la/la 
	-submsh_data=${heartFolder}/pre_simulation/map_rotational_z_la_e.dat 
	-odat=${heartFolder}/pre_simulation/elem_dat_UVC_ek_inc_la.dat 
	-mode=1"
eval $CMD

CMD="meshtool insert data 
	-msh=${heartFolder}/pre_simulation/myocardium_AV_FEC_BB 
	-submsh=${heartFolder}/surfaces_uvc_RA/ra/ra 
	-submsh_data=${heartFolder}/pre_simulation/map_rotational_z_ra_e.dat 
	-odat=${heartFolder}/pre_simulation/elem_dat_UVC_ek_inc_ra.dat 
	-mode=1"
eval $CMD

python3 combine_rot_coords.py ${heartFolder}


CMD="GlVTKConvert 
	-m ${heartFolder}/pre_simulation/myocardium_AV_FEC_BB 
	-e ${heartFolder}/pre_simulation/elem_dat_UVC_ek_combined.dat 
	-F bin 
	-o ${heartFolder}/pre_simulation/myocardium_AV_FEC_BB_elem_dat_UVC_combined 
	--trim-names"
eval $CMD