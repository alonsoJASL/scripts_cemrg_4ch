import os
import sys
import glob
import numpy as np

from seg_scripts.common import configure_logging, add_file_handler
from seg_scripts.common import parse_txt_to_json, get_json_data, make_tmp, mycp

import seg_scripts.img as img
import seg_scripts.Labels as L
import seg_scripts.FourChamberProcess as FOURCH
from seg_scripts.ImageAnalysis import ImageAnalysis
from seg_scripts.ImageAnalysis import MaskOperationMode as MM

logger = configure_logging(log_name=__name__)
ZERO_LABEL = 0

def parse_input_parameters(path2points:str, path2originjson:str, path2ptsjson:str = "", labels_file=None, set_debug=False) :

    if path2ptsjson is not None: 
        points_output_file = parse_txt_to_json(path2points, path2ptsjson, "points", "labels")
        points_data = get_json_data(points_output_file)
    else :
        points_data = None
    
    origin_spacing_output_file = parse_txt_to_json(path2points, path2originjson, "origin_spacing", "origin_spacing_labels")
    origin_data = get_json_data(origin_spacing_output_file)

    C = L.Labels(filename=labels_file)
    fcp = FOURCH.FourChamberProcess(path2points, origin_data, CONSTANTS=C, debug=set_debug)

    return fcp, C, points_data

def get_origin_and_spacing(path2points:str, segmentation_name = "seg_corrected.nrrd", dicom_dir = 'ct', output_file = "") :
    """
    Find origin and spacing of the file.
    Needs a segmentation for spacing and dicom for origin.
    
    path2points: path to the folder with points
    segmentation_name: name of the segmentation file (inside path2points)
    dicom_dir: name of the dicom folder (inside path2points)

    output_file: name of the output file (optional, saved inside path2points)
    """
    def get_vec_string(vec) :
        return f'{vec[0]} {vec[1]} {vec[2]}'
    
    logger.info("Finding origin and spacing")
    dir_name = os.path.join(path2points, dicom_dir)

    list_of_files = sorted(filter(os.path.isfile, glob.glob(os.path.join(dir_name, '*')) ) )
    image_origin = img.get_origin_from_dicom(list_of_files)

    origin_string = get_vec_string(image_origin)
    logger.info(f"Origin: {origin_string}")
    
    seg_nrrd = os.path.join(path2points, segmentation_name)
    image_spacing = img.get_image_spacing(seg_nrrd)

    spacing_string = get_vec_string(image_spacing)    
    logger.info(f"Spacing: {spacing_string}")

    if output_file != "" :    
        logger.info(f"Saving origin and spacing to {path2points}/{output_file}")

        # adding _labels to the name of the file
        output_file_labels = output_file.split('.')[0] + '_labels.txt'
        output_path = os.path.join(path2points, output_file)
        with open(output_path, 'w') as f:
            f.write(f'{origin_string}\n')
            f.write(f'{spacing_string}\n')
        
        output_path_labels = os.path.join(path2points, output_file_labels)
        with open(output_path_labels, 'w') as f:
            f.write(f'origin\n')
            f.write(f'spacing\n')
        
def create_cylinders(path2points:str, path2ptsjson="", path2originjson="", segmentation_name="seg_corrected.nrrd") : 
    fcp, _, points_data = parse_input_parameters(path2points, path2originjson, path2ptsjson, labels_file=None)

    if segmentation_name.endswith('.nii'):
        logger.info(f"Converting {segmentation_name} to .nrrd")
        segmentation_name = segmentation_name.replace('.nii','.nrrd')

    if not fcp.check_nrrd(segmentation_name) :
        msg = f"Could not find {segmentation_name} file and conversion to .nii failed."
        logger.error(msg)
        raise FileNotFoundError(msg)
    
    cylinders = [
        ("SVC", 10, 30, ["SVC_1", "SVC_2", "SVC_3"], "SVC.nrrd"),
        ("IVC", 10, 30, ["IVC_1", "IVC_2", "IVC_3"], "IVC.nrrd"),
        ("Ao", 30, 2, ["Ao_1", "Ao_2", "Ao_3"], "aorta_slicer.nrrd"),
        ("PArt", 30, 2, ["PArt_1", "PArt_2", "PArt_3"], "PArt_slicer.nrrd")
    ]

    for name, radius, height, idx, out_name in cylinders :
        logger.info(f"Generating cylinder: {name}")
        # points = np.row_stack([points_data[pt] for pt in idx])
        points = np.row_stack((points_data[idx[0]], points_data[idx[1]], points_data[idx[2]]))
        fcp.cylinder(segmentation_name, points, fcp.DIR(out_name), radius, height)

