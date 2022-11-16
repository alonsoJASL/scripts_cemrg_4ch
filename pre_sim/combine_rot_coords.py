# combine rotational coordinates

import numpy as np

def combine_elem_file(input_elemFiles,
					  output_file,
					  mode='max'):
	
	print('Reading files...')
	elemData = np.loadtxt(input_elemFiles[0],dtype=float)
	for i in range(1,len(input_elemFiles)):
		tmp = np.loadtxt(input_elemFiles[i],dtype=float)
		elemData = np.column_stack((elemData,tmp))
	print('Done.')

	if mode=='max':
		elemData_new = np.max(elemData,axis=1)
	else:
		raise Exception('Mode not recognised')

	print('Writing output...')
	np.savetxt(output_file,elemData_new)

combine_elem_file(["/data/Dropbox/Segmentations/2016111001EP/final_heart/elem_dat_UVC_ek.dat", 
				  "/data/Dropbox/Segmentations/2016111001EP/final_heart/elem_dat_UVC_ek_inc_la.dat",
				  "/data/Dropbox/Segmentations/2016111001EP/final_heart/elem_dat_UVC_ek_inc_ra.dat"], 
				  "/data/Dropbox/Segmentations/2016111001EP/final_heart/elem_dat_UVC_ek_combined.dat")