import numpy as np
import sys
import meshio
import copy
import argparse

def surf2vtx(surf):
        return np.unique(surf.flatten())

def write_vtx(vtx,vtx_file):
        f = open(vtx_file,"w")
        f.write(str(int(vtx.shape[0]))+"\n")
        f.write("intra\n")
        for v in vtx:
                f.write(str(v)+"\n")
        f.close()

parser = argparse.ArgumentParser(description='To run: python3 surf2vtx.py [heart_folder]')
parser.add_argument("heart_folder")
args = parser.parse_args()
heartFolder = args.heart_folder

first_surface = heartFolder+"/surfaces_uvc/myocardium.epi.surf"
first_output = heartFolder+"/surfaces_uvc/myocardium.epi.surf.vtx"

second_surface = heartFolder+"/surfaces_uvc/myocardium.lvendo.surf"
second_output = heartFolder+"/surfaces_uvc/myocardium.lvendo.surf.vtx"

third_surface = heartFolder+"/surfaces_uvc/myocardium.rvendo.surf"
third_output = heartFolder+"/surfaces_uvc/myocardium.rvendo.surf.vtx"

fourth_surface = heartFolder+"/surfaces_uvc/myocardium.rvendo_nosept.surf"
fourth_output = heartFolder+"/surfaces_uvc/myocardium.rvendo_nosept.surf.vtx"

fifth_surface = heartFolder+"/surfaces_uvc/myocardium.rvsept.surf"
fifth_output = heartFolder+"/surfaces_uvc/myocardium.rvsept.surf.vtx"

surf_1 = np.loadtxt(first_surface,dtype=int,skiprows=1,usecols=[1,2,3])
surf_2 = np.loadtxt(second_surface,dtype=int,skiprows=1,usecols=[1,2,3])
surf_3 = np.loadtxt(third_surface,dtype=int,skiprows=1,usecols=[1,2,3])
surf_4 = np.loadtxt(fourth_surface,dtype=int,skiprows=1,usecols=[1,2,3])
surf_5 = np.loadtxt(fifth_surface,dtype=int,skiprows=1,usecols=[1,2,3])

surf_1 = surf2vtx(surf_1)
surf_1 = surf2vtx(surf_2)
surf_1 = surf2vtx(surf_3)
surf_1 = surf2vtx(surf_4)
surf_1 = surf2vtx(surf_5)

write_vtx(surf_1,first_output)
write_vtx(surf_2,second_output)
write_vtx(surf_3,third_output)
write_vtx(surf_4,fourth_output)
write_vtx(surf_5,fifth_output)