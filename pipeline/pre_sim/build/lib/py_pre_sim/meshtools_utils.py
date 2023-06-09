import os

from py_pre_sim.mesh_utils import *
from py_pre_sim.file_utils import *

def extract_tags(input_tags,
				 labels):
	
	tags_list = []
	for l in labels:
		if type(input_tags[l])==int:
			tags_list += [input_tags[l]]
		elif type(input_tags[l])==np.ndarray:
			tags_list += list(input_tags[l])
		else:
			raise Exception("Type not recognised.")

	return tags_list

def meshtool_extract_peri(mesh,presimFolder,input_tags):

	tags_list_peri = extract_tags(input_tags,["LV","RV","LA","RA","BB","AV"])
	tags_list_peri = [str(t) for t in tags_list_peri]
	tags_list_peri_string = ",".join(tags_list_peri)

	tags_list_not_peri = extract_tags(input_tags,["Ao","PArt",
											 	  "MV","TV","AV","PV",
											 	  "LSPV","LIPV","RSPV","RIPV",
											 	  "LAA","SVC","IVC",
											 	  "LAA_ring","SVC_ring","IVC_ring",
											 	  "LSPV_ring","LIPV_ring","RSPV_ring","RIPV_ring"])
	tags_list_not_peri = [str(t) for t in tags_list_not_peri]
	tags_list_not_peri_string = ",".join(tags_list_not_peri)

	os.system("meshtool extract surface -msh="+mesh+" -surf="+presimFolder+"/peri_surface -ofmt=vtk -op="+tags_list_peri_string+"-"+tags_list_not_peri_string)
	os.system("meshtool extract unreachable -msh="+presimFolder+"/peri_surface.surfmesh -ifmt=vtk -ofmt=vtk -submsh="+presimFolder+"/peri_surface_CC")

