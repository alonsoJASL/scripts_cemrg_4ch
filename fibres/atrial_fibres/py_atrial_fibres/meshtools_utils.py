import os
import sys
import numpy as np
import copy
import meshio

from py_atrial_fibres.file_utils import *
from py_atrial_fibres.distance_utils import *

def extract_tags(tags_setup,
				 labels):
	
	tags_list = []
	for l in labels:
		if type(tags_setup[l])==int:
			tags_list += [tags_setup[l]]
		elif type(tags_setup[l])==np.ndarray:
			tags_list += list(tags_setup[l])
		else:
			raise Exception("Type not recognised.")

	return tags_list

def meshtool_extract_biatrial(meshname,
							  output_folder,
							  tags_setup,
							  overwrite=False):
	
	do = True
	if os.path.exists(output_folder+'/biatrial/biatrial.pts') and not overwrite:
		do = False
		print('Mesh already found. Not overwriting.')

	if do:	
		tags_list = extract_tags(tags_setup,["LA","RA"])
		tags_list = [str(t) for t in tags_list]
		tags_list_string = ",".join(tags_list)	

		print("----------------------------")
		print("Extracting biatrial mesh...")
		print("----------------------------")	

		cmd = "meshtool extract mesh -msh="+meshname+" -submsh="+output_folder+"/biatrial/biatrial -tags="+tags_list_string
		print(cmd)
		os.system(cmd)

def meshtool_extract_LA(output_folder,
						tags_setup,
						overwrite=False):

	do = True
	if os.path.exists(output_folder+'/la/la.pts') and not overwrite:
		do = False
		print('Mesh already found. Not overwriting.')

	if do:
		tags_list = extract_tags(tags_setup,["LA"])
		tags_list = [str(t) for t in tags_list]
		tags_list_string = ",".join(tags_list)
		
		print("--------------------------------------")
		print("Extracting LA mesh from biatrial...")
		print("--------------------------------------")
		
		cmd = "meshtool extract mesh -msh="+output_folder+"/biatrial/biatrial -submsh="+output_folder+"/la/la -tags="+tags_list_string
		os.system(cmd)

def meshtool_extract_RA(output_folder,
						tags_setup,
						overwrite=False):

	do = True
	if os.path.exists(output_folder+'/ra/ra.pts') and not overwrite:
		do = False
		print('Mesh already found. Not overwriting.')

	if do:
		tags_list = extract_tags(tags_setup,["RA"])
		tags_list = [str(t) for t in tags_list]
		tags_list_string = ",".join(tags_list)
		
		print("--------------------------------------")
		print("Extracting RA mesh from biatrial...")
		print("--------------------------------------")
		
		cmd = "meshtool extract mesh -msh="+output_folder+"/biatrial/biatrial -submsh="+output_folder+"/ra/ra -tags="+tags_list_string
		os.system(cmd)

