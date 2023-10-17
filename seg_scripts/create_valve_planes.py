import img
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import copy
import json
import os
import argparse

from common import parse_txt_to_json, get_json_data, make_tmp

# ----------------------------------------------------------------------------------------------
# Define the wall thickness
# ----------------------------------------------------------------------------------------------
SCALE_FACTOR = 1/0.39844 # scale factor

valve_WT = SCALE_FACTOR*4
valve_WT_svc_ivc = SCALE_FACTOR*4
ring_thickness = SCALE_FACTOR*4

RV_WT = SCALE_FACTOR*3.50
LA_WT = SCALE_FACTOR*2.00
RA_WT = SCALE_FACTOR*2.00
Ao_WT = SCALE_FACTOR*2.00
PArt_WT = SCALE_FACTOR*2.00

LV_BP_label = 1
LV_myo_label = 2
RV_BP_label = 3
LA_BP_label = 4
RA_BP_label = 5
Ao_BP_label = 6
PArt_BP_label = 7
LPV1_label = 8
LPV2_label = 9
RPV1_label = 10
RPV2_label = 11
LAA_label = 12
SVC_label = 13
IVC_label = 14

LV_neck_label = 101
RV_myo_label = 103
LA_myo_label = 104
RA_myo_label = 105
Ao_wall_label = 106
PArt_wall_label = 107

MV_label = 201
TV_label = 202
AV_label = 203
PV_label = 204
plane_LPV1_label = 205
plane_LPV2_label = 206
plane_RPV1_label = 207
plane_RPV2_label = 208
plane_LAA_label = 209
plane_SVC_label = 210
plane_IVC_label = 211

LPV1_ring_label = 221
LPV2_ring_label = 222
RPV1_ring_label = 223
RPV2_ring_label = 224
LAA_ring_label = 225
SVC_ring_label = 226
IVC_ring_label = 227

def extract_structure_w_distance_map(image_path, dmap_label, thresh_label, and_replace_label, tmp_dir) : 
    TMP = lambda x: os.path.join(tmp_dir, x)

    dmap_name = f'{dmap_label[0]}_DistMap.nrrd'
    thresh_name = f'{thresh_label[0]}.nrrd'

    print(' ## MV corrections: Executing distance map ## \n')
    LV_myo_DistMap = img.distance_map(image_path,dmap_label[1])
    print(' ## MV corrections: Writing temporary image ## \n')
    sitk.WriteImage(LV_myo_DistMap,TMP(dmap_name),True)

    print(' ## MV corrections: Thresholding distance filter ## \n')
    thresh_im = img.threshold_filter_nrrd(TMP(dmap_name),0,thresh_label[1])
    sitk.WriteImage(thresh_im,TMP(thresh_name),True)

    print(' ## MV correction: AND filter of distance map and LA blood pool ## \n')
    thresh_im_array, header = nrrd.read(TMP(thresh_name))
    seg_input_array, header = nrrd.read(image_path)
    thresh_im_array = img.and_filter(seg_input_array,thresh_im_array,and_replace_label[0],and_replace_label[1])
    seg_output_array = img.add_masks_replace(seg_input_array,thresh_im_array,and_replace_label[1])

    return seg_output_array