def create_svc_ivc(path2points:str, path2originjson:str, segmentation_name="seg_corrected.nrrd", output_segname="seg_s2a.nrrd", labels_file=None) :
    fcp, _, _ = parse_input_parameters(path2points, path2originjson, path2ptsjson=None, labels_file=labels_file)

    if segmentation_name.endswith('.nii'):
        logger.info(f"Converting {segmentation_name} to .nrrd")
        segmentation_name = segmentation_name.replace('.nii','.nrrd')
   
    if not fcp.check_nrrd(segmentation_name) : 
        msg = f"Could not find {segmentation_name} file and conversion to .nii failed."
        logger.error(msg)
        raise FileNotFoundError(msg)

    fcp.create_and_save_svc_ivc(segmentation_name, "SVC.nrrd", "IVC.nrrd", output_segname)

def create_slicers(path2points:str, path2ptsjson="", path2originjson="", segmentation_name="seg_s2a.nrrd") : 
    fcp, _, points_data = parse_input_parameters(path2points, path2originjson, path2ptsjson, labels_file=None)

    if segmentation_name.endswith('.nii'):
        logger.info(f"Converting {segmentation_name} to .nrrd")
        segmentation_name = segmentation_name.replace('.nii','.nrrd')

    if not fcp.check_nrrd(segmentation_name) :
        msg = f"Could not find {segmentation_name} file and conversion to .nii failed."
        logger.error(msg)
        raise FileNotFoundError(msg)
        
    slicers = [
        ("SVC_slicer", 30, 2, ["SVC_slicer_1", "SVC_slicer_2", "SVC_slicer_3"], "SVC_slicer.nrrd"),
        ("IVC_slicer", 30, 2, ["IVC_slicer_1", "IVC_slicer_2", "IVC_slicer_3"], "IVC_slicer.nrrd")
    ]

    for name, radius, height, idx, out_name in slicers : 
        logger.info(f"Generating cylinder: {name}")
        # points = np.row_stack([points_data[pt] for pt in idx])
        points = np.row_stack((points_data[idx[0]], points_data[idx[1]], points_data[idx[2]]))
        fcp.cylinder(segmentation_name, points, fcp.DIR(out_name), radius, height)

def crop_svc_ivc(path2points:str, path2ptsjson:str, path2originjson:str, labels_file=None) :
    logger.info("Cropping SVC and IVC") 
    fcp, C, points_data = parse_input_parameters(path2points, path2originjson, path2ptsjson, labels_file=labels_file)

    SVC_seed = points_data['SVC_tip']
    IVC_seed = points_data['IVC_tip']

    fcp.make_tmp()

    fcp.remove_protruding_vessel(SVC_seed, C.SVC_label, 'seg_s2a.nrrd', 'seg_s2b.nrrd')
    fcp.remove_protruding_vessel(IVC_seed, C.IVC_label, 'seg_s2b.nrrd', 'seg_s2c.nrrd')

    aorta_pair = ("aorta_slicer.nrrd", 0) # second is the slicer_label
    PArt_pair = ("PArt_slicer.nrrd", 0) # second is the slicer_label
    fcp.add_vessel_masks('seg_s2c.nrrd', 'seg_s2d.nrrd', aorta_pair, PArt_pair, "SVC_slicer.nrrd", "IVC_slicer.nrrd")

    fcp.flatten_vessel_base('seg_s2d.nrrd', 'seg_s2e.nrrd', SVC_seed, C.SVC_label)
    fcp.flatten_vessel_base('seg_s2e.nrrd', 'seg_s2f.nrrd', IVC_seed, C.IVC_label)

