import os
import sys
import numpy as np
import meshio
from math import cos,sin,sqrt
import math

from py_atrial_fibres.file_utils import *

def calculate_rotation(ax, theta):

    R = np.zeros((3,3))  
    R[0,0] = ax[0]**2 + cos(theta) * (1 - ax[0]**2);
    R[0,1] = (1 - cos(theta)) * ax[0] * ax[1] - ax[2] * sin(theta);
    R[0,2] = (1 - cos(theta)) * ax[0] * ax[2] + ax[1] * sin(theta);
    R[1,0] = (1 - cos(theta)) * ax[0] * ax[1] + ax[2] * sin(theta);
    R[1,1] = ax[1]**2 + cos(theta) * (1 - ax[1]**2);
    R[1,2] = ( 1 - cos(theta)) * ax[1] * ax[2] - ax[0] * sin(theta);
    R[2,0] = ( 1 - cos(theta)) * ax[0] * ax[2] - ax[1] * sin(theta);
    R[2,1] = ( 1 - cos(theta)) * ax[1] * ax[2] + ax[0] * sin(theta);
    R[2,2] = ax[2]**2 + cos(theta) * (1 - ax[2]**2);

    return R

def find_SVC_IVC_geodesic(output_folder,
						  r_geodesic=1000.0):	
	
	pts = read_pts(output_folder+"/ra/ra.pts")

	ra_epi_surf = read_elem(output_folder+"/ra/ra_epi.surf",el_type="Tr",tags=False)
	ra_epi_vtx = surf2vtx(ra_epi_surf)
	pts_ra_epi = pts[ra_epi_vtx,:]
	ra_epi_surf_reindexed = reindex_surf(ra_epi_vtx,ra_epi_surf)

	# mesh = meshio.Mesh(pts_ra_epi,[('triangle',ra_epi_surf_reindexed)])
	# mesh.write(output_folder+'/ra/ra_epi.vtu')

	ivc_surf = read_elem(output_folder+"/ra/ivc.surf",el_type="Tr",tags=False)
	ivc_idx = surf2vtx(ivc_surf)
	ivc_idx_epi = np.intersect1d(ra_epi_vtx,ivc_idx)
	ivc_idx_epi = reindex_vtx(ivc_idx_epi,ra_epi_vtx)

	svc_surf = read_elem(output_folder+"/ra/svc.surf",el_type="Tr",tags=False)
	svc_idx = surf2vtx(svc_surf)
	svc_idx_epi = np.intersect1d(ra_epi_vtx,svc_idx)
	svc_idx_epi = reindex_vtx(svc_idx_epi,ra_epi_vtx)

	tricuspid_surf = read_elem(output_folder+"/ra/tricuspid.surf",el_type="Tr",tags=False)
	tricuspid_vtx = surf2vtx(tricuspid_surf)
	cog_tricuspid = np.mean(pts[tricuspid_vtx,:],axis=0)
	cog_svc = np.mean(pts[svc_idx,:],axis=0)
	cog_ivc = np.mean(pts[ivc_idx,:],axis=0)
	v_svc_ivc = cog_svc-cog_ivc
	v_svc_ivc = v_svc_ivc/np.linalg.norm(v_svc_ivc)
	v_tricuspid_ivc = cog_tricuspid-cog_ivc

	cog_tricuspid_pj = cog_ivc+v_svc_ivc*np.dot(v_svc_ivc,v_tricuspid_ivc)

	long_axis = cog_tricuspid_pj-cog_tricuspid
	long_axis = long_axis/np.linalg.norm(long_axis)

	proj_ra_epi = np.dot(pts_ra_epi-cog_tricuspid,long_axis)
	ra_epi_roof = np.where(proj_ra_epi==np.max(proj_ra_epi))[0]

	print('Extracting roof to make sure pygeodesic does not go out of memory...')
	roof_extract_eidx = []
	for i,t in enumerate(ra_epi_surf_reindexed):
		cog_t = np.mean(pts_ra_epi[t,:],axis=0)
		dot_prod = np.dot(cog_t-cog_tricuspid_pj,long_axis)
		if dot_prod>0:
			roof_extract_eidx.append(i)
	surf_epi_roof = ra_epi_surf_reindexed[roof_extract_eidx,:]
	roof_extract_vtx = surf2vtx(surf_epi_roof)
	surf_epi_roof_reindexed = reindex_surf(roof_extract_vtx,surf_epi_roof)
	pts_epi_roof = pts_ra_epi[roof_extract_vtx,:]

	mesh = meshio.Mesh(pts_epi_roof,[('triangle',surf_epi_roof_reindexed)])
	mesh.write(output_folder+'/ra/ra_epi_roof.vtu')

	geoalg = geodesic.PyGeodesicAlgorithmExact(pts_epi_roof, surf_epi_roof_reindexed)

	ra_epi_roof = np.where(roof_extract_vtx==ra_epi_roof)[0]
	ivc_idx_epi = reindex_vtx(ivc_idx_epi,roof_extract_vtx)
	svc_idx_epi = reindex_vtx(svc_idx_epi,roof_extract_vtx)

	distances, best_source = geoalg.geodesicDistances(ra_epi_roof,None)
	distances_ivc = distances[ivc_idx_epi]
	ivc_idx_geodesic = ivc_idx_epi[np.where(distances_ivc==np.min(distances_ivc))[0]]

	distances_svc = distances[svc_idx_epi]
	svc_idx_geodesic = svc_idx_epi[np.where(distances_svc==np.min(distances_svc))[0]]

	distance, path = geoalg.geodesicDistance(np.array([svc_idx_geodesic]), np.array([ivc_idx_geodesic]))

	lines = np.zeros((path.shape[0]-1,2),dtype=int)
	lines[:,0] = np.arange(path.shape[0]-1)
	lines[:,1] = np.arange(path.shape[0]-1)+1
	msh_geod = meshio.Mesh(path,
    				  [('line',lines)])	
	msh_geod.write(output_folder+"/ra/svc_ivc_geodesic.vtu")

	anterior_posterior_tag = split_tricuspid_ring(pts,tricuspid_surf,
						 pts_epi_roof[svc_idx_geodesic,:],
						 pts_epi_roof[ivc_idx_geodesic,:],
						 cog_tricuspid)

	idx_geodesic = []
	for p in path:
		d = np.linalg.norm(pts_ra_epi-p,axis=1)
		idx_geodesic += list(np.where(d<=r_geodesic)[0])
	idx_geodesic = np.unique(np.array(idx_geodesic))

	eidx_geodesic = []
	for i,t in enumerate(ra_epi_surf_reindexed):
		if len(np.intersect1d(t,idx_geodesic))>0:
			eidx_geodesic.append(i)
	eidx_geodesic = np.array(eidx_geodesic)

	return eidx_geodesic,anterior_posterior_tag

