#!/bin/bash

heartFolder=$1
scriptsPath=/data/Dropbox/scripts_cemrgapp/

CMD="mkdir ${heartFolder}/sims_folder"
eval $CMD

CMD="mkdir ${heartFolder}/sims_folder/unloaded"
eval $CMD

CMD="cp ${heartFolder}/pre_simulation/elem_dat_UVC_ek_combined.dat ${heartFolder}/sims_folder/pericardium_scale.dat"
eval $CMD

CMD="cp ${heartFolder}/pre_simulation/surfaces_simulation/epicardium.surf ${heartFolder}/sims_folder"
eval $CMD

CMD="cp ${heartFolder}/pre_simulation/epicardium_for_sim.surf ${heartFolder}/sims_folder"
eval $CMD

CMD="cp ${heartFolder}/pre_simulation/surfaces_simulation/LA_endo.surf ${heartFolder}/sims_folder"
eval $CMD

CMD="cp ${heartFolder}/pre_simulation/surfaces_simulation/LV_endo.surf ${heartFolder}/sims_folder"
eval $CMD

CMD="cp ${heartFolder}/pre_simulation/myocardium_AV_FEC_BB.* ${heartFolder}/sims_folder"
eval $CMD

CMD="cp ${heartFolder}/pre_simulation/surfaces_simulation/RA_endo.surf ${heartFolder}/sims_folder"
eval $CMD

CMD="cp ${heartFolder}/pre_simulation/surfaces_simulation/RV_endo.surf ${heartFolder}/sims_folder"
eval $CMD

CMD="cp ${heartFolder}/pre_simulation/surfaces_simulation/surfaces_rings/RPVs.surf ${heartFolder}/sims_folder"
eval $CMD

CMD="cp ${heartFolder}/pre_simulation/surfaces_simulation/surfaces_rings/RPVs.surf.vtx ${heartFolder}/sims_folder"
eval $CMD

CMD="cp ${heartFolder}/pre_simulation/surfaces_simulation/surfaces_rings/SVC.surf ${heartFolder}/sims_folder"
eval $CMD

CMD="cp ${heartFolder}/pre_simulation/surfaces_simulation/surfaces_rings/SVC.surf.vtx ${heartFolder}/sims_folder"
eval $CMD

CMD="cp ${scriptsPath}/pre_sim/myocardium_AV_FEC_BB_SA.vtx ${heartFolder}/sims_folder"
eval $CMD

CMD="cp ${scriptsPath}/pre_sim/myocardium_AV_FEC_BB_apex.vtx ${heartFolder}/sims_folder"
eval $CMD