def create_myocardium(path2points:str, path2ptsjson:str, path2originjson:str, labels_file=None, mydebug=False) :
    logger.info("Creating myocardium")
    fcp, C, points_data = parse_input_parameters(path2points, path2originjson, path2ptsjson, labels_file=labels_file, set_debug=mydebug)
    fcp.save_seg_steps = True
    fcp.swap_axes = True

    ima = ImageAnalysis(path2points, debug=mydebug)

    input_seg_array = fcp.load_image_array('seg_s2f.nrrd')

    logger.info("<Step 1/10> Creating myocardium for the LV outflow tract")
    labels = [C.LV_BP_label, C.LV_neck_WT, C.LV_neck_label, 2]
    seg_new_array = fcp.create_myocardium(input_seg_array, labels, MM.ADD, None, 'seg_s3a.nrrd', dmname='LV_DistMap', thname='LV_neck.nrrd')

    seg_new_array = fcp.pushing_in(seg_new_array, C.RV_BP_label, C.LV_myo_label, C.LV_BP_label, C.LV_neck_WT)
    fcp.save_if_seg_steps(seg_new_array, 'seg_s3a.nrrd')

    logger.info("<Step 2/10> Creating the aortic wall")
    labels = [C.Ao_BP_label, C.Ao_WT, C.Ao_wall_label, C.Ao_wall_label]
    seg_new_array = fcp.create_myocardium(seg_new_array, labels, MM.REPLACE_EXCEPT, [C.LV_BP_label, C.LV_myo_label], 'seg_s3b.nrrd', dmname='Ao_DistMap', thname='Ao_wall.nrrd')

    logger.info("<Step 3/10> Creating the pulmonary artery wall")
    labels = [C.PArt_BP_label, C.PArt_WT, C.PArt_wall_label, C.PArt_wall_label]
    seg_new_array = fcp.create_myocardium(seg_new_array, labels, MM.REPLACE_EXCEPT, [3, C.Ao_wall_label], 'seg_s3c.nrrd', dmname='PArt_DistMap', thname='PArt_wall.nrrd')

    seg_new_array = fcp.pushing_in(seg_new_array, C.Ao_wall_label, C.PArt_wall_label, C.PArt_BP_label, C.PArt_WT)
    fcp.save_if_seg_steps(seg_new_array, 'seg_s3d.nrrd')

    logger.info("<Step 4/10> Cropping veins")
    aorta_slicer_array = fcp.load_image_array('aorta_slicer.nrrd')
    seg_new_array = ima.add_masks_replace_only(seg_new_array, aorta_slicer_array, ZERO_LABEL, C.Ao_wall_label)

    PArt_slicer_array = fcp.load_image_array('PArt_slicer.nrrd')
    seg_new_array = ima.add_masks_replace_only(seg_new_array, PArt_slicer_array, ZERO_LABEL, C.PArt_wall_label)

    fcp.save_if_seg_steps(seg_new_array, 'seg_s3e.nrrd')

    seg_new_array = fcp.connected_component_process(seg_new_array, points_data['Ao_tip'], C.Ao_BP_label, 'seg_s3f.nrrd')
    seg_new_array = fcp.connected_component_process(seg_new_array, points_data['PArt_tip'], C.PArt_BP_label, 'seg_s3f.nrrd')

    logger.info("<Step 5/10> Creating the right ventricular myocardium") 
    labels = [C.RV_BP_label, C.RV_WT, C.RV_myo_label, C.RV_myo_label]
    seg_new_array = fcp.create_myocardium(seg_new_array, labels, MM.REPLACE_ONLY, C.Ao_wall_label, 'seg_s3g.nrrd', dmname='RV_BP_DistMap', thname='RV_myo.nrrd')

    logger.info("<Step 6/10> Creating the left atrial myocardium")
    labels = [C.LA_BP_label, C.LA_WT, C.LA_myo_label, C.LA_myo_label, C.LA_myo_label]
    seg_new_array = fcp.create_myocardium(seg_new_array, labels, MM.REPLACE_ONLY, C.LA_myo_label, 'seg_s3h.nrrd', MM.REPLACE_ONLY, C.SVC_label, dmname='LA_BP_DistMap', thname='LA_myo.nrrd')

    logger.info("<Step 7/10> Creating the right atrial myocardium")
    labels = [C.RA_BP_label, C.RA_WT, C.RA_myo_label, C.RA_myo_label]
    seg_new_array = fcp.create_myocardium(seg_new_array, labels, MM.REPLACE_ONLY, C.RA_myo_label, 'seg_s3i.nrrd', dmname='RA_BP_DistMap', thname='RA_myo.nrrd')

    seg_new_array = fcp.pushing_in(seg_new_array, C.LA_myo_label, C.RA_myo_label, C.RA_BP_label, C.RA_WT)
    fcp.save_if_seg_steps(seg_new_array, 'seg_s3j.nrrd')

    seg_new_array = fcp.pushing_in(seg_new_array, C.Ao_wall_label, C.RA_myo_label, C.RA_BP_label, C.RA_WT)
    fcp.save_if_seg_steps(seg_new_array, 'seg_s3k.nrrd')

    seg_new_array = fcp.pushing_in(seg_new_array, C.LV_myo_label, C.RA_myo_label, C.SVC_label, C.RA_WT)
    fcp.save_if_seg_steps(seg_new_array, 'seg_s3k.nrrd')

    seg_new_array = fcp.pushing_in(seg_new_array, C.LV_myo_label, C.RA_myo_label, C.RA_BP_label, C.RA_WT)
    fcp.save_if_seg_steps(seg_new_array, 'seg_s3l.nrrd')

    logger.info("<Step 8/10> LA myo: Pushing the left atrium with the aorta") 
    seg_new_array = fcp.pushing_in(seg_new_array, C.Ao_wall_label, C.LA_myo_label, C.LA_BP_label, C.LA_WT)
    fcp.save_if_seg_steps(seg_new_array, 'seg_s3m.nrrd')

    logger.info("<Step 9/10> PArt wall: Pushing the pulmonary artery with the aorta")
    seg_new_array = fcp.pushing_in(seg_new_array, C.Ao_wall_label, C.PArt_wall_label, C.PArt_BP_label, C.PArt_WT)
    fcp.save_if_seg_steps(seg_new_array, 'seg_s3n.nrrd')

    seg_new_array = fcp.pushing_in(seg_new_array, C.LV_myo_label, C.PArt_wall_label, C.PArt_BP_label, C.PArt_WT)
    fcp.save_if_seg_steps(seg_new_array, 'seg_s3o.nrrd')
    
    logger.info("<Step 10/10> RV myo: Pushing the right ventricle with the aorta") 
    seg_new_array = fcp.pushing_in(seg_new_array, C.Ao_wall_label, C.RV_myo_label, C.RV_BP_label, C.RV_WT)
    fcp.save_if_seg_steps(seg_new_array, 'seg_s3p.nrrd')