def split_tricuspid_ring(pts,
						 tricuspid_surf,
						 svc_pts,
						 ivc_pts,
						 cog_tricuspid):
	
	v1 = svc_pts-cog_tricuspid
	v1 = v1/np.linalg.norm(v1)

	v2 = ivc_pts-cog_tricuspid
	v2 = v2/np.linalg.norm(v1)

	n_plane = np.cross(v1,v2)
	n_plane = n_plane/np.linalg.norm(n_plane)

	ant_post_tag = np.zeros((tricuspid_surf.shape[0],),dtype=int)
	for i,t in enumerate(tricuspid_surf):
		dot_prod = np.dot(pts[t[0],:]-cog_tricuspid,n_plane[0])
		if dot_prod>0:
			ant_post_tag[i] = 1	

	return ant_post_tag

def find_roof_points_LSPV_RSPV(output_folder,
							   scale_factor=1.0,
							   surface="epi"):

	pts = read_pts(output_folder+"/la/la.pts")

	la_epi_surf = read_elem(output_folder+"/la/la_"+surface+".surf",el_type="Tr",tags=False)
	la_epi_vtx = surf2vtx(la_epi_surf)
	pts_la_epi = pts[la_epi_vtx,:]
	la_epi_surf_reindexed = reindex_surf(la_epi_vtx,la_epi_surf)

	if surface=="endo":
		surf_name = output_folder+"/la/lspv_vp.surf"
	else:
		surf_name = output_folder+"/la/lspv.surf"
	lspv_surf = read_elem(surf_name,el_type="Tr",tags=False)
	lspv_idx = surf2vtx(lspv_surf)
	lspv_idx_epi = np.intersect1d(la_epi_vtx,lspv_idx)
	lspv_idx_epi = reindex_vtx(lspv_idx_epi,la_epi_vtx)

	if surface=="endo":
		surf_name = output_folder+"/la/rspv_vp.surf"
	else:
		surf_name = output_folder+"/la/rspv.surf"
	rspv_surf = read_elem(surf_name,el_type="Tr",tags=False)
	rspv_idx = surf2vtx(rspv_surf)
	rspv_idx_epi = np.intersect1d(la_epi_vtx,rspv_idx)
	rspv_idx_epi = reindex_vtx(rspv_idx_epi,la_epi_vtx)

	mitral_surf = read_elem(output_folder+"/la/mitral.surf",el_type="Tr",tags=False)
	mitral_vtx = surf2vtx(mitral_surf)
	cog_mitral = np.mean(pts[mitral_vtx,:],axis=0)
	cog_lspv = np.mean(pts[lspv_idx,:],axis=0)
	cog_rspv = np.mean(pts[rspv_idx,:],axis=0)
	v_lspv_rspv = cog_lspv-cog_rspv
	v_lspv_rspv = v_lspv_rspv/np.linalg.norm(v_lspv_rspv)
	v_mitral_rpsv = cog_mitral-cog_rspv

	cog_mitral_pj = cog_rspv+v_lspv_rspv*np.dot(v_lspv_rspv,v_mitral_rpsv)

	long_axis = cog_mitral_pj-cog_mitral
	long_axis = long_axis/np.linalg.norm(long_axis)

	# making sure the whole roof is included by moving this point down
	cog_mitral_pj = cog_mitral_pj-5000.0*scale_factor*long_axis

	proj_la_epi = np.dot(pts_la_epi-cog_mitral,long_axis)
	la_epi_roof = np.where(proj_la_epi==np.max(proj_la_epi))[0]

	print('Extracting roof to make sure pygeodesic does not go out of memory...')
	roof_extract_eidx = []
	for i,t in enumerate(la_epi_surf_reindexed):
		cog_t = np.mean(pts_la_epi[t,:],axis=0)
		dot_prod = np.dot(cog_t-cog_mitral_pj,long_axis)
		if dot_prod>0:
			roof_extract_eidx.append(i)
	surf_epi_roof = la_epi_surf_reindexed[roof_extract_eidx,:]
	roof_extract_vtx = surf2vtx(surf_epi_roof)
	surf_epi_roof_reindexed = reindex_surf(roof_extract_vtx,surf_epi_roof)
	pts_epi_roof = pts_la_epi[roof_extract_vtx,:]

	mesh = meshio.Mesh(pts_epi_roof,[('triangle',surf_epi_roof_reindexed)])
	mesh.write(output_folder+'/la/la_epi_roof.vtu')

	geoalg = geodesic.PyGeodesicAlgorithmExact(pts_epi_roof, surf_epi_roof_reindexed)

	la_epi_roof = np.where(roof_extract_vtx==la_epi_roof)[0]
	rspv_idx_epi = reindex_vtx(rspv_idx_epi,roof_extract_vtx)
	lspv_idx_epi = reindex_vtx(lspv_idx_epi,roof_extract_vtx)

	distances, best_source = geoalg.geodesicDistances(la_epi_roof,None)
	distances_rspv = distances[rspv_idx_epi]
	rspv_idx_geodesic = rspv_idx_epi[np.where(distances_rspv==np.min(distances_rspv))[0]]

	distances_lspv = distances[lspv_idx_epi]
	lspv_idx_geodesic = lspv_idx_epi[np.where(distances_lspv==np.min(distances_lspv))[0]]

	pts_lspv_roof = pts_epi_roof[lspv_idx_geodesic,:]
	pts_rspv_roof = pts_epi_roof[rspv_idx_geodesic,:]
	landmarks = np.concatenate((pts_lspv_roof,pts_rspv_roof),axis=0)

	return landmarks

