import os

from py_vent_fibres.file_utils import *
from py_vent_fibres.mesh_utils import *

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

def meshtool_extract_base(mesh,surf_folder,input_tags):

	tags_list_vent = extract_tags(input_tags,["LV","RV"])
	tags_list_vent = [str(t) for t in tags_list_vent]
	tags_list_vent_string = ",".join(tags_list_vent)

	tags_list_VPs = extract_tags(input_tags,["MV","TV","AV","PV"])
	tags_list_VPs = [str(t) for t in tags_list_VPs]
	tags_list_VPs_string = ",".join(tags_list_VPs)

	os.system("meshtool extract surface -msh="+mesh+" -surf="+surf_folder+"/tmp/myocardium.base -ofmt=vtk -op="+tags_list_vent_string+":"+tags_list_VPs_string)

def meshtool_extract_surfaces(mesh,surf_folder,input_tags):

	tags_list_vent = extract_tags(input_tags,["LV","RV"])
	tags_list_vent = [str(t) for t in tags_list_vent]
	tags_list_vent_string = ",".join(tags_list_vent)

	tags_list_VPs = extract_tags(input_tags,["MV","TV","AV","PV"])
	tags_list_VPs = [str(t) for t in tags_list_VPs]
	tags_list_VPs_string = ",".join(tags_list_VPs)

	os.system("meshtool extract surface -msh="+mesh+" -surf="+surf_folder+"/tmp/epi_endo -ofmt=vtk -op="+tags_list_vent_string+"-"+tags_list_VPs_string)
	os.system("meshtool extract unreachable -msh="+surf_folder+"/tmp/epi_endo.surfmesh -ifmt=vtk -ofmt=vtk -ofmt=carp_txt -submsh="+surf_folder+"/tmp/epi_endo_CC")

	tmp_files = os.listdir(surf_folder+"/tmp")
	epi_endo_CC = []
	i = 0
	isfile=True
	while isfile:
		if "epi_endo_CC.part"+str(i)+".elem" in tmp_files:
			epi_endo_CC.append("epi_endo_CC.part"+str(i))
		else: 
			isfile = False
		i += 1

	print("Checking connected component size and keeping only the 3 biggest...")
	if len(epi_endo_CC)>3:
		CC_size = np.zeros((len(epi_endo_CC),),dtype=int)
		for i,CC in enumerate(epi_endo_CC):
			surf = read_elem(surf_folder+"/tmp/"+CC+".elem",el_type="Tr",tags=False)
			CC_size[i] = surf.shape[0]

		epi_endo_CC_old = copy.deepcopy(epi_endo_CC)
		sorted_size = np.argsort(CC_size)
		epi_endo_CC[0] = epi_endo_CC_old[sorted_size[-1]]
		epi_endo_CC[1] = epi_endo_CC_old[sorted_size[-2]]
		epi_endo_CC[2] = epi_endo_CC_old[sorted_size[-3]]

		for i in range(len(epi_endo_CC)-3):
			os.system("rm "+surf_folder+"/tmp/"+epi_endo_CC_old[sorted_size[i]]+".*")

	# Find CoGs of surfaces
	pts0 = read_pts(surf_folder+"/tmp/"+epi_endo_CC[0]+".pts")
	surf0 = read_elem(surf_folder+"/tmp/"+epi_endo_CC[0]+".elem",el_type="Tr",tags=False)

	pts1 = read_pts(surf_folder+"/tmp/"+epi_endo_CC[1]+".pts")
	surf1 = read_elem(surf_folder+"/tmp/"+epi_endo_CC[1]+".elem",el_type="Tr",tags=False)

	pts2 = read_pts(surf_folder+"/tmp/"+epi_endo_CC[2]+".pts")
	surf2 = read_elem(surf_folder+"/tmp/"+epi_endo_CC[2]+".elem",el_type="Tr",tags=False)

	cog0 = np.mean(pts0,axis=0)
	cog1 = np.mean(pts1,axis=0)
	cog2 = np.mean(pts2,axis=0)

	# Find CoG for LV blood pool
	mesh_pts = read_pts(mesh+".pts")
	mesh_elem = read_elem(mesh+".elem",el_type="Tt",tags=True)

	lv_pts_idx = []
	for i,e in enumerate(mesh_elem):
		if e[4] == int(tags_list_vent[0]):	
			lv_pts_idx.append(int(e[1]))
			lv_pts_idx.append(int(e[2]))
			lv_pts_idx.append(int(e[3]))

	lv_pts_idx = np.unique(lv_pts_idx)
	lv_pts = np.zeros((lv_pts_idx.shape[0],3))

	for i,p in enumerate(lv_pts_idx):
		lv_pts[i] = mesh_pts[p]

	cog_lv = np.mean(lv_pts,axis=0)


	# Finding distance between surface CoGs and LV_BP CoG
	dist0 = np.zeros((1,3))
	dist1 = np.zeros((1,3))
	dist2 = np.zeros((1,3))

	for i,c in enumerate(cog_lv):
		dist0[:,i] = c - cog0[i]
		dist1[:,i] = c - cog1[i]
		dist2[:,i] = c - cog2[i]

	dist0 = np.linalg.norm(dist0)
	dist1 = np.linalg.norm(dist1)
	dist2 = np.linalg.norm(dist2)

	######## Checking orientation of surface normals on surf0 ########
	epi = 'not_yet_found'
	is_outward = np.zeros((surf0.shape[0],),dtype=int)
	for i,t in enumerate(surf0):
		v0 = pts0[t[1],:] - pts0[t[0],:]
		v0 = v0/np.linalg.norm(v0)

		v1 = pts0[t[2],:] - pts0[t[0],:]
		v1 = v1/np.linalg.norm(v1)

		n = np.cross(v0,v1)
		n = n/np.linalg.norm(n)

		dot_prod = np.dot(cog0-pts0[t[0],:],n)

		if dot_prod<0:
			is_outward[i] = 1

	if np.sum(is_outward)/surf0.shape[0]>0.7:
		print(epi_endo_CC[0]+' is the epicardium')
		epi = 0 
		
		if dist1 < dist2:
			print(epi_endo_CC[1]+' is the LV endocardium')
			print(epi_endo_CC[2]+' is the RV endocardium')
			lv_endo = 1
			rv_endo = 2
		else:
			print(epi_endo_CC[1]+' is the RV endocardium')
			print(epi_endo_CC[2]+' is the LV endocardium')
			rv_endo = 1
			lv_endo = 2

	if epi == 'not_yet_found':
		######## Checking orientation of surface normals on surf1 ########
		is_outward = np.zeros((surf1.shape[0],),dtype=int)
		for i,t in enumerate(surf1):
			v0 = pts1[t[1],:] - pts1[t[0],:]
			v0 = v0/np.linalg.norm(v0)

			v1 = pts1[t[2],:] - pts1[t[0],:]
			v1 = v1/np.linalg.norm(v1)

			n = np.cross(v0,v1)
			n = n/np.linalg.norm(n)

			dot_prod = np.dot(cog1-pts1[t[0],:],n)

			if dot_prod<0:
				is_outward[i] = 1

		if np.sum(is_outward)/surf1.shape[0]>0.7:
			print(epi_endo_CC[1]+' is the epicardium')
			epi = 1 
	
			if dist0 < dist2:
				print(epi_endo_CC[0]+' is the LV endocardium')
				print(epi_endo_CC[2]+' is the RV endocardium')
				lv_endo = 0
				rv_endo = 2
			else:
				print(epi_endo_CC[0]+' is the RV endocardium')
				print(epi_endo_CC[2]+' is the LV endocardium')
				rv_endo = 0
				lv_endo = 2

	if epi == 'not_yet_found':
		######## Checking orientation of surface normals on surf2 ########
		is_outward = np.zeros((surf2.shape[0],),dtype=int)
		for i,t in enumerate(surf2):
			v0 = pts2[t[1],:] - pts2[t[0],:]
			v0 = v0/np.linalg.norm(v0)

			v1 = pts2[t[2],:] - pts2[t[0],:]
			v1 = v1/np.linalg.norm(v1)

			n = np.cross(v0,v1)
			n = n/np.linalg.norm(n)

			dot_prod = np.dot(cog2-pts2[t[0],:],n)

			if dot_prod<0:
				is_outward[i] = 1

		if np.sum(is_outward)/surf2.shape[0]>0.7:
			print(epi_endo_CC[2]+' is the epicardium')
			epi = 2 
	
			if dist0 < dist1:
				print(epi_endo_CC[0]+' is the LV endocardium')
				print(epi_endo_CC[1]+' is the RV endocardium')
				lv_endo = 0
				rv_endo = 1
			else:
				print(epi_endo_CC[0]+' is the RV endocardium')
				print(epi_endo_CC[1]+' is the LV endocardium')
				rv_endo = 0
				lv_endo = 1


	if epi == 'not_yet_found':
		raise Exception("Surfaces could not be identified. Program terminated.")

	print('Renaming connected components...')
	formats = ["nod","eidx","elem","lon","pts"]
	for f in formats:
		os.system("mv "+surf_folder+"/tmp/"+epi_endo_CC[epi]+"."+f+" "+surf_folder+"/tmp/myocardium.epi."+f)
		os.system("mv "+surf_folder+"/tmp/"+epi_endo_CC[lv_endo]+"."+f+" "+surf_folder+"/tmp/myocardium.lvendo."+f)
		os.system("mv "+surf_folder+"/tmp/"+epi_endo_CC[rv_endo]+"."+f+" "+surf_folder+"/tmp/myocardium.rvendo."+f)

