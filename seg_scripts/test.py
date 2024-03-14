import os
from seg_scripts import ImageAnalysis
import seg_scripts.Labels as Labels

C = Labels.Labels()
path2points = '/home/alexander/Downloads'
filename = os.path.join(path2points, 'points.txt')
debug = False

ima = ImageAnalysis(path2points, debug)

seg_array = ima.load_image_array(filename)

# == 2/8
# s4a
# print('\n ## Step 2/8: Creating the mitral valve ## \n')
# LA_BP_DistMap = distance_map(path2points+'seg_s3s.nrrd',LA_BP_label)
# LA_BP_thresh = threshold_filter_nrrd(path2points+'/tmp/LA_BP_DistMap.nrrd',0,valve_WT)

# MV_array, header = nrrd.read(path2points+'/tmp/LA_BP_thresh.nrrd')
# seg_s3s_array, header = nrrd.read(path2points+'seg_s3s.nrrd')
# MV_array = and_filter(seg_s3s_array,MV_array,LV_BP_label,MV_label)
# seg_s4a_array = add_masks_replace(seg_s3s_array,MV_array,MV_label)

# seg_s4a_array = np.swapaxes(seg_s4a_array,0,2)
# save_itk(seg_s4a_array, origin, spacings, path2points+'/seg_s4a.nrrd')
# print(" ## MV: Saved segmentation with mitral valve added ## \n")
la_bp_distmap = ima.distance_map(seg_array, C.LA_BP_label, "LA_BP")
la_bp_thresh = ima.threshold_filter_array(la_bp_distmap, 0, C.valve_WT, "LA_BP")

mv_array = ima.and_filter(seg_array, la_bp_thresh, C.LV_BP_label, C.MV_label)
seg_new_array = ima.add_masks_replace(seg_array, mv_array, C.MV_label)

# if debug:
#     ima.save_itk(seg_new_array, origin, spacing, "seg_s4a.nrrd", self.swap_axes)

#== 
# s4b
# LV_myo_DistMap = distance_map(path2points+'seg_s4a.nrrd',LV_myo_label)
# sitk.WriteImage(LV_myo_DistMap,path2points+'/tmp/LV_myo_DistMap.nrrd',True)

# LA_myo_extra = threshold_filter_nrrd(path2points+'/tmp/LV_myo_DistMap.nrrd',0,LA_WT)
# sitk.WriteImage(LA_myo_extra,path2points+'/tmp/LA_myo_extra.nrrd',True)

# LA_myo_extra_array, header = nrrd.read(path2points+'/tmp/LA_myo_extra.nrrd')
# seg_s4a_array, header = nrrd.read(path2points+'/seg_s4a.nrrd')
# LA_myo_extra_array = and_filter(seg_s4a_array,LA_myo_extra_array,LA_BP_label,LA_myo_label)
# seg_s4b_array = add_masks_replace(seg_s4a_array,LA_myo_extra_array,LA_myo_label)

# seg_s4b_array = np.swapaxes(seg_s4b_array,0,2)
# save_itk(seg_s4b_array, origin, spacings, path2points+'/seg_s4b.nrrd')
# print(" ## MV extra: Saved segmentation with holes closed around mitral valve ## \n")
lv_myo_distmap = ima.distance_map(seg_new_array, C.LV_myo_label, "LV_myo")
lv_myo_thresh = ima.threshold_filter_array(lv_myo_distmap, 0, C.LA_WT, "LV_myo")

la_myo_extra_array = ima.and_filter(seg_new_array, lv_myo_thresh, C.LA_BP_label, C.LA_myo_label)
seg_new_array = ima.add_masks_replace(seg_new_array, la_myo_extra_array, C.LA_myo_label)

# if debug:
#     ima.save_itk(seg_new_array, origin, spacing, "seg_s4b.nrrd", self.swap_axes)

#== 3/8 
# s4c 
# print('\n ## Step 3/8: Creating the tricuspid valve ## \n')
# RA_BP_DistMap = distance_map(path2points+'/seg_s4b.nrrd',RA_BP_label)
# sitk.WriteImage(RA_BP_DistMap,path2points+'/tmp/RA_BP_DistMap.nrrd',True)

# RA_BP_thresh = threshold_filter_nrrd(path2points+'/tmp/RA_BP_DistMap.nrrd',0,valve_WT)
# sitk.WriteImage(RA_BP_thresh,path2points+'/tmp/RA_BP_thresh.nrrd',True)

# TV_array, header = nrrd.read(path2points+'/tmp/RA_BP_thresh.nrrd')
# seg_s4b_array, header = nrrd.read(path2points+'/seg_s4b.nrrd')
# TV_array = and_filter(seg_s4b_array,TV_array,RV_BP_label,TV_label)
# seg_s4c_array = add_masks_replace(seg_s4b_array,TV_array,TV_label)

# seg_s4c_array = np.swapaxes(seg_s4c_array,0,2)
# save_itk(seg_s4c_array, origin, spacings, path2points+'/seg_s4c.nrrd')
# print(" ## TV: Saved segmentation with tricuspid valve added ## \n")
ra_bp_distmap = ima.distance_map(seg_new_array, C.RA_BP_label, "RA_BP")
ra_bp_thresh = ima.threshold_filter_array(ra_bp_distmap, 0, C.valve_WT, "RA_BP")

tv_array = ima.and_filter(seg_new_array, ra_bp_thresh, C.RV_BP_label, C.TV_label)
seg_new_array = ima.add_masks_replace(seg_new_array, tv_array, C.TV_label)

# if debug:
#     ima.save_itk(seg_new_array, origin, spacing, "seg_s4c.nrrd", self.swap_axes)

# s4d
# RV_myo_DistMap = distance_map(path2points+'/seg_s4c.nrrd',RV_myo_label)
# sitk.WriteImage(RV_myo_DistMap,path2points+'/tmp/RV_myo_DistMap.nrrd',True)

# RA_myo_extra = threshold_filter_nrrd(path2points+'/tmp/RV_myo_DistMap.nrrd',0,RA_WT)
# sitk.WriteImage(RA_myo_extra,path2points+'/tmp/RA_myo_extra.nrrd',True)

# RA_myo_extra_array, header = nrrd.read(path2points+'/tmp/RA_myo_extra.nrrd')
# seg_s4c_array, header = nrrd.read(path2points+'/seg_s4c.nrrd')
# RA_myo_extra_array = and_filter(seg_s4c_array,RA_myo_extra_array,RA_BP_label,RA_myo_label)
# seg_s4d_array = add_masks_replace(seg_s4c_array,RA_myo_extra_array,RA_myo_label)