def meshtool_extract_surfaces(meshname,
		 					  output_folder,
		 					  tags_setup,
		 					  export_sup_inf=False,
		 					  rm_vv_from_aa=False,
		 					  surface="epi"):

	tag_la = extract_tags(tags_setup,["LA"])
	tag_la = [str(t) for t in tag_la]
	tag_la_string = ",".join(tag_la)

	tag_ra = extract_tags(tags_setup,["RA"])
	tag_ra = [str(t) for t in tag_ra]
	tag_ra_string = ",".join(tag_ra)

	if not rm_vv_from_aa:
		tag_la_rm = extract_tags(tags_setup,["mitral","RSPV","RIPV","LSPV","LIPV","LAA","PV_planes"])
	else:
		tag_la_rm = extract_tags(tags_setup,["mitral","RSPV","RIPV","LSPV","LIPV","LAA","PV_planes","LV"])
	tag_la_rm = [str(t) for t in tag_la_rm]
	tag_la_rm_string = ",".join(tag_la_rm)

	if not rm_vv_from_aa:
		tag_ra_rm = extract_tags(tags_setup,["SVC","IVC","tricuspid","VC_planes"])
	else:
		tag_ra_rm = extract_tags(tags_setup,["SVC","IVC","tricuspid","VC_planes","RV"])
	tag_ra_rm = [str(t) for t in tag_ra_rm]
	tag_ra_rm_string = ",".join(tag_ra_rm)

	tag_mv = extract_tags(tags_setup,["mitral"])
	tag_mv = [str(t) for t in tag_mv]
	tag_mv_string = ",".join(tag_mv)

	tag_tv = extract_tags(tags_setup,["tricuspid"])
	tag_tv = [str(t) for t in tag_tv]
	tag_tv_string = ",".join(tag_tv)

	tag_rpv = extract_tags(tags_setup,["RSPV","RIPV"])
	tag_rpv = [str(t) for t in tag_rpv]
	tag_rpv_string = ",".join(tag_rpv)

	tag_svc = extract_tags(tags_setup,["SVC"])
	tag_svc = [str(t) for t in tag_svc]
	tag_svc_string = ",".join(tag_svc)

	tag_lpv = extract_tags(tags_setup,["LSPV","LIPV"])
	tag_lpv = [str(t) for t in tag_lpv]
	tag_lpv_string = ",".join(tag_lpv)

	tag_ivc = extract_tags(tags_setup,["IVC"])
	tag_ivc = [str(t) for t in tag_ivc]
	tag_ivc_string = ",".join(tag_ivc)

	tag_pv_planes = extract_tags(tags_setup,["PV_planes"])
	tag_pv_planes = [str(t) for t in tag_pv_planes]
	tag_pv_planes_string = ",".join(tag_pv_planes)

	tag_vc_planes = extract_tags(tags_setup,["VC_planes"])
	tag_vc_planes = [str(t) for t in tag_vc_planes]
	tag_vc_planes_string = ",".join(tag_vc_planes)

	tag_lv = extract_tags(tags_setup,["LV"])
	tag_lv = [str(t) for t in tag_lv]
	tag_lv_string = ",".join(tag_lv)

	tag_rv = extract_tags(tags_setup,["RV"])
	tag_rv = [str(t) for t in tag_rv]
	tag_rv_string = ",".join(tag_rv)

	os.system("mkdir -p "+output_folder+"/tmp")

	print("--------------------------")
	print("Extracting mitral ring...")
	print("--------------------------")
	cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/mitral -op="+tag_la_string+":"+tag_mv_string+" -ofmt=vtk"
	os.system(cmd)

	print("--------------------------")
	print("Extracting right PV ring...")
	print("--------------------------")
	cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/rpv -op="+tag_la_string+":"+tag_rpv_string+" -ofmt=vtk"
	os.system(cmd)

	print("--------------------------")
	print("Extracting left PV ring...")
	print("--------------------------")
	cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/lpv -op="+tag_la_string+":"+tag_lpv_string+" -ofmt=vtk"
	os.system(cmd)

	if export_sup_inf:

		tag_rspv = extract_tags(tags_setup,["RSPV"])
		tag_rspv = [str(t) for t in tag_rspv]
		tag_rspv_string = ",".join(tag_rspv)	

		tag_ripv = extract_tags(tags_setup,["RIPV"])
		tag_ripv = [str(t) for t in tag_ripv]
		tag_ripv_string = ",".join(tag_ripv)	

		tag_lspv = extract_tags(tags_setup,["LSPV"])
		tag_lspv = [str(t) for t in tag_lspv]
		tag_lspv_string = ",".join(tag_lspv)	

		tag_lipv = extract_tags(tags_setup,["LIPV"])
		tag_lipv = [str(t) for t in tag_lipv]
		tag_lipv_string = ",".join(tag_lipv)

		tag_laa = extract_tags(tags_setup,["LAA"])
		tag_laa = [str(t) for t in tag_laa]
		tag_laa_string = ",".join(tag_laa)

		print("------------------------------------------")
		print("Extracting LAA ring...")
		print("------------------------------------------")
		cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/laa -op="+tag_la_string+":"+tag_laa_string+" -ofmt=vtk"
		os.system(cmd)	

		print("------------------------------------------")
		print("Extracting right inferior PV ring...")
		print("------------------------------------------")
		cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/ripv -op="+tag_la_string+":"+tag_ripv_string+" -ofmt=vtk"
		os.system(cmd)	

		print("------------------------------------------")
		print("Extracting left inferior PV ring...")
		print("------------------------------------------")
		cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/lipv -op="+tag_la_string+":"+tag_lipv_string+" -ofmt=vtk"
		os.system(cmd)

		print("------------------------------------------")
		print("Extracting right superior PV ring...")
		print("------------------------------------------")
		cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/rspv -op="+tag_la_string+":"+tag_rspv_string+" -ofmt=vtk"
		os.system(cmd)	

		print("------------------------------------------")
		print("Extracting left superior PV ring...")
		print("------------------------------------------")
		cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/lspv -op="+tag_la_string+":"+tag_lspv_string+" -ofmt=vtk"
		os.system(cmd)


	print("--------------------------")
	print("Extracting PV planes...")
	print("--------------------------")
	cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/pv_planes -op="+tag_la_string+":"+tag_pv_planes_string+" -ofmt=vtk"
	os.system(cmd)

	if export_sup_inf and surface=="endo":

		if "RSPV_vp" not in tags_setup:
			raise Exception("If you want to compute the landmarks on the endocardium, you need to provide separate tags for the valve planes")

		tag_rspv_vp = extract_tags(tags_setup,["RSPV_vp"])
		tag_rspv_vp = [str(t) for t in tag_rspv_vp]
		tag_rspv_vp_string = ",".join(tag_rspv_vp)	

		tag_ripv_vp = extract_tags(tags_setup,["RIPV_vp"])
		tag_ripv_vp = [str(t) for t in tag_ripv_vp]
		tag_ripv_vp_string = ",".join(tag_ripv_vp)	

		tag_lspv_vp = extract_tags(tags_setup,["LSPV_vp"])
		tag_lspv_vp = [str(t) for t in tag_lspv_vp]
		tag_lspv_vp_string = ",".join(tag_lspv_vp)	

		tag_lipv_vp = extract_tags(tags_setup,["LIPV_vp"])
		tag_lipv_vp = [str(t) for t in tag_lipv_vp]
		tag_lipv_vp_string = ",".join(tag_lipv_vp)

		tag_laa_vp = extract_tags(tags_setup,["LAA_vp"])
		tag_laa_vp = [str(t) for t in tag_laa_vp]
		tag_laa_vp_string = ",".join(tag_laa_vp)

		print("------------------------------------------")
		print("Extracting LAA valve plane...")
		print("------------------------------------------")
		cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/laa_vp -op="+tag_la_string+":"+tag_laa_vp_string+" -ofmt=vtk"
		os.system(cmd)	

		print("------------------------------------------")
		print("Extracting right inferior PV valve plane...")
		print("------------------------------------------")
		cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/ripv_vp -op="+tag_la_string+":"+tag_ripv_vp_string+" -ofmt=vtk"
		os.system(cmd)	

		print("------------------------------------------")
		print("Extracting left inferior PV valve plane...")
		print("------------------------------------------")
		cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/lipv_vp -op="+tag_la_string+":"+tag_lipv_vp_string+" -ofmt=vtk"
		os.system(cmd)

		print("------------------------------------------")
		print("Extracting right superior PV valve plane...")
		print("------------------------------------------")
		cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/rspv_vp -op="+tag_la_string+":"+tag_rspv_vp_string+" -ofmt=vtk"
		os.system(cmd)	

		print("------------------------------------------")
		print("Extracting left superior PV valve plane...")
		print("------------------------------------------")
		cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/lspv_vp -op="+tag_la_string+":"+tag_lspv_vp_string+" -ofmt=vtk"
		os.system(cmd)

	print("--------------------------")
	print("Extracting LA surface...")
	print("--------------------------")
	cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/la -op="+tag_la_string+"-"+tag_la_rm_string+" -ofmt=vtk"
	os.system(cmd)

	print("------------------------------------")
	print("Extracting LA and LV intersection...")
	print("------------------------------------")
	cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/la_lv -op="+tag_la_string+":"+tag_lv_string+" -ofmt=vtk"
	os.system(cmd)

	print("--------------------------")
	print("Extracting tricuspid ring...")
	print("--------------------------")
	cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/tricuspid -op="+tag_ra_string+":"+tag_tv_string+" -ofmt=vtk"
	os.system(cmd)

	print("--------------------------")
	print("Extracting SVC ring...")
	print("--------------------------")
	cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/svc -op="+tag_ra_string+":"+tag_svc_string+" -ofmt=vtk"
	os.system(cmd)

	print("--------------------------")
	print("Extracting IVC ring...")
	print("--------------------------")
	cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/ivc -op="+tag_ra_string+":"+tag_ivc_string+" -ofmt=vtk"
	os.system(cmd)

	if surface=="endo":

		if "SVC_vp" not in tags_setup:
			raise Exception("If you want to compute the landmarks on the endocardium, you need to provide separate tags for the valve planes")

		tag_svc_vp = extract_tags(tags_setup,["SVC_vp"])
		tag_svc_vp = [str(t) for t in tag_svc_vp]
		tag_svc_vp_string = ",".join(tag_svc_vp)	

		tag_ivc_vp = extract_tags(tags_setup,["IVC_vp"])
		tag_ivc_vp = [str(t) for t in tag_ivc_vp]
		tag_ivc_vp_string = ",".join(tag_ivc_vp)	

		print("--------------------------")
		print("Extracting SVC valve plane...")
		print("--------------------------")
		cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/svc_vp -op="+tag_ra_string+":"+tag_svc_vp_string+" -ofmt=vtk"
		os.system(cmd)

		print("--------------------------")
		print("Extracting IVC valve plane...")
		print("--------------------------")
		cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/ivc_vp -op="+tag_ra_string+":"+tag_ivc_vp_string+" -ofmt=vtk"
		os.system(cmd)

	print("--------------------------")
	print("Extracting PV planes...")
	print("--------------------------")
	cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/pv_planes -op="+tag_la_string+":"+tag_pv_planes_string+" -ofmt=vtk"
	os.system(cmd)

	print("--------------------------")
	print("Extracting SVC IVC planes...")
	print("--------------------------")
	cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/vc_planes -op="+tag_ra_string+":"+tag_vc_planes_string+" -ofmt=vtk"
	os.system(cmd)

	print("------------------------------------")
	print("Extracting RA and RV intersection...")
	print("------------------------------------")
	cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/ra_rv -op="+tag_ra_string+":"+tag_rv_string+" -ofmt=vtk"
	os.system(cmd)

	print("--------------------------")
	print("Extracting RA surface...")
	print("--------------------------")
	cmd = "meshtool extract surface -msh="+meshname+" -surf="+output_folder+"/tmp/ra -op="+tag_ra_string+"-"+tag_ra_rm_string+" -ofmt=vtk"
	os.system(cmd)

	print("-----------------------------------------------")
	print("Extracting LA surface connected components...")
	print("-----------------------------------------------")
	cmd = "meshtool extract unreachable -msh="+output_folder+"/tmp/la.surfmesh.vtk -submsh="+output_folder+"/tmp/la_cc -ofmt=carp_txt"
	os.system(cmd)

	print("-----------------------------------------------")
	print("Extracting RA surface connected components...")
	print("-----------------------------------------------")
	cmd = "meshtool extract unreachable -msh="+output_folder+"/tmp/ra.surfmesh.vtk -submsh="+output_folder+"/tmp/ra_cc -ofmt=carp_txt"
	os.system(cmd)

	tmp_files = os.listdir(output_folder+"/tmp")
	la_cc = []
	i = 0
	isfile=True
	while isfile:
		if "la_cc.part"+str(i)+".elem" in tmp_files:
			la_cc.append("la_cc.part"+str(i))
		else: 
			isfile = False
		i += 1

	ra_cc = []
	i = 0
	isfile=True
	while isfile:
		if "ra_cc.part"+str(i)+".elem" in tmp_files:
			ra_cc.append("ra_cc.part"+str(i))
		else: 
			isfile = False
		i += 1

	print("Checking connected component size and keeping only the two biggest...")
	if len(la_cc)>2:
		cc_size = np.zeros((len(la_cc),),dtype=int)
		for i,cc in enumerate(la_cc):
			surf = read_elem(output_folder+"/tmp/"+cc+".elem",el_type="Tr",tags=False)
			cc_size[i] = surf.shape[0]

		la_cc_old = copy.deepcopy(la_cc)
		sorted_size = np.argsort(cc_size)
		la_cc[0] = la_cc_old[sorted_size[-1]]
		la_cc[1] = la_cc_old[sorted_size[-2]]

		for i in range(len(la_cc)-2):
			os.system("rm "+output_folder+"/tmp/"+la_cc_old[sorted_size[i]]+".*")

	if len(ra_cc)>2:
		cc_size = np.zeros((len(ra_cc),),dtype=int)
		for i,cc in enumerate(ra_cc):
			surf = read_elem(output_folder+"/tmp/"+cc+".elem",el_type="Tr",tags=False)
			cc_size[i] = surf.shape[0]

		ra_cc_old = copy.deepcopy(ra_cc)
		sorted_size = np.argsort(cc_size)
		ra_cc[0] = la_cc_old[sorted_size[-1]]
		ra_cc[1] = la_cc_old[sorted_size[-2]]

		for i in range(len(ra_cc)-2):
			os.system("rm "+output_folder+"/tmp/"+ra_cc_old[sorted_size[i]]+".*")

	pts0 = read_pts(output_folder+"/tmp/"+la_cc[0]+".pts")
	surf0 = read_elem(output_folder+"/tmp/"+la_cc[0]+".elem",el_type="Tr",tags=False)

	pts1 = read_pts(output_folder+"/tmp/"+la_cc[1]+".pts")
	surf1 = read_elem(output_folder+"/tmp/"+la_cc[1]+".elem",el_type="Tr",tags=False)

	cog0 = np.mean(pts0,axis=0)
	is_outward = np.zeros((surf0.shape[0],),dtype=int)
	for i,t in enumerate(surf0):
		v0 = pts0[t[1],:] - pts0[t[0],:]
		v0 = v0/np.linalg.norm(v0)

		v1 = pts0[t[2],:] - pts0[t[0],:]
		v1 = v1/np.linalg.norm(v1)

		n = np.cross(v0,v1)
		n = n/np.linalg.norm(n)

		dot_prod = np.dot(cog0-pts0[t[0],:],n)

		if dot_prod>0:
			is_outward[i] = 1

	if np.sum(is_outward)/surf0.shape[0]>0.7:
		print(la_cc[0]+' is the epicardium')
		print(la_cc[1]+' is the endocardium')
		endo = 0
		epi = 1
	else:
		print(la_cc[1]+' is the epicardium')
		print(la_cc[0]+' is the endocardium')	
		endo = 1
		epi = 0

	print('Renaming LA connected components...')
	formats = ["nod","eidx","elem","lon","pts"]
	for f in formats:
		os.system("mv "+output_folder+"/tmp/"+la_cc[endo]+"."+f+" "+output_folder+"/tmp/la_endo."+f)
		os.system("mv "+output_folder+"/tmp/"+la_cc[epi]+"."+f+" "+output_folder+"/tmp/la_epi."+f)

	pts0 = read_pts(output_folder+"/tmp/"+ra_cc[0]+".pts")
	surf0 = read_elem(output_folder+"/tmp/"+ra_cc[0]+".elem",el_type="Tr",tags=False)

	pts1 = read_pts(output_folder+"/tmp/"+ra_cc[1]+".pts")
	surf1 = read_elem(output_folder+"/tmp/"+ra_cc[1]+".elem",el_type="Tr",tags=False)

	cog0 = np.mean(pts0,axis=0)
	is_outward = np.zeros((surf0.shape[0],),dtype=int)
	for i,t in enumerate(surf0):
		v0 = pts0[t[1],:] - pts0[t[0],:]
		v0 = v0/np.linalg.norm(v0)

		v1 = pts0[t[2],:] - pts0[t[0],:]
		v1 = v1/np.linalg.norm(v1)

		n = np.cross(v0,v1)
		n = n/np.linalg.norm(n)

		dot_prod = np.dot(cog0-pts0[t[0],:],n)

		if dot_prod>0:
			is_outward[i] = 1

	if np.sum(is_outward)/surf0.shape[0]>0.7:
		print(ra_cc[0]+' is the epicardium')
		print(ra_cc[1]+' is the endocardium')
		endo = 0
		epi = 1
	else:
		print(ra_cc[1]+' is the epicardium')
		print(ra_cc[0]+' is the endocardium')	
		endo = 1
		epi = 0

	print('Renaming RA connected components...')
	formats = ["nod","eidx","elem","lon","pts"]
	for f in formats:
		os.system("mv "+output_folder+"/tmp/"+ra_cc[endo]+"."+f+" "+output_folder+"/tmp/ra_endo."+f)
		os.system("mv "+output_folder+"/tmp/"+ra_cc[epi]+"."+f+" "+output_folder+"/tmp/ra_epi."+f)

