import img
import SimpleITK as sitk

import numpy as np
import nrrd
# import pylab
import json
import os
import argparse

from common import parse_txt_to_json, get_json_data, make_tmp

# ----------------------------------------------------------------------------------------------
# Constants 
# ----------------------------------------------------------------------------------------------
SCALE_FACTOR = 1/0.39844 # scale factor
LV_neck_WT = SCALE_FACTOR*2.00
RV_WT = SCALE_FACTOR*3.50
LA_WT = SCALE_FACTOR*2.00
RA_WT = SCALE_FACTOR*2.00
Ao_WT = SCALE_FACTOR*2.00
PArt_WT = SCALE_FACTOR*2.00
svc_ivc_pad = SCALE_FACTOR*2.00
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


    # ----------------------------------------------------------------------------------------------
    # Make a "tmp" folder for temporarily storing steps in the segmentation pipeline
    # ----------------------------------------------------------------------------------------------
    make_tmp(path2points)
    DIR = lambda x: os.path.join(path2points, x)
    TMP = lambda x: os.path.join(path2points, "tmp", x)
    # ----------------------------------------------------------------------------------------------
    # Define the wall thickness
    # ----------------------------------------------------------------------------------------------

    # ----------------------------------------------------------------------------------------------
    # Create the LV outflow tract myocardium
    # ----------------------------------------------------------------------------------------------
    print('\n ## Step 1/10: Creating myocardium for the LV outflow tract ## \n')
    print(' ## LV neck: Executing distance map ## \n')
    LV_DistMap = img.distance_map(DIR('seg_s2f.nrrd'),LV_BP_label)
    print(' ## LV neck: Writing temporary image ## \n')
    sitk.WriteImage(LV_DistMap,TMP('LV_DistMap.nrrd'),True)

    print(' ## LV neck: Thresholding distance filter ## \n')
    LV_neck = img.threshold_filter_nrrd(TMP('LV_DistMap.nrrd'),0,LV_neck_WT)
    sitk.WriteImage(LV_neck,TMP('LV_neck.nrrd'),True)

    print(' ## LV neck: Adding LV neck to LV myo ## \n')
    LV_neck_array, header = nrrd.read(TMP('LV_neck.nrrd'))
    seg_s2f_array, header = nrrd.read(DIR('seg_s2f.nrrd'))
    LV_neck_array = img.add_masks_replace(LV_neck_array,LV_neck_array,LV_neck_label)
    seg_s3a_array = img.add_masks(seg_s2f_array,LV_neck_array,2)
    # change here!

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## LV neck: Formatting and saving the segmentation ## \n')
    seg_s3a_array = np.swapaxes(seg_s3a_array,0,2)
    img.save_itk(seg_s3a_array, origin, spacings, DIR('seg_s3a.nrrd'))
    print(" ## LV neck: Saved segmentation with LV outflow tract added ## \n")

    # ----------------------------------------------------------------------------------------------
    # LV_myo is pushed by RV_BP
    # ----------------------------------------------------------------------------------------------
    print(' ## Pushing LV_myo with RV_BP ## \n')
    seg_s3a_array = img.push_inside(path2points,DIR('seg_s3a.nrrd'),RV_BP_label,LV_myo_label,LV_BP_label,LV_neck_WT)
    seg_s3a_array = np.swapaxes(seg_s3a_array,0,2)
    img.save_itk(seg_s3a_array, origin, spacings, DIR('seg_s3a.nrrd'))
    print(" ## LV neck: Preventing hole in neck due to RV BP ## \n")

    # ----------------------------------------------------------------------------------------------
    # Create the aortic wall
    # ----------------------------------------------------------------------------------------------
    print(' ## Step 2/10: Creating the aortic wall ## \n')
    print(' ## Aortic wall: Executing distance map ## \n')
    Ao_DistMap = img.distance_map(DIR('seg_s3a.nrrd'),Ao_BP_label)
    print(' ## Aortic wall: Writing temporary image ## \n')
    sitk.WriteImage(Ao_DistMap,TMP('Ao_DistMap.nrrd'),True)

    print(' ## Aortic wall: Thresholding distance filter ## \n')
    Ao_wall = img.threshold_filter_nrrd(TMP('Ao_DistMap.nrrd'),0,Ao_WT)
    sitk.WriteImage(Ao_wall,TMP('Ao_wall.nrrd'),True)

    print(' ## Aortic wall: Adding aortic wall to segmentation ## \n')
    Ao_wall_array, header = nrrd.read(TMP('Ao_wall.nrrd'))
    seg_s3a_array, header = nrrd.read(DIR('seg_s3a.nrrd'))
    Ao_wall_array = img.add_masks_replace(Ao_wall_array,Ao_wall_array,Ao_wall_label)
    seg_s3b_array = img.add_masks_replace_except_2(seg_s3a_array,Ao_wall_array,Ao_wall_label,LV_BP_label,LV_myo_label)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## Aortic wall: Formatting and saving the segmentation ## \n')
    seg_s3b_array = np.swapaxes(seg_s3b_array,0,2)
    img.save_itk(seg_s3b_array, origin, spacings, DIR('seg_s3b.nrrd'))
    print(" ## Aortic wall: Saved segmentation with aortic wall added ## \n")

    # ----------------------------------------------------------------------------------------------
    # Create the pulmonary artery wall
    # ----------------------------------------------------------------------------------------------
    print(' ## Step 3/10: Creating the pulmonary artery wall ## \n')
    print(' ## Pulmonary artery wall: Executing distance map ## \n')
    PArt_DistMap = img.distance_map(DIR('seg_s3b.nrrd'),PArt_BP_label)
    print(' ## Pulmonary artery wall: Writing temporary image ## \n')
    sitk.WriteImage(PArt_DistMap,TMP('PArt_DistMap.nrrd'),True)

    print(' ## Pulmonary artery wall: Thresholding distance filter ## \n')
    PArt_wall = img.threshold_filter_nrrd(TMP('PArt_DistMap.nrrd'),0,PArt_WT)
    sitk.WriteImage(PArt_wall,TMP('PArt_wall.nrrd'),True)

    print(' ## Pulmonary artery wall: Adding pulmonary artery wall to segmentation ## \n')
    PArt_wall_array, header = nrrd.read(TMP('PArt_wall.nrrd'))
    seg_s3b_array, header = nrrd.read(DIR('seg_s3b.nrrd'))
    PArt_wall_array = img.add_masks_replace(PArt_wall_array,PArt_wall_array,PArt_wall_label)
    seg_s3c_array = img.add_masks_replace_except_2(seg_s3b_array,PArt_wall_array,PArt_wall_label,3,Ao_wall_label)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## Pulmonary artery wall: Formatting and saving the segmentation ## \n')
    seg_s3c_array = np.swapaxes(seg_s3c_array,0,2)
    img.save_itk(seg_s3c_array, origin, spacings, DIR('seg_s3c.nrrd'))
    print(" ## Pulmonary artery wall: Saved segmentation with pulmonary artery wall added ## \n")

    # ----------------------------------------------------------------------------------------------
    # Push the pulmonary artery wall into the pulmonary artery blood pool
    # ----------------------------------------------------------------------------------------------
    print(' ## Pulmonary artery wall: Pushing the wall of the pulmonary artery ## \n')
    seg_s3d_array = img.push_inside(path2points,DIR('seg_s3c.nrrd'),Ao_wall_label,PArt_wall_label,PArt_BP_label,PArt_WT)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## Pulmonary artery wall: Formatting and saving the segmentation ## \n')
    seg_s3d_array = np.swapaxes(seg_s3d_array,0,2)
    img.save_itk(seg_s3d_array, origin, spacings, DIR('seg_s3d.nrrd'))
    print(" ## Pulmonary artery wall: Saved segmentation with pulmonary artery wall pushed inside ## \n")

    # ----------------------------------------------------------------------------------------------
    # Crop the aorta and pulmonary artery
    # ----------------------------------------------------------------------------------------------
    print(' ## Step 4/10: Cropping veins ## \n')
    seg_s3d_array, header = nrrd.read(DIR('seg_s3d.nrrd'))

    aorta_slicer_nrrd = DIR('aorta_slicer.nrrd')
    aorta_slicer_label = 0

    aorta_slicer_array, header = nrrd.read(aorta_slicer_nrrd)

    print(' ## Cropping major vessels: Slicing the aortic wall ## \n')
    seg_s3e_array = img.add_masks_replace_only(seg_s3d_array, aorta_slicer_array, aorta_slicer_label, Ao_wall_label)

    PArt_slicer_nrrd = DIR('PArt_slicer.nrrd')
    PArt_slicer_label = 0

    PArt_slicer_array, header = nrrd.read(PArt_slicer_nrrd)

    print(' ## Cropping major vessels: Slicing the pulmonary artery wall ## \n')
    seg_s3e_array = img.add_masks_replace_only(seg_s3e_array, PArt_slicer_array, PArt_slicer_label, PArt_wall_label)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## Cropping major vessels: Formatting and saving the segmentation ## \n')
    seg_s3e_array = np.swapaxes(seg_s3e_array,0,2)
    img.save_itk(seg_s3e_array, origin, spacings, DIR('seg_s3e.nrrd'))
    print(" ## Cropping major vessels: Saved segmentation with aorta and pulmonary artery sliced ## \n")

    # ----------------------------------------------------------------------------------------------
    # Prepare the seeds for the tips of the aorta and pulmonary artery
    # ----------------------------------------------------------------------------------------------
    Ao_tip_seed = points_data['Ao_tip']
    PArt_tip_seed = points_data['PArt_tip']
    Ao_wall_tip_seed = points_data['Ao_WT_tip']
    PArt_wall_tip_seed = points_data['PArt_WT_tip']

    # ----------------------------------------------------------------------------------------------
    # Crop the aorta and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## Cropping major vessels: Cropping the aorta ## \n')
    seg_s3e_nrrd = DIR('seg_s3e.nrrd')
    seg_s3f_array = img.connected_component(seg_s3e_nrrd, Ao_tip_seed, Ao_BP_label,path2points)
    seg_s3f_array = np.swapaxes(seg_s3f_array,0,2)
    img.save_itk(seg_s3f_array, origin, spacings, DIR('seg_s3f.nrrd'))

    # ----------------------------------------------------------------------------------------------
    # Crop the pulmonary artery and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## Cropping major vessels: Cropping the pulmonary artery ## \n')
    seg_s3f_nrrd = DIR('seg_s3f.nrrd')
    seg_s3f_array = img.connected_component(seg_s3f_nrrd, PArt_tip_seed, PArt_BP_label,path2points)
    seg_s3f_array = np.swapaxes(seg_s3f_array,0,2)
    img.save_itk(seg_s3f_array, origin, spacings, DIR('seg_s3f.nrrd'))

    # ----------------------------------------------------------------------------------------------
    # Create the RV myocardium
    # ----------------------------------------------------------------------------------------------
    print(' ## Step 5/10: Creating the right ventricular myocardium: ## \n')
    print(' ## RV myo: Executing distance map ## \n')
    RV_BP_DistMap = img.distance_map(DIR('seg_s3f.nrrd'),RV_BP_label)
    print(' ## RV myo: Writing temporary image ## \n')
    sitk.WriteImage(RV_BP_DistMap,TMP('RV_BP_DistMap.nrrd'),True)

    print(' ## RV myo: Thresholding distance filter ## \n')
    RV_myo = img.threshold_filter_nrrd(TMP('RV_BP_DistMap.nrrd'),0,RV_WT)
    sitk.WriteImage(RV_myo,TMP('RV_myo.nrrd'),True)

    print(' ## RV myo: Adding right ventricular myocardium to segmentation ## \n')
    RV_myo_array, header = nrrd.read(TMP('RV_myo.nrrd'))
    seg_s3f_array, header = nrrd.read(DIR('seg_s3f.nrrd'))
    RV_myo_array = img.add_masks_replace(RV_myo_array,RV_myo_array,RV_myo_label)
    seg_s3g_array = img.add_masks_replace_only(seg_s3f_array,RV_myo_array,RV_myo_label,Ao_wall_label) #NEW CHANGE SO SEE WHAT HAPPENS!

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## RV myo: Formatting and saving the segmentation ## \n')
    seg_s3g_array = np.swapaxes(seg_s3g_array,0,2)
    img.save_itk(seg_s3g_array, origin, spacings, DIR('seg_s3g.nrrd'))
    print(" ## RV myo: Saved segmentation with right ventricular myocardium added ## \n")

    # ----------------------------------------------------------------------------------------------
    # Create the LA myocardium
    # ----------------------------------------------------------------------------------------------
    print(' ## Step 6/10: Creating the left atrial myocardium: ## \n')
    print(' ## LA myo: Executing distance map ## \n')
    LA_BP_DistMap = img.distance_map(DIR('seg_s3g.nrrd'),LA_BP_label)
    print(' ## LA myo: Writing temporary image ## \n')
    sitk.WriteImage(LA_BP_DistMap,TMP('LA_BP_DistMap.nrrd'),True)

    print(' ## LA myo: Thresholding distance filter ## \n')
    LA_myo = img.threshold_filter_nrrd(TMP('LA_BP_DistMap.nrrd'),0,LA_WT)
    sitk.WriteImage(LA_myo,TMP('LA_myo.nrrd'),True)

    print(' ## LA myo: left atrial myocardium to segmentation ## \n')
    LA_myo_array, header = nrrd.read(TMP('LA_myo.nrrd'))
    seg_s3g_array, header = nrrd.read(DIR('seg_s3g.nrrd'))
    LA_myo_array = img.add_masks_replace(LA_myo_array,LA_myo_array,LA_myo_label)
    seg_s3h_array = img.add_masks_replace_only(seg_s3g_array,LA_myo_array,LA_myo_label,RA_BP_label)
    seg_s3h_array = img.add_masks_replace_only(seg_s3h_array,LA_myo_array,LA_myo_label,SVC_label)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## LA myo: Formatting and saving the segmentation ## \n')
    seg_s3h_array = np.swapaxes(seg_s3h_array,0,2)
    img.save_itk(seg_s3h_array, origin, spacings, DIR('seg_s3h.nrrd'))
    print(" ## LA myo: Saved segmentation with left atrial myocardium added ## \n")

    # # ----------------------------------------------------------------------------------------------
    # # Create the RA myocardium
    # # ----------------------------------------------------------------------------------------------
    # print(' ## Step 7/10: Creating the right atrial myocardium: ## \n')
    # print(' ## RA myo: Executing distance map ## \n')
    # RA_BP_DistMap = img.distance_map(DIR('seg_s3h.nrrd'),RA_BP_label)
    # print(' ## RA myo: Writing temporary image ## \n')
    # sitk.WriteImage(RA_BP_DistMap,TMP('RA_BP_DistMap_for_pads.nrrd'),True)

    # print(' ## RA myo: Thresholding distance filter ## \n')
    # SVC_pad = img.threshold_filter_nrrd(TMP('RA_BP_DistMap_for_pads.nrrd'),0,svc_ivc_pad)
    # sitk.WriteImage(SVC_pad,TMP('SVC_pad.nrrd'),True)

    # print(' ## RA myo: Adding SVC pad to segmentation ## \n')
    # SVC_pad_array, header = nrrd.read(TMP('SVC_pad.nrrd'))
    # seg_s3h_array, header = nrrd.read(DIR('seg_s3h.nrrd'))
    # SVC_pad_array = and_filter(seg_s3h_array,SVC_pad_array,SVC_label,RA_BP_label)

    # print(' ## RA myo: Adding IVC pad to segmentation ## \n')
    # IVC_pad_array, header = nrrd.read(TMP('SVC_pad.nrrd'))
    # seg_s3h_array, header = nrrd.read(DIR('seg_s3h.nrrd'))
    # IVC_pad_array = and_filter(seg_s3h_array,IVC_pad_array,IVC_label,RA_BP_label)

    # seg_s3hi_array = img.add_masks_replace_only(seg_s3h_array,SVC_pad_array,RA_BP_label,SVC_label)
    # seg_s3hi_array = img.add_masks_replace_only(seg_s3hi_array,IVC_pad_array,RA_BP_label,IVC_label)

    # print(' ## RA myo: Formatting and saving the segmentation ## \n')
    # seg_s3hi_array = np.swapaxes(seg_s3hi_array,0,2)
    # img.save_itk(seg_s3hi_array, origin, spacings, DIR('seg_s3hi.nrrd'))
    # print(" ## RA myo: Saved segmentation with SVC/IVC pads added ## \n")

    # print(' ## RA myo: Executing distance map again ## \n')
    # RA_BP_DistMap = img.distance_map(DIR('seg_s3hi.nrrd'),RA_BP_label)
    # print(' ## RA myo: Writing temporary image ## \n')
    # sitk.WriteImage(RA_BP_DistMap,TMP('RA_BP_DistMap.nrrd'),True)

    # print(' ## RA myo: Thresholding distance filter ## \n')
    # RA_myo = img.threshold_filter_nrrd(TMP('RA_BP_DistMap.nrrd'),0,RA_WT)
    # sitk.WriteImage(RA_myo,TMP('RA_myo.nrrd'),True)

    # print(' ## RA myo: Adding right atrial myocardium to segmentation ## \n')
    # RA_myo_array, header = nrrd.read(TMP('RA_myo.nrrd'))
    # seg_s3hi_array, header = nrrd.read(DIR('seg_s3hi.nrrd'))
    # RA_myo_array = img.add_masks_replace(RA_myo_array,RA_myo_array,RA_myo_label)
    # seg_s3i_array = img.add_masks_replace_only(seg_s3hi_array,RA_myo_array,RA_myo_label,RPV1_label)

    # ----------------------------------------------------------------------------------------------
    # Create the RA myocardium
    # ----------------------------------------------------------------------------------------------
    print(' ## Step 7/10: Creating the right atrial myocardium: ## \n')
    print(' ## RA myo: Executing distance map ## \n')
    RA_BP_DistMap = img.distance_map(DIR('seg_s3h.nrrd'),RA_BP_label)
    print(' ## RA myo: Writing temporary image ## \n')
    sitk.WriteImage(RA_BP_DistMap,TMP('RA_BP_DistMap.nrrd'),True)

    print(' ## RA myo: Thresholding distance filter ## \n')
    RA_myo = img.threshold_filter_nrrd(TMP('RA_BP_DistMap.nrrd'),0,RA_WT)
    sitk.WriteImage(RA_myo,TMP('RA_myo.nrrd'),True)

    print(' ## RA myo: Adding right atrial myocardium to segmentation ## \n')
    RA_myo_array, header = nrrd.read(TMP('RA_myo.nrrd'))
    seg_s3hi_array, header = nrrd.read(DIR('seg_s3h.nrrd'))
    RA_myo_array = img.add_masks_replace(RA_myo_array,RA_myo_array,RA_myo_label)
    seg_s3i_array = img.add_masks_replace_only(seg_s3hi_array,RA_myo_array,RA_myo_label,RPV1_label)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## RA myo: Formatting and saving the segmentation ## \n')
    seg_s3i_array = np.swapaxes(seg_s3i_array,0,2)
    img.save_itk(seg_s3i_array, origin, spacings, DIR('seg_s3i.nrrd'))
    print(" ## RA myo: Saved segmentation with right atrial myocardium added ## \n")

    # ----------------------------------------------------------------------------------------------
    # Right atrium is pushed by the left atrium
    # ----------------------------------------------------------------------------------------------
    print(' ## RA myo: Pushing the right atrium with the left atrium ## \n')
    seg_s3j_array = img.push_inside(path2points,DIR('seg_s3i.nrrd'),LA_myo_label,RA_myo_label,RA_BP_label,RA_WT)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## RA myo: Formatting and saving the segmentation ## \n')
    seg_s3j_array = np.swapaxes(seg_s3j_array,0,2)
    img.save_itk(seg_s3j_array, origin, spacings, DIR('seg_s3j.nrrd'))
    print(" ## RA myo: Saved segmentation with right atrium pushed by the left atrium ## \n")

    # ----------------------------------------------------------------------------------------------
    # Right atrium is pushed by the aorta
    # ----------------------------------------------------------------------------------------------
    print(' ## RA myo: Pushing the right atrium with the aorta ## \n')
    seg_s3k_array = img.push_inside(path2points,DIR('seg_s3j.nrrd'),Ao_wall_label,RA_myo_label,RA_BP_label,RA_WT)

    print(' ## RA myo: Formatting and saving the segmentation ## \n')
    seg_s3k_array = np.swapaxes(seg_s3k_array,0,2)
    img.save_itk(seg_s3k_array, origin, spacings, DIR('seg_s3k.nrrd'))
    print(" ## RA myo: Saved segmentation with right atrium pushed by the aorta ## \n")

    seg_s3k_array = img.push_inside(path2points,DIR('seg_s3k.nrrd'),Ao_wall_label,RA_myo_label,SVC_label,RA_WT)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## RA myo: Formatting and saving the segmentation ## \n')
    seg_s3k_array = np.swapaxes(seg_s3k_array,0,2)
    img.save_itk(seg_s3k_array, origin, spacings, DIR('seg_s3k.nrrd'))
    print(" ## RA myo: Saved segmentation with right atrium pushed by the aorta ## \n")

    # ----------------------------------------------------------------------------------------------
    # Right atrium is pushed by the left ventricle
    # ----------------------------------------------------------------------------------------------
    print(' ## RA myo: Pushing the right atrium with the left ventricle ## \n')
    seg_s3l_array = img.push_inside(path2points,DIR('seg_s3k.nrrd'),LV_myo_label,RA_myo_label,RA_BP_label,RA_WT)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## RA myo: Formatting and saving the segmentation ## \n')
    seg_s3l_array = np.swapaxes(seg_s3l_array,0,2)
    img.save_itk(seg_s3l_array, origin, spacings, DIR('seg_s3l.nrrd'))
    print(" ## RA myo: Saved segmentation with right atrium pushed by the left ventricle ## \n")

    # ----------------------------------------------------------------------------------------------
    # Left atrium is pushed by the aorta
    # ----------------------------------------------------------------------------------------------
    print(' ## Step 8/10: LA myo: Pushing the left atrium with the aorta ## \n')
    seg_s3m_array = img.push_inside(path2points,DIR('seg_s3l.nrrd'),Ao_wall_label,LA_myo_label,LA_BP_label,LA_WT)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## LA myo: Formatting and saving the segmentation ## \n')
    seg_s3m_array = np.swapaxes(seg_s3m_array,0,2)
    img.save_itk(seg_s3m_array, origin, spacings, DIR('seg_s3m.nrrd'))
    print(" ## LA myo: Saved segmentation with left atrium pushed by the aorta ## \n")

    # ----------------------------------------------------------------------------------------------
    # Pulmonary artery is pushed by the aorta
    # ----------------------------------------------------------------------------------------------
    print(' ## Step 9/10: PArt wall: Pushing the pulmonary artery with the aorta ## \n')
    seg_s3n_array = img.push_inside(path2points,DIR('seg_s3m.nrrd'),Ao_wall_label,PArt_wall_label,PArt_BP_label,PArt_WT)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## PArt wall: Formatting and saving the segmentation ## \n')
    seg_s3n_array = np.swapaxes(seg_s3n_array,0,2)
    img.save_itk(seg_s3n_array, origin, spacings, DIR('seg_s3n.nrrd'))
    print(" ## PArt wall: Saved segmentation with pulmonary artery pushed by the aorta ## \n")

    # ----------------------------------------------------------------------------------------------
    # Pulmonary artery is pushed by the left ventricle
    # ----------------------------------------------------------------------------------------------
    print(' ## PArt wall: Pushing the pulmonary artery with the left ventricle ## \n')
    seg_s3o_array = img.push_inside(path2points,DIR('seg_s3n.nrrd'),LV_myo_label,PArt_wall_label,PArt_BP_label,PArt_WT)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## PArt wall: Formatting and saving the segmentation ## \n')
    seg_s3o_array = np.swapaxes(seg_s3o_array,0,2)
    img.save_itk(seg_s3o_array, origin, spacings, DIR('seg_s3o.nrrd'))
    print(" ## PArt wall: Saved segmentation pulmonary artery pushed by the left ventricle ## \n")

    # ----------------------------------------------------------------------------------------------
    # Right ventricle is pushed by the aorta
    # ----------------------------------------------------------------------------------------------
    print(' ## Step 10/10: RV myo: Pushing the right ventricle with the aorta ## \n')
    seg_s3p_array = img.push_inside(path2points,DIR('seg_s3o.nrrd'),Ao_wall_label,RV_myo_label,RV_BP_label,RV_WT)

    # ----------------------------------------------------------------------------------------------
    # Format and save the segmentation
    # ----------------------------------------------------------------------------------------------
    print(' ## RV myo: Formatting and saving the segmentation ## \n')
    seg_s3p_array = np.swapaxes(seg_s3p_array,0,2)
    img.save_itk(seg_s3p_array, origin, spacings, DIR('seg_s3p.nrrd'))
    print(" ## RV myo: Saved segmentation with right ventricle pushed by the aorta ## \n")

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description='To run: python3 create_myo.py [path_to_points]')
    parser.add_argument("path_to_points")
    parser.add_argument("--points-json", "-pts", type=str, required=False, default="", help="Name of the json file containing the points")
    parser.add_argument("--origin-spacing-json", "-origin-spacing", type=str, required=False, default="", help="Name of the json file containing the origin and spacing")
    args = parser.parse_args()
    main(args)