# seg_s4d_array = np.swapaxes(seg_s4d_array,0,2)
# save_itk(seg_s4d_array, origin, spacings, path2points+'/seg_s4d.nrrd')
# print(" ## TV corrections: Saved segmentation with holes closed around tricuspid valve ## \n")
rv_myo_distmap = ima.distance_map(seg_new_array, C.RV_myo_label, "RV_myo")
rv_myo_thresh = ima.threshold_filter_array(rv_myo_distmap, 0, C.RA_WT, "RV_myo")

ra_myo_extra_array = ima.and_filter(seg_new_array, rv_myo_thresh, C.RA_BP_label, C.RA_myo_label)
seg_new_array = ima.add_masks_replace(seg_new_array, ra_myo_extra_array, C.RA_myo_label)

# if debug:
#     ima.save_itk(seg_new_array, origin, spacing, "seg_s4d.nrrd", self.swap_axes)

#== 4/8
# s4e
# print('\n ## Step 4/8: Creating the aortic valve ## \n')
# Ao_BP_DistMap = distance_map(path2points+'/seg_s4d.nrrd',Ao_BP_label)
# sitk.WriteImage(Ao_BP_DistMap,path2points+'/tmp/Ao_BP_DistMap.nrrd',True)

# AV = threshold_filter_nrrd(path2points+'/tmp/Ao_BP_DistMap.nrrd',0,valve_WT)
# sitk.WriteImage(AV,path2points+'/tmp/AV.nrrd',True)

# AV_array, header = nrrd.read(path2points+'/tmp/AV.nrrd')
# seg_s4d_array, header = nrrd.read(path2points+'/seg_s4d.nrrd')
# AV_array = and_filter(seg_s4d_array,AV_array,LV_BP_label,AV_label)
# seg_s4e_array = add_masks_replace(seg_s4d_array,AV_array,AV_label)

# seg_s4e_array = np.swapaxes(seg_s4e_array,0,2)
# save_itk(seg_s4e_array, origin, spacings, path2points+'/seg_s4e.nrrd')
# print(" ## AV: Saved segmentation with aortic valve added ## \n")
ao_bp_distmap = ima.distance_map(seg_new_array, C.Ao_BP_label, "Ao_BP")
av_thresh = ima.threshold_filter_array(ao_bp_distmap, 0, C.valve_WT, "AV")

av_array = ima.and_filter(seg_new_array, av_thresh, C.LV_BP_label, C.AV_label)
seg_new_array = ima.add_masks_replace(seg_new_array, av_array, C.AV_label)

# if debug:
#     ima.save_itk(seg_new_array, origin, spacing, "seg_s4e.nrrd", self.swap_axes)

# s4f
# Ao_wall_extra = threshold_filter_nrrd(path2points+'/tmp/LV_myo_DistMap.nrrd',0,Ao_WT)
# sitk.WriteImage(Ao_wall_extra,path2points+'/tmp/Ao_wall_extra.nrrd',True)

# Ao_wall_extra_array, header = nrrd.read(path2points+'/tmp/Ao_wall_extra.nrrd')
# seg_s4e_array, header = nrrd.read(path2points+'/seg_s4e.nrrd')
# Ao_wall_extra_array = and_filter(seg_s4e_array,Ao_wall_extra_array,Ao_BP_label,Ao_wall_label)
# seg_s4f_array = add_masks_replace(seg_s4e_array,Ao_wall_extra_array,Ao_wall_label)

# seg_s4f_array = np.swapaxes(seg_s4f_array,0,2)
# save_itk(seg_s4f_array, origin, spacings, path2points+'/seg_s4f.nrrd')
# print(" ## AV corrections: Saved segmentation with holes closed around aortic valve ## \n")
ao_wall_extra = ima.threshold_filter_array(lv_myo_distmap, 0, C.Ao_WT, "Ao_wall")

ao_wall_extra_array = ima.and_filter(seg_new_array, ao_wall_extra, C.Ao_BP_label, C.Ao_wall_label)
seg_new_array = ima.add_masks_replace(seg_new_array, ao_wall_extra_array, C.Ao_wall_label)

# if debug:
#     ima.save_itk(seg_new_array, origin, spacing, "seg_s4f.nrrd", self.swap_axes)

# s4f - still 
# print('\n ## AV corrections: Separating MV and AV ## \n')
# AV_DistMap = distance_map(path2points+'/seg_s4f.nrrd',AV_label)
# sitk.WriteImage(AV_DistMap,path2points+'/tmp/AV_DistMap.nrrd',True)

# AV_sep = threshold_filter_nrrd(path2points+'/tmp/AV_DistMap.nrrd',0,2*valve_WT)
# sitk.WriteImage(AV_sep,path2points+'/tmp/AV_sep.nrrd',True)

# AV_sep_array, header = nrrd.read(path2points+'/tmp/AV_sep.nrrd')
# seg_s4f_array, header = nrrd.read(path2points+'/seg_s4f.nrrd')
# AV_sep_array = and_filter(seg_s4f_array,AV_sep_array,MV_label,LV_myo_label)
# seg_s4f_array = add_masks_replace(seg_s4f_array,AV_sep_array,LV_myo_label)

# seg_s4f_array = np.swapaxes(seg_s4f_array,0,2)
# save_itk(seg_s4f_array, origin, spacings, path2points+'/seg_s4f.nrrd')
# print(" ## AV: Saved segmentation with AV and MV separated ## \n")
av_distmap = ima.distance_map(seg_new_array, C.AV_label, "AV")
av_sep = ima.threshold_filter_array(av_distmap, 0, 2*C.valve_WT, "AV_sep")

av_sep_array = ima.and_filter(seg_new_array, av_sep, C.MV_label, C.LV_myo_label)
seg_new_array = ima.add_masks_replace(seg_new_array, av_sep_array, C.LV_myo_label)

# if debug:
#     ima.save_itk(seg_new_array, origin, spacing, "seg_s4f.nrrd", self.swap_axes)

# s4ff 
# LV_myo_DistMap = distance_map(path2points+'seg_s4f.nrrd',LV_myo_label)
# sitk.WriteImage(LV_myo_DistMap,path2points+'/tmp/LV_myo_DistMap.nrrd',True)

# LA_myo_extra = threshold_filter_nrrd(path2points+'/tmp/LV_myo_DistMap.nrrd',0,LA_WT)
# sitk.WriteImage(LA_myo_extra,path2points+'/tmp/LA_myo_extra.nrrd',True)

# LA_myo_extra_array, header = nrrd.read(path2points+'/tmp/LA_myo_extra.nrrd')
# seg_s4ff_array, header = nrrd.read(path2points+'/seg_s4f.nrrd')
# LA_myo_extra_array = and_filter(seg_s4ff_array,LA_myo_extra_array,LA_BP_label,LA_myo_label)
# seg_s4ff_array = add_masks_replace(seg_s4ff_array,LA_myo_extra_array,LA_myo_label)

