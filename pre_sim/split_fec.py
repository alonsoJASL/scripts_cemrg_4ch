import os
import sys
import json
from SIMULATION_library import mesh_utils

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
meshFolder = '/data/Dropbox/Segmentations/2016111001EP/final_heart'

mesh_utils.separate_FEC_lvrv(meshFolder+'/myocardium.elem',
                                                         meshFolder+'/myocardium_AV_FEC_BB_w_full_fib.elem',
                                                         meshFolder+'/surfaces_simulation/LV_endo.surf',
                                                         meshFolder+'/surfaces_simulation/RV_endo.surf',
                                                         meshFolder+'/myocardium_AV_FEC_BB_w_full_fib_lvrv.elem',
                                                         original_tags,
                                                         new_tags)                                                                       