def meshtool_extract_septum(mesh,surf_folder,input_tags):

	tags_list_lv = extract_tags(input_tags,["LV"])
	tags_list_lv = [str(t) for t in tags_list_lv]
	tags_list_lv_string = ",".join(tags_list_lv)

	tags_list_remove = extract_tags(input_tags,["RV","RA","PArt"])
	tags_list_remove = [str(t) for t in tags_list_remove]
	tags_list_remove_string = ",".join(tags_list_remove)

	os.system("meshtool extract surface -msh="+mesh+" -surf="+surf_folder+"/tmp/myocardium.rvsept -ofmt=vtk -op="+tags_list_lv_string+"-"+tags_list_remove_string)
	os.system("meshtool extract unreachable -msh="+surf_folder+"/tmp/myocardium.rvsept.surfmesh -ifmt=vtk -ofmt=vtk -ofmt=carp_txt -submsh="+surf_folder+"/tmp/myocardium.rvsept_CC")

	tmp_files = os.listdir(surf_folder+"/tmp")
	rvsept_CC = []
	i = 0
	isfile=True
	while isfile:
		if "myocardium.rvsept_CC.part"+str(i)+".elem" in tmp_files:
			rvsept_CC.append("myocardium.rvsept_CC.part"+str(i))
		else: 
			isfile = False
		i += 1

	print("Checking connected component size and keeping only the 2 biggest...")
	if len(rvsept_CC)>2:
		CC_size = np.zeros((len(rvsept_CC),),dtype=int)
		for i,CC in enumerate(rvsept_CC):
			surf = read_elem(surf_folder+"/tmp/"+CC+".elem",el_type="Tr",tags=False)
			CC_size[i] = surf.shape[0]

		rvsept_CC_old = copy.deepcopy(rvsept_CC)
		sorted_size = np.argsort(CC_size)
		rv_sept_CC[0] = rvsept_CC_old[sorted_size[-1]]
		rv_sept_CC[1] = rvsept_CC_old[sorted_size[-2]]

		for i in range(len(epi_endo_CC)-2):
			os.system("rm "+surf_folder+"/tmp/"+rvsept_CC_old[sorted_size[i]]+".*")

	print('Renaming connected components...')
	formats = ["nod","eidx","elem","lon","pts"]
	for f in formats:
		os.system("mv "+surf_folder+"/tmp/"+rvsept_CC[0]+"."+f+" "+surf_folder+"/tmp/lvepi."+f)
		os.system("mv "+surf_folder+"/tmp/"+rvsept_CC[1]+"."+f+" "+surf_folder+"/tmp/myocardium.rvsept."+f)

