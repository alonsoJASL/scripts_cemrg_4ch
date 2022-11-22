import os
import sys
import json
from SIMULATION_library import mesh_utils
import argparse

#######################
# mesh with refined atria
#######################

parser = argparse.ArgumentParser(description='To run: python3 surface_rings.py [heart_folder]')
parser.add_argument("heart_folder")
args = parser.parse_args()
HEART_FOLDER = args.heart_folder

meshFolder=HEART_FOLDER+"pre_simulation/"
meshName = 'myocardium_AV_FEC_BB'

cmd = 'mkdir '+meshFolder+'/surfaces_simulation/surfaces_rings'
os.system(cmd)

# cmd = 'meshtool extract surface -msh='+meshFolder+'/'+meshName+' -surf='+meshFolder+'surfaces_simulation/surfaces_rings/rings -ofmt=vtk -op=19,20,22:3,4,11,12,13,14,15,16,17'
# os.system(cmd)

# harry only 
# cmd = 'meshtool extract surface -msh='+meshFolder+'/'+meshName+' -surf='+meshFolder+'surfaces_simulation/surfaces_rings/RPVs -ofmt=vtk -op=19,20-1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,21,22,23,24,25,26,27,28,29'
# os.system(cmd)

# all other hearts
cmd = 'meshtool extract surface -msh='+meshFolder+'/'+meshName+' -surf='+meshFolder+'surfaces_simulation/surfaces_rings/RPVs -ofmt=vtk -op=23,24-1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,25,26,27,28,29'
os.system(cmd)

#harry only
# cmd = 'meshtool extract surface -msh='+meshFolder+'/'+meshName+' -surf='+meshFolder+'surfaces_simulation/surfaces_rings/SVC -ofmt=vtk -op=22-1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,23,24,25,26,27,28,29'
# os.system(cmd)

# all other hearts
cmd = 'meshtool extract surface -msh='+meshFolder+'/'+meshName+' -surf='+meshFolder+'surfaces_simulation/surfaces_rings/SVC -ofmt=vtk -op=19-1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,20,21,22,23,24,25,26,27,28,29'
os.system(cmd)

# cmd = 'meshtool extract unreachable -msh='+meshFolder+'surfaces_simulation/surfaces_rings/rings.surfmesh.vtk -submsh='+meshFolder+'surfaces_simulation/surfaces_rings/rings_CC -ofmt=vtk'
# os.system(cmd)

############
# surfaces

# mesh_utils.connected_component_to_surface(meshFolder+'/surfaces_simulation/surfaces_rings/rings_CC.part1.eidx',
# 								   meshFolder+'/surfaces_simulation/surfaces_rings/rings.surf',
# 								   meshFolder+'/surfaces_simulation/surfaces_rings/SVC.surf')
# mesh_utils.surf2vtk(meshFolder+meshName,
# 			 meshFolder+'/surfaces_simulation/surfaces_rings/SVC.surf',
# 			 meshFolder+'/surfaces_simulation/surfaces_rings/SVC.surf.vtu')

# mesh_utils.connected_component_to_surface(meshFolder+'/surfaces_simulation/surfaces_rings/rings_CC.part0.eidx',
# 								   meshFolder+'/surfaces_simulation/surfaces_rings/rings.surf',
# 								   meshFolder+'/surfaces_simulation/surfaces_rings/RPVs.surf')
# mesh_utils.surf2vtk(meshFolder+meshName,
# 			 meshFolder+'/surfaces_simulation/surfaces_rings/RPVs.surf',
# 			 meshFolder+'/surfaces_simulation/surfaces_rings/RPVs.surf.vtu')
