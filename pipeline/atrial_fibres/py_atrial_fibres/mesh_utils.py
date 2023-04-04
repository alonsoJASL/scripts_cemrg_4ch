import numpy as np
import os
import trimesh

from py_atrial_fibres.file_utils import *
from py_atrial_fibres.linalg_utils import *

def compute_elemCenters(meshname,
						el_type):

	pts = read_pts(meshname+".pts") 
	elem = read_elem(meshname+".elem",el_type=el_type,tags=False) 
	n_tet = elem.shape[0] 

	cog_el = np.zeros((n_tet,3),dtype=float) 
	for i,el in enumerate(elem):
		pts_el = pts[el,:]
		cog_el[i,:] = np.mean(pts_el,axis=0)
	
	write_pts(cog_el,meshname+"_elemCenters.pts")

def laplace_endo2elem(meshname,
					  phi_nodes,
					  output_phi=None):

	if output_phi is None:
		output_phi = phi_nodes[:-4]+"_el.dat"

	elem = read_elem(meshname+".elem",el_type='Tt',tags=False)
	n_tet = elem.shape[0]	

	phi = np.loadtxt(phi_nodes,dtype=float)

	phi_el = np.empty((n_tet,),dtype=float)
	for i,tt in enumerate(elem):
		flag=0
		for k,node in enumerate(tt):
			if phi[tt[k]] == 1:
				phi_el[i] = 1
				flag=1
			if phi[tt[k]] == 0:
			    phi_el[i] = 0
			    flag=1
		if flag==0:
			phi_el[i]=np.mean(phi[tt])	

	np.savetxt(output_phi,phi_el,fmt="%g")

def tag_node2elem(meshname,
				  tag_file,
				  output_file):

	print("Mapping "+tag_file+" from nodes to elements...")

	elem = read_elem(meshname+".elem",el_type='Tr',tags=False)
	tags = np.loadtxt(tag_file,dtype=int)

	tags_el = np.zeros((elem.shape[0],),dtype=int)

	for i,tr in enumerate(elem):

		all_in = np.sum((tags[tr]!=0))
		
		if all_in==3:
			tags_el[i] = 1

	np.savetxt(output_file,tags_el,fmt="%d")

def map_fibres_3d(phi_el_file,
				  elemCenters_3d,
				  elemCenters_2d,
				  f_endo_file,
				  f_epi_file,
				  output_fibres,
				  map_tr_tt_file=None):
		
	phi = np.loadtxt(phi_el_file,dtype=float)
	cog_tt = read_pts(elemCenters_3d)
	cog_tr = read_pts(elemCenters_2d)

	f_endo = np.loadtxt(f_endo_file,dtype=float) 
	f_epi = np.loadtxt(f_epi_file,dtype=float) 

	save_mapping = False
	if map_tr_tt_file is not None:
		if os.path.exists(map_tr_tt_file):
			mapping_tr_tt = np.loadtxt(map_tr_tt_file,dtype=int)
		else:
			mapping_tr_tt = np.zeros((cog_tt.shape[0],),dtype=int)
			save_mapping = True
	else:
		mapping_tr_tt = np.zeros((cog_tt.shape[0],),dtype=int)

	if phi.shape[0] != cog_tt.shape[0]:
		raise Exception("The laplace solution is not defined on the elements.")

	f_tt = np.zeros((phi.shape[0],3),dtype=float)
	for i in range(phi.shape[0]):

		if (map_tr_tt_file is None) or save_mapping:
			distance = np.linalg.norm(cog_tr-cog_tt[i,:],axis=1)
			idx_closest_tr = np.argmin(distance)
			mapping_tr_tt[i]= idx_closest_tr
		else:
			idx_closest_tr = mapping_tr_tt[i]

		if phi[i] > 0.5:
			f_tt[i,:] = f_epi[idx_closest_tr,:]
		else:
			f_tt[i,:] = f_endo[idx_closest_tr,:]

	if save_mapping:
		np.savetxt(map_tr_tt_file,mapping_tr_tt,fmt="%d")

	write_lon(f_tt,output_fibres)	