def meshtool_extract_la_base(mesh,surf_folder,input_tags):
	tags_list_la = extract_tags(input_tags,["LA"])
	tags_list_la = [str(t) for t in tags_list_la]
	tags_list_la_string = ",".join(tags_list_la)

	tags_list_lv = extract_tags(input_tags,["LV"])
	tags_list_lv = [str(t) for t in tags_list_lv]
	tags_list_lv_string = ",".join(tags_list_lv)

	tags_list_mv = extract_tags(input_tags,["MV"])
	tags_list_mv = [str(t) for t in tags_list_mv]
	tags_list_mv_string = ",".join(tags_list_mv)

	os.system("meshtool extract surface -msh="+mesh+" -surf="+surf_folder+"/tmp/la.base -ofmt=vtk -op="+tags_list_la_string+":"+tags_list_mv_string+","+tags_list_lv_string)

def meshtool_extract_la_surfaces(mesh,surf_folder,input_tags):
	tags_list_la = extract_tags(input_tags,["LA"])
	tags_list_la = [str(t) for t in tags_list_la]
	tags_list_la_string = ",".join(tags_list_la)

	tags_list_lv = extract_tags(input_tags,["LV"])
	tags_list_lv = [str(t) for t in tags_list_lv]
	tags_list_lv_string = ",".join(tags_list_lv)

	tags_list_VPs = extract_tags(input_tags,["MV","TV","AV","PV","LSPV","LIPV","RSPV","RIPV","LAA","SVC","IVC"])
	tags_list_VPs = [str(t) for t in tags_list_VPs]
	tags_list_VPs_string = ",".join(tags_list_VPs)

	tags_list_rings = extract_tags(input_tags,["LSPV_ring","LIPV_ring","RSPV_ring","RIPV_ring","LAA_ring","SVC_ring","IVC_ring"])
	tags_list_rings = [str(t) for t in tags_list_rings]
	tags_list_rings_string = ",".join(tags_list_rings)

	os.system("meshtool extract surface -msh="+mesh+" -surf="+surf_folder+"/tmp/epi_endo -ofmt=vtk -op="+tags_list_la_string+"-"+tags_list_lv_string+","+tags_list_VPs_string+","+tags_list_rings_string)
	os.system("meshtool extract unreachable -msh="+surf_folder+"/tmp/epi_endo.surfmesh -ifmt=vtk -ofmt=vtk -ofmt=carp_txt -submsh="+surf_folder+"/tmp/epi_endo_CC")

	tmp_files = os.listdir(surf_folder+"/tmp")
	epi_endo_CC = []
	i = 0
	isfile=True
	while isfile:
		if "epi_endo_CC.part"+str(i)+".elem" in tmp_files:
			epi_endo_CC.append("epi_endo_CC.part"+str(i))
		else: 
			isfile = False
		i += 1

	print("Checking connected component size and keeping only the 2 biggest...")
	if len(epi_endo_CC)>2:
		CC_size = np.zeros((len(epi_endo_CC),),dtype=int)
		for i,CC in enumerate(epi_endo_CC):
			surf = read_elem(surf_folder+"/tmp/"+CC+".elem",el_type="Tr",tags=False)
			CC_size[i] = surf.shape[0]

		epi_endo_CC_old = copy.deepcopy(epi_endo_CC)
		sorted_size = np.argsort(CC_size)
		epi_endo_CC[0] = epi_endo_CC_old[sorted_size[-1]]
		epi_endo_CC[1] = epi_endo_CC_old[sorted_size[-2]]

		for i in range(len(epi_endo_CC)-2):
			os.system("rm "+surf_folder+"/tmp/"+epi_endo_CC_old[sorted_size[i]]+".*")

	# Find CoGs of surfaces
	pts0 = read_pts(surf_folder+"/tmp/"+epi_endo_CC[0]+".pts")
	surf0 = read_elem(surf_folder+"/tmp/"+epi_endo_CC[0]+".elem",el_type="Tr",tags=False)

	pts1 = read_pts(surf_folder+"/tmp/"+epi_endo_CC[1]+".pts")
	surf1 = read_elem(surf_folder+"/tmp/"+epi_endo_CC[1]+".elem",el_type="Tr",tags=False)

	cog0 = np.mean(pts0,axis=0)
	cog1 = np.mean(pts1,axis=0)

	######## Checking orientation of surface normals on surf0 ########
	is_outward = np.zeros((surf0.shape[0],),dtype=int)
	for i,t in enumerate(surf0):
		v0 = pts0[t[1],:] - pts0[t[0],:]
		v0 = v0/np.linalg.norm(v0)

		v1 = pts0[t[2],:] - pts0[t[0],:]
		v1 = v1/np.linalg.norm(v1)

		n = np.cross(v0,v1)
		n = n/np.linalg.norm(n)

		dot_prod = np.dot(cog0-pts0[t[0],:],n)

		if dot_prod<0:
			is_outward[i] = 1

	if np.sum(is_outward)/surf0.shape[0]>0.7:
		print(epi_endo_CC[0]+' is the epicardium')
		print(epi_endo_CC[1]+' is the endocardium')
		epi=0
		endo=1
	else:
		print(epi_endo_CC[0]+' is the endocardium')
		print(epi_endo_CC[1]+' is the epicardium')
		endo=0
		epi=1

	print('Renaming connected components...')
	formats = ["nod","eidx","elem","lon","pts"]
	for f in formats:
		os.system("mv "+surf_folder+"/tmp/"+epi_endo_CC[epi]+"."+f+" "+surf_folder+"/tmp/la.epi."+f)
		os.system("mv "+surf_folder+"/tmp/"+epi_endo_CC[endo]+"."+f+" "+surf_folder+"/tmp/la.lvendo."+f)

