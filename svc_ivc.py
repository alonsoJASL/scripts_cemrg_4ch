from img import add_masks
from img import add_masks_replace
from img import add_masks_replace_only
from img import save_itk
import SimpleITK as sitk

import numpy as np
import nrrd
import pylab

seg_corrected_nrrd = '/data/Dropbox/henry/segmentations/seg_corrected.nrrd'

svc_nrrd = '/data/Dropbox/henry/segmentations/SVC.nrrd'
svc_label = 13

ivc_nrrd = '/data/Dropbox/henry/segmentations/IVC.nrrd'
ivc_label = 14

aorta_bp_label = 6
PArt_bp_label = 7

aorta_slicer_nrrd = '/data/Dropbox/henry/segmentations/aorta_slicer.nrrd'
aorta_slicer_label = 0

PArt_slicer_nrrd = '/data/Dropbox/henry/segmentations/PArt_slicer.nrrd'
PArt_slicer_label = 0

seg_corrected_array, header1 = nrrd.read(seg_corrected_nrrd)
svc_array, header2 = nrrd.read(svc_nrrd)
ivc_array, header3 = nrrd.read(ivc_nrrd)
aorta_slicer_array, header4 = nrrd.read(aorta_slicer_nrrd)
PArt_slicer_array, header5 = nrrd.read(PArt_slicer_nrrd)

original_origin = header1['axis mins']
original_spacings = header1['spacings']

new_origin = [original_origin[0], original_origin[1], original_origin[2]]
new_spacings = [original_spacings[0], original_spacings[1], original_spacings[2]]

print(new_spacings)

# seg = add_masks(seg_corrected_array, svc_array, svc_label)
# seg = add_masks(seg, ivc_array, ivc_label)
# # seg = add_masks_replace(seg, aorta_slicer_array, aorta_slicer_label)
# # seg = add_masks_replace(seg, PArt_slicer_array, PArt_slicer_label)
# seg = add_masks_replace_only(seg, aorta_slicer_array, aorta_slicer_label, aorta_bp_label)
# seg = add_masks_replace_only(seg, PArt_slicer_array, PArt_slicer_label, PArt_bp_label)

# seg_corrected_svc_ivc_aorta_PArt = np.swapaxes(seg,0,2)

# save_itk(seg_corrected_svc_ivc_aorta_PArt, new_origin, new_spacings, '/data/Dropbox/henry/segmentations/seg_s2.nrrd')

# print("Saved segmentation with SVC/IVC added and aorta/pulmonary artery cropped")