def create_valve_planes(path2points:str, path2ptsjson:str, path2originjson:str, labels_file=None, mydebug=False) :
    logger.info("Creating valve planes")
    fcp, C, points_data = parse_input_parameters(path2points, path2originjson, path2ptsjson, labels_file=labels_file, set_debug=mydebug)
    fcp.save_seg_steps = True
    fcp.swap_axes = True

    logger.info("<Step 1/8> Cropping major vessels")
    fcp.get_connected_component_and_save('seg_s3p.nrrd', points_data['Ao_WT_tip'], C.Ao_wall_label, 'seg_s3r.nrrd')
    fcp.get_connected_component_and_save('seg_s3r.nrrd', points_data['PArt_WT_tip'], C.PArt_wall_label, 'seg_s3s.nrrd')

    input_seg_array = fcp.load_image_array('seg_s3s.nrrd')

    logger.info("<Step 2/8> Creating the mitral valve")
    labels = [C.LA_BP_label, C.valve_WT, C.LV_BP_label, C.MV_label, C.MV_label]
    seg_new_array, _, la_bp_thresh, _ = fcp.extract_structure(input_seg_array, labels, "LA_BP_DistMap", "LA_BP_thresh", "seg_s4a.nrrd")

    labels = [C.LV_myo_label, C.LA_WT, C.LA_BP_label, C.LA_myo_label, C.LA_myo_label]
    seg_new_array, lv_myo_distmap, _, _ = fcp.extract_structure(seg_new_array, labels, "LV_myo_DistMap", "LV_myo_thresh", "seg_s4b.nrrd")

    logger.info("<Step 3/8> Creating the tricuspid valve")
    labels = [C.RA_BP_label, C.valve_WT, C.RV_BP_label, C.TV_label, C.TV_label]
    seg_new_array, ra_bp_distmap, _, _ = fcp.extract_structure(seg_new_array, labels, "RA_BP_DistMap", "RA_BP_thresh", "seg_s4c.nrrd")

    labels = [C.RV_myo_label, C.RA_WT, C.RA_BP_label, C.RA_myo_label, C.RA_myo_label]
    seg_new_array, rv_myo_distmap, _, _ = fcp.extract_structure(seg_new_array, labels, "RV_myo_DistMap", "RV_myo_extra", "seg_s4d.nrrd")

    logger.info("<Step 4/8> Creating the aortic valve")
    labels = [C.Ao_BP_label, C.valve_WT, C.LV_BP_label, C.AV_label, C.AV_label]
    seg_new_array, _, _, _ = fcp.extract_structure(seg_new_array, labels, "Ao_BP_DistMap", "AV.nrrd", "seg_s4e.nrrd")

    labels = [-1, C.Ao_WT, C.Ao_BP_label, C.Ao_wall_label, C.Ao_wall_label]
    seg_new_array, _, _, _ = fcp.extract_structure(seg_new_array, labels, "LV_myo_DistMap", "Ao_wall_extra", "seg_s4f.nrrd", lv_myo_distmap)

    labels = [C.AV_label, 2*C.valve_WT, C.MV_label, C.LV_myo_label, C.LV_myo_label]
    seg_new_array, _, _, _ = fcp.extract_structure(seg_new_array, labels, "AV_DistMap", "AV_sep.nrrd", "seg_s4f.nrrd")

    labels = [C.LV_myo_label, C.LA_WT, C.LA_BP_label, C.LA_myo_label, C.LA_myo_label]
    seg_new_array, lv_myo_distmap, _, _ = fcp.extract_structure(seg_new_array, labels, "LV_myo_DistMap", "LV_myo_extra", "seg_s4ff.nrrd")

    logger.info("<Step 5/8> Creating the pulmonary valve")
    labels = [C.PArt_BP_label, C.valve_WT, C.RV_BP_label, C.PV_label, C.PV_label]
    seg_new_array, _, _, _ = fcp.extract_structure(seg_new_array, labels, "PArt_BP_DistMap", "PV.nrrd", "seg_s4g.nrrd")

    labels = [-1, C.PArt_WT, C.PArt_BP_label, C.PArt_wall_label, C.PArt_wall_label]
    seg_new_array, _, _, _ = fcp.extract_structure(seg_new_array, labels, "RV_myo_DistMap", "PArt_wall_extra", "seg_s4h.nrrd", rv_myo_distmap)
    
    seg_h_array = fcp.load_image_array('seg_s4h.nrrd')

    logger.info("<Step 6/8> Create the distance maps needed to cut the vein rings")
    labels = [C.LA_myo_label, C.ring_thickness]
    _, la_myo_thresh = fcp.extract_distmap_and_threshold(seg_new_array, labels, "LA_myo_DistMap", "LA_myo_thresh.nrrd")
    
    labels = [C.RA_myo_label, C.ring_thickness]
    _, ra_myo_thresh = fcp.extract_distmap_and_threshold(seg_new_array, labels, "RA_myo_DistMap", "RA_myo_thresh.nrrd")

    logger.info("<Step 7/8> Creating the vein rings")
    labels = [C.LPV1_label, C.ring_thickness, C.LPV1_ring_label]
    _, lpv1_ring = fcp.extract_distmap_and_threshold(seg_h_array, labels, "LPV1_BP_DistMap", "LPV1_ring.nrrd")
    seg_new_array, seg_i_array = fcp.extract_atrial_rings(seg_h_array, seg_new_array, lpv1_ring, la_myo_thresh, labels[2], "seg_s4i_lpv1.nrrd")

    labels = [C.LPV2_label, C.ring_thickness, C.LPV2_ring_label]
    _, lpv2_ring = fcp.extract_distmap_and_threshold(seg_h_array, labels, "LPV2_BP_DistMap", "LPV2_ring.nrrd")
    seg_new_array, seg_i_array = fcp.extract_atrial_rings(seg_i_array, seg_new_array, lpv2_ring, la_myo_thresh, labels[2], "seg_s4i_lpv2.nrrd")

    labels = [C.RPV1_label, C.ring_thickness, C.RPV1_ring_label]
    _, rpv1_ring = fcp.extract_distmap_and_threshold(seg_h_array, labels, "RPV1_BP_DistMap", "RPV1_ring.nrrd")
    seg_new_array, seg_i_array = fcp.extract_atrial_rings(seg_i_array, seg_new_array, rpv1_ring, la_myo_thresh, labels[2], "seg_s4i_rpv1.nrrd", [C.SVC_label])

    labels = [C.RPV2_label, C.ring_thickness, C.RPV2_ring_label]
    _, rpv2_ring = fcp.extract_distmap_and_threshold(seg_h_array, labels, "RPV2_BP_DistMap", "RPV2_ring.nrrd")
    seg_new_array, seg_i_array = fcp.extract_atrial_rings(seg_i_array, seg_new_array, rpv2_ring, la_myo_thresh, labels[2], "seg_s4i_rpv2.nrrd")

    labels = [C.LAA_label, C.ring_thickness, C.LAA_ring_label]
    _, laa_ring = fcp.extract_distmap_and_threshold(seg_h_array, labels, "LAA_BP_DistMap", "LAA_ring.nrrd")
    seg_new_array, seg_i_array = fcp.extract_atrial_rings(seg_i_array, seg_new_array, laa_ring, la_myo_thresh, labels[2], "seg_s4i_laa.nrrd")

    labels = [C.SVC_label, C.ring_thickness, C.SVC_ring_label] 
    replace_only_labels = [C.Ao_wall_label, C.LA_myo_label, C.RPV1_ring_label, C.RPV1_label, C.RPV2_ring_label, C.RPV2_label]
    _, svc_ring = fcp.extract_distmap_and_threshold(seg_h_array, labels, "SVC_BP_DistMap", "SVC_ring.nrrd")
    seg_new_array, seg_i_array = fcp.extract_atrial_rings(seg_i_array, seg_new_array, svc_ring, ra_myo_thresh, labels[2], "seg_s4i_svc.nrrd", replace_only_labels)

    labels = [C.IVC_label, C.ring_thickness, C.IVC_ring_label]
    _, ivc_ring = fcp.extract_distmap_and_threshold(seg_h_array, labels, "IVC_BP_DistMap", "IVC_ring.nrrd")
    seg_new_array, seg_i_array = fcp.extract_atrial_rings(seg_i_array, seg_new_array, ivc_ring, ra_myo_thresh, labels[2], "seg_s4i.nrrd")
    fcp.save_if_seg_steps(seg_new_array, 'seg_s4j.nrrd')
    
    logger.info("<Step 8/8> Creating the valve planes")
    seg_new_array, _ = fcp.intersect_and_replace(seg_new_array, la_bp_thresh, C.LPV1_label, C.plane_LPV1_label, C.plane_LPV1_label, "seg_s4j_lpv1.nrrd")
    seg_new_array, _ = fcp.intersect_and_replace(seg_new_array, la_bp_thresh, C.LPV2_label, C.plane_LPV2_label, C.plane_LPV2_label, "seg_s4j_lpv2.nrrd")
    seg_new_array, _ = fcp.intersect_and_replace(seg_new_array, la_bp_thresh, C.RPV1_label, C.plane_RPV1_label, C.plane_RPV1_label, "seg_s4j_rpv1.nrrd")
    seg_new_array, _ = fcp.intersect_and_replace(seg_new_array, la_bp_thresh, C.RPV2_label, C.plane_RPV2_label, C.plane_RPV2_label, "seg_s4j_rpv2.nrrd")
    seg_new_array, _ = fcp.intersect_and_replace(seg_new_array, la_bp_thresh, C.LAA_label, C.plane_LAA_label, C.plane_LAA_label, "seg_s4j_laa.nrrd")
    
    labels = [-1, C.valve_WT_svc_ivc]
    _, ra_bp_thresh_2mm = fcp.extract_distmap_and_threshold(seg_new_array, labels, "RA_BP_DistMap", "RA_BP_thresh_2mm.nrrd", dmap_array=ra_bp_distmap)

    seg_new_array, _ = fcp.intersect_and_replace(seg_new_array, ra_bp_thresh_2mm, C.SVC_label, C.plane_SVC_label, C.plane_SVC_label, "seg_s4j_svc.nrrd")
    seg_new_array, _ = fcp.intersect_and_replace(seg_new_array, ra_bp_thresh_2mm, C.RPV1_ring_label, C.plane_SVC_label, C.plane_SVC_label, "seg_s4j_svc_extra.nrrd")
    seg_new_array, _ = fcp.intersect_and_replace(seg_new_array, ra_bp_thresh_2mm, C.IVC_label, C.plane_IVC_label, C.plane_IVC_label, "seg_s4k.nrrd")

    logger.info("Finished creating valve planes")