# seg_s4ff_array = np.swapaxes(seg_s4ff_array,0,2)
# save_itk(seg_s4ff_array, origin, spacings, path2points+'/seg_s4ff.nrrd')
# print(" ## MV extra: Saved segmentation with holes closed around mitral valve ## \n")
lv_myo_distmap = ima.distance_map(seg_new_array, C.LV_myo_label, "LV_myo")
la_myo_extra = ima.threshold_filter_array(lv_myo_distmap, 0, C.LA_WT, "LV_myo_extra")

la_myo_extra_array = ima.and_filter(seg_new_array, la_myo_extra, C.LA_BP_label, C.LA_myo_label)
seg_new_array = ima.add_masks_replace(seg_new_array, la_myo_extra_array, C.LA_myo_label)

# if debug:
#     ima.save_itk(seg_new_array, origin, spacing, "seg_s4ff.nrrd", self.swap_axes)

#== 5/8
# s4g
# print('\n ## Step 5/8: Creating the pulmonary valve ## \n')
# PArt_BP_DistMap = distance_map(path2points+'/seg_s4ff.nrrd',PArt_BP_label)
# sitk.WriteImage(PArt_BP_DistMap,path2points+'/tmp/PArt_BP_DistMap.nrrd',True)

# PV = threshold_filter_nrrd(path2points+'/tmp/PArt_BP_DistMap.nrrd',0,valve_WT)
# sitk.WriteImage(PV,path2points+'/tmp/PV.nrrd',True)

# PV_array, header = nrrd.read(path2points+'/tmp/PV.nrrd')
# seg_s4ff_array, header = nrrd.read(path2points+'/seg_s4ff.nrrd')
# PV_array = and_filter(seg_s4ff_array,PV_array,RV_BP_label,PV_label)
# seg_s4g_array = add_masks_replace(seg_s4ff_array,PV_array,PV_label)

# seg_s4g_array = np.swapaxes(seg_s4g_array,0,2)
# save_itk(seg_s4g_array, origin, spacings, path2points+'/seg_s4g.nrrd')
# print(" ## PV: Saved segmentation with pulmonary valve added ## \n")
part_bp_distmap = ima.distance_map(seg_new_array, C.PArt_BP_label, "PArt_BP")
pv = ima.threshold_filter_array(part_bp_distmap, 0, C.valve_WT, "PV")

pv_array = ima.and_filter(seg_new_array, pv, C.RV_BP_label, C.PV_label)
seg_new_array = ima.add_masks_replace(seg_new_array, pv_array, C.PV_label)

# if debug:
#     ima.save_itk(seg_new_array, origin, spacing, "seg_s4g.nrrd", self.swap_axes)

# s4h
# PArt_wall_extra = threshold_filter_nrrd(path2points+'/tmp/RV_myo_DistMap.nrrd',0,PArt_WT)
# sitk.WriteImage(PArt_wall_extra,path2points+'/tmp/PArt_wall_extra.nrrd',True)

# PArt_wall_extra_array, header = nrrd.read(path2points+'/tmp/PArt_wall_extra.nrrd')
# seg_s4g_array, header = nrrd.read(path2points+'/seg_s4g.nrrd')
# PArt_wall_extra_array = and_filter(seg_s4g_array,PArt_wall_extra_array,PArt_BP_label,PArt_wall_label)
# seg_s4h_array = add_masks_replace(seg_s4g_array,PArt_wall_extra_array,PArt_wall_label)

# seg_s4h_array = np.swapaxes(seg_s4h_array,0,2)
# save_itk(seg_s4h_array, origin, spacings, path2points+'/seg_s4h.nrrd')
# print(" ## PV corrections: Saved segmentation with holes closed around pulmonary valve ## \n")
part_wall_extra = ima.threshold_filter_array(rv_myo_distmap, 0, C.PArt_WT, "PArt_wall")
part_wall_extra_array = ima.and_filter(seg_new_array, part_wall_extra, C.PArt_BP_label, C.PArt_wall_label)
seg_new_array = ima.add_masks_replace(seg_new_array, part_wall_extra_array, C.PArt_wall_label)

# if debug:
#     ima.save_itk(seg_new_array, origin, spacing, "seg_s4h.nrrd", self.swap_axes)

#== 6/8
# distance maps 
# print('\n ## Step 6/8: Create the distance maps needed to cut the vein rings ## \n')
# print(' ## Create the distance maps needed to cut the vein rings: Executing distance map ## \n')
# LA_myo_DistMap = distance_map(path2points+'/seg_s4h.nrrd',LA_myo_label)
# RA_myo_DistMap = distance_map(path2points+'/seg_s4h.nrrd',RA_myo_label)
# print(' ## Create the distance maps needed to cut the vein rings: Writing temporary image ## \n')
# sitk.WriteImage(LA_myo_DistMap,path2points+'/tmp/LA_myo_DistMap.nrrd',True)
# sitk.WriteImage(RA_myo_DistMap,path2points+'/tmp/RA_myo_DistMap.nrrd',True)

# print(' ## Cutting vein rings: Thresholding distance filter ## \n')
# LA_myo_thresh = threshold_filter_nrrd(path2points+'/tmp/LA_myo_DistMap.nrrd',0,ring_thickness)
# RA_myo_thresh = threshold_filter_nrrd(path2points+'/tmp/RA_myo_DistMap.nrrd',0,ring_thickness)
# sitk.WriteImage(LA_myo_thresh,path2points+'/tmp/LA_myo_thresh.nrrd',True)
# sitk.WriteImage(RA_myo_thresh,path2points+'/tmp/RA_myo_thresh.nrrd',True)

# LA_myo_thresh_array, header = nrrd.read(path2points+'/tmp/LA_myo_thresh.nrrd')
# RA_myo_thresh_array, header = nrrd.read(path2points+'/tmp/RA_myo_thresh.nrrd')
la_myo_distmap = ima.distance_map(seg_new_array, C.LA_myo_label, "LA_myo")
la_myo_thresh_array = ima.threshold_filter_array(la_myo_distmap, 0, C.ring_thickness, "LA_myo")

ra_myo_distmap = ima.distance_map(seg_new_array, C.RA_myo_label, "RA_myo")
ra_myo_thresh_array = ima.threshold_filter_array(ra_myo_distmap, 0, C.ring_thickness, "RA_myo")

#== 7/8
# print('\n ## Step 7/8: Creating the vein rings ## \n')
# print(' ## LPVeins1: Executing distance map ## \n')
# LPV1_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',LPV1_label)
# print(' ## LPVeins1: Writing temporary image ## \n')
# sitk.WriteImage(LPV1_BP_DistMap,path2points+'/tmp/LPV1_BP_DistMap.nrrd',True)