def export_LA_vtk_msh(output_folder,
					  tags_setup):

	tets = read_elem(output_folder+"/la/la.elem",el_type="Tt",tags=False)
	pts = read_pts(output_folder+"/la/la.pts")
	
	surface_list = [output_folder+"/tmp/la.surf",
					output_folder+"/tmp/mitral.surf",
					output_folder+"/tmp/rpv.surf",
					output_folder+"/tmp/lpv.surf",
					output_folder+"/tmp/pv_planes.surf",
					output_folder+"/tmp/la_lv.surf"]

	surface_list_string = ','.join(surface_list)

	surface_bia_list = [output_folder+"/biatrial/la.surf",
						output_folder+"/biatrial/mitral.surf",
						output_folder+"/biatrial/rpv.surf",
						output_folder+"/biatrial/lpv.surf",
						output_folder+"/biatrial/pv_planes.surf",
						output_folder+"/biatrial/la_lv.surf"]
	surface_bia_list_string = ','.join(surface_bia_list)

	print('Mapping surfaces onto biatrial mesh...')
	cmd = "meshtool map -submsh="+output_folder+"/biatrial/biatrial -files="+surface_list_string+" -outdir="+output_folder+"/biatrial/ -mode=m2s"
	os.system(cmd)

	print('Mapping surfaces onto LA mesh...')
	cmd = "meshtool map -submsh="+output_folder+"/la/la -files="+surface_bia_list_string+" -outdir="+output_folder+"/la/ -mode=m2s"
	os.system(cmd)

	la_tr = read_elem(output_folder+"/la/la.surf",el_type="Tr",tags=False)

	la_endo_eidx = read_nod_eidx(output_folder+"/tmp/la_endo.eidx")
	la_epi_eidx = read_nod_eidx(output_folder+"/tmp/la_epi.eidx")

	la_endo_tr = la_tr[la_endo_eidx,:]
	la_epi_tr = la_tr[la_epi_eidx,:]

	write_surf(output_folder+"/la/la_epi.surf",la_epi_tr)
	write_surf(output_folder+"/la/la_endo.surf",la_endo_tr)

	mitral_tr = read_elem(output_folder+"/la/mitral.surf",el_type="Tr",tags=False)
	rpv_tr = read_elem(output_folder+"/la/rpv.surf",el_type="Tr",tags=False)
	lpv_tr = read_elem(output_folder+"/la/lpv.surf",el_type="Tr",tags=False)
	pv_planes_tr = read_elem(output_folder+"/la/pv_planes.surf",el_type="Tr",tags=False)
	la_lv_tr = read_elem(output_folder+"/la/la_lv.surf",el_type="Tr",tags=False)

	la_endo_tr = np.concatenate((la_endo_tr,pv_planes_tr),axis=0)
	la_epi_tr = np.concatenate((la_epi_tr,la_lv_tr),axis=0)

	la_surface_tr = np.concatenate((la_endo_tr,la_epi_tr,mitral_tr,rpv_tr,lpv_tr),axis=0)

	tets_tags = np.zeros((tets.shape[0],),dtype=int)+tags_setup["LA"]["body"]
	surf_tags = np.zeros((la_surface_tr.shape[0],),dtype=int)

	surf_tags[:la_endo_tr.shape[0]] = tags_setup["LA"]["endo"]
	surf_tags[la_endo_tr.shape[0]:la_endo_tr.shape[0]+la_epi_tr.shape[0]] = tags_setup["LA"]["epi"]
	surf_tags[la_endo_tr.shape[0]+la_epi_tr.shape[0]:la_endo_tr.shape[0]+la_epi_tr.shape[0]+mitral_tr.shape[0]] = tags_setup["LA"]["mitral"]
	surf_tags[la_endo_tr.shape[0]+la_epi_tr.shape[0]+mitral_tr.shape[0]:la_endo_tr.shape[0]+la_epi_tr.shape[0]+mitral_tr.shape[0]+rpv_tr.shape[0]] = tags_setup["LA"]["RPV"]
	surf_tags[la_endo_tr.shape[0]+la_epi_tr.shape[0]+mitral_tr.shape[0]+rpv_tr.shape[0]:] = tags_setup["LA"]["LPV"]

	msh = meshio.Mesh(pts,
    				  [('tetra',tets),('triangle',la_surface_tr)],
    				  cell_data={'Ids': [tets_tags,surf_tags]})	

	msh.write(output_folder+"/la/la_tag.vtu")