def meshtool_extract_ra_base(mesh,surf_folder,input_tags):
	tags_list_ra = extract_tags(input_tags,["RA"])
	tags_list_ra = [str(t) for t in tags_list_ra]
	tags_list_ra_string = ",".join(tags_list_ra)

	tags_list_rv = extract_tags(input_tags,["RV"])
	tags_list_rv = [str(t) for t in tags_list_rv]
	tags_list_rv_string = ",".join(tags_list_rv)

	tags_list_tv = extract_tags(input_tags,["TV"])
	tags_list_tv = [str(t) for t in tags_list_tv]
	tags_list_tv_string = ",".join(tags_list_tv)

	os.system("meshtool extract surface -msh="+mesh+" -surf="+surf_folder+"/tmp/ra.base -ofmt=vtk -op="+tags_list_ra_string+":"+tags_list_tv_string+","+tags_list_tv_string)

def meshtool_extract_ra_surfaces(mesh,surf_folder,input_tags):
	tags_list_ra = extract_tags(input_tags,["RA"])
	tags_list_ra = [str(t) for t in tags_list_ra]
	tags_list_ra_string = ",".join(tags_list_ra)

	tags_list_rv = extract_tags(input_tags,["RV"])
	tags_list_rv = [str(t) for t in tags_list_rv]
	tags_list_rv_string = ",".join(tags_list_rv)

	tags_list_VPs = extract_tags(input_tags,["MV","TV","AV","PV","LSPV","LIPV","RSPV","RIPV","LAA","SVC","IVC"])
	tags_list_VPs = [str(t) for t in tags_list_VPs]
	tags_list_VPs_string = ",".join(tags_list_VPs)

	tags_list_rings = extract_tags(input_tags,["LSPV_ring","LIPV_ring","RSPV_ring","RIPV_ring","LAA_ring","SVC_ring","IVC_ring"])
	tags_list_rings = [str(t) for t in tags_list_rings]
	tags_list_rings_string = ",".join(tags_list_rings)

	os.system("meshtool extract surface -msh="+mesh+" -surf="+surf_folder+"/tmp/epi_endo -ofmt=vtk -op="+tags_list_ra_string+"-"+tags_list_rv_string+","+tags_list_VPs_string+","+tags_list_rings_string)
	os.system("meshtool extract unreachable -msh="+surf_folder+"/tmp/epi_endo.surfmesh -ifmt=vtk -ofmt=vtk -ofmt=carp_txt -submsh="+surf_folder+"/tmp/epi_endo_CC")

	tmp_files = os.listdir(surf_folder+"/tmp")
	epi_endo_CC = []
	i = 0
	isfile=True
	while isfile:
		if "epi_endo_CC.part"+str(i)+".elem" in tmp_files:
			epi_endo_CC.append("epi_endo_CC.part"+str(i))
		else: 
			isfile = False
		i += 1

	print("Checking connected component size and keeping only the 2 biggest...")
	if len(epi_endo_CC)>2:
		CC_size = np.zeros((len(epi_endo_CC),),dtype=int)
		for i,CC in enumerate(epi_endo_CC):
			surf = read_elem(surf_folder+"/tmp/"+CC+".elem",el_type="Tr",tags=False)
			CC_size[i] = surf.shape[0]

		epi_endo_CC_old = copy.deepcopy(epi_endo_CC)
		sorted_size = np.argsort(CC_size)
		epi_endo_CC[0] = epi_endo_CC_old[sorted_size[-1]]
		epi_endo_CC[1] = epi_endo_CC_old[sorted_size[-2]]

		for i in range(len(epi_endo_CC)-2):
			os.system("rm "+surf_folder+"/tmp/"+epi_endo_CC_old[sorted_size[i]]+".*")

	# Find CoGs of surfaces
	pts0 = read_pts(surf_folder+"/tmp/"+epi_endo_CC[0]+".pts")
	surf0 = read_elem(surf_folder+"/tmp/"+epi_endo_CC[0]+".elem",el_type="Tr",tags=False)

	pts1 = read_pts(surf_folder+"/tmp/"+epi_endo_CC[1]+".pts")
	surf1 = read_elem(surf_folder+"/tmp/"+epi_endo_CC[1]+".elem",el_type="Tr",tags=False)

	cog0 = np.mean(pts0,axis=0)
	cog1 = np.mean(pts1,axis=0)

	######## Checking orientation of surface normals on surf0 ########
	is_outward = np.zeros((surf0.shape[0],),dtype=int)
	for i,t in enumerate(surf0):
		v0 = pts0[t[1],:] - pts0[t[0],:]
		v0 = v0/np.linalg.norm(v0)

		v1 = pts0[t[2],:] - pts0[t[0],:]
		v1 = v1/np.linalg.norm(v1)

		n = np.cross(v0,v1)
		n = n/np.linalg.norm(n)

		dot_prod = np.dot(cog0-pts0[t[0],:],n)

		if dot_prod<0:
			is_outward[i] = 1

	if np.sum(is_outward)/surf0.shape[0]>0.7:
		print(epi_endo_CC[0]+' is the epicardium')
		print(epi_endo_CC[1]+' is the endocardium')
		epi=0
		endo=1
	else:
		print(epi_endo_CC[0]+' is the endocardium')
		print(epi_endo_CC[1]+' is the epicardium')
		endo=0
		epi=1

	print('Renaming connected components...')
	formats = ["nod","eidx","elem","lon","pts"]
	for f in formats:
		os.system("mv "+surf_folder+"/tmp/"+epi_endo_CC[epi]+"."+f+" "+surf_folder+"/tmp/ra.epi."+f)
		os.system("mv "+surf_folder+"/tmp/"+epi_endo_CC[endo]+"."+f+" "+surf_folder+"/tmp/ra.lvendo."+f)