# print(' ## LPVeins1: Thresholding distance filter ## \n')
# LPV1_ring = threshold_filter_nrrd(path2points+'/tmp/LPV1_BP_DistMap.nrrd',0,ring_thickness)
# sitk.WriteImage(LPV1_ring,path2points+'/tmp/LPV1_ring.nrrd',True)

# print(' ## LPVeins1: Add the ring to the segmentation ## \n')
# LPV1_ring_array, header = nrrd.read(path2points+'/tmp/LPV1_ring.nrrd')
# seg_s4h_array, header = nrrd.read(path2points+'/seg_s4h.nrrd')
# seg_s4i_array = add_masks(seg_s4h_array,LPV1_ring_array,LPV1_ring_label)

# LPV1_ring_array = and_filter(seg_s4i_array,LA_myo_thresh_array,LPV1_ring_label,LPV1_ring_label)
# seg_s4j_array = add_masks_replace(seg_s4h_array,LPV1_ring_array,LPV1_ring_label)
lpv1_bp_distmap = ima.distance_map(seg_new_array, C.LPV1_label, "LPV1_BP")
lpv1_ring = ima.threshold_filter_array(lpv1_bp_distmap, 0, C.ring_thickness, "LPV1_ring")

seg_new_array = ima.add_masks(seg_new_array, lpv1_ring, C.LPV1_ring_label) # seg_s4i_array
lpv1_ring_array = ima.and_filter(seg_new_array, la_myo_thresh_array, C.LPV1_ring_label, C.LPV1_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, lpv1_ring_array, C.LPV1_ring_label) # seg_s4j_array

# print('\n ## Creating the vein rings ## \n')
# print(' ## LPVeins2: Executing distance map ## \n')
# LPV2_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',LPV2_label)
# print(' ## LPVeins2: Writing temporary image ## \n')
# sitk.WriteImage(LPV2_BP_DistMap,path2points+'/tmp/LPV2_BP_DistMap.nrrd',True)

# print(' ## LPVeins2: Thresholding distance filter ## \n')
# LPV2_ring = threshold_filter_nrrd(path2points+'/tmp/LPV2_BP_DistMap.nrrd',0,ring_thickness)
# sitk.WriteImage(LPV2_ring,path2points+'/tmp/LPV2_ring.nrrd',True)

# print(' ## LPVeins2: Add the ring to the segmentation ## \n')
# LPV2_ring_array, header = nrrd.read(path2points+'/tmp/LPV2_ring.nrrd')
# seg_s4i_array = add_masks(seg_s4i_array,LPV2_ring_array,LPV2_ring_label)

# LPV2_ring_array = and_filter(seg_s4i_array,LA_myo_thresh_array,LPV2_ring_label,LPV2_ring_label)
# seg_s4j_array = add_masks_replace(seg_s4j_array,LPV2_ring_array,LPV2_ring_label)
lpv2_bp_distmap = ima.distance_map(seg_new_array, C.LPV2_label, "LPV2_BP")
lpv2_ring = ima.threshold_filter_array(lpv2_bp_distmap, 0, C.ring_thickness, "LPV2_ring")

seg_new_array = ima.add_masks(seg_new_array, lpv2_ring, C.LPV2_ring_label) # seg_s4i_array
lpv2_ring_array = ima.and_filter(seg_new_array, la_myo_thresh_array, C.LPV2_ring_label, C.LPV2_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, lpv2_ring_array, C.LPV2_ring_label) # seg_s4j_array

# print('\n ## Creating the vein rings ## \n')
# print(' ## RPVeins1: Executing distance map ## \n')
# RPV1_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',RPV1_label)
# print(' ## RPVeins1: Writing temporary image ## \n')
# sitk.WriteImage(RPV1_BP_DistMap,path2points+'/tmp/RPV1_BP_DistMap.nrrd',True)

# print(' ## RPVeins1: Thresholding distance filter ## \n')
# RPV1_ring = threshold_filter_nrrd(path2points+'/tmp/RPV1_BP_DistMap.nrrd',0,ring_thickness)
# sitk.WriteImage(RPV1_ring,path2points+'/tmp/RPV1_ring.nrrd',True)

# print(' ## RPVeins1: Add the ring to the segmentation ## \n')
# RPV1_ring_array, header = nrrd.read(path2points+'/tmp/RPV1_ring.nrrd')
# seg_s4i_array = add_masks_replace_only(seg_s4i_array,RPV1_ring_array,RPV1_ring_label,SVC_label)

# RPV1_ring_array = and_filter(seg_s4i_array,LA_myo_thresh_array,RPV1_ring_label,RPV1_ring_label)
# seg_s4j_array = add_masks_replace(seg_s4j_array,RPV1_ring_array,RPV1_ring_label)
rpv1_bp_distmap = ima.distance_map(seg_new_array, C.RPV1_label, "RPV1_BP")
rpv1_ring = ima.threshold_filter_array(rpv1_bp_distmap, 0, C.ring_thickness, "RPV1_ring")

seg_new_array = ima.add_masks_replace_only(seg_new_array, rpv1_ring, C.RPV1_ring_label, C.SVC_label) # seg_s4i_array
rpv1_ring_array = ima.and_filter(seg_new_array, la_myo_thresh_array, C.RPV1_ring_label, C.RPV1_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, rpv1_ring_array, C.RPV1_ring_label) # seg_s4j_array

# print('\n ## Creating the vein rings ## \n')
# print(' ## RPVeins2: Executing distance map ## \n')
# RPV2_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',RPV2_label)
# print(' ## RPVeins2: Writing temporary image ## \n')
# sitk.WriteImage(RPV2_BP_DistMap,path2points+'/tmp/RPV2_BP_DistMap.nrrd',True)

# print(' ## RPVeins2: Thresholding distance filter ## \n')
# RPV2_ring = threshold_filter_nrrd(path2points+'/tmp/RPV2_BP_DistMap.nrrd',0,ring_thickness)
# sitk.WriteImage(RPV2_ring,path2points+'/tmp/RPV2_ring.nrrd',True)

# print(' ## RPVeins2: Add the ring to the segmentation ## \n')
# RPV2_ring_array, header = nrrd.read(path2points+'/tmp/RPV2_ring.nrrd')
# seg_s4i_array = add_masks(seg_s4i_array,RPV2_ring_array,RPV2_ring_label)

# RPV2_ring_array = and_filter(seg_s4i_array,LA_myo_thresh_array,RPV2_ring_label,RPV2_ring_label)
# seg_s4j_array = add_masks_replace(seg_s4j_array,RPV2_ring_array,RPV2_ring_label)
rpv2_bp_distmap = ima.distance_map(seg_new_array, C.RPV2_label, "RPV2_BP")
rpv2_ring = ima.threshold_filter_array(rpv2_bp_distmap, 0, C.ring_thickness, "RPV2_ring")