def export_vtk_meshes_caroline(output_folder,
							   raa_apex_file=None,
							   surface="epi"):

	tets = read_elem(output_folder+"/la/la.elem",el_type="Tt",tags=False)
	pts = read_pts(output_folder+"/la/la.pts")
	
	surface_list = [output_folder+"/tmp/la.surf",
					output_folder+"/tmp/mitral.surf",
					output_folder+"/tmp/ripv.surf",
					output_folder+"/tmp/rspv.surf",
					output_folder+"/tmp/lipv.surf",
					output_folder+"/tmp/lspv.surf",
					output_folder+"/tmp/laa.surf",
					output_folder+"/tmp/pv_planes.surf",
					output_folder+"/tmp/la_lv.surf"]
	if surface=="endo":
		surface_list += [output_folder+"/tmp/ripv_vp.surf",
						 output_folder+"/tmp/rspv_vp.surf",
						 output_folder+"/tmp/lipv_vp.surf",
						 output_folder+"/tmp/lspv_vp.surf",
						 output_folder+"/tmp/laa_vp.surf"]
	surface_list_string = ','.join(surface_list)

	surface_bia_list = [output_folder+"/biatrial/la.surf",
						output_folder+"/biatrial/mitral.surf",
						output_folder+"/biatrial/ripv.surf",
						output_folder+"/biatrial/rspv.surf",
						output_folder+"/biatrial/lipv.surf",
						output_folder+"/biatrial/lspv.surf",
						output_folder+"/biatrial/laa.surf",
						output_folder+"/biatrial/pv_planes.surf",
						output_folder+"/biatrial/la_lv.surf"]
	if surface=="endo":
		surface_bia_list += [output_folder+"/biatrial/ripv_vp.surf",
						 	 output_folder+"/biatrial/rspv_vp.surf",
						 	 output_folder+"/biatrial/lipv_vp.surf",
						 	 output_folder+"/biatrial/lspv_vp.surf",
						 	 output_folder+"/biatrial/laa_vp.surf"]
	surface_bia_list_string = ','.join(surface_bia_list)

	print('Mapping surfaces onto biatrial mesh...')
	cmd = "meshtool map -submsh="+output_folder+"/biatrial/biatrial -files="+surface_list_string+" -outdir="+output_folder+"/biatrial/ -mode=m2s"
	os.system(cmd)

	print('Mapping surfaces onto LA mesh...')
	cmd = "meshtool map -submsh="+output_folder+"/la/la -files="+surface_bia_list_string+" -outdir="+output_folder+"/la/ -mode=m2s"
	os.system(cmd)

	la_tr = read_elem(output_folder+"/la/la.surf",el_type="Tr",tags=False)

	la_endo_eidx = read_nod_eidx(output_folder+"/tmp/la_endo.eidx")
	la_epi_eidx = read_nod_eidx(output_folder+"/tmp/la_epi.eidx")

	la_endo_tr = la_tr[la_endo_eidx,:]
	la_epi_tr = la_tr[la_epi_eidx,:]

	write_surf(output_folder+"/la/la_epi.surf",la_epi_tr)
	write_surf(output_folder+"/la/la_endo.surf",la_endo_tr)

	tets = read_elem(output_folder+"/ra/ra.elem",el_type="Tt",tags=False)
	pts = read_pts(output_folder+"/ra/ra.pts")
	
	surface_list = [output_folder+"/tmp/ra.surf",
					output_folder+"/tmp/tricuspid.surf",
					output_folder+"/tmp/svc.surf",
					output_folder+"/tmp/ivc.surf",
					output_folder+"/tmp/vc_planes.surf",
					output_folder+"/tmp/ra_rv.surf"]

	if surface=="endo":
		surface_list += [output_folder+"/tmp/svc_vp.surf",
						 output_folder+"/tmp/ivc_vp.surf"]
	surface_list_string = ','.join(surface_list)

	surface_bia_list = [output_folder+"/biatrial/ra.surf",
						output_folder+"/biatrial/tricuspid.surf",
						output_folder+"/biatrial/svc.surf",
						output_folder+"/biatrial/ivc.surf",
						output_folder+"/biatrial/vc_planes.surf",
						output_folder+"/biatrial/ra_rv.surf"]
	if surface=="endo":
		surface_bia_list += [output_folder+"/biatrial/svc_vp.surf",
						 	 output_folder+"/biatrial/ivc_vp.surf"]
	surface_bia_list_string = ','.join(surface_bia_list)

	print('Mapping surfaces onto biatrial mesh...')
	cmd = "meshtool map -submsh="+output_folder+"/biatrial/biatrial -files="+surface_list_string+" -outdir="+output_folder+"/biatrial/ -mode=m2s"
	os.system(cmd)

	print('Mapping surfaces onto RA mesh...')
	cmd = "meshtool map -submsh="+output_folder+"/ra/ra -files="+surface_bia_list_string+" -outdir="+output_folder+"/ra/ -mode=m2s"
	os.system(cmd)

	ra_tr = read_elem(output_folder+"/ra/ra.surf",el_type="Tr",tags=False)

	ra_endo_eidx = read_nod_eidx(output_folder+"/tmp/ra_endo.eidx")
	ra_epi_eidx = read_nod_eidx(output_folder+"/tmp/ra_epi.eidx")

	ra_endo_tr = ra_tr[ra_endo_eidx,:]
	ra_epi_tr = ra_tr[ra_epi_eidx,:]

	ra_rv_tr = read_elem(output_folder+"/ra/ra_rv.surf",el_type="Tr",tags=False)
	ra_epi_tr = np.concatenate((ra_epi_tr,ra_rv_tr),axis=0)

	write_surf(output_folder+"/ra/ra_epi.surf",ra_epi_tr)
	write_surf(output_folder+"/ra/ra_endo.surf",ra_endo_tr)

	print('-----------------------------------------------------')
	print('Finding LA landmarks...')
	print('-----------------------------------------------------')

	la_roof_landmarks = find_roof_points_LSPV_RSPV(output_folder,
												   surface=surface)
	la_lspv_rspv_posterior_landmarks,la_region_landmarks_pv = find_LSPV_RSPV_posterior_points(output_folder,la_roof_landmarks,
																							  surface=surface)

	la_laa_septal_posterior_landmarks,laa_region_landmarks = find_LAA_septal_posterior_points(output_folder,
																	np.concatenate((la_roof_landmarks,la_lspv_rspv_posterior_landmarks),axis=0),
																	surface=surface)
	
	landmarks = np.concatenate((la_roof_landmarks,la_laa_septal_posterior_landmarks),axis=0)
	landmarks = np.concatenate((landmarks,la_lspv_rspv_posterior_landmarks),axis=0)

	landmarks_visualise = np.zeros((7,3),dtype=float)
	landmarks_visualise[0,:] = landmarks[0,:]
	landmarks_visualise[1:,:] = landmarks
	write_pts(landmarks_visualise,output_folder+'/la/landmarks.pts')
	np.savetxt(output_folder+"/la/prodLaLandmarks.txt",landmarks,delimiter=',')

	region_landmarks = np.zeros((6,3),dtype=float)
	region_landmarks[:4,:] = la_region_landmarks_pv
	region_landmarks[4:,:] = laa_region_landmarks
	np.savetxt(output_folder+"/la/prodLaRegion.txt",region_landmarks,delimiter=',')

	landmarks_visualise = np.zeros((7,3),dtype=float)
	landmarks_visualise[0,:] = region_landmarks[0,:]
	landmarks_visualise[1:,:] = region_landmarks
	write_pts(landmarks_visualise,output_folder+'/la/landmarks_regions.pts')

	print('-----------------------------------------------------')
	print('Finding RA landmarks...')
	print('-----------------------------------------------------')

	landmarks_septum = find_septal_point(output_folder,
										 surface=surface)
	landmarks_svc_ivc_posterior, landmarks_regions_roof = find_SVC_IVC_roof_points(output_folder,landmarks_septum,
																				   surface=surface)
	landmarks = np.concatenate((landmarks_septum,landmarks_svc_ivc_posterior),axis=0)

	ivc_posterior_landmarks,region_landmarks_ivc = find_IVC_posterior_points(output_folder,landmarks,surface=surface)
	
	if raa_apex_file is not None:
		if os.path.exists(raa_apex_file):
			landmarks_raa_apex = np.loadtxt(raa_apex_file)
			landmark_raa_base = find_raa_base(output_folder,landmarks_raa_apex,surface=surface)
			region_landmarks_raa = np.concatenate((landmarks_raa_apex,landmark_raa_base),axis=0)
		else:
			raise Exception("Cannot find apex file.")
	else:
		region_landmarks_raa = find_raa_points(output_folder,landmarks_septum[0,:],surface=surface)


	landmarks_rearranged = np.zeros((6,3),dtype=float)
	landmarks_rearranged[0,:] = landmarks_septum[1,:]
	landmarks_rearranged[1,:] = ivc_posterior_landmarks[0,:]
	landmarks_rearranged[2,:] = landmarks_septum[0,:]
	landmarks_rearranged[3,:] = ivc_posterior_landmarks[1,:]
	landmarks_rearranged[4,:] = landmarks_svc_ivc_posterior[0,:]
	landmarks_rearranged[5,:] = landmarks_svc_ivc_posterior[1,:]

	landmarks_visualise[0,:] = landmarks_rearranged[0,:]
	landmarks_visualise[1:,:] = landmarks_rearranged
	write_pts(landmarks_visualise,output_folder+'/ra/landmarks.pts')
	np.savetxt(output_folder+"/ra/prodRaLandmarks.txt",landmarks_rearranged,delimiter=',')

	region_landmarks = np.zeros((6,3),dtype=float)
	region_landmarks[:2,:] = region_landmarks_ivc
	region_landmarks[2:4,:] = landmarks_regions_roof
	region_landmarks[4:,:] = region_landmarks_raa
	np.savetxt(output_folder+"/ra/prodRaRegion.txt",region_landmarks,delimiter=',')

	landmarks_visualise = np.zeros((7,3),dtype=float)
	landmarks_visualise[0,:] = region_landmarks[0,:]
	landmarks_visualise[1:,:] = region_landmarks
	write_pts(landmarks_visualise,output_folder+'/ra/landmarks_regions.pts')

	print('-----------------------------------------------------')
	print('Organising folders...')
	print('-----------------------------------------------------')

	os.system("mkdir -p "+output_folder+"/LA_endo/")
	os.system("mkdir -p "+output_folder+"/LA_epi/")
	os.system("mkdir -p "+output_folder+"/RA_endo/")
	os.system("mkdir -p "+output_folder+"/RA_epi/")

	os.system("meshtool convert -imsh="+output_folder+"/tmp/la_endo -ofmt=vtk_polydata -omsh="+output_folder+"/LA_endo/LA_endo")
	os.system("meshtool convert -imsh="+output_folder+"/tmp/ra_endo -ofmt=vtk_polydata -omsh="+output_folder+"/RA_endo/RA_endo")
	os.system("cp "+output_folder+"/la/prodLaLandmarks.txt "+output_folder+"/LA_endo/")
	os.system("cp "+output_folder+"/la/prodLaRegion.txt "+output_folder+"/LA_endo/")
	os.system("cp "+output_folder+"/la/prodLaLandmarks.txt "+output_folder+"/LA_epi/")
	os.system("cp "+output_folder+"/la/prodLaRegion.txt "+output_folder+"/LA_epi/")

	os.system("meshtool convert -imsh="+output_folder+"/tmp/la_epi -ofmt=vtk_polydata -omsh="+output_folder+"/LA_epi/LA_epi")
	os.system("meshtool convert -imsh="+output_folder+"/tmp/ra_epi -ofmt=vtk_polydata -omsh="+output_folder+"/RA_epi/RA_epi")
	os.system("cp "+output_folder+"/ra/prodRaLandmarks.txt "+output_folder+"/RA_endo/")
	os.system("cp "+output_folder+"/ra/prodRaRegion.txt "+output_folder+"/RA_endo/")
	os.system("cp "+output_folder+"/ra/prodRaLandmarks.txt "+output_folder+"/RA_epi/")
	os.system("cp "+output_folder+"/ra/prodRaRegion.txt "+output_folder+"/RA_epi/")

