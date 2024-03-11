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
la_bp_distmap = ima.distance_map(seg_array, C.LA_BP_label)
la_bp_thresh = ima.threshold_filter(la_bp_distmap, 0, C.valve_WT)

mv_array = ima.and_filter(seg_array, la_bp_thresh, C.LV_BP_label, C.MV_label)
seg_new_array = ima.add_masks_replace(seg_array, mv_array, C.MV_label)

#== 
# s4b
lv_myo_distmap = ima.distance_map(seg_new_array, C.LV_myo_label)
lv_myo_thresh = ima.threshold_filter(lv_myo_distmap, 0, C.LA_WT)

la_myo_extra_array = ima.and_filter(seg_new_array, lv_myo_thresh, C.LA_BP_label, C.LA_myo_label)
seg_new_array = ima.add_masks_replace(seg_new_array, la_myo_extra_array, C.LA_myo_label)

#== 3/8 
# s4c 

"""
print('\n ## Step 2/8: Creating the mitral valve ## \n')
LA_BP_DistMap = distance_map(path2points+'seg_s3s.nrrd',LA_BP_label)
LA_BP_thresh = threshold_filter_nrrd(path2points+'/tmp/LA_BP_DistMap.nrrd',0,valve_WT)

MV_array, header = nrrd.read(path2points+'/tmp/LA_BP_thresh.nrrd')
seg_s3s_array, header = nrrd.read(path2points+'seg_s3s.nrrd')
MV_array = and_filter(seg_s3s_array,MV_array,LV_BP_label,MV_label)
seg_s4a_array = add_masks_replace(seg_s3s_array,MV_array,MV_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
seg_s4a_array = np.swapaxes(seg_s4a_array,0,2)
save_itk(seg_s4a_array, origin, spacings, path2points+'/seg_s4a.nrrd')
print(" ## MV: Saved segmentation with mitral valve added ## \n")

# ----------------------------------------------------------------------------------------------
# Closing holes around the mitral valve (MV)
# ----------------------------------------------------------------------------------------------
LV_myo_DistMap = distance_map(path2points+'seg_s4a.nrrd',LV_myo_label)
sitk.WriteImage(LV_myo_DistMap,path2points+'/tmp/LV_myo_DistMap.nrrd',True)

LA_myo_extra = threshold_filter_nrrd(path2points+'/tmp/LV_myo_DistMap.nrrd',0,LA_WT)
sitk.WriteImage(LA_myo_extra,path2points+'/tmp/LA_myo_extra.nrrd',True)

LA_myo_extra_array, header = nrrd.read(path2points+'/tmp/LA_myo_extra.nrrd')
seg_s4a_array, header = nrrd.read(path2points+'/seg_s4a.nrrd')
LA_myo_extra_array = and_filter(seg_s4a_array,LA_myo_extra_array,LA_BP_label,LA_myo_label)
seg_s4b_array = add_masks_replace(seg_s4a_array,LA_myo_extra_array,LA_myo_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
seg_s4b_array = np.swapaxes(seg_s4b_array,0,2)
save_itk(seg_s4b_array, origin, spacings, path2points+'/seg_s4b.nrrd')
print(" ## MV extra: Saved segmentation with holes closed around mitral valve ## \n")

# ----------------------------------------------------------------------------------------------
# Create the tricuspid valve (TV)
# ----------------------------------------------------------------------------------------------
print('\n ## Step 3/8: Creating the tricuspid valve ## \n')
RA_BP_DistMap = distance_map(path2points+'/seg_s4b.nrrd',RA_BP_label)
sitk.WriteImage(RA_BP_DistMap,path2points+'/tmp/RA_BP_DistMap.nrrd',True)

RA_BP_thresh = threshold_filter_nrrd(path2points+'/tmp/RA_BP_DistMap.nrrd',0,valve_WT)
sitk.WriteImage(RA_BP_thresh,path2points+'/tmp/RA_BP_thresh.nrrd',True)

TV_array, header = nrrd.read(path2points+'/tmp/RA_BP_thresh.nrrd')
seg_s4b_array, header = nrrd.read(path2points+'/seg_s4b.nrrd')
TV_array = and_filter(seg_s4b_array,TV_array,RV_BP_label,TV_label)
seg_s4c_array = add_masks_replace(seg_s4b_array,TV_array,TV_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
seg_s4c_array = np.swapaxes(seg_s4c_array,0,2)
save_itk(seg_s4c_array, origin, spacings, path2points+'/seg_s4c.nrrd')
print(" ## TV: Saved segmentation with tricuspid valve added ## \n")

# ----------------------------------------------------------------------------------------------
# Closing holes around the tricuspid valve (TV)
# ----------------------------------------------------------------------------------------------
RV_myo_DistMap = distance_map(path2points+'/seg_s4c.nrrd',RV_myo_label)
sitk.WriteImage(RV_myo_DistMap,path2points+'/tmp/RV_myo_DistMap.nrrd',True)

RA_myo_extra = threshold_filter_nrrd(path2points+'/tmp/RV_myo_DistMap.nrrd',0,RA_WT)
sitk.WriteImage(RA_myo_extra,path2points+'/tmp/RA_myo_extra.nrrd',True)

RA_myo_extra_array, header = nrrd.read(path2points+'/tmp/RA_myo_extra.nrrd')
seg_s4c_array, header = nrrd.read(path2points+'/seg_s4c.nrrd')
RA_myo_extra_array = and_filter(seg_s4c_array,RA_myo_extra_array,RA_BP_label,RA_myo_label)
seg_s4d_array = add_masks_replace(seg_s4c_array,RA_myo_extra_array,RA_myo_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
seg_s4d_array = np.swapaxes(seg_s4d_array,0,2)
save_itk(seg_s4d_array, origin, spacings, path2points+'/seg_s4d.nrrd')
print(" ## TV corrections: Saved segmentation with holes closed around tricuspid valve ## \n")

# ----------------------------------------------------------------------------------------------
# Create the aortic valve (AV)
# ----------------------------------------------------------------------------------------------
print('\n ## Step 4/8: Creating the aortic valve ## \n')
Ao_BP_DistMap = distance_map(path2points+'/seg_s4d.nrrd',Ao_BP_label)
sitk.WriteImage(Ao_BP_DistMap,path2points+'/tmp/Ao_BP_DistMap.nrrd',True)

AV = threshold_filter_nrrd(path2points+'/tmp/Ao_BP_DistMap.nrrd',0,valve_WT)
sitk.WriteImage(AV,path2points+'/tmp/AV.nrrd',True)

AV_array, header = nrrd.read(path2points+'/tmp/AV.nrrd')
seg_s4d_array, header = nrrd.read(path2points+'/seg_s4d.nrrd')
AV_array = and_filter(seg_s4d_array,AV_array,LV_BP_label,AV_label)
seg_s4e_array = add_masks_replace(seg_s4d_array,AV_array,AV_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
seg_s4e_array = np.swapaxes(seg_s4e_array,0,2)
save_itk(seg_s4e_array, origin, spacings, path2points+'/seg_s4e.nrrd')
print(" ## AV: Saved segmentation with aortic valve added ## \n")

# ----------------------------------------------------------------------------------------------
# Closing holes around the aortic valve (AV)
# ----------------------------------------------------------------------------------------------

Ao_wall_extra = threshold_filter_nrrd(path2points+'/tmp/LV_myo_DistMap.nrrd',0,Ao_WT)
sitk.WriteImage(Ao_wall_extra,path2points+'/tmp/Ao_wall_extra.nrrd',True)

Ao_wall_extra_array, header = nrrd.read(path2points+'/tmp/Ao_wall_extra.nrrd')
seg_s4e_array, header = nrrd.read(path2points+'/seg_s4e.nrrd')
Ao_wall_extra_array = and_filter(seg_s4e_array,Ao_wall_extra_array,Ao_BP_label,Ao_wall_label)
seg_s4f_array = add_masks_replace(seg_s4e_array,Ao_wall_extra_array,Ao_wall_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
seg_s4f_array = np.swapaxes(seg_s4f_array,0,2)
save_itk(seg_s4f_array, origin, spacings, path2points+'/seg_s4f.nrrd')
print(" ## AV corrections: Saved segmentation with holes closed around aortic valve ## \n")

# ----------------------------------------------------------------------------------------------
# Separating the MV and AV
# ----------------------------------------------------------------------------------------------
print('\n ## AV corrections: Separating MV and AV ## \n')
AV_DistMap = distance_map(path2points+'/seg_s4f.nrrd',AV_label)
sitk.WriteImage(AV_DistMap,path2points+'/tmp/AV_DistMap.nrrd',True)

AV_sep = threshold_filter_nrrd(path2points+'/tmp/AV_DistMap.nrrd',0,2*valve_WT)
sitk.WriteImage(AV_sep,path2points+'/tmp/AV_sep.nrrd',True)

AV_sep_array, header = nrrd.read(path2points+'/tmp/AV_sep.nrrd')
seg_s4f_array, header = nrrd.read(path2points+'/seg_s4f.nrrd')
AV_sep_array = and_filter(seg_s4f_array,AV_sep_array,MV_label,LV_myo_label)
seg_s4f_array = add_masks_replace(seg_s4f_array,AV_sep_array,LV_myo_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
seg_s4f_array = np.swapaxes(seg_s4f_array,0,2)
save_itk(seg_s4f_array, origin, spacings, path2points+'/seg_s4f.nrrd')
print(" ## AV: Saved segmentation with AV and MV separated ## \n")

# ----------------------------------------------------------------------------------------------
# Closing new holes around the mitral valve (MV)
# ----------------------------------------------------------------------------------------------
LV_myo_DistMap = distance_map(path2points+'seg_s4f.nrrd',LV_myo_label)
sitk.WriteImage(LV_myo_DistMap,path2points+'/tmp/LV_myo_DistMap.nrrd',True)

LA_myo_extra = threshold_filter_nrrd(path2points+'/tmp/LV_myo_DistMap.nrrd',0,LA_WT)
sitk.WriteImage(LA_myo_extra,path2points+'/tmp/LA_myo_extra.nrrd',True)

LA_myo_extra_array, header = nrrd.read(path2points+'/tmp/LA_myo_extra.nrrd')
seg_s4ff_array, header = nrrd.read(path2points+'/seg_s4f.nrrd')
LA_myo_extra_array = and_filter(seg_s4ff_array,LA_myo_extra_array,LA_BP_label,LA_myo_label)
seg_s4ff_array = add_masks_replace(seg_s4ff_array,LA_myo_extra_array,LA_myo_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
seg_s4ff_array = np.swapaxes(seg_s4ff_array,0,2)
save_itk(seg_s4ff_array, origin, spacings, path2points+'/seg_s4ff.nrrd')
print(" ## MV extra: Saved segmentation with holes closed around mitral valve ## \n")

# ----------------------------------------------------------------------------------------------
# Create the pulmonary valve (PV)
# ----------------------------------------------------------------------------------------------
print('\n ## Step 5/8: Creating the pulmonary valve ## \n')
PArt_BP_DistMap = distance_map(path2points+'/seg_s4ff.nrrd',PArt_BP_label)
sitk.WriteImage(PArt_BP_DistMap,path2points+'/tmp/PArt_BP_DistMap.nrrd',True)

PV = threshold_filter_nrrd(path2points+'/tmp/PArt_BP_DistMap.nrrd',0,valve_WT)
sitk.WriteImage(PV,path2points+'/tmp/PV.nrrd',True)

PV_array, header = nrrd.read(path2points+'/tmp/PV.nrrd')
seg_s4ff_array, header = nrrd.read(path2points+'/seg_s4ff.nrrd')
PV_array = and_filter(seg_s4ff_array,PV_array,RV_BP_label,PV_label)
seg_s4g_array = add_masks_replace(seg_s4ff_array,PV_array,PV_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
seg_s4g_array = np.swapaxes(seg_s4g_array,0,2)
save_itk(seg_s4g_array, origin, spacings, path2points+'/seg_s4g.nrrd')
print(" ## PV: Saved segmentation with pulmonary valve added ## \n")

# ----------------------------------------------------------------------------------------------
# Closing holes around the pulmonary valve (PV)
# ----------------------------------------------------------------------------------------------

PArt_wall_extra = threshold_filter_nrrd(path2points+'/tmp/RV_myo_DistMap.nrrd',0,PArt_WT)
sitk.WriteImage(PArt_wall_extra,path2points+'/tmp/PArt_wall_extra.nrrd',True)

PArt_wall_extra_array, header = nrrd.read(path2points+'/tmp/PArt_wall_extra.nrrd')
seg_s4g_array, header = nrrd.read(path2points+'/seg_s4g.nrrd')
PArt_wall_extra_array = and_filter(seg_s4g_array,PArt_wall_extra_array,PArt_BP_label,PArt_wall_label)
seg_s4h_array = add_masks_replace(seg_s4g_array,PArt_wall_extra_array,PArt_wall_label)

# ----------------------------------------------------------------------------------------------
# Format and save the segmentation
# ----------------------------------------------------------------------------------------------
seg_s4h_array = np.swapaxes(seg_s4h_array,0,2)
save_itk(seg_s4h_array, origin, spacings, path2points+'/seg_s4h.nrrd')
print(" ## PV corrections: Saved segmentation with holes closed around pulmonary valve ## \n")
"""