seg_new_array = ima.add_masks(seg_new_array, rpv2_ring, C.RPV2_ring_label) # seg_s4i_array
rpv2_ring_array = ima.and_filter(seg_new_array, la_myo_thresh_array, C.RPV2_ring_label, C.RPV2_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, rpv2_ring_array, C.RPV2_ring_label) # seg_s4j_array

# print('\n ## Creating the vein rings ## \n')
# print(' ## LAA: Executing distance map ## \n')
# LAA_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',LAA_label)
# print(' ## LAA: Writing temporary image ## \n')
# sitk.WriteImage(LAA_BP_DistMap,path2points+'/tmp/LAA_BP_DistMap.nrrd',True)

# print(' ## LAA: Thresholding distance filter ## \n')
# LAA_ring = threshold_filter_nrrd(path2points+'/tmp/LAA_BP_DistMap.nrrd',0,ring_thickness)
# sitk.WriteImage(LAA_ring,path2points+'/tmp/LAA_ring.nrrd',True)

# print(' ## LAA: Add the ring to the segmentation ## \n')
# LAA_ring_array, header = nrrd.read(path2points+'/tmp/LAA_ring.nrrd')
# seg_s4i_array = add_masks(seg_s4i_array,LAA_ring_array,LAA_ring_label)

# LAA_ring_array = and_filter(seg_s4i_array,LA_myo_thresh_array,LAA_ring_label,LAA_ring_label)
# seg_s4j_array = add_masks_replace(seg_s4j_array,LAA_ring_array,LAA_ring_label)
laa_bp_distmap = ima.distance_map(seg_new_array, C.LAA_label, "LAA_BP")
laa_ring = ima.threshold_filter_array(laa_bp_distmap, 0, C.ring_thickness, "LAA_ring")

seg_new_array = ima.add_masks(seg_new_array, laa_ring, C.LAA_ring_label) # seg_s4i_array
laa_ring_array = ima.and_filter(seg_new_array, la_myo_thresh_array, C.LAA_ring_label, C.LAA_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, laa_ring_array, C.LAA_ring_label) # seg_s4j_array

# print('\n ## Creating the vein rings ## \n')
# print(' ## SVC: Executing distance map ## \n')
# SVC_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',SVC_label)
# print(' ## SVC: Writing temporary image ## \n')
# sitk.WriteImage(SVC_BP_DistMap,path2points+'/tmp/SVC_BP_DistMap.nrrd',True)

# print(' ## SVC: Thresholding distance filter ## \n')
# SVC_ring = threshold_filter_nrrd(path2points+'/tmp/SVC_BP_DistMap.nrrd',0,ring_thickness)
# sitk.WriteImage(SVC_ring,path2points+'/tmp/SVC_ring.nrrd',True)

# print(' ## SVC: Add the ring to the segmentation ## \n')
# SVC_ring_array, header = nrrd.read(path2points+'/tmp/SVC_ring.nrrd')
# seg_s4i_array = add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,Ao_wall_label)
# seg_s4i_array = add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,LA_myo_label)
# seg_s4i_array = add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,RPV1_ring_label)
# seg_s4i_array = add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,RPV1_label)
# seg_s4i_array = add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,RPV2_ring_label)
# seg_s4i_array = add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,RPV2_label)

# SVC_ring_array = and_filter(seg_s4i_array,RA_myo_thresh_array,SVC_ring_label,SVC_ring_label)
# seg_s4j_array = add_masks_replace(seg_s4j_array,SVC_ring_array,SVC_ring_label)
svc_bp_distmap = ima.distance_map(seg_new_array, C.SVC_label, "SVC_BP")
svc_ring = ima.threshold_filter_array(svc_bp_distmap, 0, C.ring_thickness, "SVC_ring")

seg_new_array = ima.add_masks_replace_only(seg_new_array, svc_ring, C.SVC_ring_label, C.Ao_wall_label) # seg_s4i_array
seg_new_array = ima.add_masks_replace_only(seg_new_array, svc_ring, C.SVC_ring_label, C.LA_myo_label) # seg_s4i_array
seg_new_array = ima.add_masks_replace_only(seg_new_array, svc_ring, C.SVC_ring_label, C.RPV1_ring_label) # seg_s4i_array
seg_new_array = ima.add_masks_replace_only(seg_new_array, svc_ring, C.SVC_ring_label, C.RPV1_label) # seg_s4i_array
seg_new_array = ima.add_masks_replace_only(seg_new_array, svc_ring, C.SVC_ring_label, C.RPV2_ring_label) # seg_s4i_array
seg_new_array = ima.add_masks_replace_only(seg_new_array, svc_ring, C.SVC_ring_label, C.RPV2_label) # seg_s4i_array

svc_ring_array = ima.and_filter(seg_new_array, ra_myo_thresh_array, C.SVC_ring_label, C.SVC_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, svc_ring_array, C.SVC_ring_label) # seg_s4j_array

# print('\n ## Creating the vein rings ## \n')
# print(' ## IVC: Executing distance map ## \n')
# IVC_BP_DistMap = distance_map(path2points+'/seg_s4h.nrrd',IVC_label)
# print(' ## IVC: Writing temporary image ## \n')
# sitk.WriteImage(IVC_BP_DistMap,path2points+'/tmp/IVC_BP_DistMap.nrrd',True)

# print(' ## IVC: Thresholding distance filter ## \n')
# IVC_ring = threshold_filter_nrrd(path2points+'/tmp/IVC_BP_DistMap.nrrd',0,ring_thickness)
# sitk.WriteImage(IVC_ring,path2points+'/tmp/IVC_ring.nrrd',True)

# print(' ## IVC: Add the ring to the segmentation ## \n')
# IVC_ring_array, header = nrrd.read(path2points+'/tmp/IVC_ring.nrrd')
# seg_s4i_array = add_masks(seg_s4i_array,IVC_ring_array,IVC_ring_label)

# IVC_ring_array = and_filter(seg_s4i_array,RA_myo_thresh_array,IVC_ring_label,IVC_ring_label)
# seg_s4j_array = add_masks_replace(seg_s4j_array,IVC_ring_array,IVC_ring_label)

# print(' ## Vein rings: Formatting and saving the segmentation ## \n')
# seg_s4i_array = np.swapaxes(seg_s4i_array,0,2)
# save_itk(seg_s4i_array, origin, spacings, path2points+'/seg_s4i.nrrd')
# print(" ## Vein rings: Saved segmentation with veins rings added ## \n")

