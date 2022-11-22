import numpy as np
import sys
import meshio
import copy
import argparse

parser = argparse.ArgumentParser(description='To run: python3 surf2vtx.py [heart_folder]')
parser.add_argument("heart_folder")
args = parser.parse_args()
HEART_FOLDER = args.heart_folder

meshFolder=HEART_FOLDER+"pre_simulation/"

def surf2vtx(surf):
        return np.unique(surf.flatten())

def write_vtx(vtx,vtx_file):
        f = open(vtx_file,"w")
        f.write(str(int(vtx.shape[0]))+"\n")
        f.write("intra\n")
        for v in vtx:
                f.write(str(v)+"\n")
        f.close()

first_surface = meshFolder+"/surfaces_simulation/surfaces_rings/RPVs.surf"
first_output = meshFolder+"/surfaces_simulation/surfaces_rings/RPVs.surf.vtx"

second_surface = meshFolder+"/surfaces_simulation/surfaces_rings/SVC.surf"
second_output = meshFolder+"/surfaces_simulation/surfaces_rings/SVC.surf.vtx"

surf_1 = np.loadtxt(first_surface,dtype=int,skiprows=1,usecols=[1,2,3])
surf_1 = surf2vtx(surf_1)
write_vtx(surf_1,first_output)

surf_2 = np.loadtxt(second_surface,dtype=int,skiprows=1,usecols=[1,2,3])
surf_2 = surf2vtx(surf_2)
write_vtx(surf_2,second_output)