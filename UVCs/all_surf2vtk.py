import sys
import numpy as np
import copy
import meshio
import numpy as np
import sys
import os
import copy
import glob
import argparse
import time

from tqdm import tqdm

def surf2vtk(msh_file,surf_file,output_name):
    print('Converting '+surf_file+' to vtk...' )

    surf = np.loadtxt(surf_file,dtype=int,skiprows=1,usecols=[1,2,3])
    vtx = surf2vtx(surf)

    # msh = meshio.read(msh_file)
    pts = np.loadtxt(msh_file+".pts",dtype=float,skiprows=1)

    pts_surf = pts[vtx,:]

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

    meshio.write(output_name, surf_vtk_msh,file_format="vtk")

def surf2vtx(surf):
    return np.unique(surf.flatten())

def main(args):
    surfFolder = args.surfFolder
    mesh = args.mesh

    surf_files_list = os.listdir(surfFolder)

    surf_files = glob.glob(surfFolder+'/*.surf')
    print(surf_files)

    for surf_file in surf_files:
        out_surf = str(surf_file)+'.vtk'
        surf2vtk(mesh,surf_file,out_surf)
        print('Done')

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.formatter_class = argparse.ArgumentDefaultsHelpFormatter

    parser.add_argument('--mesh', type=str, default=None,
                        help='Provide path to the mesh to which the surfs belong')


    parser.add_argument('--surfFolder', type=str, default=None,
                        help='Provide path to the folder containing the surfaces')

    args = parser.parse_args()

    main(args)