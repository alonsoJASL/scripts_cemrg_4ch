import os
import sys
import json
from SIMULATION_library import mesh_utils

#######################
# mesh with refined atria
#######################
meshFolder = '/data/Dropbox/Segmentations/2016111001EP/final_heart/'
meshName = 'myocardium'

cmd = 'mkdir '+meshFolder+'/surfaces_simulation/surfaces_rings'
os.system(cmd)

cmd = 'meshtool extract surface -msh='+meshFolder+'/'+meshName+' -surf='+meshFolder+'surfaces_simulation/surfaces_rings/rings -ofmt=vtk -op=19,20,22:3,4,11,12,13,14,15,16,17'
os.system(cmd)

cmd = 'meshtool extract unreachable -msh='+meshFolder+'surfaces_simulation/surfaces_rings/rings.surfmesh.vtk -submsh='+meshFolder+'surfaces_simulation/surfaces_rings/rings_CC -ofmt=vtk'
os.system(cmd)

############
# surfaces

mesh_utils.connected_component_to_surface(meshFolder+'/surfaces_simulation/surfaces_rings/rings_CC.part0.eidx',
								   meshFolder+'/surfaces_simulation/surfaces_rings/rings.surf',
								   meshFolder+'/surfaces_simulation/surfaces_rings/SVC.surf')
mesh_utils.surf2vtk(meshFolder+meshName,
			 meshFolder+'/surfaces_simulation/surfaces_rings/SVC.surf',
			 meshFolder+'/surfaces_simulation/surfaces_rings/SVC.surf.vtu')

mesh_utils.connected_component_to_surface(meshFolder+'/surfaces_simulation/surfaces_rings/rings_CC.part1.eidx',
								   meshFolder+'/surfaces_simulation/surfaces_rings/rings.surf',
								   meshFolder+'/surfaces_simulation/surfaces_rings/RPVs.surf')
mesh_utils.surf2vtk(meshFolder+meshName,
			 meshFolder+'/surfaces_simulation/surfaces_rings/RPVs.surf',
			 meshFolder+'/surfaces_simulation/surfaces_rings/RPVs.surf.vtu')