def meshtool_extract_epi_endo_surfs(mesh,presimFolder,input_tags):
	os.system("meshtool extract surface -msh="+mesh+" -surf="+presimFolder+"surfaces_simulation/surface_heart -ofmt=carp_txt")
	os.system("meshtool extract unreachable -msh="+presimFolder+"surfaces_simulation/surface_heart.surfmesh -submsh="+presimFolder+"surfaces_simulation/surface_heart_CC -ofmt=carp_txt")

	tmp_files = os.listdir(presimFolder+"/surfaces_simulation/")
	surf_heart_CC = []
	i = 0
	isfile=True
	while isfile:
		if "surface_heart_CC.part"+str(i)+".elem" in tmp_files:
			surf_heart_CC.append("surface_heart_CC.part"+str(i))
		else: 
			isfile = False
		i += 1

	print("Checking connected component size and keeping only the 5 biggest...")
	if len(surf_heart_CC)>5:
		CC_size = np.zeros((len(surf_heart_CC),),dtype=int)
		for i,CC in enumerate(surf_heart_CC):
			surf = read_elem(presimFolder+"/surfaces_simulation/"+CC+".elem",el_type="Tr",tags=False)
			CC_size[i] = surf.shape[0]

		surf_heart_CC_old = copy.deepcopy(surf_heart_CC)
		sorted_size = np.argsort(CC_size)
		surf_heart_CC[0] = surf_heart_CC_old[sorted_size[-1]]
		surf_heart_CC[1] = surf_heart_CC_old[sorted_size[-2]]
		surf_heart_CC[2] = surf_heart_CC_old[sorted_size[-3]]
		surf_heart_CC[3] = surf_heart_CC_old[sorted_size[-4]]
		surf_heart_CC[4] = surf_heart_CC_old[sorted_size[-5]]

		for i in range(len(surf_heart_CC)-5):
			print("Removing extraneous surfaces...")
			os.system("rm "+presimFolder+"/surfaces_simulation/"+surf_heart_CC_old[sorted_size[i]]+".*")

	surf0 = read_elem(presimFolder+"/surfaces_simulation/"+surf_heart_CC[0]+".elem",el_type="Tr",tags=False)
	surf1 = read_elem(presimFolder+"/surfaces_simulation/"+surf_heart_CC[1]+".elem",el_type="Tr",tags=False)
	surf2 = read_elem(presimFolder+"/surfaces_simulation/"+surf_heart_CC[2]+".elem",el_type="Tr",tags=False)
	surf3 = read_elem(presimFolder+"/surfaces_simulation/"+surf_heart_CC[3]+".elem",el_type="Tr",tags=False)
	surf4 = read_elem(presimFolder+"/surfaces_simulation/"+surf_heart_CC[4]+".elem",el_type="Tr",tags=False)
	
	surfs = [surf0,surf1,surf2,surf3,surf4]

	pts0 = read_pts(presimFolder+"/surfaces_simulation/"+surf_heart_CC[0]+".pts")
	pts1 = read_pts(presimFolder+"/surfaces_simulation/"+surf_heart_CC[1]+".pts")
	pts2 = read_pts(presimFolder+"/surfaces_simulation/"+surf_heart_CC[2]+".pts")
	pts3 = read_pts(presimFolder+"/surfaces_simulation/"+surf_heart_CC[3]+".pts")
	pts4 = read_pts(presimFolder+"/surfaces_simulation/"+surf_heart_CC[4]+".pts")

	pts = [pts0,pts1,pts2,pts3,pts4]

	# Find CoGs of surfaces
	cog0 = find_cog_surf(pts[0])
	cog1 = find_cog_surf(pts[1])
	cog2 = find_cog_surf(pts[2])
	cog3 = find_cog_surf(pts[3])
	cog4 = find_cog_surf(pts[4])

	surf_cogs = [cog0,cog1,cog2,cog3,cog4]

	print("Finding the centre of gravity of each blood pool...")
	mesh_pts = read_pts(mesh+".pts")
	mesh_elem = read_elem(mesh+".elem",el_type="Tt",tags=True)

	lv_tag = extract_tags(input_tags,["LV"])
	cog_lv = find_cog_vol(mesh_pts,mesh_elem,lv_tag[0])
	print("LV centre of gravity found.")

	rv_tag = extract_tags(input_tags,["RV"])
	cog_rv = find_cog_vol(mesh_pts,mesh_elem,rv_tag[0])
	print("RV centre of gravity found.")

	la_tag = extract_tags(input_tags,["LA"])
	cog_la = find_cog_vol(mesh_pts,mesh_elem,la_tag[0])
	print("LA centre of gravity found.")

	ra_tag = extract_tags(input_tags,["RA"])
	cog_ra = find_cog_vol(mesh_pts,mesh_elem,ra_tag[0])
	print("RA centre of gravity found.")

	print("Searching for the epicardium by checking the direction of surface normals...")
	surf_orientated_out = False
	i = 0
	while surf_orientated_out == False:
		surf_orientated_out = query_outwards_surf(surfs[i],pts[i],surf_cogs[i])
		if surf_orientated_out == True:
			print("		"+surf_heart_CC[i]+' is the epicardium')
			ID_epi = i
		i += 1

	remaining_surf_list = list(range(5))
	remaining_surf_list.remove(ID_epi)

	surf_dist = []
	print("Finding distance between surf CoGs and LV CoG...")
	for i in remaining_surf_list:
		dist = calculate_dist(surf_cogs[i],cog_lv)
		surf_dist.append(dist)

	idx_ID_lv = np.argmin(surf_dist)
	ID_lv = remaining_surf_list[idx_ID_lv]
	print("		"+surf_heart_CC[ID_lv]+' is the LV endocardium')
	remaining_surf_list.remove(ID_lv)

	surf_dist = []
	print("Finding distance between surf CoGs and RV CoG...")
	for i in remaining_surf_list:
		dist = calculate_dist(surf_cogs[i],cog_rv)
		surf_dist.append(dist)

	idx_ID_rv = np.argmin(surf_dist)
	ID_rv = remaining_surf_list[idx_ID_rv]
	print("		"+surf_heart_CC[ID_rv]+' is the RV endocardium')
	remaining_surf_list.remove(ID_rv)

	surf_dist = []
	print("Finding distance between surf CoGs and LA CoG...")
	for i in remaining_surf_list:
		dist = calculate_dist(surf_cogs[i],cog_la)
		surf_dist.append(dist)

	idx_ID_la = np.argmin(surf_dist)
	ID_la = remaining_surf_list[idx_ID_la]
	print("		"+surf_heart_CC[ID_la]+' is the LA endocardium')
	remaining_surf_list.remove(ID_la)

	print("And therefore...")
	ID_ra = remaining_surf_list[0]
	print("		"+surf_heart_CC[ID_ra]+' is the RA endocardium')

	connected_component_to_surface(presimFolder+"/surfaces_simulation/"+surf_heart_CC[ID_epi],
								   presimFolder+"/surfaces_simulation/surface_heart.surf",
								   presimFolder+"/surfaces_simulation/epicardium")
	surf2vtk(mesh,
			 presimFolder+"/surfaces_simulation/epicardium.surf",
			 presimFolder+"/surfaces_simulation/epicardium.surf.vtk")

	connected_component_to_surface(presimFolder+"/surfaces_simulation/"+surf_heart_CC[ID_lv],
								   presimFolder+"/surfaces_simulation/surface_heart.surf",
								   presimFolder+"/surfaces_simulation/LV_endo")
	surf2vtk(mesh,
			 presimFolder+"/surfaces_simulation/LV_endo.surf",
			 presimFolder+"/surfaces_simulation/LV_endo.surf.vtk")

	connected_component_to_surface(presimFolder+"/surfaces_simulation/"+surf_heart_CC[ID_rv],
								   presimFolder+"/surfaces_simulation/surface_heart.surf",
								   presimFolder+"/surfaces_simulation/RV_endo")
	surf2vtk(mesh,
			 presimFolder+"/surfaces_simulation/RV_endo.surf",
			 presimFolder+"/surfaces_simulation/RV_endo.surf.vtk")

	connected_component_to_surface(presimFolder+"/surfaces_simulation/"+surf_heart_CC[ID_la],
								   presimFolder+"/surfaces_simulation/surface_heart.surf",
								   presimFolder+"/surfaces_simulation/LA_endo")
	surf2vtk(mesh,
			 presimFolder+"/surfaces_simulation/LA_endo.surf",
			 presimFolder+"/surfaces_simulation/LA_endo.surf.vtk")

	connected_component_to_surface(presimFolder+"/surfaces_simulation/"+surf_heart_CC[ID_ra],
								   presimFolder+"/surfaces_simulation/surface_heart.surf",
								   presimFolder+"/surfaces_simulation/RA_endo")
	surf2vtk(mesh,
			 presimFolder+"/surfaces_simulation/RA_endo.surf",
			 presimFolder+"/surfaces_simulation/RA_endo.surf.vtk")