def map_tags_3d(phi_el_file,
				elemCenters_3d,
				elemCenters_2d,
				tags_2d_file,
				output_tags,
				endo_tags=[],
				map_tr_tt_file=None):
		
	phi = np.loadtxt(phi_el_file,dtype=float)
	cog_tt = read_pts(elemCenters_3d)
	cog_tr = read_pts(elemCenters_2d)

	tags_2d = np.loadtxt(tags_2d_file,dtype=int)

	save_mapping = False
	if map_tr_tt_file is not None:
		if os.path.exists(map_tr_tt_file):
			mapping_tr_tt = np.loadtxt(map_tr_tt_file,dtype=int)
		else:
			mapping_tr_tt = np.zeros((cog_tt.shape[0],),dtype=int)
			save_mapping = True
	else:
		mapping_tr_tt = np.zeros((cog_tt.shape[0],),dtype=int)

	if phi.shape[0] != cog_tt.shape[0]:
		raise Exception("The laplace solution is not defined on the elements.")

	tags_tt = np.zeros((phi.shape[0],),dtype=float)
	for i in range(phi.shape[0]):

		if (map_tr_tt_file is None) or save_mapping:
			distance = np.linalg.norm(cog_tr-cog_tt[i,:],axis=1)
			idx_closest_tr = np.argmin(distance)
			mapping_tr_tt[i]= idx_closest_tr
		else:
			idx_closest_tr = mapping_tr_tt[i]

		if tags_2d[idx_closest_tr] in endo_tags:
			if phi[i]==0:
				tags_tt[i] = tags_2d[idx_closest_tr]
		else:
			tags_tt[i] = tags_2d[idx_closest_tr]

	if save_mapping:
		np.savetxt(map_tr_tt_file,mapping_tr_tt,fmt="%d")

	np.savetxt(output_tags,tags_tt)	

def find_transmural_direction_Gl(meshname,
							  phi_el_file,
							  output_file):

	cmd = "GlGradient -m "+meshname
	cmd += " -S elem_ctr -t elem_ctr "
	cmd += "-d "+phi_el_file+" -o "+output_file

	os.system(cmd)


def find_transmural_direction(meshname_3d,
							  meshname_2d,
							  elemCenters_3d,
				  			  elemCenters_2d,
				  			  output_file,
							  map_tr_tt_file=None):
	
	elem_3d = read_elem(meshname_3d+".elem",el_type="Tt",tags=False)

	cog_tt = read_pts(elemCenters_3d)
	cog_tr = read_pts(elemCenters_2d)

	normals_surf = compute_normal_from_surface(meshname_2d)
	normals_tets = np.zeros((elem_3d.shape[0],3),dtype=float)

	save_mapping = False
	if map_tr_tt_file is not None:
		if os.path.exists(map_tr_tt_file):
			mapping_tr_tt = np.loadtxt(map_tr_tt_file,dtype=int)
		else:
			mapping_tr_tt = np.zeros((cog_tt.shape[0],),dtype=int)
			save_mapping = True
	else:
		mapping_tr_tt = np.zeros((cog_tt.shape[0],),dtype=int)

	for i in range(elem_3d.shape[0]):

		if (map_tr_tt_file is None) or save_mapping:
			distance = np.linalg.norm(cog_tr-cog_tt[i,:],axis=1)
			idx_closest_tr = np.argmin(distance)
			mapping_tr_tt[i]= idx_closest_tr
		else:
			idx_closest_tr = mapping_tr_tt[i]

		normals_tets[i,:] = normals_surf[idx_closest_tr,:]

	if save_mapping:
		np.savetxt(map_tr_tt_file,mapping_tr_tt,fmt="%d")

	write_lon(normals_tets,output_file)

def tag_connected_component_2d(meshname,
							   tag_file,
							   tag_outfile,
							   vtx_threshold=10):

	print("Removing components with less than "+str(vtx_threshold)+" point from "+tag_file+"...")

	pts = read_pts(meshname+".pts")
	elem = read_elem(meshname+".elem",el_type="Tr",tags=False)
	tags = np.loadtxt(tag_file,dtype=int)

	elem_tag = elem[np.where(tags!=0)[0],:]
	tag_vtx = surf2vtx(elem_tag)
	pts_tag = pts[tag_vtx,:]
	elem_tag_reindexed = reindex_surf(tag_vtx,elem_tag)

	mesh_tag = trimesh.Trimesh(vertices=pts_tag,
							   faces=elem_tag_reindexed,
							   process=False)

	cc_labels_tag = trimesh.graph.connected_component_labels(mesh_tag.edges)
	n_cc = np.max(cc_labels_tag)+1

	if n_cc > 1:
		cc_size = np.array([(cc_labels_tag == i).sum() for i in range(n_cc)])

		remove_cc_idx = np.where(cc_size<=vtx_threshold)[0]

		for cc in remove_cc_idx:
			vtx_cc = tag_vtx[np.where(cc_labels_tag==cc)[0]]
			for i,tr in enumerate(elem):
				inters = np.intersect1d(vtx_cc,tr)
				if inters.size:
					tags[i] = 0

	np.savetxt(tag_outfile,tags,fmt="%d")

def combine_tags(meshname,
				 tagfile_list,
				 tags,
				 default_tag,
				 output_file):

	if len(tagfile_list)!=len(tags):
		raise Exception("Tags and tag files do not match in size.")

	elem = read_elem(meshname+".elem",el_type="Tr",tags=False)

	tags_combined = np.zeros((elem.shape[0],),dtype=int)+default_tag

	for i,tag_file in enumerate(tagfile_list):
		tmp = np.loadtxt(tag_file,dtype=int)
		tags_combined[np.where(tmp==1)[0]] = tags[i]

	np.savetxt(output_file,tags_combined,fmt="%d")