def find_LSPV_RSPV_posterior_points(output_folder,
								    lspv_rspv_roof_points,
								    surface="epi"):

	pts_lspv_roof = lspv_rspv_roof_points[0,:]
	pts_rspv_roof = lspv_rspv_roof_points[1,:]

	pts = read_pts(output_folder+"/la/la.pts")

	la_epi_surf = read_elem(output_folder+"/la/la_"+surface+".surf",el_type="Tr",tags=False)
	la_epi_vtx = surf2vtx(la_epi_surf)
	pts_la_epi = pts[la_epi_vtx,:]
	la_epi_surf_reindexed = reindex_surf(la_epi_vtx,la_epi_surf)

	if surface=="endo":
		surf_name = output_folder+"/la/lspv_vp.surf"
	else:
		surf_name = output_folder+"/la/lspv.surf"	
	lspv_surf = read_elem(surf_name,el_type="Tr",tags=False)
	lspv_idx = surf2vtx(lspv_surf)
	lspv_idx_epi = np.intersect1d(la_epi_vtx,lspv_idx)
	lspv_idx_epi = reindex_vtx(lspv_idx_epi,la_epi_vtx)

	if surface=="endo":
		surf_name = output_folder+"/la/rspv_vp.surf"
	else:
		surf_name = output_folder+"/la/rspv.surf"
	rspv_surf = read_elem(surf_name,el_type="Tr",tags=False)
	rspv_idx = surf2vtx(rspv_surf)
	rspv_idx_epi = np.intersect1d(la_epi_vtx,rspv_idx)
	rspv_idx_epi = reindex_vtx(rspv_idx_epi,la_epi_vtx)

	if surface=="endo":
		surf_name = output_folder+"/la/lipv_vp.surf"
	else:
		surf_name = output_folder+"/la/lipv.surf"
	lipv_surf = read_elem(surf_name,el_type="Tr",tags=False)
	lipv_idx = surf2vtx(lipv_surf)
	lipv_idx_epi = np.intersect1d(la_epi_vtx,lipv_idx)
	lipv_idx_epi = reindex_vtx(lipv_idx_epi,la_epi_vtx)

	if surface=="endo":
		surf_name = output_folder+"/la/ripv_vp.surf"
	else:
		surf_name = output_folder+"/la/ripv.surf"
	ripv_surf = read_elem(surf_name,el_type="Tr",tags=False)
	ripv_idx = surf2vtx(ripv_surf)
	ripv_idx_epi = np.intersect1d(la_epi_vtx,ripv_idx)
	ripv_idx_epi = reindex_vtx(ripv_idx_epi,la_epi_vtx)

	mitral_surf = read_elem(output_folder+"/la/mitral.surf",el_type="Tr",tags=False)
	mitral_vtx = surf2vtx(mitral_surf)
	cog_mitral = np.mean(pts[mitral_vtx,:],axis=0)
	cog_lspv = np.mean(pts[lspv_idx,:],axis=0)
	cog_rspv = np.mean(pts[rspv_idx,:],axis=0)

	v1 = cog_lspv-cog_mitral
	v1 = v1/np.linalg.norm(v1)

	v2 = cog_rspv-cog_mitral
	v2 = v2/np.linalg.norm(v1)

	n_plane = np.cross(v1,v2)
	n_plane = n_plane/np.linalg.norm(n_plane)

	dot_prod = 0.
	print('Finding posterior LSPV rim...')
	for v in lspv_idx_epi:
		dot_prod_tmp = np.dot(pts_la_epi[v,:]-cog_mitral,n_plane)

		if dot_prod_tmp<dot_prod:
			idx_posterior_lpsv = v
			dot_prod = dot_prod_tmp

	dot_prod = 0.
	print('Finding posterior RSPV rim...')
	for v in rspv_idx_epi:
		dot_prod_tmp = np.dot(pts_la_epi[v,:]-cog_mitral,n_plane)
		
		if dot_prod_tmp<dot_prod:
			idx_posterior_rpsv = v
			dot_prod = dot_prod_tmp

	pts_lspv_posterior = pts_la_epi[idx_posterior_lpsv,:]
	pts_rspv_posterior = pts_la_epi[idx_posterior_rpsv,:]

	landmarks = np.concatenate((pts_lspv_posterior,pts_rspv_posterior),axis=0)
	landmarks = np.reshape(landmarks,(2,3))

	# -------------------------------------------------------------------------------------- #
	region_landmarks = np.zeros((4,3),dtype=float)

	v_rspv_across = cog_rspv-pts_rspv_posterior	
	v_rspv_across = v_rspv_across/np.linalg.norm(v_rspv_across)

	print('Finding anterior RSPV rim...')
	dot_prod = 0.
	for v in rspv_idx_epi:
		dot_prod_tmp = np.dot(pts_la_epi[v,:]-pts_rspv_posterior,v_rspv_across)

		if dot_prod_tmp>dot_prod:
			dot_prod = dot_prod_tmp
			idx_rspv_anterior = v
	region_landmarks[0,:] = pts_la_epi[idx_rspv_anterior,:]

	dot_prod = 0.
	print('Finding posterior RIPV rim...')
	for v in ripv_idx_epi:
		dot_prod_tmp = np.dot(pts_la_epi[v,:]-cog_mitral,n_plane)
		
		if dot_prod_tmp<dot_prod:
			idx_posterior_ripv = v
			dot_prod = dot_prod_tmp
	region_landmarks[1,:] = pts_la_epi[idx_posterior_ripv,:]

	dot_prod = 0.
	print('Finding posterior LIPV rim...')
	for v in lipv_idx_epi:
		dot_prod_tmp = np.dot(pts_la_epi[v,:]-cog_mitral,n_plane)
		
		if dot_prod_tmp<dot_prod:
			idx_posterior_lipv = v
			dot_prod = dot_prod_tmp
	region_landmarks[2,:] = pts_la_epi[idx_posterior_lipv,:]

	v_lspv_across = cog_lspv-pts_lspv_posterior	
	v_lspv_across = v_lspv_across/np.linalg.norm(v_lspv_across)

	print('Finding anterior LSPV rim...')
	dot_prod = 0.
	for v in lspv_idx_epi:
		dot_prod_tmp = np.dot(pts_la_epi[v,:]-pts_lspv_posterior,v_lspv_across)

		if dot_prod_tmp>dot_prod:
			dot_prod = dot_prod_tmp
			idx_lspv_anterior = v
	region_landmarks[3,:] = pts_la_epi[idx_lspv_anterior,:]

	return landmarks,region_landmarks