def mapping_surfaces(mesh,surf_folder,input_tags):
	connected_component_to_surface(surf_folder+'/tmp/myocardium.epi',surf_folder+'/tmp/epi_endo.surf',surf_folder+'/tmp/myocardium.epi')
	connected_component_to_surface(surf_folder+'/tmp/myocardium.lvendo',surf_folder+'/tmp/epi_endo.surf',surf_folder+'/tmp/myocardium.lvendo')
	connected_component_to_surface(surf_folder+'/tmp/myocardium.rvendo',surf_folder+'/tmp/epi_endo.surf',surf_folder+'/tmp/myocardium.rvendo')

	connected_component_to_surface(surf_folder+'/tmp/lvepi',surf_folder+'/tmp/myocardium.rvsept.surf',surf_folder+'/tmp/lvepi')
	connected_component_to_surface(surf_folder+'/tmp/myocardium.rvsept',surf_folder+'/tmp/myocardium.rvsept.surf',surf_folder+'/tmp/myocardium.rvsept')

	surf2vtk(mesh,surf_folder+'/tmp/myocardium.epi'+'.surf',surf_folder+'/tmp/myocardium.epi'+'.vtk')

def mapping_surfaces_la(mesh,surf_folder,input_tags):
	connected_component_to_surface(surf_folder+'/tmp/la.epi',surf_folder+'/tmp/epi_endo.surf',surf_folder+'/tmp/la.epi')
	connected_component_to_surface(surf_folder+'/tmp/la.lvendo',surf_folder+'/tmp/epi_endo.surf',surf_folder+'/tmp/la.lvendo')

	surf2vtk(mesh,surf_folder+'/tmp/la.epi'+'.surf',surf_folder+'/tmp/la.epi'+'.vtk')
	surf2vtk(mesh,surf_folder+'/tmp/la.lvendo'+'.surf',surf_folder+'/tmp/la.lvendo'+'.vtk')
	