def main(args) : 
    path2points = args.path_to_points
    path2ptsjson = args.points_json
    path2originjson = args.origin_spacing_json

    points_output_file = parse_txt_to_json(path2points, path2ptsjson, "points", "labels")
    points_data = get_json_data(points_output_file)

    origin_spacing_output_file = parse_txt_to_json(path2points, path2originjson, "origin_spacing", "origin_spacing_labels")
    origin_data = get_json_data(origin_spacing_output_file)

    origin = origin_data['origin']
    spacings = origin_data['spacing']

    make_tmp(path2points)
    DIR = lambda x: os.path.join(path2points, x)
    TMP = lambda x: os.path.join(path2points, "tmp", x)
    tmp_dir = TMP('')

    # ----------------------------------------------------------------------------------------------
    # Prepare the seed points
    # ----------------------------------------------------------------------------------------------
    Ao_wall_tip_seed = points_data['Ao_WT_tip']
    PArt_wall_tip_seed = points_data['PArt_WT_tip']

    # ----------------------------------------------------------------------------------------------
    # Removing parts of Ao and PArt wall remaining from cropping 
    # ----------------------------------------------------------------------------------------------
    print('\n ## Step 1/8: Cropping major vessels ## \n')
    print(' ## Cropping major vessels: Removing remaining wall segments ## \n')
    seg_s3r_array = img.connected_component(DIR('seg_s3p.nrrd'), Ao_wall_tip_seed, Ao_wall_label,path2points)
    seg_s3r_array = np.swapaxes(seg_s3r_array,0,2)
    img.save_itk(seg_s3r_array, origin, spacings, DIR('seg_s3r.nrrd'))
    print(" ## Cropping major vessels: Saved segmentation with aorta cropped ## \n")

    seg_s3s_array = img.connected_component(DIR('seg_s3r.nrrd'), PArt_wall_tip_seed, PArt_wall_label,path2points)
    seg_s3s_array = np.swapaxes(seg_s3s_array,0,2)
    img.save_itk(seg_s3s_array, origin, spacings, DIR('seg_s3s.nrrd'))
    print(" ## Cropping major vessels: Saved segmentation with pulmonary artery cropped ## \n")

    # ----------------------------------------------------------------------------------------------
    # Create the mitral valve (MV)
    # ----------------------------------------------------------------------------------------------
    print('\n ## Step 2/8: Creating the mitral valve ## \n')
    dmap_label = ('LA_BP', LA_BP_label)
    thresh_label = ('LA_BP_thresh', valve_WT)
    and_replace_label = [LV_BP_label, MV_label]
    seg_s4a_array = extract_structure_w_distance_map(DIR('seg_s3s.nrrd'), dmap_label, thresh_label, and_replace_label, tmp_dir)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## MV: Formatting and saving the segmentation ## \n')
    seg_s4a_array = np.swapaxes(seg_s4a_array,0,2)
    img.save_itk(seg_s4a_array, origin, spacings, DIR('seg_s4a.nrrd'))
    print(" ## MV: Saved segmentation with mitral valve added ## \n")

    # ----------------------------------------------------------------------------------------------
    # Closing holes around the mitral valve (MV)
    # ----------------------------------------------------------------------------------------------
    print(' ## MV corrections: Closing holes around the mitral valve ## \n')
    dmap_label = ('LV_myo', LV_myo_label)
    thresh_label = ('LV_myo_extra', LA_WT)
    and_replace_label = [LA_BP_label,LA_myo_label]
    seg_s4b_array = extract_structure_w_distance_map(DIR('seg_s4a.nrrd'), dmap_label, thresh_label, and_replace_label, tmp_dir)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## MV corrections: Formatting and saving the segmentation ## \n')
    seg_s4b_array = np.swapaxes(seg_s4b_array,0,2)
    img.save_itk(seg_s4b_array, origin, spacings, DIR('seg_s4b.nrrd'))
    print(" ## MV extra: Saved segmentation with holes closed around mitral valve ## \n")

    # ----------------------------------------------------------------------------------------------
    # Create the tricuspid valve (TV)
    # ----------------------------------------------------------------------------------------------
    print('\n ## Step 3/8: Creating the tricuspid valve ## \n')
    dmap_label = ('RA_BP', RA_BP_label)
    thresh_label = ('RA_BP_thresh', valve_WT)
    and_replace_label = [RV_BP_label, TV_label]
    seg_s4c_array = extract_structure_w_distance_map(DIR('seg_s4b.nrrd'), dmap_label, thresh_label, and_replace_label, tmp_dir)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## TV: Formatting and saving the segmentation ## \n')
    seg_s4c_array = np.swapaxes(seg_s4c_array,0,2)
    img.save_itk(seg_s4c_array, origin, spacings, DIR('seg_s4c.nrrd'))
    print(" ## TV: Saved segmentation with tricuspid valve added ## \n")

    # ----------------------------------------------------------------------------------------------
    # Closing holes around the tricuspid valve (TV)
    # ----------------------------------------------------------------------------------------------
    print(' ## TV corrections: Closing holes around the tricuspid valve ## \n')
    dmap_label = ('RA_myo', RA_myo_label)
    thresh_label = ('RA_myo_extra', RA_WT)
    and_replace_label = [RA_BP_label,RA_myo_label]
    seg_s4d_array = extract_structure_w_distance_map(DIR('seg_s4c.nrrd'), dmap_label, thresh_label, and_replace_label, tmp_dir)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## TV corrections: Formatting and saving the segmentation ## \n')
    seg_s4d_array = np.swapaxes(seg_s4d_array,0,2)
    img.save_itk(seg_s4d_array, origin, spacings, DIR('seg_s4d.nrrd'))
    print(" ## TV corrections: Saved segmentation with holes closed around tricuspid valve ## \n")

    # ----------------------------------------------------------------------------------------------
    # Create the aortic valve (AV)
    # ----------------------------------------------------------------------------------------------
    print('\n ## Step 4/8: Creating the aortic valve ## \n')
    dmap_label = ('Ao_BP', Ao_BP_label)
    thresh_label = ('AV', valve_WT)
    and_replace_label = [LV_BP_label, AV_label]
    seg_s4e_array = extract_structure_w_distance_map(DIR('seg_s4d.nrrd'), dmap_label, thresh_label, and_replace_label, tmp_dir)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## AV: Formatting and saving the segmentation ## \n')
    seg_s4e_array = np.swapaxes(seg_s4e_array,0,2)
    img.save_itk(seg_s4e_array, origin, spacings, DIR('seg_s4e.nrrd'))
    print(" ## AV: Saved segmentation with aortic valve added ## \n")

    # ----------------------------------------------------------------------------------------------
    # Closing holes around the aortic valve (AV)
    # ----------------------------------------------------------------------------------------------
    print(' ## AV corrections: Closing holes around the aortic valve ## \n')

    print(' ## AV corrections: Thresholding distance filter ## \n')
    Ao_wall_extra = img.threshold_filter_nrrd(TMP('LV_myo_DistMap.nrrd'),0,Ao_WT)
    sitk.WriteImage(Ao_wall_extra,TMP('Ao_wall_extra.nrrd'),True)

    print(' ## AV corrections: AND filter of distance map and Ao blood pool ## \n')
    Ao_wall_extra_array, header = nrrd.read(TMP('Ao_wall_extra.nrrd'))
    seg_s4e_array, header = nrrd.read(DIR('seg_s4e.nrrd'))
    Ao_wall_extra_array = img.and_filter(seg_s4e_array,Ao_wall_extra_array,Ao_BP_label,Ao_wall_label)
    seg_s4f_array = img.add_masks_replace(seg_s4e_array,Ao_wall_extra_array,Ao_wall_label)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## AV corrections: Formatting and saving the segmentation ## \n')
    seg_s4f_array = np.swapaxes(seg_s4f_array,0,2)
    img.save_itk(seg_s4f_array, origin, spacings, DIR('seg_s4f.nrrd'))
    print(" ## AV corrections: Saved segmentation with holes closed around aortic valve ## \n")

    # ----------------------------------------------------------------------------------------------
    # Separating the MV and AV
    # ----------------------------------------------------------------------------------------------
    print('\n ## AV corrections: Separating MV and AV ## \n')
    print(' ## AV: Executing distance map ## \n')
    AV_DistMap = img.distance_map(DIR('seg_s4f.nrrd'),AV_label)
    print(' ## AV: Writing temporary image ## \n')
    sitk.WriteImage(AV_DistMap,TMP('AV_DistMap.nrrd'),True)

    print(' ## AV: Thresholding distance filter ## \n')
    AV_sep = img.threshold_filter_nrrd(TMP('AV_DistMap.nrrd'),0,2*valve_WT)
    sitk.WriteImage(AV_sep,TMP('AV_sep.nrrd'),True)

    print(' ## AV: AND filter of distance map and MV ## \n')
    AV_sep_array, header = nrrd.read(TMP('AV_sep.nrrd'))
    seg_s4f_array, header = nrrd.read(DIR('seg_s4f.nrrd'))
    AV_sep_array = img.and_filter(seg_s4f_array,AV_sep_array,MV_label,LV_myo_label)
    seg_s4f_array = img.add_masks_replace(seg_s4f_array,AV_sep_array,LV_myo_label)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## AV: Formatting and saving the segmentation ## \n')
    seg_s4f_array = np.swapaxes(seg_s4f_array,0,2)
    img.save_itk(seg_s4f_array, origin, spacings, DIR('seg_s4f.nrrd'))
    print(" ## AV: Saved segmentation with AV and MV separated ## \n")

    # ----------------------------------------------------------------------------------------------
    # Closing new holes around the mitral valve (MV)
    # ----------------------------------------------------------------------------------------------
    print(' ## MV corrections: Closing holes around the mitral valve ## \n')
    print(' ## MV corrections: Executing distance map ## \n')
    LV_myo_DistMap = img.distance_map(DIR('seg_s4f.nrrd'),LV_myo_label)
    print(' ## MV corrections: Writing temporary image ## \n')
    sitk.WriteImage(LV_myo_DistMap,TMP('LV_myo_DistMap.nrrd'),True)

    print(' ## MV corrections: Thresholding distance filter ## \n')
    LA_myo_extra = img.threshold_filter_nrrd(TMP('LV_myo_DistMap.nrrd'),0,LA_WT)
    sitk.WriteImage(LA_myo_extra,TMP('LA_myo_extra.nrrd'),True)

    print(' ## MV correction: AND filter of distance map and LA blood pool ## \n')
    LA_myo_extra_array, header = nrrd.read(TMP('LA_myo_extra.nrrd'))
    seg_s4ff_array, header = nrrd.read(DIR('seg_s4f.nrrd'))
    LA_myo_extra_array = img.and_filter(seg_s4ff_array,LA_myo_extra_array,LA_BP_label,LA_myo_label)
    seg_s4ff_array = img.add_masks_replace(seg_s4ff_array,LA_myo_extra_array,LA_myo_label)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## MV corrections: Formatting and saving the segmentation ## \n')
    seg_s4ff_array = np.swapaxes(seg_s4ff_array,0,2)
    img.save_itk(seg_s4ff_array, origin, spacings, DIR('seg_s4ff.nrrd'))
    print(" ## MV extra: Saved segmentation with holes closed around mitral valve ## \n")

    # ----------------------------------------------------------------------------------------------
    # Create the pulmonary valve (PV)
    # ----------------------------------------------------------------------------------------------
    print('\n ## Step 5/8: Creating the pulmonary valve ## \n')
    print(' ## PV: Executing distance map ## \n')
    PArt_BP_DistMap = img.distance_map(DIR('seg_s4ff.nrrd'),PArt_BP_label)
    print(' ## PV: Writing temporary image ## \n')
    sitk.WriteImage(PArt_BP_DistMap,TMP('PArt_BP_DistMap.nrrd'),True)

    print(' ## PV: Thresholding distance filter ## \n')
    PV = img.threshold_filter_nrrd(TMP('PArt_BP_DistMap.nrrd'),0,valve_WT)
    sitk.WriteImage(PV,TMP('PV.nrrd'),True)

    print(' ## PV: AND filter of distance map and RV blood pool ## \n')
    PV_array, header = nrrd.read(TMP('PV.nrrd'))
    seg_s4ff_array, header = nrrd.read(DIR('seg_s4ff.nrrd'))
    PV_array = img.and_filter(seg_s4ff_array,PV_array,RV_BP_label,PV_label)
    seg_s4g_array = img.add_masks_replace(seg_s4ff_array,PV_array,PV_label)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## PV: Formatting and saving the segmentation ## \n')
    seg_s4g_array = np.swapaxes(seg_s4g_array,0,2)
    img.save_itk(seg_s4g_array, origin, spacings, DIR('seg_s4g.nrrd'))
    print(" ## PV: Saved segmentation with pulmonary valve added ## \n")

    # ----------------------------------------------------------------------------------------------
    # Closing holes around the pulmonary valve (PV)
    # ----------------------------------------------------------------------------------------------
    print(' ## PV corrections: Closing holes around the pulmonary valve ## \n')

    print(' ## PV corrections: Thresholding distance filter ## \n')
    PArt_wall_extra = img.threshold_filter_nrrd(TMP('RV_myo_DistMap.nrrd'),0,PArt_WT)
    sitk.WriteImage(PArt_wall_extra,TMP('PArt_wall_extra.nrrd'),True)

    print(' ## PV corrections: AND filter of distance map and PArt blood pool ## \n')
    PArt_wall_extra_array, header = nrrd.read(TMP('PArt_wall_extra.nrrd'))
    seg_s4g_array, header = nrrd.read(DIR('seg_s4g.nrrd'))
    PArt_wall_extra_array = img.and_filter(seg_s4g_array,PArt_wall_extra_array,PArt_BP_label,PArt_wall_label)
    seg_s4h_array = img.add_masks_replace(seg_s4g_array,PArt_wall_extra_array,PArt_wall_label)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## PV corrections: Formatting and saving the segmentation ## \n')
    seg_s4h_array = np.swapaxes(seg_s4h_array,0,2)
    img.save_itk(seg_s4h_array, origin, spacings, DIR('seg_s4h.nrrd'))
    print(" ## PV corrections: Saved segmentation with holes closed around pulmonary valve ## \n")

    # ----------------------------------------------------------------------------------------------
    # Creating the distance maps needed to cut the vein rings
    # ----------------------------------------------------------------------------------------------
    print('\n ## Step 6/8: Create the distance maps needed to cut the vein rings ## \n')
    print(' ## Create the distance maps needed to cut the vein rings: Executing distance map ## \n')
    LA_myo_DistMap = img.distance_map(DIR('seg_s4h.nrrd'),LA_myo_label)
    RA_myo_DistMap = img.distance_map(DIR('seg_s4h.nrrd'),RA_myo_label)
    print(' ## Create the distance maps needed to cut the vein rings: Writing temporary image ## \n')
    sitk.WriteImage(LA_myo_DistMap,TMP('LA_myo_DistMap.nrrd'),True)
    sitk.WriteImage(RA_myo_DistMap,TMP('RA_myo_DistMap.nrrd'),True)

    print(' ## Cutting vein rings: Thresholding distance filter ## \n')
    LA_myo_thresh = img.threshold_filter_nrrd(TMP('LA_myo_DistMap.nrrd'),0,ring_thickness)
    RA_myo_thresh = img.threshold_filter_nrrd(TMP('RA_myo_DistMap.nrrd'),0,ring_thickness)
    sitk.WriteImage(LA_myo_thresh,TMP('LA_myo_thresh.nrrd'),True)
    sitk.WriteImage(RA_myo_thresh,TMP('RA_myo_thresh.nrrd'),True)

    LA_myo_thresh_array, header = nrrd.read(TMP('LA_myo_thresh.nrrd'))
    RA_myo_thresh_array, header = nrrd.read(TMP('RA_myo_thresh.nrrd'))

    # ----------------------------------------------------------------------------------------------
    # Create ring for LPVeins1
    # ----------------------------------------------------------------------------------------------
    print('\n ## Step 7/8: Creating the vein rings ## \n')
    print(' ## LPVeins1: Executing distance map ## \n')
    LPV1_BP_DistMap = img.distance_map(DIR('seg_s4h.nrrd'),LPV1_label)
    print(' ## LPVeins1: Writing temporary image ## \n')
    sitk.WriteImage(LPV1_BP_DistMap,TMP('LPV1_BP_DistMap.nrrd'),True)

    print(' ## LPVeins1: Thresholding distance filter ## \n')
    LPV1_ring = img.threshold_filter_nrrd(TMP('LPV1_BP_DistMap.nrrd'),0,ring_thickness)
    sitk.WriteImage(LPV1_ring,TMP('LPV1_ring.nrrd'),True)

    print(' ## LPVeins1: Add the ring to the segmentation ## \n')
    LPV1_ring_array, header = nrrd.read(TMP('LPV1_ring.nrrd'))
    seg_s4h_array, header = nrrd.read(DIR('seg_s4h.nrrd'))
    seg_s4i_array = img.add_masks(seg_s4h_array,LPV1_ring_array,LPV1_ring_label)

    LPV1_ring_array = img.and_filter(seg_s4i_array,LA_myo_thresh_array,LPV1_ring_label,LPV1_ring_label)
    seg_s4j_array = img.add_masks_replace(seg_s4h_array,LPV1_ring_array,LPV1_ring_label)

    # ----------------------------------------------------------------------------------------------
    # Create ring for LPVeins2
    # ----------------------------------------------------------------------------------------------
    print('\n ## Creating the vein rings ## \n')
    print(' ## LPVeins2: Executing distance map ## \n')
    LPV2_BP_DistMap = img.distance_map(DIR('seg_s4h.nrrd'),LPV2_label)
    print(' ## LPVeins2: Writing temporary image ## \n')
    sitk.WriteImage(LPV2_BP_DistMap,TMP('LPV2_BP_DistMap.nrrd'),True)

    print(' ## LPVeins2: Thresholding distance filter ## \n')
    LPV2_ring = img.threshold_filter_nrrd(TMP('LPV2_BP_DistMap.nrrd'),0,ring_thickness)
    sitk.WriteImage(LPV2_ring,TMP('LPV2_ring.nrrd'),True)

    print(' ## LPVeins2: Add the ring to the segmentation ## \n')
    LPV2_ring_array, header = nrrd.read(TMP('LPV2_ring.nrrd'))
    seg_s4i_array = img.add_masks(seg_s4i_array,LPV2_ring_array,LPV2_ring_label)

    LPV2_ring_array = img.and_filter(seg_s4i_array,LA_myo_thresh_array,LPV2_ring_label,LPV2_ring_label)
    seg_s4j_array = img.add_masks_replace(seg_s4j_array,LPV2_ring_array,LPV2_ring_label)

    # ----------------------------------------------------------------------------------------------
    # Create ring for RPVeins1
    # ----------------------------------------------------------------------------------------------
    print('\n ## Creating the vein rings ## \n')
    print(' ## RPVeins1: Executing distance map ## \n')
    RPV1_BP_DistMap = img.distance_map(DIR('seg_s4h.nrrd'),RPV1_label)
    print(' ## RPVeins1: Writing temporary image ## \n')
    sitk.WriteImage(RPV1_BP_DistMap,TMP('RPV1_BP_DistMap.nrrd'),True)

    print(' ## RPVeins1: Thresholding distance filter ## \n')
    RPV1_ring = img.threshold_filter_nrrd(TMP('RPV1_BP_DistMap.nrrd'),0,ring_thickness)
    sitk.WriteImage(RPV1_ring,TMP('RPV1_ring.nrrd'),True)

    print(' ## RPVeins1: Add the ring to the segmentation ## \n')
    RPV1_ring_array, header = nrrd.read(TMP('RPV1_ring.nrrd'))
    seg_s4i_array = img.add_masks_replace_only(seg_s4i_array,RPV1_ring_array,RPV1_ring_label,SVC_label)

    RPV1_ring_array = img.and_filter(seg_s4i_array,LA_myo_thresh_array,RPV1_ring_label,RPV1_ring_label)
    seg_s4j_array = img.add_masks_replace(seg_s4j_array,RPV1_ring_array,RPV1_ring_label)

    # ----------------------------------------------------------------------------------------------
    # Create ring for RPVeins2
    # ----------------------------------------------------------------------------------------------
    print('\n ## Creating the vein rings ## \n')
    print(' ## RPVeins2: Executing distance map ## \n')
    RPV2_BP_DistMap = img.distance_map(DIR('seg_s4h.nrrd'),RPV2_label)
    print(' ## RPVeins2: Writing temporary image ## \n')
    sitk.WriteImage(RPV2_BP_DistMap,TMP('RPV2_BP_DistMap.nrrd'),True)

    print(' ## RPVeins2: Thresholding distance filter ## \n')
    RPV2_ring = img.threshold_filter_nrrd(TMP('RPV2_BP_DistMap.nrrd'),0,ring_thickness)
    sitk.WriteImage(RPV2_ring,TMP('RPV2_ring.nrrd'),True)

    print(' ## RPVeins2: Add the ring to the segmentation ## \n')
    RPV2_ring_array, header = nrrd.read(TMP('RPV2_ring.nrrd'))
    seg_s4i_array = img.add_masks(seg_s4i_array,RPV2_ring_array,RPV2_ring_label)

    RPV2_ring_array = img.and_filter(seg_s4i_array,LA_myo_thresh_array,RPV2_ring_label,RPV2_ring_label)
    seg_s4j_array = img.add_masks_replace(seg_s4j_array,RPV2_ring_array,RPV2_ring_label)

    # ----------------------------------------------------------------------------------------------
    # Create ring for LAA
    # ----------------------------------------------------------------------------------------------
    print('\n ## Creating the vein rings ## \n')
    print(' ## LAA: Executing distance map ## \n')
    LAA_BP_DistMap = img.distance_map(DIR('seg_s4h.nrrd'),LAA_label)
    print(' ## LAA: Writing temporary image ## \n')
    sitk.WriteImage(LAA_BP_DistMap,TMP('LAA_BP_DistMap.nrrd'),True)

    print(' ## LAA: Thresholding distance filter ## \n')
    LAA_ring = img.threshold_filter_nrrd(TMP('LAA_BP_DistMap.nrrd'),0,ring_thickness)
    sitk.WriteImage(LAA_ring,TMP('LAA_ring.nrrd'),True)

    print(' ## LAA: Add the ring to the segmentation ## \n')
    LAA_ring_array, header = nrrd.read(TMP('LAA_ring.nrrd'))
    seg_s4i_array = img.add_masks(seg_s4i_array,LAA_ring_array,LAA_ring_label)

    LAA_ring_array = img.and_filter(seg_s4i_array,LA_myo_thresh_array,LAA_ring_label,LAA_ring_label)
    seg_s4j_array = img.add_masks_replace(seg_s4j_array,LAA_ring_array,LAA_ring_label)

    # ----------------------------------------------------------------------------------------------
    # Create ring for SVC
    # ----------------------------------------------------------------------------------------------
    print('\n ## Creating the vein rings ## \n')
    print(' ## SVC: Executing distance map ## \n')
    SVC_BP_DistMap = img.distance_map(DIR('seg_s4h.nrrd'),SVC_label)
    print(' ## SVC: Writing temporary image ## \n')
    sitk.WriteImage(SVC_BP_DistMap,TMP('SVC_BP_DistMap.nrrd'),True)

    print(' ## SVC: Thresholding distance filter ## \n')
    SVC_ring = img.threshold_filter_nrrd(TMP('SVC_BP_DistMap.nrrd'),0,ring_thickness)
    sitk.WriteImage(SVC_ring,TMP('SVC_ring.nrrd'),True)

    print(' ## SVC: Add the ring to the segmentation ## \n')
    SVC_ring_array, header = nrrd.read(TMP('SVC_ring.nrrd'))
    seg_s4i_array = img.add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,Ao_wall_label)
    seg_s4i_array = img.add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,LA_myo_label)
    seg_s4i_array = img.add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,RPV1_ring_label)
    seg_s4i_array = img.add_masks_replace_only(seg_s4i_array,SVC_ring_array,SVC_ring_label,RPV1_label)

    SVC_ring_array = img.and_filter(seg_s4i_array,RA_myo_thresh_array,SVC_ring_label,SVC_ring_label)
    seg_s4j_array = img.add_masks_replace(seg_s4j_array,SVC_ring_array,SVC_ring_label)

    # ----------------------------------------------------------------------------------------------
    # Create ring for IVC
    # ----------------------------------------------------------------------------------------------
    print('\n ## Creating the vein rings ## \n')
    print(' ## IVC: Executing distance map ## \n')
    IVC_BP_DistMap = img.distance_map(DIR('seg_s4h.nrrd'),IVC_label)
    print(' ## IVC: Writing temporary image ## \n')
    sitk.WriteImage(IVC_BP_DistMap,TMP('IVC_BP_DistMap.nrrd'),True)

    print(' ## IVC: Thresholding distance filter ## \n')
    IVC_ring = img.threshold_filter_nrrd(TMP('IVC_BP_DistMap.nrrd'),0,ring_thickness)
    sitk.WriteImage(IVC_ring,TMP('IVC_ring.nrrd'),True)

    print(' ## IVC: Add the ring to the segmentation ## \n')
    IVC_ring_array, header = nrrd.read(TMP('IVC_ring.nrrd'))
    seg_s4i_array = img.add_masks(seg_s4i_array,IVC_ring_array,IVC_ring_label)

    IVC_ring_array = img.and_filter(seg_s4i_array,RA_myo_thresh_array,IVC_ring_label,IVC_ring_label)
    seg_s4j_array = img.add_masks_replace(seg_s4j_array,IVC_ring_array,IVC_ring_label)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## Vein rings: Formatting and saving the segmentation ## \n')
    seg_s4i_array = np.swapaxes(seg_s4i_array,0,2)
    img.save_itk(seg_s4i_array, origin, spacings, DIR('seg_s4i.nrrd'))
    print(" ## Vein rings: Saved segmentation with veins rings added ## \n")

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## Cutting vein rings: Formatting and saving the segmentation ## \n')
    seg_s4j_array = np.swapaxes(seg_s4j_array,0,2)
    img.save_itk(seg_s4j_array, origin, spacings, DIR('seg_s4j.nrrd'))
    print(" ## Cutting vein rings: Saved segmentation with veins rings added ## \n")

    # ----------------------------------------------------------------------------------------------
    # Creating plane for LPV1
    # ----------------------------------------------------------------------------------------------
    print('\n ## Step 8/8: Creating the valve planes ## \n')
    print(' ## Valve planes: LPV1 ## \n')
    seg_s4j_array, header = nrrd.read(DIR('seg_s4j.nrrd'))
    LA_BP_thresh_array, header = nrrd.read(TMP('LA_BP_thresh.nrrd'))

    plane_LPV1_array = img.and_filter(seg_s4j_array,LA_BP_thresh_array,LPV1_label,plane_LPV1_label)
    seg_s4k_array = img.add_masks_replace(seg_s4j_array,plane_LPV1_array,plane_LPV1_label)

    # ----------------------------------------------------------------------------------------------
    # Creating plane for LPV2
    # ----------------------------------------------------------------------------------------------
    print(' ## Valve planes: LPV2 ## \n')
    plane_LPV2_array = img.and_filter(seg_s4k_array,LA_BP_thresh_array,LPV2_label,plane_LPV2_label)
    seg_s4k_array = img.add_masks_replace(seg_s4k_array,plane_LPV2_array,plane_LPV2_label)

    # ----------------------------------------------------------------------------------------------
    # Creating plane for RPV1
    # ----------------------------------------------------------------------------------------------
    print(' ## Valve planes: RPV1 ## \n')
    plane_RPV1_array = img.and_filter(seg_s4k_array,LA_BP_thresh_array,RPV1_label,plane_RPV1_label)
    seg_s4k_array = img.add_masks_replace(seg_s4k_array,plane_RPV1_array,plane_RPV1_label)

    # ----------------------------------------------------------------------------------------------
    # Creating plane for RPV2
    # ----------------------------------------------------------------------------------------------
    print(' ## Valve planes: RPV2 ## \n')
    plane_RPV2_array = img.and_filter(seg_s4k_array,LA_BP_thresh_array,RPV2_label,plane_RPV2_label)
    seg_s4k_array = img.add_masks_replace(seg_s4k_array,plane_RPV2_array,plane_RPV2_label)

    # ----------------------------------------------------------------------------------------------
    # Creating plane for LAA
    # ----------------------------------------------------------------------------------------------
    print(' ## Valve planes: LAA ## \n')
    plane_LAA_array = img.and_filter(seg_s4k_array,LA_BP_thresh_array,LAA_label,plane_LAA_label)
    seg_s4k_array = img.add_masks_replace(seg_s4k_array,plane_LAA_array,plane_LAA_label)

    # ----------------------------------------------------------------------------------------------
    # Creating plane for SVC
    # ----------------------------------------------------------------------------------------------
    print(' ## Valve planes: SVC ## \n')
    RA_BP_thresh_2mm = img.threshold_filter_nrrd(TMP('RA_BP_DistMap.nrrd'),0,valve_WT_svc_ivc)
    sitk.WriteImage(RA_BP_thresh_2mm,TMP('RA_BP_thresh_2mm.nrrd'),True)

    RA_BP_thresh_2mm_array, header = nrrd.read(TMP('RA_BP_thresh_2mm.nrrd'))

    plane_SVC_array = img.and_filter(seg_s4k_array,RA_BP_thresh_2mm_array,SVC_label,plane_SVC_label)
    plane_SVC_extra_array = img.and_filter(seg_s4k_array,RA_BP_thresh_2mm_array,RPV1_ring_label,plane_SVC_label)
    seg_s4k_array = img.add_masks_replace(seg_s4k_array,plane_SVC_array,plane_SVC_label)
    seg_s4k_array = img.add_masks_replace(seg_s4k_array,plane_SVC_extra_array,plane_SVC_label)

    # ----------------------------------------------------------------------------------------------
    # Creating plane for IVC
    # ----------------------------------------------------------------------------------------------
    print(' ## Valve planes: IVC ## \n')
    plane_IVC_array = img.and_filter(seg_s4k_array,RA_BP_thresh_2mm_array,IVC_label,plane_IVC_label)
    seg_s4k_array = img.add_masks_replace(seg_s4k_array,plane_IVC_array,plane_IVC_label)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## Valve planes: Formatting and saving the segmentation ## \n')
    seg_s4k_array = np.swapaxes(seg_s4k_array,0,2)
    img.save_itk(seg_s4k_array, origin, spacings, DIR('seg_s4k.nrrd'))
    print(" ## Valve planes: Saved segmentation with all valve planes added ## \n")

if __name__ == '__main__' : 
    parser = argparse.ArgumentParser(description='To run: python3 create_myo.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    args = parser.parse_args()
    main(args)