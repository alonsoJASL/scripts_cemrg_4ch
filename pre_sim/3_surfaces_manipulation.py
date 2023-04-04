import os
import sys
import json
from SIMULATION_library import mesh_utils
import argparse

# I want to have only one epicardial surface and one map
# for scaling the stiffness of the peri springs
# meshFolder = '/data/Dropbox/mesh_refinement/case19_1000um/'
# mesh_utils.combine_elem_file([meshFolder+'scaled_v.dat',meshFolder+'scaled_la_smooth.dat',meshFolder+'scaled_ra_smooth.dat'],
# 					          meshFolder+'pericardium_scale.dat')


#######################
# mesh with refined atria
#######################
parser = argparse.ArgumentParser(description='To run: python3 surfaces_manipulation.py [heart_folder]')
parser.add_argument("heart_folder")
args = parser.parse_args()
HEART_FOLDER = args.heart_folder

meshFolder=HEART_FOLDER+"pre_simulation/"
meshName = 'myocardium_AV_FEC_BB'

cmd = 'mkdir '+meshFolder+'/surfaces_simulation'
os.system(cmd)

cmd = 'meshtool extract surface -msh='+meshFolder+'/'+meshName+' -surf='+meshFolder+'surfaces_simulation/surface_heart -ofmt=vtk'
os.system(cmd)

cmd = 'meshtool extract unreachable -msh='+meshFolder+'surfaces_simulation/surface_heart.surfmesh.vtk -submsh='+meshFolder+'surfaces_simulation/surface_heart_CC -ofmt=vtk'
os.system(cmd)

############
# surfaces

# mesh_utils.combine_elem_file([meshFolder+'scaled_v.dat',meshFolder+'scaled_la_smooth.dat',meshFolder+'scaled_ra_smooth.dat'],
# 					          meshFolder+'pericardium_scale.dat')

# map five connected components:
# 0 : RA endo
mesh_utils.connected_component_to_surface(meshFolder+'/surfaces_simulation/surface_heart_CC.part4.eidx',
								   meshFolder+'/surfaces_simulation/surface_heart.surf',
								   meshFolder+'/surfaces_simulation/RA_endo.surf')
mesh_utils.surf2vtk(meshFolder+meshName,
			 meshFolder+'/surfaces_simulation/RA_endo.surf',
			 meshFolder+'/surfaces_simulation/RA_endo.surf.vtu')

# 1 : epicardium
mesh_utils.connected_component_to_surface(meshFolder+'/surfaces_simulation/surface_heart_CC.part1.eidx',
								   meshFolder+'/surfaces_simulation/surface_heart.surf',
								   meshFolder+'/surfaces_simulation/epicardium.surf')
mesh_utils.surf2vtk(meshFolder+meshName,
			 meshFolder+'/surfaces_simulation/epicardium.surf',
			 meshFolder+'/surfaces_simulation/epicardium.surf.vtu')

# # 2 : LA endo
mesh_utils.connected_component_to_surface(meshFolder+'/surfaces_simulation/surface_heart_CC.part2.eidx',
								   meshFolder+'/surfaces_simulation/surface_heart.surf',
								   meshFolder+'/surfaces_simulation/LA_endo.surf')
mesh_utils.surf2vtk(meshFolder+meshName,
			 meshFolder+'/surfaces_simulation/LA_endo.surf',
			 meshFolder+'/surfaces_simulation/LA_endo.surf.vtu')

# 3 : RV endo
mesh_utils.connected_component_to_surface(meshFolder+'/surfaces_simulation/surface_heart_CC.part3.eidx',
								   meshFolder+'/surfaces_simulation/surface_heart.surf',
								   meshFolder+'/surfaces_simulation/RV_endo.surf')
mesh_utils.surf2vtk(meshFolder+meshName,
			 meshFolder+'/surfaces_simulation/RV_endo.surf',
			 meshFolder+'/surfaces_simulation/RV_endo.surf.vtu')

# 4 : LV endo
mesh_utils.connected_component_to_surface(meshFolder+'/surfaces_simulation/surface_heart_CC.part0.eidx',
								   meshFolder+'/surfaces_simulation/surface_heart.surf',
								   meshFolder+'/surfaces_simulation/LV_endo.surf')
mesh_utils.surf2vtk(meshFolder+meshName,
			 meshFolder+'/surfaces_simulation/LV_endo.surf',
			 meshFolder+'/surfaces_simulation/LV_endo.surf.vtu')

print("CHECK THAT THE SURFACES ARE AS EXPECTED!")