# print(' ## Cutting vein rings: Formatting and saving the segmentation ## \n')
# seg_s4j_array = np.swapaxes(seg_s4j_array,0,2)
# save_itk(seg_s4j_array, origin, spacings, path2points+'/seg_s4j.nrrd')
# print(" ## Cutting vein rings: Saved segmentation with veins rings added ## \n")
ivc_bp_distmap = ima.distance_map(seg_new_array, C.IVC_label, "IVC_BP")
ivc_ring = ima.threshold_filter_array(ivc_bp_distmap, 0, C.ring_thickness, "IVC_ring")

seg_new_array = ima.add_masks(seg_new_array, ivc_ring, C.IVC_ring_label) # seg_s4i_array

# if debug:
#     ima.save_itk(seg_new_array, origin, spacing, "seg_s4i.nrrd", self.swap_axes)

ivc_ring_array = ima.and_filter(seg_new_array, ra_myo_thresh_array, C.IVC_ring_label, C.IVC_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, ivc_ring_array, C.IVC_ring_label) # seg_s4j_array

# if debug:
#     ima.save_itk(seg_new_array, origin, spacing, "seg_s4j.nrrd", self.swap_axes)

# #== 8/8
# print('\n ## Step 8/8: Creating the valve planes ## \n')
# print(' ## Valve planes: LPV1 ## \n')
# seg_s4j_array, header = nrrd.read(path2points+'/seg_s4j.nrrd')
# LA_BP_thresh_array, header = nrrd.read(path2points+'/tmp/LA_BP_thresh.nrrd')

# plane_LPV1_array = and_filter(seg_s4j_array,LA_BP_thresh_array,LPV1_label,plane_LPV1_label)
# seg_s4k_array = add_masks_replace(seg_s4j_array,plane_LPV1_array,plane_LPV1_label)
plane_lpv1_array = ima.and_filter(seg_new_array, la_myo_thresh_array, C.LPV1_label, C.plane_LPV1_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_lpv1_array, C.plane_LPV1_label)

# print(' ## Valve planes: LPV2 ## \n')
# plane_LPV2_array = and_filter(seg_s4k_array,LA_BP_thresh_array,LPV2_label,plane_LPV2_label)
# seg_s4k_array = add_masks_replace(seg_s4k_array,plane_LPV2_array,plane_LPV2_label)
plane_lpv2_array = ima.and_filter(seg_new_array, la_bp_thresh, C.LPV2_label, C.plane_LPV2_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_lpv2_array, C.plane_LPV2_label)

# print(' ## Valve planes: RPV1 ## \n')
# plane_RPV1_array = and_filter(seg_s4k_array,LA_BP_thresh_array,RPV1_label,plane_RPV1_label)
# seg_s4k_array = add_masks_replace(seg_s4k_array,plane_RPV1_array,plane_RPV1_label)
plane_rpv1_array = ima.and_filter(seg_new_array, la_bp_thresh, C.RPV1_label, C.plane_RPV1_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_rpv1_array, C.plane_RPV1_label)

# print(' ## Valve planes: RPV2 ## \n')
# plane_RPV2_array = and_filter(seg_s4k_array,LA_BP_thresh_array,RPV2_label,plane_RPV2_label)
# seg_s4k_array = add_masks_replace(seg_s4k_array,plane_RPV2_array,plane_RPV2_label)
plane_rpv2_array = ima.and_filter(seg_new_array, la_bp_thresh, C.RPV2_label, C.plane_RPV2_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_rpv2_array, C.plane_RPV2_label)

# print(' ## Valve planes: LAA ## \n')
# plane_LAA_array = and_filter(seg_s4k_array,LA_BP_thresh_array,LAA_label,plane_LAA_label)
# seg_s4k_array = add_masks_replace(seg_s4k_array,plane_LAA_array,plane_LAA_label)
plane_laa_array = ima.and_filter(seg_new_array, la_bp_thresh, C.LAA_label, C.plane_LAA_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_laa_array, C.plane_LAA_label)

# print(' ## Valve planes: SVC ## \n')
# RA_BP_thresh_2mm = threshold_filter_nrrd(path2points+'/tmp/RA_BP_DistMap.nrrd',0,valve_WT_svc_ivc)
# sitk.WriteImage(RA_BP_thresh_2mm,path2points+'/tmp/RA_BP_thresh_2mm.nrrd',True)
ra_bp_thresh_2mm = ima.threshold_filter_array(ra_bp_distmap, 0, C.valve_WT_svc_ivc, "RA_BP_thresh_2mm")

# RA_BP_thresh_2mm_array, header = nrrd.read(path2points+'/tmp/RA_BP_thresh_2mm.nrrd')

# plane_SVC_array = and_filter(seg_s4k_array,RA_BP_thresh_2mm_array,SVC_label,plane_SVC_label)
# plane_SVC_extra_array = and_filter(seg_s4k_array,RA_BP_thresh_2mm_array,RPV1_ring_label,plane_SVC_label)
# seg_s4k_array = add_masks_replace(seg_s4k_array,plane_SVC_array,plane_SVC_label)
# seg_s4k_array = add_masks_replace(seg_s4k_array,plane_SVC_extra_array,plane_SVC_label)
plane_svc_array = ima.and_filter(seg_new_array, ra_bp_thresh_2mm, C.SVC_label, C.plane_SVC_label)
plane_svc_extra_array = ima.and_filter(seg_new_array, ra_bp_thresh_2mm, C.RPV1_ring_label, C.plane_SVC_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_svc_array, C.plane_SVC_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_svc_extra_array, C.plane_SVC_label)

# print(' ## Valve planes: IVC ## \n')
# plane_IVC_array = and_filter(seg_s4k_array,RA_BP_thresh_2mm_array,IVC_label,plane_IVC_label)
# seg_s4k_array = add_masks_replace(seg_s4k_array,plane_IVC_array,plane_IVC_label)
plane_ivc_array = ima.and_filter(seg_new_array, ra_bp_thresh_2mm, C.IVC_label, C.plane_IVC_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_ivc_array, C.plane_IVC_label)

# print(' ## Valve planes: Formatting and saving the segmentation ## \n')
# seg_s4k_array = np.swapaxes(seg_s4k_array,0,2)
# save_itk(seg_s4k_array, origin, spacings, path2points+'/seg_s4k.nrrd')
# print(" ## Valve planes: Saved segmentation with all valve planes added ## \n")

# if debug:
#     ima.save_itk(seg_new_array, origin, spacing, "seg_s4k.nrrd", self.swap_axes)

######

import os
from seg_scripts import ImageAnalysis
import seg_scripts.Labels as Labels

C = Labels.Labels()
path2points = '/home/alexander/Downloads'
filename = os.path.join(path2points, 'points.txt')
debug = False
swap_axes = True

ima = ImageAnalysis(path2points, debug)

seg_array = ima.load_image_array(filename)

