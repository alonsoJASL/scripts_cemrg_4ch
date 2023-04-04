import numpy as np
import copy
import pygeodesic.geodesic as geodesic
import json
import meshio
import vtk
import os
from vtk.util import numpy_support

class NumpyEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, np.integer):
			return int(obj)
		elif isinstance(obj, np.floating):
			return float(obj)
		elif isinstance(obj, np.ndarray):
			return obj.tolist()
		return json.JSONEncoder.default(self, obj)

def read_pts(filename):
	print('Reading '+filename+'...')
	return np.loadtxt(filename, dtype=float, skiprows=1)

def read_elem(filename,el_type='Tt',tags=True):
	print('Reading '+filename+'...')

	if el_type=='Tt':
		if tags:
			return np.loadtxt(filename, dtype=int, skiprows=1, usecols=(1,2,3,4,5))
		else:
			return np.loadtxt(filename, dtype=int, skiprows=1, usecols=(1,2,3,4))
	elif el_type=='Tr':
		if tags:
			return np.loadtxt(filename, dtype=int, skiprows=1, usecols=(1,2,3,4))
		else:
			return np.loadtxt(filename, dtype=int, skiprows=1, usecols=(1,2,3))
	elif el_type=='Ln':
		if tags:
			return np.loadtxt(filename, dtype=int, skiprows=1, usecols=(1,2,3))
		else:
			return np.loadtxt(filename, dtype=int, skiprows=1, usecols=(1,2))
	else:
		raise Exception('element type not recognised. Accepted: Tt, Tr, Ln')

def read_lon(filename):
	print('Reading '+filename+'...')

	return np.loadtxt(filename, dtype=float, skiprows=1)

def setup_sim(heartFolder,presimFolder,fch_apex,fch_sa):
	os.system("mkdir "+heartFolder+"/sims_folder")

	os.system("cp "+presimFolder+"/elem_dat_UVC_ek_combined.dat "+heartFolder+"/sims_folder/pericardium_scale.dat")
	os.system("cp "+presimFolder+"/surfaces_simulation/epicardium.surf "+heartFolder+"/sims_folder")
	os.system("cp "+presimFolder+"/epicardium_for_sim.surf "+heartFolder+"/sims_folder")
	os.system("cp "+presimFolder+"/surfaces_simulation/LA_endo.surf "+heartFolder+"/sims_folder")
	os.system("cp "+presimFolder+"/surfaces_simulation/LV_endo.surf "+heartFolder+"/sims_folder")
	os.system("cp "+presimFolder+"/myocardium_AV_FEC_BB.* "+heartFolder+"/sims_folder")
	os.system("cp "+presimFolder+"/surfaces_simulation/RA_endo.surf "+heartFolder+"/sims_folder")
	os.system("cp "+presimFolder+"/surfaces_simulation/RV_endo.surf "+heartFolder+"/sims_folder")
	os.system("cp "+presimFolder+"/surfaces_simulation/surfaces_rings/RPVs.surf "+heartFolder+"/sims_folder")
	os.system("cp "+presimFolder+"/surfaces_simulation/surfaces_rings/RPVs.surf.vtx "+heartFolder+"/sims_folder")
	os.system("cp "+presimFolder+"/surfaces_simulation/surfaces_rings/SVC.surf "+heartFolder+"/sims_folder")
	os.system("cp "+presimFolder+"/surfaces_simulation/surfaces_rings/SVC.surf.vtx "+heartFolder+"/sims_folder")

	os.system("cp "+fch_apex+" "+heartFolder+"/sims_folder")
	os.system("cp "+fch_sa+" "+heartFolder+"/sims_folder")