def find_LAA_septal_posterior_points(output_folder,
								     landmarks,
							   		 scale_factor=1.0,
							   		 surface="epi"):

	pts_lspv_roof = landmarks[0,:]
	pts_rspv_roof = landmarks[1,:]
	pts_lspv_posterior = landmarks[2,:]
	pts_rspv_posterior = landmarks[3,:]

	pts = read_pts(output_folder+"/la/la.pts")

	la_epi_surf = read_elem(output_folder+"/la/la_"+surface+".surf",el_type="Tr",tags=False)
	la_epi_vtx = surf2vtx(la_epi_surf)
	pts_la_epi = pts[la_epi_vtx,:]
	la_epi_surf_reindexed = reindex_surf(la_epi_vtx,la_epi_surf)

	if surface=="endo":
		surf_name = output_folder+"/la/lspv_vp.surf"
	else:
		surf_name = output_folder+"/la/lspv.surf"	
	lspv_surf = read_elem(surf_name,el_type="Tr",tags=False)
	lspv_idx = surf2vtx(lspv_surf)
	lspv_idx_epi = np.intersect1d(la_epi_vtx,lspv_idx)
	lspv_idx_epi = reindex_vtx(lspv_idx_epi,la_epi_vtx)

	if surface=="endo":
		surf_name = output_folder+"/la/ripv_vp.surf"
	else:
		surf_name = output_folder+"/la/ripv.surf"
	ripv_surf = read_elem(surf_name,el_type="Tr",tags=False)
	ripv_idx = surf2vtx(ripv_surf)
	ripv_idx_epi = np.intersect1d(la_epi_vtx,ripv_idx)
	ripv_idx_epi = reindex_vtx(ripv_idx_epi,la_epi_vtx)

	if surface=="endo":
		surf_name = output_folder+"/la/rspv_vp.surf"
	else:
		surf_name = output_folder+"/la/rspv.surf"
	rspv_surf = read_elem(surf_name,el_type="Tr",tags=False)
	rspv_idx = surf2vtx(rspv_surf)
	rspv_idx_epi = np.intersect1d(la_epi_vtx,rspv_idx)
	rspv_idx_epi = reindex_vtx(rspv_idx_epi,la_epi_vtx)

	if surface=="endo":
		surf_name = output_folder+"/la/laa_vp.surf"
	else:
		surf_name = output_folder+"/la/laa.surf"
	laa_surf = read_elem(surf_name,el_type="Tr",tags=False)
	laa_idx = surf2vtx(laa_surf)
	laa_idx_epi = np.intersect1d(la_epi_vtx,laa_idx)
	laa_idx_epi = reindex_vtx(laa_idx_epi,la_epi_vtx)

	mitral_surf = read_elem(output_folder+"/la/mitral.surf",el_type="Tr",tags=False)
	mitral_vtx = surf2vtx(mitral_surf)
	cog_mitral = np.mean(pts[mitral_vtx,:],axis=0)
	cog_lspv = np.mean(pts[lspv_idx,:],axis=0)
	cog_rspv = np.mean(pts[rspv_idx,:],axis=0)
	cog_ripv = np.mean(pts[ripv_idx,:],axis=0)
	cog_laa = np.mean(pts[laa_idx,:],axis=0)

	v1 = cog_lspv-cog_mitral
	v1 = v1/np.linalg.norm(v1)

	v2 = cog_rspv-cog_mitral
	v2 = v2/np.linalg.norm(v1)

	n_plane = np.cross(v1,v2)
	n_plane = n_plane/np.linalg.norm(n_plane)

	long_axis = cog_rspv-cog_mitral
	long_axis = long_axis/np.linalg.norm(long_axis)

	dot_prod = 1e10
	print('Finding most posterior LAA point...')
	for v in laa_idx_epi:
		dot_prod_tmp = np.dot(pts_la_epi[v,:]-cog_mitral,n_plane)
		
		if dot_prod_tmp<dot_prod:
			idx_posterior_laa = v
			dot_prod = dot_prod_tmp
	pts_laa_posterior = pts_la_epi[idx_posterior_laa,:]
	n_distance_posterior = np.dot(pts_lspv_posterior-pts_lspv_roof,n_plane)
	pts_laa_posterior_pj = pts_laa_posterior+n_plane*n_distance_posterior
	cog_mitral_pj = cog_mitral+n_plane*n_distance_posterior

	distance_laa = np.linalg.norm(pts_la_epi-pts_laa_posterior_pj,axis=1)
	landmark_laa_posterior = pts_la_epi[np.where(distance_laa==np.min(distance_laa))[0][0]]

	print("Finding septal posterior point...")
	v1 = cog_ripv-cog_mitral
	v1 = v1/np.linalg.norm(v1)

	n_septum = np.cross(v1,v2)
	n_septum = n_septum/np.linalg.norm(n_septum)

	dot_prod = 1e10
	for i in range(pts_la_epi.shape[0]):
		dot_prod_tmp = np.dot(pts_la_epi[i,:]-landmark_laa_posterior,n_septum)
		dot_prod_vertical = np.dot(pts_la_epi[i,:]-landmark_laa_posterior,long_axis)

		if dot_prod_tmp<dot_prod and dot_prod_vertical>5000.0*scale_factor:
			idx_posterior_septum = i
			dot_prod = dot_prod_tmp

	landmark_sept_posterior = pts_la_epi[idx_posterior_septum,:]

	landmarks = np.concatenate((landmark_laa_posterior,landmark_sept_posterior),axis=0)
	landmarks = np.reshape(landmarks,(2,3))

	# --------------------------------------------------------------------------------- #
	region_landmarks = np.zeros((2,3),dtype=float)
	region_landmarks[0,:] = pts_laa_posterior

	dot_prod = 0.
	print('Finding most anterior LAA point...')
	for v in laa_idx_epi:
		dot_prod_tmp = np.dot(pts_la_epi[v,:]-cog_mitral,n_plane)
		
		if dot_prod_tmp>dot_prod:
			idx_anterior_laa = v
			dot_prod = dot_prod_tmp
	region_landmarks[1,:] = pts_la_epi[idx_anterior_laa,:]

	return landmarks,region_landmarks

