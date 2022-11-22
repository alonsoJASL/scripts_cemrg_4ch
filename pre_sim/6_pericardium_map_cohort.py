#!/usr/bin/env python2

import os
import sys
import math
import subprocess
import copy
#import matplotlib as mpl
#import matplotlib.pyplot as mplplot
import numpy as np
import sets
import scipy.linalg as spla
import scipy.signal as spsig
import argparse

parser = argparse.ArgumentParser(description='To run: python3 pericardium_map_cohort.py [heart_folder]')
parser.add_argument("heart_folder")
args = parser.parse_args()
basedir = args.heart_folder

def read_pnts(filename):
    return np.loadtxt(filename, dtype=float, skiprows=1)


def write_pnts(filename, pts):
    assert len(pts.shape) == 2 and pts.shape[1] == 3
    with open(filename, 'w') as fp:
        fp.write('{}\n'.format(pts.shape[0]))
        for pnt in pts:
            fp.write('{0[0]}\t{0[1]}\t{0[2]}\n'.format(pnt))


def read_surface(filename):
    return np.loadtxt(filename, dtype=int, skiprows=1, usecols=(1,2,3))


def write_surface(filename, surfs):
    assert len(surfs.shape) == 2 and surfs.shape[1] == 3
    with open(filename, 'w') as fp:
        fp.write('{}\n'.format(surfs.shape[0]))
        for tri in surfs:
            fp.write('Tr {0[0]}\t{0[1]}\t{0[2]}\n'.format(tri))


def read_neubc(filename):
   return np.loadtxt(filename, dtype=int, skiprows=1, usecols=(0,1,2,3,4,5)) 


def read_elems(filename):
  return np.loadtxt(filename, dtype=int, skiprows=1, usecols=(1,2,3,4,5))


def vector_cprod(vec1, vec2):
  return np.array([vec1[1]*vec2[2]-vec1[2]*vec2[1],
                   vec1[2]*vec2[0]-vec1[0]*vec2[2],
                   vec1[0]*vec2[1]-vec1[1]*vec2[0]])

def read_dat(filename):
    return np.loadtxt(filename, dtype=float, skiprows=0)

def read_vtx(filename):
    return np.loadtxt(filename, dtype=int, skiprows=2)

def vector_sprod(vec1, vec2):
  return vec1[0]*vec2[0]+vec1[1]*vec2[1]+vec1[2]*vec2[2]


def create_csys(vec):
    vec0 = None
    vec1 = None
    if (vec[0] < 0.5) and (vec[1] < 0.5):
        tmp = math.sqrt(vec[1]*vec[1]+vec[2]*vec[2])
        vec1 = np.array([0.0, -vec[2]/tmp, vec[1]/tmp])
        vec0 = vector_cprod(vec, vec1)
    else:
        tmp = math.sqrt(vec[0]*vec[0]+vec[1]*vec[1])
        vec1 = np.array([vec[1]/tmp, -vec[0]/tmp, 0.0])
        vec0 = vector_cprod(vec, vec1)
    return [vec0, vec1, vec]

def main():

    subprocess.call('clear')

    outfile='elem_dat_UVC_ek.dat'

    basename = basedir+'/pre_simulation/myocardium_AV_FEC_BB'
    pnts = read_pnts(basename+'.pts')    
    elem = read_elems(basename+'.elem')

    print('Read mesh')    

    # datdir = basedir+'/biv/UVC_ek/UVC'
    datdir = basedir+'/surfaces_uvc/BiV/uvc'
    # datname = os.path.join(datdir, 'COORDS_Z')
    datname = os.path.join(datdir, 'BiV.uvc_z')
    UVCpts = read_dat(datname+'.dat')

    print('Found z coords')

    # vtxdir = basedir+'/biv'
    # vtxname = os.path.join(vtxdir, 'biv')
    vtxdir = basedir+'/surfaces_uvc/BiV'
    vtxname = os.path.join(vtxdir, 'BiV')
    vtxsubmsh = np.fromfile(vtxname+".nod", dtype=int, count=-1)

    print('Found BiV mesh')

    pcatags = [1, 2]
    UVCptsmsh = np.zeros(len(pnts[:,0]))
    for i, ind in enumerate(vtxsubmsh):
        UVCptsmsh[ind] = UVCpts[i]

    print('Something to do with pericardium tags (part 1)')

    UVCelem = []
    for i, elm in enumerate(elem):
        if ( elem[i,4] in pcatags ):
            UVCelem.append((UVCptsmsh[elm[0]]+UVCptsmsh[elm[1]]+UVCptsmsh[elm[2]]+UVCptsmsh[elm[3]])*0.25)
        else:
            UVCelem.append(0.0)

    print('Something to do with pericardium tags (part 2)')

    np.savetxt(os.path.join(basedir+'/pre_simulation/', 'UVC_elem.dat'), UVCelem, fmt='%.8f')

    # compute the data on the elements
    p1 = 1.5266
    p2 = -0.37
    p3 = 0.4964
    p4 = 0

    th = 0.82

    elemdat = []
    for i, l in enumerate(UVCelem):
        if ( elem[i,4] in pcatags ):
            if (UVCelem[i] >= th):
                elemdat.append(0.0) 
            else: 
                x = UVCelem[i]
                x_m = th-x
                elemdat.append(p1*x_m**3 + p2*x_m**2 + p3*x_m + p4)
        else:
            elemdat.append(0.0)    

    # np.savetxt(os.path.join(basedir,outfile), elemdat, fmt='%.8f')
    np.savetxt(basedir+'/pre_simulation/'+outfile, elemdat, fmt='%.8f') 

    print('DONE')

    # cmd = 'GlVTKConvert -m '+basename+' -e '+os.path.join(basedir, outfile)+' -e '+os.path.join(basedir, '/UVC_elem.dat')+' -F bin -o '+basename+'_elem_dat_UVC'+' --trim-names'
    # os.system(str(cmd))

    cmd = 'GlVTKConvert -m '+basename+' -e '+basedir+'/pre_simulation/'+outfile+' -e '+basedir+'/pre_simulation/UVC_elem.dat'+' -F bin -o '+basename+'_elem_dat_UVC'+' --trim-names'
    os.system(str(cmd))

if __name__ == '__main__':
    main()