def mapping_surfaces_ra(mesh,surf_folder,input_tags):
	connected_component_to_surface(surf_folder+'/tmp/ra.epi',surf_folder+'/tmp/epi_endo.surf',surf_folder+'/tmp/ra.epi')
	connected_component_to_surface(surf_folder+'/tmp/ra.lvendo',surf_folder+'/tmp/epi_endo.surf',surf_folder+'/tmp/ra.lvendo')

	surf2vtk(mesh,surf_folder+'/tmp/ra.epi'+'.surf',surf_folder+'/tmp/ra.epi'+'.vtk')
	surf2vtk(mesh,surf_folder+'/tmp/ra.lvendo'+'.surf',surf_folder+'/tmp/ra.lvendo'+'.vtk')
	


def picking_apex(segmentation,mesh,surf_folder,seg_tags):
	tags_list_lv = extract_tags(seg_tags,["LV_BP"])
	tags_list_la = extract_tags(seg_tags,["LA_BP"])
	lv_cavity = str(tags_list_lv[0])
	base = str(tags_list_la[0])

	pts = mesh+'.pts'
	vtx = surf_folder+'/tmp/myocardium.epi.vtx'

	os.system("pickapex "+segmentation+" "+lv_cavity+" "+base+" "+pts+" "+vtx+" > "+surf_folder+"/myocardium.apex.vtx")