def meshtool_extract_rings(mesh,presimFolder,input_tags):
	print("Extracting the RSPV ring and RIPV ring for use as boundary conditions...")
	tags_list_rpv_rings = extract_tags(input_tags,["RSPV_ring","RIPV_ring"])
	tags_list_rpv_rings = [str(t) for t in tags_list_rpv_rings]
	tags_list_rpv_rings_string = ",".join(tags_list_rpv_rings)

	tags_list_other = extract_tags(input_tags,["LV","RV","LA","RA",
											   "Ao","PArt",
											   "MV","TV","AV","PV",
											   "LSPV","LIPV","RSPV","RIPV",
											   "LAA","SVC","IVC",
											   "LAA_ring","SVC_ring","IVC_ring",
											   "LSPV_ring","LIPV_ring"])
	tags_list_other = [str(t) for t in tags_list_other]
	tags_list_other_string = ",".join(tags_list_other)

	os.system("meshtool extract surface -msh="+mesh+" -surf="+presimFolder+"/surfaces_simulation/surfaces_rings/RPVs -ofmt=vtk -op="+tags_list_rpv_rings_string+"-"+tags_list_other_string)

	print("Extracting the SVC ring for use as a boundary condition...")
	tags_list_svc_ring = extract_tags(input_tags,["SVC_ring"])
	tags_list_svc_ring = [str(t) for t in tags_list_svc_ring]
	tags_list_svc_ring_string = ",".join(tags_list_svc_ring)

	tags_list_other = extract_tags(input_tags,["LV","RV","LA","RA",
											   "Ao","PArt",
											   "MV","TV","AV","PV",
											   "LSPV","LIPV","RSPV","RIPV",
											   "LAA","SVC","IVC",
											   "LAA_ring","IVC_ring",
											   "LSPV_ring","LIPV_ring","RSPV_ring","RIPV_ring"])
	tags_list_other = [str(t) for t in tags_list_other]
	tags_list_other_string = ",".join(tags_list_other)

	os.system("meshtool extract surface -msh="+mesh+" -surf="+presimFolder+"/surfaces_simulation/surfaces_rings/SVC -ofmt=vtk -op="+tags_list_svc_ring_string+"-"+tags_list_other_string)

	print("Converting necessary surfs to vtx files...")
	rpvs_surface = np.loadtxt(presimFolder+"/surfaces_simulation/surfaces_rings/RPVs.surf",dtype=int,skiprows=1,usecols=[1,2,3])
	rpvs_vtx = surf2vtx(rpvs_surface)
	write_vtx(rpvs_vtx,presimFolder+"/surfaces_simulation/surfaces_rings/RPVs.surf.vtx")

	svc_surface = np.loadtxt(presimFolder+"/surfaces_simulation/surfaces_rings/RPVs.surf",dtype=int,skiprows=1,usecols=[1,2,3])
	svc_vtx = surf2vtx(svc_surface)
	write_vtx(svc_vtx,presimFolder+"/surfaces_simulation/surfaces_rings/SVC.surf.vtx")