# fcp.get_connected_component_and_save('seg_s3p.nrrd', points_data['Ao_WT_tip'], C.Ao_wall_label, 'seg_s3r.nrrd')
# fcp.get_connected_component_and_save('seg_s3r.nrrd', points_data['PArt_WT_tip'], C.PArt_wall_label, 'seg_s3s.nrrd')

# 2/8: Mitral valve 
la_bp_distmap = ima.distance_map(seg_array, C.LA_BP_label, "LA_BP")
la_bp_thresh = ima.threshold_filter_array(la_bp_distmap, 0, C.valve_WT, "LA_BP")

mv_array = ima.and_filter(seg_array, la_bp_thresh, C.LV_BP_label, C.MV_label)
seg_new_array = ima.add_masks_replace(seg_array, mv_array, C.MV_label)

ima.save_itk(seg_new_array, origin, spacing, "seg_s4a.nrrd", swap_axes)

lv_myo_distmap = ima.distance_map(seg_new_array, C.LV_myo_label, "LV_myo")
lv_myo_thresh = ima.threshold_filter_array(lv_myo_distmap, 0, C.LA_WT, "LV_myo")

la_myo_extra_array = ima.and_filter(seg_new_array, lv_myo_thresh, C.LA_BP_label, C.LA_myo_label)
seg_new_array = ima.add_masks_replace(seg_new_array, la_myo_extra_array, C.LA_myo_label)

ima.save_itk(seg_new_array, origin, spacing, "seg_s4b.nrrd", swap_axes)

# 3/8: Tricuspid valve 
ra_bp_distmap = ima.distance_map(seg_new_array, C.RA_BP_label, "RA_BP")
ra_bp_thresh = ima.threshold_filter_array(ra_bp_distmap, 0, C.valve_WT, "RA_BP")

tv_array = ima.and_filter(seg_new_array, ra_bp_thresh, C.RV_BP_label, C.TV_label)
seg_new_array = ima.add_masks_replace(seg_new_array, tv_array, C.TV_label)

ima.save_itk(seg_new_array, origin, spacing, "seg_s4c.nrrd", swap_axes)

rv_myo_distmap = ima.distance_map(seg_new_array, C.RV_myo_label, "RV_myo")
rv_myo_thresh = ima.threshold_filter_array(rv_myo_distmap, 0, C.RA_WT, "RV_myo")

ra_myo_extra_array = ima.and_filter(seg_new_array, rv_myo_thresh, C.RA_BP_label, C.RA_myo_label)
seg_new_array = ima.add_masks_replace(seg_new_array, ra_myo_extra_array, C.RA_myo_label)

ima.save_itk(seg_new_array, origin, spacing, "seg_s4d.nrrd", swap_axes)

# 4/8: Aortic valve
ao_bp_distmap = ima.distance_map(seg_new_array, C.Ao_BP_label, "Ao_BP")
av_thresh = ima.threshold_filter_array(ao_bp_distmap, 0, C.valve_WT, "AV")

av_array = ima.and_filter(seg_new_array, av_thresh, C.LV_BP_label, C.AV_label)
seg_new_array = ima.add_masks_replace(seg_new_array, av_array, C.AV_label)

ima.save_itk(seg_new_array, origin, spacing, "seg_s4e.nrrd", swap_axes)

ao_wall_extra = ima.threshold_filter_array(lv_myo_distmap, 0, C.Ao_WT, "Ao_wall")

ao_wall_extra_array = ima.and_filter(seg_new_array, ao_wall_extra, C.Ao_BP_label, C.Ao_wall_label)
seg_new_array = ima.add_masks_replace(seg_new_array, ao_wall_extra_array, C.Ao_wall_label)

ima.save_itk(seg_new_array, origin, spacing, "seg_s4f.nrrd", swap_axes)

av_distmap = ima.distance_map(seg_new_array, C.AV_label, "AV")
av_sep = ima.threshold_filter_array(av_distmap, 0, 2*C.valve_WT, "AV_sep")

av_sep_array = ima.and_filter(seg_new_array, av_sep, C.MV_label, C.LV_myo_label)
seg_new_array = ima.add_masks_replace(seg_new_array, av_sep_array, C.LV_myo_label)

ima.save_itk(seg_new_array, origin, spacing, "seg_s4f.nrrd", swap_axes)

lv_myo_distmap = ima.distance_map(seg_new_array, C.LV_myo_label, "LV_myo")
la_myo_extra = ima.threshold_filter_array(lv_myo_distmap, 0, C.LA_WT, "LV_myo_extra")

la_myo_extra_array = ima.and_filter(seg_new_array, la_myo_extra, C.LA_BP_label, C.LA_myo_label)
seg_new_array = ima.add_masks_replace(seg_new_array, la_myo_extra_array, C.LA_myo_label)

ima.save_itk(seg_new_array, origin, spacing, "seg_s4ff.nrrd", swap_axes)

# 5/8: Pulmonary valve
part_bp_distmap = ima.distance_map(seg_new_array, C.PArt_BP_label, "PArt_BP")
pv = ima.threshold_filter_array(part_bp_distmap, 0, C.valve_WT, "PV")

pv_array = ima.and_filter(seg_new_array, pv, C.RV_BP_label, C.PV_label)
seg_new_array = ima.add_masks_replace(seg_new_array, pv_array, C.PV_label)

ima.save_itk(seg_new_array, origin, spacing, "seg_s4g.nrrd", swap_axes)

part_wall_extra = ima.threshold_filter_array(rv_myo_distmap, 0, C.PArt_WT, "PArt_wall")
part_wall_extra_array = ima.and_filter(seg_new_array, part_wall_extra, C.PArt_BP_label, C.PArt_wall_label)
seg_new_array = ima.add_masks_replace(seg_new_array, part_wall_extra_array, C.PArt_wall_label)

ima.save_itk(seg_new_array, origin, spacing, "seg_s4h.nrrd", swap_axes)

# 6/8: Vein rings (distance maps)
la_myo_distmap = ima.distance_map(seg_new_array, C.LA_myo_label, "LA_myo")
la_myo_thresh_array = ima.threshold_filter_array(la_myo_distmap, 0, C.ring_thickness, "LA_myo")

ra_myo_distmap = ima.distance_map(seg_new_array, C.RA_myo_label, "RA_myo")
ra_myo_thresh_array = ima.threshold_filter_array(ra_myo_distmap, 0, C.ring_thickness, "RA_myo")

# 7/8: Vein rings
lpv1_bp_distmap = ima.distance_map(seg_new_array, C.LPV1_label, "LPV1_BP")
lpv1_ring = ima.threshold_filter_array(lpv1_bp_distmap, 0, C.ring_thickness, "LPV1_ring")