def find_septal_point(output_folder,
					  surface="epi"):

	pts = read_pts(output_folder+"/ra/ra.pts")

	ra_epi_surf = read_elem(output_folder+"/ra/ra_"+surface+".surf",el_type="Tr",tags=False)
	ra_epi_vtx = surf2vtx(ra_epi_surf)
	pts_ra_epi = pts[ra_epi_vtx,:]
	ra_epi_surf_reindexed = reindex_surf(ra_epi_vtx,ra_epi_surf)

	if surface=="endo":
		surf_name = output_folder+"/ra/ivc_vp.surf"
	else:
		surf_name = output_folder+"/ra/ivc.surf"
	ivc_surf = read_elem(surf_name,el_type="Tr",tags=False)
	ivc_idx = surf2vtx(ivc_surf)
	ivc_idx_epi = np.intersect1d(ra_epi_vtx,ivc_idx)
	ivc_idx_epi = reindex_vtx(ivc_idx_epi,ra_epi_vtx)

	if surface=="endo":
		surf_name = output_folder+"/ra/svc_vp.surf"
	else:
		surf_name = output_folder+"/ra/svc.surf"
	svc_surf = read_elem(surf_name,el_type="Tr",tags=False)
	svc_idx = surf2vtx(svc_surf)
	svc_idx_epi = np.intersect1d(ra_epi_vtx,svc_idx)
	svc_idx_epi = reindex_vtx(svc_idx_epi,ra_epi_vtx)

	tricuspid_surf = read_elem(output_folder+"/ra/tricuspid.surf",el_type="Tr",tags=False)
	tricuspid_vtx = surf2vtx(tricuspid_surf)
	cog_tricuspid = np.mean(pts[tricuspid_vtx,:],axis=0)
	cog_svc = np.mean(pts[svc_idx,:],axis=0)
	cog_ivc = np.mean(pts[ivc_idx,:],axis=0)
	v_svc_ivc = cog_svc-cog_ivc
	v_svc_ivc = v_svc_ivc/np.linalg.norm(v_svc_ivc)
	v_tricuspid_ivc = cog_tricuspid-cog_ivc
	v_tricuspid_ivc = v_tricuspid_ivc/np.linalg.norm(v_tricuspid_ivc)

	cog_svc_tricuspid = 0.5*(cog_tricuspid+cog_svc)

	n_septum = np.cross(v_tricuspid_ivc,v_svc_ivc)
	n_septum = n_septum/np.linalg.norm(n_septum)

	print('Extracting septal part to make sure pygeodesic does not go out of memory...')
	septum_extract_eidx = []
	cog_el = np.zeros((ra_epi_surf_reindexed.shape[0],3),dtype=float)
	for i,t in enumerate(ra_epi_surf_reindexed):
		cog_t = np.mean(pts_ra_epi[t,:],axis=0)
		cog_el[i,:] = cog_t
		dot_prod = np.dot(cog_t-cog_svc_tricuspid,n_septum)
		if dot_prod<0:
			septum_extract_eidx.append(i)
	surf_epi_septum = ra_epi_surf_reindexed[septum_extract_eidx,:]
	septum_extract_vtx = surf2vtx(surf_epi_septum)
	surf_epi_septum_reindexed = reindex_surf(septum_extract_vtx,surf_epi_septum)
	pts_epi_septum = pts_ra_epi[septum_extract_vtx,:]

	distances = np.linalg.norm(pts_epi_septum-cog_svc_tricuspid,axis=1)
	idx_septum = np.where(distances==np.min(distances))[0]
	landmark_septum = pts_epi_septum[idx_septum[0]]

	idx_septum = septum_extract_vtx[idx_septum]

	radius = 0.5*np.linalg.norm(landmark_septum-cog_svc)
	centre = 0.5*(landmark_septum+cog_svc)
	distances = np.linalg.norm(cog_el-centre,axis=1)
	septum_smaller_eidx = np.where(distances<radius)[0]
	septum_extract_eidx = np.intersect1d(septum_extract_eidx,septum_smaller_eidx)
	surf_epi_septum = ra_epi_surf_reindexed[septum_extract_eidx,:]
	septum_extract_vtx = surf2vtx(surf_epi_septum)
	surf_epi_septum_reindexed = reindex_surf(septum_extract_vtx,surf_epi_septum)
	pts_epi_septum = pts_ra_epi[septum_extract_vtx,:]

	mesh = meshio.Mesh(pts_epi_septum,[('triangle',surf_epi_septum_reindexed)])
	mesh.write(output_folder+'/ra/ra_epi_septum.vtu')

	geoalg = geodesic.PyGeodesicAlgorithmExact(pts_epi_septum, surf_epi_septum_reindexed)
	svc_idx_epi = reindex_vtx(svc_idx_epi,septum_extract_vtx)
	idx_septum = np.where(septum_extract_vtx==idx_septum)[0]

	distances, best_source = geoalg.geodesicDistances(idx_septum,None)
	distances_svc = distances[svc_idx_epi]
	svc_idx_epi_geod = svc_idx_epi[np.where(distances_svc==np.min(distances_svc))[0][0]]

	landmark_svc_septum = pts_epi_septum[svc_idx_epi_geod,:]
	landmarks = np.concatenate((landmark_septum,landmark_svc_septum))
	landmarks = np.reshape(landmarks,(2,3))

	return landmarks