def meshtool_extract_biv(mesh,surf_folder,input_tags):
	tags_list_lv = extract_tags(input_tags,["LV"])
	tags_list_lv = [str(t) for t in tags_list_lv]
	tags_list_lv_string = ",".join(tags_list_lv)

	tags_list_rv = extract_tags(input_tags,["RV"])
	tags_list_rv = [str(t) for t in tags_list_rv]
	tags_list_rv_string = ",".join(tags_list_rv)

	os.system("meshtool extract mesh -msh="+mesh+" -submsh="+surf_folder+"/BiV/BiV -tags="+tags_list_lv_string+","+tags_list_rv_string)

def meshtool_map_vtx(surf_folder):
	os.system("meshtool map -submsh="+surf_folder+"/BiV/BiV"
				  			+" -files="+surf_folder+"/myocardium.apex.vtx,"
				  					   +surf_folder+"/tmp/myocardium.base.surf.vtx,"
				  					   +surf_folder+"/tmp/myocardium.epi.surf.vtx,"
				  					   +surf_folder+"/tmp/myocardium.lvendo.surf.vtx,"
				  					   +surf_folder+"/tmp/myocardium.rvendo.surf.vtx,"
				  					   +surf_folder+"/tmp/myocardium.rvendo_nosept.surf.vtx,"
				  					   +surf_folder+"/tmp/myocardium.rvsept.surf.vtx"
				  			+" -outdir="+surf_folder+"/BiV")

	os.system("meshtool map -submsh="+surf_folder+"/BiV/BiV"
				  			+" -files="+surf_folder+"/tmp/myocardium.base.surf,"
				  					   +surf_folder+"/tmp/myocardium.epi.surf,"
				  					   +surf_folder+"/tmp/myocardium.lvendo.surf,"
				  					   +surf_folder+"/tmp/myocardium.rvendo.surf,"
				  					   +surf_folder+"/tmp/myocardium.rvendo_nosept.surf,"
				  					   +surf_folder+"/tmp/myocardium.rvsept.surf" 
				  			+" -outdir="+surf_folder+"/BiV")

