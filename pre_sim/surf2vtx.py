import numpy as np
import sys
import meshio
import copy

def surf2vtx(surf):
        return np.unique(surf.flatten())

def write_vtx(vtx,vtx_file):
        f = open(vtx_file,"w")
        f.write(str(int(vtx.shape[0]))+"\n")
        f.write("intra\n")
        for v in vtx:
                f.write(str(v)+"\n")
        f.close()

first_surface = "/data/Dropbox/Segmentations/2016111001EP/final_heart/surfaces_simulation/RPVs.surf"
first_output = "/data/Dropbox/Segmentations/2016111001EP/final_heart/surfaces_simulation/RPVs.surf.vtx"


surf_1 = np.loadtxt(first_surface,dtype=int,skiprows=1,usecols=[1,2,3])

surf_1 = surf2vtx(surf_1)

write_vtx(surf_1,first_output)