def find_SVC_IVC_roof_points(output_folder,
							 landmarks_septum,
							 scale_factor=1.0,
							 surface="epi"):

	landmark_septum = landmarks_septum[0,:]
	landmark_svc_septum = landmarks_septum[1,:]

	pts = read_pts(output_folder+"/ra/ra.pts")

	ra_epi_surf = read_elem(output_folder+"/ra/ra_"+surface+".surf",el_type="Tr",tags=False)
	ra_epi_vtx = surf2vtx(ra_epi_surf)
	pts_ra_epi = pts[ra_epi_vtx,:]
	ra_epi_surf_reindexed = reindex_surf(ra_epi_vtx,ra_epi_surf)

	if surface=="endo":
		surf_name = output_folder+"/ra/ivc_vp.surf"
	else:
		surf_name = output_folder+"/ra/ivc.surf"
	ivc_surf = read_elem(surf_name,el_type="Tr",tags=False)
	ivc_idx = surf2vtx(ivc_surf)
	ivc_idx_epi = np.intersect1d(ra_epi_vtx,ivc_idx)
	ivc_idx_epi = reindex_vtx(ivc_idx_epi,ra_epi_vtx)

	if surface=="endo":
		surf_name = output_folder+"/ra/svc_vp.surf"
	else:
		surf_name = output_folder+"/ra/svc.surf"
	svc_surf = read_elem(surf_name,el_type="Tr",tags=False)
	svc_idx = surf2vtx(svc_surf)
	svc_idx_epi = np.intersect1d(ra_epi_vtx,svc_idx)
	svc_idx_epi = reindex_vtx(svc_idx_epi,ra_epi_vtx)

	tricuspid_surf = read_elem(output_folder+"/ra/tricuspid.surf",el_type="Tr",tags=False)
	tricuspid_vtx = surf2vtx(tricuspid_surf)
	cog_tricuspid = np.mean(pts[tricuspid_vtx,:],axis=0)
	cog_svc = np.mean(pts[svc_idx,:],axis=0)
	cog_ivc = np.mean(pts[ivc_idx,:],axis=0)
	v_svc_ivc = cog_svc-cog_ivc
	v_svc_ivc = v_svc_ivc/np.linalg.norm(v_svc_ivc)
	v_tricuspid_ivc = cog_tricuspid-cog_ivc
	d_tricuspid_ivc = np.linalg.norm(v_tricuspid_ivc)
	v_tricuspid_ivc = v_tricuspid_ivc/d_tricuspid_ivc

	n_septum = np.cross(v_tricuspid_ivc,v_svc_ivc)
	n_septum = n_septum/np.linalg.norm(n_septum)

	dot_prod = 0.
	print('Finding posterior SVC rim...')
	for v in svc_idx_epi:
		dot_prod_tmp = np.dot(pts_ra_epi[v,:]-cog_tricuspid,n_septum)

		if dot_prod_tmp>dot_prod:
			idx_posterior_svc = v
			dot_prod = dot_prod_tmp
	landmark_svc_posterior = pts_ra_epi[idx_posterior_svc,:]

	cog_tricuspid_pj = cog_ivc+v_svc_ivc*np.dot(v_svc_ivc,d_tricuspid_ivc*v_tricuspid_ivc)

	long_axis = cog_tricuspid_pj-cog_tricuspid
	long_axis = long_axis/np.linalg.norm(long_axis)

	proj_ra_epi = np.dot(pts_ra_epi-cog_tricuspid,long_axis)
	ra_epi_roof = np.where(proj_ra_epi==np.max(proj_ra_epi))[0]

	print('Extracting roof to make sure pygeodesic does not go out of memory...')
	roof_extract_eidx = []
	for i,t in enumerate(ra_epi_surf_reindexed):
		cog_t = np.mean(pts_ra_epi[t,:],axis=0)
		dot_prod = np.dot(cog_t-cog_tricuspid_pj,long_axis)
		if dot_prod>-2000.0*scale_factor:
			roof_extract_eidx.append(i)
	surf_epi_roof = ra_epi_surf_reindexed[roof_extract_eidx,:]
	roof_extract_vtx = surf2vtx(surf_epi_roof)
	surf_epi_roof_reindexed = reindex_surf(roof_extract_vtx,surf_epi_roof)
	pts_epi_roof = pts_ra_epi[roof_extract_vtx,:]

	mesh = meshio.Mesh(pts_epi_roof,[('triangle',surf_epi_roof_reindexed)])
	mesh.write(output_folder+'/ra/ra_epi_roof.vtu')

	geoalg = geodesic.PyGeodesicAlgorithmExact(pts_epi_roof, surf_epi_roof_reindexed)
	
	idx_posterior_svc = np.where(roof_extract_vtx==idx_posterior_svc)[0]
	ivc_idx_epi = reindex_vtx(ivc_idx_epi,roof_extract_vtx)

	distances, best_source = geoalg.geodesicDistances(idx_posterior_svc,None)
	distances_ivc = distances[ivc_idx_epi]
	ivc_idx_epi_geod = ivc_idx_epi[np.where(distances_ivc==np.min(distances_ivc))[0][0]]
	landmark_ivc_posterior = pts_epi_roof[ivc_idx_epi_geod,:]

	landmarks = np.concatenate((landmark_svc_posterior,landmark_ivc_posterior),axis=0)
	landmarks = np.reshape(landmarks,(2,3))

	# ----------------------------------------------------------------------- #
	landmarks_regions = np.zeros((2,3),dtype=float)

	midway = 0.5*(landmark_svc_posterior+landmark_ivc_posterior)
	distances = np.linalg.norm(pts_epi_roof-midway,axis=1)
	landmarks_regions[0,:] = pts_epi_roof[np.where(distances==np.min(distances))[0][0],:]

	landmarks_regions[1,:] = landmark_svc_posterior

	return landmarks,landmarks_regions