def clean_segmentation(path2points:str, path2ptsjson:str, path2originjson:str, labels_file=None) :
    logger.info("Cleaning segmentation")
    fcp, C, _ = parse_input_parameters(path2points, path2originjson, path2ptsjson, labels_file=labels_file)

    # mycp(fcp.DIR('seg_s4k.nrrd'), fcp.DIR('seg_s5.nrrd'))
    input_image = 'seg_s4k.nrrd'
    output_image = 'seg_s5.nrrd'

    list_of_corrections1 = [(C.RPV1_ring_label,C.RPV2_ring_label,C.RPV2_label,C.ring_thickness),
                            (C.LPV1_ring_label,C.LPV2_ring_label,C.LPV2_label,C.ring_thickness),
                            (C.LPV1_ring_label,C.LAA_ring_label,C.LAA_label,C.ring_thickness),
                            (C.RV_myo_label,C.Ao_wall_label,C.Ao_BP_label,C.Ao_WT),
                            (C.SVC_ring_label,C.LA_myo_label,C.LA_BP_label,C.LA_WT)]
    
    seg_new_array = fcp.load_image_array(input_image)
    
    for pusher_wall_lab,pushed_wall_lab,pushed_BP_lab, pushed_WT in list_of_corrections1 : 
        seg_new_array = fcp.pushing_in(seg_new_array, pusher_wall_lab, pushed_wall_lab, pushed_BP_lab, pushed_WT)
        print(f'Shape after pushing in {pusher_wall_lab} to {pushed_wall_lab}: {seg_new_array.shape}')
    
    fcp.save_image_array(seg_new_array, fcp.DIR(output_image))
    


