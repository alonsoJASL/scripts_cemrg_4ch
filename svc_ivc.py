from img import add_masks
from img import save_itk
import SimpleITK as sitk

import numpy as np
import nrrd
import pylab

seg_corrected_nrrd = '/data/Dropbox/henry/segmentations/seg_corrected.nrrd'

svc_nrrd = '/data/Dropbox/henry/segmentations/SVC.nrrd'
svc_label = '13'

ivc_nrrd = '/data/Dropbox/henry/segmentations/IVC.nrrd'
ivc_label = '14'

seg_corrected_array, header1 = nrrd.read(seg_corrected_nrrd)
svc_array, header2 = nrrd.read(svc_nrrd)
ivc_array, header3 = nrrd.read(ivc_nrrd)

original_origin = header1['axis mins']
original_spacings = header1['spacings']

print(original_origin)
print(original_spacings)

new_origin = [original_origin[0], original_origin[1], original_origin[2]]
new_spacings = [original_spacings[0], original_spacings[1], original_spacings[2]]

print(new_origin)
print(new_spacings)

seg_corrected_svc = add_masks(seg_corrected_array, svc_array, svc_label)
seg_corrected_svc_ivc = add_masks(seg_corrected_svc, ivc_array, ivc_label)

seg_corrected_svc_ivc = np.swapaxes(seg_corrected_svc_ivc,0,2)
print(seg_corrected_svc_ivc.shape)

save_itk(seg_corrected_svc_ivc, new_origin, new_spacings, '/data/Dropbox/henry/segmentations/seg_svc_ivc.nrrd')