def find_IVC_posterior_points(output_folder,
							  landmarks,
							  scale_factor=1.0,
							  surface="epi"):

	landmark_septum = landmarks[0,:]
	landmark_svc_septum = landmarks[1,:]
	landmark_svc_posterior = landmarks[2,:]
	landmark_ivc_top = landmarks[3,:]

	pts = read_pts(output_folder+"/ra/ra.pts")

	ra_epi_surf = read_elem(output_folder+"/ra/ra_"+surface+".surf",el_type="Tr",tags=False)
	ra_epi_vtx = surf2vtx(ra_epi_surf)
	pts_ra_epi = pts[ra_epi_vtx,:]
	ra_epi_surf_reindexed = reindex_surf(ra_epi_vtx,ra_epi_surf)

	if surface=="endo":
		surf_name = output_folder+"/ra/ivc_vp.surf"
	else:
		surf_name = output_folder+"/ra/ivc.surf"
	ivc_surf = read_elem(surf_name,el_type="Tr",tags=False)
	ivc_idx = surf2vtx(ivc_surf)
	ivc_idx_epi = np.intersect1d(ra_epi_vtx,ivc_idx)
	ivc_idx_epi = reindex_vtx(ivc_idx_epi,ra_epi_vtx)

	if surface=="endo":
		surf_name = output_folder+"/ra/svc_vp.surf"
	else:
		surf_name = output_folder+"/ra/svc.surf"
	svc_surf = read_elem(surf_name,el_type="Tr",tags=False)
	svc_idx = surf2vtx(svc_surf)
	svc_idx_epi = np.intersect1d(ra_epi_vtx,svc_idx)
	svc_idx_epi = reindex_vtx(svc_idx_epi,ra_epi_vtx)

	tricuspid_surf = read_elem(output_folder+"/ra/tricuspid.surf",el_type="Tr",tags=False)
	tricuspid_vtx = surf2vtx(tricuspid_surf)
	tricuspid_idx_epi = np.intersect1d(ra_epi_vtx,tricuspid_vtx)
	tricuspid_idx_epi = reindex_vtx(tricuspid_idx_epi,ra_epi_vtx)	

	cog_tricuspid = np.mean(pts[tricuspid_vtx,:],axis=0)
	cog_svc = np.mean(pts[svc_idx,:],axis=0)
	cog_ivc = np.mean(pts[ivc_idx,:],axis=0)
	v_svc_ivc = cog_svc-cog_ivc
	v_svc_ivc = v_svc_ivc/np.linalg.norm(v_svc_ivc)
	v_tricuspid_ivc = cog_tricuspid-cog_ivc
	d_tricuspid_ivc = np.linalg.norm(v_tricuspid_ivc)
	v_tricuspid_ivc = v_tricuspid_ivc/d_tricuspid_ivc

	v_ivc_across = cog_ivc-landmark_ivc_top	
	v_ivc_across = v_ivc_across/np.linalg.norm(v_ivc_across)

	dot_prod = 0.
	for v in ivc_idx_epi:
		dot_prod_tmp = np.dot(pts_ra_epi[v,:]-landmark_ivc_top,v_ivc_across)

		if dot_prod_tmp>dot_prod:
			dot_prod = dot_prod_tmp
			idx_ivc_bottom = v
	landmarks_ivc_bottom = pts_ra_epi[idx_ivc_bottom,:]

	distances = np.linalg.norm(pts_ra_epi[tricuspid_idx_epi	,:]-landmarks_ivc_bottom,axis=1)
	idx_tricuspid = tricuspid_idx_epi[np.where(distances==np.min(distances))[0][0]]
	shortest = np.min(distances)

	midway = 0.5*(pts_ra_epi[idx_tricuspid,:]+landmarks_ivc_bottom)
	distances = np.linalg.norm(pts_ra_epi-midway,axis=1)
	idx_tricuspid_posterior = np.where(distances==np.min(distances))[0][0]
	landmark_tricuspid_posterior = pts_ra_epi[idx_tricuspid_posterior,:]

	landmarks = np.concatenate((landmarks_ivc_bottom,landmark_tricuspid_posterior))
	landmarks = np.reshape(landmarks,(2,3))

	# ----------------------------------------------------------------------------------- #
	region_landmarks = np.zeros((2,3),dtype=float)
	region_landmarks[0,:] = landmarks_ivc_bottom

	v_tricuspid_svc = cog_svc-cog_tricuspid
	v_tricuspid_svc = v_tricuspid_svc/np.linalg.norm(v_tricuspid_svc)

	v_tricuspid_septum = landmark_septum-cog_tricuspid
	v_tricuspid_septum = v_tricuspid_septum/np.linalg.norm(v_tricuspid_septum)

	n_raa = np.cross(v_tricuspid_septum,v_tricuspid_svc)
	n_raa = n_raa/np.linalg.norm(n_raa)

	septal_point_CS = landmark_septum-n_raa*10000.0*scale_factor
	distances = np.linalg.norm(pts_ra_epi-septal_point_CS,axis=1)
	region_landmarks[1,:] = pts_ra_epi[np.where(distances==np.min(distances))[0][0],:]

	return landmarks,region_landmarks

