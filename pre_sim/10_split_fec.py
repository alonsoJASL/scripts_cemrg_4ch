import os
import sys
import json
import argparse
from SIMULATION_library import mesh_utils

parser = argparse.ArgumentParser(description='To run: python3 split_fec.py [heart_folder]')
parser.add_argument("heart_folder")
args = parser.parse_args()
HEART_FOLDER = args.heart_folder

json_tags = "/data/Dropbox/rosie/cycle_simulations/tags.json"
f_input = open(json_tags,"r")
original_tags = json.load(f_input)
f_input.close()

json_tags = "/data/Dropbox/rosie/cycle_simulations/tags_lvrv.json"
f_input = open(json_tags,"r")
new_tags = json.load(f_input)
f_input.close()

#######################
# mesh with refined atria
#######################
meshFolder = HEART_FOLDER+'/meshing/myocardium_OUT/'

mesh_utils.separate_FEC_lvrv(meshFolder+'/myocardium.elem',
                                                         HEART_FOLDER+'/sims_folder/myocardium_AV_FEC_BB.elem',
                                                         HEART_FOLDER+'/sims_folder/LV_endo.surf',
                                                         HEART_FOLDER+'/sims_folder/RV_endo.surf',
                                                         HEART_FOLDER+'/sims_folder/myocardium_AV_FEC_BB_lvrv.elem',
                                                         original_tags,
                                                         new_tags)                                                                       

os.system("cp "+HEART_FOLDER+"/sims_folder/myocardium_AV_FEC_BB.lon "+HEART_FOLDER+"/sims_folder/myocardium_AV_FEC_BB_lvrv.lon")
os.system("cp "+HEART_FOLDER+"/sims_folder/myocardium_AV_FEC_BB.pts "+HEART_FOLDER+"/sims_folder/myocardium_AV_FEC_BB_lvrv.pts")
os.system("meshtool convert -imsh="+HEART_FOLDER+"/sims_folder/myocardium_AV_FEC_BB_lvrv -omsh="+HEART_FOLDER+"/sims_folder/myocardium_AV_FEC_BB_lvrv -ofmt=vtk_bin")