import numpy as np
import json
import os

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

def read_tets_cnnx(filename):
	print('Reading '+filename+'...')

	tets = []
	cnnx = []
	with open(filename) as f:
		content = f.read().splitlines()
		for i in range(1,len(content)):
			if content[i][0:2] == 'Tt':
				tets.append(np.fromstring(content[i][3:].strip(), dtype=int, sep=' '))
			elif content[i][0:2] == 'Ln':
		  		cnnx.append(np.fromstring(content[i][3:].strip(), dtype=int, sep=' '))
	tets = np.array(tets)
	cnnx = np.array(cnnx)

	return tets,cnnx

def read_uvc(filename):
	print('Reading '+filename+'...')

	return np.loadtxt(filename, dtype=float, skiprows=0)

def read_vtx(filename,init_row=2):
	print('Reading '+filename+'...')

	return np.loadtxt(filename, dtype=int, skiprows=init_row)

def read_landmarks(filename):
	print('Reading '+filename+'...')

	return np.loadtxt(filename, dtype=float, skiprows=0)

def read_txt(filename):
	print('Reading '+filename+'...')

	return np.loadtxt(filename, dtype=float, skiprows=0)

def read_dat(filename,header_lines=0):
	print('Reading '+filename+'...')

	return np.loadtxt(filename, dtype=float, skiprows=header_lines)

def read_CV_file(filename):
	print('Reading '+filename+'...')

	return np.loadtxt(filename,dtype=float,skiprows=0,delimiter=":",usecols=[1])

def read_nod(filename):
	nod = np.fromfile(filename, dtype=int, count=-1)

	return nod

def numpy_hook(dct):
    for key, value in dct.items():
        if isinstance(value, list):
            value = np.array(value)
            dct[key] = value
    return dct

def load_json(filename):
	print('Reading '+filename+'...')

	dct = {}
	with open(filename, "r") as f:
		dct = json.load(f, object_hook=numpy_hook)
	return dct

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

def save_json(dct, filename):
    with open(filename, "w") as f:
        json.dump(dct, f, cls=NumpyEncoder, indent=4)
    return

def read_clinical(filename):

	data = np.loadtxt(filename,delimiter=',',skiprows=1,usecols=(1,2,3,4,5))

	return data

def write_pts(pts,filename):

	print('Writing '+filename+'...')

	assert pts.shape[1] == 3
	with open(filename, 'w') as fp:
		fp.write('{}\n'.format(pts.shape[0]))
		for pnt in pts:
			fp.write('{0[0]} {0[1]} {0[2]}\n'.format(pnt))
	fp.close()

def write_elem(elem,
			   tags,
			   filename,
			   el_type='Tt'):
	print('Writing '+filename+'...')

	if el_type=='Tt':
		assert elem.shape[1] == 4
	elif el_type=='Tr':
		assert elem.shape[1] == 3
	elif el_type=='Ln':
		assert elem.shape[1] == 2
	else:
		raise Exception('element type not recognised. Accepted: Tt, Tr, Ln')

	assert elem.shape[0] == tags.shape[0]

	with open(filename, 'w') as fe:
		fe.write('{}\n'.format(elem.shape[0]))
		for i,el in enumerate(elem):
			fe.write(el_type)
			for e in el:
				fe.write(' '+str(e))
			fe.write(' '+str(tags[i]))
			fe.write('\n')
	fe.close()


def write_lon(lon,filename):
	print('Writing '+filename+'...')

	assert lon.shape[1] % 3 == 0
	with open(filename, 'w') as fl:
		fl.write('{}\n'.format(int(lon.shape[1]/3)))
		for ll in lon:
			for i,l in enumerate(ll):
				if i==len(ll)-1:
					fl.write(str(l)+'\n')
				else:
					fl.write(str(l)+' ')
	fl.close()

def write_uvcs(filename, uvcs):
	print('Writing '+filename+'...')

	with open(filename, 'w') as f:
		f.write('{}\n'.format(uvcs.shape[0]))
		for uvc in uvcs:
			f.write('{0[0]}\t{0[1]}\t{0[2]}\t{0[3]}\n'.format(uvc))

def write_dat(filename, dat):
	print('Writing '+filename+'...')

	with open(filename, 'w') as fd:
		for d in dat:
			fd.write('{}\n'.format(d))

def write_vtx(filename, vtx,init_row=2):
	print('Writing '+filename+'...')

	with open(filename, 'w') as fd:
		if init_row==2:
			fd.write('{}\n'.format(vtx.shape[0]))
			fd.write('intra\n')
		for v in vtx:
			fd.write('{}\n'.format(int(v)))

def write_tets_ln(filename,elem,cnnx):
	print('Writing '+filename+'...')

	with open(filename, 'w') as fp:
		fp.write('{}\n'.format(elem.shape[0] + cnnx.shape[0]))
		for el in elem:
			fp.write('Tt {} {} {} {} {}\n'.format(int(el[0]),int(el[1]),int(el[2]),int(el[3]),int(el[4])))
		for cn in cnnx:
			fp.write('Ln {} {} {}\n'.format(int(cn[0]),int(cn[1]),int(cn[2])))


def write_surf(filename,surf):
	print('Writing '+filename+'...')

	with open(filename, 'w') as fp:
		fp.write('{}\n'.format(surf.shape[0]))
		for t in surf:
			fp.write('Tr {} {} {}\n'.format(int(t[0]),int(t[1]),int(t[2])))

def vtx_to_pts(msh_name,vtx_name,init_row=0):
	print('Converting '+vtx_name+' to pts...')

	pts = read_pts(msh_name+".pts")
	
	vtx = read_vtx(vtx_name,init_row=init_row)
	write_pts(pts[vtx,:],vtx_name+".pts")


def surf2vtx(surf_name):
	print('Converting '+surf_name+' to vtx...')

	surf = read_elem(surf_name,el_type='Tr',tags=False)

	vtx = np.unique(surf.flatten())

	return vtx