def renaming_myo_files(surf_folder):
	os.system("mv "+surf_folder+"/BiV/myocardium.base.surf "+surf_folder+"/BiV/BiV.base.surf")
	os.system("mv "+surf_folder+"/BiV/myocardium.apex.vtx "+surf_folder+"/BiV/BiV.apex.vtx")
	os.system("mv "+surf_folder+"/BiV/myocardium.base.surf.vtx "+surf_folder+"/BiV/BiV.base.surf.vtx")
	os.system("mv "+surf_folder+"/BiV/myocardium.epi.surf "+surf_folder+"/BiV/BiV.epi.surf")
	os.system("mv "+surf_folder+"/BiV/myocardium.epi.surf.vtx "+surf_folder+"/BiV/BiV.epi.surf.vtx")
	os.system("mv "+surf_folder+"/BiV/myocardium.lvendo.surf "+surf_folder+"/BiV/BiV.lvendo.surf")
	os.system("mv "+surf_folder+"/BiV/myocardium.lvendo.surf.vtx "+surf_folder+"/BiV/BiV.lvendo.surf.vtx")
	os.system("mv "+surf_folder+"/BiV/myocardium.rvendo.surf "+surf_folder+"/BiV/BiV.rvendo.surf")
	os.system("mv "+surf_folder+"/BiV/myocardium.rvendo.surf.vtx "+surf_folder+"/BiV/BiV.rvendo.surf.vtx")
	os.system("mv "+surf_folder+"/BiV/myocardium.rvendo_nosept.surf.vtx "+surf_folder+"/BiV/BiV.rvendo_nosept.surf.vtx")
	os.system("mv "+surf_folder+"/BiV/myocardium.rvendo_nosept.surf "+surf_folder+"/BiV/BiV.rvendo_nosept.surf")
	os.system("mv "+surf_folder+"/BiV/myocardium.rvsept.surf.vtx "+surf_folder+"/BiV/BiV.rvsept.surf.vtx")
	os.system("mv "+surf_folder+"/BiV/myocardium.rvsept.surf "+surf_folder+"/BiV/BiV.rvsept.surf")

def meshtool_extract_la(mesh,surf_folder,input_tags):
	tags_list_la = extract_tags(input_tags,["LA"])
	tags_list_la_string = str(tags_list_la[0])
	os.system("meshtool extract mesh -msh="+mesh+" -submsh="+surf_folder+"/la/la -tags="+tags_list_la_string)

def meshtool_map_vtx_la(surf_folder):
	os.system("meshtool map -submsh="+surf_folder+"/la/la"
							+" -files="+surf_folder+"/tmp/la.apex.vtx,"
									   +surf_folder+"/tmp/la.base.surf.vtx,"
									   +surf_folder+"/tmp/la.epi.vtx,"
									   +surf_folder+"/tmp/la.lvendo.vtx"
							+" -outdir="+surf_folder+"/la")

	os.system("meshtool convert -imsh="+surf_folder+"/la/la -omsh="+surf_folder+"/la/la -ofmt=vtk_bin")


def meshtool_extract_ra(mesh,surf_folder,input_tags):
	tags_list_ra = extract_tags(input_tags,["RA"])
	tags_list_ra_string = str(tags_list_ra[0])
	os.system("meshtool extract mesh -msh="+mesh+" -submsh="+surf_folder+"/ra/ra -tags="+tags_list_ra_string)

def meshtool_map_vtx_ra(surf_folder):
	os.system("meshtool map -submsh="+surf_folder+"/ra/ra" 
						  " -files="+surf_folder+"/tmp/ra.apex.vtx,"
						  			+surf_folder+"/tmp/ra.base.surf.vtx,"
						  			+surf_folder+"/tmp/ra.epi.vtx,"
						  			+surf_folder+"/tmp/ra.lvendo.vtx"
						  " -outdir="+surf_folder+"/ra")

	os.system("meshtool convert -imsh="+surf_folder+"/ra/ra -omsh="+surf_folder+"/ra/ra -ofmt=vtk_bin")