def recompute_raa_base(output_folder,
					   raa_apex_file,
					   landmarks_file,
					   scale=1.0,
					   surface="epi"):
	
	if os.path.exists(raa_apex_file):
			landmarks_raa_apex = np.loadtxt(raa_apex_file)
			landmark_raa_base = find_raa_base(output_folder,landmarks_raa_apex,surface=surface)
			landmarks_raa_apex = np.reshape(landmarks_raa_apex,(1,3))
			region_landmarks_raa = np.concatenate((landmarks_raa_apex,landmark_raa_base),axis=0)
	else:
		raise Exception("Cannot find apex file.")

	region_landmarks = np.loadtxt(landmarks_file,dtype=float,delimiter=',')
	region_landmarks[-2:,:] = region_landmarks_raa
	np.savetxt(landmarks_file,region_landmarks*scale,delimiter=',')

def scale_landmarks(landmarks_file,
					scale=1.0):

	landmarks = np.loadtxt(landmarks_file,dtype=float,delimiter=',')
	np.savetxt(landmarks_file,landmarks*scale,delimiter=',')

def export_RA_vtk_msh(output_folder,
					  tags_setup,
					  r_geodesic=1000.0):

	tets = read_elem(output_folder+"/ra/ra.elem",el_type="Tt",tags=False)
	pts = read_pts(output_folder+"/ra/ra.pts")
	
	surface_list = [output_folder+"/tmp/ra.surf",
					output_folder+"/tmp/tricuspid.surf",
					output_folder+"/tmp/svc.surf",
					output_folder+"/tmp/ivc.surf",
					output_folder+"/tmp/vc_planes.surf",
					output_folder+"/tmp/ra_rv.surf"]
	surface_list_string = ','.join(surface_list)

	surface_bia_list = [output_folder+"/biatrial/ra.surf",
						output_folder+"/biatrial/tricuspid.surf",
						output_folder+"/biatrial/svc.surf",
						output_folder+"/biatrial/ivc.surf",
						output_folder+"/biatrial/vc_planes.surf",
						output_folder+"/biatrial/ra_rv.surf"]
	surface_bia_list_string = ','.join(surface_bia_list)

	print('Mapping surfaces onto biatrial mesh...')
	cmd = "meshtool map -submsh="+output_folder+"/biatrial/biatrial -files="+surface_list_string+" -outdir="+output_folder+"/biatrial/ -mode=m2s"
	os.system(cmd)

	print('Mapping surfaces onto RA mesh...')
	cmd = "meshtool map -submsh="+output_folder+"/ra/ra -files="+surface_bia_list_string+" -outdir="+output_folder+"/ra/ -mode=m2s"
	os.system(cmd)

	ra_tr = read_elem(output_folder+"/ra/ra.surf",el_type="Tr",tags=False)

	ra_endo_eidx = read_nod_eidx(output_folder+"/tmp/ra_endo.eidx")
	ra_epi_eidx = read_nod_eidx(output_folder+"/tmp/ra_epi.eidx")

	ra_endo_tr = ra_tr[ra_endo_eidx,:]
	ra_epi_tr = ra_tr[ra_epi_eidx,:]

	write_surf(output_folder+"/ra/ra_epi.surf",ra_epi_tr)
	write_surf(output_folder+"/ra/ra_endo.surf",ra_endo_tr)

	tricuspid_tr = read_elem(output_folder+"/ra/tricuspid.surf",el_type="Tr",tags=False)
	svc_tr = read_elem(output_folder+"/ra/svc.surf",el_type="Tr",tags=False)
	ivc_tr = read_elem(output_folder+"/ra/ivc.surf",el_type="Tr",tags=False)
	vc_planes_tr = read_elem(output_folder+"/ra/vc_planes.surf",el_type="Tr",tags=False)
	ra_rv_tr = read_elem(output_folder+"/ra/ra_rv.surf",el_type="Tr",tags=False)

	ra_endo_tr = np.concatenate((ra_endo_tr,vc_planes_tr),axis=0)
	ra_epi_tr = np.concatenate((ra_epi_tr,ra_rv_tr),axis=0)

	ra_surface_tr = np.concatenate((ra_endo_tr,ra_epi_tr,tricuspid_tr,svc_tr,ivc_tr),axis=0)

	print("---------------------------------------------")
	print("Extracting points for SVC IVC geodesic...")
	print("---------------------------------------------")
	idx_geodesic,anterior_posterior_tag = find_SVC_IVC_geodesic(output_folder,r_geodesic=r_geodesic)
	tags_ra_epi = np.zeros((ra_epi_tr.shape[0],),dtype=int)+tags_setup["RA"]["epi"]
	tags_ra_epi[idx_geodesic] = tags_setup["RA"]["roof_line"]

	tricuspid_ant_post_tag = np.zeros((tricuspid_tr.shape[0],),dtype=int)+tags_setup["RA"]["tricuspid_anterior"]
	tricuspid_ant_post_tag[np.where(anterior_posterior_tag==1)[0]] = tags_setup["RA"]["tricuspid_posterior"]

	tets_tags = np.zeros((tets.shape[0],),dtype=int)+tags_setup["RA"]["body"]
	surf_tags = np.zeros((ra_surface_tr.shape[0],),dtype=int)

	surf_tags[:ra_endo_tr.shape[0]] = tags_setup["RA"]["endo"]
	surf_tags[ra_endo_tr.shape[0]:ra_endo_tr.shape[0]+ra_epi_tr.shape[0]] = tags_ra_epi
	surf_tags[ra_endo_tr.shape[0]+ra_epi_tr.shape[0]:ra_endo_tr.shape[0]+ra_epi_tr.shape[0]+tricuspid_tr.shape[0]] = tricuspid_ant_post_tag
	surf_tags[ra_endo_tr.shape[0]+ra_epi_tr.shape[0]+tricuspid_tr.shape[0]:ra_endo_tr.shape[0]+ra_epi_tr.shape[0]+tricuspid_tr.shape[0]+svc_tr.shape[0]] = tags_setup["RA"]["SVC"]
	surf_tags[ra_endo_tr.shape[0]+ra_epi_tr.shape[0]+tricuspid_tr.shape[0]+svc_tr.shape[0]:] = tags_setup["RA"]["IVC"]

	msh = meshio.Mesh(pts,
    				  [('tetra',tets),('triangle',ra_surface_tr)],
    				  cell_data={'Ids': [tets_tags,surf_tags]})	

	msh.write(output_folder+"/ra/ra_tag.vtu")