def find_raa_base(output_folder,
				  raa_apex,
				  raa_length=10000.0,
				  surface="epi"):

	pts = read_pts(output_folder+"/ra/ra.pts")

	ra_epi_surf = read_elem(output_folder+"/ra/ra_"+surface+".surf",el_type="Tr",tags=False)
	ra_epi_vtx = surf2vtx(ra_epi_surf)
	pts_ra_epi = pts[ra_epi_vtx,:]
	ra_epi_surf_reindexed = reindex_surf(ra_epi_vtx,ra_epi_surf)

	cog_ra = np.mean(pts_ra_epi,axis=0)

	if surface=="endo":
		surf_name = output_folder+"/ra/ivc_vp.surf"
	else:
		surf_name = output_folder+"/ra/ivc.surf"
	ivc_surf = read_elem(surf_name,el_type="Tr",tags=False)
	ivc_idx = surf2vtx(ivc_surf)
	ivc_idx_epi = np.intersect1d(ra_epi_vtx,ivc_idx)
	ivc_idx_epi = reindex_vtx(ivc_idx_epi,ra_epi_vtx)

	v_ivc_raa = raa_apex-cog_ra
	v_ivc_raa = v_ivc_raa/np.linalg.norm(v_ivc_raa)

	raa_tip_pj = raa_apex-v_ivc_raa*raa_length
	distances = np.linalg.norm(pts_ra_epi-raa_tip_pj,axis=1)
	landmark_raa_base = pts_ra_epi[np.where(distances==np.min(distances))[0][0],:]

	landmarks = np.reshape(landmark_raa_base,(1,3))

	return landmarks

def find_raa_points(output_folder,
					septal_point,
					raa_length=10000.0,
					surface="epi"):

	pts = read_pts(output_folder+"/ra/ra.pts")

	ra_epi_surf = read_elem(output_folder+"/ra/ra_"+surface+".surf",el_type="Tr",tags=False)
	ra_epi_vtx = surf2vtx(ra_epi_surf)
	pts_ra_epi = pts[ra_epi_vtx,:]
	ra_epi_surf_reindexed = reindex_surf(ra_epi_vtx,ra_epi_surf)

	cog_ra = np.mean(pts_ra_epi,axis=0)

	if surface=="endo":
		surf_name = output_folder+"/ra/ivc_vp.surf"
	else:
		surf_name = output_folder+"/ra/ivc.surf"
	ivc_surf = read_elem(surf_name,el_type="Tr",tags=False)
	ivc_idx = surf2vtx(ivc_surf)
	ivc_idx_epi = np.intersect1d(ra_epi_vtx,ivc_idx)
	ivc_idx_epi = reindex_vtx(ivc_idx_epi,ra_epi_vtx)

	if surface=="endo":
		surf_name = output_folder+"/ra/svc_vp.surf"
	else:
		surf_name = output_folder+"/ra/svc.surf"
	svc_surf = read_elem(surf_name,el_type="Tr",tags=False)
	svc_idx = surf2vtx(svc_surf)
	svc_idx_epi = np.intersect1d(ra_epi_vtx,svc_idx)
	svc_idx_epi = reindex_vtx(svc_idx_epi,ra_epi_vtx)	

	tricuspid_surf = read_elem(output_folder+"/ra/tricuspid.surf",el_type="Tr",tags=False)
	tricuspid_vtx = surf2vtx(tricuspid_surf)
	tricuspid_idx_epi = np.intersect1d(ra_epi_vtx,tricuspid_vtx)
	tricuspid_idx_epi = reindex_vtx(tricuspid_idx_epi,ra_epi_vtx)		

	cog_tricuspid = np.mean(pts[tricuspid_vtx,:],axis=0)
	cog_svc = np.mean(pts[svc_idx,:],axis=0)
	cog_ivc = np.mean(pts[ivc_idx,:],axis=0)	

	v_tricuspid_svc = cog_svc-cog_tricuspid
	v_tricuspid_svc = v_tricuspid_svc/np.linalg.norm(v_tricuspid_svc)	

	v_tricuspid_septum = septal_point-cog_tricuspid
	v_tricuspid_septum = v_tricuspid_septum/np.linalg.norm(v_tricuspid_septum)	

	n_raa = np.cross(v_tricuspid_septum,v_tricuspid_svc)
	n_raa = n_raa/np.linalg.norm(n_raa)

	print('Finding RAA tip...')
	dot_prod = 0.
	for p in pts_ra_epi:
		dot_prod_tmp = np.dot(p-cog_ivc,n_raa)	

		if dot_prod_tmp>dot_prod:
			landmark_raa_tip = p
			dot_prod = dot_prod_tmp

	# cog_ra = np.mean(np.concatenate((cog_tricuspid,cog_svc,cog_ivc),axis=0),axis=0)
	# distances = np.linalg.norm(pts_ra_epi-cog_ivc,axis=1)
	# idx_raa = np.where(distances==np.max(distances))[0][0]
	# landmark_raa_tip = pts_ra_epi[idx_raa,:]

	v_ivc_raa = landmark_raa_tip-cog_ivc
	v_ivc_raa = v_ivc_raa/np.linalg.norm(v_ivc_raa)

	raa_tip_pj = landmark_raa_tip-v_ivc_raa*raa_length
	distances = np.linalg.norm(pts_ra_epi-raa_tip_pj,axis=1)
	landmark_raa_base = pts_ra_epi[np.where(distances==np.min(distances))[0][0],:]

	landmarks = np.concatenate((landmark_raa_tip,landmark_raa_base))
	landmarks = np.reshape(landmarks,(2,3))

	return landmarks