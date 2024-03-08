#import nibabel as nib
#import os
#import numpy as np
import nibabel as nib
#import sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load in 4D nifti image and change to a list of 3D images')

    parser.add_argument('niifile', help='4D cine nifti image')
    parser.add_argument('outdir', help='output directory for 3D images and imgTimes.lst file')
    parser.add_argument('-skipTime', type=int, default=1, help='output every nth time point [1]')
    args = parser.parse_args()    
        
    nii = nib.load(args.niifile)

    #outdir='/home/ale12/Dropbox/Work/Atria/VC/data/case001/2_motion/'

    imgs=nib.funcs.four_to_three(nii)
    f = open(args.outdir+'imgTimes.lst', 'w')
    f.write('dcm- .nii\n')
    j=0; 
    for i in range(0,len(imgs),args.skipTime):
        filename=args.outdir+'dcm-'+str(j)+'.nii'
        nib.loadsave.save(imgs[i], filename)
        f.write(str(j)+' '+str(j)+'\n')
        j+=1
    f.close()
    

