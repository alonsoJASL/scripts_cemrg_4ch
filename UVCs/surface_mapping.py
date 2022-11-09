import numpy as np
import sys
import meshio
import copy

def surf2vtk(msh_file,
             surf_file,
             output_name):
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


def write_surf(surf,surf_file):
        f = open(surf_file,"w")
        f.write(str(int(surf.shape[0]))+"\n")
        for t in surf:
                f.write("Tr "+str(t[0])+" "+str(t[1])+" "+str(t[2])+"\n")
        f.close()

def write_vtx(vtx,vtx_file):
        f = open(vtx_file,"w")
        f.write(str(int(vtx.shape[0]))+"\n")
        f.write("intra\n")
        for v in vtx:
                f.write(str(v)+"\n")
        f.close()

def connected_component_to_surface(eidx_file,
                                   original_surface,
                                   output_surface):

        eidx = np.fromfile(eidx_file+".eidx", dtype=int, count=-1)
        nod = np.fromfile(eidx_file+".nod", dtype=int, count=-1)
        surf = np.loadtxt(original_surface,dtype=int,skiprows=1,usecols=[1,2,3])
        vtx = surf2vtx(surf)

        subsurf = surf[eidx,:]
        subvtx = vtx[nod]
 
        write_surf(subsurf,output_surface+".surf")
        write_vtx(subvtx,output_surface+".vtx")

surface_name=sys.argv[1]
original_surface=sys.argv[2]
output_surface=sys.argv[3]
msh_file=sys.argv[4]

connected_component_to_surface(surface_name,
                               original_surface,
                               output_surface)

surf2vtk(msh_file,
         output_surface+".surf",
         output_surface+".vtk")