import sys
import numpy as np
import copy
import meshio
import numpy as np
import sys
import copy
from tqdm import tqdm
import time

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

def connected_component_to_surface(eidx_file,original_surface,output_surface):
	eidx = np.fromfile(eidx_file+".eidx", dtype=int, count=-1)
	nod = np.fromfile(eidx_file+".nod", dtype=int, count=-1)
	surf = np.loadtxt(original_surface,dtype=int,skiprows=1,usecols=[1,2,3])
	vtx = surf2vtx(surf)

	subsurf = surf[eidx,:]
	subvtx = vtx[nod]

	write_surf(subsurf,output_surface+".surf")
	write_vtx(subvtx,output_surface+".vtx")

def remove_sept(mesh,surf_folder):
	print("Converting rvendo.surf and rvsept.surf to rvendo.vtx and rvsept.vtx")
	rvendo_surf = np.loadtxt(surf_folder+"/tmp/myocardium.rvendo.surf",dtype=int,skiprows=1,usecols=[1,2,3])
	rvsept_surf = np.loadtxt(surf_folder+"/tmp/myocardium.rvsept.surf",dtype=int,skiprows=1,usecols=[1,2,3])

	rvendo_vtx = surf2vtx(rvendo_surf)
	rvsept_vtx = surf2vtx(rvsept_surf)

	print("Finding the free wall")
	freewall_vtx = np.setdiff1d(rvendo_vtx,rvsept_vtx)

	freewall_tr = []
	sept_tr = []

	for tr in tqdm (rvendo_surf, desc="Looping over triangles..."):
		if len(np.intersect1d(tr,rvsept_vtx))<3:
			freewall_tr.append(tr)
        # else:
        	# sept_tr.append(tr)

	print("Finished looping over triangles")

	freewall_tr = np.array(freewall_tr)

	write_surf(freewall_tr,surf_folder+"/tmp/myocardium.rvendo_nosept.surf")
	freewall_vtx = surf2vtx(freewall_tr)
	write_vtx(freewall_vtx,surf_folder+"/tmp/myocardium.rvendo_nosept.surf"+".vtx")

	surf2vtk(mesh,surf_folder+"/tmp/myocardium.rvendo_nosept.surf",surf_folder+"/tmp/myocardium.rvendo_nosept.surf"+".vtk")

def prepare_vtx_for_uvc(surf_folder):
	epi_surf = np.loadtxt(surf_folder+"/tmp/myocardium.epi.surf",dtype=int,skiprows=1,usecols=[1,2,3])
	lvendo_surf = np.loadtxt(surf_folder+"/tmp/myocardium.lvendo.surf",dtype=int,skiprows=1,usecols=[1,2,3])
	rvendo_surf = np.loadtxt(surf_folder+"/tmp/myocardium.rvendo.surf",dtype=int,skiprows=1,usecols=[1,2,3])
	rvendo_nosept_surf = np.loadtxt(surf_folder+"/tmp/myocardium.rvendo_nosept.surf",dtype=int,skiprows=1,usecols=[1,2,3])
	rvsept_surf = np.loadtxt(surf_folder+"/tmp/myocardium.rvsept.surf",dtype=int,skiprows=1,usecols=[1,2,3])

	epi_surf_vtx = surf2vtx(epi_surf)
	lvendo_surf_vtx = surf2vtx(lvendo_surf)
	rvendo_surf_vtx = surf2vtx(rvendo_surf)
	rvendo_nosept_surf_vtx = surf2vtx(rvendo_nosept_surf)
	rvsept_surf_vtx = surf2vtx(rvsept_surf)

	write_vtx(epi_surf,surf_folder+"/tmp/myocardium.epi.surf.vtx")
	write_vtx(lvendo_surf,surf_folder+"/tmp/myocardium.lvendo.surf.vtx")
	write_vtx(rvendo_surf,surf_folder+"/tmp/myocardium.rvendo.surf.vtx")
	write_vtx(rvendo_nosept_surf,surf_folder+"/tmp/myocardium.rvendo_nosept.surf.vtx")
	write_vtx(rvsept_surf,surf_folder+"/tmp/myocardium.rvsept.surf.vtx")