seg_new_array = ima.add_masks(seg_new_array, lpv1_ring, C.LPV1_ring_label) # seg_s4i_array
lpv1_ring_array = ima.and_filter(seg_new_array, la_myo_thresh_array, C.LPV1_ring_label, C.LPV1_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, lpv1_ring_array, C.LPV1_ring_label) # seg_s4j_array

lpv2_bp_distmap = ima.distance_map(seg_new_array, C.LPV2_label, "LPV2_BP")
lpv2_ring = ima.threshold_filter_array(lpv2_bp_distmap, 0, C.ring_thickness, "LPV2_ring")

seg_new_array = ima.add_masks(seg_new_array, lpv2_ring, C.LPV2_ring_label) # seg_s4i_array
lpv2_ring_array = ima.and_filter(seg_new_array, la_myo_thresh_array, C.LPV2_ring_label, C.LPV2_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, lpv2_ring_array, C.LPV2_ring_label) # seg_s4j_array

rpv1_bp_distmap = ima.distance_map(seg_new_array, C.RPV1_label, "RPV1_BP")
rpv1_ring = ima.threshold_filter_array(rpv1_bp_distmap, 0, C.ring_thickness, "RPV1_ring")

seg_new_array = ima.add_masks_replace_only(seg_new_array, rpv1_ring, C.RPV1_ring_label, C.SVC_label) # seg_s4i_array
rpv1_ring_array = ima.and_filter(seg_new_array, la_myo_thresh_array, C.RPV1_ring_label, C.RPV1_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, rpv1_ring_array, C.RPV1_ring_label) # seg_s4j_array

rpv2_bp_distmap = ima.distance_map(seg_new_array, C.RPV2_label, "RPV2_BP")
rpv2_ring = ima.threshold_filter_array(rpv2_bp_distmap, 0, C.ring_thickness, "RPV2_ring")

seg_new_array = ima.add_masks(seg_new_array, rpv2_ring, C.RPV2_ring_label) # seg_s4i_array
rpv2_ring_array = ima.and_filter(seg_new_array, la_myo_thresh_array, C.RPV2_ring_label, C.RPV2_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, rpv2_ring_array, C.RPV2_ring_label) # seg_s4j_array

laa_bp_distmap = ima.distance_map(seg_new_array, C.LAA_label, "LAA_BP")
laa_ring = ima.threshold_filter_array(laa_bp_distmap, 0, C.ring_thickness, "LAA_ring")

seg_new_array = ima.add_masks(seg_new_array, laa_ring, C.LAA_ring_label) # seg_s4i_array
laa_ring_array = ima.and_filter(seg_new_array, la_myo_thresh_array, C.LAA_ring_label, C.LAA_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, laa_ring_array, C.LAA_ring_label) # seg_s4j_array
#######

svc_bp_distmap = ima.distance_map(seg_new_array, C.SVC_label, "SVC_BP")
svc_ring = ima.threshold_filter_array(svc_bp_distmap, 0, C.ring_thickness, "SVC_ring")

seg_new_array = ima.add_masks_replace_only(seg_new_array, svc_ring, C.SVC_ring_label, C.Ao_wall_label) # seg_s4i_array
seg_new_array = ima.add_masks_replace_only(seg_new_array, svc_ring, C.SVC_ring_label, C.LA_myo_label) # seg_s4i_array
seg_new_array = ima.add_masks_replace_only(seg_new_array, svc_ring, C.SVC_ring_label, C.RPV1_ring_label) # seg_s4i_array
seg_new_array = ima.add_masks_replace_only(seg_new_array, svc_ring, C.SVC_ring_label, C.RPV1_label) # seg_s4i_array
seg_new_array = ima.add_masks_replace_only(seg_new_array, svc_ring, C.SVC_ring_label, C.RPV2_ring_label) # seg_s4i_array
seg_new_array = ima.add_masks_replace_only(seg_new_array, svc_ring, C.SVC_ring_label, C.RPV2_label) # seg_s4i_array

svc_ring_array = ima.and_filter(seg_new_array, ra_myo_thresh_array, C.SVC_ring_label, C.SVC_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, svc_ring_array, C.SVC_ring_label) # seg_s4j_array

ivc_bp_distmap = ima.distance_map(seg_new_array, C.IVC_label, "IVC_BP")
ivc_ring = ima.threshold_filter_array(ivc_bp_distmap, 0, C.ring_thickness, "IVC_ring")

seg_new_array = ima.add_masks(seg_new_array, ivc_ring, C.IVC_ring_label) # seg_s4i_array

ima.save_itk(seg_new_array, origin, spacing, "seg_s4i.nrrd", swap_axes)

ivc_ring_array = ima.and_filter(seg_new_array, ra_myo_thresh_array, C.IVC_ring_label, C.IVC_ring_label)
seg_new_array = ima.add_masks_replace(seg_new_array, ivc_ring_array, C.IVC_ring_label) # seg_s4j_array

ima.save_itk(seg_new_array, origin, spacing, "seg_s4j.nrrd", swap_axes)

# 8/8: Valve Planes
plane_lpv1_array = ima.and_filter(seg_new_array, la_myo_thresh_array, C.LPV1_label, C.plane_LPV1_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_lpv1_array, C.plane_LPV1_label)

plane_lpv2_array = ima.and_filter(seg_new_array, la_bp_thresh, C.LPV2_label, C.plane_LPV2_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_lpv2_array, C.plane_LPV2_label)

plane_rpv1_array = ima.and_filter(seg_new_array, la_bp_thresh, C.RPV1_label, C.plane_RPV1_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_rpv1_array, C.plane_RPV1_label)

plane_rpv2_array = ima.and_filter(seg_new_array, la_bp_thresh, C.RPV2_label, C.plane_RPV2_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_rpv2_array, C.plane_RPV2_label)

plane_laa_array = ima.and_filter(seg_new_array, la_bp_thresh, C.LAA_label, C.plane_LAA_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_laa_array, C.plane_LAA_label)

ra_bp_thresh_2mm = ima.threshold_filter_array(ra_bp_distmap, 0, C.valve_WT_svc_ivc, "RA_BP_thresh_2mm")

plane_svc_array = ima.and_filter(seg_new_array, ra_bp_thresh_2mm, C.SVC_label, C.plane_SVC_label)
plane_svc_extra_array = ima.and_filter(seg_new_array, ra_bp_thresh_2mm, C.RPV1_ring_label, C.plane_SVC_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_svc_array, C.plane_SVC_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_svc_extra_array, C.plane_SVC_label)

plane_ivc_array = ima.and_filter(seg_new_array, ra_bp_thresh_2mm, C.IVC_label, C.plane_IVC_label)
seg_new_array = ima.add_masks_replace(seg_new_array, plane_ivc_array, C.plane_IVC_label)

ima.save_itk(seg_new_array, origin, spacing, "seg_s4k.nrrd", swap_axes)