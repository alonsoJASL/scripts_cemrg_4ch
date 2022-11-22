import numpy as np
import sys
import meshio
import copy
import argparse
import os

from DATA_library import motion_volume

parser = argparse.ArgumentParser(description='To run: python3 extra_check_surfs.py [heart_folder]')
parser.add_argument("heart_folder")
args = parser.parse_args()
HEART_FOLDER = args.heart_folder

simsFolder=HEART_FOLDER+"sims_folder/"
mesh=HEART_FOLDER+"sims_folder/myocardium_AV_FEC_BB_lvrv"

os.system("mkdir "+simsFolder+"/check_surfs")

def surf2vtk(msh_file,
                         surf_file,
                         output_name):
        print('Converting '+surf_file+' to vtk...' )

        surf = motion_volume.read_surf(surf_file)
        vtx = motion_volume.surf2vtx(surf)

        # msh = meshio.read(msh_file)
        pts_msh = motion_volume.read_pts(msh_file+".pts")

        # pts_surf = msh.points[vtx,:]
        pts_surf = pts_msh[vtx,:]

        surf_reindexed = copy.deepcopy(surf)
        for i in range(surf.shape[0]):
                surf_reindexed[i,0] = np.where(vtx==surf[i,0])[0]
                surf_reindexed[i,1] = np.where(vtx==surf[i,1])[0]
                surf_reindexed[i,2] = np.where(vtx==surf[i,2])[0]

        cells = {"triangle": surf_reindexed}
        surf_vtk_msh = meshio.Mesh(
                                pts_surf,
                                cells
                                )

        meshio.write(output_name, surf_vtk_msh,file_format="vtu")

surf = simsFolder+"/epicardium.surf"
surf = surf2vtk(mesh,surf,simsFolder+"/check_surfs/epicardium.vtu")

surf = simsFolder+"/epicardium_for_sim.surf"
surf = surf2vtk(mesh,surf,simsFolder+"/check_surfs/epicardium_for_sim.vtu")

surf = simsFolder+"/LA_endo.surf"
surf = surf2vtk(mesh,surf,simsFolder+"/check_surfs/LA_endo.vtu")

surf = simsFolder+"/LV_endo.surf"
surf = surf2vtk(mesh,surf,simsFolder+"/check_surfs/LV_endo.vtu")

surf = simsFolder+"/RA_endo.surf"
surf = surf2vtk(mesh,surf,simsFolder+"/check_surfs/RA_endo.vtu")

surf = simsFolder+"/RV_endo.surf"
surf = surf2vtk(mesh,surf,simsFolder+"/check_surfs/RV_endo.vtu")

surf = simsFolder+"/RPVs.surf"
surf = surf2vtk(mesh,surf,simsFolder+"/check_surfs/RPVs.vtu")

surf = simsFolder+"/SVC.surf"
surf = surf2vtk(mesh,surf,simsFolder+"/check_surfs/SVC.vtu")