def combine_elem_dats(heartFolder,presimFolder):
	la_map_dat=heartFolder+"/surfaces_uvc_LA/la/uvc/map_rotational_z.dat"
	ra_map_dat=heartFolder+"/surfaces_uvc_RA/ra/uvc/map_rotational_z.dat"

	os.system("cp "+la_map_dat+" "+presimFolder+"/map_rotational_z_la.dat")
	os.system("cp "+ra_map_dat+" "+presimFolder+"/map_rotational_z_ra.dat")

	os.system("meshtool interpolate node2elem "
						+"-omsh="+heartFolder+"/surfaces_uvc_LA/la/la "
						+"-idat="+presimFolder+"/map_rotational_z_la.dat "
						+"-odat="+presimFolder+"/map_rotational_z_la_e.dat")

	os.system("meshtool interpolate node2elem "
						+"-omsh="+heartFolder+"/surfaces_uvc_RA/ra/ra "
						+"-idat="+presimFolder+"/map_rotational_z_ra.dat "
						+"-odat="+presimFolder+"/map_rotational_z_ra_e.dat")

	os.system("meshtool insert data "
						+"-msh="+presimFolder+"/myocardium_AV_FEC_BB "
						+"-submsh="+heartFolder+"/surfaces_uvc_LA/la/la "
						+"-submsh_data="+presimFolder+"/map_rotational_z_la_e.dat "
						+"-odat="+presimFolder+"/elem_dat_UVC_ek_inc_la.dat "
						+"-mode=1")

	os.system("meshtool insert data "
						+"-msh="+presimFolder+"/myocardium_AV_FEC_BB "
						+"-submsh="+heartFolder+"/surfaces_uvc_RA/ra/ra "
						+"-submsh_data="+presimFolder+"/map_rotational_z_ra_e.dat "
						+"-odat="+presimFolder+"/elem_dat_UVC_ek_inc_ra.dat "
						+"-mode=1")

	combine_rot_coords(presimFolder)

	os.system("GlVTKConvert "
				+"-m "+presimFolder+"/myocardium_AV_FEC_BB "
				+"-e "+presimFolder+"/elem_dat_UVC_ek_combined.dat "
				+"-F bin "
				+"-o "+presimFolder+"/myocardium_AV_FEC_BB_elem_dat_UVC_combined "
				+"--trim-names")
